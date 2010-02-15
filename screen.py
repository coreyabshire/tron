import os, sys, tron
from Tkinter import *

class EndOfGame():
    def __init__(self, result):
        self.result = result

class Grid():

    def make_cell(self, x, y, z, color):
        return self.canvas.create_rectangle(x,y,x+z,y+z,fill=color)
    
    def __init__(self, parent, height, width, cellsize, color):
        h, w, z = height, width, cellsize
        self.height = height
        self.width = width
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

    def __init__(self, parent, board, cellsize, colors):
        Grid.__init__(self, parent, board.height, board.width, \
                          cellsize, colors[' '])
        self.colors = colors
        self.draw(board)
        
    def draw(self, board):
        for y in range(board.height):
            for x in range(board.width):
                self[y,x] = self.colors[board[y,x]]

    def update(self, board):
        self[board.me()] = self.colors[tron.ME]
        self[board.them()] = self.colors[tron.THEM]

def read_board(stream=sys.stdin):
    line1 = stream.readline().strip()
    try:
        height, width = [int(s) for s in line1.split(' ')]
        lines = [stream.readline() for i in range(height)]
        return tron.Board(width, height, lines)
    except ValueError:
        raise EndOfGame(line1)
    
def update():
    try:
        grid.update(read_board())
        root.after(delay_ms, update)
    except EndOfGame as end:
        print end.result
    
delay_ms = len(sys.argv) > 1 and int(float(sys.argv[1]) * 1000) or 100
squaresize = len(sys.argv) > 2 and int(sys.argv[2]) or 15

root = Tk()
root.bind("<Escape>", lambda e: quit())
board = read_board()
colors = { "#": "gray", "1": "red", "2": "blue", " ": "white" }
grid = TronGrid(root, board, squaresize, colors)
grid.draw(board)
grid.pack()
root.after(delay_ms, update)
mainloop()
