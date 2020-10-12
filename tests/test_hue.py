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
                _hue_service = lamp.getServiceByUUID('932c32bd-0000-47a2-835a-a8d455b859dd')
                handle = _hue_service.getCharacteristics('932c32bd-0002-47a2-835a-a8d455b859dd')[0]
                _handle = handle.getHandle()
                print(handle)
                resp = lamp.readCharacteristic(_handle)
                print("READING...")
                print(resp.decode('utf-8'))
            except Exception as e:
                print(e)


if __name__ == '__main__':
    main()
    input()