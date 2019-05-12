#!/usr/bin/env python

from iot_wand.mqtt_connections import GestureServer, GestureClient, ClientConnection, TOPICS
from iot_wand import helpers as _h
import argparse
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
"""
relative imports -->
"""
import settings as _s
from behavior import on_spell, on_quaternion

def main():
    config = _h.yaml_read(_s.PATH_CONFIG)
    conn = GestureClient(config, debug=_s.DEBUG)
    conn.start(async=True, async_callback=lambda _conn: __async_callback(conn, _s.DEBUG))

def __async_callback(conn, debug):
    print('test')
    input()

if __name__ == '__main__':
    main()
