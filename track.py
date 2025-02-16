""" In this module:
Class Track
"""

import datetime

from grid import Grid
from geometry import Vector


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
        if len(self.lines) == 0:  # startPoint is to ensure rider always starts 30px above first line pixel!
            self.startPoint = line.r1 - Vector(0, 30)
            self.app.rider.rebuild(self.startPoint)
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

    # Loading and saving
    def import_(self, dict):
        # TODO: Implement restauring previous track upon fail saving
        # backupLines = self.lines
        # backupStart = self.startPoint

        self.__init__(self.app)
        for attr, val in dict.items():
            exec(f'self.{attr} = val')
        return True

    def build_export_payload(self):
        return {attr: eval(f'self.{attr}') for attr in self.imexport_attrs}
