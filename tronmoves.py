import time, logging
import games, utils
import tron
from tronutils import *
from aimatron import *

#_____________________________________________________________________
# Strategy Definition
#

def surrender_move(board):
    "Return a constant move in order to surrender."
    return tron.NORTH

def random_move(board):
    "Just return any random legal move."
    return random.choice(board.moves())

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

# Create a single instance of the game implementation to
# use in interfacing to the AIMA alpha-beta search routine.
game = TronGame() 

def minimax_move(board, finish_by=None):
    "Find a move based on an alpha-beta search of the game tree."
    
    def make_cutoff(max_depth, stats):
        def cutoff(state, depth):
            if finish_by and time.time() >= finish_by:
                raise TimeAlmostUp()
            too_deep = depth > max_depth
            game_over = game.terminal_test(state)
            should_cutoff = too_deep or game_over
            stats.nodes += 1
            logging.debug('max_depth: %s, %d, %d', stats, stats.max_depth, depth)
            stats.max_depth = max(stats.max_depth, depth)
            if should_cutoff:
                logging.debug('cutoff (%d, %s, %s)', depth, too_deep, game_over)
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

