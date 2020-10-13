from phue import Bridge
import timeit

IP_BRIDGE = '10.0.0.46'

class LightsManager():
    def __init__(self, ip_addr):
        self._bridge = Bridge(ip_addr)
        self._bridge.connect()

    @property
    def is_lights_on(self):
        return self._lights_on

    @is_lights_on.setter
    def is_lights_on(self, value):
        if type(value) == bool:
            self._lights_on = value

    def get_api(self):
        return self._bridge.get_api()

    def get_lights(self):
        return self._bridge.get_light_objects('list')

    def toggle_lights(self):
        for light in self._bridge.get_light_objects('list'):
            is_on = not light.on
            print(is_on)
            light.on = is_on

class ButtonManager():
    def __init__(self):
        self._press_start = 0
        self._press_end = 0

    def reset_press_timer(self):
        self._press_start = self._press_end = 0

    def start_press_timer(self):
        self._press_start = timeit.default_timer()

    def end_press_timer(self):
        self._press_end = timeit.default_timer()

    def get_press_time(self):
        return self._press_end - self._press_start

lights_manager = LightsManager(IP_BRIDGE)
button_manager = ButtonManager()

def on_button(pressed):
    global lights_manager
    if pressed:
        button_manager.reset_press_timer()
        button_manager.start_press_timer()
    else:
        button_manager.end_press_timer()
        time_pressed = button_manager.get_press_time()
        if time_pressed > .5 and time_pressed < 2:
            lights_manager.toggle_lights()

def on_spell(gesture, spell):
    print(spell)

def on_quaternion(x, y, z, w):
    pass
    #print(x, y, x, w)
