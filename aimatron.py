# aimatron: Interfaces the AIMA games framework to Tron (for minimax).
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

import logging, time
import games, utils
import tron
from tronutils import *

class TimeAlmostUp():
    "Exception class that represents when move submission is due."
    pass

class TronState():
    "Represents a single game state for minimax search."

    # This state is slightly different than normal to represent
    # the fact that Tron players make their moves simultaneously.
    # Normally, minimax expects the players to take turns.

    # This class implements simultenous moves by simply caching the
    # first move and not updating the board when its made. Then,
    # when the second move is made, it applies both moves.

    def __init__(self, board, to_move, move1=None):

        # The basic state information.
        self.board = board
        self.to_move = to_move
        self.move1 = move1

        # Caches to speed things up.
        self.score_cache = None
        self.move_cache = {}

class TronGame(games.Game):
    "A representation of Tron compatible with AIMA alpha-beta."

    def legal_moves(self, state):
        "Find all the moves possible from the current state."
        a = state.board.find(state.to_move)
        return [move_made(a, b) for b in adjacent(state.board, a, is_floor)]

    def make_move(self, move, state):
        "Return the new state resulting from making the given move."

        # We gain some efficiency here by treating the states as a
        # tree and caching the children for the next time we build it.
        # If this move has already been applied for this state in this
        # particular tree, return that instead of recomputing.
        if move in state.move_cache:
            return state.move_cache[move]
        
        next_to_move = opponent(state.to_move)

        if state.move1:
            # The first move has already been made, so apply both
            # moves to the board to create the next state.
            next_board = apply_move(state.board, next_to_move, state.move1)
            next_board = apply_move(next_board, state.to_move, move)
            next_state = TronState(next_board, next_to_move)
            
        else:
            # This is the first move for this turn. Do not update
            # the board. Just cache this move and wait for the next one.
            # Since the board is not updated, the position should
            # still evaluate to the same score.
            next_state = TronState(state.board, next_to_move, move)
            next_state.score_cache = state.score_cache

        # Cache this work so we don't have to repeat it during
        # the iterative deepening search.
        state.move_cache[move] = next_state
        
        return next_state

    def utility(self, state, player):
        "Determine the utility of the given terminal state for player."
        return win_lose_or_draw(state.board, tron.ME)

    def terminal_test(self, state):
        "Determine whether the current state is a leaf state."
        return is_game_over(state.board)

    def move_to_return(self, move):
        "Translate this move into what should be returned to the bot."
        # Useless for this one, but required for the chunky bot.
        return move

class TronChunkyGame(TronGame):
    "A representation of Tron compatible with AIMA alpha-beta."

    def __init__(self, n):
        self.patterns = [
            (tron.NORTH, tron.EAST, tron.WEST, tron.SOUTH),
            (tron.NORTH, tron.WEST, tron.EAST, tron.SOUTH),
            (tron.SOUTH, tron.WEST, tron.EAST, tron.NORTH),
            (tron.SOUTH, tron.EAST, tron.WEST, tron.NORTH),
            (tron.EAST, tron.NORTH, tron.SOUTH, tron.WEST),
            (tron.EAST, tron.SOUTH, tron.NORTH, tron.WEST),
            (tron.WEST, tron.SOUTH, tron.NORTH, tron.EAST),
            (tron.WEST, tron.NORTH, tron.SOUTH, tron.EAST)]
        self.n = n

    def legal_moves(self, state):
        "Find all the moves possible from the current state."
        moves = []
        for pattern in self.patterns:
            coords = board.find(state.to_move)
            move_fn = lambda board: follow_wall_move(board, pattern)
            path = apply_move_fn(state.board, move_fn, max_len=self.n)
            if path and path not in moves:
                moves.add(path)
        return moves

    def make_move(self, move, state):
        "Return the new state resulting from making the given move."
        if move in state.move_cache:
            logging.debug('cache hit on child')
            return state.move_cache[move]
        next_to_move = opponent(state.to_move)
        if state.move1:
            board = state.board
            for i in range(self.n):
                try:
                    board = apply_move(board, next_to_move, state.move1[i])
                    board = apply_move(board, state.to_move, move[i])
                except KeyError:
                    break
            next_state = TronState(board, next_to_move)
        else:
            next_state = TronState(state.board, next_to_move, move)
            next_state.score_cache = state.score_cache
        state.move_cache[move] = next_state
        next_state.parent = state
        next_state.last_move = move
        return next_state

    def move_to_return(self, move):
        "Translate this move into what should be returned to the bot."
        return move[0]

