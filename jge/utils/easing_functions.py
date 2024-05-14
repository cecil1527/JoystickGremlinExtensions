import copy

from jge.utils import utils


class SmoothStart:
    def __init__(self, degree: float) -> None:
        """
        * a functor that smoothly starts.
        * inputs and outputs range from [0, 1]

        Args:
            degree (float): degree of polynomial to use
        """
        self._degree = degree

    def __call__(self, input: float) -> float:
        return self.output(input)

    def output(self, input: float) -> float:
        return input**self._degree


class SmoothStop:
    def __init__(self, degree: float) -> None:
        """
        * a functor that smoothly stops.
        * inputs and outputs range from [0, 1]

        Args:
            degree (float): degree of polynomial to use
        """
        self._degree = degree

    def __call__(self, input: float) -> float:
        return self.output(input)

    def output(self, input: float) -> float:
        return 1 - (1 - input) ** self._degree


class SmoothStep:
    def __init__(self, start_degree: float, stop_degree: float) -> None:
        """
        * a functor that smoothly starts and stops.
        * inputs and outputs range from [0, 1]

        Args:
            start_degree (float): degree of polynomial to use to start
            stop_degree (float): degree of polynomial to use to stop
        """
        self._smooth_start = SmoothStart(start_degree)
        self._smooth_stop = SmoothStop(stop_degree)

    def __call__(self, input: float) -> float:
        return self.output(input)

    def output(self, input: float) -> float:
        if input < 0.5:
            input = utils.normalize(input, 0, 0.5)
            out = self._smooth_start(input)
            return utils.denormalize(out, 0, 0.5)
        else:
            input = utils.normalize(input, 0.5, 1.0)
            out = self._smooth_stop(input)
            return utils.denormalize(out, 0.5, 1.0)


