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

## Samsung Smart TV, see below
#        Require not ip 185.109.16.136
#        Require not ip 185.109.16.135
    </RequireAll>
</Location>

Alias /tile-util/ /var/www/tile-util/
<Directory /var/www/tile-util>
    Require all granted
</Directory>

RewriteEngine on

# Lacking attribution and high traffic
RewriteCond "%{HTTP_USER_AGENT}" "railon.vonatDroid" [OR]
# 50k to 200k tile requets per day but website is not public (looks like for-charge service)
# Responding with HTTP status 429 for about 5 days did not make this client to go away.
RewriteCond "%{HTTP_REFERER}" "//rastreobusmen\.geovoy\.com/" [OR]
# More than 20k tile requets per day but website is not public (looks like for-charge service)
RewriteCond "%{HTTP_REFERER}" "//(www\.)?geliospro\.com/"
# SEO website with ads and no meaningful content after a rough review (no HTTP 429 prior to black tile response)
RewriteCond "%{HTTP_REFERER}" "//zugradar.info/"
RewriteRule "." "/tile-util/black.png" [PT]

# Requests with invalid URLs (missing style name), 300k requests per day, user-agent is a Samsung TV
RewriteCond "%{HTTP_USER_AGENT}" "SMART-TV; Linux; Tizen 4.0"
RewriteRule "^/[0-9]" "/tile-util/black.png" [PT]

# Embedded, unpatched software
RewriteCond "%{HTTP_USER_AGENT}" "^Mozilla/4\.0"
# Empty user agents
RewriteCond "%{HTTP_REFERER}" "^$"
RewriteRule "." "-" [F]

# User-agent of a browser more than 10 years old and no referer
RewriteCond "%{HTTP_USER_AGENT}" "^Opera/9\."
# Empty user agents
RewriteCond "%{HTTP_REFERER}" "^$"
RewriteRule "." "-" [F]

# Generic user agents
# Dalvik, an Android HTTP library
RewriteCond "%{HTTP_USER_AGENT}" "^Dalvik/[0-9.]+ \(Linux; U; Android" [OR]
# Dart:io, a NodeJS HTTP library
RewriteCond "%{HTTP_USER_AGENT}" "^Dart/\d+\.\d+ \(dart:io\)$" [OR]
# python-requests, a Python HTTP library
RewriteCond "%{HTTP_USER_AGENT}" "^python-requests/" [OR]
# Empty user agents
RewriteCond "%{HTTP_USER_AGENT}" "^$"
RewriteRule "." "-" [F]

# More than 20k tile requets per day but website is not public (looks like for-charge service)
RewriteCond "%{HTTP_REFERER}" "//tapiagps\.mx/" [OR]
RewriteCond "%{HTTP_REFERER}" "//rw.tideen.com:38172/" [OR]
RewriteCond "%{HTTP_REFERER}" "//live1.trackandsnap.com/" [OR]
RewriteCond "%{HTTP_REFERER}" "//utysmpo.uzgps.uz/?" [OR]
RewriteCond "%{HTTP_REFERER}" "//tfc-colector.flash-its.eu/?" [OR]
# More than 60k tile requets per day but website is commercial (but open to public)
RewriteCond "%{HTTP_REFERER}" "//www.flatlooker.com/?"
# More than 40k tile requets, commercial asset tracking
RewriteCond "%{HTTP_REFERER}" "//glogist.ru/?"
# More than 10k tile requets per day but website is not public (looks like for-charge service)
RewriteCond "%{HTTP_REFERER}" "//servidormapa.com/?" [OR]
RewriteCond "%{HTTP_REFERER}" "//gps.sharpsoftco.com/?" [OR]
RewriteCond "%{HTTP_REFERER}" "//199.203.232.80/?" [OR]
# Requests with 12 years old Safari on iPad. More than 158k requests on a single day.
RewriteCond expr "%{REMOTE_ADDR} -ipmatch '85.214.47.106'" [OR]
# More than 190k tile request per IP, most requests with openrailwaymap.org referer, some with Internet Explorer 7 and no referrer
# Requests with referer requested zoom level 14 only.
RewriteCond expr "%{REMOTE_ADDR} -ipmatch '158.181.72.225'" [OR]
RewriteCond expr "%{REMOTE_ADDR} -ipmatch '158.181.73.249'" [OR]
# More than 20k tile request per IP and day but strange user agents and no referers
RewriteCond "%{HTTP_USER_AGENT}" "Mozilla/4.7[35]"
## Requests with invalid URLs (missing style name), 300k requests per day, user-agent is a Samsung TV
#RewriteCond expr "%{REMOTE_ADDR} -ipmatch '185.109.16.136'" [OR]
#RewriteCond expr "%{REMOTE_ADDR} -ipmatch '185.109.16.135'"
RewriteRule "." "-" [R=429,L]

## Monitoring tool doing test requests every second for three map styles
#RewriteCond "%{HTTP_USER_AGENT}" "SynxHealthTest"
#RewriteRule "." "-" [R=429,L]

ErrorLog {{ apache2_logdir }}/{{ tileserver.hostname }}.error.log
CustomLog {{ apache2_logdir }}/{{ tileserver.hostname }}.access.log combined
