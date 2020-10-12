from iot_wand.btle_scanners import HueScanner
from iot_wand.btle_inerfaces import HueInterface

lights = []

def main():
    global lights
    debug = True
    hue_scanner = HueScanner(debug=debug)
    if not len(lights):
        lights = [
            HueInterface(device, debug=debug).connect()
            for device in hue_scanner.scan()
        ]

    for light in lights:
        try:
            services = light.getServices()
            for service in services:
                print('----------service--------')
                print(service.uuid)
                print('------------------------')
                for char in service.getCharacteristics():
                    print(char.uuid)
                    print("HANDLE=" + str(char.getHandle()))
                    print(char.propertiesToString())
                print('------------------------', end="\r\n\r\n")

            print('writing to handle 39')
            light.writeCharacteristic(39, bytes([1]))
            print('reading val')
            resp = light.readCharacteristic(39)
            print(resp)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
    input()