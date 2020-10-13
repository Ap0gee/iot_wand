from phue import Bridge

IP_BRIDGE = '10.0.0.46'

class LightManager():
    def __init__(self, ip_addr):
        self._bridge = Bridge(ip_addr)
        self._bridge.connect()

    def get_api(self):
        return self._bridge.get_api()

    def get_lights(self):
        return self._bridge.get_light_objects('list')

manager = LightManager(IP_BRIDGE)

def on_button(pressed):
    global manager

    if pressed:
        print("DOWN")
        print(manager.get_lights())

def on_spell(gesture, spell):
    print(spell)

def on_quaternion(x, y, z, w):
    pass
    #print(x, y, x, w)
