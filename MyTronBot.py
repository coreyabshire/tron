#!/usr/bin/python

"""TronBot implementation by Corey Abshire."""

from collections import deque
import random, math, numpy
import optparse, logging, time, cProfile, sys
import games, utils
import tron
from tronutils import *

#_____________________________________________________________________
# Configuration
#

argp = optparse.OptionParser()
argp.add_option("-d", "--depth", type="int", dest="depth", default=8)
argp.add_option("-l", "--log", dest="logfile", default=None)
argp.add_option("--hurry", type="float", dest="hurry", default=0.1)
argp.add_option("--profile", dest="profile", default=None)
argp.add_option("--time_limit", dest="time_limit", type="float", default=1.0)
argp.add_option("--ab_thresh", dest="alphabeta_threshold", type="int", default=9)

#_____________________________________________________________________
# AIMA Alpha-Beta Search Interface
#

# TODO: Need to find a reliable way to test this without
#       putting something in place that I constantly have
#       to modify. Maybe record some scenarios like I
#       started before and write the test cases against it.

def touching(t):
    for c in t:
        p = set(p for p,d in c)
        if tron.ME in p and tron.THEM in p:
            return True
    return False

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
        self.actual = False
        try:
            self._count_around = dfs_count_around(board)
            p1, p2, t = self._count_around
            self._connected = touching(t)
        except KeyError:
            self._count_around = None
            self._connected = False

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

    def count_around(self, player):
        "All the open spaces around coords."
        # http://mail.python.org/pipermail/image-sig/2005-September/003559.html
        board = self.board
        count = 0
        edge = [player]
        seen = set([player])
        while edge:
            newedge = []
            for tile in edge:
                for adj in adjacent(board, tile, is_floor):
                    if adj not in seen:
                        if board[adj] == tron.FLOOR:
                            count += 1
                            seen.add(adj)
                            newedge.append(adj)
            edge = newedge
        return count

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

    def connected(self):
        return self._connected

    def score(self):
        "Assign a score to this board relative to player."
        if self._score:
            logging.debug('cache hit on score: %0.2f', self._score)
            return self._score
        board, player = self.board, self.to_move
        score = 0.0
        if self._count_around:
            p1, p2, t = self._count_around
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

        logging.debug('score %0.2f; %s', score, self.list_moves())
        for line in board.board:
            logging.debug(line)
        self._score = score
        return score

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

#_____________________________________________________________________
# Strategy Definition
#

# Create a single instance of the game implementation to
# use in interfacing to the AIMA alpha-beta search routine.
game = TronGame() 

def surrender_move(board):
    "Return a constant move in order to surrender."
    return tron.NORTH

def random_move(board):
    "Just return any random legal move."
    return random.choice(board.moves())

def most_open_move(board, order):
    "Find the move that has the most open floor filled around it."
    p1, p2, t = dfs_count_around(board)
    wall_move = follow_wall_move(board, order)
    open_move = utils.argmax(p1.keys(), lambda k: p1[k])
    if p1[wall_move] == p1[open_move]:
        best_move = wall_move
    else:
        best_move = open_move
    logging.debug("most open move is: %s (%d) %s", best_move, p1[best_move], p1)
    return best_move

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

def minimax_move(board, finish_by=None):
    "Find a move based on an alpha-beta search of the game tree."
    
    def make_cutoff(max_depth, stats):
        def cutoff(state, depth):
            if finish_by and time.time() >= finish_by:
                raise TimeAlmostUp()
            too_deep = depth > max_depth
            game_over = game.terminal_test(state)
            disconnected = not state.connected()
            should_cutoff = too_deep or game_over# or disconnected
            stats.nodes += 1
            logging.debug('max_depth: %s, %d, %d', stats, stats.max_depth, depth)
            stats.max_depth = max(stats.max_depth, depth)
            if should_cutoff:
                logging.debug('cutoff (%d, %s, %s, %s)', depth, too_deep, \
                                  game_over, disconnected)
                return True
            else:
                return False
        return cutoff
    state = TronState.make_root(board, tron.ME)
    best_completed_move = state.board.moves()[0]
    eval_fn = lambda state: state.score()
    try:
        for depth_limit in xrange(sys.maxint):
            stats = utils.Struct(nodes=0, max_depth=0, hurried=False)
            cut_fn = make_cutoff(depth_limit, stats)
            move = games.alphabeta_search(state, game, cutoff_test=cut_fn, eval_fn=eval_fn)
            logging.debug('alphabeta %s %s (%s)', depth_limit, move, stats)
            if stats.nodes <= 2:
                return move
            else:
                best_completed_move = move
    except TimeAlmostUp:
        logging.debug('alphabeta time almost up %s %s', depth_limit, move)
        return best_completed_move

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

