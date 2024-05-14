from bisect import bisect_left, bisect_right


def clamp(num, min_val, max_val):
    """
    clamps num to be between min and max
    """
    return max(min(num, max_val), min_val)


def lerp(x1, y1, x2, y2, x) -> float:
    """
    linear interpolation. given that:

    * x1 -> y1
    * x2 -> y2
    * what does x yield?
    """

    # https://stackoverflow.com/questions/4353525/floating-point-linear-interpolation

    if x1 == x2:
        return y1

    f = (x - x1) / (x2 - x1)
    return (y1 * (1 - f)) + (y2 * f)


def normalize(val, min_val, max_val, norm_low=0.0, norm_high=1.0):
    """
    takes val, in range of [min, max], and scales it to be in range of [norm_low.
    norm_high]
    """
    return lerp(min_val, norm_low, max_val, norm_high, val)


def denormalize(norm, min_val, max_val, norm_low=0.0, norm_high=1.0):
    """
    takes norm, in range of [norm_low, norm_high], and scales it to be in range
    of [min_val. max_val]
    """
    return lerp(norm_low, min_val, norm_high, max_val, norm)


def sigmoid(input: float, curvature: float) -> float:
    """
    applies sigmoid function to emulate DCS curvature

    * input: [-1, 1]
    * curvature: [-1, 1]

    * return: [-1, 1]
    """

    # https://dinodini.wordpress.com/2010/04/05/normalized-tunable-sigmoid-functions/
    #
    # i'm using: y = (x - ax)/(a - 2a*abs(x) + 1).
    #
    # NOTE this is not the same sigmoid function DCS uses (not sure which
    # one they use)
    return (input - curvature * input) / (curvature - 2 * curvature * abs(input) + 1)


def binary_floor_excl(arr, val):
    """binary floor exclusive.
    * returns index of value in arr strictly less than val.
    * index is guaranteed to be in range [0, maxIdx - 1], so you can always
        add 1 to get a valid ceiling idx."""

    # https://docs.python.org/3.11/library/bisect.html#examples
    i = bisect_left(arr, val) - 1
    i = clamp(i, 0, len(arr) - 2)
    return i


def binary_ceil_excl(arr, val):
    """binary ceiling exclusive.
    * returns index of value in arr strictly greater than val.
    * index is guaranteed to be in range [1, maxIdx], so you can always
        subtract 1 to get a valid floor idx."""

    i = bisect_right(arr, val)
    i = clamp(i, 1, len(arr) - 1)
    return i


def is_between(val, n1, n2):
    """returns if val lies between n1 and n2 (order agnostic)"""
    return n1 <= val <= n2 or n2 <= val <= n1


if __name__ == "__main__":
    vals = [i for i in range(0, 110, 10)]
    assert binary_floor_excl(vals, 64.21) == 6
    assert binary_floor_excl(vals, 20) == 1
    assert binary_floor_excl(vals, -20) == 0
    assert binary_floor_excl(vals, 200) == 9
    assert binary_ceil_excl(vals, 33.5) == 4
    assert binary_ceil_excl(vals, 40) == 5
    assert binary_ceil_excl(vals, -20) == 1
    assert binary_ceil_excl(vals, 200) == 10

    assert is_between(5, 1, 10) == True
    assert is_between(5, 12, -5) == True
    assert is_between(11, 20, 13) == False
    assert is_between(-2, -3, -4) == False
