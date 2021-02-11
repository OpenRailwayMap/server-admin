ServerName {{ tileserver.hostname }}
{% for host_alias in tileserver.hostname_aliases -%}
ServerAlias {{ host_alias }}
{% endfor %}
ServerAdmin info@openrailwaymap.org

DocumentRoot /var/www/tiles
{% if 'letsencrypt' in group_names %}
LogLevel info tile:warn ssl:warn
{% else %}
LogLevel info tile:warn
{% endif %}

ModTileRenderdSocketName /var/lib/tirex/modtile.sock
ModTileTileDir           /var/lib/tirex/tiles
AddTileConfig            /standard standard
AddTileConfig            /maxspeed maxspeed
AddTileConfig            /signals signals
AddTileConfig            /electrification electrification
Redirect permanent       /electrified /electrification
ModTileRequestTimeout 0
ModTileMissingRequestTimeout 90
ModTileMaxLoadOld 4
ModTileMaxLoadMissing 8

# Tile throttling for abusers
ModTileEnableTileThrottling On
ModTileEnableTileThrottlingXForward 0
ModTileThrottlingTiles 10000 1
ModTileThrottlingRenders 128 0.2

Header set Access-Control-Allow-Origin "*"

<Location />
    <RequireAll>
        Require all granted
        Require not ip 5.35.80.253
    </RequireAll>
</Location>

RewriteEngine on
RewriteCond "%{HTTP_USER_AGENT}" "railon.vonatDroid"
RewriteRule "." "-" [F]

ErrorLog {{ apache2_logdir }}/{{ tileserver.hostname }}.error.log
CustomLog {{ apache2_logdir }}/{{ tileserver.hostname }}.access.log combined
