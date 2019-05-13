from enum import Enum

_state = None

class Blah():
    def __init__(self, msg):
        self.msg = msg

class Blah2():
    def __init__(self, msg):
        self.msg = msg

class TEST(Enum):
    A =  Blah
    B =  Blah2

def set_state(state):
    if isinstance(state, TEST):
        state = state.value

    _state = state('test')

    return _state


def main():
    x = TEST.A
    print(set_state(x).msg)


if __name__ == '__main__':
    main()
