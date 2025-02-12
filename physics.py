

import copy

from geometry import Line, Vector, distance
from tool_helpers import Ink


class Constraint:
    def __init__(self, pnt1, pnt2, restLength):
        #p1 and p2 are points
        self.pnt1, self.pnt2 = pnt1, pnt2
        self.restLength = restLength

    def __repr__(self):
        return str((self.pnt1, self.pnt2, self.restLength))

    def resolve_constraint(self):
        """resolves a given constraint"""
        delta = self.pnt1.r - self.pnt2.r
        deltaLength = delta.magnitude()
        diff = (deltaLength - self.restLength) / deltaLength
        self.pnt1.r -= delta * diff / 2
        self.pnt2.r += delta * diff / 2

    def resolve_legs(self):
        """the constraint can only take on a minimum length"""
        delta = self.pnt1.r - self.pnt2.r
        deltaLength = delta.magnitude()
        diff = (deltaLength - self.restLength) / deltaLength
        if diff < 0:  # length is too small
            self.pnt1.r -= delta * diff / 2
            self.pnt2.r += delta * diff / 2

    def check_endurance(self, data, kill_bosh):
        """if the ratio of the difference of length is beyond a certain
            limit, destroy line rider's attachment to the sled"""
        delta = self.pnt1.r - self.pnt2.r
        diff = (delta.magnitude() - self.restLength)
        ratio = abs(diff / self.restLength)
        if ratio > data.endurance:
            kill_bosh()  # remove constraints

    def resolve_scarf(self):
        """one sided constraints"""
        delta = self.pnt1.r - self.pnt2.r
        deltaLength = delta.magnitude()
        diff = (deltaLength - self.restLength) / deltaLength
        self.pnt2.r += delta * diff

def cnstr(pnt1, pnt2, scale:float=1):
    length = (pnt1.r - pnt2.r).magnitude()
    return Constraint(pnt1, pnt2, length * scale)

def det(a, b, c, d):
    """determinant"""
    # | a b |
    # | c d |
    return a * d - b * c

def is_in_line_region(r, line, data):
    """rectangular region defined by endpoints of a line segment or points"""
    return is_in_region(r, line.r1, line.r2, data)

def in_window(pos, data):
    return is_in_region(pos, Vector(0, 0), data.windowSize, data)

def almost_equal(a, b, data):
    return abs(a - b) < data.epsilon / 100

def is_in_region(r, pnt1, pnt2, data):
    if isinstance(pnt1, Vector):
        x1, x2, y1, y2 = pnt1.x, pnt2.x, pnt1.y, pnt2.y
    else:
        x1, x2, y1, y2 = pnt1[0], pnt2[0], pnt1[1], pnt2[1]
    if isinstance(r, Vector):
        rx, ry = r.x, r.y
    else:
        rx, ry = r[0], r[1]
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)
    isInRect = x1 <= rx <= x2 and y1 <= ry <= y2
    isOnHLine = x1 == x2 and almost_equal(x1, rx, data) and y1 <= ry <= y2
    isOnVLine = y1 == y2 and almost_equal(y1, ry, data) and x1 <= rx <= x2
    return isInRect or isOnHLine or isOnVLine

def intersect_point(line1, line2, data):
    """Returns the coordinates of intersection between line segments.
    If the lines are not intersecting, returns None."""
    a1, b1, c1 = line1.linear_equation()
    a2, b2, c2 = line2.linear_equation()
    d = det(a1, b1, a2, b2)
    if d == 0: return None
    x = 1.0 * det(c1, b1, c2, b2) / d
    y = 1.0 * det(a1, c1, a2, c2) / d
    intersection = Vector(x, y)
    if (is_in_line_region(intersection, line1, data)
            and is_in_line_region(intersection, line2, data)):
        return intersection  #position vector of point of intersection

