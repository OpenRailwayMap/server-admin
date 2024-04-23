ServerName {{ api_hostname }}
DocumentRoot {{ website_dir }}

ProxyPass /server-status !

ProxyPass /timestamp !
Alias "/timestamp" "/nvme/data/timestamp.txt"
Alias "/v2/timestamp" "/nvme/data/timestamp.txt"
Header set Access-Control-Allow-Origin "*"
<location /timestamp>
    ForceType text/plain
    Require all granted
</location>
<location /v2/timestamp>
    ForceType text/plain
    Require all granted
</location>

{% if 'letsencrypt' in group_names %}
ProxyPass /.well-known !
{% endif %}

RewriteEngine on
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

# This IP appears with referer web.alarmmonitor.de on the tile server. On the API vhost, all requests end with status 408.
RewriteCond expr "%{REMOTE_ADDR} -ipmatch '80.153.203.81'" [OR]
RewriteCond expr "%{REMOTE_ADDR} -ipmatch '195.192.216.10'"
RewriteRule "." "-" [R=429,L]

ProxyPass /v2 !
WSGIScriptAlias /v2 /opt/OpenRailwayMap-api/api.py
WSGIProcessGroup api_v2

<Location /v2>
    Require all granted
</Location>

ProxyPreserveHost On
ProxyPass / http://localhost:9002/
ProxyPassReverse / http://localhost:9002/

ErrorLog {{ apache2_logdir }}/api.openrailwaymap.org.error.log
{% if 'letsencrypt' in group_names %}
LogLevel info ssl:warn
{% endif %}
CustomLog {{ apache2_logdir }}/api.openrailwaymap.org.access.log combined
