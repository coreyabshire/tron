#!/usr/bin/python

"""Moves in a random direction"""

import random, tron

def which_move(board):
    return random.choice(board.moves())

# make a move each turn
for board in tron.Board.generate():
    tron.move(which_move(board))
