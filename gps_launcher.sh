#! /bin/sh
# gps_launcher.sh

sudo python /home/pi/scripts/raspi_gps.py

# [Unit]
# Description=GPS launcher
# After=network.target

# [Service]
# ExecStart=/usr/bin/python3 /home/pi/scripts/Raspi_GPS_CAN_acc_mag/raspi_gps.py
# Restart=on-failure
# RestartSec=5s

# [Install]
# WantedBy=multi-user.target
