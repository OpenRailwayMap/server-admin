    ServerName {{ mail.http_hostname }}    
    <Directory /var/lib/mailman/archives/>
        Options FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
    <Directory /usr/share/images/mailman/>
        AllowOverride None
        Require all granted
    </Directory>
    
    Alias /pipermail/ /var/lib/mailman/archives/public/
    Alias /archives/ /var/lib/mailman/archives/public/
    Alias /images/mailman/ /usr/share/images/mailman/
    
    RedirectMatch ^/mailman[/]*$ /mailman3
    # redirect people following links into the somehow correct direction
    RedirectMatch ^/listinfo$ /mailman3

    <Location /mailman>
        RewriteEngine On
        RewriteRule "^/mailman/listinfo/([^/]+)/?$" "/mailman3/postorius/lists/$1.openrailwaymap.org/" [R=302]
    </Location>
    
    ErrorLog {{ apache2_logdir }}/{{ mail.http_hostname }}.error.log
    LogLevel info ssl:warn tile:warn
    CustomLog {{ apache2_logdir }}/{{ mail.http_hostname }}.access.log combined
