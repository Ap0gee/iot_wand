from iot_wand import helpers as _h
import settings as _s

_h.restrict_client_system(_h.SYSTEMS.WINDOWS)

import win32api

x_dim = win32api.GetSystemMetrics(0)
y_dim = win32api.GetSystemMetrics(1)

def on_button(pressed):
    pass

def on_spell(gesture, spell):
    print(gesture, spell)

def on_quaternion(x, y, z, w):
    x_pos = int(round(x_dim * ((int(x) * 4 + 1000) / 2000)))
    y_pos = int(round(y_dim * (1 - (int(y) * 4 + 1000) / 2000)))

    print(x_pos, y_pos)

    win32api.SetCursorPos((x_pos, y_pos))