#!/usr/bin/python

"""Template for your tron bot"""

import tron

import random

def read_board(filename):
    "Read a board from a map file."
    f = open(filename)
    width,height = [int(s) for s in f.readline().strip().split()]
    board = [s[:width] for s in f.readlines()]
    f.close()
    return tron.Board(width, height, board)

def adjacent_floor(board, origin):
    "Return the positions around origin that are floor spaces (open)."
    return [c for c in board.adjacent(origin) if board[c] == tron.FLOOR]

def which_move(board):

    # fill in your code here. it must return one of the following directions:
    #   tron.NORTH, tron.EAST, tron.SOUTH, tron.WEST

    # For now, choose a legal move randomly.
    # Note that board.moves will produce [NORTH] if there are no
    # legal moves available.
    return random.choice(board.moves())

# you do not need to modify this part
if __name__ == "__main__":
    for board in tron.Board.generate():
        tron.move(which_move(board))
