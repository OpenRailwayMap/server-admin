# destination location of this file: /etc/apache2/sites-available

ServerName tiles.openrailwaymap.org
ServerAlias a.tiles.openrailwaymap.org
ServerAlias b.tiles.openrailwaymap.org
ServerAlias c.tiles.openrailwaymap.org
ServerAlias tiles.buegelfalte.openrailwaymap.org
ServerAdmin info@openrailwaymap.org

DocumentRoot /var/www/tiles
LogLevel info tile:warn ssl:warn
ModTileRenderdSocketName /var/lib/tirex/modtile.sock
ModTileTileDir           /var/lib/tirex/tiles
AddTileConfig            /standard standard
AddTileConfig            /maxspeed maxspeed
AddTileConfig            /signals signals
AddTileConfig            /electrification electrification
ModTileRequestTimeout 0
ModTileMissingRequestTimeout 90
ModTileMaxLoadOld 4
ModTileMaxLoadMissing 8

# Tile throttling for abusers
ModTileEnableTileThrottling On
ModTileEnableTileThrottlingXForward 0
ModTileThrottlingTiles 10000 1
ModTileThrottlingRenders 128 0.2

ErrorLog /var/log/apache2/tiles.openrailwaymap.org.error.log
CustomLog /var/log/apache2/tiles.openrailwaymap.org.access.log combined
