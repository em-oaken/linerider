"""Player as in `DVD player`, not the physical person :)"""


import copy
from geometry import Vector


class Player:
    def __init__(self, app):
        self.app = app
        self.is_paused = True
        self.slowmo = False
        self.follow = True
        self.flag = False
        self.flagged_rider = None

        self.zoom = 1
        self.panPos = Vector(0, 0)
        self.cam = self.panPos

    def set_zoom(self, new_zoom):
        if 0.1 < new_zoom < 10:
            self.zoom = new_zoom

    def set_panpos(self):
        self.panPos = Vector(0, 0) - self.app.ui.canvas_center
        self.cam = self.panPos

    def stop(self):
        self.is_paused = True
        self.slowmo = False
        self.app.reset_rider()

    def play_pause(self):  # technically toggles between play and pause
        self.is_paused = not self.is_paused
        if self.is_paused and self.follow:  # pausing
            self.app.track.panPos = self.app.rider.pos.r - self.app.ui.canvas_center
        elif not self.is_paused:
            self.app.tm.tempLine = None

    def play_from_beginning(self):
        self.is_paused = False
        self.app.reset_rider(True)

    def toggle_slowmo(self):
        if not self.is_paused:
            self.slowmo = not self.slowmo

    def update_camera(self):
        # Bugfix needed: When set a flag and hit pause, the camera doesn't center on flag
        if self.is_paused or not self.follow:
            self.cam = self.panPos + self.app.ui.canvas_center
        else:
            self.cam = self.app.rider.pos.r
        c = self.app.ui.canvas_center
        z = self.zoom
        cam = self.cam
        self.app.ui.canvas_topleft = cam - c / z
        self.app.ui.canvas_bottomright = cam + c / z

    def set_flag(self):
        self.flag = True
        self.flagged_rider = copy.deepcopy(self.app.rider)
        # very tricky part here - Why deactivated?
        # self.flagged_rider.accQueueNow = copy.copy(self.rider.accQueuePast)

    def reset_flag(self):
        self.flag = False

    def in_window(self, pos: Vector):
        return (0 <= pos.x <= self.app.ui.canvas_size.x) and (0 <= pos.y <= self.app.ui.canvas_size.y)

    def adjust_pz(self, pnt):
        """turns rider's world position to screen position"""
        return (pnt - self.cam) * self.zoom + self.app.ui.canvas_center

    def inverse_pz(self, pnt):
        """turns screen position to rider's world position"""
        return (pnt - self.app.ui.canvas_center) / self.zoom + self.cam
