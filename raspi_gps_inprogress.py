#! /usr/bin/env python3

# BME Solar Boat Team 2022
# Boat name: Lana
# Responsible for code: bm971

# on Raspberry PI 4
# Sends GPS coordinates and heading of motion from GPS module to influxDB
# GPS module: Sparkfun u-blox NEO-M9N
# Connected to Raspberry PI via serial port


from ublox_gps import UbloxGps
import serial
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np
import time

import pathlib
scriptpath = pathlib.Path(__file__).parent.resolve()

# sets the connection with GPS module
# to check which serial port is connected to GPS module run: ls -la /dev/serial/by-id 
port = serial.Serial('/dev/ttyGPS', baudrate=38400, timeout=1) # change ttyGPS if neccessary
gps = UbloxGps(port)

# Sets the variables of the influxDB (You can generate an API token from the "API Tokens Tab" in the UI)
token = "" # lana_token
org = "sbt"
bucket = "lana" # database
tokenfile = open(scriptpath/".lana_token","r")
lana_token = str(tokenfile.read())
tokenfile.close()
urlfile = open(scriptpath/".lana_token","r")
influx_url = str(urlfile.read())
urlfile.close()

# sends given data to influxDB which is set in function
def send2influx(msg2send):
    with InfluxDBClient(url=influx_url, token=lana_token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket, org, msg2send)


# contiounusly checks six GPS signal in every second, weather they are close to each other (in 0.02 range) or not 
def gps_verify():
  gpslat_probes = [0, 1, 2, 3, 4, 5]
  gpslon_probes = [0, 1, 2, 3, 4, 5]
  geo = gps.geo_coords()
  while True: # ez így loopban megy, nem biztos, hogy a legjobb megoldás?
    for x in range(6): # contiounusly rotates the last six data, check in every rotation
        gpslat_probes[x] = round(geo.lat,2)
        gpslon_probes[x] = round(geo.lon,2)
        if gpslat_probes[0] in np.arange(gpslat_probes[1]-0.01, gpslat_probes[1]+0.02,0.01) and gpslat_probes[1] in np.arange(gpslat_probes[2]-0.01, gpslat_probes[2]+0.02,0.01) and gpslat_probes[2] in np.arange(gpslat_probes[3]-0.01, gpslat_probes[3]+0.02,0.01) and gpslat_probes[3] in np.arange(gpslat_probes[4]-0.01, gpslat_probes[4]+0.02,0.01) and gpslat_probes[4] in np.arange(gpslat_probes[5]-0.01, gpslat_probes[5]+0.02,0.01):
            if gpslon_probes[0] in np.arange(gpslon_probes[1]-0.01, gpslon_probes[1]+0.02,0.01) and gpslon_probes[1] in np.arange(gpslon_probes[2]-0.01, gpslon_probes[2]+0.02,0.01) and gpslon_probes[2] in np.arange(gpslon_probes[3]-0.01, gpslon_probes[3]+0.02,0.01) and gpslon_probes[3] in np.arange(gpslon_probes[4]-0.01, gpslon_probes[4]+0.02,0.01) and gpslon_probes[4] in np.arange(gpslon_probes[5]-0.01, gpslon_probes[5]+0.02,0.01):
              gps_err4 = 0 # GPS position is acceptable
              gps_err_msg4 = Point("GPS_Precison_Error") \
                      .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                      .field("Error_message", gps_err4) \
                      .time(datetime.utcnow(), WritePrecision.NS)
              send2influx(gps_err_msg4)
              return True
            else:
              gps_err4 = 1 # valami int vagy string amit a grafana feldogoz hibaüzenetként
              gps_err_msg4 = Point("GPS_Precison_Error") \
                      .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                      .field("Error_message", gps_err4) \
                      .time(datetime.utcnow(), WritePrecision.NS)
              send2influx(gps_err_msg4)
              return False
    time.sleep(1)

def run():
    try:
        while True:
            try:
                gps_err1 = 0 # Communication OK with GPS module
                gps_err_msg1 = Point("GPS_Comm_Error") \
                  .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                  .field("Error_message", gps_err1) \
                  .time(datetime.utcnow(), WritePrecision.NS)
                send2influx(gps_err_msg1)

                geo = gps.geo_coords()

                if geo.lon == 0.0 and geo.lat == 0.0:
                    gps_err2 = 1 # GPS pozicio 0, valoszinuleg nincs GPS jel, nezd meg a kek PPS LED vilagit-e
                    gps_err_msg2 = Point("GPS_Position_Error") \
                      .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                      .field("Error_message", gps_err2) \
                      .time(datetime.utcnow(), WritePrecision.NS)
                    send2influx(gps_err_msg2)
                else:
                    gps_err2 = 0 # van GPS jel
                    gps_err_msg2 = Point("GPS_Position_Error") \
                      .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                      .field("Error_message", gps_err2) \
                      .time(datetime.utcnow(), WritePrecision.NS)
                    send2influx(gps_err_msg2)
                
                if geo.lon != 0.0 and geo.lat != 0.0 and geo.headMot == 0.0:
                    gps_err3 = 1 # Van GPS jel, de nem halad a hajo:OOO
                    gps_err_msg3 = Point("GPS_Motion_Error") \
                      .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                      .field("Error_message", gps_err3) \
                      .time(datetime.utcnow(), WritePrecision.NS)
                    send2influx(gps_err_msg3)
                else:
                    gps_err3 = 0 # Van GPS jel, halad a hajo
                    gps_err_msg3 = Point("GPS_Motion_Error") \
                      .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                      .field("Error_message", gps_err3) \
                      .time(datetime.utcnow(), WritePrecision.NS)
                    send2influx(gps_err_msg3)
                
                gps_coords = Point("GPS_coordinates") \
                  .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                  .field("Longitude", geo.lon) \
                  .field("Latitude", geo.lat) \
                  .time(datetime.utcnow(), WritePrecision.NS)
                
                heading = Point("heading") \
                  .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                  .field("Heading_of_Motion", geo.headMot) \
                  .time(datetime.utcnow(), WritePrecision.NS)
                
                # # lehet külön kiküldés javítana a heading problémán???
                # lana_gps = []
                # lana_gps.append([gps_coords, heading])
                # send2influx(lana_gps)

                send2influx(gps_coords)
                send2influx(heading)      
                    
            except (ValueError, IOError) as err:
                gps_err1 = 1 # Communication Error with GPS module
                gps_err_msg1 = Point("GPS_Comm_Error") \
                  .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                  .field("Error_message", gps_err1) \
                  .time(datetime.utcnow(), WritePrecision.NS)
                send2influx(gps_err_msg1)

        time.sleep(0.50) # biztos ami sicher      

    finally:
        port.close()


if __name__ == '__main__':
  # if six GPS signals are in 0.02 range it enables to run the 'run' function
    while gps_verify() == True: # folyamatosan chekkel (remelem)
        run()
