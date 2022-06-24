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

# sets the connection with GPS module
# to check which serial port is connected to GPS module run: ls -la /dev/serial/by-id 
port = serial.Serial('/dev/ttyACM0', baudrate=38400, timeout=1) # change ttyACM0 if neccessary (to the correct port)
gps = UbloxGps(port)

# # ha nem lenne jó a kiküldéskor írt megoldás
# import time # lehet nem kell
# utcdate = datetime.datetime.utcnow()
# timestamp = utcdate + datetime.timedelta(hours=2) #ez igy joooo?
# vagy lehet import pytz-vel is

# Sets the variables of the influxDB (You can generate an API token from the "API Tokens Tab" in the UI)
token = "APPLVlMGyeWeKoRhipR-1ULSX5mtduugSWo2jDTbXyDinF1TyahGU9smvMOkSwrP0TdYv6VIVEm7jcLosozZUg==" # lana_token
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
                geo = gps.geo_coords()
#                 print("Longitude: ", geo.lon) # majd ki kell törölni
#                 print("Latitude: ", geo.lat)  # majd ki kell törölni
#                 print("Heading of Motion: ", geo.headMot) # majd ki kell törölni
                
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
                print(err) # majd ki kell törölni
                com_err_msg = Point("GPS module comm Error") \
                  .tag("sensor", "sparkfun ublox NEO-M9N") \
                  .field("Communication Error message", err) \
                  .time(datetime.utcnow(), WritePrecision.NS)
                send2influx(com_err_msg)
                 

    finally:
        port.close()


if __name__ == '__main__':
    run()