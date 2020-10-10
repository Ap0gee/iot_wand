import os
import subprocess
import iot_wand.clients.settings as _s
from iot_wand import helpers as _h
import asyncio

def main(dir_top):
    config = _h.yaml_read(_s.PATH_CONFIG)
    active_clients = config['active']
    tasks = []
    loop = asyncio.get_event_loop()
    if len(active_clients):
        for entry in os.scandir(_s.DIR_BASE):
            if os.path.isdir(entry.path) and entry.name in config['active']:
                print("Activating client: %s..." % entry.name)
                path_client = entry.path
                cmd = "python %s %s" % (os.path.join(path_client, 'client.py'), dir_top)
                tasks.append(start_process(cmd))

        clients = asyncio.gather(*tasks)
        loop.run_until_complete(clients)

    else:
        print("No active clients.")

async def start_process(cmd):
    subprocess.call(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    await asyncio.
