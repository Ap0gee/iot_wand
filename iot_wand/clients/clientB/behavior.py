from iot_wand import helpers as _h
import settings as _s
from pymouse import PyMouse

_m = PyMouse()
x_dim, y_dim = _m.screen_size()

def on_spell(gesture, spell):
    print(spell)

def on_quaternion(x, y, z, w):
    x_pos = x_dim * ((x * 4 + 1000) / 2000)
    y_pos = y_dim * (1.0 - (y * 4 + 1000) / 2000)
    # Move the mouse
    _m.move(int(round(x_pos)), int(round(y_pos)))