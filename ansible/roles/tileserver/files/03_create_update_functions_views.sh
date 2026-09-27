#!/bin/bash

set -euo pipefail

echo "Post processing imported data"
cd /opt/OpenRailwayMap-vector/import

run_sql() {
    echo "Running $1 ..."
    psql -f "$1"
}

# Functions
run_sql sql/tile_functions.sql
run_sql sql/api_facility_functions.sql
run_sql sql/api_milestone_functions.sql

# YAML data
run_sql sql/signal_features.sql
run_sql sql/operators.sql

# Post processing
run_sql sql/get_station_importance.sql
run_sql sql/update_station_importance.sql
echo "Running osm2pgsql-gen ..."
osm2pgsql-gen \
  --database gis \
  --style openrailwaymap.lua
run_sql sql/stations_clustered.sql

# Tile and API views on processed data
run_sql sql/tile_views.sql
run_sql sql/api_facility_views.sql
