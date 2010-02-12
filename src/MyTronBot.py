#!/usr/bin/python

"""Template for your tron bot"""

import tron

import random

def which_move(board):

    # fill in your code here. it must return one of the following directions:
    #   tron.NORTH, tron.EAST, tron.SOUTH, tron.WEST

    # For now, choose a legal move randomly.
    # Note that board.moves will produce [NORTH] if there are no
    # legal moves available.
    return random.choice(board.moves())

# you do not need to modify this part
for board in tron.Board.generate():
    tron.move(which_move(board))
