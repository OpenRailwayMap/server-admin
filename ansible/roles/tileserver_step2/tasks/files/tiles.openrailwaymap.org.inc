# destination location of this file: /etc/apache2/sites-available

ServerName tiles.openrailwaymap.org
ServerAlias a.tiles.openrailwaymap.org
ServerAlias b.tiles.openrailwaymap.org
ServerAlias c.tiles.openrailwaymap.org
ServerAlias tiles.buegelfalte.openrailwaymap.org
ServerAlias openrailwaymap2019.michreichert.de
ServerAdmin info@openrailwaymap.org

DocumentRoot /var/www/tiles
LogLevel info tile:warn
ModTileRenderdSocketName /var/lib/tirex/modtile.sock
ModTileTileDir           /var/lib/tirex/tiles
AddTileConfig            /standard standard
AddTileConfig            /maxspeed maxspeed
AddTileConfig            /signals signals
ModTileRequestTimeout 0
ModTileMissingRequestTimeout 90
ModTileMaxLoadOld 4
ModTileMaxLoadMissing 8

Alias "/.well-known/acme-challenge/" "/var/lib/acme/challenges/"
<location /.well-known/acme-challenge/>
    Require all granted
</location>

ErrorLog /var/log/apache2/tiles.openrailwaymap.org.error.log
CustomLog /var/log/apache2/tiles.openrailwaymap.org.access.log combined
