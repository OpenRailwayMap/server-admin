#! /usr/bin/env bash

# OpenRailwayMap Copyright (C) 2019 Michael Reichert
# This program comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it under certain conditions.
# See the LICENSE file for details.

# Script to update the tile rendering database and routing graph.
# Configuration happens in the config.cfg file which is source at the beginning of this script.

# Logs are written to STDOUT which will end up in Systemd's Journal.

set -euo pipefail

source $(dirname ${0})/config.cfg

function apply_diff_database {
    echo "derive diff"
    $OSMIUM derive-changes -o $DERIVED_DIFF $PLANET_FILTERED_OLD $PLANET_FILTERED

    echo "apply diff"
    $OSM2PGSQL --append -d $DATABASE --merc --multi-geometry --hstore --style $OSM2PGSQL_STYLE --tag-transform $OSM2PGSQL_LUA --expire-tiles $EXPIRE_TILES_ZOOM --expire-output $EXPRIE_OUTPUT --expire-bbox-size 30000 --cache 12000 --slim $FLATNODES_OPTION $DERIVED_DIFF

    echo "removing applied diff"
    rm $DERIVED_DIFF

    echo "Expiring up to $(wc -l $EXPIRE_OUTPUT) tiles"
    cat $EXPIRE_OUTPUT | sed -e "s;^\\([0-9]\\+\\)/\\([0-9]\\+\\)/\\([0-9]\\+\\)$;map=$TIREX_MAPS x=\\2 y=\\3 z=\\1;g" | tirex-batch -p $TIREX_RERENDER_PRIO
    rm $EXPIRE_OUTPUT
}


function update_routing_graph {
}

if [ "$TILE_RENDERING" -ne 1 ] && [ "$ROUTING" -ne 1 ]; then
    echo "ERROR: Either tile rendering or routing has to be enabled."
    exit 1
fi

while /bin/true; do
    echo "updating planet"
    while /bin/true; do
        ($PYOSMIUM_UP_TO_DATE -v --tmpdir $PLANET_UPDATE_TMP -s 2000 $PLANET_FILE; sleep 2s) && break
    done

    echo "filtering planet"
    if [ -f "$PLANET_FILTERED" ]; then
        mv $PLANET_FILTERED $PLANET_FILTERED_OLD
    fi
    $OSMIUM tags-filter -o $PLANET_FILTERED $PLANET_FILE $OSMIUM_FILTER_EXPR

    if [ "$TILE_RENDERING" = 1 ]; then
        apply_diff_database
    fi

    if [ "$ROUTING" = 1 ]; then
        update_routing_graph
    fi

    REPLICATION_TIMESTAMP=$($OSMIUM fileinfo -g header.option.osmosis_replication_timestamp $PLANET_FILE)
    echo "replication timestamp is $REPLICATION_TIMESTAMP"
    echo $REPLICATION_TIMESTAMP > $TIMESTAMP_FILE

    sleep $SLEEP_TIME
done
