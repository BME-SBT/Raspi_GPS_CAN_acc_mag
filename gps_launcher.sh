#! /bin/sh
# gps_launcher.sh

sudo python /home/pi/scripts/raspi_gps.py

# [Unit]
# Description=GPS launcher
# After=network.target

# [Service]
# ExecStart=/usr/bin/python3 /home/pi/scripts/raspi_gps.py
# Restart=always

# [Install]
# WantedBy=multi-user.target
