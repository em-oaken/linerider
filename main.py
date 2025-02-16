

import time
import os
import pickle
import copy
from pathlib import Path

from ui import UI, SavePopup, LoadPopup
from player import Player
from world import World
from track import Track
from rider import Rider
from tools import ToolManager

class App:
    def __init__(self):
        self.world = World(app=self)
        self.player = Player(app=self)
        self.ui = UI(app=self)
        self.player.set_panpos()
        self.track = Track(app=self)
        self.rider = Rider(self.track.startPoint)
        self.tm = ToolManager(self)
        self.start_session()
        self.dir_tracks = Path('./savedLines/')
        self.dir_tracks.mkdir(exist_ok=True)

        self.timer_fired()
        self.ui.start_mainloop()

    def start_session(self):
        self.time_now = time.time()
        self.undoStack = []
        self.redoStack = []
        self.world.collisionPoints = []

    def timer_fired(self):
        start = time.perf_counter()
        if not self.player.is_paused:
            self.world.step_forward()
        self.player.update_camera()
        self.ui.update_cursor()
        self.ui.redraw_all()

        # an attempt to keep a constant fps
        delay = int(1000 * (time.perf_counter() - start))
        delta = max(1, self.world.timeDelta - delay)
        if self.player.slowmo and not self.player.is_paused:
            delta = max(4, 200 - delay)
        self.ui.canvas.after(delta, self.timer_fired)

    def reset_rider(self, from_beginning=False):
        """Places rider on starting point OR on flag point"""
        if from_beginning or not self.player.flag:
            self.rider.rebuild(self.track.startPoint)
        else:
            self.rider = copy.deepcopy(self.player.flagged_rider)


    #####
    # New, open, save track
    #####
    def new_track(self):
        if self.track.edits_not_saved:
            if self.ui.open_popup('ok_or_cancel','Unsaved changes!', 'Unsaved changes!\nContinue?'):
                self.start_session()
                self.reset_rider()
        else:
            self.start_session()
            self.reset_rider()

    def reload_on_exit_save(self):
        # TODO: Make it open the last track saved!
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
            # TODO: Add something in case loading didn't work out (use backup!)
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

    #####
    # Undo, redo
    #####
    def add_to_history(self, action, undo, redo):
        if undo:
            self.redoStack += [action]
        else:  # else, put in undo stack
            self.undoStack += [action]
            if len(self.undoStack) > 500:  # it's up to the user to back up :|
                self.undoStack.pop(0)
        self.track.track_modified()

    def undo_cmd(self):
        if len(self.undoStack) > 0:
            obj, command = self.undoStack.pop(-1)
            command(obj, undo=True)

    def redo_cmd(self):
        if len(self.redoStack) > 0:
            obj, command = self.redoStack.pop(-1)
            command(obj, redo=True)

    def adjust_pz(self, pnt):
        """turns rider's world position to screen position"""
        return (pnt - self.player.cam) * self.player.zoom + self.ui.canvas_center

    def inverse_pz(self, pnt):
        """turns screen position to rider's world position"""
        return (pnt - self.ui.canvas_center) / self.player.zoom + self.player.cam

    def eval_speed(self):
        velocity = self.rider.points[0].r - self.rider.points[0].r0
        return velocity.magnitude()


if __name__ == "__main__":
    app = App()
