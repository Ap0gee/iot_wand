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

        GPIO.cleanup()
        print('fogger ready for input...')

    def on(self):
        print('turning on fogger..')
        self.__gpio_pin_setup(self._on_pin)
        GPIO.output(self._on_pin, GPIO.HIGH)

    def off(self):
        print('turning off fogger..')
        self.__gpio_pin_setup(self._off_pin)
        GPIO.output(self._off_pin, GPIO.HIGH)

    def __gpio_pin_setup(self, pin, mode=GPIO.BCM, direction=GPIO.OUT):
        GPIO.setmode(mode)
        GPIO.setup(pin, direction)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if type(value) == bool:
            self._state = value

    def toggle(self):
        self.off() if self.state else self.on()

fogger_manager = FoggerManager()

def on_button(pressed):
    global fogger_manager

    if pressed:
        try:
            print("Pressed = %s" % pressed)
            print("STATE = %s" % str(fogger_manager.state))
            if fogger_manager.state:
                fogger_manager.state = False
                fogger_manager.off()
                time.sleep(1)
            else:
                fogger_manager.state = True
                fogger_manager.on()
                time.sleep(1)
        except Exception as e:
            print(e)
            input() and exit(1)
        finally:
            GPIO.cleanup()

def on_spell(gesture, spell):
    pass
    #print(spell)

def on_quaternion(x, y, z, w):
    pass
    #print(x, y, x, w)
