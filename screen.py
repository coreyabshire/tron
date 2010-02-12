import os, sys
from Tkinter import *

delay_ms = len(sys.argv) > 1 and int(float(sys.argv[1]) * 1000) or 100
squaresize = len(sys.argv) > 2 and int(sys.argv[2]) or 15

root = Tk()

root.bind("<Escape>", lambda e: quit())

dims = sys.stdin.readline().split(" ")
gridwidth = int(dims[0])
gridheight = int(dims[1])
lines = [sys.stdin.readline() for i in range(gridheight)]

colors = { "#": "gray", "1": "red", "2": "blue", " ": "white" }

w = Canvas(root, width=squaresize*gridwidth, height=squaresize*gridheight)
w.pack()

grid = []

def draw(lines):
    for y in range(gridheight):
        line = []
        for x in range(gridwidth):
            x1 = x * squaresize
            x2 = x1 + squaresize
            y1 = y * squaresize
            y2 = y1 + squaresize
            r = w.create_rectangle(x1, y1, x2, y2, fill=colors[lines[y][x]])
            line.append(r)
            grid.append(line)

def update():
    line1 = sys.stdin.readline().strip()
    if line1 == "%d %d" % (gridwidth,gridheight):
        lines = [sys.stdin.readline() for i in range(gridheight)]
        draw(lines)
        root.after(delay_ms, update)
    else:
        print line1

draw(lines)
root.after(delay_ms, update)
mainloop()
