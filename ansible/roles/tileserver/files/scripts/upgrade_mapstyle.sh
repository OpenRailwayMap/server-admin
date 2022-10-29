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
    echo "Updating database views."
    echo "If errors are reported, remove and recreate the view using following commands:"
    echo "sudo -u osmimport psql -d gis -c 'DROP VIEW viewname CASCADE;'"
    echo "sudo -u osmimport psql -d gis -f sql/osm_carto_views.sql && sudo -u osmimport psql -d gis -f sql/get_station_importance.sql"
    echo "and rerun this script afterwards."
    sudo -u osmimport psql -d gis -f sql/osm_carto_views.sql
    echo "If errors are reported, remove and recreate the view using following commands:"
    echo "sudo -u osmimport psql -d gis -c 'DROP FUNCTION function_name CASCADE;'"
    echo "sudo -u osmimport psql -d gis -f sql/functions.sql"
    echo "and rerun this script afterwards."
    sudo -u osmimport psql -d gis -f sql/functions.sql
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

DO_STYLES=1
if [ $# -eq 1 -a "${1}" = "--no-styles" ]; then
    echo "Skipping style and tile update"
else
    if [ $# -gt 2 -a "${1:?}" = "--bbox" ]; then
        BBOX=${2:?}
        shift 2
    else
        BBOX=-150,-55,180,71
    fi
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

    echo "Reload tirex-backend-manager to use new map styles"
    systemctl reload tirex-backend-manager

    echo "Sending rerender requests to Tirex"
    sudo -u osmimport tirex-batch -f exists -p 21 z=${MINZOOM:?}-${MAXZOOM:?} map=${STYLES:?} bbox=${BBOX:?}
fi

update_website_git_and_build_l10n
