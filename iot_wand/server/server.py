from iot_wand.mqtt_connections import GestureServer
from iot_wand.btle_scanners import WandScanner
from iot_wand.btle_inerfaces import GestureInterface
import iot_wand.server.settings as _s
import iot_wand.helpers as _h
import threading
import time
import random

def main():
    config = _h.yaml_read(_s.PATH_CONFIG)
    conn = GestureServer(config, debug=_s.DEBUG)
    conn.start(async=True, async_callback=lambda conn: async_callback(conn, debug=_s.DEBUG))

def ensure_wand_connected(conn, wands, lock, stop, debug):
    wand_scanner = WandScanner(conn, GestureInterface, debug=debug)
    while True:
        if stop():
            break
        
        if len(wands) == 0:
            lock.acquire()
            print('connecting')
            wands = wand_scanner.scan(connect=True)
            lock.release()
        else:
            if not wands[0].connected:
                lock.acquire()    
                wands.clear()
                lock.release()
        
    
    print('out of loop')

def async_callback(conn, debug=False):
    wands = []
    workers = []
    stop_threads = False
    lock = threading.Lock()

    workers.append(
        threading.Thread(
            name="ensure_wand_connected",
            target=ensure_wand_connected,
            args=(conn, wands, lock, lambda: stop_threads, debug)
        )
    )

    try:
        _h.start_threads(*workers)

        while 1:
            print(len(wands))
            time.sleep(1)

    except (KeyboardInterrupt, Exception) as e:
        stop_threads = True
        _h.join_threads(*workers)
        conn.disconnect()
        for wand in wands:
            wand.disconnect()
        wands.clear()

if __name__ == "__main__":
    main()
