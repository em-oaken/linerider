

import copy

from geometry import Point, Line, Vector, distance
from tool_helpers import Ink

factor = 10

class World:
    def __init__(self, app):
        self.app = app
        self.timeDelta = 16  # Target interval between frames. 16ms -> 62.5fps
        self.grav = Vector(0, 30.0 / 1000 * factor)  # pixels per frame**2
        self.drag = 0.9999999 ** factor
        self.acc = 0.1 * factor  # acceleration line constant
        self.epsilon = 0.00000000001  # larger than floating point errors
        self.lineThickness = 0.001
        self.maxiter = 100

    def step_forward(self):
        if self.app.ui.show_collisions:
            self.collisionPoints = []

        for pnt in self.app.rider.points:  # first, update points based on inertia, gravity, and drag
            pnt.r, pnt.r0 = self.free_fall(pnt), pnt.r
        for pnt in self.app.rider.scarf:  # scarves are special :|
            pnt.r, pnt.r0 = self.free_fall(pnt, mass=0.5), pnt.r

        # Acceleration lines rider collided with in last round now take effect
        for pnt, lines in self.app.rider.accQueueNow.items():
            for line in lines:
                pnt.r += (line.r2 - line.r1).normalize() * self.acc
        self.app.rider.accQueueNow, self.app.rider.accQueuePast = dict(), self.app.rider.accQueueNow

        for _ in range(10):
            # collisions get priority to prevent phasing through lines
            for cnstr in self.app.rider.legsC:
                cnstr.resolve(neg_factor_only=True)
            if self.app.rider.onSled:
                for cnstr in self.app.rider.slshC:
                    cnstr.check_endurance(self.app.rider)
            for cnstr in self.app.rider.constraints:
                cnstr.resolve()
            for pnt in self.app.rider.points:
                accLines = self.resolve_collision(pnt, self.app.track.grid, self.app.rider, self.app.ui)
                if len(accLines) > 0:  # contains lines
                    self.app.rider.accQueueNow[pnt] = accLines

        for cnstr in self.app.rider.scarfCnstr:
            cnstr.resolve(static_p1=True)

    def free_fall(self, pnt, mass: float = 1):
        """All points are independent, acting only on inertia, drag, and gravity
        The velocity is implied with the previous position"""
        velocity = pnt.r - pnt.r0
        return pnt.r + velocity * self.drag * mass + self.grav  # TODO: Drag should be with speed²!

    def resolve_collision(self, pnt, grid, rider, ui):
        """takes a solid point, finds and resolves collisions,
        and returns the acceleration lines it collided with"""
        hasCollided = True
        maxiter = self.maxiter
        accLines = set()

        while hasCollided and maxiter > 0:
            hasCollided = False
            lines = grid.get_solid_lines(pnt)  # get the lines the point may collide with
            collidingLines, collisionPoints, intersections = self.get_colliding_lines(pnt, lines)

            if len(collisionPoints) == 0:  # no more collisions
                break
            elif len(collisionPoints) > 1:  # get the intersection point closest to the point
                futurePoint = self.closest_collision_point(pnt, intersections, collisionPoints)
                index = collisionPoints.index(futurePoint)
                collidingLine = collidingLines[index]
            else:
                futurePoint = collisionPoints[0]
                collidingLine = collidingLines[0]
            # set future point to above point, evaluate acc line if necessary
            pnt.r = futurePoint
            if collidingLine.ink == Ink.Acc:
                accLines.add(collidingLine)

            hasCollided = True
            maxiter -= 1
            if ui.show_collisions:
                self.collisionPoints += [copy.copy(futurePoint)]
            if pnt == rider.points[0]:
                rider.kill_bosh()  # LINE RIDER'S BUTT IS SENSITIVE. TOUCH IT AND HE FALLS OFF THE SLED.
        return accLines

    def get_colliding_lines(self, pnt, lines):
        """"returns a list of the lines "pnt" actually collides with
            and the respective intersection points"""
        collisionPoints = []
        collidingLines = []
        intersections = []
        for line in lines:
            point = self.get_collision(pnt, line)  # future position of pnt, intersection pt
            if point is not None:
                collidingLines += [line]
                collisionPoints += [point[0]]
                intersections += [point[1]]
        return collidingLines, collisionPoints, intersections

    def get_collision(self, pnt: Point, line: Line):
        """Returns the position after collision (if it exists)
        Returns:
        - futurePos: The point where pnt will end up after collision
        - intersection: The point where pnt trajectory meets the line"""
        trajectory = Line(pnt.r, pnt.r0)
        intersection = self.intersect_point(trajectory, line)
        thickness = self.lineThickness + self.epsilon
        futurePos = self.closest_point_on_line(pnt.r, line)

        if intersection is not None:  # if intersecting, project position onto line
            futurePos += (futurePos - pnt.r).normalize() * thickness
            return futurePos, intersection

        if self.distance_from_line(pnt.r, line) < self.lineThickness:  # if inside line, do same as above except reverse direction of epsilon
            futurePos += (pnt.r - futurePos).normalize() * thickness
            return futurePos, pnt.r  # pnt.r is in hte line: it's the intersection

        return None

    def intersect_point(self, line1, line2):
        """Returns the coordinates of intersection between line segments.
        If the lines are not intersecting, returns None."""
        a1, b1, c1 = line1.linear_equation()
        a2, b2, c2 = line2.linear_equation()
        d = det(a1, b1, a2, b2)
        if d == 0:
            return None
        x = 1.0 * det(c1, b1, c2, b2) / d
        y = 1.0 * det(a1, c1, a2, c2) / d
        intersection_pt = Vector(x, y)

        # Check if intersection point is on the segment. TODO: Really, no easier way to do that?
        if self.is_in_line_region(intersection_pt, line1) and self.is_in_line_region(intersection_pt, line2):
            return intersection_pt
        return None

    def is_in_line_region(self, r, line):
        """rectangular region defined by the 2 endpoints of a line segment or points"""
        return self.is_in_region(r, line.r1, line.r2)

    def is_in_region(self, r: Vector, pnt1: Vector, pnt2: Vector):
        x1, x2 = min(pnt1.x, pnt2.x), max(pnt1.x, pnt2.x)
        y1, y2 = min(pnt1.y, pnt2.y), max(pnt1.y, pnt2.y)

        is_in_rect = x1 <= r.x <= x2 and y1 <= r.y <= y2
        is_on_h_line = x1 == x2 and self.almost_equal(x1, r.x) and y1 <= r.y <= y2
        is_on_v_line = y1 == y2 and self.almost_equal(y1, r.y) and x1 <= r.x <= x2
        return is_in_rect or is_on_h_line or is_on_v_line

    def closest_point_on_line(self, r, line):
        """closest point on a line to a point(position vector)"""
        a, b, c1 = line.linear_equation()
        c2 = -b * r.x + a * r.y
        d = det(a, b, -b, a)
        if d == 0:
            point = r  # POINT IS ON LINE
        else:
            x = det(a, b, c2, c1) / d
            y = det(a, -b, c1, c2) / d
            point = Vector(x, y)  # it's a position vector!
        return point

    def distance_from_line(self, r, line):
        """distance between a point and a line segment"""
        line_point = self.closest_point_on_line(r, line)
        if self.is_in_line_region(line_point, line):
            dist = distance(r, line_point)
        else:
            dist = min(distance(r, line.r1), distance(r, line.r2))
        return dist

    def closest_collision_point(self, pnt, intersections, collisionPoints):
        dists = [distance(pnt.r0, pt) for pt in intersections]
        idx_closest = dists.index(min(dists))
        return collisionPoints[idx_closest]

    def almost_equal(self, a, b):
        return abs(a - b) < self.epsilon / 100

    def get_lines_around(self, pos, radius):
        """Returns a set of lines to be removed, part of the eraser"""
        lines_found = set()
        cells = self.app.track.grid.grid_neighbors(pos)  # list of 9 closest cell positions
        for gPos in cells:  # each cell has a position/key on the grid/dict
            cell = self.app.track.grid.solids.get(gPos, set())  # each cell is a set of lines
            for line in cell:
                if self.distance_from_line(pos, line) * self.app.player.zoom <= radius:
                    lines_found.add(line)
            cell = self.app.track.grid.scenery.get(gPos, set())
            for line in cell:
                if self.distance_from_line(pos, line) * self.app.player.zoom <= radius:
                    lines_found.add(line)
        return lines_found

def det(a, b, c, d):
    """determinant"""
    return a * d - b * c
