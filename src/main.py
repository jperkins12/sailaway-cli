'''
Sailaway API CLI
Run using Python3
'''

import argparse
import sys

import api
import gpsd


def usage():
    pass


def main():

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title='Commands', help='cli functions', dest='command')

    parser_login = subparsers.add_parser('login', help='Login to Sailaway')
    parser_login.add_argument('-u', '--user', help='Sailaway Username')
    parser_login.add_argument('-w', '--password', help='Sailaway Password')

    parser_list = subparsers.add_parser('list-boats', help='List User Boats')

    parser_gps = subparsers.add_parser('gps-serve', help='Start GPSD Server')
    parser_gps.add_argument('boatid', help='User Boat ID')
    parser_gps.add_argument('-p', '--port', type=int,
                            default=2947, help='GPSD Port, Default: 2947')

    args = parser.parse_args()

    # login
    if args.command == 'login':

        if args.user:
            email = args.user
        else:
            email = input('Email: ')

        if args.password:
            password = args.password
        else:
            password = input('Password: ')

        sw = api.Sailaway()
        sw.login(email, password)

    # list-boats
    if args.command == 'list-boats':
        sw = api.Sailaway()
        sw.login()
        for boat in sw.getUserBoats()['userboats']:
            if boat['ubtname'] is not None:
                printstring = 'ID: {id}, Name: {name}, Description: {des}'.format(
                    id=boat['ubtnr'], name=boat['ubtname'], des=boat['prdtitle'])
                print(printstring)

    # gps-serve
    if args.command == 'gps-serve':
        boat = args.boatid
        port = args.port

        sw = api.Sailaway()
        sw.login()

        gdaemon = gpsd.GPSD()
        gdaemon.serve(sw, boat, port)


if __name__ == "__main__":
    main()
