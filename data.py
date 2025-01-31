

from dataclasses import dataclass

from geometry import Vector

@dataclass
class Data:
    delta: int = 10
    timeDelta = 10  #100 hz/fps
    grav = Vector(0, 30.0 / 1000 * delta)  #pixels per frame**2
    drag = 0.9999999 ** delta
    acc = 0.1 * delta  #acceleration line constant
    epsilon = 0.00000000001  #larger than floating point errors
    lineThickness = 0.001
    endurance = 0.4
    gridSize = 50
    iterations = 10
    maxiter = 100
    viewLines = True
    viewVector = False
    viewPoints = False
    viewGrid = False
    viewStatus = True
    viewCollisions = False
    viewThinLines = False
    slowmo = False
    follow = True
    mouseEnable = True
    center = Vector(400, 300)
    topLeft = Vector(0, 0)
    bottomRight = Vector(800, 600)
    windowSize = Vector(800, 600)
    message = ""

    def show_mdfy(self):
        if self.modified:
            self.message = "*"
        else:
            self.message = ""

