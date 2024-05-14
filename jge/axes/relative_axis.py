import threading
import time

from jge.utils.easing_functions import EasingGenerator
from jge.gremlin_interface import VjoyAxis


class RelativeAxis:
    # TODO async threads get a little weird if you use this with a hat switch,
    # because you can do a circle on the hat and potentially start a second
    # competing thread that'll be incrementing the axis in the other direction.
    # (because you never released the hat - never went back to the hat's central
    # position)
    #
    # actually you can easily do it with two buttons as well. holding button 1
    # to inc the axis and then holding button 2 to dec the axis results in two
    # competing threads and releasing either of the buttons stops it all.
    #
    # i'm just going to leave it for now. i'm not sure of a simple way to fix
    # that behavior. it's tempting to keep a list of presses and delete an entry
    # on release and only stop once the list is empty, but that won't work with
    # hats which can have a different number of presses/releases if you do
    # circles.

    def __init__(
        self, axis_id: int, easing_generator: EasingGenerator, device_id: int = 1
    ) -> None:
        """
        controls a vjoy axis, as a relative axis, based on button presses.

        Args:
            * axis_id (int): vjoy axis ID
            * easing_generator (EasingGenerator): easing generator used to
              increment the relative axis
            * device_id (int, optional): vjoy device ID. Defaults to 1.

        NOTE JG basically already has this functionality. you can do a repeating
        macro to inc/dec an axis while you hold a button, but it's at a constant
        velocity. i want the ability to customize the acceleration of the axis
        to be able to interact with it more smoothly.
        """

        self._axis = VjoyAxis(axis_id, device_id)
        self._easing_generator = easing_generator.copy()
        # keeps track of if button is pressed or not (for the async timer)
        self._is_pressed = False

    def press(self, direction: int):
        """
        starts the relative axis's motion

        :param direction: either 1 or -1
        :return:
        """

        self._is_pressed = True
        threading.Thread(target=self.__run_async, args=[direction]).start()

    def release(self):
        """stops the relative axis's motion"""

        self._is_pressed = False

    def __run_async(self, direction: int):
        # NOTE this should only ever be called on a separate thread because it
        # uses sleep, which will block the rest of the JG python code from
        # running

        # smoothly moves the axis while the button is pressed

        self._easing_generator.reset()
        while self._is_pressed:
            output = self._easing_generator.get_output()

            # direction will either be +-1
            self._axis.inc_val(direction * output)
            time.sleep(self._easing_generator.get_sleep_time())
