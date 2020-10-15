#! /usr/bin/env python3
#! _*_ coding: utf-8 _*_

__version__ = '0.9.0'

import argparse
import iot_wand.settings as _s
import os
from multiprocessing import Process

def spawn_server():
    from iot_wand.server import server
    p = Process(server.main())
    p.start()
    return p

def main(args):
    if args.to_run == 'server':
        server = spawn_server()
        while 1:
            if not server.is_alive():
                print('spawning new server...')
                server = spawn_server()

    if args.to_run == 'clients':
        from iot_wand.clients import clients
        clients.main(os.path.dirname(_s.DIR_BASE))

def parse_args():
    parser = argparse.ArgumentParser(
        prog='iot-wand',
    )
    subparsers = parser.add_subparsers(
        help='sub-command help'
    )
    parser.add_argument('-v', '--version',
        action='version',
        version='%(prog)s v{version}'.format(version=__version__)
    )
    run_parser = subparsers.add_parser('run')

    run_parser.add_argument('to_run',
        help='run the server, clients, the config web-site, or all (default: %(default)s)',
        choices=['server', 'clients', 'web', 'all'],
        default='all'
    )
    make_parser = subparsers.add_parser('make')

    make_parser.add_argument('to_make',
        help='make a fresh client within /clients',
        choices=['client']
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)