#! /usr/bin/env bash

# Delete old metatiles

set -euo pipefail

TILEDIR=/var/lib/tirex/tiles

function delete_metatiles () {
    ZOOM=$1
    MAX_DAYS=$2
    STYLE=$3
    DIR=$TILEDIR/$STYLE/$ZOOM
    echo "Removing metatiles older than $MAX_DAYS from $DIR"
    find $DIR -type f -mtime +$MAX_DAYS -delete
}

for STYLE in standard maxspeed gauge electrification signals ; do
    delete_metatiles 19 41 $STYLE
    delete_metatiles 18 41 $STYLE
    delete_metatiles 17 41 $STYLE
    delete_metatiles 16 51 $STYLE
    delete_metatiles 15 61 $STYLE
    delete_metatiles 14 71 $STYLE
    delete_metatiles 13 81 $STYLE
done
echo "Removed old metatiles." 
