

class Grid:
    def __init__(self, app):
        self.app = app

    def reset_grid(self):
        for line in self.app.track.lines:
            self.add_to_grid(line)

    def add_to_grid(self, line):
        cells = self.get_grid_cells(line)
        if line.type == "scene":
            grid = self.app.grid.scenery
        else:
            grid = self.app.grid.solids
        for cell in cells:
            lines = grid.get(cell, set([]))
            lines |= {line}
            grid[cell] = lines

    def get_grid_cells(self, line):
        """returns a list of the cells the line exists in"""
        firstCell = self.grid_pos(line.r1)
        lastCell = self.grid_pos(line.r2)
        if firstCell[0] > lastCell[0]:  # going in negative x direction MAKES BUGS
            # JUST FLIP'EM
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
        topLeft = self.grid_pos(self.app.data.topLeft)
        bottomRight = self.grid_pos(self.app.data.bottomRight)
        x1, x2 = topLeft[0], bottomRight[0]
        y1, y2 = topLeft[1], bottomRight[1]
        g = self.app.data.gridSize
        cols = range(x1, x2 + g, g)
        rows = range(y1, y2 + g, g)
        cells = [(x, y) for x in cols for y in rows]
        return cells

    def grid_pos(self, pnt):
        return self.grid_floor(pnt.x), self.grid_floor(pnt.y)

    def grid_floor(self, x):
        return int(x - x % self.app.data.gridSize)

    def get_grid_ints(self, line, firstCell, lastCell):
        a, b, c = line.linear_equation()
        dx = dy = self.app.data.gridSize  # defined to be always positive
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
