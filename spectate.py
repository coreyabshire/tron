import os, sys, tron, MyTronBot, screen
from Tkinter import *

delay_ms = len(sys.argv) > 1 and int(float(sys.argv[1]) * 1000) or 100
squaresize = len(sys.argv) > 2 and int(sys.argv[2]) or 15

root = Tk()
root.bind("<Escape>", lambda e: quit())

board = screen.read_board()
grid = screen.TronGrid(root, board, squaresize, screen.colors)
grid.draw(board)
grid.pack()

def update():
    try:
        grid.update(screen.read_board())
        root.after(delay_ms, update)
    except screen.EndOfGame as end:
        print end.result


root.after(delay_ms, update)
mainloop()
