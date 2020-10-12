from iot_wand import helpers as _h
import settings as _s

def on_button(pressed):
    pass

def on_spell(gesture, spell):
    print(spell)

def on_quaternion(x, y, z, w):
    print(x, y, x, w)
