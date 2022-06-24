# Raspi_GPS_CAN_acc_mag
Raspberry PI-hez csatlakoztatott GPS, CAN, accelerometer, magnetometer modulok adatai influxDB-be


Raspberry PI config:
OS: Raspberry PI OS Lite (64-bit) (headless)
hostname: telemetpi
username: pi
pwd: uszikAhajo!
network config: Ethernet; Bakonyi mobilnet hotspot (SSID: G5_8658 pwd: nemmondommeg:P)
Installed modules: 
-	python3
-	idle3 
-	pip

For installed python libraries: -> see below

Location of scripts: /home/pi/scripts
-	raspi_gps.py <- sending GPS data from NEO-M9N to influxDB
-	raspi_acc_mag.py <- sending acceleration, magnetic field data from LSM303d to influxDB

Run scripts after boot:
	crontab: 
@reboot sudo python /home/pi/scripts/raspi_gps.py
@reboot sudo python /home/pi/scripts/raspi_acc_mag.py

Linux webserver config:
hostname: influx.solarboatteam.hu 
IP: 159.223.24.39
username: sbt
pwd: kérdezd meg Magyar Mátét

InfluxDB config:
install mode: docker
container ID: 243c548a0249 
influx GUI: http://influx.solarboatteam.hu:8086 
username: admin
pwd: kérdezd meg Magyar Mátét
buckets (databases): 
-	sbt (ID: de434eeb1358699e) Retention: 7 days
-	lana (ID: 9f55909d46f827ec) Retention: 7 days
Ennél hosszabb retentiont nem tudok adni, mert a következő hibaüzenetet kapom: Failed to update bucket: "shard-group duration must also be updated to be smaller than new retention duration" 
Majd ha lesz rá időm utánaolvasok jobban, hogy ez mi a tosz. Vagy új bucketet csinálok.
API tokens:
-	admin’s Token -> permissions: all (8WjcfKiq7otthk5XjhFokcI8Ll37ni_GyGBJ4KjYZt2LE34NDsfm_wRqdBKnexFcYSXkk2d28Xr2p0PZk-1quA==)
-	lana_token -> permisiions: buckets-lana (read, write)
(APPLVlMGyeWeKoRhipR-1ULSX5mtduugSWo2jDTbXyDinF1TyahGU9smvMOkSwrP0TdYv6VIVEm7jcLosozZUg==)

Grafana config:
install mode: docker
container ID: d11f3bdda3d9 



Installed python libraries:
pi@telemetpi:~/scripts $ pip list
Package            Version
------------------ ---------
arandr             0.1.10
astroid            2.5.1
asttokens          2.0.4
automationhat      0.2.0
beautifulsoup4     4.9.3
blinker            1.4
blinkt             0.1.2
buttonshim         0.0.2
Cap1xxx            0.1.3
certifi            2020.6.20
chardet            4.0.0
click              7.1.2
colorama           0.4.4
colorzero          1.1
cryptography       3.3.2
cupshelpers        1.0
dbus-python        1.2.16
distro             1.5.0
docutils           0.16
drumhat            0.1.0
envirophat         1.0.0
ExplorerHAT        0.4.2
Flask              1.1.2
fourletterphat     0.1.0
gpio               0.3.0
gpiozero           1.6.2
html5lib           1.1
i2cdev             1.2.4
i2cdevice          0.0.7
idna               2.10
influxdb           5.3.1
influxdb-client    1.29.1
isort              5.6.4
itsdangerous       1.1.0
jedi               0.18.0
Jinja2             2.11.3
lazy-object-proxy  0.0.0
logilab-common     1.8.1
lsm303d            0.0.5
lxml               4.6.3
MarkupSafe         1.1.1
mccabe             0.6.1
microdotphat       0.2.1
mote               0.0.4
motephat           0.0.3
msgpack            1.0.4
mypy               0.812
mypy-extensions    0.4.3
numpy              1.19.5
oauthlib           3.1.0
olefile            0.46
pantilthat         0.0.7
parso              0.8.1
pexpect            4.8.0
pgzero             1.2
phatbeat           0.1.1
pianohat           0.1.0
piglow             1.2.5
pigpio             1.78
Pillow             8.1.2
pip                20.3.4
psutil             5.8.0
pycairo            1.16.2
pycups             2.0.1
pygame             1.9.6
Pygments           2.7.1
PyGObject          3.38.0
pyinotify          0.9.6
PyJWT              1.7.1
pylint             2.7.2
pyOpenSSL          20.0.1
pyserial           3.5b0
pysmbc             1.0.23
python-apt         2.2.1
python-dateutil    2.8.2
pytz               2022.1
rainbowhat         0.1.0
reportlab          3.5.59
requests           2.25.1
requests-oauthlib  1.0.0
responses          0.12.1
roman              2.0.0
RPi.GPIO           0.7.0
RTIMULib           7.2.1
Rx                 3.2.0
scrollphat         0.0.7
scrollphathd       1.2.1
Send2Trash         1.6.0b1
sense-hat          2.2.0
setuptools         52.0.0
simplejson         3.17.2
six                1.16.0
skywriter          0.0.7
smbus              1.1.post2
sn3218             1.2.7
soupsieve          2.2.1
sparkfun-ublox-gps 1.1.4
spidev             3.5
ssh-import-id      5.10
thonny             3.3.14
toml               0.10.1
touchphat          0.0.1
twython            3.8.2
typed-ast          1.4.2
typing-extensions  3.7.4.3
unicornhathd       0.0.4
urllib3            1.26.5
webencodings       0.5.1
Werkzeug           1.0.1
wheel              0.34.2
wrapt              1.12.1
