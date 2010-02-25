import logging, time
import games, utils
import tron
from tronutils import *

#_____________________________________________________________________
# AIMA Alpha-Beta Search Interface
#

class TimeAlmostUp():
    pass

#_____________________________________________________________________
# Simple Representation (one move at a time)
#

class TronState():

    def __init__(self, board, to_move, move1=None):

        # The basic state information.
        self.board = board
        self.to_move = to_move
        self.move1 = move1

        # Caches to speed things up.
        self.score_cache = None
        self.move_cache = {}

        # The parent and last move are for listing the path.
        self.parent = None
        self.last_move = None 

    def list_moves(self):
        state = self
        moves = []
        while state:
            if state.parent:
                d = DIR_ABBRS[state.last_move]
                moves.append("%s,%s" % (state.parent.to_move, d))
            state = state.parent
        moves.reverse()
        return moves

class TronGame(games.Game):
    "A representation of Tron compatible with AIMA alpha-beta."

    def legal_moves(self, state):
        "Find all the moves possible from the current state."
        pos = state.board.find(state.to_move)
        return [move_made(pos, adj) for adj in adjacent(state.board, pos, is_floor)]

    def make_move(self, move, state):
        "Return the new state resulting from making the given move."
        if move in state.move_cache:
            logging.debug('cache hit on child')
            return state.move_cache[move]
        next_to_move = opponent(state.to_move)
        if state.move1:
            next_board = try_move(state.board, next_to_move, state.move1)
            next_board = try_move(next_board, state.to_move, move)
            next_state = TronState(next_board, next_to_move)
        else:
            next_state = TronState(state.board, next_to_move, move)
        state.move_cache[move] = next_state
        next_state.parent = state
        next_state.last_move = move
        return next_state

    def utility(self, state, player):
        "Determine the utility of the given terminal state for player."
        return win_lose_or_draw(state.board, tron.ME)

    def terminal_test(self, state):
        "Determine whether the current state is a leaf state."
        return is_game_over(state.board)

    def display(self, state):
        "Print the board to the console."
        print_board(state.board)

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

        # Neither of us have space. So its a draw.
        if not (p1 or p2):
            score = -0.5

        # I have no space, but they do. So I lose.
        elif not p1:
            score = -1.0

        # They have no space, but I do. So I win.
        elif not p2:
            score = 1.0

        # We both have space. Figure out who has more.
        else:
            m1, m2 = max(p1.values()), max(p2.values())
            total = m1 + m2
            score = float(m1) / float(total) * 2.0 - 1.0
                
    # KeyError occurs if one of the players disappear (i.e. they crashed)
    except KeyError:
        score = -0.5 

    # Write out some debug messages.
    logging.debug('score %0.2f; %s', score, state.list_moves())
    for line in state.board.board:
        logging.debug(line)

    # Save this in case we need it again.
    state.score_cache = score
    return score


#_____________________________________________________________________
# Cut-off Function (also very important)
#

def make_cutoff_fn(max_depth, stats, finish_by):
    "Create a cutoff function based on the given parameters."
    
    def cutoff_fn(state, depth):
        "Determine whether to cutoff the search."
        if finish_by and time.time() >= finish_by:
            raise TimeAlmostUp()
        stats.nodes += 1
        stats.max_depth = max(stats.max_depth, depth)
        if depth > max_depth or game.terminal_test(state):
            return True
        else:
            return False
        
    return cutoff_fn


#_____________________________________________________________________
# Interface Function for the Bot
#

# Create a single instance of the game implementation to
# use in interfacing to the AIMA alpha-beta search routine.
game = TronGame() 

def alphabeta_search(board, finish_by=None):
    "Find a move based on an alpha-beta search of the game tree."
    best_completed_move = board.moves()[0]
    state = TronState(board, tron.ME)
    try:
        for depth_limit in xrange(sys.maxint):
            stats = utils.Struct(nodes=0, max_depth=0)
            cutoff_fn = make_cutoff_fn(depth_limit, stats, finish_by)
            move = games.alphabeta_search(state, game, None, cutoff_fn, eval_fn)
            logging.debug('alphabeta %s %s (%s)', depth_limit, move, stats)
            if stats.nodes <= 2:
                return move
            else:
                best_completed_move = move
    except TimeAlmostUp:
        logging.debug('alphabeta time almost up %s %s', depth_limit, move)
        return best_completed_move
