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
import math

import pathlib
scriptpath = pathlib.Path(__file__).parent.resolve()

# sets the connection with GPS module
# to check which serial port is connected to GPS module run: ls -la /dev/serial/by-id 
port = serial.Serial('/dev/ttyGPS', baudrate=38400, timeout=1) # change default:ttyACM0 if neccessary (to the correct port: ttyGPS)
gps = UbloxGps(port)

# Sets the variables of the influxDB (You can generate an API token from the "API Tokens Tab" in the GUI)
org = "sbt"
bucketfile = open(scriptpath/".bucket_name","r") # database name
bucket_name = str(bucketfile.read())
bucketfile.close()
tokenfile = open(scriptpath/".lana_token","r")
lana_token = str(tokenfile.read())
tokenfile.close()
urlfile = open(scriptpath/".influx_url","r")
influx_url = str(urlfile.read())
urlfile.close()

# sends given data to influxDB which is set in function
def send2influx(msg2send):
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

i = 1
lat_1 = 1
lon_1 = 1
lat_2 = 2
lon_2 = 2
timestmp1 = 1
timestmp2 = 2

def setNsend (msg_type,msg_name,value):
  influxmsg = Point(msg_type) \
    .tag("sensor", "sparkfun_ublox_NEO-M9N") \
    .field(msg_name, value) \
    .time(datetime.utcnow(), WritePrecision.NS)
  send2influx(influxmsg)

def run():
    try:
        while True:
            try:
                gps_err1 = 0 # Communication OK with GPS module
                setNsend("GPS_Comm_Error", "Error_message", gps_err1)
                # gps_err_msg1 = Point("GPS_Comm_Error") \
                #   .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                #   .field("Error_message", gps_err1) \
                #   .time(datetime.utcnow(), WritePrecision.NS)
                # send2influx(gps_err_msg1)

                geo = gps.geo_coords()
                
                if geo.lon == 0.0 and geo.lat == 0.0 and geo.headMot == 0.0:
                    gps_err2 = 1 # GPS pozicio 0, valoszinuleg nincs GPS jel, nezd meg a kek PPS LED vilagit-e
                    gps_err_msg2 = Point("GPS_Position_Error") \
                      .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                      .field("Error_message", gps_err2) \
                      .time(datetime.utcnow(), WritePrecision.NS)
                    send2influx(gps_err_msg2)
                    gps_err3 = 1 # nem halad a hajo:OOO
                    gps_err_msg3 = Point("GPS_Motion_Error") \
                      .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                      .field("Error_message", gps_err3) \
                      .time(datetime.utcnow(), WritePrecision.NS)
                    send2influx(gps_err_msg3)
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
                elif geo.lon != 0.0 and geo.lat != 0.0 and geo.headMot != 0.0:
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
                send2influx(gps_coords)
                
                heading = Point("heading") \
                  .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                  .field("Heading_of_Motion", geo.headMot) \
                  .time(datetime.utcnow(), WritePrecision.NS)
                send2influx(heading)

                # print("anyadat")
                # veh = gps.veh_attitude()
                # print("a kurva anyadat")
                # print("Roll: ", veh.att_roll)
                # print("a jo edes budos kurva anyadat")
                # print("Pitch: ", veh.pitch)
                # print("Heading: ", veh.heading)
                # print("Roll Acceleration: ", veh.accRoll)
                # print("Pitch Acceleration: ", veh.accPitch)
                # print("Heading Acceleration: ", veh.accHeading)

                gps_time = gps.date_time()
                global i
                global lat_1
                global lon_1
                global lat_2
                global lon_2
                global timestmp1
                global timestmp2
                while i < 3:
                    if i == 1:
                      lat_1 = geo.lat
                      lon_1 = geo.lon
                      timestmp1 = gps_time.sec
                      print("act i: ", i, "lat_1: ", lat_1, "lon_1: ", lon_1, "timestmp1: ", timestmp1)
                      i += 1
                      print("incremented i: ", i)
                      continue
                    if i == 2:
                      lat_2 = geo.lat
                      lon_2 = geo.lon
                      timestmp2 = gps_time.sec
                      print("i before reset: ", i)
                      i = 1
                      print("act i: ", i, "lat_2: ", lat_2, "lon_2: ", lon_2, "timestmp2: ", timestmp2)

                gps_speed = speed_on_geoid(lat_1, lon_1, lat_2, lon_2, timestmp1, timestmp2)
                print("lat_1, lon_1, lat_2, lon_2, timestmp1, timestmp2: ", lat_1, lon_1, lat_2, lon_2, timestmp1, timestmp2)
                print(gps_speed)

                GPSspeed = Point("GPS_speed") \
                  .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                  .field("Speed", gps_speed) \
                  .time(datetime.utcnow(), WritePrecision.NS)
                send2influx(GPSspeed)     
                    
            except (ValueError, IOError) as err:
                gps_err1 = 1 # Communication Error with GPS module
                gps_err_msg1 = Point("GPS_Comm_Error") \
                  .tag("sensor", "sparkfun_ublox_NEO-M9N") \
                  .field("Error_message", gps_err1) \
                  .time(datetime.utcnow(), WritePrecision.NS)
                send2influx(gps_err_msg1)
                
        time.sleep(1) # 1 sec

    finally:
        port.close()

if __name__ == '__main__':
    run()
