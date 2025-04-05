""" In this module:
Class Track

TODO: Grid should be accessed directly, all should go through Track()
TODO: Export grid coords to UI so that UI only draw lines (player requests UI to draw lines)
"""

import datetime

from grid import Grid
from geometry import Vector, distance, Line


class Track:
    def __init__(self, app):
        self.app = app
        self._name = f'Untitled, created on {datetime.datetime.now():%Y-%m-%d at %H-%M-%S}'
        self.orig_name = True
        self.save_statustag = ''
        self.lines = []
        self.edits_not_saved = False
        self.startPoint = Vector(0, 0)

        self.grid = Grid(track=self)

        self.imexport_attrs = ('lines', )

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.orig_name = False

    def track_modified(self, edits_not_saved=True):
        self.edits_not_saved = edits_not_saved
        self.save_statustag = '*' if self.edits_not_saved else ''

    def add_line(self, line, undo=False, redo=False):
        """Adds a single line to the track"""
        # startPoint is to ensure rider always starts 30px above first line pixel! Disabled.
        # if len(self.lines) == 0:
        #     self.startPoint = line.r1 - Vector(0, 30)
        #     self.app.rider.rebuild(self.startPoint)
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

    def get_closest_segment_end(self, pos):
        """finds the closest endpoint of a line segment to a given point"""
        closest_point = pos
        smallest_dist = self.app.player.snap_radius / self.app.player.zoom
        for line in self.get_lines_between(self.app.ui.canvas_topleft, self.app.ui.canvas_bottomright):
            dist = distance(line.r1, pos)
            if dist < smallest_dist:
                smallest_dist = dist
                closest_point = line.r1
            dist = distance(line.r2, pos)
            if dist < smallest_dist:
                smallest_dist = dist
                closest_point = line.r2
        return closest_point

    def get_drawing_data(self, grid):
        drawing_data = {}
        topleft_cell = self.grid.grid_pos(self.app.ui.canvas_topleft)
        bottomright_cell = self.grid.grid_pos(self.app.ui.canvas_bottomright + Vector(self.grid.spacing, self.grid.spacing))

        if grid:
            drawing_data['grid_vlines'] = [
                (Vector(x, topleft_cell[1]), Vector(x, bottomright_cell[1]))
                for x in range(topleft_cell[0], bottomright_cell[0], self.grid.spacing)
            ]
            drawing_data['grid_hlines'] = [
                (Vector(topleft_cell[0], y), Vector(bottomright_cell[0], y))
                for y in range(topleft_cell[1], bottomright_cell[1], self.grid.spacing)
            ]
            drawing_data['grid_cells_with_lines'] = [
                (Vector(cell), Vector(cell) + Vector(self.grid.spacing, self.grid.spacing))
                for cell in self.app.track.grid.solids
            ]
            drawing_data['grid_cells_with_rider'] = []
            for point in self.app.rider.points:
                velLine = Line(point.r, point.r + (point.r - point.r0))
                drawing_data['grid_cells_with_rider'].extend([
                    (
                        Vector(cell),
                        Vector(cell) + Vector(self.grid.spacing, self.grid.spacing),
                        'green' if cell in self.app.track.grid.solids else 'cyan'
                    )
                    for cell in self.app.track.grid.get_grid_cells(velLine)
                ])

        return drawing_data

    def get_lines_between(self, canvas_topleft, canvas_bottomright):
        lines = set()
        for gPos in self.grid.grid_in_screen(canvas_topleft, canvas_bottomright):
            lines.update(self.grid.solids.get(gPos, {None}))
            lines.update(self.grid.scenery.get(gPos, {None}))
        return {line for line in lines if line is not None}

    def get_lines_around(self, pos, radius):
        """Returns a set of lines to be removed, part of the eraser"""
        lines_found = set()
        cells = self.grid.grid_neighbors(pos)  # list of 9 closest cell positions
        for gPos in cells:  # each cell has a position/key on the grid/dict
            cell = self.grid.solids.get(gPos, set())  # each cell is a set of lines
            for line in cell:
                if self.app.world.distance_from_line(pos, line) * self.app.player.zoom <= radius:
                    lines_found.add(line)
            cell = self.grid.scenery.get(gPos, set())
            for line in cell:
                if self.app.world.distance_from_line(pos, line) * self.app.player.zoom <= radius:
                    lines_found.add(line)
        return lines_found

    # Loading and saving
    def import_(self, dict):
        # TODO: Implement restauring previous track upon fail saving
        # backupLines = self.lines
        # backupStart = self.startPoint

        self.__init__(self.app)
        for attr, val in dict.items():
            exec(f'self.{attr} = val')
        self.grid.reset_grid()
        return True

    def build_export_payload(self):
        return {attr: eval(f'self.{attr}') for attr in self.imexport_attrs}
