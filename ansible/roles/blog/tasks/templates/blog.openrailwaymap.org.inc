    DocumentRoot {{ blog.directory }}
    ServerName {{ blog.hostname }}
    {% for host_alias in blog.hostname_aliases -%}
    ServerAlias {{ host_alias }}
    {% endfor %}

    <Directory {{ blog.directory }}>
        AllowOverride None
    </Directory>

    AddType application/json .json

    ErrorLog {{ apache2_logdir }}/{{ blog.hostname }}.error.log
    LogLevel info
    CustomLog {{ apache2_logdir }}/{{ blog.hostname }}.access.log combined

    DirectoryIndex index.php
