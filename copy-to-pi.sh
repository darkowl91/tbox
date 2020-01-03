#!/bin/bash

HOST=10.6.203.1

echo "...copy opnehab2 dir"
scp -r ~/Projects/tbox/openhab2/* pi@$HOST:/etc/openhab2/

echo "...copy tbot dir"
scp -r ~/Projects/tbox/tbot/* pi@$HOST:/home/pi/tbot/