class EasingGenerator:
    def __init__(
        self, easing_fn, num_steps: int, sleep_time_s: float, magnitude: float = 1.0
    ) -> None:
        """
        NOTE you should probably use one of the helper functions below, instead
        of creating this directly!

        a helper class to generate values for stepping along an easing function
        during a loop. it'll tell you:

        1. how many steps to loop for
        2. the current smoothed value
        3. how long to sleep for in each loop iteration

        Args:
            * easing_fn (function/functor): should take in normalized input [0,
              1] and produce normalized output [0, 1]
            * num_steps (int): num steps until magnitude is reached
            * sleep_time_s (float): sleep time in seconds
            * magnitude (float): magnitude to internally multiply the normalized
              easing function by. NOTE this is not required, because you can
              always multiply the output by your own magnitude externally. this
              was primarily added to test out a constant average rate easing
              generator
        """

        self._easing_fn = easing_fn
        self._num_steps = num_steps
        self._sleep_time_s = sleep_time_s
        self._magnitude = magnitude

        self._normalized_step = 1.0 / self._num_steps
        self._normalized_val = 0

    def copy(self):
        """
        because EasingGenerators store internal state, when using the same one
        multiple times, you're going to want to make copies when passing it
        around and storing it

        Returns:
            EasingGenerator: returns a copy of the easing generator
        """
        c = copy.copy(self)
        c.reset()
        return c

    @staticmethod
    def ConstantTime(
        easing_fn, time_s: float, frequency_hz: float, magnitude: float = 1.0
    ):
        """
        makes EasingGenerator that reaches full magnitude in a constant time.

        Args:
            * easing_fn (function/functor): should take in normalized input [0,
              1] and produce normalized output [0, 1]
            * time_s (float): how long (seconds) it'll take to hit full
              magnitude
            * frequency_hz (float): frequency you'll get values out
            * magnitude (float): magnitude to internally multiply the normalized
              easing function by. NOTE this is not required, because you can
              always multiply the output by your own magnitude externally, but
              sometimes it's nice to bundle a magnitude with the easing
              generator

        Returns:
            EasingGenerator:
        """

        num_steps = round(frequency_hz * time_s)
        sleep_time = 1.0 / frequency_hz
        return EasingGenerator(easing_fn, num_steps, sleep_time, magnitude)

    @staticmethod
    def ConstantRate(
        easing_fn, rate: float, frequency_hz: float, magnitude: float = 1.0
    ):
        """
        makes EasingGenerator that reaches magnitude at a constant average rate.
        (it'll reach full magnitude in magnitude/rate seconds)

        Args:
            * easing_fn (function/functor): should take in normalized input [0,
              1] and produce normalized output [0, 1]
            * rate (float): magnitude / seconds to max
            * frequency_hz (float): frequency you'll get values out
            * magnitude (float): magnitude to internally multiply the normalized
              easing function by. NOTE this is required because if you want a
              constant average rate, then the magnitude needs to come into play.
              use `.set_magnitude()` to preserve constant average rate when
              changing magnitude.

        Returns:
            EasingGenerator:

        More Notes: the instantaneous rate is subject to a smoothing curve, so
        it will vary with time. but since the total time is now dependent on
        magnitude, the average rate is constant. the basic idea is, if you have
        a rate of 10, then the easing generator will go from 0 to magnitude in
        magnitude/10 seconds.

        Example:

        * rate is 5. the easing generator will go from a magnitude of:
        * 0 to 5 in 1.0s
        * 0 to 10 in 2.0s
        * 0 to 15 in 3.0s
        * etc.
        """

        time_s = magnitude / rate
        num_steps = round(frequency_hz * time_s)
        sleep_time = 1.0 / frequency_hz
        eg = EasingGenerator(easing_fn, num_steps, sleep_time, magnitude)
        eg._rate = rate  # HACK
        return eg

    def set_magnitude(self, magnitude) -> None:
        if hasattr(self, "_rate"):
            # HACK if we're a constant rate EG, then a bunch of stuff needs
            # adjusted. there's probably a cleaner way to handle this :/
            time_s = magnitude / self._rate
            hz = 1 / self._sleep_time_s
            self._num_steps = round(hz * time_s)
            self._normalized_step = 1.0 / self._num_steps

        self._magnitude = magnitude

    def reset(self) -> None:
        """reset internal values. call this before beginning your loop"""
        self._normalized_val = 0

    def _increment(self) -> None:
        # normalized value will increase from [0, 1] with constant steps
        self._normalized_val += self._normalized_step
        self._normalized_val = utils.clamp(self._normalized_val, 0, 1)

    def get_output(self) -> float:
        """increment and get next output value"""
        self._increment()
        return self._magnitude * self._easing_fn(self._normalized_val)

    def get_sleep_time(self) -> float:
        """
        returns time to sleep (in seconds), so when you call this in a loop,
        you'll be generating output values at the desired frequency.
        """
        return self._sleep_time_s

    def get_num_steps(self) -> int:
        """
        returns number of steps to reach full magnitude. if your loop is
        supposed to go from [0, mag] and stop, you'll call your loop for this
        number of steps
        """
        return self._num_steps


if __name__ == "__main__":
    import time

    smooth_step = SmoothStep(3, 3)

    print("\nEasing Generator Constant Time")
    easing_gen_ct = EasingGenerator.ConstantTime(smooth_step, 2, 20, 100)
    t1 = time.time()
    for i in range(easing_gen_ct.get_num_steps()):
        print(easing_gen_ct.get_output())
        time.sleep(easing_gen_ct.get_sleep_time())
    t2 = time.time()
    print(f"easing generator ran for: {t2-t1}s")

    print("\nEasing Generator Constant Rate")
    easing_gen_cr = EasingGenerator.ConstantRate(smooth_step, 10, 20, 30)
    t1 = time.time()
    for i in range(easing_gen_cr.get_num_steps()):
        print(easing_gen_cr.get_output())
        time.sleep(easing_gen_cr.get_sleep_time())
    t2 = time.time()
    print(f"easing generator ran for: {t2-t1}s")
