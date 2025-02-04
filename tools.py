""" In this module:
Class Tool
Class Ink
Class ToolManager
"""




from geometry import Vector, distance, SolidLine, Line
from physics import in_window
from tool_helpers import Ink, Tool


class ToolManager:
    def __init__(self, app):
        self.app = app
        self.set_ink(Ink.Solid)
        self.snap_radius = 10
        self.snap_ruler = True
        self.name = [None, None]  # left, right
        self.tool = [None, None]  # handler for the actual tools
        self.take('left', Tool.Pencil)
        self.take('right', Tool.Pan)

    def get_tool_name(self, side:str):
        return self.name[self.get_side_id(side)].value

    def get_side_id(self, side:str):
        return 0 if side == 'left' else 1

    def take(self, side:str, tool:Tool):
        side_id = self.get_side_id(side)
        self.name[side_id] = tool
        match self.name[side_id]:
            case Tool.Pencil:
                self.tool[side_id] = Pencil(self)
            case Tool.Ruler:
                self.tool[side_id] = Ruler(self)
            case Tool.Eraser:
                self.tool[side_id] = Eraser(self)
            case Tool.Pan:
                self.tool[side_id] = Pan(self)

    def use(self, side:str, event):
        self.tool[self.get_side_id(side)].use(event)

    def set_ink(self, ink:Ink):
        self.ink = ink


class Pencil:
    def __init__(self, tm):
        self.tm = tm  # ToolManager = tm
        self.temp_point = None

    def use(self, event):
        pos = Vector(event.x, event.y)
        if self.tm.app.data.pause == True and in_window(pos, self.tm.app.data):
            pos = self.tm.app.inverse_pz(pos)
            if event.type == "4":  # pressed
                self.temp_point = pos
            elif event.type == "6" and self.temp_point is not None:  # moved
                min_len = self.tm.app.tm.snap_radius / self.tm.app.track.zoom
                if distance(self.temp_point, pos) > min_len:  # to avoid making lines of 0 length
                    line = SolidLine(self.temp_point, pos, self.tm.ink)
                    self.tm.app.track.add_line(line)
                    self.temp_point = pos
            elif event.type == "5":
                self.temp_point = None


class Ruler:
    def __init__(self, tm):
        self.tm = tm  # ToolManager = tm
        self.temp_point = None

    def use(self, event):
        pos = Vector(event.x, event.y)
        if self.tm.app.data.pause == True and in_window(pos, self.tm.app.data):
            pos = self.tm.app.inverse_pz(pos)
            if self.tm.snap_ruler:
                pos = self.tm.app.ui.closest_point_to_line_point(pos)
            if event.type == "4":  # pressed
                self.temp_point = pos
            elif event.type == "5" and self.temp_point is not None:  # released
                self.tm.app.data.tempLine = None  # TODO: What does this do?
                min_len = self.tm.snap_radius / self.tm.app.track.zoom
                if distance(self.temp_point, pos) > min_len:  # to avoid making lines of 0 length
                    self.tm.app.track.add_line(
                        SolidLine(self.temp_point, pos, self.tm.ink)
                    )
                self.temp_point = None
            elif event.type == "6" and self.temp_point is not None:  # moved
                self.tm.app.data.tempLine = Line(self.temp_point, pos)


class Eraser:
    def __init__(self, tm, radius=10):
        self.tm = tm  # ToolManager = tm
        self.radius = radius

    def use(self, event):
        pos = Vector(event.x, event.y)
        if self.tm.app.data.pause and event.ink != "5" and in_window(pos, self.tm.app.data):  # on press and move
            pos = self.tm.app.inverse_pz(pos)
            removed_lines = self.tm.app.track.get_lines_around(pos, self.radius)
            if len(removed_lines) > 0:
                for line in removed_lines:
                    if line in self.tm.app.track.lines:
                        self.tm.app.track.remove_line(line)


