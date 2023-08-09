#! /usr/bin/env python3

import serial
from ublox_gps import UbloxGps

# Soros port beállítása
port = serial.Serial('/dev/ttyGPS', baudrate=38400, timeout=1)

# GPS modul inicializálása
gps = UbloxGps(port)

# Utolsó 10 GPS adat tárolására szolgáló lista
last_10_coords = []

def run():
    while True:
        try:
            # GPS adatok kiolvasása
            geo = gps.geo_coords()
            #lon = geo.lon
            #lat = geo.lat

            # Az utolsó 10 adat tárolása
            last_10_coords.append((geo.lon, geo.lat))
            print("lon:",geo.lon)
            print("lat:",geo.lat)

            # Csak az utolsó 10 adatot tároljuk
            if len(last_10_coords) > 10:
                last_10_coords.pop(0)

            # Ellenőrzés, hogy az utolsó 10 adat a megadott tartományon belül van-e
            in_range = all(
                abs(last_10_coords[i][0] - geo.lon) <= 0.01 and
                abs(last_10_coords[i][1] - geo.lat) <= 0.01
                for i in range(len(last_10_coords))
            )

            # Ha az adatok a tartományon belül vannak, kiírjuk őket
            if in_range:
                print("GPS adatok a tartományon belül:")
                for i, (geo.lon, geo.lat) in enumerate(last_10_coords, start=1):
                    print(f"{i}. Adat - Hosszúság: {geo.lon}, Szélesség: {geo.lat}")
            else:
                print("GPS adatok nem esnek a tartományon belül.")

        except (KeyboardInterrupt, SystemExit):
            print("Kilépés...")
            break
        except Exception as e:
            print(f"Hiba történt: {e}")

if __name__ == '__main__':
    run()