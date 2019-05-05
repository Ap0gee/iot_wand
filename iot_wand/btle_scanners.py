from bluepy.btle import *

class WandScanner(DefaultDelegate):
    """A scanner class to connect to wands
    """

    def __init__(self, mqtt_conn, wand_interface, debug=False):
        """Create a new scanner

        Keyword Arguments:
            wand_interface {class} -- Class to use when connecting to wand (default: {WandInterface})
            debug {bool} -- Print debug messages (default: {False})
        """
        super().__init__()
        self.debug = debug
        self._name = None
        self._prefix = None
        self._mac = None
        self._scanner = Scanner().withDelegate(self)
        self._devices = []
        self._wand_interface = wand_interface
        self._mqtt_conn = mqtt_conn

    def scan(self, name=None, prefix="Kano-Wand", mac=None, timeout=1.0, connect=False):
        """Scan for devices

        Keyword Arguments:
            name {str} -- Name of the device to scan for (default: {None})
            prefix {str} -- Prefix of name of device to scan for (default: {"Kano-Wand"})
            mac {str} -- MAC Address of the device to scan for (default: {None})
            timeout {float} -- Timeout before returning from scan (default: {1.0})
            connect {bool} -- Connect to the wands automatically (default: {False})

        Returns {Wand[]} -- Array of wand objects
        """

        if self.debug:
            print("Scanning for {} seconds...".format(timeout))
        try:
            name_check = not (name is None)
            prefix_check = not (prefix is None)
            mac_check = not (mac is None)
            assert name_check or prefix_check or mac_check
        except AssertionError as e:
            print("Either a name, prefix, or mac address must be provided to find a wand")
            raise e

        if name is not None:
            self._name = name
        elif prefix is not None:
            self._prefix = prefix
        elif mac is not None:
            self._mac = mac

        self._interfaces = []
        self._scanner.scan(timeout)
        # after self._scanner.handleDiscovery -->
        if connect:
            for interface in self._interfaces:
                #start behavior -->
                interface.connect()
        return self._interfaces

    def handleDiscovery(self, device, isNewDev, isNewData):
        """Check if the device matches

        Arguments:
            device {bluepy.ScanEntry} -- Device data
            isNewDev {bool} -- Whether the device is new
            isNewData {bool} -- Whether the device has already been seen
        """

        if isNewDev:
            # Perform initial detection attempt
            mode = 0
            found = 0
            name = device.getValueText(9)
            if self._name is not None:
                mode += 1
                if name == self._name:
                    found += 1
            if self._prefix is not None:
                mode += 1
                if name is not None and name.startswith(self._prefix):
                    found += 1
            if self._mac is not None:
                mode += 1
                if device.addr == self._mac:
                    found += 1

            if found >= mode:
                self._interfaces.append(self._wand_interface(device, self._mqtt_conn, debug=self.debug))

            elif self.debug:
                if name != "None":
                    print("Mac: {}\tCommon Name: {}".format(device.addr, name))
                else:
                    print("Mac: {}".format(device.addr))

        
