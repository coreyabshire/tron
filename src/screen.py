from Tkinter import *

master = Tk()

squaresize = 10
gridheight = 15
gridwidth = 15

w = Canvas(master, width=squaresize*gridwidth, height=squaresize*gridheight)
w.pack()

grid = []

for y in range(gridheight):
    line = []
    for x in range(gridwidth):
        x1 = x * squaresize
        x2 = x1 + squaresize
        y1 = y * squaresize
        y2 = y1 + squaresize
        r = w.create_rectangle(x1, y1, x2, y2, fill='white')
        line.append(r)
    grid.append(line)

w.itemconfigure(grid[5][5], fill = 'red')
w.itemconfigure(grid[10][10], fill = 'blue')
for y in range(gridheight):
    w.itemconfigure(grid[y][0], fill='gray')
    w.itemconfigure(grid[y][gridwidth-1], fill='gray')
for x in range(gridwidth):
    w.itemconfigure(grid[0][x], fill='gray')
    w.itemconfigure(grid[gridheight-1][x], fill='gray')
mainloop()
