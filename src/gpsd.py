# coding=utf-8

import socket
import time
import datetime
import json
from threading import Thread


def checksum_NMEA(stringa_input):
    # Calcolo del checksum in formato NMEA - attenzione, per semplicità le eccezioni non sono gestite
    # Calculate the NMEA checksum - Note, for simplicity the exceptions have not been managed
    
    # trova il primo carattere dopo $
    # Find the first character after $
    payload_start = stringa_input.find('$') + 1
    payload_end = stringa_input.find('*')      # trova il carattere * || find the * character
    # dati di cui fare XOR
    payload = stringa_input[payload_start: payload_end]
    ck = 0
    for ch in payload:      # ciclo di calcolo del checksum || checksum calculation cycle
        ck = ck ^ ord(ch)   # XOR
    str_ck = '%02X' % ck    # trasforma il valore calcolato in una stringa di 2 caratteri || transforms the calculated value into a 2 character string
    return(str_ck)


class GPSD:
    def __init__(self):
        self.currentPacket = None
        self.lat = None
        self.lon = None
        self.speed = None
        self.hdg = None
        self.conf = 'nmea'

    def updatePosition(self, lat, lon, speed, hdg):
        self.lat = lat
        self.lon = lon
        self.speed = speed * 0.5144
        self.speedkn = speed
        self.hdg = hdg

    def formatCoords(self, coord, dpad=2):
        d = str(int(abs(coord))).zfill(dpad)
        m = str(int(abs((coord - int(coord)) * 60))).zfill(7)
        
        formatted = d + m
        return formatted
        
    def prepareJSONData(self):
        if not self.lat or not self.lon:
            return None

        return {
            "device": "sailaway",
            "class": "TPV",
            "lat": self.lat,
            "lon": self.lon,
            #"alt": 0,
            "track": self.hdg,
            "speed": self.speed,  # meter per second
            "mode": 2,
            #"time":"2010-04-30T11:48:20.10Z",
            "ept": 0.005,
            "epx": 15.319,
            "epy": 17.054,
            "epv": 124.484,
            "climb": -0.085,
            "eps": 34.11
        }

    def prepareNMEAData(self):
        if not self.lat or not self.lon:
            return []

        hdt = "$GPHDT," + str(self.hdg) + ",T*"
        hdt += checksum_NMEA(hdt)

        gll = "$GPGLL,"

        gll += self.formatCoords(self.lat) + ","
        
        if self.lat > 0:
            gll += 'N'
        else:
            gll += 'S'
        gll += ','

        gll += self.formatCoords(self.lon) + ","
        
        if self.lon > 0:
            gll += 'E'
        else:
            gll += 'W'
        gll += ','
        gll += datetime.datetime.utcnow().strftime('%H%M%S.%f')[:9] + ',A*'
        gll += checksum_NMEA(gll)

        return [
            bytes(hdt, 'ascii'),
            bytes(gll, 'ascii')
        ]

    def serveClient(self, api, boatid, client):
        i = 0

        time.sleep(1)
        client.send(bytes(json.dumps({"class": "VERSION", "release": "3.17",
                                      "rev": "3.17", "proto_major": 3, "proto_minor": 12}), 'ascii'))
        conf = client.recv(1024)
        self.conf = 'nmea'

        # TODO check if it wants json or nmea

        time.sleep(1)
        client.send(bytes(json.dumps({"class": "DEVICES", "devices": [
                    {"class": "DEVICE", "path": "sailaway", "activated": 1269959537.20, "native": 0, "bps": 4800, "parity": "N", "stopbits": 1, "cycle": 1.00}]}), 'ascii'))
        client.send(bytes(json.dumps({"class": "WATCH", "enable": True, "json": True, "nmea": True,
                                      "raw": 0, "scaled": False, "timing": False, "split24": False, "pps": False}), 'ascii'))

        while True:
            if self.conf == 'nmea':
                for p in self.prepareNMEAData():
                    client.send(p)
            elif self.conf == 'json':
                pack = self.prepareJSONData()
                if pack:
                    client.send(
                        bytes(json.dumps(self.currentPacket), 'ascii'))

            time.sleep(1)

            if i % 5 == 0:
                print('Updating positon')
                bi = api.getBoatInfo(boatid)
                self.updatePosition(float(bi['ubtlat']), float(bi['ubtlon']), float(
                    bi['ubtspeedoverground']), float(bi['ubtheading']))
                print('Lat: {lat}, Long: {lon}'.format(
                    lat=bi['ubtlat'], lon=bi['ubtlon']))

            i += 1

    def serve(self, api, boatid, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("127.0.0.1", port))
        self.socket.listen(5)

        #pt = Thread (target=self.poolPosition, args=(api, boatid,))
        # pt.run()

        print('Serving GPSD at port {prt}'.format(prt=port))
        while True:
            (client, address) = self.socket.accept()
            print('New connection')
            ct = Thread(target=self.serveClient, args=(api, boatid, client,))
            ct.run()
