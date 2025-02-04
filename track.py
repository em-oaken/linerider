""" In this module:
Class Track
"""


from geometry import Vector
from physics import distance_from_line


class Track:
    def __init__(self, app):
        self.app = app
        self.lines = []
        self.name = "Untitled"
        self.startPoint = Vector(0, 0)

        # These 2 should be part of UI
        self.zoom = 1
        self.panPos = Vector(0, 0) - app.data.center

    def add_line(self, line, undo=False, redo=False):
        """Adds a single line to the track"""
        if len(self.lines) == 0:
            self.startPoint = line.r1 - Vector(0, 30)
            self.app.ui.make_rider()
        self.lines += [line]
        self.app.grid.add_to_grid(line)
        inverse = (line, self.remove_line)
        self.app.add_to_history(inverse, undo, redo)

    def remove_line(self, line, undo=False, redo=False):
        """Removes a single line from the track"""
        self.lines.remove(line)
        self.app.grid.remove_from_grid(line)
        inverse = (line, self.add_line)
        self.app.add_to_history(inverse, undo, redo)

    def get_lines_around(self, pos, radius):
        """Returns a set of lines to be removed, part of the eraser"""
        lines_found = set()
        cells = self.app.grid.grid_neighbors(pos)  # list of 9 closest cell positions
        for gPos in cells:  # each cell has a position/key on the grid/dict
            cell = self.app.grid.solids.get(gPos, set())  # each cell is a set of lines
            for line in cell:
                if distance_from_line(pos, line, self.app.data) * self.zoom <= radius:
                    lines_found.add(line)
            cell = self.app.grid.scenery.get(gPos, set())
            for line in cell:
                if distance_from_line(pos, line, self.app.data) * self.zoom <= radius:
                    lines_found.add(line)
        return lines_found

