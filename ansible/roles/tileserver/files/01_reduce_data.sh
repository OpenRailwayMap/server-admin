#! /bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Author: Hidde Wieringa <hidde@hiddewieringa.nl>
# Author: Michael Reichert <osm-ml@michreichert.de>

set -euo pipefail

psql -c "delete from platforms p where not exists(select * from routes r where r.platform_ref_ids @> Array[p.osm_id]) and not exists(select * from railway_line l where st_dwithin(p.way, l.way, 20));"
