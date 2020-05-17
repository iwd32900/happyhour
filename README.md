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
Remote: `git clone happyhour.git/ happyhour`