import time
from gremlin_interface import VjoyButton

class DoubleClickToggle:

    def __init__(self, button_id: int, double_click_time_s: float, device_id: int = 1):
        """
        controls a vjoy button, toggling it on/off depending on if you double
        click. double clicking will keep the button on until it's pressed again.

        Args:
            * button_id (int): vjoy button ID
            * double_click_time_s (float): double click time in seconds
            * device_id (int, optional): vjoy device ID, in case you need to use
              a vjoy device other than 1. Defaults to 1.
        """

        self._button = VjoyButton(button_id, device_id)
        self._double_click_time_s = double_click_time_s

        self._t0 = 0
        self._t1 = 0

    def press(self):
        """
        presses the button
        """
        self._t0 = self._t1
        self._t1 = time.time()

        self._button.press()

    def release(self):
        """
        releases the button, but only if we haven't double clicked it
        """

        diff = self._t1 - self._t0
        # print(f"{diff=}")
        if diff > self._double_click_time_s:
            self._button.release()
        # else the button stays on

    def force_release(self):
        """
        forces the release of the button
        """
        self._button.release()


if __name__ == "__main__":
    d = DoubleClickToggle(10, 0.1, 1)

    for i in range(2):
        d.press()
        time.sleep(0.1)
        d.release()
        time.sleep(0.1)
    assert not d._button.is_pressed()

    for i in range(2):
        d.press()
        time.sleep(0.035)
        d.release()
        time.sleep(0.035)
    assert d._button.is_pressed()