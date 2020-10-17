from iot_wand import helpers as _h
import settings as _s
import time

_h.restrict_client_system('Linux')

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class FoggerManager():
    def __init__(self):
        self._state = False
        self._on_pin = 23
        self._off_pin = 24
        self._t_delay = 2

        #setup
        GPIO.setup(self._on_pin, GPIO.OUT)
        GPIO.setup(self._off_pin, GPIO.OUT)

        print('fogger ready for input...')

    def on(self):
        self.state = True
        GPIO.output(self._on_pin, GPIO.HIGH)
        GPIO.cleanup()

    def off(self):
        self.state = False
        GPIO.output(self._off_pin, GPIO.HIGH)
        GPIO.cleanup()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if isinstance(value, bool):
            self.state = value

    def toggle(self):
        self.state = not self.state
        f = self.off if self.state else self.on
        f()

fogger_manager = FoggerManager()

def on_button(pressed):
    if pressed:
        print('toggling fogger...')
        fogger_manager.toggle()
        print('fogger state is now %s' % str(fogger_manager.state))


def on_spell(gesture, spell):
    pass
    #print(spell)

def on_quaternion(x, y, z, w):
    pass
    #print(x, y, x, w)
