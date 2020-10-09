#!/usr/bin/env python

import argparse
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from iot_wand.mqtt_connections import GestureClient
from iot_wand import helpers as _h



import settings as _s
from behavior import on_spell, on_quaternion

def main():
    config = _h.yaml_read(_s.PATH_CONFIG)
    conn = GestureClient(config, debug=_s.DEBUG)
    conn.on_spell = on_spell
    conn.on_quaternion = on_quaternion
    conn.start(False)

if __name__ == '__main__':
    main()
