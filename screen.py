import os, sys, tron, MyTronBot
from Tkinter import *

colors = { "#": "gray",
           "1": "red",
           "2": "blue",
           " ": "white" }

heat_colors = ((255, 255, 255), (255, 255, 0), (255, 128, 0), (255, 0, 0))

class EndOfGame():
    def __init__(self, result):
        self.result = result

def rgb((r, g, b)):
    return "#%02x%02x%02x" % (r, g, b)

def gradient2(c1, c2, n):
    r1,g1,b1 = c1
    r2,g2,b2 = c2
    rd,gd,bd = float(r2-r1), float(g2-g1), float(b2-b1)
    ra,ga,ba = rd/n, gd/n, bd/n
    r, g, b = r1, g1, b1
    colors = []
    for i in range(n):
        colors.append(rgb((int(r), int(g), int(b))))
        r, g, b = r + ra, g + ga, b + ba
    return colors

def gradient(base, total):
    spreads = len(base) - 1
    colors = ['#000000' for i in range(total)]
    perset = total / spreads
    extra = total % spreads
    sets = [perset for i in range(spreads)]
    for i in range(extra):
        sets[i] += 1
    j = 0
    for i in range(spreads):
        for c in gradient2(base[i], base[i+1], sets[i]):
            colors[j] = c
            j += 1
    colors[0] = rgb(base[0])
    colors[len(colors)-1] = rgb(base[len(base)-1])
    return colors

class Grid():

    def make_cell(self, x, y, z, color):
        return self.canvas.create_rectangle(x,y,x+z,y+z,fill=color)
    
    def __init__(self, parent, height, width, cellsize, color):
        h, w, z = height, width, cellsize
        self.height = height
        self.width = width
        self.cellsize = cellsize
        self.canvas = Canvas(parent, width=w*z, height=h*z)
        self.cells = {}
        for y in range(h):
            for x in range(w):
                self.cells[y,x] = self.make_cell(x*z, y*z, z, color)

    def __setitem__(self, yx, color):
        self.canvas.itemconfigure(self.cells[yx], fill=color)

    def pack(self):
        self.canvas.pack()

class TronGrid(Grid):

    def __init__(self, parent, board, cellsize=15, colors=colors):
        Grid.__init__(self, parent, board.height, board.width, \
                          cellsize, colors[' '])
        self.colors = colors
        self.me = board.me()
        self.them = board.them()
        self.centers = {}
        self.draw(board)
        self.last_me_line = None
        self.last_them_line = None

    def draw(self, board):
        z = self.cellsize
        for y in range(board.height):
            for x in range(board.width):
                self[y,x] = self.colors[board[y,x]]
                self.centers[y,x] = y * z + (z / 2), x * z + z / 2

    def draw_line(self, a, b, arrow='none', fill='black'):
        y1,x1 = self.centers[a]
        y2,x2 = self.centers[b]
        return self.canvas.create_line(x1, y1, x2, y2, arrow=arrow, fill=fill)

    def draw_lines(self, board, path, fill='black'):
        for i in xrange(len(path)-2):
            self.draw_line(path[i], path[i+1], 'none', fill)
        self.draw_line(path[-2], path[-1], 'last', fill)
    
    def update(self, board):
        if self.last_me_line:
            self.canvas.itemconfigure(self.last_me_line, arrow='none')
        me = board.me()
        self.last_me_line = self.draw_line(self.me, me, 'last', 'white')
        self[board.me()] = self.colors[tron.ME]
        if self.last_them_line:
            self.canvas.itemconfigure(self.last_them_line, arrow='none')
        them = board.them()
        self.last_them_line = self.draw_line(self.them, them, 'last', 'white')
        self[board.them()] = self.colors[tron.THEM]
        self.me = me
        self.them = them

def show_board(board, squaresize=15):
    root = Tk()
    root.bind("<Escape>", lambda e: root.destroy())
    grid = TronGrid(root, board, squaresize, colors)
    grid.draw(board)
    grid.pack()
    mainloop()

def show_path(board, path, fill='yellow', line_color='black'):
    root = Tk()
    root.bind("<Escape>", lambda e: root.destroy())
    grid = TronGrid(root, board, 15, colors)
    grid.draw(board)
    for p in path:
        if board[p] == tron.FLOOR:
            grid[p] = fill
    if line_color:
        grid.draw_lines(board, path)
    grid.pack()
    mainloop()

def show_heat(board, heat):
    max_heat = max(heat.values())
    grad = gradient(heat_colors, max_heat + 1)
    root = Tk()
    root.bind("<Escape>", lambda e: root.destroy())
    grid = TronGrid(root, board, 15, colors)
    grid.draw(board)
    for p in heat.keys():
        if board[p] == tron.FLOOR:
            grid[p] = grad[heat[p]]
    grid.pack()
    mainloop()
    
def read_board(stream=sys.stdin):
    line1 = stream.readline().strip()
    try:
        height, width = [int(s) for s in line1.split(' ')]
        lines = [stream.readline() for i in range(height)]
        return tron.Board(width, height, lines)
    except ValueError:
        raise EndOfGame(line1)
