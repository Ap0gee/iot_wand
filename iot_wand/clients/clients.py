import os
import subprocess
import iot_wand.clients.settings as _s
from iot_wand import helpers as _h
import platform

def main(dir_top):
    config = _h.yaml_read(_s.PATH_CONFIG)
    active_clients = config['active']
    if len(active_clients):
        for entry in os.scandir(_s.DIR_BASE):
            if os.path.isdir(entry.path) and entry.name in config['active']:
                print("Activating client: %s..." % entry.name)
                path_client = entry.path
                system = platform.system()
                python = 'python'
                terminal_cmd = 'start cmd /K'
                if system == 'Linux':
                    terminal_cmd = 'lxterminal -e'
                    python = '$py3'
                cmd = "%s %s %s %s" % (terminal_cmd, python, os.path.join(path_client, 'client.py'), dir_top)
                subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        print("No active clients.")


