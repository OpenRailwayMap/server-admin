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
{% for style in tileserver.styles -%}
AddTileConfig            /{{ style }} {{ style }}
{% endfor %}
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
	# Tile scraping 2021-12-28
        Require not ip 5.166.235.3
    </RequireAll>
</Location>

RewriteEngine on

# Lacking attribution and high traffic
RewriteCond "%{HTTP_USER_AGENT}" "railon.vonatDroid"
RewriteRule "." "-" [F]

# Generic Android user agent
RewriteCond "%{HTTP_USER_AGENT}" "^Dalvik/[0-9.]+ \(Linux; U; Android"
RewriteRule "." "-" [F]

# Monitoring tool doing test requests every second for three map styles, Deutsche Bahn IP
# RewriteCond "%{HTTP_USER_AGENT}" "SynxHealthTest"
# RewriteRule "." "-" [R=429,L]

ErrorLog {{ apache2_logdir }}/{{ tileserver.hostname }}.error.log
CustomLog {{ apache2_logdir }}/{{ tileserver.hostname }}.access.log combined
