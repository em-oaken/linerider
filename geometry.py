

import math


class Point(object):
    """points have position and velocity implied by previous position"""

    def __init__(self, *args):
        x, y = args[0], args[1]
        self.r = Vector(x, y)  # current position
        self.r0 = Vector(x, y)  # position one frame before. no value, set to same as x,y

    def __repr__(self):
        return "Point" + str((self.r, self.r0))

class Line(object):
    """lines are defined by two points, p1 and p2"""

    #   __slots__ = ('r1', 'r2') #I ANTICIPATE THOUSANDS OF LINES
    def __init__(self, r1, r2):
        #points are position vectors
        if isinstance(r1, Vector) and isinstance(r2, Vector):
            self.r1 = r1
            self.r2 = r2
        else:  #inputs are tuples
            self.r1 = Vector(r1[0], r1[1])
            self.r2 = Vector(r2[0], r2[1])

    def __repr__(self):
        return "Line" + str((self.r1, self.r2))

    def linear_equation(self):
        """in the form of ax+by=c"""
        a = self.r2.y - self.r1.y
        b = self.r1.x - self.r2.x
        c = a * self.r1.x + b * self.r1.y
        return a, b, c

class SolidLine(Line):
    """collidable lines"""
    def __init__(self, r1, r2, ink):
        super(SolidLine, self).__init__(r1, r2)
        #       self.dir = (self.r2-self.r1).normalize() #direction the line points in
        #normal to line, 90 degrees ccw (to the left). DARN YOU FLIPPED COORDINATES
        #       self.norm = vector(self.dir.y, -self.dir.x)
        self.ink = ink

    def __repr__(self):
        return "solidLine" + str((self.r1, self.r2, self.ink))

class Vector(object):
    #slots for optimization...?
    #   __slots__ = ('x', 'y')
    def __init__(self, x, y:float=0):
        if type(x) == tuple:
            x, y = x[0], x[1]
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "vector" + str((self.x, self.y))

    #vector addition/subtraction
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    #scalar multiplication/division
    def __mul__(self, other):
        """exception: if other is also a vector, DOT PRODUCT
            I do it all the time in my 3d calc hw anyways :|"""
        if isinstance(other, Vector):
            return dot(self, other)
        else:
            return Vector(self.x * other, self.y * other)

    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other)

    def __imul__(self, other):
        self.x *= other
        self.y *= other
        return self

    def __idiv__(self, other):
        self.x /= other
        self.y /= other
        return self

    def magnitude2(self):
        """the square of the magnitude of this vector"""
        return distance2((self.x, self.y), (0, 0))

    def magnitude(self):
        """magnitude of this vector)"""
        return distance((self.x, self.y), (0, 0))

    def normalize(self):
        """unit vector. same direction but with a magnitude of 1"""
        if (self.x, self.y) == (0, 0):
            return Vector(0, 0)
        else:
            return self / self.magnitude()

    def rotate(self, other):
        """rotates vector in radians"""
        x = self.x * math.cos(other) - self.y * math.sin(other)
        y = self.x * math.sin(other) + self.y * math.cos(other)
        return Vector(x, y)

    def get_angle(self):
        """gets angle of vector relative to x axis"""
        return math.atan2(self.y, self.x)

# x**0.5 is annoying to compute, in python and in real life, it's a bit faster
def distance2(p, q):
    """distance squared between these points"""
    if isinstance(p, Vector) and isinstance(q, Vector):
        return (p.x - q.x) ** 2 + (p.y - q.y) ** 2
    else:
        return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def distance(p, q):
    """distance between these points"""
    return distance2(p, q) ** 0.5

def dot(u, v):
    """dot product of these vectors, a scalar"""
    return u.x * v.x + u.y * v.y
