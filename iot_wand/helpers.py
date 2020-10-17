import yaml
import io
import timeit
import platform
from enum import Enum

class SYSTEMS(Enum):
    LINUX = 'Linux'
    WINDOWS = 'Windows'

class Quaternion():
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

def yaml_read(path, mode="r"):
    with open(path, mode) as stream:
        return (yaml.safe_load(stream))

def yaml_write(data, path, mode="w", encoding="utf8"):
    with io.open(path) as outfile:
        yaml.safe_dump(data, outfile, default_flow_style=False, allow_unicode=True)

def b_decode(bytes, encoding="utf-8"):
    return bytes.decode(encoding)

def check_key(dict, key):
    return key in dict.keys()

def now():
    return timeit.default_timer()

def elapsed(start):
    return now() - start

def dd(*args):
    print(*args)
    exit(0)

def join_threads(*threads):
    for thread in threads:
        thread.join()

def start_threads(*threads):
    for thread in threads:
        thread.start()

def restrict_client_system(system):
    if isinstance(system, SYSTEMS):
        system = system.value
    _system = platform.system()
    if _system != system:
        print('This client was intended for %s systems only.' % system)
        exit(1)