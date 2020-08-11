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

## Configure SSH
In `~/.ssh/config`:
```
Host happyhour
HostName happyhour.ianwdavis.com
User ubuntu
IdentityFile ~/.ssh/LightsailDefaultKey-us-east-1.pem
```

## Push code

```
git clone https://github.com/iwd32900/happyhour.git
cd happyhour
sudo apt install python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
mkdir static
python3 server.py
```

## Configure Nginx as reverse proxy

Resources:
- https://flask-socketio.readthedocs.io/en/latest/#using-nginx-as-a-websocket-reverse-proxy
- https://docs.aiohttp.org/en/stable/deployment.html#nginx-configuration
- https://www.nginx.com/blog/websocket-nginx/

```
cd /etc/nginx/sites-enabled/
sudo ln -s ~/happyhour/happyhour.nginx
```

In `/etc/nginx/nginx.conf`:
```
gzip off;
```
Having `gzip on` leads to lots of 400 errors with WebSockets!

Test config: `sudo nginx -t`
Restart: `sudo systemctl restart nginx`

## Configure SSL
`sudo apt install python3-certbot-nginx`
`sudo certbot --nginx -d happyhour.ianwdavis.com`
Test to make sure auto-renewal is working: `sudo certbot renew --dry-run`

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

The thing that took me forever was to figure out that `happyhour.sh`
had to start the server **as a background process**.
Otherwise, startup timed out, and Monit killed the process after 30 sec.

## Deploy updates

```
cd happyhour
git pull
pgrep -f happyhour    # optional
sudo monit restart happyhour
pgrep -f happyhour    # optional, should show different process ID
```

## Nginx log analysis

`sudo apt install goaccess`
`goaccess --log-format=COMBINED <(zcat -f /var/log/nginx/access.log*) --ignore-crawlers`

# TODO

- allow naming tables
- broadcast chat messages to all participants
- re-broadcast which room people are in periodically (to make sure things are in sync)