# TODO: Test case on which_move which tests that index out of
#       range no longer occurs when we have no move available
#       at the beginning of our turn. legal_moves was returning
#       properly but the outer alpha-beta search threw index error.

# TODO: Test case for when the players collide. The legal moves
#       function was apparently picking up board from an outer
#       scope, instead of the one within the current state. This
#       was causing it to report that a square was open even though
#       the opponent was already on it.

#_____________________________________________________________________
# Main Decision Routine
#

def which_move(board, start_time, order, same_dist):
    "Determine which move to make given the current board state."

    # If I don't have any legal moves, its not even worth trying
    # one of the other strategies. This is done here to support
    # calling the other strategies from the command line.
    if not adjacent_floor(board, board.me()):
        logging.debug('no legal moves remaining; bypassign strategy')
        return surrender_move(board)

    # Calculate the shortest path from me to them. This is useful
    # for a couple of different strategies, plus, it tells me if
    # we are still connected or not.
    try:
        path_to_them = shortest_path(board, board.me(), board.them())
    except KeyError:
        path_to_them = None

    # Calculate the points that are the same distance between me
    # and them. 
            
    # If we're no longer connected, we do not need to consider
    # the opponents moves at all. Instead, we should just focus
    # on using as much of the board as possible. The best strategy
    # I have for that at the moment is the most open strategy.
    if not path_to_them:
        logging.debug('not connected, so using most open')
        return most_open_move(board, order)

    # If we're close enough that minimax with alpha-beta pruning
    # is practical, then we should use that. It should return the
    # absolute best move if it can see far enough ahead in terms
    # of board space.
    if moves_between(path_to_them) <= config.alphabeta_threshold:
        finish_by = start_time + config.time_limit - config.hurry
        logging.debug('within threshold, so using alphabeta')
        return minimax_move(board, finish_by)

    # If there is a set of a few points that me and my opponent
    # are an equal distance from, then the are probably pretty
    # important on the board (such as for 'u' and for 'joust').
    # As such, go target those points. Once those points have
    # been achieved, just try to fill in the remaining space.
    # (I still have concerns about this one. Needs work.)
    if len(same_dist) > 1 and len(same_dist) <= 4:
        logging.debug('targeting first same dist tile')
        return same_dist_move(board, same_dist, order)

    # If all else fails, lets just charge the opponent by taking
    # the shortest path to them and try to let the minimax with
    # alpha-beta pruning get us a victory.
    logging.debug('using shortest path to opponent')
    return follow_path_move(board, path_to_them)

def enable_logging(logfile, level=logging.DEBUG):
    "Enable logging to the specified logfile."
    logging.basicConfig(filename=logfile, level=level, filemode='w')

def mainloop():

    order = list(tron.DIRECTIONS)
    random.shuffle(order)
    nmoves = 0
    first_move = True

    # Start looping through all the boards, just like in the example.
    for board in tron.Board.generate():

        start_time = time.time()

        if first_move:
            same_dist = same_distance(board, board.me(), board.them())
            first_move = False

        # Log the current move number.
        logging.debug('move %d', nmoves)

        # Call the configured strategy to determine the best move.
        # Then update the local state object and log a few details.
        # Finally, submit the move to the engine using the API.
        my_move = which_move(board, start_time, order, same_dist)
        logging.debug('chose %s', DIR_NAMES[my_move])
        logging.debug("took %0.3f seconds", time.time() - start_time)
        logging.debug('my new pos: %s', board.me())
        tron.move(my_move)

        nmoves += 1

#_____________________________________________________________________
# Main Block
#
# This is the main startup section for MyTronBot.
#
# It supports the following use cases:
#        
#  1. Running from the server with no arguments
#     using whatever strategy and configuration I
#     have determine is the best I have.
#
#  2. Running from my local command line, accepting
#     various arguments I can use to tweak, test,
#     and analyze its performance.
#
#  3. Being imported from the python shell as a
#     library so that I can interact with the logic
#     in real-time to inspect and to support development.
#
#  4. Being imported as a library from another script
#     to support unit testing or visualization.
#
if __name__ == "__main__":
    config, args = argp.parse_args()
    if config.logfile:
        enable_logging(config.logfile)
    logging.debug('config: %s', config)
    if config.profile:
        cProfile.run('mainloop()', config.profile)
    else:
        mainloop()

else:
    # Most common case for starting as a library
    # is for an online session from the interpreter
    # or for the test cases. Calling parse_args
    # even though there won't be any will set up
    # all the defaults for either case, which is good.
    config, args = argp.parse_args() 
