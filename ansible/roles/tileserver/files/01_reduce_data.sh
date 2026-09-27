#!/bin/bash

set -euo pipefail

psql --dbname gis --variable ON_ERROR_STOP=on --pset pager=off -f /opt/OpenRailwayMap-vector/import/sql/reduce_data.sql
