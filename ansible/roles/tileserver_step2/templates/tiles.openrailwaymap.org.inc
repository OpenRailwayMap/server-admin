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
# more than 20k tile requets per day, website is not public
# Responding with HTTP status 429 for multiple weeks did not make this client to go away.
RewriteCond "%{HTTP_REFERER}" "//live1.trackandsnap.com/" [OR]
RewriteCond "%{HTTP_REFERER}" "//utysmpo\.uzgps.uz/?" [OR]
# More than 20k tile requets per day but website is not public (looks like for-charge service)
RewriteCond "%{HTTP_REFERER}" "//(www\.)?geliospro\.com/" [OR]
# More than 60k tile requets per day but website is commercial (but open to public)
RewriteCond "%{HTTP_REFERER}" "//www.flatlooker.com/?" [OR]
# More than 20k tile requets per day but website is not public (looks like for-charge service)
RewriteCond "%{HTTP_REFERER}" "//gps.sharpsoftco.com/?" [OR]
# More than 10k tile requets per day but website is not public (looks like for-charge service)
RewriteCond "%{HTTP_REFERER}" "//servidormapa.com/?" [OR]
RewriteCond "%{HTTP_REFERER}" "//gps\.teambyte\.al/" [OR]
# More than 20k tile requets per day but website is not public (looks like for-charge service)
RewriteCond "%{HTTP_REFERER}" "//libellule\.sudcontractors\.com/?" [OR]
RewriteCond "%{HTTP_REFERER}" "//sc-libellule\.com/?" [OR]
# More than 70k tile requets, commercial asset tracking
RewriteCond "%{HTTP_REFERER}" "//glogist.ru/?" [OR]
# Lacking attribution and more than 10k tile requests per day
RewriteCond "%{HTTP_REFERER}" "//fow\.vicc\.wang/?" [OR]
# SEO website with ads and no meaningful content after a rough review (no HTTP 429 prior to black tile response)
RewriteCond "%{HTTP_REFERER}" "//zugradar.info/"
RewriteRule "." "/tile-util/black.png" [PT]

# Lacking attribution and high traffic, friendly attribution tile as response
# 100k tile requets per day for public realtime tracking of BDZ trains, lacking attribution
RewriteCond "%{HTTP_REFERER}" "//radar\.bdz\.bg/"
RewriteRule "." "/tile-util/attribution-tile.png" [PT]

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
# python-requests, a Python HTTP library
RewriteCond "%{HTTP_USER_AGENT}" "^MOBAC/" [OR]
# Wget, non-interactive network downloader
RewriteCond "%{HTTP_USER_AGENT}" "^Wget/" [OR]
# Go HTTP client
RewriteCond "%{HTTP_USER_AGENT}" "^Go-http-client/" [OR]
# Empty user agents
RewriteCond "%{HTTP_USER_AGENT}" "^$"
RewriteRule "." "-" [F]

# More than 10k tile requets per day but website is not public (looks like for-charge service)
RewriteCond "%{HTTP_REFERER}" "//www\.transferoviarcalatori\.ro/?" [OR]
# More than 20k tile requets per day but website is not public (looks like for-charge service)
RewriteCond "%{HTTP_REFERER}" "//tapiagps\.mx/" [OR]
RewriteCond "%{HTTP_REFERER}" "//atlas2\.org/" [OR]
# More than 10k tile requets per day but website is not public (looks like for-charge service)
# More than 190k tile request per IP (sometimes more then 300k requests per day) from TeleColumbus subnet, most requests with openrailwaymap.org referer, some with Internet Explorer 7 and no referrer
# Requests with referer requested zoom level 13 or 14 only. 2023-10
RewriteCond expr "%{REMOTE_ADDR} -ipmatch '158.181.72.225'" [OR]
RewriteCond expr "%{REMOTE_ADDR} -ipmatch '158.181.73.177'" [OR]
RewriteCond expr "%{REMOTE_ADDR} -ipmatch '158.181.73.249'" [OR]
# More than 20k tile requets per 14 hours
RewriteCond expr "%{REMOTE_ADDR} -ipmatch '80.156.193.26'" [OR]
# Jiangmen Global Eyes Police Bureau, 16k requests per 10 hours
RewriteCond expr "%{REMOTE_ADDR} -ipmatch '219.130.135.190'" [OR]
# Korean IP, 550k requests per 10 hours, many IE7, 2023-10-17
RewriteCond expr "%{REMOTE_ADDR} -ipmatch '59.31.87.129'" [OR]
# Korean IP, 122k requests per 18 hours, many IE7, 2024-0423-
RewriteCond expr "%{REMOTE_ADDR} -ipmatch '213.121.90.57'" [OR]
# More than 20k tile request per IP and day but strange user agents and no referers
RewriteCond "%{HTTP_USER_AGENT}" "Mozilla/4.7[35]"
RewriteRule "." "-" [R=429,L]

# Monitoring tool doing test requests every second for three map styles
# Running on a DB IP, therefore difficult to ban
RewriteCond "%{HTTP_USER_AGENT}" "SynxHealthTest"
RewriteRule "." "-" [R=429,L]

ErrorLog {{ apache2_logdir }}/{{ tileserver.hostname }}.error.log
CustomLog {{ apache2_logdir }}/{{ tileserver.hostname }}.access.log combined
