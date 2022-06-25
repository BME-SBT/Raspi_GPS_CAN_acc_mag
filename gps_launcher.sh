#! /bin/sh
# gps_launcher.sh

mkdir /tmp/gps_log
sudo chmod 755 /tmp/gps_log
sudo python /home/pi/scripts/raspi_gps.py >> /tmp/gps_log/gps_log-$(date +"%y-%m-%d-%T").txt
