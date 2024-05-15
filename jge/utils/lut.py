from jge.utils.utils import lerp, binary_floor_excl


def negate_and_reverse(values):
    reversed = values.copy()
    for i in range(len(reversed)):
        reversed[i] *= -1
    reversed.reverse()
    return reversed


class LookupTable:
    def __init__(self, keys, vals) -> None:
        """a lookup table that linearly interpolates between values"""
        self.keys = keys
        self.vals = vals

    @staticmethod
    def FromPoints(points, make_symmetrical: bool = False):
        """
        returns a lookup table created from the list of points

        Args:
            * points: List of points, where each point is a (key, value) tuple
            * make_symmetrical (bool, optional): shorthand for making a
              symmetrical LUT, where you supply all positive points and the
              corresponding negative points will automatically get added.
              Defaults to False.

        Returns:
            LookupTable:
        """
        keys = [p[0] for p in points]
        vals = [p[1] for p in points]

        if make_symmetrical:
            keys = negate_and_reverse(keys) + keys
            vals = negate_and_reverse(vals) + vals

        return LookupTable(keys, vals)

    def output(self, input) -> float:
        """lerps to calc output based on input"""
        floor_idx = binary_floor_excl(self.keys, input)
        ceil_idx = floor_idx + 1
        return lerp(
            self.keys[floor_idx],
            self.vals[floor_idx],
            self.keys[ceil_idx],
            self.vals[ceil_idx],
            input,
        )

    # TODO add another function to handle the case where input may be OOB?


if __name__ == "__main__":
    lut = LookupTable([x for x in range(11)], [x * x for x in range(11)])
    assert lut.output(5) == 25
    assert lut.output(7) == 49

    lut2 = LookupTable.FromPoints(
        [(0.1, 0.1), (0.2, 0.4), (0.3, 1.0)], make_symmetrical=True
    )
    for k, v in zip(lut2.keys, lut2.vals):
        print(k, v)
