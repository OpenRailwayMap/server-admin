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
    Alias /images/mailman/ /usr/share/images/mailman/
    ScriptAlias /admin /usr/lib/cgi-bin/mailman/admin
    ScriptAlias /admindb /usr/lib/cgi-bin/mailman/admindb
    ScriptAlias /confirm /usr/lib/cgi-bin/mailman/confirm
    ScriptAlias /create /usr/lib/cgi-bin/mailman/create
    ScriptAlias /edithtml /usr/lib/cgi-bin/mailman/edithtml
    ScriptAlias /listinfo /usr/lib/cgi-bin/mailman/listinfo
    ScriptAlias /options /usr/lib/cgi-bin/mailman/options
    ScriptAlias /private /usr/lib/cgi-bin/mailman/private
    ScriptAlias /rmlist /usr/lib/cgi-bin/mailman/rmlist
    ScriptAlias /roster /usr/lib/cgi-bin/mailman/roster
    ScriptAlias /subscribe /usr/lib/cgi-bin/mailman/subscribe
    ScriptAlias /mailman/ /usr/lib/cgi-bin/mailman/
    
    RedirectMatch ^/mailman[/]*$ /mailman/listinfo
    RedirectMatch ^/$ /listinfo
    
    ErrorLog {{ apache2_logdir }}/{{ mail.http_hostname }}.error.log
    LogLevel info ssl:warn tile:warn
    CustomLog {{ apache2_logdir }}/{{ mail.http_hostname }}.access.log combined
