#!/bin/bash

cd ~/scrader;
git commit -a -m 'a'
git push
ssh root@146.185.138.240 <<'ENDSSH'
cd ~/scrader_mock
kill -9 `ps -ef | grep scrader_server.py | awk '{print $2}' | sed -n 1p`
git pull
ENDSSH
#python scrader_server.py </dev/null >/var/log/root-backup.log 2>&1 &

