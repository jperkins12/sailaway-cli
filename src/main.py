# import argparse
import sys

import api
import gpsd


def usage():
    pass


def main():
    argvn = len(sys.argv)

    print (sys.argv)

    # No args, usage
    if argvn < 2:
        usage()
        sys.exit()

    # login
    elif argvn > 1 and sys.argv[1] == 'login':
        email = None
        password = None

        if argvn > 2:
            email = sys.argv[2]
        else:
            email = raw_input('Email: ')
        if argvn > 3:
            password = sys.argv[3]
        else:
            password = raw_input('Password: ')

        sw = api.Sailaway()
        sw.login(email, password)

    # list-boats
    elif argvn > 1 and sys.argv[1] == 'list-boats':
        sw = api.Sailaway()
        sw.login()
        for boat in sw.getUserBoats()['userboats']:
            if boat['ubtname'] is not None:
                printstring = 'ID: {id}, Name: {name}, Description: {des}'.format(
                    id=boat['ubtnr'], name=boat['ubtname'], des=boat['prdtitle'])
                print(printstring)

    # gps-serve
    elif argvn > 2 and sys.argv[1] == 'gps-serve':
        boat = sys.argv[2]
        port = 2947

        if argvn > 3:
            port = int(sys.argv[3])

        sw = api.Sailaway()
        sw.login()

        gdaemon = gpsd.GPSD()
        gdaemon.serve(sw, boat, port)


if __name__ == "__main__":
    main()
