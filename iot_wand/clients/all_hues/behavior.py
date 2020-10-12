from iot_wand import helpers as _h
import settings as _s
from iot_wand.btle_scanners import HueScanner
from iot_wand.btle_inerfaces import HueInterface

debug = _s.DEBUG
lights = []
lights_enabled = True
hue_scanner = HueScanner(debug=debug)
if not len(lights):
    lights = [
        HueInterface(device, debug=debug).connect()
        for device in hue_scanner.scan()
    ]

def on_button(pressed):
    global lights_enabled
    enabled = not lights_enabled
    for light in lights:
        light.set_light(enabled)
        lights_enabled = enabled

def on_spell(gesture, spell):
    print(spell)

def on_quaternion(x, y, z, w):
    pass
    #print(x, y, x, w)
