'''a single point of contact with joystick gremlin in case it changes'''

# real Gremlin section ---------------------------------------------------------
# import gremlin

# def _get_vjoy_proxy():
#     vjoy_proxy = gremlin.joystick_handling.VJoyProxy()
#     # gremlin.util.log(f"vjoy_proxy = {vjoy_proxy}")
#     return vjoy_proxy

#     # NOTE as far as i can tell:
#     # * VJoyProxy just contains a static dictionary of vjoy devices
#     # * it implements __getitem__(), so you can get the first, second, etc. vjoy
#     #   device
#     # * from that device, you can get a button or axis and set their values
#     #
#     # i think that's right
#     # * because if you log vjoy proxy IDs, they're all different, but each
#     #   instance of the proxy class doesn't matter, only the class's static
#     #   dictionary matters. 
#     # * and if you log a device's button/axis IDs, they're all the same for a
#     #   particular index, so it'a all pointing to the same underlying object.

# def _get_vjoy_button(button_id: int, device_id: int):
#     proxy = _get_vjoy_proxy()
#     return proxy[device_id].button(button_id)


# def _get_vjoy_axis(axis_id: int, device_id: int):
#     proxy = _get_vjoy_proxy()
#     return proxy[device_id].axis(axis_id)
# ------------------------------------------------------------------------------


# Mock section for testing -----------------------------------------------------
class MockAxis:
    def __init__(self, axis_id: int, device_id: int) -> None:
        self.id = axis_id
        self.value = 0.0


class MockButton:
    def __init__(self, button_id: int, device_id: int) -> None:
        self.id = button_id
        self.is_pressed = False


def _get_vjoy_button(button_id: int, device_id: int):
    return MockButton(button_id, device_id)


def _get_vjoy_axis(axis_id: int, device_id: int):
    return MockAxis(axis_id, device_id)
# ------------------------------------------------------------------------------


class VjoyAxis:
    def __init__(self, axis_id: int, device_id: int) -> None:
        self.__axis = _get_vjoy_axis(axis_id, device_id)

    def get_val(self) -> float:
        return self.__axis.value
    
    def set_val(self, val) -> None:
        self.__axis.value = val

    def inc_val(self, delta) -> None:
        '''increment axis value by delta'''
        self.__axis.value += delta

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