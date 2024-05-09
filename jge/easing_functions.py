import copy

from jge import utils


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
        return utils.lerp(
            0, self._smooth_start(input), 1, self._smooth_stop(input), input
        )


class EasingGenerator:
    def __init__(
        self, easing_fn, magnitude: float, num_steps: int, sleep_time_s: float
    ) -> None:
        """
        a helper class to generate values for stepping along an easing function
        during a loop. it'll tell you:

        1. how many steps to loop for
        2. the current smoothed value
        3. how long to sleep for in each loop iteration

        Args:
            * easing_fn (function/functor): should take in normalized input [0,
              1] and produce normalized output [0, 1]
            * magnitude (float): magnitude to multiply the normalized easing
              function by
            * num_steps (int): num steps until magnitude is reached
            * sleep_time_s (float): sleep time in seconds
        """

        self._easing_fn = easing_fn
        self._magnitude = magnitude
        self._num_steps = num_steps
        self._sleep_time_s = sleep_time_s

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
    def ConstantTime(easing_fn, magnitude: float, time_s: float, frequency_hz: float):
        """
        makes EasingGenerator that reaches magnitude in a constant time.

        Args:
            * easing_fn (function/functor): should take in normalized input [0,
              1] and produce normalized output [0, 1]
            * magnitude (float): magnitude to multiply the normalized easing
              function by
            * time_s (float): how long (seconds) it'll take to hit full
              magnitude
            * frequency_hz (float): frequency you'll get values out

        Returns:
            EasingGenerator:
        """

        num_steps = round(frequency_hz * time_s)
        sleep_time = 1.0 / frequency_hz
        return EasingGenerator(easing_fn, magnitude, num_steps, sleep_time)

    @staticmethod
    def ConstantRate(easing_fn, magnitude: float, rate: float, frequency_hz: float):
        """
        makes EasingGenerator that reaches magnitude at a "constant rate".
        (it'll reach full magnitude in magnitude/rate seconds)

        Args:
            * easing_fn (function/functor): should take in normalized input [0,
              1] and produce normalized output [0, 1]
            * magnitude (float): magnitude to multiply the normalized easing
              function by
            * rate (float): magnitude / seconds to max
            * frequency_hz (float): frequency you'll get values out

        Returns:
            EasingGenerator:

        More Notes: i put constant rate in quotes because the real rate is
        subject to a smoothing curve, so it is varying with time. but the total
        time is dependent on magnitude, so the average rate over its full
        duration of use is constant. the basic idea is, if you have a rate of
        10, then the easing generator will go from 0 to magnitude in
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
        eg = EasingGenerator(easing_fn, magnitude, num_steps, sleep_time)
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
    xs = [x / 100 for x in range(101)]

    smooth_start = SmoothStart(3)
    ys = [smooth_start(x) for x in xs]
    print("\nsmooth start")
    for x, y in zip(xs, ys):
        print(f"{x},{y}")

    smooth_stop = SmoothStop(3)
    ys = [smooth_stop(x) for x in xs]
    print("\nsmooth stop")
    for x, y in zip(xs, ys):
        print(f"{x},{y}")

    smooth_step = SmoothStep(3, 3)
    ys = [smooth_step(x) for x in xs]
    print("\nsmooth step")
    for x, y in zip(xs, ys):
        print(f"{x},{y}")

    import time

    print("\nEasing Generator Constant Time")
    easing_gen_ct = EasingGenerator.ConstantTime(smooth_step, 100, 2, 20)
    t1 = time.time()
    for i in range(easing_gen_ct.get_num_steps()):
        print(easing_gen_ct.get_output())
        time.sleep(easing_gen_ct.get_sleep_time())
    t2 = time.time()
    print(f"easing generator ran for: {t2-t1}s")

    print("\nEasing Generator Constant Rate")
    easing_gen_cr = EasingGenerator.ConstantRate(smooth_step, 30, 10, 20)
    t1 = time.time()
    for i in range(easing_gen_cr.get_num_steps()):
        print(easing_gen_cr.get_output())
        time.sleep(easing_gen_cr.get_sleep_time())
    t2 = time.time()
    print(f"easing generator ran for: {t2-t1}s")
