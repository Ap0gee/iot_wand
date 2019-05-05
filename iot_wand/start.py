from settings import *

from wand import WandScanner
from interfaces import GestureCapture
from connections import GestureServer
from helpers import YamlManager


def main():
    config = YamlManager(CONFIG_PATH).read()
    server = config['server']

    mqtt_conn = GestureServer(
        server['hostname'],
        port=server['port'],
        keepalive=server['keepalive'],
        bind_address=server['bind_address']
    )

    mqtt_conn.subscribe_internal()
    mqtt_conn.loop()

    wand_scanner = WandScanner(mqtt_conn, wand_interface=GestureCapture, debug=DEBUG)

    wands = []

    try:
        while len(wands) == 0:
            print("Scanning...")
            wands = wand_scanner.scan(connect=True)

    except (KeyboardInterrupt, Exception) as e:
        for wand in wands:
            wand.disconnect()


if __name__ == "__main__":
    main()



