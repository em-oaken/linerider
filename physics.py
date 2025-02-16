


from geometry import Point, distance

class Constraint:
    def __init__(self, pnt1: Point, pnt2: Point, rest_length):  #p1 and p2 are points
        self.pnt1, self.pnt2 = pnt1, pnt2
        self.rest_length = rest_length

    def __repr__(self):
        return str((self.pnt1, self.pnt2, self.rest_length))

    def resolve(self, neg_factor_only=False, static_p1=False):
        """Resolves the constraint by bringing p1 and p2 closer to each-other.
        The higher the difference between length and rest-length, the bigger the correction to get them back together
        neg_factor_only: For legs
        static_p1: One-sided constraint for scarf"""
        delta = self.pnt1.r - self.pnt2.r
        length = distance(self.pnt1.r, self.pnt2.r)  # Was delta.magnitude() before, but why?
        factor = (length - self.rest_length) / length

        if neg_factor_only:
            if factor < 0:
                self.pnt1.r -= delta * factor / 2
                self.pnt2.r += delta * factor / 2
        elif static_p1:
            self.pnt2.r += delta * factor
        else:
            self.pnt1.r -= delta * factor / 2
            self.pnt2.r += delta * factor / 2

    def check_endurance(self, rider):
        """if the ratio of the difference of length is beyond a certain
            limit, destroy line rider's attachment to the sled"""
        delta = self.pnt1.r - self.pnt2.r
        diff = (delta.magnitude() - self.rest_length)
        ratio = abs(diff / self.rest_length)
        if ratio > rider.endurance:
            rider.kill_bosh()  # remove constraints

def cnstr(pnt1, pnt2, scale:float=1):
    length = (pnt1.r - pnt2.r).magnitude()
    return Constraint(pnt1, pnt2, length * scale)
