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
            try:
                services = lamp.getServices()
                for service in services:
                    print('----------service--------')
                    print(service.uuid)
                    print('------------------------')
                    for char in service.getCharacteristics():
                        print(char.uuid)
                        print("HANDLE=" + str(char.getHandle()))
                        print(char.propertiesToString())
                       
                    print('------------------------', end="\r\n\r\n")
            except Exception as e:
                print(e)


if __name__ == '__main__':
    main()
    input()