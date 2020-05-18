# Configuring server

## Install Nginx
Start with AWS Lightsail Ubuntu 18.04 LTS

`sudo apt update`
`sudo apt upgrade`
`sudo apt install nginx`

## Configure domain name
Check public IP address in browser (HTTP).
In Lightsail > Networking, add static IP address to server.
Check static IP address in browser (HTTP).
In AWS > Route53 > Hosted Zone for ianwdavis.com,
create an `A` record for happyhour.ianwdavis.com pointing to the static IP.
Wait for this to take effect -- may be a few minutes.
Confirm new domain name in browser (HTTP).

## Configure SSL
`sudo apt install python3-certbot-nginx`
`sudo vim /etc/nginx/sites-available/default`
Modify `server_default` line to `happyhour.ianwdavis.com`
`sudo certbot --nginx -d happyhour.ianwdavis.com`
Test to make sure auto-renewal is working: `sudo certbot renew --dry-run`

## Configure SSH
In `~/.ssh/config`:
```
Host happyhour
HostName happyhour.ianwdavis.com
User ubuntu
IdentityFile ~/.ssh/LightsailDefaultKey-us-east-1.pem
```

## Push code
Remote: `git init --bare happyhour.git`
Local: `git remote add origin ssh://happyhour/home/ubuntu/happyhour.git`
Local: `git push --set-upstream origin master`

Remote:
```
git clone happyhour.git/ happyhour
cd happyhour
sudo apt install python3-pip
sudo pip3 install -r requirements.txt
python3 server.py
```

## Configure Nginx as reverse proxy

Resources:
- https://flask-socketio.readthedocs.io/en/latest/#using-nginx-as-a-websocket-reverse-proxy
- https://docs.aiohttp.org/en/stable/deployment.html#nginx-configuration
- https://www.nginx.com/blog/websocket-nginx/

In `/etc/nginx/sites-available/default`, at the top level:
```
map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
}

upstream aiohttp {
        server 127.0.0.1:26614 max_fails=0;
}
```

Inside the `server` block:
```
        location / {
                include proxy_params;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection $connection_upgrade;
                proxy_redirect off;
                proxy_buffering off;
                proxy_pass http://aiohttp;
        }
```

In `/etc/nginx/nginx.conf`:
```
gzip off;
```

Having `gzip on` leads to lots of 400 errors with WebSockets!

Test config: `sudo nginx -t`
Restart: `sudo systemctl restart nginx`

## Make Python start automatically

`sudo apt install monit`

In `/etc/monit/monitrc`, uncomment:
```
set httpd port 2812 and
    use address localhost  # only accept connection from localhost
    allow localhost        # allow localhost to connect to the server and
```
and do `sudo monit reload; sudo monit status`.

Write `/etc/monit/conf-available/happyhour`:
```
 check process happyhour with pidfile /var/run/happyhour.pid
   start program = "/home/ubuntu/happyhour/happyhour.sh start"  #as uid "ubuntu" and gid "ubuntu"
   stop program = "/home/ubuntu/happyhour/happyhour.sh stop"  #as uid "ubuntu" and gid "ubuntu"
```

Symbolic link to `/etc/monit/conf-enabled/happyhour`
and run `sudo monit reload; sudo monit status`.

## Take 2

Can't make Monit work properly (without a pid file?).

`nohup python3 server.py &`