#!/usr/bin/python3
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2018-2020 Tom Hughes
# OpenRailwayMap Copyright (C) 2021 Michael Reichert
#
# This file is part of the OpenRailwayMap server admin tools repository
# (https://github.com/OpenRailwayMap/server-admin).
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# This script is a modified copy of expire-tiles-single by Tom Hughes published at
# https://github.com/openstreetmap/chef/blob/master/cookbooks/tile/templates/default/expire-tiles.erb
# under Apache License 2.0. See Apache_License_v2.txt for the full legal text of that license.

"""
Derive meta tiles to be updated from a OSM change and a node location cache and write them to
standard output to be fed into tirex-batch.
"""

import argparse
import os
import osmium as o
import pyproj
import psycopg2

# width/height of the spherical mercator projection
SIZE = 40075016.6855784
COORDINATE_PRECISION = 10000000

proj_transformer = pyproj.transformer.Transformer.from_crs('epsg:4326', 'epsg:3857', always_xy = True)


def top_left_tile(x, y):
    "Return X and Y tile index of top left tile in the metatile this tile is located in."
    x = (x >> 3) << 3
    y = (y >> 3) << 3
    return x, y


class TileCollector(o.SimpleHandler):

    def __init__(self, node_cache, db_connection, zoom):
        super(TileCollector, self).__init__()
        if node_cache:
            self.node_cache = o.index.create_map("dense_file_array," + node_cache)
            self.db_connection = None
        else:
            self.node_cache = None
            self.db_connection = db_connection
        self.done_nodes = set()
        self.tile_set = set()
        self.zoom = zoom

    def add_tile_from_node(self, location):
        if not location.valid():
            return

        lat = max(-85, min(85.0, location.lat))
        x, y = proj_transformer.transform(location.lon, lat)

        # renormalise into unit space [0,1]
        x = 0.5 + x / SIZE
        y = 0.5 - y / SIZE
        # transform into tile space
        x = x * 2**self.zoom
        y = y * 2**self.zoom
        # chop of the fractional parts and reduce to top left tile of the metatile
        x, y = top_left_tile(int(x), int(y))
        self.tile_set.add((x, y, self.zoom))

    def node(self, node):
        # we put all the nodes into the hash, as it doesn't matter whether the node was
        # added, deleted or modified - the tile will need updating anyway.
        self.done_nodes.add(node.id)
        self.add_tile_from_node(node.location)

    def _location_from_int(self, x, y):
        return float(x) / COORDINATE_PRECISION, float(y) / COORDINATE_PRECISION

    def _get_node_location(self, node_ref):
        if self.node_cache:
            return self.node_cache.get(node_ref)
        with self.db_connection.cursor() as cur:
            cur.execute("SELECT lon, lat FROM planet_osm_nodes WHERE id = %s", (node_ref,))
            row = cur.fetchone()
            x = row[0]
            y = row[1]
            lon, lat = self._location_from_int(x, y)
            return o.osm.Location(lon, lat)

    def way(self, way):
        for n in way.nodes:
            if not n.ref in self.done_nodes:
                self.done_nodes.add(n.ref)
                try:
                    location = self._get_node_location(n.ref)
                    self.add_tile_from_node(location)
                    #self.add_tile_from_node(self.node_cache.get(n.ref))
                except KeyError:
                    pass # no coordinate


def xyz_to_tirex(x, y, z, destination_zoom):
    x = x >> (2 * (z - destination_zoom))
    y = y >> (2 * (z - destination_zoom))
    return x, y


def expire_tirex(tile, zoom, map_name):
    print("z={} x={} y={} map={}".format(zoom, tile[0], tile[1], map_name))


def expire_meta_tiles(options):
    try:
        if not options.node_cache:
            db_conn = psycopg2.connect(options.db_params)
        else:
            db_conn = None
        proc = TileCollector(options.node_cache, db_conn, options.max_zoom)
        proc.apply_file(options.inputfile)
    finally:
        if db_conn:
            db_conn.close()

    tile_set = proc.tile_set

    # turn all the tiles into expires, putting them in the set
    # so that we don't expire things multiple times
    for z in range(options.min_zoom, options.max_zoom + 1):
        meta_set = set()
        new_set = set()
        for xy in tile_set:
            meta = xyz_to_tirex(xy[0], xy[1], xy[2], z)
            meta_set.add(meta)

        # expire all meta tiles
        for meta in meta_set:
            for map_name in options.map:
                expire_tirex(meta, z, map_name)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     usage='%(prog)s [options] <inputfile>')
    parser.add_argument('--min', action='store', dest='min_zoom', default=13,
                        type=int,
                        help='Minimum zoom for expiry.')
    parser.add_argument('--max', action='store', dest='max_zoom', default=20,
                        type=int,
                        help='Maximum zoom for expiry.')
    parser.add_argument('--map', action='append', dest='map', default=None,
                        help='Tirex map name (repeat for multiple maps).')
    parser.add_argument('--meta-tile-size', action='store', dest='meta_size',
                        default=8, type=int,
                        help='The size of the meta tile blocks.')
    parser.add_argument('--node-cache', action='store', dest='node_cache',
                        help='osm2pgsql flatnode file.')
    parser.add_argument('--db-params', action='store', dest='db_params',
                        default='dbname=gis',
                        help='Database connection string, e.g. "dbname=gis user=postgres password=12345 host=127.0.0.1 port=5432".')
    parser.add_argument('inputfile',
                        help='OSC input file.')

    options = parser.parse_args()

    expire_meta_tiles(options)
