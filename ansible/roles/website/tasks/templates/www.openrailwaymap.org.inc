    DocumentRoot {{ website_dir }}
    ServerName {{ website_hostname }}
    {% for host_alias in website_hostname_aliases -%}
    ServerAlias {{ host_alias }}
    {% endfor %}

    <Directory {{ website_dir }}>
        AllowOverride None
    </Directory>

    AddType application/json .json

    # alias for imprint
    Alias /de/imprint {{website_dir}}/imprint-de.html
    Alias /en/imprint {{website_dir}}/imprint-en.html

    # language redirection for imprint page
    RewriteEngine On
    RewriteCond %{REQUEST_URI} ^/imprint$
    RewriteCond %{HTTP:Accept-Language} ^de[-,;].*$ [NC]
    RewriteRule ^/imprint$ /imprint-de.html [L,R=307]
    RewriteCond %{HTTP:Accept-Language} ^en[-,;].*$ [NC]
    RewriteRule ^/imprint$ /imprint-en.html [L,R=307]
    RewriteCond %{HTTP:Accept-Language} [,;]de[-,;].*$ [NC]
    RewriteRule ^/imprint$ /imprint-de.html [L,R=307]
    RewriteCond %{HTTP:Accept-Language} [,;]en[-,;].*$ [NC]
    RewriteRule ^/imprint$ /imprint-en.html [L,R=307]

    ErrorLog {{ apache2_logdir }}/{{ website_hostname }}.error.log
{% if 'letsencrypt' in group_names %}
    LogLevel info ssl:warn
{% endif %}
    CustomLog {{ apache2_logdir }}/{{ website_hostname }}.access.log combined

    DirectoryIndex index.php
