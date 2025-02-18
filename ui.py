
import os
import copy
import tkinter as tk
from tkinter import messagebox
import time

from geometry import Vector, Line, distance
from tools import Tool, Ink
from help_screen import HelpDisplayer

class UI:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="white")
        self.build_window()
        self.canvas.pack(fill="both", expand=True)

        self.canvas_size = Vector(800, 600)
        self.canvas_center = Vector(400, 300)
        self.canvas_topleft = Vector(0, 0)
        self.canvas_bottomright = Vector(800, 600)

        self.temp_message = ''
        self.help_popup = False
        self.help_index = 1
        self.helpscreen = HelpDisplayer(self.canvas)

        self.show_lines = True
        self.show_vector = False
        self.show_points = False
        self.show_grid = False
        self.show_status = True
        self.show_collisions = False
        # TODO: Show rider's trace

        self.thin_lines = False

        def resize(event):
            self.canvas_size = Vector(event.width, event.height)
            oldCenter = copy.copy(self.canvas_center)
            self.canvas_center = Vector(event.width / 2, event.height / 2)
            delta = self.canvas_center - oldCenter
            self.app.player.panPos -= delta

        self.canvas.bind("<Configure>", resize)

    def start_mainloop(self):
        self.root.mainloop()

    def build_window(self):
        self.root.title("Line Rider")

        def reset_temp_message():
            self.temp_message = ''

        def display_t(boolean, m1, m2):
            self.temp_message = m1 if boolean else m2
            self.canvas.after(1000, reset_temp_message)

        # TOP BAR MENU
        def snap():
            self.app.tm.snap_ruler = not self.app.tm.snap_ruler
            display_t(self.app.tm.snap_ruler, "Line snapping on", "Line snapping off")

        def view_vector():
            self.show_vector = not self.show_vector
            display_t(self.show_vector, "Showing velocity", "Hiding velocity")

        def view_points():
            self.show_points = not self.show_points
            display_t(self.show_points, "Showing snapping points", "Hiding snapping points")

        def view_lines():
            self.show_lines = not self.show_lines
            display_t(self.show_lines, "Showing lines", "Hiding lines")

        def view_grid():
            self.show_grid = not self.show_grid
            display_t(self.show_grid, "Showing grid", "Hiding grid")

        def view_status():
            self.show_status = not self.show_status
            display_t(self.show_status, "Showing status messages",
                      "Status messages are hidden, how can you see this?")

        def view_collisions():
            self.show_collisions = not self.show_collisions
            display_t(self.show_collisions, "Showing collision points", "Hiding collision points")

        def go_to_start():
            if self.app.player.is_paused:
                self.app.player.panPos = self.app.track.startPoint - self.canvas_center

        def last_line():
            if self.app.player.is_paused and len(self.app.track.lines) > 0:
                self.app.player.panPos = self.app.track.lines[-1].r2 - self.canvas_center

        def follow_rider():
            self.app.player.follow = not self.app.player.follow
            display_t(self.app.player.follow, "Following rider", "Not following rider")

        def view_thin_lines():
            self.thin_lines = not self.thin_lines
            display_t(self.thin_lines, "Viewing thin lines", "Viewing normal lines")

        def view_help():
            self.help_popup = not self.help_popup

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        fileMenu = tk.Menu(menubar, tearoff=False)
        fileMenu.add_command(label='New (ctrl+n)', command=self.app.new_track)
        fileMenu.add_command(label='Open (ctrl+o)', command=self.app.open_track)
        fileMenu.add_command(label='Save (ctrl+s)', command=self.app.save_track)
        menubar.add_cascade(label='File', menu=fileMenu)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Undo (ctrl+z)", command=self.app.undo_cmd)
        edit_menu.add_command(label="Redo (ctrl+shift+z)", command=self.app.undo_cmd)
        edit_menu.add_command(label="Toggle Line Snapping (s)", command=snap)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        tool_menu = tk.Menu(menubar)
        tool_menu.add_command(label="Pencil (q)", command=lambda: self.app.tm.take(Tool.Pencil, 'left'))
        tool_menu.add_command(label="Ruler (w)", command=lambda: self.app.tm.take(Tool.Ruler, 'left'))
        tool_menu.add_command(label="Eraser (e)", command=lambda: self.app.tm.take(Tool.Eraser, 'left'))
        tool_menu.add_separator()
        tool_menu.add_command(label="Solid (1)", command=lambda: self.app.tm.set_ink(Ink.Solid))
        tool_menu.add_command(label="Acceleration (2)", command=lambda: self.app.tm.set_ink(Ink.Acc))
        tool_menu.add_command(label="Scenery (3)", command=lambda: self.app.tm.set_ink(Ink.Scene))
        menubar.add_cascade(label="Tools", menu=tool_menu)

        viewMenu = tk.Menu(menubar)
        viewMenu.add_command(label="Velocity Vectors (v)", command=view_vector)
        viewMenu.add_command(label="Points (b)", command=view_points)
        viewMenu.add_command(label="Collisions (c)", command=view_collisions)
        viewMenu.add_command(label="Lines", command=view_lines)
        viewMenu.add_command(label="Thin Lines", command=view_thin_lines)
        viewMenu.add_command(label="Grid", command=view_grid)
        viewMenu.add_command(label="Status", command=view_status)
        viewMenu.add_separator()
        viewMenu.add_command(label="Starting Point (home)", command=go_to_start)
        viewMenu.add_command(label="Last Line (end)", command=last_line)
        viewMenu.add_command(label="Follow Rider", command=follow_rider)
        menubar.add_cascade(label="View", menu=viewMenu)

        playMenu = tk.Menu(menubar)
        playMenu.add_command(label="Play/Pause (space/p)", command=self.app.player.play_pause)
        playMenu.add_command(label="Stop (space)", command=self.app.player.stop)
        playMenu.add_command(label="Step (t)", command=self.app.world.step_forward)
        playMenu.add_command(label="Reset Position (r)", command=self.app.reset_rider)
        playMenu.add_command(label="Flag (f)", command=self.app.player.set_flag)
        playMenu.add_command(label="Reset Flag (ctrl+f)", command=self.app.player.reset_flag)
        playMenu.add_command(label="Play from Beginning (ctrl+p)", command=self.app.player.play_from_beginning)
        playMenu.add_command(label="Slow-mo (m)", command=self.app.player.toggle_slowmo)
        menubar.add_cascade(label="Playback", menu=playMenu)

        helpMenu = tk.Menu(menubar)
        helpMenu.add_command(label="Help", command=view_help)
        helpMenu.add_command(label="About", command=self.do_about)
        menubar.add_cascade(label="Help", menu=helpMenu)

        # Keyboard and mouse interactions
        def key_pressed(event):
            k = event.keysym
            c = event.char

            if c == "t":
                if self.app.player.is_paused:
                    self.app.world.step_forward()
            elif c == "p":
                self.app.player.play_pause()
            elif c == " ":
                if self.app.player.is_paused:
                    self.app.player.play_pause()
                else:
                    self.app.player.stop()
            elif c == "q":
                self.app.tm.take(Tool.Pencil)
            elif c == "w":
                self.app.tm.take(Tool.Ruler)
            elif c == "e":
                self.app.tm.take(Tool.Eraser)
            elif c == "m":
                self.app.player.toggle_slowmo()
            elif c == "r":
                self.app.reset_rider()
            elif c == "f":
                self.app.player.set_flag()
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
                if k == "Left" and i > 1:
                    self.help_index -= 1
                if k == "Right" and i < 8:
                    self.help_index += 1
            self.redraw_all()

        self.root.bind("<Button-1>", lambda e: self.app.tm.use('left', e))
        self.root.bind("<B1-Motion>", lambda e: self.app.tm.use('left', e))
        self.root.bind("<ButtonRelease-1>", lambda e: self.app.tm.use('left', e))
        self.root.bind("<Button-3>", lambda e: self.app.tm.use('right', e))
        self.root.bind("<B3-Motion>", lambda e: self.app.tm.use('right', e))
        self.root.bind("<ButtonRelease-3>", lambda e: self.app.tm.use('right', e))
        self.root.bind("<Button-2>", lambda e: self.app.tm.use('scroll-click', e))
        self.root.bind("<B2-Motion>", lambda e: self.app.tm.use('scroll-click', e))
        self.root.bind("<MouseWheel>", lambda e: self.app.tm.use('scroll', e))
        self.root.bind('<KeyPress>', key_pressed)  # <KeyRelease> exists as well - just in case
        self.root.bind('<Home>', lambda _: go_to_start())
        self.root.bind('<End>', lambda _: last_line())
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.on_exit())
        self.root.bind('<Escape>', lambda _: self.root.destroy())

        prefix = '<Command-' if os.name == 'mac' else '<Control-'
        self.root.bind(prefix+'z>', lambda _: self.app.undo_cmd())
        self.root.bind(prefix+'Shift-Z>', lambda _: self.app.redo_cmd())
        self.root.bind(prefix+'s>', lambda _: self.app.save_track(popup=False))
        self.root.bind(prefix+'Shift-s>', lambda _: self.app.save_track(popup=True))
        self.root.bind(prefix+'p>', lambda _: self.app.play_from_beginning())
        self.root.bind(prefix+'o>', lambda _: self.app.open_track())
        self.root.bind(prefix+'n>', lambda _: self.app.new_track())
        self.root.bind(prefix+'f>', lambda _: self.app.player.reset_flag())

    def redraw_all(self):
        self.canvas.delete(tk.ALL)

        def draw_lines(line_list):
            for (pt1, pt2) in line_list:
                pt1, pt2 = self.app.player.adjust_pz(pt1), self.app.player.adjust_pz(pt2)
                self.canvas.create_line(pt1.x, pt1.y, pt2.x, pt2.y)

        def draw_rectangles(rect_list, fill_colour='black'):
            for rect in rect_list:
                if len(rect) == 3:
                    (cell, cell2, color) = rect
                else:
                    (cell, cell2, color) = *rect, fill_colour
                cell, cell2 = self.app.player.adjust_pz(cell), self.app.player.adjust_pz(cell2)
                self.canvas.create_rectangle(cell.x, cell.y, cell2.x, cell2.y, fill=color)

        track_drawing_data = self.app.track.get_drawing_data(
            grid=self.show_grid,
            # lines=self.show_lines,
            # points=self.show_points
        )

        if self.show_grid:
            draw_lines(track_drawing_data['grid_vlines'])
            draw_lines(track_drawing_data['grid_hlines'])
            draw_rectangles(track_drawing_data['grid_cells_with_lines'], fill_colour='yellow')
            draw_rectangles(track_drawing_data['grid_cells_with_rider'])

        if self.show_lines:
            self.draw_lines()
        if self.show_points:
            self.draw_points()

        if self.app.player.flag:
            self.draw_flag()
        self.draw_rider()
        if self.show_vector:
            self.draw_vectors()
        if self.show_collisions:
            self.draw_collisions()
        if self.show_status:
            self.status_display()
        if self.help_popup:
            self.helpscreen.show(self.help_index, self.canvas_center)

    def draw_lines(self):
        width = 1 if self.thin_lines else 3 * self.app.player.zoom

        for line in self.app.track.grid.lines_in_screen():
            a, b = self.app.player.adjust_pz(line.r1), self.app.player.adjust_pz(line.r2)
            color = "black"
            arrow = None
            if line.ink == Ink.Scene and self.app.player.is_paused:
                color = "green"
            elif line.ink == Ink.Acc and self.app.player.is_paused:
                color = "red"
                arrow = tk.LAST
            self.canvas.create_line(a.x, a.y, b.x, b.y, width=width,
                               caps=tk.ROUND, fill=color, arrow=arrow)

        if self.app.rider.onSled:  # Display sled string
            for line in self.app.rider.sledString:
                a, b = self.app.player.adjust_pz(line[0].r), self.app.player.adjust_pz(line[1].r)
                self.canvas.create_line(a.x, a.y, b.x, b.y)

        if self.app.tm.tempLine is not None and self.app.player.is_paused:
            line = self.app.tm.tempLine
            a, b = self.app.player.adjust_pz(line.r1), self.app.player.adjust_pz(line.r2)
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
            pnt = self.app.player.adjust_pz(line.r1)
            x, y = pnt.x, pnt.y
            self.canvas.create_oval((x - r, y - r), (x + r, y + r), outline="blue", width=3)
            pnt = self.app.player.adjust_pz(line.r2)
            x, y = pnt.x, pnt.y
            self.canvas.create_oval((x - r, y - r), (x + r, y + r), outline="blue", width=3)

    def draw_flag(self):
        parts = self.app.player.flagged_rider.flag_drawing_vectors
        bosh = self.app.player.flagged_rider.boshParts
        for i in range(len(parts)):
            part = parts[i]  # part contains tuples of line segments and stuff
            point0, point1 = bosh[i]  # each value has two Point objects
            angle = (point1.r - point0.r).get_angle()
            for shape in part:  # segment: tuple of line properties for rendering
                shape.render(point0.r, angle, self.app)

    def draw_scarf(self, c):
        color = c
        w = 4 * self.app.player.zoom
        for line in self.app.rider.scarfCnstr:
            color = "white" if color == c else c
            pnt1, pnt2 = self.app.player.adjust_pz(line.pnt1.r), self.app.player.adjust_pz(line.pnt2.r)
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
        a, b = self.app.player.adjust_pz(pnt.r), self.app.player.adjust_pz(pnt.r + vel)
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
            pnt = self.app.player.adjust_pz(point.r)
            self.canvas.create_oval(pnt.x + 2, pnt.y + 2, pnt.x - 2, pnt.y - 2, fill="red")
        for pnt in self.app.world.collisionPoints:
            pnt = self.app.player.adjust_pz(pnt)
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
        speed = f'{self.app.rider.speed:.1f} pixels/frame' if not self.app.player.is_paused else ''

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
        if self.app.player.is_paused:
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
        elif type == 'showinfo':
            return messagebox.showinfo(title, content)

    def do_about(self):
        self.open_popup(
            type='showinfo',
            title='About',
            content='''Line Rider Python v1.4
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
spring lines and trigger lines are implemented'''
        )


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