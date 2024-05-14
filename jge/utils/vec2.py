from jge.utils.utils import lerp


class Vec2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @staticmethod
    def From(v):
        """returns Vec2, created from a tuple or list, or another Vec2"""
        return Vec2(v[0], v[1])

    @staticmethod
    def ToTuple(v):
        return (v.x, v.y)

    def __getitem__(self, idx) -> float:
        if idx == 0:
            return self.x
        if idx == 1:
            return self.y
        raise IndexError

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

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
        """
        adds p1 and p2. returns a new Point
        """
        return Vec2(p1.x + p2.x, p1.y + p2.y)

    @staticmethod
    def Subtract(p1, p2):
        """
        subtracts p2 from p1 (does p1 minus p2). returns a new Point
        """
        return Vec2(p1.x - p2.x, p1.y - p2.y)

    @staticmethod
    def Multiply(p, s):
        return Vec2(p.x * s, p.y * s)

    @staticmethod
    def Lerp(p1, p2, t):
        """
        linearly interpolates between p1 and p2, using proportion t
        """

        diff = p2 - p1
        diff *= t
        return p1 + diff

    @staticmethod
    def LerpX(p1, p2, x):
        """
        linearly interpolates between p1 and p2, using value x
        """
        t = lerp(p1.x, 0, p2.x, 1, x)
        return Vec2.Lerp(p1, p2, t)

    @staticmethod
    def Slope(p1, p2) -> float:
        """returns slope between p1 and p2"""
        return (p2.y - p1.y) / (p2.x - p1.x)


if __name__ == "__main__":
    p1 = Vec2(1, 2)
    p2 = Vec2(2, 3)
    p2 += p1
    p5 = p2 * 10
    assert p2 == Vec2(3, 5)
    assert p5 == Vec2(30, 50)

    p11 = Vec2(0, 0)
    p12 = Vec2(100, 500)
    assert Vec2.Lerp(p11, p12, 0.50) == Vec2(50, 250)
