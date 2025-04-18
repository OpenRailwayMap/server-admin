#! /usr/bin/env bash

set -euo pipefail

DBNAME=gis
DIR=/opt/OpenRailwayMap-api/

for FILE in update_milestones.sql update_facilities.sql ; do
    echo "Running queries in ${DIR}/${FILE} against database $DBNAME"
    psql -d "$DBNAME" -f "${DIR}/${FILE}"
done
