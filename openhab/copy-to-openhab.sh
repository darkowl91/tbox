#!/bin/bash

HOST=10.6.203.1

echo "...copy opnehab2 dir"
scp -r ~/Projects/tbox/openhab/openhab2/* pi@$HOST:/etc/openhab2/
