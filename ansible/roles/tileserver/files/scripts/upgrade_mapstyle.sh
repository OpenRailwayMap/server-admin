#! /usr/bin/env bash

set -euo pipefail

function update_git_and_build_styles {
    MAPSTYLE_GIT=/opt/OpenRailwayMap-CartoCSS/
    cd $MAPSTYLE_GIT
    echo "Fetching latest Git commits and checkout origin/master"
    sudo -u osmimport git fetch origin
    sudo -u osmimport git checkout origin/master
    echo "Building map styles"
    sudo -u osmimport make CARTO=node_modules/carto/bin/carto
}

if [ $# -lt 3 ]; then
    echo "ERROR: Wrong usage."
    echo "Usage: $0 RERENDER_MINZOOM RERENDER_MAXZOOM STYLES_TO_RERENDER..."
    exit 1
fi

MINZOOM=$1
shift
MAXZOOM=$1
shift
STYLES=""
for ARG in $@; do
    if [ "$STYLES" = "" ]; then
        STYLES=$ARG
    else
        STYLES=",$STYLES"
    fi
done

update_git_and_build_styles

echo "Restarting Tirex to clean old queue"
systemctl restart tirex-master tirex-backend-manager

echo "Sending rerender requests to Tirex"
echo "sudo -u tirex tirex-batch -f exists -p 21 z=$MINZOOM-$MAXZOOM map=$STYLES bbox=-180,-80,180,80"
sudo -u osmimport tirex-batch -f exists -p 21 z=$MINZOOM-$MAXZOOM map=$STYLES bbox=-180,-80,180,80
