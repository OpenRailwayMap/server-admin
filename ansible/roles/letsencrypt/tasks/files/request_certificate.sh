#! /usr/bin/env bash

set -euo pipefail

if [ "$#" -ne "2" ]; then
  echo "Too few or too much arguments. Correct usage: $0 DOMAIN MORE_ARGS"
  exit 1
fi

source $(dirname ${0})/acme_scripts_config.cfg

DOMAIN=$1
MORE_ARGS=$2

# Request a new LetsEncrypt certificate
$ACME_TINY $MORE_ARGS --directory-url "$ACME_API" --account-key $ACME_WORKING_DIR/account.key --csr $ACME_WORKING_DIR/domain.csr --acme-dir $ACME_WORKING_DIR/challenges/
