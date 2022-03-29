#!/usr/bin/python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Expire meta tiles from a OSM change file by resetting their modified time.

This script is based on expire-tiles-single from
https://github.com/openstreetmap/chef/blob/master/cookbooks/tile/files/default/bin/expire-tiles-single
which was published under Apache License version 2.
"""

import argparse
import os
import osmium as o
import math

# width/height of the spherical mercator projection
SIZE = 40075016.6855784

def lonlat_to_merc(lon, lat):
    lon_rad = math.radians(lon)
    lat_rad = math.radians(lat)
    HALF_SIZE = 0.5 * SIZE
    x_merc = (lon_rad / (math.pi)) * HALF_SIZE
    y_merc = (math.log(math.tan(0.25 * math.pi + 0.5 * lat_rad))) * (HALF_SIZE / math.pi)
    return x_merc, y_merc

class TileCollector(o.SimpleHandler):

    def __init__(self, node_cache, zoom):
        super(TileCollector, self).__init__()
        self.node_cache = o.index.create_map("dense_file_array," + node_cache)
        self.done_nodes = set()
        self.tile_set = set()
        self.zoom = zoom

    def add_tile_from_node(self, location):
        if not location.valid():
            return

        lat = max(-85, min(85.0, location.lat))
        #x, y = proj_transformer.transform(location.lon, lat)
        x, y = lonlat_to_merc(location.lon, lat)

        # renormalise into unit space [0,1]
        x = 0.5 + x / SIZE
        y = 0.5 - y / SIZE
        # transform into tile space
        x = x * 2**self.zoom
        y = y * 2**self.zoom
        # chop of the fractional parts
        self.tile_set.add((int(x), int(y), self.zoom))

    def node(self, node):
        # we put all the nodes into the hash, as it doesn't matter whether the node was
        # added, deleted or modified - the tile will need updating anyway.
        self.done_nodes.add(node.id)
        self.add_tile_from_node(node.location)

    def way(self, way):
        for n in way.nodes:
            if not n.ref in self.done_nodes:
                self.done_nodes.add(n.ref)
                try:
                    self.add_tile_from_node(self.node_cache.get(n.ref))
                except KeyError:
                    pass # no coordinate


def xyz_to_topleft(x, y, z, meta_size):
    """ Return tile ID of top left corner of the meta tile.
    """
    x = x - (x % meta_size)
    y = y - (y % meta_size)
    return x, y, z


def expire_tile(x, y, z):
    print('{}/{}/{}'.format(z, x, y))


def expire_meta_tiles(options):
    proc = TileCollector(options.node_cache, options.max_zoom)
    proc.apply_file(options.inputfile)

    tile_set = proc.tile_set

    # turn all the tiles into expires, putting them in the set
    # so that we don't expire things multiple times
    for z in range(options.max_zoom, options.min_zoom - 1, -1):
        meta_set = set()
        new_set = set()
        for xy in tile_set:
            x, y, z = xyz_to_topleft(xy[0], xy[1], xy[2], options.meta_size)
            meta_set.add((x, y, z))

            # add the parent into the set for the next round
            new_set.add((int(xy[0]/2), int(xy[1]/2), xy[2] - 1))

        # expire all meta tiles
        for meta in meta_set:
            expire_tile(meta[0], meta[1], meta[2])

        # continue with parent tiles
        tile_set = new_set

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
    parser.add_argument('--meta-tile-size', action='store', dest='meta_size',
                        default=8, type=int,
                        help='The size of the meta tile blocks.')
    parser.add_argument('--node-cache', action='store', dest='node_cache',
                        default='/store/database/nodes',
                        help='osm2pgsql flatnode file.')
    parser.add_argument('inputfile',
                        help='OSC input file.')

    options = parser.parse_args()

    expire_meta_tiles(options)