def closest_point_on_line(r, line):
    """closest point on a line to a point(position vector)"""
    a, b, c1 = line.linear_equation()
    c2 = -b * r.x + a * r.y
    d = det(a, b, -b, a)
    if d == 0:
        point = r  #POINT IS ON LINE
    else:
        x = det(a, b, c2, c1) / d
        y = det(a, -b, c1, c2) / d
        point = Vector(x, y)  #it's a position vector!
    return point

def distance_from_line(r, line, data):
    """distance between a point and a line segment"""
    line_point = closest_point_on_line(r, line)
    if is_in_line_region(line_point, line, data):
        dist = distance(r, line_point)
    else:
        dist = min(distance(r, line.r1), distance(r, line.r2))
    return dist

def get_collision(pnt, line, data):
    """returns the position after collision(if it exists)"""
    trajectory = Line(pnt.r, pnt.r0)
    intersection = intersect_point(trajectory, line, data)
    thickness = data.lineThickness + data.epsilon
    if intersection != None:
        #if intersecting, project position onto line
        futurePos = closest_point_on_line(pnt.r, line)
        #line thickness
        futurePos += (futurePos - pnt.r).normalize() * thickness
        #        print("intersection!")
        return futurePos, intersection
    elif distance_from_line(pnt.r, line, data) < data.lineThickness:
        #if inside line, do same as above except reverse direction of epsilon
        futurePos = closest_point_on_line(pnt.r, line)
        futurePos += (pnt.r - futurePos).normalize() * thickness
        #        print("inside line! Moving", pnt.r, "to", futurePos)
        return futurePos, pnt.r  #pnt.r is in hte line: it's the intersection
    else:
        return None

def get_colliding_lines(pnt, lines, data):
    """"returns a list of the lines "pnt" actually collides with
        and the respective intersection points"""
    collisionPoints = []
    collidingLines = []
    intersections = []
    for line in lines:
        point = get_collision(pnt, line, data)
        if point != None:
            collidingLines += [line]
            collisionPoints += [point[0]]
            intersections += [point[1]]
    return collidingLines, collisionPoints, intersections

def closest_point(pnt, points):
    closestPoint = points[0]  #first point
    minDist = distance(closestPoint, pnt)
    for point in points[1:]:
        dist = distance(point, pnt)
        if dist < minDist:
            minDist = dist
            closestPoint = point
    return closestPoint

def closest_collision_point(pnt, intersections, collisionPoints):
    closestIntersection = closest_point(pnt.r0, intersections)
    i = intersections.index(closestIntersection)
    return collisionPoints[i]

def resolve_collision(pnt, data, grid, rider):
    """takes a solid point, finds and resolves collisions,
    and returns the acceleration lines it collided with"""
    hasCollided = True
    a = data.acc
    maxiter = data.maxiter
    accLines = set()
    while hasCollided and maxiter > 0:
        hasCollided = False
        lines = grid.get_solid_lines(pnt)  #get the lines the point may collide with
        #get the collision points of the lines the point actually collides with
        collidingLines, collisionPoints, intersections = get_colliding_lines(pnt, lines, data)

        if collisionPoints == []:  #no collisions? break
            break
        elif len(collisionPoints) > 1:
            #more than one collision points: get the intersection point closest to the point
            futurePoint = closest_collision_point(pnt, intersections, collisionPoints)
            index = collisionPoints.index(futurePoint)
            collidingLine = collidingLines[index]
        else:
            futurePoint = collisionPoints[0]
            collidingLine = collidingLines[0]
        #set future point to above point, evaluate acc line if necessary
        pnt.r = futurePoint
        if collidingLine.ink == Ink.Acc:
            accLines.add(collidingLine)

        hasCollided = True
        maxiter -= 1
        if data.view_collisions:
            data.collisionPoints += [copy.copy(futurePoint)]
        if pnt == rider.points[0]:  # Content of sensitive_butt()
            # LINE RIDER'S BUTT IS SENSITIVE. TOUCH IT AND HE FALLS OFF THE SLED.
            rider.kill_bosh()
    return accLines
