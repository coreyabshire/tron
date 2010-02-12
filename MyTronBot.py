#!/usr/bin/python

"""Template for your tron bot"""

import tron

import random

infinity = 1.0e400

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

def terminal_test(board):
    "Determine whether this board is at an end game state."
    return not adjacent_floor(board, board.me()) \
        or not adjacent_floor(board, board.them())

def utility(board, player):
    "Did player on board is a win (1), lose (-1), or draw (0)."
    me_stuck = not adjacent_floor(board, board.me())
    them_stuck = not adjacent_floor(board, board.them())
    if me_stuck and them_stuck:
        return 0
    elif me_stuck or them_stuck:
        if player == tron.ME:
            return me_stuck and -1 or 1
        else:
            return me_stuck and 1 or -1
    else:
        return 0

def set_char(s, i, c):
    "Set character at index i in string s to c."
    return s[:i] + c + s[i+1:]
    
def try_move(board, player, move):
    "Create a copy of board where player is moved in direction."
    lines = [line for line in board.board] # shallow copy
    (y1,x1) = board.find(player)
    (y2,x2) = board.rel(move, (y1,x1))
    lines[y1] = set_char(lines[y1], x1, tron.WALL)
    lines[y2] = set_char(lines[y2], x2, player)
    return tron.Board(board.width, board.height, lines)

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
