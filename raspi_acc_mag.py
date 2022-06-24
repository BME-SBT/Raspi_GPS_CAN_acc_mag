# BME Solar Boat Team 2022
# Boat name: Lana
# Responsible for code: BM

# on Raspberry PI 4
# Sends acceleration, magnetic field data from accelero-, magnetometer to influxDB
# GPS module: LSM303d
# Connected to Raspberry PI via I^2C

import time
from lsm303d import LSM303D
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


lsm = LSM303D(0x1d)  # Change to 0x1e if you have soldered the address jumper

# # ha nem lenne jó a kiküldéskor írt megoldás
# utcdate = datetime.datetime.utcnow()
# timestamp = utcdate + datetime.timedelta(hours=2) #ez igy joooo?
# # vagy lehet import pytz-vel is

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
    while True:
        try:
            acc_xyz = lsm.accelerometer()
            print(("{:+06.2f}g : {:+06.2f}g : {:+06.2f}g").format(*acc_xyz)) # majd ki kell torolni
            acc = Point("acceleration") \
                  .tag("sensor", "LSM303d") \
                  .field("Acceleration", ("{:+06.2f}g : {:+06.2f}g : {:+06.2f}g").format(*acc_xyz)) \
                  .time(datetime.utcnow(), WritePrecision.NS)
            
            mag_xyz = lsm.magnetometer()
            print(("{:+06.2f} : {:+06.2f} : {:+06.2f}").format(*mag_xyz)) # majd ki kell torolni
            mag = Point("magnetic_field") \
                  .tag("sensor", "LSM303d") \
                  .field("Magnetic field", ("{:+06.2f} : {:+06.2f} : {:+06.2f}").format(*mag_xyz)) \
                  .time(datetime.utcnow(), WritePrecision.NS)
            
            lana_acc_mag = []
            lana_acc_mag.append([acc, mag])
            
            send2influx(lana_acc_mag)
            
            time.sleep(1.0/50)


        except (ValueError, IOError) as err:
            print(err) # majd ki kell törölni
            com_err_msg = Point("Accelero-, magnetometer comm Error") \
                .tag("sensor", "LSM303d") \
                .field("Communication Error message", err) \
                .time(datetime.utcnow(), WritePrecision.NS)
            send2influx(com_err_msg)

if __name__ == '__main__':
    run()