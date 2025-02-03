

import time
import os
import pickle
import tkinter as tk
from tkinter import messagebox
import copy

from ui import UI
from data import Data
from track import Track
from rider import Rider
from grid import Grid
from tools import ToolManager
from geometry import Vector
from physics import resolve_collision

class App:
    def __init__(self):
        self.data = Data()
        self.track = Track(app=self)
        self.rider = Rider()
        self.grid = Grid(app=self)
        self.tm = ToolManager(self)
        self.init()
        self.ui = UI(app=self)
        self.timer_fired()
        self.ui.start_mainloop()


    def init(self):
        self.ctrlPressed = False
        self.data.help = False
        self.data.helpIndex = 0
        self.grid.solids = dict()
        self.grid.scenery = dict()
        self.data.undoStack = []
        self.data.redoStack = []
        self.data.tempPoint = Vector(0, 0)
        self.data.tempLine = None
        self.data.pause = True
        self.data.cam = self.track.panPos
        self.data.flag = False
        self.data.timeCurrent = time.time()
        self.data.modified = False
        self.data.collisionPoints = []
        self.data.tracer = []

    def timer_fired(self):
        start = time.perf_counter()
        if not self.data.pause:
            self.update_positions()
        self.update_camera()
        self.ui.update_cursor()
        self.ui.redraw_all()

        # an attempt to keep a constant 40 fps
        delay = int(1000 * (time.perf_counter() - start))
        delta = self.data.timeDelta - delay
        delta = max(1, delta)
        slow = max(4, 200 - delay)
        if self.data.slowmo and not self.data.pause:
            delta = slow
        self.ui.canvas.after(delta, self.timer_fired)

    def new_track(self):
        if self.data.modified:
            if messagebox.askokcancel(
                    "Unsaved changes!", "Unsaved changes!\nContinue?"):
                self.init()
                self.reset_rider()
        else:
            self.init()
            self.reset_rider()

    def load_track(self):
        window = tk.Toplevel()
        window.title("Load Track")
        loadWindow = tk.Listbox(window)
        loadWindow.pack()

        def exit():
            window.destroy()

        if os.path.isdir("savedLines"):
            def do_load():
                loadWindow.delete(0, tk.END)
                for track in os.listdir("savedLines"):
                    loadWindow.insert(0, track)

                def load():
                    name = loadWindow.get(tk.ACTIVE)
                    path = "savedLines/" + name
                    backupLines = self.track.lines
                    backupStart = self.track.startPoint
                    self.init()
                    self.reset_rider()
                    with open(path, "rb") as track:
                        try:
                            self.track = pickle.load(track, encoding='latin1')  # ACTUAL LOADING
                        except Exception as error:  # in case it's not a valid file
                            self.track.lines = backupLines
                            self.track.startPoint = backupStart
                            loadWindow.delete(0, tk.END)
                            loadWindow.insert(0, "Y U NO LOAD")
                            loadWindow.insert(tk.END, "VALID TRACK")
                            print(error)
                            window.after(1000, do_load)
                    self.ui.make_rider()
                    self.grid.reset_grid()

                cancelButton.config(text="Close")
                loadButton.config(text="Load", command=load)

            cancelButton = tk.Button(window, text="Cancel", command=exit)
            loadButton = tk.Button(window, text="Ok", command=do_load)
            loadButton.pack()
            cancelButton.pack()
            if self.data.modified:
                loadWindow.insert(0, "Unsaved changes!")
                loadWindow.insert(tk.END, "Continue?")
            else:
                do_load()
        else:
            loadWindow.insert(0, "savedLines folder")
            loadWindow.insert(tk.END, "does not exist!")
            cancelButton = tk.Button(window, text="Okay ):", command=exit)
            loadWindow.pack()

    def save_track(self):
        window = tk.Toplevel()
        window.title("Save Track")
        saveWindow = tk.Entry(window)
        saveWindow.insert(0, self.track.name)

        def exit():
            window.destroy()

        def save_attempt():
            name = saveWindow.get()
            self.track.name = name
            path = "savedLines/" + name

            def save():
                saveWindow.delete(0, tk.END)
                try:
                    with open(path, "wb") as track:
                        pickle.dump(self.track, track)  # ACTUAL SAVING
                    saveWindow.insert(0, "Saved!")
                    self.track_modified(False)
                    window.after(1000, exit)
                except Exception as error:
                    saveWindow.insert(0, "Failed to save! D:")
                    print(error)
                    window.after(1000, lambda: undo(False))

            def undo(YN=True):
                saveWindow.delete(0, tk.END)
                saveWindow.insert(0, name)
                loadButton.config(text="Save", command=save_attempt)
                if YN:
                    cancelButton.destroy()

            if not os.path.isdir("savedLines"):
                os.mkdir("savedLines")
            if os.path.isfile(path):
                saveWindow.delete(0, tk.END)
                saveWindow.insert(0, "Overwrite track?")
                loadButton.config(text="Yes", command=save)
                cancelButton = tk.Button(window, text="No", command=undo)
                cancelButton.pack()
            else:
                save()

        loadButton = tk.Button(window, text="Save", command=save_attempt)
        saveWindow.pack()
        loadButton.pack()

    def on_exit_save(self):
        if not os.path.isdir("savedLines"):
            os.mkdir("savedLines")
        path = "savedLines/ONEXITSAVE_"
        self.track.name = "ONEXITSAVE_"
        try:
            with open(path, "wb") as track:
                pickle.dump(self.track, track)
        except Exception as error:
            print('Error saving: ', error)
            if not self.data.modified or tk.messagebox.askokcancel(
                    "Unsaved changes!", "Failed to save! D:\nExit anyways?"):
                self.ui.root.destroy()
        self.ui.root.destroy()

    def reload_on_exit_save(self):
        path = "savedLines/ONEXITSAVE_"
        if os.path.isfile(path):
            with open(path, "rb") as track:
                self.track = pickle.load(track, encoding='latin1')
            self.grid.reset_grid()

    def track_modified(self, isMdfy=True):
        self.data.modified = isMdfy
        self.data.show_mdfy()

    def add_to_history(self, action, undo, redo):
        undoStack = self.data.undoStack
        redoStack = self.data.redoStack
        if undo:  # call from undo, put in redo stack
            redoStack += [action]
        else:  # else, put in undo stack
            undoStack += [action]
            if len(undoStack) > 500:  # it's up to the user to back up :|
                undoStack.pop(0)
        if not redo and not undo:  # eg call from line tool
            redoStack = []  # clear redo stack
        self.track_modified()

    def undo_cmd(self):
        if len(self.data.undoStack) == 0:
            pass
        else:
            obj, command = self.data.undoStack.pop(-1)  # last action
            command(obj, undo=True)

    def redo_cmd(self):
        if len(self.data.redoStack) == 0:
            pass
        else:
            obj, command = self.data.redoStack.pop(-1)
            command(obj, redo=True)

    def stop(self):
        self.data.pause = True
        self.data.slowmo = False
        self.reset_rider()

    def play_pause(self):  # technically toggles between play and pause
        self.data.pause = not self.data.pause
        if self.data.pause and self.data.follow:  # pausing
            self.track.panPos = self.rider.pos.r - self.data.center
        elif not self.data.pause:
            self.data.tempLine = None

    def update_positions(self):
        if self.data.viewCollisions:
            self.data.collisionPoints = []
        for pnt in self.rider.points:
            # first, update points based on inertia, gravity, and drag
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
        a = self.data.acc
        for pnt, lines in accQueue.items():
            for line in lines:
                acc = (line.r2 - line.r1).normalize()
                acc *= a
                pnt.r += acc
        self.rider.accQueuePast = copy.copy(self.rider.accQueueNow)
        self.rider.accQueueNow = dict()  # empty queue after
        for i in range(self.data.iterations):
            # collisions get priority to prevent phasing through lines
            for cnstr in self.rider.legsC:
                cnstr.resolve_legs()
            if self.rider.onSled:
                for cnstr in self.rider.slshC:
                    cnstr.check_endurance(self.data, self.rider.kill_bosh)
            for cnstr in self.rider.constraints:
                cnstr.resolve_constraint()
            for pnt in self.rider.points:
                accLines = resolve_collision(pnt, self.data, self.grid, self.rider)
                if len(accLines) > 0:  # contains lines
                    self.rider.accQueueNow[pnt] = accLines
        scarfStrength = 1
        # again, scarves are special
        for i in range(scarfStrength):
            for cnstr in self.rider.scarfCnstr:
                cnstr.resolve_scarf()

    def free_fall(self, pnt, mass: float = 1):
        """All points are independent, acting only on inertia, drag, and gravity
        The velocity is implied with the previous position"""
        velocity = pnt.r - pnt.r0
        pnt.r = pnt.r + velocity * self.data.drag * mass + self.data.grav

    def flag(self):
        self.data.flag = True
        self.data.flagBosh = copy.deepcopy(self.rider)
        # very tricky part here

    #   canvas.data.flagBosh.accQueueNow = copy.copy(
    #                canvas.data.flagBosh.accQueuePast)

    def reset_flag(self):
        self.data.flag = False

    def play_from_beginning(self):
        self.data.pause = False
        self.reset_rider(True)

    def reset_rider(self, fromBeginning=False):
        self.data.tracer = []
        if fromBeginning or not self.data.flag:
            self.ui.make_rider()
        else:
            self.rider = copy.deepcopy(self.data.flagBosh)

    def lmouse_pressed(self, event):
        self.tm.use('left', event)

    def rmouse_pressed(self, event):
        self.tm.use('right', event)

    def mmouse_pressed(self, event):
        self.zoom(event)
        self.ui.redraw_all()

    def adjust_pz(self, pnt):
        return (pnt - self.data.cam) * self.track.zoom + self.data.center

    def inverse_pz(self, pnt):
        """turns relative position to absolute"""
        return (pnt - self.data.center) / self.track.zoom + self.data.cam

    def eval_speed(self):
        totalVel = Vector(0, 0)
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
        if self.data.pause or not self.data.follow:
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
