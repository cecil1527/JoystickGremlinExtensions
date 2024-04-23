import utils


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
        return input ** self._degree


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
        return utils.lerp(0, self._smooth_start(input),
                          1, self._smooth_stop(input),
                          input)


class EasingGenerator:
    def __init__(self, easing_fn, max_rate: float, time_to_max_s: float, 
                 rate_hz: float) -> None:
        """
        a simple helper class to generate values for stepping along an easing
        function through time.

        Args:
            * easing_fn: should be a function/functor that takes in normalized
              input [0, 1] and produces normalized output [0, 1]
            * max_rate (float): what the maximum rate the output will have (as
              long as you get outputs at the Hz you promised)
            * time_to_max_s (float): time (seconds) to reach the max rate
            * rate_hz (float): how often this will be called in hertz
        """        

        self._easing_fn = easing_fn
        self._max_val = max_rate / rate_hz
        
        steps_to_max = rate_hz * time_to_max_s
        self._normalized_step = 1.0 / steps_to_max
        self._normalized_val = 0
        
        self._sleep_time_s = 1.0 / rate_hz

    def reset(self) -> None:
        self._normalized_val = 0

    def _increment(self) -> None:
        self._normalized_val += self._normalized_step
        self._normalized_val = utils.clamp(self._normalized_val, 0, 1)

    def get_output(self) -> float:
        '''increment and get output value'''
        self._increment()
        return self._max_val * self._easing_fn(self._normalized_val)
    
    def get_sleep_time(self) -> float:
        '''
        returns the time to sleep (in seconds), so you can call this in a loop
        and be generating output values at the desired frequency
        '''
        return self._sleep_time_s


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
    print("\neasing generator")
    hz = 20
    time_to_max_s = 2
    easing_gen = EasingGenerator(smooth_start, 1, time_to_max_s, hz)
    t1 = time.time()
    for i in range(time_to_max_s * hz):
        print(easing_gen.get_output())
        time.sleep(easing_gen.get_sleep_time())
    t2 = time.time()
    print(f"easing generator ran for: {t2-t1}s")
