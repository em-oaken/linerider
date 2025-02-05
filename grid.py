

from tool_helpers import Ink
from geometry import Line

class Grid:
    def __init__(self, track):
        self.track = track
        self.spacing = 50
        self.solids = dict()
        self.scenery = dict()

    def reset_grid(self):
        for line in self.track.lines:
            self.add_to_grid(line)

    def add_to_grid(self, line):
        cells = self.get_grid_cells(line)
        if line.ink == Ink.Scene:
            grid = self.scenery
        else:
            grid = self.solids
        for cell in cells:
            lines = grid.get(cell, set())
            lines |= {line}
            grid[cell] = lines

    def get_grid_cells(self, line):
        """returns a list of the cells the line exists in"""
        firstCell = self.grid_pos(line.r1)
        lastCell = self.grid_pos(line.r2)
        if firstCell[0] > lastCell[0]:  # going in negative x direction MAKES BUGS
            firstCell, lastCell = lastCell, firstCell
        cells = [firstCell]
        gridInts = self.get_grid_ints(line, firstCell, lastCell)
        cell = firstCell
        for x in sorted(gridInts):  # ordered by which cell the line enters
            dcor = gridInts[x]
            cell = cell[0] + dcor[0], cell[1] + dcor[1]
            cells += [cell]
        #   if lastCell not in cells:
        #       cells += [lastCell]
        return cells

    def grid_in_screen(self):
        """returns a list of visible cells"""
        # absolute positions
        topLeft = self.grid_pos(self.track.app.data.topLeft)
        bottomRight = self.grid_pos(self.track.app.data.bottomRight)
        x1, x2 = topLeft[0], bottomRight[0]
        y1, y2 = topLeft[1], bottomRight[1]
        g = self.spacing
        cols = range(x1, x2 + g, g)
        rows = range(y1, y2 + g, g)
        cells = [(x, y) for x in cols for y in rows]
        return cells

    def remove_from_grid(self, line):
        """removes the line in the cells the line exists in"""
        removedCells = self.get_grid_cells(line)  # list of cell positions
        if line.ink == Ink.Scene:
            grid = self.scenery
        else:
            grid = self.solids
        for gPos in removedCells:
            cell = grid[gPos]
            # SET OF LINES, REMEMBER?
            cell.remove(line)
            if len(cell) == 0:  # get rid of the cell entirely if no lines
                grid.pop(gPos)

    def grid_neighbors(self, pos):
        """returns a list of the positions of the cells at and around the pos"""
        cells = {}
        x, y = self.grid_pos(pos)
        g = self.spacing
        return [(x, y), (x + g, y), (x + g, y + g), (x, y + g), (x - g, y + g),
                (x - g, y), (x - g, y - g), (x, y - g), (x + g, y - g)]

    def grid_pos(self, pnt):
        return self.grid_floor(pnt.x), self.grid_floor(pnt.y)

    def grid_floor(self, x):
        return int(x - x % self.spacing)

    def get_grid_ints(self, line, firstCell, lastCell):
        a, b, c = line.linear_equation()
        dx = dy = self.spacing  # defined to be always positive
        if lastCell[1] < firstCell[1]:  # y is decreasing
            dy *= -1
        gridInts = {}
        xInc, yInc = (dx, 0), (0, dy)
        # normally, I would just use x = (c-b*y)/a
        if b == 0:  # a might be 0 so SWAP VALUES
            b, a = a, b
            yInc, xInc = xInc, yInc
            dy, dx = dx, dy
            firstCell = firstCell[1], firstCell[0]
            lastCell = lastCell[1], lastCell[0]
        # vertical line intersections, exclude 0th line
        for x in range(firstCell[0], lastCell[0], dx):
            x += dx
            gridInts[x] = xInc
        # horizontal line intersections, exclude 0th line
        for y in range(firstCell[1], lastCell[1], dy):
            if dy > 0:
                y += dy
            x = (c - b * y) / a
            gridInts[x] = yInc
        return gridInts

    def get_solid_lines(self, pnt):
        """returns a set of lines that exist in the same cells as the point"""
        vLine = Line(pnt.r0, pnt.r)
        lines = set()
        for gPos in self.get_grid_cells(vLine):  # list of cell positions
            cell = self.solids.get(gPos, set())
            lines |= cell  # add to set of lines to check collisions
        return lines
