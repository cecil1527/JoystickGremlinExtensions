"""a single point of contact with joystick gremlin in case it changes"""

"""
https://stackoverflow.com/questions/3496592/conditional-import-of-modules-in-python

if you run the code from a JG plugin, it should import the real gremlin package.
but if you run the code standalone, then it'll import my little mock package
instead
"""

try:
    import gremlin
except ImportError:
    import jge.gremlin_mock as gremlin

from jge.utils import utils


def _get_vjoy_proxy():
    vjoy_proxy = gremlin.joystick_handling.VJoyProxy()
    # gremlin.util.log(f"vjoy_proxy = {vjoy_proxy}")
    return vjoy_proxy

    # NOTE as far as i can tell:
    # * VJoyProxy just contains a static dictionary of vjoy devices
    # * it implements __getitem__(), so you can get the first, second, etc. vjoy
    #   device
    # * from that device, you can get a button or axis and set their values
    #
    # i think that's right
    # * because if you log vjoy proxy IDs, they're all different, but each
    #   instance of the proxy class doesn't matter, only the class's static
    #   dictionary matters.
    # * and if you log a device's button/axis IDs, they're all the same for a
    #   particular index, so it'a all pointing to the same underlying object for
    #   that button/axis.


def _get_vjoy_button(button_id: int, device_id: int):
    proxy = _get_vjoy_proxy()
    return proxy[device_id].button(button_id)


def _get_vjoy_axis(axis_id: int, device_id: int):
    proxy = _get_vjoy_proxy()
    return proxy[device_id].axis(axis_id)


class VjoyAxis:
    def __init__(self, axis_id: int, device_id: int) -> None:
        self.__axis = _get_vjoy_axis(axis_id, device_id)

    def get_val(self) -> float:
        return self.__axis.value

    def set_val(self, val) -> None:
        val = utils.clamp(val, -1.0, 1.0)
        self.__axis.value = val

        # NOTE JG clamps values that are OOB before sending them to vjoy, but it
        # will spam the system log with warnings when doing it, so clamp here
        # before setting vjoy axis val

    def inc_val(self, delta) -> None:
        """increment axis value by delta"""

        # use set val so it clamps correctly
        self.set_val(self.get_val() + delta)


class VjoyButton:
    def __init__(self, button_id: int, device_id: int) -> None:
        self.__button = _get_vjoy_button(button_id, device_id)

    def is_pressed(self) -> bool:
        return self.__button.is_pressed

    def set_pressed(self, b: bool) -> None:
        self.__button.is_pressed = b

    def press(self) -> None:
        self.set_pressed(True)

    def release(self) -> None:
        self.set_pressed(False)