#_____________________________________________________________________
# Evaluation Function (very important)
#

def eval_fn(state):
    "Assign a score to this board relative to player."

    # Check the cache first, since computing it is expensive.
    if state.score_cache:
        logging.debug('cache hit on score: %0.2f', state.score_cache)
        return state.score_cache
    
    try:
        p1, p2, t, touching = dfs_count_around(state.board)

        # Neither of us have space.
        # Thus, it's a draw.
        if not (p1 or p2):
            score = -0.5

        # I have no space, but they do.
        # Thus, I lose.
        elif not p1:
            score = -1.0

        # They have no space, but I do.
        # Thus, I win.
        elif not p2:
            score = 1.0

        # We both have some space available.
        # Whoever has more is most likely to win.
        else:
            m1, m2 = max(p1.values()), max(p2.values())
            total = m1 + m2
            score = float(m1) / float(total) * 2.0 - 1.0
                
    # KeyError occurs if one of the players disappear (i.e. they crashed)
    except KeyError:
        score = -0.5 

    # Write out some debug messages.
    logging.debug('score %0.2f', score)
    for line in state.board.board:
        logging.debug(line)

    # Save this in case we need it again.
    state.score_cache = score
    return score

#_____________________________________________________________________
# Cut-off Function (also very important)
#

def make_cutoff_fn(max_depth, stats, finish_by, game):
    "Create a cutoff function based on the given parameters."
    
    # This cutoff function is pretty simple. Basically it
    # does the normal depth test, in support of the iterative
    # deepening search, along with the required terminal test.

    # The main thing it adds is the time check. Whenever this
    # is called it checks if its nearing the deadline for
    # submitting the move and throws an exception that will
    # be caught by the search, so that the best completed move
    # so far can be returned on time to the game engine.

    def cutoff_fn(state, depth):
        "Determine whether to cutoff the search."
        
        if finish_by and time.time() >= finish_by:
            raise TimeAlmostUp()
        
        stats.nodes += 1
        stats.max_depth = max(stats.max_depth, depth)
        
        return depth >= max_depth or game.terminal_test(state)
        
    return cutoff_fn

#_____________________________________________________________________
# Primary Interface for the Bot
#

def alphabeta_search(board, game, finish_by=None):
    "Find a move based on an alpha-beta search of the game tree."

    # Pick at least some default to move if we're really slow.
    # We also keep it updated each level further we go down.
    best_completed_move = board.moves()[0]
    
    try:
        state = TronState(board, tron.ME)

        # Use iterative deepening search around the AIMA minimax
        # algorithm (the one that uses alpha-beta pruning and allows
        # the search to be cutoff and evaluated early. We deepen by
        # 2 to account for the way the moves are handled simultaneously
        # by the game class to match the production engine.
        for depth_limit in xrange(2, sys.maxint, 2):

            stats = utils.Struct(nodes=0, max_depth=0)
            cutoff_fn = make_cutoff_fn(depth_limit, stats, finish_by, game)
            move = games.alphabeta_search(state, game, None, cutoff_fn, eval_fn)

            # Return this move if we didn't get any deeper.
            if stats.nodes <= 2:
                return game.move_to_return(move)
            else:
                best_completed_move = game.move_to_return(move)
                
    except TimeAlmostUp:
        return best_completed_move
