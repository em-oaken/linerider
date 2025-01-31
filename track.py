

from dataclasses import dataclass

from geometry import Vector
from physics import distance_from_line


@dataclass
class Track:
    def __init__(self, app):
        self.app = app

    def add_line(self, line, undo=False, redo=False):
        """adds a single line to the track"""
        if len(self.lines) == 0:
            self.startPoint = line.r1 - Vector(0, 30)
            self.app.ui.make_rider()
        self.lines += [line]
        self.app.grid.add_to_grid(line)
        inverse = (line, self.remove_line)
        self.app.add_to_history(inverse, undo, redo)

    def remove_line(self, line, undo=False, redo=False):
        """removes a single line from the track"""
        self.lines.remove(line)
        self.app.grid.remove_from_grid(line)
        inverse = (line, self.add_line)
        self.app.add_to_history(inverse, undo, redo)

    def remove_lines_list(self, pos):
        """returns a set of lines to be removed, part of the eraser"""
        z = self.zoom
        removedLines = set()
        radius = self.app.tools.eraserRadius
        cells = self.app.grid.grid_neighbors(pos)  # list of 9 closest cell positions
        for gPos in cells:  # each cell has a position/key on the grid/dict
            cell = self.app.grid.solids.get(gPos, set())  # each cell is a set of lines
            for line in cell:
                if distance_from_line(pos, line) * z <= radius:
                    removedLines |= {line}
            cell = self.app.grid.scenery.get(gPos, set())
            for line in cell:
                if distance_from_line(pos, line) * z <= radius:
                    removedLines |= {line}
        return removedLines