class Pan:
    def __init__(self, tm):
        self.tm = tm  # ToolManager = tm

    def use(self, event):
        if self.tm.app.data.pause or not self.tm.app.data.follow:
            pos = (event.x, event.y)
            if event.type == "4":  # pressed
                self.tm.app.data.tempCam = pos
            # elif event.type == "5":  # released
            #     pass
            elif event.type == "6":  # moved
                pan = Vector(self.tm.app.data.tempCam) - Vector(pos)
                self.tm.app.track.panPos += pan / self.tm.app.track.zoom
                self.tm.app.data.tempCam = pos



# TO THE BIN:
# def pencil(self, event, app):
#     pos = Vector(event.x, event.y)
#     if app.data.pause == True and in_window(pos, app.data):
#         pos = app.inverse_pz(pos)
#         if event.type == "4":  #pressed
#             app.data.tempPoint = pos
#         elif event.type == "6" and app.data.tempPoint != None:  #moved
#             #to avoid making lines of 0 length
#             minLen = app.tools.snapRadius / app.track.zoom
#             if distance(app.data.tempPoint, pos) > minLen:
#                 lineType = app.tools.lineType
#                 line = SolidLine(app.data.tempPoint, pos, lineType)
#                 app.track.add_line(line)
#                 app.data.tempPoint = pos
#         elif event.type == "5":
#             app.data.tempPoint = None
#
#
# def pan(self, event, app):
#     if app.data.pause or not app.data.follow:
#         z = app.track.zoom
#         pos = (event.x, event.y)
#         if event.type == "4":  #pressed
#             app.data.tempCam = pos
#         elif event.type == "5":  #released
#             pass
#         elif event.type == "6":  #moved
#             pan = Vector(app.data.tempCam) - Vector(pos)
#             app.track.panPos += pan / z
#             app.data.tempCam = pos
#
# def make_line(event, app):
#     pos = Vector(event.x, event.y)
#     if app.data.pause == True and in_window(pos, app.data):
#         pos = app.inverse_pz(pos)
#         if app.tools.snap == True:
#             pos = app.ui.closest_point_to_line_point(pos)
#         if event.type == "4":  #pressed
#             app.data.tempPoint = pos
#         elif event.type == "5" and app.data.tempPoint != None:  #released
#             app.data.tempLine = None
#             lineType = app.tools.lineType
#             minLen = app.tools.snapRadius / app.track.zoom
#             #to avoid making lines of 0 length
#             if distance(app.data.tempPoint, pos) > minLen:
#                 line = SolidLine(app.data.tempPoint, pos, lineType)
#                 app.track.add_line(line)
#             app.data.tempPoint = None
#         elif event.type == "6" and app.data.tempPoint != None:  #moved
#             app.data.tempLine = Line(app.data.tempPoint, pos)
#
#
# def eraser(event, app):
#     pos = Vector(event.x, event.y)
#     if app.data.pause == True and event.type != "5" and in_window(pos, app.data):
#         pos = app.inverse_pz(pos)
#         removedLines = app.track.get_lines_around(pos)
#         if len(removedLines) > 0:
#             for line in removedLines:
#                 if line in app.track.lines:
#                     app.track.remove_line(line)

#
# @dataclass
# class Tools:
#     lineType = "solid"
#     eraserRadius = 10
#     snapRadius = 10
#     leftTool = pencil
#     rightTool = pan
#     snap = True
#     avail_tools = {
#         'pencil': pencil,
#         'pan': pan,
#         'make_line': make_line,
#         'eraser': eraser
#     }
#     ctrlPressed = False
#
#     def set_l_tool(self, tool_name):
#         self.leftTool = self.avail_tools[tool_name]
#
#     def get_l_tool_name(self):
#         return self.leftTool.__name__
#
#     def set_r_tool(self, tool_name):
#         self.rightTool = self.avail_tools[tool_name]
#
#     def set_ink(self, lineType):
#         self.lineType = lineType