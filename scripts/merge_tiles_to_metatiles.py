#! /usr/bin/env python3

import argparse
import sys

parser = argparse.ArgumentParser(description="Read a tile expiry list, drop tiles of the same metatile and write the result to standard output.")
parser.add_argument("-z", "--zoom", type=str, help="zoom levels in the following syntax: <int>-<int> or just <int>, i.e. 12-19 for zoom levels 12 to 19")
parser.add_argument("input_file", type=argparse.FileType("r"))
args = parser.parse_args()

zooms = args.zoom.split("-")
if len(zooms) < 1 or len(zooms) > 2:
    sys.stderr.write("ERROR: Invalid --zoom option provided.\n")
    exit(1)
try:
    zooms = [ int(z) for z in zooms ]
except ValueError:
    sys.stderr.write("ERROR: Invalid --zoom option provided, values are no integers.\n")
    exit(1)
minzoom = zooms[0]
if len(zooms) == 1:
    maxzoom = minzoom
else:
    maxzoom = zooms[1]
if minzoom > maxzoom:
    sys.stderr.write("ERROR: Maxzoom is larger than minzoom.\n")
    exit(1)
if maxzoom < 0:
    sys.stderr.write("ERROR: Maxzoom is negative.\n")
    exit(1)
if maxzoom > 22:
    sys.stderr.write("ERROR: Maxzoom is too large.\n")
    exit(1)

# create lists for last x and y index we have seen at each zoom level
last_x = [ -1 for i in range(0, maxzoom - minzoom + 1) ]
last_y = [ -1 for i in range(0, maxzoom - minzoom + 1) ]

for line in args.input_file:
    items = line.strip().split("/")
    if len(items) != 3:
        continue
    try:
        items = [ int(e) for e in items ]
    except ValueError:
        sys.stderr.write("Failed to parse line from input: {}".format(line))
        exit(1)
    # normalise by diving the integer by 8
    x_norm = (items[1] >> 3) << 3
    y_norm = (items[2] >> 3) << 3
    offset = items[0] - minzoom
    if last_x[offset] == x_norm and last_y[offset] == y_norm:
        continue
    sys.stdout.write(line)
    last_x[offset] = x_norm
    last_y[offset] = y_norm
