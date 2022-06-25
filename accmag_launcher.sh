#! /bin/sh
# accmag_launcher.sh

mkdir /tmp/accmag_log
sudo chmod 755 /tmp/accmag_log
sudo python /home/pi/scripts/raspi_acc_mag.py >> /tmp/accmag_log/accmag_log-$(date +"%y-%m-%d-%T").txt
