from iot_wand.mqtt_connections import GestureServer, ClientConnection, TOPICS
from iot_wand.btle_scanners import WandScanner
from iot_wand.btle_inerfaces import GestureInterface, PATTERN
import iot_wand.server.settings as _s
import iot_wand.helpers as _h
from enum import Enum
import moosegesture
import asyncio
import timeit
import time


def main():
    config = _h.yaml_read(_s.PATH_CONFIG)
    conn = GestureServer(config, debug=_s.DEBUG)
    conn.start(async=True, async_callback=lambda _conn: AsyncServerStateManager(_conn, _s.DEBUG))


class AsyncServerStateManager:
    def __init__(self, mqtt_conn, debug=False):
        self.conn = mqtt_conn
        self._state = self.state(SERVER_STATES.GESTURE_CAPTURE)
        print('started server state manager')
        wands = []
        try:
            sec_ka = 0
            sec_ka_max = 60
            wand_scanner = WandScanner(debug=debug)
            run = True

            while run:
                if not len(wands):
                    wands = [
                        GestureInterface(device, debug=debug).connect()
                        .on('post_connect', lambda interface: self.state().on_post_connect(interface))
                        .on('quaternion', lambda interface, x, y, z, w: self.state().on_quaternion(interface, x, y, z, w))
                        .on('button_press', lambda interface, pressed: self.state().on_button_press(interface, pressed))
                        .on('post_disconnect', lambda interface: self.state().on_post_disconnect(interface))
                        for device in wand_scanner.scan()
                    ]
                else:
                    if not wands[0].connected:
                        wands.clear()
                        sec_ka = 0
                    else:
                        if sec_ka >= sec_ka_max:
                            sec_ka = 0
                            wands[0].keep_alive()
                        else:
                            sec_ka += 1

                        time.sleep(1)

        except (KeyboardInterrupt, Exception) as e:
            self.conn.stop()
            for wand in wands:
                wand.disconnect()
            wands.clear()
            exit(1)

    def state(self, state=None):
        if isinstance(state, SERVER_STATES):
            self._state = state.value
        else:
            if isinstance(state, type):
                self._state = state

        return self._state(self)


class ServerState():
    def __init__(self, manager):
        self.manager = manager
        self.conn = manager.conn
        self.interface = None

    def on_post_connect(self, interface):
        self.interface = interface

    def on_post_disconnect(self, interface):
        pass

    def on_quaternion(self, interface, x, y, z, w):
        pass

    def on_button_press(self, interface, pressed):
        pass

    def switch(self, state):
         return self.manager.state(state)


class GestureCaptureState(ServerState):
    def __init__(self, manager):
        super(GestureCaptureState, self).__init__(manager)

        self.pressed = False
        self.positions = []
        self.spell = None
        self.speed_clicks = 0
        self.press_start = self.press_end = timeit.default_timer()

        print("started capture state")

        self.gestures = { #TODO get from config?
            ("DL", "R", "DL"): "stupefy",
            ("DR", "R", "UR", "D"): "wingardium_leviosa",
            ("UL", "UR"): "reducio",
            ("DR", "U", "UR", "DR", "UR"): "flipendo",
            ("R", "D"): "expelliarmus",
            ("UR", "U", "D", "UL", "L", "DL"): "incendio",
            ("UR", "U", "DR"): "lumos",
            ("U", "D", "DR", "R", "L"): "locomotor",
            ("DR", "DL"): "engorgio",
            ("UR", "R", "DR"): "aguamenti",
            ("UR", "R", "DR", "UR", "R", "DR"): "avis",
            ("D", "R", "U"): "reducto"
        }

    def on_quaternion(self, interface, x, y, z, w):
        if self.pressed:
            self.positions.append(tuple([x, -1 * y]))

        self.conn.signed_publish(TOPICS.QUATERNIONS.value, ClientConnection.data_encode("%d %d %d %d" % (x, y, z, w)))

    def on_button_press(self, interface, pressed):
        self.pressed = pressed

        if pressed:
            self.spell = None
            self.press_start = timeit.default_timer()

            if self.press_start - self.press_end > .2:
                self.speed_clicks = 0
        else:
            self.press_end = timeit.default_timer()

            if self.press_end - self.press_start < .2:
                self.speed_clicks += 1

                if self.speed_clicks >= 3:
                    interface.disconnect()
                    exit(0)

                elif self.speed_clicks == 2:
                    interface.vibrate(PATTERN.BURST)
                    self.switch(SERVER_STATES.PROFILE_SELECT)

                elif self.speed_clicks == 1:
                    print('reset')
                    self.positions = []
                    interface.reset_position()

            else:
                self.speed_clicks = 0

                gesture = moosegesture.getGesture(self.positions)
                self.positions = []

                closest = moosegesture.findClosestMatchingGesture(gesture, self.gestures, maxDifference=1)

                if closest:
                    self.spell = self.gestures[closest[0]]
                    self.conn.signed_publish(TOPICS.SPELLS.value, ClientConnection.data_encode({"gesture": gesture, "spell": self.spell}))

                print("{}: {}".format(gesture, self.spell))


class ProfileSelectState(ServerState):
    def __init__(self, manager):
        super(ProfileSelectState, self).__init__(manager)

        self.pressed = False
        self.speed_clicks = 0
        self.profiles = self.conn.profiles()

        print("started capture state")

        self.interface.vibrate()

    def on_quaternion(self, interface, x, y, z, w):
        if self.pressed:
            print(self.profiles)


    def on_button_press(self, interface, pressed):
        if pressed:
            self.press_start = timeit.default_timer()

            if self.press_start - self.press_end > .2:
                self.speed_clicks = 0
        else:
            self.press_end = timeit.default_timer()

            if self.press_end - self.press_start < .2:
                self.speed_clicks += 1

                if self.speed_clicks >= 3:
                    interface.disconnect()
                    exit(0)

                elif self.speed_clicks == 2:
                    interface.vibrate(PATTERN.BURST)
                    self.switch(SERVER_STATES.GESTURE_CAPTURE)

                elif self.speed_clicks == 1:
                    print('reset')
                    self.positions = []
                    interface.reset_position()


class SERVER_STATES(Enum):
    GESTURE_CAPTURE = GestureCaptureState
    PROFILE_SELECT = ProfileSelectState