#! /usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# OpenRailwayMap Copyright (C) 2012 Alexander Matheisen
# OpenRailwayMap Copyright (C) 2019 Michael Reichert
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

# This script does the initial data import into the tile rendering database. Configuration happens
# in the config.cfg file which is source at the beginning of this script.

set -euo pipefail

# source configuration
source $(dirname ${0})/config.cfg

echo "Started processing at $(date)"

echo "[1/4] Downloading planet file"
wget --progress=dot:giga --no-clobber -O $PLANET_FILE --continue https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf || true
RET_CODE=$?
if [ $RET_CODE -eq 1 ]; then
    PLANET_SIZE=$(stat --printf="%s" "$PLANET_FILE")
    if [ "$PLANET_SIZE" -lt 91279000000 ]; then
         echo "ERROR: Planet download failed with return code $RET_CODE and found file is too small."
	 exit 1
    fi
elif [ $RET_CODE -gt 0 ]; then
    echo "ERROR: Planet download failed with return code $RET_CODE and found file is too small."
    exit 1
fi

echo "[2/4] Filtering data extract"
FILTER_ARG=""
if [[ -n "OSMIUM_FILTER_EXPR_FILE" ]]; then
    FILTER_ARG="-e $OSMIUM_FILTER_EXPR_FILE"
fi
$OSMIUM tags-filter $FILTER_ARG -o $PLANET_FILTERED $PLANET_FILE $OSMIUM_FILTER_EXPR

echo "[3/4] Import data into database"
if [[ -v "OSM2PGSQL_FLATNODES" ]]; then
    FLATNODES_OPTION="--flat-node $OSM2PGSQL_FLATNODES"
else
    FLATNODES_OPTION=""
fi
if [[ -n "OSM2PGSQL_TAG_TRANSFORM" ]]; then
    TAG_TRANSFORM_OPTION="--tag-transform $OSM2PGSQL_TAG_TRANSFORM"
else
    TAG_TRANSFORM_OPTION=""
fi
if [ "$OSM2PGSQL_OUTPUT" = "pgsql" ]; then
    EXTRA_OPTS="--merc --hstore"
else
    EXTRA_OPTS=""
fi

$OSM2PGSQL --create -d $DATABASE_NAME --output $OSM2PGSQL_OUTPUT $EXTRA_OPTS --multi-geometry --style $OSM2PGSQL_STYLE $TAG_TRANSFORM_OPTION --slim $FLATNODES_OPTION $PLANET_FILTERED

echo "[4/4] Running additional update scripts in /opt/OpenRailwayMap-server-config/post-update.d/"
run-parts --exit-on-error -v /opt/OpenRailwayMap-server-config/post-import.d/

REPLICATION_TIMESTAMP=$($OSMIUM fileinfo -g header.option.osmosis_replication_timestamp $PLANET_FILE)
echo "replication timestamp is $REPLICATION_TIMESTAMP"
date --date="$REPLICATION_TIMESTAMP" +%s > $TIMESTAMP_PATH

echo "Finished import at $(date), please install mod_tile and Tirex now."
