from iot_wand import helpers as _h
import settings as _s
import time
import win32api

current = win32api.GetCursorPos()
x_dim = win32api.GetSystemMetrics(0)
y_dim = win32api.GetSystemMetrics(1)

def on_spell(gesture, spell):
    print(spell)

def on_quaternion(x, y, z, w):
    x_pos = x_dim * ((x * 4 + 1000) / 2000)
    y_pos = y_dim * (1.0 - (y * 4 + 1000) / 2000)
    print(int(round(x_pos)),int(round(y_pos)))

    win32api.SetCursorPos((int(round(x_pos)),int(round(y_pos))))