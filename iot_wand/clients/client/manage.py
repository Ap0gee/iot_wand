from iot_wand.mqtt_connections import GestureClient
import iot_wand.helpers as _h
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
    conn.on_spell = on_spell
    conn.on_quaternion = on_quaternion
    conn.start()

if __name__ == "__main__":
    main()