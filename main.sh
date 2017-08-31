#!/bin/bash

nohup python ./appWatcher.py >/dev/null 2>&1 &
python ./DDNSServer.py >/tmp/DDNSServer.log
sleep 30d