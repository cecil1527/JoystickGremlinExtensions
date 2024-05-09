import threading
import time


class Tempo:
    def __init__(self, short_press_callable, long_press_callable, delay_s=1.0):
        """
        a tempo is a short vs long press container.

        Args:
            * short_press_callable: callable to run on a short press
            * long_press_callable: callable to run on a long press
            * delay_s (float, optional): how long to wait before a press is
              considered a long press. Defaults to 1.0.
        """

        self._short_callable = short_press_callable
        self._long_callable = long_press_callable
        self._delay_s = delay_s

        self._pressed = False
        self._did_long_press = False

        self._press_id = 0
        # NOTE bah, i want the long press to automatically execute after the
        # delay. i don't want you to be forced to release the button to have it
        # execute. but if you press, release, and press again the thread will
        # have no idea that it's a new press, so every press is going to get a
        # UID for now.

    def __run_async(self, press_id):
        time.sleep(self._delay_s)
        # only execute if we're still on the same press after sleeping
        if self._pressed and self._press_id == press_id:
            self._did_long_press = True
            self._long_callable()

    def press(self):
        self._pressed = True
        self._press_id += 1
        threading.Thread(target=self.__run_async, args=[self._press_id]).start()

    def release(self):
        self._pressed = False

        # only do short press if long press hasn't been executed
        if not self._did_long_press:
            self._short_callable()

        self._did_long_press = False
