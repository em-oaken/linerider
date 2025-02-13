

import time
import os
import pickle
import tkinter as tk
import copy
from pathlib import Path

from ui import UI, SavePopup, LoadPopup
from data import Data
from track import Track
from rider import Rider
from tools import ToolManager
from physics import resolve_collision

class App:
    def __init__(self):
        self.ctrlPressed = False

        self.data = Data()
        self.track = Track(app=self)
        self.rider = Rider(self.track.startPoint)
        self.tm = ToolManager(self)
        self.start_session()
        self.ui = UI(app=self)
        self.timer_fired()
        self.dir_tracks = Path('./savedLines/')
        self.dir_tracks.mkdir(exist_ok=True)

        self.ui.start_mainloop()

    def start_session(self):
        self.time_now = time.time()
        self.is_paused = True
        self.undoStack = []
        self.redoStack = []

        # TODO: Need to understand those below!
        self.data.cam = self.track.panPos
        self.data.flag = False
        self.data.collisionPoints = []

    def timer_fired(self):
        start = time.perf_counter()
        if not self.is_paused:
            self.update_positions()
        self.update_camera()
        self.ui.update_cursor()
        self.ui.redraw_all()

        # an attempt to keep a constant fps
        delay = int(1000 * (time.perf_counter() - start))
        delta = max(1, self.data.timeDelta - delay)
        if self.data.slowmo and not self.is_paused:
            delta = max(4, 200 - delay)
        self.ui.canvas.after(delta, self.timer_fired)

    def new_track(self):
        if self.track.edits_not_saved:
            if self.ui.open_popup('ok_or_cancel','Unsaved changes!', 'Unsaved changes!\nContinue?'):
                self.start_session()
                self.reset_rider()
        else:
            self.start_session()
            self.reset_rider()

    def reload_on_exit_save(self):
        path = "savedLines/ONEXITSAVE_"
        if os.path.isfile(path):
            with open(path, "rb") as track:
                self.track = pickle.load(track, encoding='latin1')
            self.track.grid.reset_grid()

    def open_track(self):

        if self.track.edits_not_saved:
            if not self.ui.open_popup(
                title='Unsaved track',
                content='Your track will be lost. Do you want to continue?'
            ):
                return

        def clickopen_callback(popup, filename):
            track_to_load = self.dir_tracks / filename
            print(f'Opening track {track_to_load}')

            # Read the file, and THEN try to load it
            with open(track_to_load, "rb") as pickled_track:
                try:
                    dict_track = pickle.load(pickled_track)
                except Exception as error:
                    popup.fail(f'Error while opening track: {error}')
            self.track.import_(dict_track)
            # TODO: Add something in case loading didn't work out (backup!)
            popup.success()

            self.start_session()
            self.rider.rebuild(self.track.startPoint)
            self.reset_rider()
            self.track.grid.reset_grid()

        _ = LoadPopup(
            title='Open track',
            track_list=[file.name for file in self.dir_tracks.iterdir()],
            clickopen_callback=clickopen_callback
        )

    def write_pickled_track_on_disk(self, filepath, export_payload):
        try:
            with open(filepath, 'wb') as pkl_handle:
                pickle.dump(export_payload, pkl_handle)
            self.track.track_modified(False)
            self.track.save_statustag = "Saved!"
            return True
        except Exception as error:
            print(f'Error while saving: {error}')
            self.track.save_statustag = "Failed to save! D:"
            return False

    def save_track(self, popup=False):
        export_payload = self.track.build_export_payload()

        def clicksave_callback(popup, trackname, overwrite=False):
            filepath = self.dir_tracks / trackname
            if filepath.exists() and not overwrite:
                popup.ask_if_overwrite()
            else:
                if self.write_pickled_track_on_disk(filepath, export_payload):
                    self.track.name = trackname
                    popup.success()
                else:
                    popup.fail()

        if popup or self.track.orig_name:
            _ = SavePopup(
                title='Save this track',
                ini_trackname=self.track.name,
                clicksave_callback=clicksave_callback
            )
        else:  # CTRL+S or [X] and name already modified -> Just save, no popup
            filepath = self.dir_tracks / self.track.name
            if self.write_pickled_track_on_disk(filepath, export_payload):
                return True
            return False


    def add_to_history(self, action, undo, redo):
        undoStack = self.undoStack
        redoStack = self.redoStack
        if undo:  # call from undo, put in redo stack
            redoStack += [action]
        else:  # else, put in undo stack
            undoStack += [action]
            if len(undoStack) > 500:  # it's up to the user to back up :|
                undoStack.pop(0)
        if not redo and not undo:  # eg call from line tool
            redoStack = []  # clear redo stack
        self.track.track_modified()

    def undo_cmd(self):
        if len(self.undoStack) == 0:
            pass
        else:
            obj, command = self.undoStack.pop(-1)  # last action
            command(obj, undo=True)

    def redo_cmd(self):
        if len(self.redoStack) == 0:
            pass
        else:
            obj, command = self.redoStack.pop(-1)
            command(obj, redo=True)

    def stop(self):
        self.is_paused = True
        self.data.slowmo = False
        self.reset_rider()

    def play_pause(self):  # technically toggles between play and pause
        self.is_paused = not self.is_paused
        if self.is_paused and self.data.follow:  # pausing
            self.track.panPos = self.rider.pos.r - self.data.center
        elif not self.is_paused:
            self.tm.tempLine = None

    def update_positions(self):
        if self.data.view_collisions:
            self.data.collisionPoints = []
        for pnt in self.rider.points:  # first, update points based on inertia, gravity, and drag
            pastPos = pnt.r
            self.free_fall(pnt)
            pnt.r0 = pastPos
        # scarves are special :|
        for pnt in self.rider.scarf:
            pastPos = pnt.r
            self.free_fall(pnt, 0.5)
            pnt.r0 = pastPos
        # add in the acceleration lines from previous step
        accQueue = self.rider.accQueueNow
        for pnt, lines in accQueue.items():
            for line in lines:
                acc = (line.r2 - line.r1).normalize() * self.data.acc
                pnt.r += acc
        self.rider.accQueuePast = copy.copy(self.rider.accQueueNow)
        self.rider.accQueueNow = dict()
        for _ in range(10):
            # collisions get priority to prevent phasing through lines
            for cnstr in self.rider.legsC:
                cnstr.resolve(neg_factor_only=True)
            if self.rider.onSled:
                for cnstr in self.rider.slshC:
                    cnstr.check_endurance(self.data, self.rider.kill_bosh)
            for cnstr in self.rider.constraints:
                cnstr.resolve()
            for pnt in self.rider.points:
                accLines = resolve_collision(pnt, self.data, self.track.grid, self.rider)
                if len(accLines) > 0:  # contains lines
                    self.rider.accQueueNow[pnt] = accLines

        for cnstr in self.rider.scarfCnstr:
            cnstr.resolve(static_p1=True)

    def free_fall(self, pnt, mass: float = 1):
        """All points are independent, acting only on inertia, drag, and gravity
        The velocity is implied with the previous position"""
        velocity = pnt.r - pnt.r0
        pnt.r = pnt.r + velocity * self.data.drag * mass + self.data.grav

    def flag(self):
        self.data.flag = True
        self.flagged_rider = copy.deepcopy(self.rider)

        # very tricky part here - Why deactivated?
        # self.flagged_rider.accQueueNow = copy.copy(self.rider.accQueuePast)

    def reset_flag(self):
        self.data.flag = False

    def play_from_beginning(self):
        self.is_paused = False
        self.reset_rider(True)

    def reset_rider(self, from_beginning=False):
        """Places rider on starting point OR on flag point"""
        if from_beginning or not self.data.flag:
            self.rider.rebuild(self.track.startPoint)
        else:
            self.rider = copy.deepcopy(self.flagged_rider)

    def lmouse_pressed(self, event):
        self.tm.use('left', event)

    def rmouse_pressed(self, event):
        self.tm.use('right', event)

    def mmouse_pressed(self, event):
        self.zoom(event)
        self.ui.redraw_all()

    def adjust_pz(self, pnt):
        """turns rider's world position to screen position"""
        return (pnt - self.data.cam) * self.track.zoom + self.data.center

    def inverse_pz(self, pnt):
        """turns screen position to rider's world position"""
        return (pnt - self.data.center) / self.track.zoom + self.data.cam

    def eval_speed(self):
        point = self.rider.points[0]
        velocity = point.r - point.r0
        return velocity.magnitude()

    def zoom(self, event):
        if event.type == "4":  # pressed
            self.temp_zoom = event.y
        #        cor = inverse_pz(vector(event.x, event.y))
        #        print(cor.x, cor.y)
        elif event.type == "6":  # moved
            delta = event.y - self.temp_zoom
            zoom = 0.99 ** delta
            zoom *= self.track.zoom
            if (0.1 < zoom and delta > 0) or (10 > zoom and delta < 0):
                self.track.zoom = zoom
            self.temp_zoom = event.y

    def zoom_m(self, event):
        if (event.delta % 120) == 0:
            event.delta /= 120
        zoom = 1.1 ** event.delta
        zoom *= self.track.zoom
        if ((0.1 < zoom and event.delta < 0) or
                (10 > zoom and event.delta > 0)):
            self.track.zoom = zoom

    def update_camera(self):
        if self.is_paused or not self.data.follow:
            self.data.cam = self.track.panPos + self.data.center
        else:
            self.data.cam = self.rider.pos.r
        c = self.data.center
        z = self.track.zoom
        cam = self.data.cam
        self.data.topLeft = cam - c / z
        self.data.bottomRight = cam + c / z


if __name__ == "__main__":
    app = App()
