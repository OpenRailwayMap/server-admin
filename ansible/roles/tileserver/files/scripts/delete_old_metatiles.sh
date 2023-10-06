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
    delete_metatiles 18 61 $STYLE
    delete_metatiles 17 81 $STYLE
    delete_metatiles 16 91 $STYLE
    delete_metatiles 15 121 $STYLE
    delete_metatiles 14 141 $STYLE
    delete_metatiles 13 181 $STYLE
done
echo "Removed old metatiles." 
