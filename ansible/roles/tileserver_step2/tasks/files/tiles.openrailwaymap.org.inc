# destination location of this file: /etc/apache2/sites-available
DocumentRoot /var/www/tiles
LogLevel info
ModTileRenderdSocketName /var/lib/tirex/modtile.sock
ModTileTileDir           /var/lib/tirex/tiles
AddTileConfig            /standard standard
AddTileConfig            /maxspeed maxspeed
AddTileConfig            /signals signals
ModTileRequestTimeout 0
ModTileMissingRequestTimeout 90
ModTileMaxLoadOld 4
ModTileMaxLoadMissing 8
