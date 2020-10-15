import platform
import os
import subprocess
import sys
import time
import signal

def mk_server_cmd(dir, module, new_terminal=True):
    import iot_wand.server.settings as _s

    system = platform.system()
    print(system)
    python = 'python'
    terminal_cmd = 'start cmd /K'
    if system == 'Linux':
        terminal_cmd = 'lxterminal'
        python = '%s' % os.path.join(dir, 'env/bin/python3')
    print(python)
    path_module = os.path.join(_s.DIR_BASE, module)
    if new_terminal:
        cmd = '%s %s %s %s' % (terminal_cmd, python, path_module, dir)
    else:
        cmd = '%s %s %s' % (python, path_module, dir)
    print(cmd)
    return cmd

def main(dir_top):
    cmd = mk_server_cmd(dir_top, 'server_manager.py')
    return subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

if __name__ == '__main__':
    dir_top = sys.argv[1]
    sys.path.append(dir_top)
    cmd = mk_server_cmd(dir_top, 'server.py', new_terminal=False).split()
    try:
        while 1:
            print('Spawning server process...')
            print(cmd)
            try:
                process = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                #non-zero exit status
                if e.returncode == 2:
                    continue
                else:
                    print(e.output)
                    exit(1)
            time.sleep(3)
            continue
    except KeyboardInterrupt as e:
        exit(1)