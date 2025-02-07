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
        if self.tm.app.is_paused == True and in_window(pos, self.tm.app.data):
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
        if self.tm.app.is_paused == True and in_window(pos, self.tm.app.data):
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
        if self.tm.app.is_paused and event.ink != "5" and in_window(pos, self.tm.app.data):  # on press and move
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
        if self.tm.app.is_paused or not self.tm.app.data.follow:
            pos = (event.x, event.y)
            if event.type == "4":  # pressed
                self.tm.app.data.tempCam = pos
            # elif event.type == "5":  # released
            #     pass
            elif event.type == "6":  # moved
                pan = Vector(self.tm.app.data.tempCam) - Vector(pos)
                self.tm.app.track.panPos += pan / self.tm.app.track.zoom
                self.tm.app.data.tempCam = pos


