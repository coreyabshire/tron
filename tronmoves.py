# tronmoves: Moves library for a Google AI 2010 TronBot entry.
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

import time, logging, games, utils, tron
from tronutils import *
from aimatron import *


#_____________________________________________________________________
# Basic Moves (from starter package)
#


def random_move(board):
    "Just return any random legal move."
    return random.choice(board.moves())


def most_free_move(board):
    "Find the move that has the most immediate floor tiles."
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


def follow_wall_move(board, order):
    "Find a move that follows the wall, favoring the order given."
    decision = board.moves()[0]
    for dir in order:
        dest = board.rel(dir)
        if not board.passable(dest):
            continue
        adj = board.adjacent(dest)
        if any(board[pos] == tron.WALL for pos in adj):
            decision = dir
            break
    return decision


#_____________________________________________________________________
# Core Moves (called directly from my main bot)
#


def surrender_move(board):
    "Return a constant move in order to surrender."
    return tron.NORTH


def most_open_move(board, order):
    "Find the move that has the most open floor filled around it."
    p1, p2, t, touching = dfs_count_around(board)
    wall_move = follow_wall_move(board, order)
    open_move = utils.argmax(p1.keys(), lambda k: p1[k])
    if p1[wall_move] == p1[open_move]:
        best_move = wall_move
    else:
        best_move = open_move
    logging.debug("most open move is: %s (%d) %s", best_move, p1[best_move], p1)
    return best_move


def minimax_move(board, finish_by=None):
    "Find a move based on an alpha-beta search of the game tree."
    game = TronGame()
    return alphabeta_search(board, game, finish_by)


def follow_path_move(board, path):
    "Follow the given path."
    return move_made(board.me(), path[1])


def same_dist_move(board, same_dist, order):
    "Try to draw a line through the same distance tiles."
    first_point = same_dist[0]
    last_point = same_dist[-1]
    if board.passable(first_point):
        path = shortest_path(board, board.me(), first_point)
        return move_made(board.me(), path[1])
    elif board.passable(last_point):
        path = shortest_path(board, board.me(), last_point)
        return move_made(board.me(), path[1])
    else:
        return most_open_move(board, order)


#_____________________________________________________________________
# Experimental Moves (tried, but not in use)
#


def chunky_minimax_move(board, chunk_size, finish_by=None):
    "Find a move based on an alpha-beta search of the game tree."
    game = TronChunkyGame(chunk_size)
    return alphabeta_search(board, game, finish_by)


def hotspot_move(board):
    "Find the move that targets the next hot spot."
    try:
        me = board.me()
        heat = heat_map(board)
        hotspots = heat.keys()
        hotspots.sort(key=lambda k: heat[k], reverse=True)
        target = hotspots[0]
        path = shortest_path(board, me, target)
        next_step = path[1]
        move = move_made(me, next_step)
        return move
    except KeyError:
        return minimax_move(state)


