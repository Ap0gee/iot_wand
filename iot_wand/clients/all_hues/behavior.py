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
import threading
import time

class AsyncLightManager:
    def __init__(self, debug=False):
        self._lock = threading.Lock()
        self._light_management_thread = None
        self._lights = []
        self._lights_enabled = True
        self.run = True

        if not self._light_management_thread:
            self._light_management_thread = threading.Thread(target=self._manage_lights, args=(debug,))
            self._light_management_thread.start()

    def _manage_lights(self, debug):
        try:
            hue_scanner = HueScanner(debug=debug)

            while self.run:
                with self._lock:
                    if not len(self._lights):
                        self._lights = [
                            HueInterface(device, debug=debug).connect()
                            for device in hue_scanner.scan()
                        ]
                    else:
                        print("%s lights connected." % len(self._lights))
                        time.sleep(1)

        except (KeyboardInterrupt, Exception) as e:
            print(e)

    def get_lights(self):
        return self._lights

    def set_lights(self, on=True):
        for light in self._lights:
            light.set_light(on)

    def toggle_lights(self):
        self.set_lights(not self._lights_enabled)
        self._lights_enabled = not self._lights_enabled

manager = AsyncLightManager(_s.DEBUG) #called when imported

def on_button(pressed):
    global manager

    if pressed:
        print("DOWN")


def on_spell(gesture, spell):
    print(spell)

def on_quaternion(x, y, z, w):
    pass
    #print(x, y, x, w)
