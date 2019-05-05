from iot_wand.mqtt_connections import GestureServer
from iot_wand.btle_scanners import WandScanner
from iot_wand.btle_inerfaces import GestureInterface
import iot_wand.server.settings as _s
import iot_wand.helpers as _h
import argparse

def main():
    config = _h.yaml_read(_s.PATH_CONFIG)
    conn = GestureServer(config, wand_scanner=WandScanner, wand_interface=GestureInterface, debug=_s.DEBUG)
    conn.start()

if __name__ == "__main__":
    main()