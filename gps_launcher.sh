#! /bin/sh
# gps_launcher.sh

sudo python /home/pi/scripts/raspi_gps.py

#root@bmraspizero:/etc/systemd/system# cat GPS_launcher.service
# [Unit]
# Description=GPS launcher
# After=network.target

# [Service]
# ExecStart=/usr/bin/python3 /home/pi/scripts/Raspi_GPS_CAN_acc_mag/raspi_gps.py
# Restart=on-failure
# RestartSec=5s

# [Install]
# WantedBy=multi-user.target
