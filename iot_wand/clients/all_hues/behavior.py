import platform

if platform.system() != 'Linux':
    print("This is a linux only client as it relies on the bluepy library.")
    exit(1)
else:
    print('Client meets platform requirements!')

import os
from iot_wand import helpers as _h
import settings as _s
from iot_wand.btle_scanners import HueScanner
from iot_wand.btle_inerfaces import HueInterface

debug = _s.DEBUG
lights = []
lights_enabled = True

def post_connect():
    try:
        global lights
        hue_scanner = HueScanner(debug=debug)
        print('scanning for lamps...')
        if not len(lights):
            lights = [
                HueInterface(device, debug=debug).connect()
                for device in hue_scanner.scan()
            ]
    except Exception as e:
        print(e)

def on_button(pressed):
    print("PRESSED")

def on_spell(gesture, spell):
    print(spell)

def on_quaternion(x, y, z, w):
    pass
    #print(x, y, x, w)
