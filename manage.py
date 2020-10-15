#! /usr/bin/env python3
#! _*_ coding: utf-8 _*_

__version__ = '0.9.0'

import argparse
import iot_wand.settings as _s
import os
import sys
import threading

def main(args):
    dir_top = os.path.dirname(_s.DIR_BASE)

    if hasattr(args, 'to_run'):
        if args.to_run == 'server':
            from iot_wand.server import server
            server.main()

        if args.to_run == 'clients':
            from iot_wand.clients import clients
            clients.main(dir_top)

    elif hasattr(args, 'to_make'):
        pass

    elif hasattr(args, 'i'):
        args.i()

def interactive():
    try:
        while 1:
            del sys.argv[1:]
            [sys.argv.append(i) for i in input("Enter a command:").split()]
            args = parse_args()
            print(args)
            main(args)
    except (Exception, KeyboardInterrupt) as e:
        exit(1)

def action_interactive(dest, option_strings):
    threading.Thread(target=interactive).start()

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
    parser.add_argument('-i', action='store_const', default=interactive, const=interactive)
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
