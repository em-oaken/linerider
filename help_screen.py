
import tkinter as tk
import tomllib
from dataclasses import dataclass
from geometry import Vector


@dataclass
class HelpPage:
    title: str
    content: str
    lines: str
    lines_width: int

class HelpDisplayer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.pages = {}
        self.load_content()

    def show(self, page_index, canvas_center):
        page = self.pages[page_index]
        padx, pady, width = 10, 60, 580
        topleft = canvas_center - Vector(300, 200)
        bottomright = canvas_center + Vector(300, 200)

        self.canvas.create_rectangle(topleft.x, topleft.y, bottomright.x, bottomright.y, width=5, fill="#eee")
        self.canvas.create_text(
            topleft.x + 10, topleft.y + 5,anchor=tk.NW, width=580,
            font=("Arial", "25", "bold"), text=page.title
        )
        self.canvas.create_text(
            topleft.x + padx, topleft.y + pady, anchor=tk.NW, width=width,
            font=("Arial", "15"), text=page.content
        )
        for line in page.lines:
            a, b = topleft + Vector(*line[0]), topleft + Vector(*line[1])
            self.canvas.create_line(a.x, a.y, b.x, b.y, width=page.lines_width, cap=tk.ROUND)
        self.canvas.create_text(
            bottomright.x - 10, bottomright.y + 5, anchor=tk.NE,
            font=("Arial", "15"), text=str(page_index) + "/8"
        )

    def load_content(self):
        with open('help_pages.toml', 'rb') as f:
            help_content = tomllib.load(f)
        for key, val in help_content.items():
            self.pages[int(key)] = HelpPage(**val)
