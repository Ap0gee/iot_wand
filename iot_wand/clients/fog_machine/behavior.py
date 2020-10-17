from iot_wand import helpers as _h
import settings as _s
import time

_h.restrict_client_system('Linux')

import RPi.GPIO as GPIO

class FoggerManager():
    def __init__(self):
        self._state = False
        self._on_pin = 17
        self._off_pin = 27
        self._t_delay = 2

        #setup
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self._on_pin, GPIO.OUT)
        GPIO.setup(self._off_pin, GPIO.OUT)

        GPIO.cleanup()
        print('fogger ready for input...')

    def on(self):
        print('turning on fogger..')
        self.state = True
        GPIO.output(self._on_pin, GPIO.HIGH)
        time.sleep(3)
        GPIO.cleanup()

    def off(self):
        print('turning off fogger..')
        self.state = False
        GPIO.output(self._off_pin, GPIO.HIGH)
        time.sleep(3)
        GPIO.cleanup()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if isinstance(value, bool):
            self.state = value

    def toggle(self):
        self.off() if self.state else self.on()

fogger_manager = FoggerManager()

def on_button(pressed):
    if pressed:
        fogger_manager.toggle()

def on_spell(gesture, spell):
    pass
    #print(spell)

def on_quaternion(x, y, z, w):
    pass
    #print(x, y, x, w)
