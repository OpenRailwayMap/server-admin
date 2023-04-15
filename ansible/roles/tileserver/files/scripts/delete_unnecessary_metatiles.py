#! /usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright (c) 2023 Michael Reichert
# Copyright (c) 2010 Jochen Topf
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; If not, see http://www.gnu.org/licenses/.


"""Find and delete metatiles with or without any views.

This script reads a preprocessed list of tile requests (unique) and deletes all metatiles which have zero requests.
The list of tile requests must be a plain text file with one request URL per line. Each line must match the following format:
{map}/{zoom}/{x}/{y}.{suffix}

You can generate this file from Apache log file using
cut -d \  -f 7 < access.log | grep "^/mymapstyle/" | sort | uniq > tile_requests.txt
"""

import argparse
import os
import sys


def tile_from_path(path, zoom):
    p = path
    if path.startswith("/"):
        p = p[1:]
    parts = p.split("/")
    if len(parts) == 4:
        parts = parts[1:]
    if len(parts) != 3:
        return (None, None)
    try:
        z = int(parts[0])
        if z != zoom:
            return (None, None)
        x = int(parts[1])
        y = int(parts[2].split(".")[0])
        return (x, y)
    except ValueError:
        return (None, None)


def metapath_to_zxy(directory, path):
    # This function is derived from https://github.com/openstreetmap/tirex/blob/master/lib/Tirex/Metatile.pm
    p = path
    if path.startswith(directory):
        p = p[len(directory):]
    if p.startswith("/"):
        p = p[1:]
    if path.endswith(".meta"):
        p = p[:-5]
    parts = p.split("/")
    try:
        z = int(parts[0])
    except ValueError:
        return None, None
    x = 0
    y = 0
    for i in range(1, len(parts)):
        try:
            c = int(parts[i])
        except ValueError:
            return None, None
        if c < 0 or c > 255:
            return None, None
        x <<= 4
        y <<= 4
        x |= (c & 0xf0) >> 4
        y |= (c & 0x0f)
    return x, y

def print_tile(print_tile_ids, path, z, x, y):
    if print_tile_ids:
        for offset_x in range(0, 8):
            for offset_y in range(0, 8):
                print("{}/{}/{}".format(z, x + offset_x, y + offset_y))
    else:
        print(path)


parser = argparse.ArgumentParser(description="Read list of requested tiles and delete all other metatiles from the cache")
parser.add_argument("-a", "--print-accessed", action="store_true", help="Print only (meta)tiles with requests.")
parser.add_argument("-d", "--dry-run", action="store_true", help="Dry run, print deletes only.")
parser.add_argument("--delete-unused", action="store_true", help="Delete metatiles without any requests.")
parser.add_argument("-c", "--cache-directory", type=str, required=True, help="Path to metatile cache of this map style (without zoom level)")
parser.add_argument("-l", "--list", type=argparse.FileType("r"), required=True, help="Path to list of accessed tiles")
parser.add_argument("-u", "--print-unused", action="store_true", help="Print only (meta)tiles without any requests.")
parser.add_argument("-t", "--print-tiles", action="store_true", help="Print tile IDs only.")
parser.add_argument("-z", "--zoom", type=int, required=True, help="Zoom level")
args = parser.parse_args()

if args.print_accessed and args.print_unused:
    sys.stderr.write("ERROR: You cannot the exclusive both option --print-existing and --print-missing.\n")
    exit(1)
if not args.print_accessed and not args.print_unused and not args.delete_unused:
    sys.stderr.write("ERROR: Do action selected.\n")
    exit(1)

# Read tile list
tiles = set()
sys.stderr.write("Reading acccessed tiles.\n")
for line in args.list:
    t = tile_from_path(line, args.zoom)
    if t[0] is not None:
        tiles.add(t)
if len(tiles) == 0:
    sys.stderr.write("ERROR: Did not find any tiles on zoom level {} in the list of accessed tiles. Exiting.\n".format(args.zoom))

# Go through metatiles
sys.stderr.write("Scanning tile cache.\n")
cache_directory = os.path.join(args.cache_directory, str(args.zoom))
deletes = 0
if args.dry_run:
    sys.stderr.write("DRY RUN\n")
for root, dirs, files in os.walk(cache_directory):
    for name in files:
        complete_path = os.path.join(root, name)
        x, y = metapath_to_zxy(cache_directory, complete_path)
        if x is None or y is None:
            continue
        found = False
        for offset_x in range(0, 8):
            for offset_y in range(0, 8):
                if (x + offset_x, y + offset_y) in tiles:
                    found = True
                    break
            if found:
                break
        if found and args.print_accessed:
            print_tile(args.print_tiles, complete_path, args.zoom, x, y)
        if not found and args.print_unused:
            print_tile(args.print_tiles, complete_path, args.zoom, x, y)
        if not found and args.delete_unused:
            sys.stderr.write("Deleting {}\n".format(complete_path))
            if not args.dry_run:
                os.remove(complete_path)
            deletes += 1
if deletes > 0:
    sys.stderr.write("Deleted {} metatiles at zoom level {}.\n".format(deletes, args.zoom))
