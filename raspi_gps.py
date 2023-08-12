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

# array for the last 2 GPS data
speed_coords = []

def get_speed():
    # read GPS data
    geo = gps.geo_coords()
    gps_time = gps.date_time()
    # store the last 2 data
    speed_coords.append((geo.lon, geo.lat, gps_time.sec))
    lon1=speed_coords[0][0]
    lat1=speed_coords[0][1]
    lon2=speed_coords[1][0]
    lat2=speed_coords[1][1]
    tmstmp1=speed_coords[0][2]
    tmstmp2=speed_coords[1][2]
    # remove the oldest data if array lenght is more than 2
    if len(speed_coords) > 2:
        speed_coords.pop(0)
    # check whether there is enough (2) data to compare
    if len(speed_coords) >= 2: # you can delete it, but the data transmission will start one cycle later (which takes seconds possibly)
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
        if tmstmp2 < tmstmp1:
            time_s = (tmstmp2 + 60 - tmstmp1) / 1000.0 # if the second timestamp is in the next minute
        else:
            time_s = (tmstmp2 - tmstmp1) / 1000.0
        speed_mps = dist / time_s
        speed_kph = (speed_mps * 3600.0) / 1000.0
        print("lat_1, lon_1, lat_2, lon_2, timestmp1, timestmp2: ", lat1, lon1, lat2, lon2, tmstmp1, tmstmp2)
        print("gps speed",speed_kph)
        return speed_kph

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

            print("################",datetime.now(),"#########################################")

            # check whether there is enough (10) data to compare
            if len(last_10_coords) >= 10: # you can delete it, but the data transmission will start one cycle later (which takes seconds possibly)
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
                lon = geo.lon
                lat = geo.lat
                
                if geo.lon == 0.0 and geo.lat == 0.0 and geo.headMot == 0.0:
                    setNsend("GPS_Position_Error", "Error_message", 1) # GPS pozicio 0, valoszinuleg nincs GPS jel, nezd meg a kek PPS LED vilagit-e
                    setNsend("GPS_Motion_Error", "Error_message", 1) # nem halad a hajo:OOO
                elif geo.lon != 0.0 and geo.lat != 0.0 and geo.headMot == 0.0:
                    setNsend("GPS_Position_Error", "Error_message", 0) # van GPS jel
                    setNsend("GPS_Motion_Error", "Error_message", 1) # Van GPS jel, de nem halad a hajo:OOO
                else:
                    setNsend("GPS_Position_Error", "Error_message", 0) # van GPS jel
                    setNsend("GPS_Motion_Error", "Error_message", 0) # Van GPS jel, halad a hajo

                if precision_check()==True:
                    print("elvileg most pontos!!!!!!!!!!!!!!!")
                    print("Longitude", geo.lon, "Latitude", geo.lat)

                    setNsend("GPS_coordinates", "Longitude", geo.lon)
                    setNsend("GPS_coordinates", "Latitude", geo.lat)
                    
                    setNsend("heading", "Heading_of_Motion", geo.headMot)
                 
                    setNsend("GPS_speed", "Speed", get_speed()) 

                # time.sleep(1) # sec #it's already fckn slow without sleep (cycle runs for ~2 sec) 
                    
            except (ValueError, IOError) as err:
                setNsend("GPS_Comm_Error", "Error_message", 1) # Communication Error with GPS module

    finally:
        port.close()

if __name__ == '__main__':
    run()
