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

    # No account signup or anything other for users from Tor and spam hosters (reading archives still permitted)
    <Location /mailman3>
        <Limit POST >
	    <RequireAll>
                Require all granted
		# Tor
		Require not ip 77.247.181.160/28
		Require not ip 85.248.227.160/28
                Require not ip 91.192.103.4/30
                Require not ip 91.192.103.8/29
                Require not ip 91.192.103.16/28
                Require not ip 91.192.103.32/27
                Require not ip 91.192.103.64/27
                Require not ip 91.192.103.96/28
		Require not ip 162.247.72.0/22
                Require not ip 185.220.100.0/22
                Require not ip 185.121.69.0/24

		# Other spammers
		# Multiple signups from various hosts in this network
		Require not ip 31.220.40.0/23
		Require not ip 199.249.230.0/24
		# AS43350, NForce Entertainment BV, shady
		Require not ip 77.247.176.0/21
		Require not ip 185.56.80.0/24
		Require not ip 185.107.68.0/22
		# AS51852, Private Layer, located in Panama but servers in Switzerland
		Require not ip 179.43.128.0/18
		# AS16276, OVH, not known for good abuse handling, sorry for VPN users using this hoster
		Require not ip 51.38.0.0/16
		Require not ip 51.68.212.0/22
                Require not ip 51.77.148.0/22
		Require not ip 51.91.0.0/16
                Require not ip 51.195.100.0/22
                Require not ip 51.210.0.0/16
		Require not ip 145.239.0.0/16

		# Temporary blocks
		# 2021-01-14, spamming for a couple of days
		Require not ip 95.211.230.211
	    </RequireAll>
        </Limit>
    </Location>
    
    ErrorLog {{ apache2_logdir }}/{{ mail.http_hostname }}.error.log
    LogLevel info ssl:warn tile:warn
    CustomLog {{ apache2_logdir }}/{{ mail.http_hostname }}.access.log combined
