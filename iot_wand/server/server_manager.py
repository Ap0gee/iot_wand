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
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

if __name__ == '__main__':
    print('Starting server manager...')
    dir_top = sys.argv[1]
    sys.path.append(dir_top)
    cmd = mk_server_cmd(dir_top, 'server.py', new_terminal=True)
    process_needed = True
    try:
        while 1:
            try:
                if process_needed:
                    print('Spawning server process...')
                    process = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    process.wait()
                    process_needed = True
                    continue
            except (Exception, subprocess.CalledProcessError) as e:
                print("EXCEPTION IN CHILD PROCESS")
                #non-zero exit status
                if isinstance(e, subprocess.CalledProcessError):
                    if e.returncode != 0:
                        process_needed = True
                        continue
                print(e)
                exit(1)
            print('Waiting for process to exit...', end="\r")
            time.sleep(3)
            continue
    except KeyboardInterrupt as e:
        exit(1)