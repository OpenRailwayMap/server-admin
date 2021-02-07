ServerName {{ api_hostname }}
DocumentRoot {{ website_dir }}

ProxyPass /server-status !

ProxyPass /timestamp !
Alias "/timestamp" "/nvme/data/timestamp.txt"
Header set Access-Control-Allow-Origin "*"
<location /timestamp>
    ForceType text/plain
    Require all granted
</location>

{% if 'letsencrypt' in group_names %}
ProxyPass /.well-known !
{% endif %}

ProxyPreserveHost On
ProxyPass / http://localhost:9002/
ProxyPassReverse / http://localhost:9002/

ErrorLog {{ apache2_logdir }}/api.openrailwaymap.org.error.log
LogLevel info ssl:warn
CustomLog {{ apache2_logdir }}/api.openrailwaymap.org.access.log combined
