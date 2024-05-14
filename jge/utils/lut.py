from jge.utils.utils import lerp, binary_floor_excl


class LookupTable:
    def __init__(self, keys, vals) -> None:
        """a lookup table that linearly interpolates between values"""
        self.keys = keys
        self.vals = vals

    @staticmethod
    def FromPoints(*points):
        """
        returns a lookup table created from points, where each point is a (key,
        value)
        """
        keys = [p[0] for p in points]
        vals = [p[1] for p in points]
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
