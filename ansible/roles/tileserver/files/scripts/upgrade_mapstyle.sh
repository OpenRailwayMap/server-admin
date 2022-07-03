#! /usr/bin/env bash

set -euo pipefail

function update_git_and_build_styles {
    MAPSTYLE_GIT=/opt/OpenRailwayMap-CartoCSS/
    pushd ${MAPSTYLE_GIT}
    echo "Fetching latest Git commits and checkout origin/master"
    sudo -u osmimport git fetch origin
    sudo -u osmimport git checkout origin/master
    echo "Building map styles"
    sudo -u osmimport make CARTO=node_modules/carto/bin/carto
    popd
}

function update_website_git_and_build_l10n {
    WEBSITE_GIT=/var/www/www.openrailwaymap.org
    pushd ${WEBSITE_GIT}
    echo "updating upstream website changes"
    git pull --ff
    make
    popd
}

if [ $# -lt 3 ]; then
    echo "ERROR: Wrong usage."
    echo "Usage: $0 RERENDER_MINZOOM RERENDER_MAXZOOM STYLES_TO_RERENDER..."
    exit 1
fi

MINZOOM=$1
MAXZOOM=$2
shift 2
STYLES=$( IFS=, ; echo "${*}" )

update_git_and_build_styles

echo "Restarting Tirex to clean old queue"
systemctl restart tirex-master tirex-backend-manager

echo "Sending rerender requests to Tirex"
sudo -u osmimport tirex-batch -f exists -p 21 z=${MINZOOM:?}-${MAXZOOM:?} map=${STYLES:?} bbox=-180,-80,180,80

update_website_git_and_build_l10n
