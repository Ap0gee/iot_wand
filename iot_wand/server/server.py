from iot_wand.mqtt_connections import GestureServer, ClientConnection, TOPICS
from iot_wand.btle_scanners import WandScanner
from iot_wand.btle_inerfaces import GestureInterface
import iot_wand.server.settings as _s
import iot_wand.helpers as _h
import asyncio
import time

def main():
    config = _h.yaml_read(_s.PATH_CONFIG)
    conn = GestureServer(config, debug=_s.DEBUG)
    conn.start(async=True, async_callback=lambda _conn: __async_callback(conn, _s.DEBUG))

def __async_callback(conn, debug):
    wands = []
    wand_scanner = WandScanner(debug=debug)
    loop = asyncio.get_event_loop()
    lock = asyncio.Lock()
    run = True

    try:
        while run:
            if not len(wands):
                wands = [
                    GestureInterface(device, debug=debug).connect()
                    .on('post_connect', lambda interface: __on_post_connect(interface, conn, loop, lock))
                    .on('spell', lambda gesture, spell: __on_spell(gesture, spell, conn))
                    .on('position', lambda x, y, z, w: __on_quaternion(x, y, z, w, conn))
                    .on('post_disconnect', lambda interface: __on_post_disconnect(interface, conn))
                    for device in wand_scanner.scan()
                ]
            else:
                if not wands[0].connected:
                    wands.clear()
                time.sleep(1)

    except (KeyboardInterrupt, Exception) as e:
        conn.stop()
        for wand in wands:
            wand.disconnect()
        wands.clear()


def __on_post_connect(interface, conn, loop, lock):
    pass

def __on_post_disconnect(interface, conn):
    pass


def __on_spell(gesture, spell, conn):
    conn.signed_publish(TOPICS.SPELLS.value, ClientConnection.data_encode({"gesture": gesture, "spell": spell}))


def __on_quaternion(x, y, z, w, conn):
    conn.signed_publish(TOPICS.QUATERNIONS.value, ClientConnection.data_encode(','.join([x, y, z, w])))
