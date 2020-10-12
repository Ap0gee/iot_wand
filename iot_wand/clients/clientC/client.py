#!/usr/bin/env python

import sys
import os

exit_status = 0

def main():
    try:
        config = _h.yaml_read(_s.PATH_CONFIG)
        conn = GestureClient(config, debug=_s.DEBUG)
        conn.on_spell = on_spell
        conn.on_quaternion = on_quaternion
        conn.on_button = on_button
        print('Starting connection...', end='\r\n\r\n')
        conn.start(as_async=False)
    except Exception as e:
        print(e)
        exit_status = 1

if __name__ == '__main__':
    dir_top = sys.argv[1]
    sys.path.append(dir_top)
        
    try:
        import iot_wand.settings as _iot_s
        sys.path.append(_iot_s.DIR_BASE)

        from iot_wand import helpers as _h
        import settings as _s
        from iot_wand.mqtt_connections import GestureClient
        from behavior import *
    except ImportError as e:
        print(e)
        exit_status = 1

    main()
    exit(exit_status)



