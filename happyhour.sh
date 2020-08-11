#!/bin/bash
case $1 in
    start)
       #echo $$ > /var/run/happyhour.pid;
       #exec 2>&1 /usr/bin/python3 /home/ubuntu/happyhour/server.py 1>/tmp/happyhour.out
       /home/ubuntu/happyhour/venv/bin/python3 /home/ubuntu/happyhour/server.py &> /tmp/happyhour.out &
       echo $! > /var/run/happyhour.pid
       ;;
    stop)
        kill `cat /var/run/happyhour.pid` ;;
    *)
        echo "usage: happyhour {start|stop}" ;;
esac
exit 0
