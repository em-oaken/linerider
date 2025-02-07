""" In this module:
Class Track
"""

import datetime

from grid import Grid
from geometry import Vector
from physics import distance_from_line


class Track:
    def __init__(self, app):
        self.app = app
        self._name = f'Untitled, created on {datetime.datetime.now():%Y-%m-%d %H-%M-%S}'
        self.orig_name = True
        self.save_statustag = ''
        self.lines = []
        self.edits_not_saved = False
        self.startPoint = Vector(0, 0)

        self.grid = Grid(track=self)

        self.imexport_attrs = ('lines', )  #, 'grid')

        # These 2 should be part of UI
        self.zoom = 1
        self.panPos = Vector(0, 0) - app.data.center

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.orig_name = False

    def track_modified(self, isMdfy=True):
        self.edits_not_saved = isMdfy
        self.show_mdfy()

    def show_mdfy(self):
        self.save_statustag = '*' if self.edits_not_saved else ''

    def add_line(self, line, undo=False, redo=False):
        """Adds a single line to the track"""
        if len(self.lines) == 0:
            self.startPoint = line.r1 - Vector(0, 30)
            self.app.ui.make_rider()
        self.lines += [line]
        self.grid.add_to_grid(line)
        inverse = (line, self.remove_line)
        self.app.add_to_history(inverse, undo, redo)

    def remove_line(self, line, undo=False, redo=False):
        """Removes a single line from the track"""
        self.lines.remove(line)
        self.grid.remove_from_grid(line)
        inverse = (line, self.add_line)
        self.app.add_to_history(inverse, undo, redo)

    def get_lines_around(self, pos, radius):
        """Returns a set of lines to be removed, part of the eraser"""
        lines_found = set()
        cells = self.grid.grid_neighbors(pos)  # list of 9 closest cell positions
        for gPos in cells:  # each cell has a position/key on the grid/dict
            cell = self.grid.solids.get(gPos, set())  # each cell is a set of lines
            for line in cell:
                if distance_from_line(pos, line, self.app.data) * self.zoom <= radius:
                    lines_found.add(line)
            cell = self.grid.scenery.get(gPos, set())
            for line in cell:
                if distance_from_line(pos, line, self.app.data) * self.zoom <= radius:
                    lines_found.add(line)
        return lines_found

    # Loading and saving
    def import_(self):
        pass

    def build_export_payload(self):
        return {attr: eval(f'self.{attr}') for attr in self.imexport_attrs}


