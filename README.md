# Raspi_GPS_CAN_acc_mag
Raspberry PI-hez csatlakoztatott GPS modul adatait küldi ki influxDB-be

LÉtre kell hozni és kitölteni:
influxvars.txt
tartalma:
```
bucket_name
influx_url
inlfux_token
```

Raspberry PI:
OS: Raspberry PI OS Lite (64-bit) (headless)
hostname: telemetpi
username: pi
Installed modules: 
-	python3
-	idle3 
-	pip
-   pyserial
-   influxdb_client
-   sparkfun-ublox-gps

Location of scripts: /home/pi/scripts
-	raspi_gps.py <- sends GPS data from NEO-M9N to influxDB

Run scripts after boot -> GPS_launcher.service
in systemd (/etc/systemd/system/):

Linux webserver:
hostname: influx.solarboatteam.hu 
IP: 159.223.24.39
username: sbt
pwd: kérdezd meg Magyar Mátét

InfluxDB config:
install mode: docker
influx GUI: http://influx.solarboatteam.hu:8086 
username: admin
pwd: kérdezd meg Magyar Mátét
buckets (databases): 
-	sbt (ID: de434eeb1358699e) Retention: forever
-	lana (ID: 9f55909d46f827ec) Retention: forever

API tokens:
-	admin’s Token -> permissions: all (......)
-	lana_token -> permissions: buckets-lana (read, write)

USB config ttyGPS saját Raspin:

looking at parent device '/devices/platform/soc/3f980000.usb/usb1/1-1':
ATTRS{idProduct}=="01a9"
ATTRS{idVendor}=="1546"

SUBSYSTEM=="tty", ATTRS{idProduct}=="01a9", ATTRS{idVendor}=="1546", SYMLINK+="ttyGPS"

lrwxrwxrwx  1 root root           7 Jun 27 21:50 ttyGPS -> ttyACM0

