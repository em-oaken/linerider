
import os
import copy
import tkinter as tk
from tkinter import messagebox
import time

from geometry import Vector, Line, distance
from tools import Tool, Ink

class UI:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="white")
        self.setup_window()
        self.canvas.pack(fill="both", expand=True)

        self.temp_message = ''
        self.help_popup = False
        self.help_index = 0

        def resize(event):
            self.app.data.windowSize = Vector(event.width, event.height)
            oldCenter = copy.copy(self.app.data.center)
            self.app.data.center = Vector(event.width / 2, event.height / 2)
            delta = self.app.data.center - oldCenter
            self.app.track.panPos -= delta

        self.canvas.bind("<Configure>", resize)

    def start_mainloop(self):
        self.root.mainloop()

    def setup_window(self):
        self.root.title("Line Rider")

        def reset_temp_message():
            self.temp_message = ''

        def display_t(boolean, m1, m2):
            self.temp_message = m1 if boolean else m2
            self.canvas.after(1000, reset_temp_message)

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        # FILE
        fileMenu = tk.Menu(menubar, tearoff=False)
        fileMenu.add_command(label='New (ctrl+n)', command=self.app.new_track)
        fileMenu.add_command(label='Open (ctrl+o)', command=self.app.open_track)
        fileMenu.add_command(label='Save (ctrl+s)', command=self.app.save_track)
        menubar.add_cascade(label='File', menu=fileMenu)

        # EDIT
        def undo():
            if self.app.is_paused: self.app.undo_cmd()

        def redo():
            if self.app.is_paused: self.app.redo_cmd()

        def snap():
            self.app.tm.snap_ruler = not self.app.tm.snap_ruler
            display_t(self.app.tm.snap_ruler, "Line snapping on", "Line snapping off")

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Undo (ctrl+z)", command=undo)
        edit_menu.add_command(label="Redo (ctrl+shift+z)", command=redo)
        edit_menu.add_command(label="Toggle Line Snapping (s)", command=snap)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        tool_menu = tk.Menu(menubar)
        tool_menu.add_command(label="Pencil (q)", command=lambda: self.app.tm.take('left', Tool.Pencil))
        tool_menu.add_command(label="Ruler (w)", command=lambda: self.app.tm.take('left', Tool.Ruler))
        tool_menu.add_command(label="Eraser (e)", command=lambda: self.app.tm.take('left', Tool.Eraser))
        tool_menu.add_separator()
        tool_menu.add_command(label="Solid (1)", command=lambda: self.app.tm.set_ink(Ink.Solid))
        tool_menu.add_command(label="Acceleration (2)", command=lambda: self.app.tm.set_ink(Ink.Acc))
        tool_menu.add_command(label="Scenery (3)", command=lambda: self.app.tm.set_ink(Ink.Scene))
        menubar.add_cascade(label="Tools", menu=tool_menu)

        # view
        def view_vector():
            self.app.data.view_vector = not self.app.data.view_vector
            display_t(self.app.data.view_vector, "Showing velocity", "Hiding velocity")

        def view_points():
            self.app.data.view_points = not self.app.data.view_points
            display_t(self.app.data.view_points, "Showing snapping points",
                      "Hiding snapping points")

        def view_lines():
            self.app.data.view_lines = not self.app.data.view_lines
            display_t(self.app.data.view_lines, "Showing lines", "Hiding lines")

        def view_grid():
            self.app.data.view_grid = not self.app.data.view_grid
            print('o')
            display_t(self.app.data.view_grid, "Showing grid", "hiding grid")

        def view_status():
            self.app.data.view_status = not self.app.data.view_status
            display_t(self.app.data.view_status, "Showing status messages",
                      "Status messages are hidden, how can you see this?")

        def view_collisions():
            self.app.data.view_collisions = not self.app.data.view_collisions
            display_t(self.app.data.view_collisions, "Showing collision points",
                      "Hiding collision points")

        def go_to_start():
            if self.app.is_paused:
                self.app.track.panPos = self.app.track.startPoint - self.app.data.center

        def last_line():
            if self.app.is_paused and len(self.app.track.lines) > 0:
                lastLine = self.app.track.lines[-1].r2
                self.app.track.panPos = lastLine - self.app.data.center

        def follow_rider():
            self.app.data.follow = not self.app.data.follow
            display_t(self.app.data.follow, "Following rider", "Not following rider")

        def view_thin_lines():
            self.app.data.view_thin_lines = not self.app.data.view_thin_lines
            display_t(self.app.data.view_thin_lines, "Viewing normal lines",
                      "Viewing normal lines")

        viewMenu = tk.Menu(menubar)
        viewMenu.add_command(label="Velocity Vectors (v)", command=view_vector)
        viewMenu.add_command(label="Points (b)", command=view_points)
        viewMenu.add_command(label="Collisions (c)", command=view_collisions)
        viewMenu.add_command(label="Thin Lines", command=view_thin_lines)
        viewMenu.add_command(label="Grid", command=view_grid)
        viewMenu.add_command(label="Status", command=view_status)
        viewMenu.add_separator()
        viewMenu.add_command(label="Starting Point (home)", command=go_to_start)
        viewMenu.add_command(label="Last Line (end)", command=last_line)
        viewMenu.add_command(label="Follow Rider", command=follow_rider)
        menubar.add_cascade(label="View", menu=viewMenu)

        # playback
        def slowmo():
            if not self.app.is_paused:
                self.app.data.slowmo = not self.app.data.slowmo

        playMenu = tk.Menu(menubar)
        playMenu.add_command(label="Play/Pause (space/p)", command=self.app.play_pause)
        playMenu.add_command(label="Stop (space)", command=self.app.stop)
        playMenu.add_command(label="Step (t)", command=self.app.update_positions)
        playMenu.add_command(label="Reset Position (r)", command=self.app.reset_rider)
        playMenu.add_command(label="Flag (f)", command=self.app.flag)
        playMenu.add_command(label="Reset Flag (ctrl+f)", command=self.app.reset_flag)
        playMenu.add_command(label="Play from Beginning (ctrl+p)",
                             command=self.app.play_from_beginning)
        playMenu.add_command(label="Slow-mo (m)", command=slowmo)
        menubar.add_cascade(label="Playback", menu=playMenu)

        # help
        def view_help():
            self.help_popup = not self.help_popup

        helpMenu = tk.Menu(menubar)
        helpMenu.add_command(label="Help", command=view_help)
        helpMenu.add_command(label="About", command=self.do_about)
        menubar.add_cascade(label="Help", menu=helpMenu)
        # bindings
        self.root.bind("<Button-1>", self.app.lmouse_pressed)
        self.root.bind("<B1-Motion>", self.app.lmouse_pressed)
        self.root.bind("<ButtonRelease-1>", self.app.lmouse_pressed)
        self.root.bind("<Button-3>", self.app.rmouse_pressed)
        self.root.bind("<B3-Motion>", self.app.rmouse_pressed)
        self.root.bind("<ButtonRelease-3>", self.app.rmouse_pressed)
        self.root.bind("<Button-2>", self.app.mmouse_pressed)
        self.root.bind("<B2-Motion>", self.app.mmouse_pressed)
        self.root.bind("<MouseWheel>", self.app.zoom_m)
        self.app.ctrlPressed = False

        def key_pressed(event):
            k = event.keysym
            c = event.char
            if k == "Control_L" or k == "Control_R" or k == "Command_L" or k == "Command_R":
                self.app.ctrlPressed = True
            if self.app.ctrlPressed:
                return None
            elif c == "t":
                if self.app.is_paused: self.app.update_positions()
            elif c == "p":
                self.app.play_pause()
            elif c == " ":
                if self.app.is_paused:
                    self.app.play_pause()
                else:
                    self.app.stop()
            elif c == "q":
                self.app.tm.take(Tool.Pencil)
            elif c == "w":
                self.app.tm.take(Tool.Ruler)
            elif c == "e":
                self.app.tm.take(Tool.Eraser)
            elif c == "m":
                slowmo()
            elif c == "r":
                self.app.reset_rider()
            elif c == "f":
                self.app.flag()
            elif c == "v":
                view_vector()
            elif c == "b":
                view_points()
            elif c == "1":
                self.app.tm.set_ink(Ink.Solid)
            elif c == "2":
                self.app.tm.set_ink(Ink.Acc)
            elif c == "3":
                self.app.tm.set_ink(Ink.Scene)
            elif c == "d":
                self.app.dump()
            elif c == "h":
                view_help()
            elif c == "s":
                snap()
            elif c == "c":
                view_collisions()
            if self.help_popup:
                i = self.help_index
                if k == "Left" and i > 0:
                    self.help_index -= 1
                if k == "Right" and i < 7:
                    self.help_index += 1
            self.redraw_all()

        def key_released(event):
            k = event.keysym
            if k == "Control_L" or k == "Control_R" or k == "Command_L" or k == "Command_R":
                self.app.ctrlPressed = False

        self.root.bind("<KeyPress>", key_pressed)
        self.root.bind("<KeyRelease>", key_released)
        self.root.bind("<Home>", lambda e: go_to_start())
        self.root.bind("<End>", lambda e: last_line())
        if os.name == "mac":
            self.root.bind("<Command-z>", lambda _: undo())
            self.root.bind("<Command-Shift-Z>", lambda _: redo())
            self.root.bind("<Command-s>", lambda _: self.app.save_track(popup=False))
            self.root.bind("<Command-Shift-s>", lambda _: self.app.save_track(popup=True))
            self.root.bind("<Command-p>", lambda _: self.app.play_from_beginning())
            self.root.bind("<Command-o>", lambda _: self.app.open_track())
            self.root.bind("<Command-n>", lambda _: self.app.new_track())
            self.root.bind("<Command-f>", lambda _: self.app.reset_flag())
        else:
            self.root.bind("<Control-z>", lambda _: undo())
            self.root.bind("<Control-Shift-Z>", lambda _: redo())
            self.root.bind("<Control-s>", lambda _: self.app.save_track(popup=False))
            self.root.bind("<Control-Shift-s>", lambda _: self.app.save_track(popup=True))
            self.root.bind("<Control-p>", lambda _: self.app.play_from_beginning())
            self.root.bind("<Control-o>", lambda _: self.app.open_track())
            self.root.bind("<Control-n>", lambda _: self.app.new_track())
            self.root.bind("<Control-f>", lambda _: self.app.reset_flag())
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.on_exit())

    def redraw_all(self):
        self.canvas.delete(tk.ALL)
        if self.app.data.view_grid:
            self.draw_grid()
        if self.app.data.view_lines:
            self.draw_lines()
        if self.app.data.view_points:
            self.draw_points()
        if self.app.data.flag:
            self.draw_flag()
        self.draw_rider()
        if self.app.data.view_vector:
            self.draw_vectors()
        if self.app.data.view_collisions:
            self.draw_collisions()
        if self.app.data.view_status:
            self.status_display()
        if self.help_popup:
            self.do_help()

    def show_grid(self):
        topLeft, bottomRight = self.app.data.topLeft, self.app.data.bottomRight
        g = self.app.track.grid.spacing
        topLeft = self.app.track.grid.grid_pos(topLeft)
        bottomRight = self.app.track.grid.grid_pos(bottomRight + Vector(g, g))
        for x in range(topLeft[0], bottomRight[0], g):
            a, b = Vector(x, topLeft[1]), Vector(x, bottomRight[1])
            a, b = self.app.adjust_pz(a), self.app.adjust_pz(b)
            self.canvas.create_line(a.x, a.y, b.x, b.y)
        for y in range(topLeft[1], bottomRight[1], g):
            a, b = Vector(topLeft[0], y), Vector(bottomRight[0], y)
            a, b = self.app.adjust_pz(a), self.app.adjust_pz(b)
            self.canvas.create_line(a.x, a.y, b.x, b.y)

    def draw_grid(self):
        """for debugging"""
        g = self.app.track.grid.spacing
        self.show_grid()
        for cell in self.app.track.grid.solids:  # cells are positions/keys in the grid dict
            cell = Vector(cell)
            cell2 = cell + Vector(g, g)
            cell, cell2 = self.app.adjust_pz(cell), self.app.adjust_pz(cell2)
            self.canvas.create_rectangle(cell.x, cell.y, cell2.x, cell2.y, fill="yellow")
        for point in self.app.rider.points:
            velocity = point.r - point.r0
            velLine = Line(point.r, point.r + velocity)
            cells = self.app.track.grid.get_grid_cells(velLine)
            for cell in cells:
                if cell in self.app.track.grid.solids:
                    color = "green"
                else:
                    color = "cyan"
                cell = Vector(cell)
                cell2 = cell + Vector(g, g)
                cell, cell2 = self.app.adjust_pz(cell), self.app.adjust_pz(cell2)
                self.canvas.create_rectangle(cell.x, cell.y, cell2.x, cell2.y, fill=color)

    def lines_in_screen(self):
        lines = set()
        for gPos in self.app.track.grid.grid_in_screen():
            try:  # a bit more efficient than using a conditional
                lines |= self.app.track.grid.solids[gPos]
            except KeyError:
                pass
            try:
                lines |= self.app.track.grid.scenery[gPos]
            except KeyError:
                pass
        return lines

    def closest_point_to_line_point(self, pos):
        """finds the closest endpoint of a line segment to a given point"""
        closestPoint = pos
        minDist = self.app.tm.snap_radius / self.app.track.zoom
        for line in self.lines_in_screen():
            dist = distance(line.r1, pos)
            if dist < minDist:
                minDist = dist
                closestPoint = line.r1
            dist = distance(line.r2, pos)
            if dist < minDist:
                minDist = dist
                closestPoint = line.r2
        return closestPoint

    def draw_lines(self):
        width = 1 if self.app.data.view_thin_lines else 3 * self.app.track.zoom

        for line in self.lines_in_screen():
            a, b = self.app.adjust_pz(line.r1), self.app.adjust_pz(line.r2)
            color = "black"
            arrow = None
            if line.ink == Ink.Scene and self.app.is_paused:
                color = "green"
            if line.ink == Ink.Acc and self.app.is_paused:
                color = "red"
                arrow = tk.LAST
            self.canvas.create_line(a.x, a.y, b.x, b.y, width=width,
                               caps=tk.ROUND, fill=color, arrow=arrow)

        if self.app.rider.onSled:
            for line in self.app.rider.sledString:
                a, b = self.app.adjust_pz(line[0].r), self.app.adjust_pz(line[1].r)
                self.canvas.create_line(a.x, a.y, b.x, b.y)

        if self.app.tm.tempLine is not None and self.app.is_paused:
            line = self.app.tm.tempLine
            a, b = self.app.adjust_pz(line.r1), self.app.adjust_pz(line.r2)
            color = 'red' if distance(a, b) < self.app.tm.snap_radius else 'grey'
            self.canvas.create_line(a.x, a.y, b.x, b.y, fill=color)

    def draw_points(self):
        r = self.app.tm.snap_radius
        #    for point in canvas.data.points:
        #        pnt = adjust_pz(point.r)
        #        x, y = pnt.x, pnt.y
        #        if is_in_region((x,y), vector(-r,-r), canvas.data.center*2+vector(r,r)):
        #            canvas.create_oval((x-r, y-r), (x+r, y+r))
        for line in self.app.track.lines:
            pnt = self.app.adjust_pz(line.r1)
            x, y = pnt.x, pnt.y
            self.canvas.create_oval((x - r, y - r), (x + r, y + r), outline="blue", width=3)
            pnt = self.app.adjust_pz(line.r2)
            x, y = pnt.x, pnt.y
            self.canvas.create_oval((x - r, y - r), (x + r, y + r), outline="blue", width=3)

    def draw_flag(self):
        parts = self.app.flagged_rider.flag_drawing_vectors
        bosh = self.app.flagged_rider.boshParts
        for i in range(len(parts)):
            part = parts[i]  # part contains tuples of line segments and stuff
            point0, point1 = bosh[i]  # each value has two Point objects
            angle = (point1.r - point0.r).get_angle()
            for shape in part:  # segment: tuple of line properties for rendering
                shape.render(point0.r, angle, self.app)

    def draw_scarf(self, c):
        color = c
        w = 4 * self.app.track.zoom
        for line in self.app.rider.scarfCnstr:
            if color == c:
                color = "white"
            else:
                color = c
            pnt1, pnt2 = self.app.adjust_pz(line.pnt1.r), self.app.adjust_pz(line.pnt2.r)
            self.canvas.create_line([(pnt1.x, pnt1.y), (pnt2.x, pnt2.y)],
                               width=w, fill=color, capstyle=tk.BUTT)

    def draw_rider(self):
        self.draw_scarf("red")
        parts = self.app.rider.drawing_vectors
        bosh = self.app.rider.boshParts
        for i in range(len(parts)):
            part = parts[i]  # part contains tuples of line segments and stuff
            point0, point1 = bosh[i]  # each value has two Point objects
            angle = (point1.r - point0.r).get_angle()
            for shape in part:  # segment: tuple of line properties for rendering
                shape.render(point0.r, angle, self.app)

    def draw_vectors(self):
        #    for pnt in canvas.rider.points:
        pnt = self.app.rider.pos
        velocity = (pnt.r - pnt.r0)
        vel = velocity.normalize() * 100
        a, b = self.app.adjust_pz(pnt.r), self.app.adjust_pz(pnt.r + vel)
        speed = velocity.magnitude()
        red = int(254 * (1.02 ** (-speed))) + 1
        blue = int(255 * (1 - (1.05 ** (-speed))))
        color = blue + (red << 16)  # 0xrr00bb
        color = hex(color)[2:]
        if len(color) < 6:
            color = "#0" + color
        else:
            color = "#" + color
        self.canvas.create_line(a.x, a.y, b.x, b.y, width=3, arrow=tk.LAST,
                           fill=color)

    def draw_collisions(self):
        for point in self.app.rider.points:
            pnt = self.app.adjust_pz(point.r)
            self.canvas.create_oval(pnt.x + 2, pnt.y + 2, pnt.x - 2, pnt.y - 2, fill="red")
        for pnt in self.app.data.collisionPoints:
            pnt = self.app.adjust_pz(pnt)
            self.canvas.create_oval(pnt.x + 2, pnt.y + 2, pnt.x - 2, pnt.y - 2, fill="yellow", width=0)

    def status_display(self):
        """Displays info on top-left corner"""
        message = f'Track: {self.app.track.name}'
        if len(self.app.track.lines) == 0:
            message = "Press H for help"
        if self.help_popup:
            message = "Press H to close"
        message += " " + self.app.track.save_statustag

        tmp_msg = '' if self.temp_message == '' else self.temp_message + '\n'

        prev_time_now = self.app.time_now
        self.app.time_now = time.time()
        duration = self.app.time_now - prev_time_now
        fps = 1/float(duration) if duration != 0 else 0

        line_count = len(self.app.track.lines)
        speed = f'{self.app.eval_speed():.1f} pixels/frame' if not self.app.is_paused else ''

        self.canvas.create_text(
            5, 0, anchor="nw",
            text=f'{message}\n{tmp_msg}{fps:.0f} fps\n{line_count} lines in track\n{speed}'
        )

    def update_cursor(self):
        tools_to_cur = {
            'default': 'arrow',
            'pencil': 'pencil',
            'ruler': 'crosshair',
            'eraser': 'circle'
        }
        cur = tools_to_cur['default']
        if self.app.is_paused:
            cur = tools_to_cur[self.app.tm.get_tool_name('left')]
        self.canvas.config(cursor=cur)

    def on_exit(self):
        if not self.app.save_track():
            if not self.open_popup('ok_or_cancel', 'Unsaved changes!', 'Failed to save!\nExit anyways?'):
                return
        self.root.destroy()


    def open_popup(self, type='ok_or_cancel', title='', content=''):
        if type == 'ok_or_cancel':
            return messagebox.askokcancel(title, content)

    def do_help(self):
        center = self.app.data.center
        TL = center - Vector(300, 200)
        BR = center + Vector(300, 200)
        self.canvas.create_rectangle(TL.x, TL.y, BR.x, BR.y, width=5, fill="#eee")

        def title(text):
            self.canvas.create_text(TL.x + 10, TL.y + 5, anchor=tk.NW, width=580,
                               font=("Arial", "25", "bold"), text=text)

        def contents(x, y, w, text):
            self.canvas.create_text(TL.x + x, TL.y + y, anchor=tk.NW, width=w,
                               font=("Arial", "15"), text=text)

        def to_play():
            title("How to play Line Rider Python")
            contents(10, 60, 580, """Draw a line from the top left to the bottom \
    right with the left mouse button. Press the space bar to play and watch the \
    rider go. Press space again to stop and go back to editing. (paraphrased from \
    the original version of Line Rider)
    That was interesting. Was it? If you want to do more, use the left and \
    right arrow keys to navigate the help contents to see how to do more.
    Note: If you open a menu and click on the dashed lines, you "tear off" \
    the menu to make a separate window for the menu.
    Note2: \
    If you're on a mac, the menus are at the top of your screen, not this window.
    """)

        def tools():  # and edit
            title("Editing tracks")
            contents(10, 60, 580, """Left mouse button: Draw/erase lines.
    Middle mouse button: Zoom in and out of the track.
    Right mouse button: Pan around the track.
    In the Edit menu:
    Undo and redo: Undoes and redoes your last action.
    Toggle line snapping: Toggles the lines you draw to snap to the endpoints of \
    other lines.
    In the Tools menu:
    Pencil: For free-hand drawing
    Line: Draws straight lines
    Eraser: Removes lines from the track
    """)

        def line_types():
            title("Types of lines")
            contents(10, 60, 580, """Solid line: An ordinary line. However, unlike \
    the lines in the original Line Rider, the rider collides with BOTH SIDES of \
    the line.
    Acceleration line: A solid line that accelerates the rider in the direction of \
    the arrow.
    Scenery line: The rider does not collide with this line.
    Spring line: Not implemented yet.
    Trigger line: Not implemented yet.
    """)

        def playback():
            title("Playing tracks")
            contents(10, 60, 580, """Play: Starts the track.
    Stop: Stops the track. You can alternate between playing and stopping by \
    pressing just the space bar.
    Pause: Pauses the track. You can alternate between playing and pausing by \
    pressing just the "p" button.
    Step: Plays one frame of the track, for precise track making.
    Reset position: resets the position of the rider to the start point.
    Flag: Saves the current position and velocity of the rider. This causes "Play" \
    to start the track from this point, and "Reset position" to reset to this point.
    Reset flag: Removes the flag.
    Play from beginning: Plays the track from the beginning, ignoring the flag.
    Slow-mo: Toggles playing the track in slow motion.
    """)

        def view():
            title("View options")
            contents(10, 60, 580, """Velocity vector: Shows the vector describing \
    the rider's speed and direction of motion. Red is slow, blue is fast.
    Points: Shows the endpoints of the lines in the track. The radius of the \
    circle cooresponds with the radius of line snapping.
    Thin lines: Turns the width of lines to be as thin as possible, in case you \
    need precision.
    Status: Shows/hides the information on the top-left corner of the window.
    Starting point: Moves the camera to the starting point
    Last line: Moves the camera to the end of the last line drawn.
    Follow rider: Toggles whether the camera is following the rider in playback.
    Grid and collisions: Debugging stuff. Don't worry about it :|
    """)

        def saving():
            title("Saving and loading")
            contents(10, 60, 580, """New track: Erases the current track.
    Save track: Saves the current track with a given name to /savedLines.
    Load track: Lets you load a track from /savedLines.
    /SavedLines is a folder in the same place as where this .py file is.
    When you exit, the current track is automatically saved to a file called \
    "ONEXITSAVE_".
    When you open this program again, it automatically loads "ONEXITSAVE_".
    """)

        def tips1():
            title("Tips on making tracks")
            contents(10, 60, 580, """If you didn't already find out, the rider \
    will fall off his sled if you hit him hard enough. However, he'll also fall \
    off if a line forces him off the seat of his sled. Yes, he will fall off if a \
    line touches his butt. HE'S VERY SENSITIVE THERE :|
    If, for whatever reason, you want to drive \
    the rider into a sharp angle, that will cause this program to lag (not crash). \
    If you really want to do it, I advise you to add in a small perpendicular line \
    at the point of intersection.
    """)
            lines = [
                ((174.0, 275.0), (491.0, 317.0)), ((491.0, 317.0), (188.0, 369.0)),
                ((480.0, 300.0), (480.0, 340.0)), ((43.0, 324.0), (169.0, 328.0)),
                ((169.0, 328.0), (133.0, 311.0)), ((169.0, 328.0), (134.0, 351.0))]
            for line in lines:
                a, b = Vector(line[0]) + TL, Vector(line[1]) + TL
                self.canvas.create_line(a.x, a.y, b.x, b.y, width=3, cap=tk.ROUND)

        def tips2():
            title("Tips on making tracks")
            contents(10, 60, 580, """If you notice you're spending a lot of time \
    on a single track, it would be a good idea to make back up files just in case \
    something bad happens (eg this program somehow corrupts the save or you mess \
    up the track and can't fix it)
    On drawing smooth curves:
    Lazy way                  Lazy but effective          Pro (takes time)
    \n\n\n\n\n
    Don't forget to have fun! ~Conundrumer
    """)
            lines = [
                ((220.0, 238.0), (230.0, 292.0)), ((219.0, 260.0), (247.0, 312.0)),
                ((230.0, 292.0), (270.0, 331.0)), ((247.0, 312.0), (297.0, 343.0)),
                ((270.0, 331.0), (335.0, 352.0)), ((297.0, 343.0), (370.0, 354.0)),
                ((432.0, 239.0), (435.0, 260.0)), ((435.0, 260.0), (443.0, 283.0)),
                ((443.0, 283.0), (456.0, 304.0)), ((456.0, 304.0), (475.0, 324.0)),
                ((475.0, 324.0), (497.0, 337.0)), ((497.0, 337.0), (526.0, 346.0)),
                ((526.0, 346.0), (554.0, 350.0)), ((554.0, 350.0), (585.0, 351.0)),
                ((16.0, 230.0), (19.0, 346.0)), ((19.0, 346.0), (163.0, 347.0)),
                ((16.0, 230.0), (34.0, 346.0)), ((18.0, 260.0), (56.0, 347.0)),
                ((18.0, 278.0), (76.0, 346.0)), ((20.0, 297.0), (98.0, 346.0)),
                ((20.0, 314.0), (123.0, 348.0)), ((21.0, 329.0), (147.0, 346.0))]
            for line in lines:
                a, b = Vector(line[0]) + TL, Vector(line[1]) + TL
                self.canvas.create_line(a.x, a.y, b.x, b.y, width=1, cap=tk.ROUND)

        helpContents = [to_play, tools, line_types, playback, view, saving, tips1, tips2]
        i = self.help_index
        helpContents[i]()
        self.canvas.create_text(BR.x - 10, TL.y + 5, anchor=tk.NE,
                           font=("Arial", "15"), text=str(i + 1) + "/8")

    def do_about(self):
        messagebox.showinfo("About", """Line Rider Python v1.4
    Created by David Lu (Conundrumer)
    Something about fair use for education purposes here...
    Line Rider originally created by Bostjan Cadez (fsk)
    Collision detection adapted from:
    www.t3hprogrammer.com/research/line-circle-collision/tutorial
    Constraint algorithm adapted from:
    www.gpgstudy.com/gpgiki/GDC 2001%3A Advanced Character Physics
    Thanks to:
    Matthew (mhenr18)
    My brother
    Everyone else at www.weridethelines.com
    Line Rider Python will be discontinued after
    spring lines and trigger lines are implemented""")


