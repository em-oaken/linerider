
import math
import tkinter as tk

from geometry import Vector


class Shape:
    # [type, [coords], fill=fColor, outline=oColor, width=w, special
    #special: (r, start, extent) or (smooth, cap)]    cors = copy.copy(sgmnt[0])
    def __init__(self, cors, fillColor, lineColor, width):
        #        cors = copy.copy(coords)
        for i in range(len(cors)):
            cors[i] = Vector(cors[i]) * 0.25  #scale
        self.cors = cors
        self.fillColor = fillColor
        self.lineColor = lineColor
        self.width = width


class LineShape(Shape):
    def __init__(self, cors, fillColor=None, lineColor="black", width=1,
                 smooth=False, cap=tk.ROUND):
        super(LineShape, self).__init__(cors, fillColor, lineColor, width)
        self.isSmooth = smooth
        self.capstyle = cap

    def render(self, pnt0, angle, app):
        w = self.width
        if w != 1:
            w *= app.track.zoom * 0.25
        cors = []
        for i in range(len(self.cors)):
            cor = self.cors[i].rotate(angle)
            cor = app.adjust_pz(cor + pnt0)
            cors += (cor.x, cor.y)  #convert to tuples, put into list
        app.ui.canvas.create_line(cors, fill=self.lineColor, width=w,
                           joinstyle=tk.MITER, capstyle=self.capstyle)


class Polygon(Shape):
    def __init__(self, cors, fillColor="white", lineColor="black", width=1,
                 smooth=False):
        super(Polygon, self).__init__(cors, fillColor, lineColor, width)
        self.isSmooth = smooth

    def render(self, pnt0, angle, app):
        w = self.width
        if w != 1:
            w *= app.track.zoom * 0.25
        cors = []
        for i in range(len(self.cors)):
            cor = self.cors[i].rotate(angle)
            cor = app.adjust_pz(cor + pnt0)
            cors += (cor.x, cor.y)  #convert to tuples, put into list
        app.ui.canvas.create_polygon(cors, fill=self.fillColor, outline=self.lineColor,
                              smooth=self.isSmooth, width=w)


class Arc(Shape):  #also pieslice
    def __init__(self, cors, fillColor="white", lineColor="black", width=1,
                 theta=(1, 0, 90)):
        super(Arc, self).__init__(cors, fillColor, lineColor, width)
        self.center = self.cors[0]
        self.radius = theta[0] * 0.25
        self.start = theta[1]
        self.extent = theta[2]

    def render(self, pnt0, angle, app):
        center = self.center.rotate(angle)
        center = app.adjust_pz(center + pnt0)
        x, y = center.x, center.y
        w = self.width
        if w != 1:
            w *= app.track.zoom * 0.25
        angle = math.degrees(angle)
        strt = self.start - angle
        r = self.radius * app.track.zoom
        if self.fillColor == None:
            app.ui.canvas.create_arc(x + r, y + r, x - r, y - r, style=tk.ARC,
                              start=strt, extent=self.extent,
                              width=w, outline=self.lineColor)
        else:
            app.ui.canvas.create_arc(x + r, y + r, x - r, y - r, style=tk.PIESLICE, width=w,
                              start=strt, extent=self.extent,
                              fill=self.fillColor, outline=self.lineColor)


class Circle(Shape):
    def __init__(self, cors, fillColor="white", lineColor="black", width=1,
                 radius=1):
        super(Circle, self).__init__(cors, fillColor, lineColor, width)
        self.center = self.cors[0]
        self.radius = radius * 0.25

    def render(self, pnt0, angle, app):
        center = self.center.rotate(angle)
        center = app.adjust_pz(center + pnt0)
        x, y = center.x, center.y
        w = self.width
        if w != 1:
            w *= app.track.zoom * 0.25
        r = self.radius * app.track.zoom
        app.ui.canvas.create_oval(x + r, y + r, x - r, y - r, width=w,
                           fill=self.fillColor, outline=self.lineColor)
