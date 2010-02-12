#!/usr/bin/python

import tron

def which_move(board):
    bestcount = -1
    bestmove = tron.NORTH
    for dir in board.moves():
        dest = board.rel(dir)
        count = 0
        for pos in board.adjacent(dest):
            if board[pos] == tron.FLOOR:
                count += 1
        if count > bestcount:
            bestcount = count
            bestmove = dir
    return bestmove

# make a move each turn
for board in tron.Board.generate():
    tron.move(which_move(board))

