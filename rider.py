

import copy
import tkinter as tk

from geometry import Point, Vector
from shapes import LineShape, Arc, Polygon, Circle
from physics import cnstr


class Rider:
    def __init__(self, start_point):  # make_rider() | startPoint = self.app.track.startPoint
        self.onSled = True
        self.accQueuePast = dict()
        self.accQueueNow = dict()

        # Points
        sled = [Point(0, 0), Point(0, 10), Point(30, 10), Point(35, 0)]
        bosh = [Point(10, 0), Point(10, -11), Point(23, -10), Point(23, -10),
                Point(20, 10), Point(20, 10)]
        scrf = [Point(7, -10), Point(3, -10), Point(0, -10), Point(-4, -10),
                Point(-7, -10), Point(-11, -10)]

        self.pos = bosh[0]

        self.boshParts = (
            (bosh[1], bosh[2]), (bosh[0], bosh[4]),
            (sled[0], sled[3]), (bosh[0], bosh[5]),
            (bosh[0], bosh[1]), (bosh[1], bosh[3])
        )
        self.sledString = ((bosh[2], sled[3]), (bosh[3], sled[3]))
        for point in sled + bosh + scrf:
            point.r += start_point
            point.r0 += start_point - Vector(1, 0)
        self.points = bosh + sled
        self.scarf = scrf

        # Constraints
        sledC = [cnstr(sled[0], sled[1]), cnstr(sled[1], sled[2]),
                 cnstr(sled[2], sled[3]), cnstr(sled[3], sled[0]),
                 cnstr(sled[0], sled[2]), cnstr(sled[1], sled[3])]
        boshC = [cnstr(bosh[0], bosh[1]), cnstr(bosh[1], bosh[2]),
                 cnstr(bosh[1], bosh[3]), cnstr(bosh[0], bosh[4]),
                 cnstr(bosh[0], bosh[5])]
        slshC = [cnstr(sled[0], bosh[0]), cnstr(sled[1], bosh[0]),
                 cnstr(sled[2], bosh[0]), cnstr(sled[0], bosh[1]),
                 cnstr(sled[3], bosh[2]), cnstr(sled[3], bosh[3]),
                 cnstr(sled[2], bosh[4]), cnstr(sled[2], bosh[5])]
        legsC = [cnstr(bosh[1], bosh[4], 0.5), cnstr(bosh[1], bosh[5], 0.5)]
        scrfC = [cnstr(bosh[1], scrf[0]), cnstr(scrf[0], scrf[1]),
                 cnstr(scrf[1], scrf[2]), cnstr(scrf[2], scrf[3]),
                 cnstr(scrf[3], scrf[4]), cnstr(scrf[4], scrf[5])]

        self.constraints = sledC + boshC + slshC
        self.slshC = slshC
        self.legsC = legsC
        self.scarfCnstr = scrfC

        self.drawing_vectors = self.gen_drawing_vectors()
        self.flag_drawing_vectors = self.gen_flag_drawings()

    def gen_drawing_vectors(self):
        s = 0.25  # scale down
        sled = [
            # base structure
            LineShape([(0, 0), (94.4, 0)], width=6, lineColor="#aaa"),
            LineShape([(-2, 38.2), (108.4, 38.2)], width=6, lineColor="#aaa"),
            LineShape([(16.6, 3), (16.6, 35.2)], width=6, lineColor="#aaa"),
            LineShape([(75, 3), (75, 35.2)], width=6, lineColor="#aaa"),
            Arc([(108.4, 11.6)], theta=(26.7, -90, 260),
                width=6, lineColor="#aaa", fillColor=None)
            # outline
        ]
        body = [
            # face
            Polygon([(54, -17.4), (54, 19), (60.6, 28.4), (86, 18.6), (80.8, -17.4)],
                    smooth=True),
            Circle([(68, 12)], fillColor="black", radius=3.2),
            # torso
            Polygon([(0, -17.4), (56, -17.4), (56, 17.8), (0, 17.8)]),
            # hat
            Arc([(80.8, 0)], theta=(20.2, -90, 180)),
            Circle([(106.8, 0)], fillColor="black", radius=5.8),
            LineShape([(80.8, 21.2), (80.8, -21.2)], width=6),
            Polygon([(56, -19.4), (56, -1.6), (80.8, -1.6), (80.8, -19.4)],
                    fillColor="black"),
            # scarf
            LineShape([(49.2, -20), (49.2, -12)], lineColor="red", width=16, cap=tk.BUTT),
            LineShape([(49.2, -12), (49.2, -4)], lineColor="white", width=16, cap=tk.BUTT),
            LineShape([(49.2, -4), (49.2, 4)], lineColor="red", width=16, cap=tk.BUTT),
            LineShape([(49.2, 4), (49.2, 12)], lineColor="white", width=16, cap=tk.BUTT),
            LineShape([(49.2, 12), (49.2, 20)], lineColor="red", width=16, cap=tk.BUTT)
        ]
        arm1 = [
            LineShape([(0, 0), (40, 0)], width=10.8),
            Polygon([(40, -5.4), (44, -5.4), (46.4, -9.2), (48.4, -9.6), (49, -8.8),
                     (48.4, -5.2), (52.4, -5.4), (55.2, -4.4), (56.6, -2.4), (56.6, 2.4),
                     (55.2, 4.4), (52.4, 5.4), (40, 5.4)])
        ]
        leg1 = [
            LineShape([(0, 0), (38.2, 0)], width=10.8),
            Polygon([(38.2, -5.4), (47.2, -5.4), (53, -15.8), (57.4, -15.4),
                     (57.4, 5.6), (38.2, 5.4)])
        ]
        arm2 = copy.deepcopy(arm1)
        leg2 = copy.deepcopy(leg1)
        return [arm1, leg1, sled, leg2, body, arm2]

    def gen_flag_drawings(self):
        parts = copy.deepcopy(self.drawing_vectors)
        for part in parts:
            for shape in part:
                if shape.lineColor == "red":
                    shape.lineColor = "#eee"
                elif shape.lineColor == "#aaa":
                    shape.lineColor = "#eee"
                elif shape.lineColor == "black":
                    shape.lineColor = "#ddd"
                if shape.fillColor == "black":
                    shape.fillColor = "#ddd"
        return parts

    def rebuild(self, start_point):
        self.__init__(start_point)

    def kill_bosh(self):
        if self.onSled:
            self.constraints = self.constraints[:-8]
            self.onSled = False

