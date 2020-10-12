from iot_wand.btle_scanners import HueScanner
from iot_wand.btle_inerfaces import HueInterface

def main():
    lights = []
    debug = True
    hue_scanner = HueScanner(debug=debug)
    if not len(lights):
        lamps = [
            HueInterface(device, debug=debug).connect()
            for device in hue_scanner.scan()
        ]

        for lamp in lamps:
            for char in lamp.getCharacteristics():
                try:
                    print('writing')
                    char.write(0)
                except Exception as e:
                    print(e)

if __name__ == '__main__':
    main()
    input()