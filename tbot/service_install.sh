#!/bin/bash

sudo cp tBot.service /etc/systemd/system/tBot.service

echo "...start service"
sudo systemctl start tBot.service
