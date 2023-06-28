from ublox_gps import UbloxGps
import serial
import time

port = serial.Serial('/dev/ttyGPS', baudrate=38400, timeout=1) # change default:ttyACM0 if neccessary (to the correct port: ttyGPS)
gps = UbloxGps(port)

# Fő ciklus
while True:
    # GPS adatok frissítése
    gps.update()

    # Sebesség adatok kinyerése
    speed = gps.get_ground_speed() * 1.852  # Sebesség átalakítása km/h-ra

    # Koordináta adatok kinyerése
    latitude = gps.get_latitude()
    longitude = gps.get_longitude()

    # Kiíratás a konzolra
    print("Sebesség: {} km/h".format(speed))
    print("Koordináták: {}, {}".format(latitude, longitude))

    # Várakozás
    time.sleep(1)
