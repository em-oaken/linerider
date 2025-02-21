""" In this module:
Class Tool
Class Ink
Class ToolManager
"""

from geometry import Vector, distance, SolidLine, Line
from tool_helpers import Ink, Tool


class ToolManager:
    def __init__(self, app):
        self.app = app
        self.set_ink(Ink.Solid)
        self.sides = ['left', 'right', 'scroll', 'scroll-click']
        self.name = [None, None, None, None]
        self.tool = [None, None, None, None]  # handler for the actual tools

        self.take(Tool.Pencil, 'left')
        self.take(Tool.Pan, 'right')
        self.take(Tool.ZoomScroll, 'scroll')
        self.take(Tool.ZoomDrag, 'scroll-click')

        self.tempLine = None

    def get_tool_name(self, side:str):
        return self.name[self.get_side_id(side)].value

    def get_side_id(self, side:str):
        return self.sides.index(side)

    def take(self, tool:Tool, side:str = 'left'):
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
            case Tool.ZoomScroll:
                self.tool[side_id] = ZoomScroll(self)
            case Tool.ZoomDrag:
                self.tool[side_id] = ZoomDrag(self)

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
        if self.tm.app.player.is_paused and self.tm.app.player.in_window(pos):
            pos = self.tm.app.player.inverse_pz(pos)
            if event.type == "4":  # pressed
                self.temp_point = pos
            elif event.type == "6" and self.temp_point is not None:  # moved
                min_len = self.tm.app.player.snap_radius / self.tm.app.player.zoom
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
        if self.tm.app.player.is_paused and self.tm.app.player.in_window(pos):
            pos = self.tm.app.player.inverse_pz(pos)
            if self.tm.app.player.snap_ruler:
                pos = self.tm.app.track.get_closest_segment_end(pos)
            if event.type == "4":  # pressed
                self.temp_point = pos
            elif event.type == "5" and self.temp_point is not None:  # released
                self.tm.tempLine = None
                min_len = self.tm.app.player.snap_radius / self.tm.app.player.zoom
                if distance(self.temp_point, pos) > min_len:  # to avoid making lines of 0 length
                    self.tm.app.track.add_line(
                        SolidLine(self.temp_point, pos, self.tm.ink)
                    )
                self.temp_point = None
            elif event.type == "6" and self.temp_point is not None:  # moved
                self.tm.tempLine = Line(self.temp_point, pos)


class Eraser:
    def __init__(self, tm, radius=10):
        self.tm = tm  # ToolManager = tm
        self.radius = radius

    def use(self, event):
        pos = Vector(event.x, event.y)
        if self.tm.app.player.is_paused and event.type != "5" and self.tm.app.player.in_window(pos):  # on press and move
            pos = self.tm.app.player.inverse_pz(pos)
            removed_lines = self.tm.app.world.get_lines_around(pos, self.radius)
            if len(removed_lines) > 0:
                for line in removed_lines:
                    if line in self.tm.app.track.lines:
                        self.tm.app.track.remove_line(line)


class Pan:
    def __init__(self, tm):
        self.tm = tm  # ToolManager = tm

    def use(self, event):
        if self.tm.app.player.is_paused or not self.tm.app.player.follow:
            pos = (event.x, event.y)
            if event.type == "4":  # pressed
                self.tempCam = pos
            # elif event.type == "5":  # released
            #     pass
            elif event.type == "6":  # moved
                pan = Vector(self.tempCam) - Vector(pos)
                self.tm.app.player.panPos += pan / self.tm.app.player.zoom
                self.tempCam = pos

class ZoomScroll:
    """Changes zoom level contained between 0.1 and 10.
    Scroll up = zoom in = higher zoom value"""
    def __init__(self, tm):
        self.tm = tm  # ToolManager = tm

    def use(self, event):
        # About event.delta: https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/event-handlers.html
        if (event.delta % 120) == 0:  # Assumes that if delta is 120, then we're on Windows
            event.delta /= 120
        new_zoom = self.tm.app.player.zoom * 1.1 ** event.delta
        self.tm.app.player.set_zoom(new_zoom)

class ZoomDrag:
    """Reacts on scroll + drag up/down
    Move mouse up = zoom in = higher zoom value"""
    def __init__(self, tm):
        self.tm = tm  # ToolManager = tm

    def use(self, event):
        if event.type == '4':  # pressed
            self.orig_y = event.y
        elif event.type == '6':  # moved
            delta = event.y - self.orig_y
            new_zoom = self.tm.app.player.zoom * 0.99 ** delta
            self.tm.app.player.set_zoom(new_zoom)
            self.orig_y = event.y
