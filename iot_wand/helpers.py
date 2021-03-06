import yaml
import io
import timeit

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