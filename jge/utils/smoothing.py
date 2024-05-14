class MovingAverage:
    def __init__(self, size: int) -> None:
        self._nums = [0] * size
        self._idx = 0
        self._total = 0

    def __call__(self, num: float):
        self.update(num)
        return self.get_avg()

    def update(self, num: float):
        oldest_val = self._nums[self._idx]
        self._nums[self._idx] = num

        self._total -= oldest_val
        self._total += num

        self._idx += 1
        if self._idx == len(self._nums):
            self._idx = 0

    def get_avg(self) -> float:
        return self._total / len(self._nums)


class ExponentialSmoothing:
    def __init__(self, alpha: float) -> None:
        self._alpha = alpha
        self._prev_value = 0

    def __call__(self, num: float) -> float:
        self.update(num)
        return self.get_val()

    def update(self, num: float):
        self._prev_value = self._alpha * num + (1 - self._alpha) * self._prev_value

    def get_val(self) -> float:
        return self._prev_value


class PassthroughSmoothing:
    def __init__(self, smoothing_fn, passthrough_region: float) -> None:
        """
        a wrapper around a smoothing function/functor where you define a
        passthrough region, above which no smoothing occurs.

        Args:
            * smoothing_fn (_type_): smoothing function/functor
            * passthrough_region (float): region above whose absolute value, you
              want the signal to pass through and not get smoothed

        Further notes: the quick and easy smoothing methods all introduce a bit
        of lag, which means if you quickly "flick" an axis, the smoothed signal
        probably won't max out, but we'd like to be able to hit max zoom (for
        example). by doing a "passthrough" region, where no smoothing occurs,
        you will still be able to max out a heavily smoothed axis.
        """

        self._smoothing_fn = smoothing_fn
        self._passthrough = passthrough_region

    def __call__(self, num: float) -> float:
        # always influence the smoothed value, just don't use it if we're above
        # the passthrough region. this prevents erroneous axis "bouncing" as you
        # come out of the passthrough region
        smooth_val = self._smoothing_fn(num)

        if abs(num) > self._passthrough:
            return num
        else:
            return smooth_val


if __name__ == "__main__":
    moving_average = MovingAverage(10)
    for _ in range(20):
        moving_average(1.0)
