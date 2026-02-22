#!/bin/bash

set -euo pipefail

echo "Post processing imported data"
cd /opt/OpenRailwayMap-vector/import

# Functions
psql -f sql/tile_functions.sql
psql -f sql/api_facility_functions.sql
psql -f sql/api_milestone_functions.sql

# YAML data
psql -f sql/signal_features.sql
psql -f sql/operators.sql

# Post processing
psql -f sql/get_station_importance.sql
psql -f sql/update_station_importance.sql
osm2pgsql-gen \
  --database gis \
  --style openrailwaymap.lua
psql -f sql/stations_clustered.sql

# Tile and API views on processed data
psql -f sql/tile_views.sql
psql -f sql/api_facility_views.sql