"""SavePopup
This is the window to....save the track!"""
class SavePopup:
    def __init__(self, title, ini_trackname, clicksave_callback):
        self.window = tk.Toplevel()
        self.window.title(title)
        self.window.geometry('300x80')

        self.clicksave_callback = clicksave_callback
        self.trackname = ini_trackname

        self.trackname_input = tk.Entry(self.window)
        self.trackname_input.insert(0, self.trackname)
        self.save_btn = tk.Button(
            self.window,
            text="Save",
            command=lambda: self.clicksave_callback(self, self.trackname_input.get())
        )
        self.trackname_input.pack(fill=tk.X, expand=True, padx=10, pady=20)
        self.save_btn.pack()

    def ask_if_overwrite(self):
        self.trackname_input.delete(0, tk.END)
        self.trackname_input.insert(0, 'Overwrite track?')
        self.save_btn.config(
            text='Yes',
            command=self.clicksave_callback(self, self.trackname_input.get(), overwrite=True)
        )
        self.cancel_btn = tk.Button(self.window, text='No', command=self.revert_to_ini_screen)
        self.cancel_btn.pack()

    def revert_to_ini_screen(self, destroy_cancel_btn=True):
        self.trackname_input.delete(0, tk.END)
        self.trackname_input.insert(0, self.trackname)
        self.save_btn = tk.Button(
            self.window,
            text='Save',
            command=lambda: self.clicksave_callback(self, self.trackname_input.get())
        )
        if destroy_cancel_btn:
            self.cancel_btn.destroy()

    def success(self):
        self.trackname_input.insert(0, 'Saved!')
        self.window.after(1000, lambda: self.window.destroy())

    def fail(self):
        self.trackname_input.insert(0, 'Failed to save!')
        self.window.after(1000, lambda: self.revert_to_ini_screen(False))


"""LoadPopup
This is the window to....open a track!"""
class LoadPopup:
    def __init__(self, title, track_list, clickopen_callback):
        self.clickopen_callback = clickopen_callback
        self.window = tk.Toplevel()
        self.window.title(title)
        self.window.geometry('400x300')
        self.loadWindow = tk.Listbox(self.window)
        self.loadWindow.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.cancel_btn = tk.Button(self.window, text="Cancel", command=exit)
        self.open_btn = tk.Button(
            self.window,
            text="Open",
            command=lambda: self.clickopen_callback(self, self.loadWindow.get(tk.ACTIVE))
        )
        self.open_btn.pack()
        self.cancel_btn.pack()

        # Load existing tracks
        for track in track_list:
            self.loadWindow.insert(0, track)

    def fail(self, message):
        messagebox.showerror(title='Error loading', message=message)

    def success(self):
        self.window.destroy()