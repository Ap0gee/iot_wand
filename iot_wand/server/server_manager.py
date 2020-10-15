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
        terminal_cmd = 'lxterminal -e'
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
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()[0]
    if p.returncode != 0:
           print("CAPTURED OUTPUT FROM MAIN %s %s" % (p.returncode, output))

if __name__ == '__main__':
    print('Starting server manager...')
    dir_top = sys.argv[1]
    sys.path.append(dir_top)
    cmd = mk_server_cmd(dir_top, 'server.py', new_terminal=True)

    try:
        p = subprocess.run(cmd, shell=True)
        p.check_returncode()
        input()
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        input()

