#!/bin/bash

sudo -u ubuntu bash << EOF
cd /home/ubuntu/

export PATH=/home/ubuntu/miniconda3/bin:$PATH

export SECRET_KEY=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 16)

cd /home/ubuntu/pannotia/
git pull
gunicorn --bind 127.0.0.1:6000 --workers 5 -t 600 dashboard.wsgi:app 1>>/home/ubuntu/flask.out 2>>/home/ubuntu/flask.err &
disown
EOF
