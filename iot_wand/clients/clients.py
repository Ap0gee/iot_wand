import os
import subprocess
import iot_wand.clients.settings as _s
from iot_wand import helpers as _h
import platform
import threading

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
                title = os.path.basename(path_client)
                terminal_cmd = 'start cmd /K'
                print(system)
                if system == 'Linux':
                    terminal_cmd = 'lxterminal -e --title=%s' % title
                    python = '$py3'
                cmd = "%s %s %s %s" % (terminal_cmd, python, os.path.join(path_client, 'client.py'), dir_top)
                print(cmd)
                cmd_thread = threading.Thread(target=open_new_terminal, args=(cmd,))
                cmd_thread.start()

    else:
        print("No active clients.")

def open_new_terminal(cmd):
    subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)