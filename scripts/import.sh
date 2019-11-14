#!/bin/bash

# OpenRailwayMap Copyright (C) 2012 Alexander Matheisen
# This program comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it under certain conditions.
# See https://wiki.openstreetmap.org/wiki/OpenRailwayMap for details.

set -euo pipefail

# source configuration
source $(dirname ${0})/config.cfg

echo "Started processing at $(date)"

echo "[1/3] Downloading planet file"
wget -O $PLANET_FILE https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf

echo "[2/3] Filtering data extract"
$OSMIUM tags-filter -o $PLANET_FILTERED $PLANET_FILE $OSMIUM_FILTER_EXPR

echo "[2/3] Import data into database"
if [ "$OSM2PGSQL_USE_FLATNODES" -eq 1 ]; then
    FLATNODES_OPTION="--flat-node $OSM2PGSQL_FLATNODES"
else
    FLATNODES_OPTION=""
fi
$OSM2PGSQL -d $DATABASE --merc --multi-geometry --hstore --style $OSM2PGSQL_STYLE --tag-transform $OSM2PGSQL_LUA --expire-tiles $EXPIRE_TILES_ZOOM --expire-output $EXPRIE_OUTPUT --expire-bbox-size 30000 --cache 12000 --slim $FLATNODES_OPTION $PLANET_FILTERED

REPLICATION_TIMESTAMP=$($OSMIUM fileinfo -g header.option.osmosis_replication_timestamp $PLANET_FILE)
echo "replication timestamp is $REPLICATION_TIMESTAMP"
echo $REPLICATION_TIMESTAMP > $TIMESTAMP_FILE

echo "[3/3] Prerendering tiles"
tirex-batch --prio $TIREX_PRERENDER_QUEUE map=$TIREX_MAPS z=0-12
cd $PROJECTPATH/renderer

echo "Finished processing at $(date)"
