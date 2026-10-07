#! /bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Author: Hidde Wieringa <hidde@hiddewieringa.nl>
# Author: Michael Reichert <osm-ml@michreichert.de>

set -euo pipefail

psql --dbname gis --variable ON_ERROR_STOP=on --pset pager=off -f /opt/OpenRailwayMap-vector/import/sql/transform_data.sql
