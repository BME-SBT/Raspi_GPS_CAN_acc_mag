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
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import math

import pathlib
scriptpath = pathlib.Path(__file__).parent.resolve()

# sets the connection with GPS module
port = serial.Serial('/dev/ttyGPS', baudrate=38400, timeout=1) # change default:ttyACM0 if neccessary (to the correct port: ttyGPS)
gps = UbloxGps(port)

# Sets the variables of the influxDB (You can generate an API token from the "API Tokens Tab" in the GUI)
org = "sbt"
with open(scriptpath/'influxvars.txt', 'r') as f:
    bucket_name = f.readline().strip()
    influx_url = f.readline().strip()
    lana_token = f.readline().strip()

# sends given data to influxDB which is set in function
def setNsend (msg_type,msg_name,value):
  msg2send = Point(msg_type) \
    .tag("sensor", "sparkfun_ublox_NEO-M9N") \
    .field(msg_name, value) \
    .time(datetime.utcnow(), WritePrecision.NS)
  with InfluxDBClient(url=influx_url, token=lana_token, org=org, timeout=30_000) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket_name, org, msg2send)

def speed_on_geoid(lat1, lon1, lat2, lon2, tmstmp1, tmstmp2):
      # Convert degrees to radians
      lat1 = lat1 * math.pi / 180.0
      lon1 = lon1 * math.pi / 180.0
      lat2 = lat2 * math.pi / 180.0
      lon2 = lon2 * math.pi / 180.0
      # radius of earth in metres
      r = 6378100
      # P
      rho1 = r * math.cos(lat1)
      z1 = r * math.sin(lat1)
      x1 = rho1 * math.cos(lon1)
      y1 = rho1 * math.sin(lon1)
      # Q
      rho2 = r * math.cos(lat2)
      z2 = r * math.sin(lat2)
      x2 = rho2 * math.cos(lon2)
      y2 = rho2 * math.sin(lon2)
      # Dot product
      dot = (x1 * x2 + y1 * y2 + z1 * z2)
      cos_theta = dot / (r * r)
      theta = math.acos(cos_theta)
      # Distance in Metres
      dist = r * theta
      # timestamp is in milliseconds
      time_s = (tmstmp2 - tmstmp1) / 1000.0
      speed_mps = dist / time_s
      speed_kph = (speed_mps * 3600.0) / 1000.0
      return speed_kph

# define variables for gps_speed comparison:
i = 1
lat_1 = 1
lon_1 = 1
lat_2 = 2
lon_2 = 2
timestmp1 = 1
timestmp2 = 2

# array for the last 10 GPS data
last_10_coords = []

def precision_check():
    while True:
        try:
            # read GPS data
            geo = gps.geo_coords()
            # store the last 10 data
            last_10_coords.append((geo.lon, geo.lat))
            # remove the oldest data if array lenght is more than 10
            if len(last_10_coords) > 10:
                last_10_coords.pop(0)

            # check whether there is enough (10) data to compare
            if len(last_10_coords) >= 10:
                # ckeck whether the actual data is in range of +/-0.01 of the last 10 data
                in_range = all(
                    abs(last_10_coords[i][0] - geo.lon) <= 0.01 and 
                    abs(last_10_coords[i][1] - geo.lat) <= 0.01
                    for i in range(len(last_10_coords))
                )

                # if the latest datapoint is in the defined range, return True
                if in_range:
                    return True
                else:
                    return False
            else:
                return False
        except Exception:
            return False

def run():
    try:
        while True:
            try:
                setNsend("GPS_Comm_Error", "Error_message", 0) # Communication OK with GPS module

                geo = gps.geo_coords()
                
                if geo.lon == 0.0 and geo.lat == 0.0 and geo.headMot == 0.0:
                    setNsend("GPS_Position_Error", "Error_message", 1) # GPS pozicio 0, valoszinuleg nincs GPS jel, nezd meg a kek PPS LED vilagit-e
                    setNsend("GPS_Motion_Error", "Error_message", 1) # nem halad a hajo:OOO
                elif geo.lon != 0.0 and geo.lat != 0.0 and geo.headMot == 0.0:
                    setNsend("GPS_Position_Error", "Error_message", 0) # van GPS jel
                    setNsend("GPS_Motion_Error", "Error_message", 1) # Van GPS jel, de nem halad a hajo:OOO
                else:
                    setNsend("GPS_Position_Error", "Error_message", 0) # van GPS jel
                    setNsend("GPS_Motion_Error", "Error_message", 0) # Van GPS jel, halad a hajo
                
                #precision_check()

                if precision_check()==True:
                    # gps_coords = Point("GPS_coordinates") \
                    # .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                    # .field("Longitude", geo.lon) \
                    # .field("Latitude", geo.lat) \
                    # .time(datetime.utcnow(), WritePrecision.NS)
                    # send2influx(gps_coords)

                    setNsend("GPS_coordinates", "Longitude", geo.lon)
                    setNsend("GPS_coordinates", "Latitude", geo.lat)
                    
                    setNsend("heading", "Heading_of_Motion", geo.headMot)

                    # extremely ugly solution, to be improved
                    # change variables to global for the if statements
                    gps_time = gps.date_time()
                    global i
                    global lat_1
                    global lon_1
                    global lat_2
                    global lon_2
                    global timestmp1
                    global timestmp2
                    
                    if i < 3:
                        # save earlier the state of lat, lon and time for compare, increment the state counter
                        if i == 1:
                            lat_1 = geo.lat
                            lon_1 = geo.lon
                            timestmp1 = gps_time.sec
                            i += 1
                            # save the later state of lat, lon and time for compare, reset the state counter
                        elif i == 2:
                            lat_2 = geo.lat
                            lon_2 = geo.lon
                            timestmp2 = gps_time.sec
                            i = 1

                    gps_speed = speed_on_geoid(lat_1, lon_1, lat_2, lon_2, timestmp1, timestmp2)

                    setNsend("GPS_speed", "Speed", gps_speed) 
                # else:
                #     continue

                # time.sleep(1) # sec #it's already fckn slow without sleep (cycle runs for ~2 sec) 
                    
            except (ValueError, IOError) as err:
                setNsend("GPS_Comm_Error", "Error_message", 1) # Communication Error with GPS module

    finally:
        port.close()

if __name__ == '__main__':
    run()
