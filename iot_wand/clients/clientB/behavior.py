from iot_wand import helpers as _h
import settings as _s
import time
import win32api

current = win32api.GetCursorPos()
cx = sx = current[0]
cy = sy = current[1]

def on_spell(gesture, spell):
    print(spell)

def on_quaternion(x, y, z, w):
    print(x, y)
    win32api.SetCursorPos((int(x),int(y)))