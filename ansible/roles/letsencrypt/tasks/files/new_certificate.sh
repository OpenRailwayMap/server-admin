#! /usr/bin/env bash

# Generate certificate signing request (CSR)
# This script must run as root because only root has access to the domain key.

set -euo pipefail

if [ "$#" -ne 0 ]; then
  echo "Wrong usage -- this script does not expect any arguments."
  exit 1
fi

source $(dirname ${0})/acme_scripts_config.cfg

echo "Generating CSR"
openssl req -new -sha256 -key $LETSENCRYPT_ETC/domain.key -subj "/" -reqexts SAN -config <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=$SUBJECT_ALT_NAMES")) > $ACME_WORKING_DIR/domain.csr

# current date
TODAY=`date +"%Y-%m-%d"`

# request certificate
echo "Requesting certificate"
CERT_FILENAME=$DOMAIN-$TODAY.crt
sudo -u acme bash $ACME_TINY_DIR/request_certificate.sh $DOMAIN " " > $ACME_WORKING_DIR/$CERT_FILENAME || { echo 'requesting certificate failed' ; exit 1; }

# move certificate to the directory where the certificates are stored
mv $ACME_WORKING_DIR/$CERT_FILENAME $LETSENCRYPT_ETC/$DOMAIN-$TODAY-fullchain.pem

# set ownership and permissions
echo "Set ownership and permissions"
chmod 644 $LETSENCRYPT_ETC/$DOMAIN-$TODAY-fullchain.pem
chown root:root $LETSENCRYPT_ETC/$DOMAIN-$TODAY-fullchain.pem

# change symlinks
echo "Updating symlinks"
#ln -s $LETSENCRYPT_ETC/$CERT_FILENAME $LETSENCRYPT_ETC/$DOMAIN.crt.new
ln -s $LETSENCRYPT_ETC/$DOMAIN-$TODAY-fullchain.pem $LETSENCRYPT_ETC/$DOMAIN-chain.crt.new

# move these symlinks on the old ones
mv $LETSENCRYPT_ETC/$DOMAIN-chain.crt.new $LETSENCRYPT_ETC/$DOMAIN-chain.crt

# reload services
echo "Reload Apache and Postfix"
systemctl reload apache2.service
systemctl reload postfix.service

# clean up
rm $ACME_WORKING_DIR/domain.csr
echo "Finished"
