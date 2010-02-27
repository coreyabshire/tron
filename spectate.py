# spectate: Allows you to watch a Tron match in Tkinter.
# Copyright (C) 2010 Corey Abshire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
