import threading
import time

from gremlin_interface import VjoyAxis
import utils

class RelativeAxis:

    # TODO async timers get a little weird if you use it with a hat switch,
    #  because you can do a circle on the hat and potentially start a second
    #  "competing timer" that'll be incrementing the axis in the other
    #  direction. a possible easy fix is a bool to keep track of if a timer is
    #  running, and then have the press() method just do nothing if a timer is
    #  already running.
    #
    # bah, that's a bad answer i think... if you test it with a button, and
    # press button 1 and the relative axis starts moving, then you press button
    # 2, the additional timer gets ignored, BUT if you release button 2, button
    # 1's timer stops... it's like you have to keep track of a list of buttons
    # that get pressed and only stop the timer when that specific button gets
    # released, so i'm not going to worry about it for now. though if you press
    # the hat switch up/down really fast, it does screw up...

    def __init__(self, axis_id: int, max_rate: float = 0.50, 
                 time_to_max_s: float = 2, frequency_hz: int = 10, 
                 device_id: int = 1) -> None:
        """
        controls a vjoy axis, as a relative axis, based on button presses.

        Args:
            * axis_id (int): vjoy axis ID
            * max_rate (float, optional): max rate in axis percent/sec that you
              want the relative axis to be able to move. Defaults to 0.50.
            * time_to_max_s (float, optional): how long (in seconds) you want it
              to take to reach max step size. accepts 0 for instant max.
              Defaults to 2.
            * frequency (int, optional): adjustments per second (Hz). Defaults
              to 10.
            * device_id (int, optional): vjoy device ID. Defaults to 1.
        
        NOTE JG already has this (you can do a repeating macro to inc/dec an
        axis while you hold a button), but it's at a constant velocity and i
        want the motion of the axis to be able to smoothly accelerate.
        """

        self._axis = VjoyAxis(axis_id, device_id)
        # keeps track of if button is pressed or not (for the async timer)
        self._is_pressed = False 

        # precalculate some values
        self._max_step_size = max_rate / frequency_hz
        self._sleep_time = 1.0 / frequency_hz

        if time_to_max_s == 0:
            self._accel_step = self._max_step_size
        else:
            # because frequency * time is how many steps before hitting max step
            # size, the accel step is:
            self._accel_step = self._max_step_size / (frequency_hz * time_to_max_s)

    def press(self, direction: int):
        """
        starts the relative axis's motion

        :param direction: either 1 or -1
        :return:
        """

        self._is_pressed = True
        threading.Thread(target=self.__run_async, args=[direction]).start()

    def release(self):
        """stops the relative axis motion"""

        self._is_pressed = False

    def __run_async(self, direction: int):
        # NOTE this should only ever be called on a separate thread because it
        # uses sleep, which will block the rest of JG from running

        # smoothly moves the axis while the button is pressed

        step_size = 0
        while self._is_pressed:
            # accelerate step
            step_size += self._accel_step
            step_size = utils.clamp(step_size, self._accel_step, self._max_step_size)

            # direction will either be +-1
            self._axis.inc_val(direction * step_size)
            time.sleep(self._sleep_time)
