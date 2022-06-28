#! /usr/bin/env python3

# BME Solar Boat Team 2022
# Boat name: Lana
# Responsible for code: BM

# on Raspberry PI 4
# Sends CAN data from the BMS to influxDB
# BMS
# Connected to Raspberry PI via serial port

import time
import serial
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# sets the connection with GPS module
# to check which serial port is connected to GPS module run: ls -la /dev/serial/by-id 
port = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=1) # change ttyACM0 if neccessary (to the correct port)

# # ha nem lenne jó a kiküldéskor írt megoldás
# import time # lehet nem kell
# utcdate = datetime.datetime.utcnow()
# timestamp = utcdate + datetime.timedelta(hours=2) #ez igy joooo?
# vagy lehet import pytz-vel is

# Sets the variables of the influxDB (You can generate an API token from the "API Tokens Tab" in the UI)
token = "masold ki influxbol vagy a raspin lavo tobbi scriptbol" # lana_token
org = "sbt"
bucket = "lana" # database

# sends given data to influxDB which is set in function
def send2influx(msg2send):
    with InfluxDBClient(url="http://influx.solarboatteam.hu:8086", token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket, org, msg2send)
#     client.close() # lehet fölösleges

def run():

    try:
#         print("Listening for UBX Messages") # majd ki kell törölni
        while True:
            try:
                # write your code here
                
                
                can_msg = Point("BMS data") \
                  .tag("sensor", "CAN") \
                  .field("SOC", fasztudjami) \ # change fasztudjami if necessery
                  .time(datetime.utcnow(), WritePrecision.NS)
                
                
                send2influx(can_msg)
                
                time.sleep(1.0/50)
                
                
            except (ValueError, IOError) as err:
                print(err) # lehet ki majd kell törölni
                com_err_msg = Point("GPS module comm Error") \
                  .tag("sensor", "sparkfun ublox NEO-M9N") \
                  .field("Communication Error message", err) \
                  .time(datetime.utcnow(), WritePrecision.NS)
                send2influx(com_err_msg)
                 

    finally:
        port.close()


if __name__ == '__main__':
    run()                