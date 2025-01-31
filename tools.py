

from dataclasses import dataclass

from geometry import Vector, distance, SolidLine, Line
from physics import in_window


def pencil(self, event, app):
    pos = Vector(event.x, event.y)
    if app.data.pause == True and in_window(pos, app.data):
        pos = app.inverse_pz(pos)
        if event.type == "4":  #pressed
            app.data.tempPoint = pos
        elif event.type == "6" and app.data.tempPoint != None:  #moved
            #to avoid making lines of 0 length
            minLen = app.tools.snapRadius / app.track.zoom
            if distance(app.data.tempPoint, pos) > minLen:
                lineType = app.tools.lineType
                line = SolidLine(app.data.tempPoint, pos, lineType)
                app.track.add_line(line)
                app.data.tempPoint = pos
        elif event.type == "5":
            app.data.tempPoint = None


def pan(self, event, app):
    if app.data.pause or not app.data.follow:
        z = app.track.zoom
        pos = (event.x, event.y)
        if event.type == "4":  #pressed
            app.data.tempCam = pos
        elif event.type == "5":  #released
            pass
        elif event.type == "6":  #moved
            pan = Vector(app.data.tempCam) - Vector(pos)
            app.track.panPos += pan / z
            app.data.tempCam = pos

def make_line(event, app):
    pos = Vector(event.x, event.y)
    if app.data.pause == True and in_window(pos, app.data):
        pos = app.inverse_pz(pos)
        if app.tools.snap == True:
            pos = app.ui.closest_point_to_line_point(pos)
        if event.type == "4":  #pressed
            app.data.tempPoint = pos
        elif event.type == "5" and app.data.tempPoint != None:  #released
            app.data.tempLine = None
            lineType = app.tools.lineType
            minLen = app.tools.snapRadius / app.track.zoom
            #to avoid making lines of 0 length
            if distance(app.data.tempPoint, pos) > minLen:
                line = SolidLine(app.data.tempPoint, pos, lineType)
                app.track.add_line(line)
            app.data.tempPoint = None
        elif event.type == "6" and app.data.tempPoint != None:  #moved
            app.data.tempLine = Line(app.data.tempPoint, pos)


def eraser(event, app):
    pos = Vector(event.x, event.y)
    if app.data.pause == True and event.type != "5" and in_window(pos, app.data):
        pos = app.inverse_pz(pos)
        removedLines = app.track.remove_lines_list(pos)
        if len(removedLines) > 0:
            for line in removedLines:
                if line in app.track.lines:
                    app.track.remove_line(line)


@dataclass
class Tools:
    lineType = "solid"
    eraserRadius = 10
    snapRadius = 10
    leftTool = pencil
    rightTool = pan
    snap = True
    avail_tools = {
        'pencil': pencil,
        'pan': pan,
        'make_line': make_line,
        'eraser': eraser
    }
    ctrlPressed = False

    def set_l_tool(self, tool_name):
        self.leftTool = self.avail_tools[tool_name]

    def get_l_tool_name(self):
        return self.leftTool.__name__

    def set_r_tool(self, tool_name):
        self.rightTool = self.avail_tools[tool_name]

    def set_line(self, lineType):
        self.lineType = lineType