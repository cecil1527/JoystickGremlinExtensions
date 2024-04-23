from bisect import bisect_left, bisect_right


def clamp(num, min_val, max_val):
    '''
    clamps num to be between min and max
    '''
    return max(min(num, max_val), min_val)


def lerp(x1, y1, x2, y2, x) -> float:
    '''
    linear interpolation. given that:
    
    * x1 -> y1
    * x2 -> y2
    * what does x yield?
    '''
    
    # https://stackoverflow.com/questions/4353525/floating-point-linear-interpolation

    if x1 == x2:
        return y1

    f = (x - x1) / (x2 - x1)
    return (y1 * (1 - f)) + (y2 * f)


def normalize(val, min_val, max_val, norm_low = 0.0, norm_high = 1.0):
    '''
    takes val, in range of [min, max], and scales it to be in range of [norm_low.
    norm_high]
    '''
    return lerp(min_val, norm_low, max_val, norm_high, val)


def unnormalize(norm, min_val, max_val, norm_low = 0.0, norm_high = 1.0):
    '''
    takes norm, in range of [norm_low, norm_high], and scales it to be in range
    of [min_val. max_val]
    '''
    return lerp(norm_low, min_val, norm_high, max_val, norm)


def sigmoid(input: float, curvature: float) -> float:

    '''
    applies sigmoid function to emulate DCS curvature

    * input_val: [-1, 1]
    * curvature: [-1, 1]
    
    * return: [-1, 1]
    '''

    # https://dinodini.wordpress.com/2010/04/05/normalized-tunable-sigmoid-functions/
    #
    # i'm using: y = (x - ax)/(a - 2a*abs(x) + 1). 
    # 
    # NOTE this is not the same sigmoid function DCS uses (not sure which
    # one they use)
    return (input - curvature * input) / (curvature - 2 * curvature * abs(input) + 1)


def binary_floor_excl(arr, val):
    '''binary floor exclusive. 
    * returns index of value in arr strictly less than val. 
    * index is guaranteed to be in range [0, maxIdx - 1], so you can always
        add 1 to get a valid ceiling idx.'''

    # https://docs.python.org/3.11/library/bisect.html#examples
    i = bisect_left(arr, val) - 1
    i = clamp(i, 0, len(arr) - 2)
    return i


def binary_ceil_excl(arr, val):
    '''binary ceiling exclusive. 
    * returns index of value in arr strictly greater than val. 
    * index is guaranteed to be in range [1, maxIdx], so you can always
        subtract 1 to get a valid floor idx.'''

    i = bisect_right(arr, val)
    i = clamp(i, 1, len(arr) - 1)
    return i


def is_between(val, n1, n2):
    '''returns if val lies between n1 and n2 (order agnostic)'''
    return n1 <= val <= n2 or n2 <= val <= n1

class Vec2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @staticmethod
    def From(v):
        '''returns Vec2, created from a tuple or list, or another Vec2'''
        return Vec2(v[0], v[1])
    
    def __getitem__(self, idx) -> float:
        if idx == 0:
            return self.x
        if idx == 1:
            return self.y
        raise IndexError

    def __str__(self) -> str:
        return f"<{self.x}, {self.y}>"

    def __eq__(self, other) -> bool:
        return Vec2.Equals(self, other)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __add__(self, other):
        return Vec2.Add(self, other)

    def __sub__(self, other):
        return Vec2.Subtract(self, other)

    def __mul__(self, scalar):
        return Vec2.Multiply(self, scalar)

    @staticmethod
    def Copy(p):
        return Vec2(p.x, p.y)

    @staticmethod
    def Equals(p1, p2):
        return p1.x == p2.x and p1.y == p2.y
        # TODO add a default epsilon param?

    @staticmethod
    def Add(p1, p2):
        '''
        adds p1 and p2. returns a new Point
        '''
        return Vec2(p1.x + p2.x, p1.y + p2.y)

    @staticmethod
    def Subtract(p1, p2):
        '''
        subtracts p2 from p1 (does p1 minus p2). returns a new Point
        '''
        return Vec2(p1.x - p2.x, p1.y - p2.y)

    @staticmethod
    def Multiply(p, s):
        return Vec2(p.x * s, p.y * s)

    @staticmethod
    def Lerp(p1, p2, t):
        '''
        linearly interpolates between p1 and p2, using proportion t
        '''

        diff = p2 - p1
        diff *= t
        return p1 + diff

    @staticmethod
    def LerpX(p1, p2, x):
        '''
        linearly interpolates between p1 and p2, using value x
        '''
        t = lerp(p1.x, 0, p2.x, 1, x)
        return Vec2.Lerp(p1, p2, t)
    
    @staticmethod
    def Slope(p1, p2) -> float:
        '''returns slope between p1 and p2'''
        return (p2.y - p1.y) / (p2.x - p1.x)


class LookupTable:
    def __init__(self, keys, vals) -> None:
        '''a lookup table that linearly interpolates between values'''
        self.keys = keys
        self.vals = vals
    
    @staticmethod
    def FromPoints(*points):
        '''
        returns a lookup table created from points, where each point is a (key,
        value)
        '''
        keys = [p[0] for p in points]
        vals = [p[1] for p in points]
        return LookupTable(keys, vals)

    def output(self, input) -> float:
        '''lerps to calc output based on input'''
        floor_idx = binary_floor_excl(self.keys, input)
        ceil_idx = floor_idx + 1
        return lerp(self.keys[floor_idx], self.vals[floor_idx],
                    self.keys[ceil_idx], self.vals[ceil_idx], 
                    input)
    
    # TODO add another function to handle the case where input may be OOB?


if __name__ == "__main__":
    p1 = Vec2(1, 2)
    p2 = Vec2(2, 3)
    p2 += p1
    p5 = p2 * 10
    assert(p2 == Vec2(3, 5))
    assert(p5 == Vec2(30, 50))

    p11 = Vec2(0, 0)
    p12 = Vec2(100, 500)
    assert(Vec2.Lerp(p11, p12, 0.50) == Vec2(50, 250))

    vals = [i for i in range(0, 110, 10)]
    assert(binary_floor_excl(vals, 64.21) == 6)
    assert(binary_floor_excl(vals, 20) == 1)
    assert(binary_floor_excl(vals, -20) == 0)
    assert(binary_floor_excl(vals, 200) == 9)
    assert(binary_ceil_excl(vals, 33.5) == 4)
    assert(binary_ceil_excl(vals, 40) == 5)
    assert(binary_ceil_excl(vals, -20) == 1)
    assert(binary_ceil_excl(vals, 200) == 10)

    assert(is_between(5, 1, 10) == True)
    assert(is_between(5, 12, -5) == True)
    assert(is_between(11, 20, 13) == False)
    assert(is_between(-2, -3, -4) == False)

    lut = LookupTable([x for x in range(11)], [x * x for x in range(11)])
    assert(lut.output(5) == 25)
    assert(lut.output(7) == 49)