import logging, time
import games, utils
import tron
from tronutils import *

#_____________________________________________________________________
# AIMA Alpha-Beta Search Interface
#

# TODO: Need to find a reliable way to test this without
#       putting something in place that I constantly have
#       to modify. Maybe record some scenarios like I
#       started before and write the test cases against it.

class TimeAlmostUp():
    pass

class TronState():

    def __init__(self, board, to_move, move1=None):
        self.board = board
        self.to_move = to_move
        self.move1 = move1
        self._score = None
        self._children = {}
        self._available = None
        self._adjacent = {}
        try:
            self._count_around = dfs_count_around(board)
        except KeyError:
            self._count_around = None

    def adjacent(self, coords):
        "Find all the moves possible from the current state."
        if coords in self._adjacent:
            return self._adjacent[coords]
        else:
            b = self.board # short-hand for the board in the current state
            possible = [(d,b.rel(d, coords)) for d in tron.DIRECTIONS]
            passable = [(d,pos) for (d,pos) in possible if b.passable(pos)]
            self._adjacent[coords] = passable
            return passable

    def available(self):
        "Find all the moves possible from the current state."
        return self.adjacent(self.board.find(self.to_move))

    @classmethod
    def make_root(self, board, to_move):
        root = TronState(board, to_move, None)
        root.parent = None
        root.last_move = None 
        return root

    def make_move(self, move):
        if move in self._children:
            logging.debug('cache hit on child')
            return self._children[move]
        next_to_move = opponent(self.to_move)
        if self.move1:
            next_board = try_move(self.board, next_to_move, self.move1)
            next_board = try_move(next_board, self.to_move, move)
            child = TronState(next_board, next_to_move)
        else:
            child = TronState(self.board, next_to_move, move)
        self._children[move] = child
        child.parent = self
        child.last_move = move
        return child

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
        return [d for (d,s) in state.available()]

    def make_move(self, move, state):
        "Return the new state resulting from making the given move."
        return state.make_move(move)

    def utility(self, state, player):
        "Determine the utility of the given terminal state for player."
        return win_lose_or_draw(state.board, tron.ME)

    def terminal_test(self, state):
        "Determine whether the current state is a leaf state."
        return is_game_over(state.board)

    def display(self, state):
        "Print the board to the console."
        print_board(state.board)

def eval_fn(state):
    "Assign a score to this board relative to player."
    if state._score:
        logging.debug('cache hit on score: %0.2f', state._score)
        return state._score
    board, player = state.board, state.to_move
    score = 0.0
    if state._count_around:
        p1, p2, t, touching = state._count_around
        if not (p1 or p2):
            score = -0.5
        elif not p1:
            score = -1.0
        elif not p2:
            score = 1.0
        else:
            m1, m2 = max(p1.values()), max(p2.values())
            total = m1 + m2
            if total == 0.0:
                score = -0.5
            else: 
                score = float(m1) / float(total) * 2.0 - 1.0
    else:
        score = -0.5 # one of the players disappears if they crash

    logging.debug('score %0.2f; %s', score, state.list_moves())
    for line in board.board:
        logging.debug(line)
    state._score = score
    return score


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

# Create a single instance of the game implementation to
# use in interfacing to the AIMA alpha-beta search routine.
game = TronGame() 

def alphabeta_search(board, finish_by=None):
    "Find a move based on an alpha-beta search of the game tree."
    best_completed_move = board.moves()[0]
    state = TronState.make_root(board, tron.ME)
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
