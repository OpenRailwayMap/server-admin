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

echo "[1/3] Downloading planet file"
wget --progress=dot:giga --no-clobber -O $PLANET_FILE https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf

echo "[2/3] Filtering data extract"
$OSMIUM tags-filter -o $PLANET_FILTERED $PLANET_FILE $OSMIUM_FILTER_EXPR

echo "[3/3] Import data into database"
if [[ -v "OSM2PGSQL_FLATNODES" ]]; then
    FLATNODES_OPTION="--flat-node $FLATNODES_FILE"
else
    FLATNODES_OPTION=""
fi
$OSM2PGSQL -d $DATABASE_NAME --merc --multi-geometry --hstore --style $OSM2PGSQL_STYLE --tag-transform $OSM2PGSQL_LUA --slim $FLATNODES_OPTION $PLANET_FILTERED

REPLICATION_TIMESTAMP=$($OSMIUM fileinfo -g header.option.osmosis_replication_timestamp $PLANET_FILE)
echo "replication timestamp is $REPLICATION_TIMESTAMP"
date --date="$REPLICATION_TIMESTAMP" +%s > $TIMESTAMP_PATH

echo "Finished import at $(date), please install mod_tile and Tirex now."
