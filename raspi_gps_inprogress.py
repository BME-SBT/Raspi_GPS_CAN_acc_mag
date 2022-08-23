#! /usr/bin/env python3

# BME Solar Boat Team 2022
# Boat name: Lana
# Responsible for code: BM

# on Raspberry PI 4
# Sends GPS coordinates and heading of motion from GPS module to influxDB
# GPS module: u-blox NEO-M9N
# Connected to Raspberry PI via serial port


from ublox_gps import UbloxGps
import serial
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np
import logging
import time

# Logging setup
log_format = '%(asctime)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)
logger = logging.getLogger()
logger.setLevel('INFO')
timestr = time.strftime("%Y%m%d_%H%M")
logfilename = "GPS_log_" + timestr + ".log"
handler = logging.FileHandler(logfilename)
handler.setFormatter(formatter)
logger.addHandler(handler)

# sets the connection with GPS module
# to check which serial port is connected to GPS module run: ls -la /dev/serial/by-id 
port = serial.Serial('/dev/ttyGPS', baudrate=38400, timeout=1) # change ttyGPS if neccessary
gps = UbloxGps(port)

# Sets the variables of the influxDB (You can generate an API token from the "API Tokens Tab" in the UI)
token = "" # lana_token
org = "sbt"
bucket = "lana" # database

# sends given data to influxDB which is set in function
def send2influx(msg2send):
    with InfluxDBClient(url=, token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket, org, msg2send)


# contiounusly checks six GPS signal, weather they are close to each other (in 0.02 range) or not 
def gps_verify():
  gpslat_probes = [0, 1, 2, 3, 4, 5]
  gpslon_probes = [0, 1, 2, 3, 4, 5]
  geo = gps.geo_coords()
  while True: # ez így loopban megy, nem biztos, hogy a legjobb megoldás?
     for x in range(6):
        gpslat_probes[x] = round(geo.lat,2)
        gpslon_probes[x] = round(geo.lon,2)
        if gpslat_probes[0] in np.arange(gpslat_probes[1]-0.01, gpslat_probes[1]+0.02,0.01) and gpslat_probes[1] in np.arange(gpslat_probes[2]-0.01, gpslat_probes[2]+0.02,0.01) and gpslat_probes[2] in np.arange(gpslat_probes[3]-0.01, gpslat_probes[3]+0.02,0.01) and gpslat_probes[3] in np.arange(gpslat_probes[4]-0.01, gpslat_probes[4]+0.02,0.01) and gpslat_probes[4] in np.arange(gpslat_probes[5]-0.01, gpslat_probes[5]+0.02,0.01):
            if gpslon_probes[0] in np.arange(gpslon_probes[1]-0.01, gpslon_probes[1]+0.02,0.01) and gpslon_probes[1] in np.arange(gpslon_probes[2]-0.01, gpslon_probes[2]+0.02,0.01) and gpslon_probes[2] in np.arange(gpslon_probes[3]-0.01, gpslon_probes[3]+0.02,0.01) and gpslon_probes[3] in np.arange(gpslon_probes[4]-0.01, gpslon_probes[4]+0.02,0.01) and gpslon_probes[4] in np.arange(gpslon_probes[5]-0.01, gpslon_probes[5]+0.02,0.01):
              return True
            else:
              return False # meg kell csinálni, hogy logba és/vagy influxba küldjön hibaüzit ekkor!!!!

            

def run():

    try:
        while True:
            try:
                geo = gps.geo_coords()

                if geo.lon == 0.0 and geo.lat == 0.0:
                    gps_err = "GPS pozicio 0, valoszinuleg nincs GPS jel, nezd meg a kek PPS LED vilagit-e"
                    gps_err_msg = Point("GPS Error") \
                      .tag("sensor", "sparkfun ublox NEO-M9N") \
                      .field("Error message", gps_err) \
                      .time(datetime.utcnow(), WritePrecision.NS)
                    send2influx(gps_err_msg)
                
                if geo.lon != 0.0 and geo.lat != 0.0 and geo.headMot == 0.0:
                    gps_err = "Van GPS jel, de nem halad a hajo:OOO"
                    gps_err_msg = Point("GPS Error") \
                      .tag("sensor", "sparkfun ublox NEO-M9N") \
                      .field("Error message", gps_err) \
                      .time(datetime.utcnow(), WritePrecision.NS)
                    send2influx(gps_err_msg)
                
                
                gps_coords = Point("GPS coordinates") \
                  .tag("sensor", "sparkfun ublox NEO-M9N") \
                  .field("Longitude", geo.lon) \
                  .field("Latitude", geo.lat) \
                  .time(datetime.utcnow(), WritePrecision.NS)
                
                heading = Point("heading") \
                  .tag("sensor", "sparkfun ublox NEO-M9N") \
                  .field("Heading of Motion", geo.headMot) \
                  .time(datetime.utcnow(), WritePrecision.NS)
                
                lana_gps = []
                lana_gps.append([gps_coords, heading])
                
                send2influx(lana_gps)
                    
                    
            except (ValueError, IOError) as err:
#                print(err) # logba kell kiírni
                com_err_msg = Point("GPS module comm Error") \
                  .tag("sensor", "sparkfun ublox NEO-M9N") \
                  .field("Communication Error message", err) \
                  .time(datetime.utcnow(), WritePrecision.NS)
                send2influx(com_err_msg)
                 

    finally:
        port.close()


if __name__ == '__main__':
  # if six GPS signals are in 0.02 range it enables to run the 'run' function
    while gps_verify() == True: # folyamatosan chekkel (remélem)
        run()
