import time
import requests
import json


class Sailaway:
    def __init__(self):
        self.headers = {}

        self.backend = 'https://backend.sailaway.world/cgi-bin/sailaway'

        try:
            f = open('login.auth', 'r')
            d = json.loads(f.read())
            self.email = d['email']
            self.password = d['password']
        except IOError:
            # print (e)
            self.email = None
            self.password = None

    def _saveLogin(self):
        f = open('login.auth', 'w')
        f.write(json.dumps({'email': self.email, 'password': self.password}))
        f.close()
        print('Saved Credentials')

    def login(self, email=None, password=None):
        if email is not None and password is not None:
            self.email = email
            self.password = password

        payload = {'email': self.email, 'pwd': self.password,
                   'page': self.backend + '/events.pl'}
        # import pdb; pdb.set_trace()
        r = requests.post(
            self.backend + '/weblogin.pl', data=payload)

        # print r.headers
        session = r.headers['Set-Cookie'].split('=')[1].split(';')[0]
        self.headers = {"Cookie": "CGISESSID=" + session}
        self._saveLogin()
        time.sleep(1)

    def getMission(self, missionid):
        r = requests.get(self.backend + '/GetMission.pl?misnr=' +
                         str(missionid), headers=self.headers)
        return r.json()

    def getLeaderBoard(self, missionid):
        r = requests.get(self.backend + '/GetLeaderboard.pl?misnr=' +
                         str(missionid), headers=self.headers)
        return r.json()

    def getMissions(self, history=False, rtype=0):
        if history:
            hist = 1
        else:
            hist = 0

        r = requests.get(self.backend + '/GetMissions.pl?race=1&tutorial=0&hist=' +
                         str(hist) + '&racetype=' + str(rtype), headers=self.headers)
        return r.json()

    def getUserBoats(self):
        # print (self.headers)
        r = requests.get(
            self.backend + '/GetUserBoats.pl', headers=self.headers)
        return r.json()

    def getBoatInfo(self, boatid):
        r = requests.get(
            self.backend + '/BoatInfo.pl?ubtnr=' + str(boatid), headers=self.headers)
        return r.json()

    def getTrips(self, boatid):
        r = requests.get(
            self.backend + '/Trip.pl?action=list&ubtnr=' + str(boatid), headers=self.headers)
        return r.json()

    def deleteTrip(self, boatid, tripid):
        r = requests.get(self.backend + '/Trip.pl?action=del&trpnr=' +
                         str(tripid) + '&ubtnr=' + str(boatid), headers=self.headers)
        return r.json()

    def saveTrip(self, boatid, tripid, checkpoints=[]):
        pass
