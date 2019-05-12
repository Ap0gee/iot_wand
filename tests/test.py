import asyncio
from iot_wand.mqtt_connections import ClientConnection, TOPICS
import iot_wand.helpers as _h
import iot_wand.server.settings as _s
import time

def main():
    config = _h.yaml_read(_s.PATH_CONFIG)
    conn = ClientConnection(config, debug=_s.DEBUG)
    conn.start()

    run = True
    try:
        while run:
            conn.signed_publish(TOPICS.QUATERNIONS.value, ClientConnection.data_encode({'x': 1, 'y': 2, 'z': 3, 'w': 4}))
            time.sleep(1)
    except (KeyboardInterrupt, Exception) as e:
        exit(0)

if __name__ == '__main__':
   main()