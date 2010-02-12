#!/usr/bin/python

"""Follows the wall"""

import random, tron

# preference order of directions
ORDER = list(tron.DIRECTIONS)
random.shuffle(ORDER)

def which_move(board):

    decision = board.moves()[0]

    for dir in ORDER:

        # where we will end up if we move this way
        dest = board.rel(dir)

        # destination is passable?
        if not board.passable(dest):
            continue

        # positions adjacent to the destination
        adj = board.adjacent(dest)

        # if any wall adjacent to the destination
        if any(board[pos] == tron.WALL for pos in adj):
            decision = dir
            break

    return decision

# make a move each turn
for board in tron.Board.generate():
    tron.move(which_move(board))

