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
import threading


def main():
    config = _h.yaml_read(_s.PATH_CONFIG)
    conn = GestureServer(config, debug=_s.DEBUG)
    conn.start(as_async=True, async_callback=lambda _conn: AsyncServerStateManager(_conn, config, _s.DEBUG))


class AsyncServerStateManager:
    def __init__(self, mqtt_conn, config, debug=False):
        self._lock = threading.Lock()
        self.conn = mqtt_conn
        self.interface = None
        self._state = self.set_state(SERVER_STATES.GESTURE_CAPTURE.value)
        self._wand_management_thread = None
        self._ping_clients_thread = None
        self._loop_state_thread = None
        self.run = True

        if not self._wand_management_thread:
            self._wand_management_thread = threading.Thread(target=self._manage_wands, args=(debug, config))
            self._wand_management_thread.start()

        if not self._loop_state_thread:
            self._loop_state_thread = threading.Thread(target=self._loop_state)
            self._loop_state_thread.start()

    def _manage_wands(self, debug, config):
        wands = []
        broker = config['broker']
        try:
            sec_ka = 0
            sec_ka_max = broker['keepalive']
            wand_scanner = WandScanner(debug=debug)

            while self.run:
                with self._lock:
                    if not len(wands):
                        wands = [
                            GestureInterface(device, debug=debug)
                            .on('post_connect', lambda interface: self.get_state().on_post_connect(interface))
                            .on('post_disconnect', lambda interface: self.get_state().on_post_disconnect(interface))
                            .on('button_press', lambda interface, pressed: self.get_state().on_button_press(interface, pressed))
                            .on('quaternion', lambda interface, x, y, z, w: self.get_state().on_quaternion(interface, x, y, z, w))
                            .connect()
                            for device in wand_scanner.scan(discovery_callback=self._on_discovery)
                        ]
                    else:
                        if not wands[0].connected:
                            wands.clear()
                            sec_ka = 0
                        else:
                            if sec_ka >= sec_ka_max:
                                sec_ka = 0
                                if wands[0].should_keep_alive():
                                    wands[0].keep_alive()
                                else:
                                    if debug:
                                        print('skipping keep alive')
                                wands[0].resume_keep_alive()
                            else:
                                sec_ka += 1

                        self.conn.ping_collect_clients()
                        time.sleep(1)

        except (KeyboardInterrupt, Exception) as e:
            #self.conn.stop()
            #self.run = False
            #for wand in wands:
            #    wand.disconnect()
            #wands.clear()
            #self._wand_management_thread.join()
            #exit(1)
            print(e)

    def _on_discovery(self, devices):
        print('setting state to capture gesture state')
        self.set_state(SERVER_STATES.GESTURE_CAPTURE.value)

    def _loop_state(self):
        while 1:
            self.get_state().on_loop()
            time.sleep(2)

    def set_state(self, state):
        self._state = state(self)
        return self._state

    def get_state(self):
        return self._state


class ServerState():
    def __init__(self, manager):
        self.manager = manager
        self.conn = manager.conn
        self.interface = manager.interface

    def on_post_connect(self, interface):
        self.manager.interface = interface
        self.interface = interface
        interface.subscribe_button()
        interface.subscribe_position()

    def on_post_disconnect(self, interface):
        pass

    def on_quaternion(self, interface, x, y, z, w):
        pass

    def on_button_press(self, interface, pressed):
        pass

    def on_loop(self):
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

        if self.interface:
            if self.interface.debug:
                print("resuming keep alive...")
            self.interface.resume_keep_alive()

    def on_quaternion(self, interface, x, y, z, w):
        if self.pressed:
            self.positions.append(tuple([x, -1 * y]))

        self.conn.signed_addressed_publish(
            TOPICS.QUATERNIONS.value,
            self.conn.current_profile().uuid,
            ClientConnection.data_encode("%d %d %d %d" % (x, y, z, w))
        )

    def on_button_press(self, interface, pressed):
        self.conn.signed_addressed_publish(
            TOPICS.BUTTON.value,
            self.conn.current_profile().uuid,
            ClientConnection.data_encode(bytes(pressed))
        )
        self.pressed = pressed

        if pressed:
            self.spell = None
            self.press_start = timeit.default_timer()

            if self.press_start - self.press_end > .4:
                self.speed_clicks = 0

        else:
            self.press_end = timeit.default_timer()

            if self.press_end - self.press_start < .4:
                self.positions = []
                interface.reset_position()
                self.speed_clicks += 1

                if self.speed_clicks == 2:
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
                        self.conn.signed_addressed_publish(
                            TOPICS.SPELLS.value,
                            self.conn.current_profile().uuid,
                            ClientConnection.data_encode({"gesture": gesture, "spell": self.spell})
                        )

                    print("{}: {}".format(gesture, self.spell))

class ProfileSelectState(ServerState):
    def __init__(self, manager):
        super(ProfileSelectState, self).__init__(manager)

        self.pressed = False
        self.speed_clicks = 0
        self.quaternion_state = _h.Quaternion(0, 0, 0, 0)
        self.last_profile_uuid = None
        self.conn.clear_current_profile()
        self.press_start = self.press_end = timeit.default_timer()
        self.connections_count = len(self.conn.profiles())
        self.interface.pause_keep_alive() #pause keep alive to avoid write conflicts (guessing)
        self.interface.set_led('#ffffff', True)
        self.interface.vibrate(PATTERN.BURST)

    def on_quaternion(self, interface, x, y, z, w):
        self.quaternion_state.x = x
        self.quaternion_state.y = y
        self.quaternion_state.x = z
        self.quaternion_state.w = w

    def on_loop(self):
        try:
            print('profile select loop')

            if self.quaternion_state.w >= 375:
                self.conn.next_profile()
            if self.quaternion_state.w <= -375:
                self.conn.prev_profile()

            print(self.conn._client_profiles)
            print(self.conn._selected_profile_index)

            profile = self.conn.current_profile()

            if profile.uuid != self.last_profile_uuid:
                print('switching to', profile.uuid)
                print(profile.vibrate_on)
                print(profile.vibrate_pattern)
                self.last_profile_uuid = profile.uuid

                if profile.vibrate_on:
                    self.interface.vibrate(profile.vibrate_pattern)

                #time.sleep(.5) #add time between writes to avoid conflict (guessing)

                self.interface.set_led(profile.led_color, profile.led_on)


        except (KeyboardInterrupt, Exception) as e:
            print(e)
            #exit(1)

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