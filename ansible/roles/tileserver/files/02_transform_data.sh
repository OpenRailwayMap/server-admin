#! /bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Author: Hidde Wieringa <hidde@hiddewieringa.nl>
# Author: Michael Reichert <osm-ml@michreichert.de>

set -euo pipefail

psql -c "update stations s set way = l.way from landuse l where ST_Within(s.way, l.way) and feature = 'yard' and GeometryType(s.way) = 'POINT' and s.osm_type = 'N';"

