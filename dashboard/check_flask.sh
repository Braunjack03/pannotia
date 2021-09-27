#!/bin/bash

echo "checking gunicorn"

lsof -i -P -n | grep LISTEN | grep -q :6000
rc=$?
if [[ $rc != 0 ]]
then
    echo "restarting gunicorn"
    bash /home/ubuntu/panthalassa/leads/startup.sh
fi
