from iot_wand.mqtt_connections import GestureServer, ClientConnection, TOPICS, SYS_LEVELS
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
        self._state = self.set_state(SERVER_STATES.GESTURE_CAPTURE.value)
        self.run = True

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run_async_tasks(debug))


    async def run_async_tasks(self, debug):
        await asyncio.gather(
            self.manage_wands(debug),
            self.ping_clients_forever(),
            self.loop_state()
        )

    async def manage_wands(self, debug):
        wands = []
        try:
            sec_ka = 0
            sec_ka_max = 60
            wand_scanner = WandScanner(debug=debug)

            while self.run:
                if not len(wands):
                    wands = [
                        GestureInterface(device, debug=debug)
                        .on('post_connect', lambda interface: self.get_state().on_post_connect(interface))
                        .on('post_disconnect', lambda interface: self.get_state().on_post_disconnect(interface))
                        .on('button_press', lambda interface, pressed: self.get_state().on_button_press(interface, pressed))
                        .on('quaternion', lambda interface, x, y, z, w: self.get_state().on_quaternion(interface, x, y, z, w))
                        .connect()
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

                        await asyncio.sleep(1)

        except (KeyboardInterrupt, Exception) as e:
            self.conn.stop()
            for wand in wands:
                wand.disconnect()
            wands.clear()
            exit(1)

    async def ping_clients_forever(self):
        try:
            while self.run:
                self.conn.ping_collect_clients()
                await asyncio.sleep(1)

        except (KeyboardInterrupt, Exception) as e:
            exit(1)

    async def loop_state(self):
        try:
            while self.run:
                await self.get_state().on_loop()

        except (KeyboardInterrupt, Exception) as e:
            exit(1)

    def set_state(self, state):
        self._state = state(self)
        return self._state

    def get_state(self):
        return self._state

class ServerState():
    def __init__(self, manager):
        self.manager = manager
        self.conn = manager.conn
        self.interface = None

    def on_post_connect(self, interface):
        self.interface = interface
        interface.subscribe_button()
        interface.subscribe_position()

    def on_post_disconnect(self, interface):
        pass

    def on_quaternion(self, interface, x, y, z, w):
        pass

    def on_button_press(self, interface, pressed):
        pass

    async def on_loop(self):
        pass

    def switch(self, state):
        return self.manager.set_state(state)


class GestureCaptureState(ServerState):
    def __init__(self, manager):
        super(GestureCaptureState, self).__init__(manager)

        self.pressed = False
        self.positions = []
        self.spell = None
        self.speed_clicks = 0
        self.press_start = self.press_end = timeit.default_timer()

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

        self.conn.signed_publish(TOPICS.QUATERNIONS.value, ClientConnection.data_encode(
            ClientConnection.addressed_payload("", "%d %d %d %d" % (x, y, z, w))
        ))

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
                self.positions = []
                interface.reset_position()
                self.speed_clicks += 1

                if self.speed_clicks == 2:
                    interface.vibrate(PATTERN.BURST)
                    self.switch(SERVER_STATES.PROFILE_SELECT.value)

            else:
                self.speed_clicks = 0

                if self.press_end - self.press_start > 7:
                    interface.disconnect()
                    exit(0)

                else:
                    gesture = moosegesture.getGesture(self.positions)
                    self.positions = []

                    closest = moosegesture.findClosestMatchingGesture(gesture, self.gestures, maxDifference=1)

                    if closest:
                        self.spell = self.gestures[closest[0]]
                        self.conn.signed_publish(TOPICS.SPELLS.value, ClientConnection.data_encode(
                            ClientConnection.addressed_payload("", {"gesture": gesture, "spell": self.spell})
                        ))

                    print("{}: {}".format(gesture, self.spell))


class ProfileSelectState(ServerState):
    def __init__(self, manager):
        super(ProfileSelectState, self).__init__(manager)

        self.pressed = False
        self.speed_clicks = 0
        self.quaternion_state = _h.Quaternion(0, 0, 0, 0)

    def on_quaternion(self, interface, x, y, z, w):
        self.quaternion_state.x = x
        self.quaternion_state.y = y
        self.quaternion_state.x = z
        self.quaternion_state.w = w

    async def on_loop(self):
        try:
            if self.quaternion_state.w >= 375:
                self.conn.next_profile()
            if self.quaternion_state.w <= -375:
                self.conn.prev_profile()

            print("profile switch", self.conn.current_profile().led_color)
        except Exception as e:
            print(e)

        await asyncio.sleep(1)

    def on_button_press(self, interface, pressed):
        if pressed:
            self.press_start = timeit.default_timer()

            if self.press_start - self.press_end > .2:
                self.speed_clicks = 0
        else:
            self.press_end = timeit.default_timer()

            if self.press_end - self.press_start < .2:
                self.positions = []
                interface.reset_position()
                self.speed_clicks += 1

                if self.speed_clicks == 2:
                    interface.vibrate(PATTERN.BURST)
                    self.switch(SERVER_STATES.GESTURE_CAPTURE.value)

            else:
                self.speed_clicks = 0

                if self.press_end - self.press_start > 7:
                    interface.disconnect()
                    exit(0)



class SERVER_STATES(Enum):
    GESTURE_CAPTURE = GestureCaptureState
    PROFILE_SELECT = ProfileSelectState