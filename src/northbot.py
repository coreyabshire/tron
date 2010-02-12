#!/usr/bin/python

"""Template for your tron bot"""

import tron

import random

def which_move(board):
    return tron.NORTH

# you do not need to modify this part
for board in tron.Board.generate():
    tron.move(which_move(board))
