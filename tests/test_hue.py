from iot_wand.btle_scanners import HueScanner
from iot_wand.btle_inerfaces import HueInterface

def main():
    lights = []
    debug = True
    hue_scanner = HueScanner(debug=debug)
    if not len(lights):
        wands = [
            HueInterface(device, debug=debug).connect()
            for device in hue_scanner.scan()
        ]

if __name__ == '__main__':
    main()