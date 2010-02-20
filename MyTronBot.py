#!/usr/bin/python

"""TronBot implementation by Corey Abshire."""

from collections import deque
import random, math, numpy
import optparse, logging, time, cProfile
import games, utils
import dijkstra
import tron

#_____________________________________________________________________
# Constants and Enumerations
#

DIR_NAMES = { tron.NORTH : 'NORTH', tron.SOUTH : 'SOUTH',
              tron.EAST  : 'EAST',  tron.WEST  : 'WEST' }

DIR_ABBRS = dict(zip(DIR_NAMES.keys(), [s[0] for s in DIR_NAMES.values()]))

#_____________________________________________________________________
# Configuration
#

argp = optparse.OptionParser()
argp.add_option("-d", "--depth", type="int", dest="depth", default=6)
argp.add_option("-l", "--log", dest="logfile", default=None)
argp.add_option("-s", "--strategy", default="main")
argp.add_option("--hurry", type="float", dest="hurry", default=0.01)
argp.add_option("--profile", dest="profile", default=None)

#_____________________________________________________________________
# Board Helper Functions
#

def read_board(filename):
    "Read a board from a map file."
    f = open(filename)
    width,height = [int(s) for s in f.readline().strip().split()]
    board = [s[:width] for s in f.readlines()]
    f.close()
    return tron.Board(width, height, board)

def write_board(board, filename):
    f = open(filename, 'w')
    f.write('%d %d\n' % (board.width, board.height))
    for line in board.board:
        f.write('%s\n' % line)
    f.close()

def print_board(board, filename):
    print board.width, board.height
    for line in board.board:
        print line

def valid_coords(board, (y,x)):
    "Are the coordinates within the board dimensions?"
    return 0 <= y < board.height and 0 <= x < board.width

def tile_is_a(kind_of):
    "Return a tile matcher that checks if the tile at coords is kind_of."
    def fn(board, coords):
        if valid_coords(board, coords):
            return board[coords] == kind_of
    return fn

def invert(fn):
    return lambda *args: not fn(*args)

is_wall = tile_is_a(tron.WALL)
is_floor = tile_is_a(tron.FLOOR)
is_nonwall = invert(tile_is_a(tron.WALL))

adjacent_floor = lambda board, coords: adjacent(board, coords, is_floor)

def tiles_matching(board, fn):
    "Collect all tiles on the board matching fn."
    tiles = []
    for y in xrange(board.height):
        for x in xrange(board.width):
            if fn(board, (y,x)):
                tiles.append((y,x))
    return tiles

def adjacent(board, coords, fn):
    "Find all tiles on board adjacent to coords matching fn."
    return [a for a in board.adjacent(coords) if fn(board, a)]

def surrounding_offset_array():
    z = [-1, 0, 1]
    return [(s,t) for t in z for s in z]

SOA = surrounding_offset_array()

def offset((y,x), (t,s)):
    return (y+t, x+s)

def surrounding_nonfloor(board, origin):
    a = [offset(origin, o) for o in SOA]
    return [c for c in a if board[c] != tron.FLOOR]

def move_made((y1,x1),(y2,x2)):
    "Return the move needed to get from a to b. Assumes adjacency."
    if   y2 < y1: return tron.NORTH
    elif y2 > y1: return tron.SOUTH
    elif x2 > x1: return tron.EAST
    else        : return tron.WEST

def is_game_over(board):
    "Determine whether this board is at an end game state."
    try:
        return not adjacent(board, board.me(), is_floor) \
            or not adjacent(board, board.them(), is_floor)
    except KeyError:
        return True # one player disappears if they crash into each other

def print_board(board):
    "Print the board just like the engine does to stdout."
    print board.height, board.width
    print '\n'.join(board.board)

def win_lose_or_draw(board, player):
    "Did player on board is a win (1), lose (-1), or draw (0.0)."
    try:
        me = board.me()
        them = board.them()
    except KeyError:
        return -0.5 # one player disappears if they crash into each other
    me_stuck = not adjacent(board, me, is_floor)
    them_stuck = not adjacent(board, them, is_floor)
    if me_stuck and them_stuck:
        return -0.5
    elif me_stuck or them_stuck:
        if player == tron.ME:
            return me_stuck and -1 or 1
        else:
            return me_stuck and 1 or -1
    else:
        return -0.5

def set_char(s, i, c):
    "Return a copy of s with the character at index i replaced with c."
    return s[:i] + c + s[i+1:]
    
def try_move(board, p, d):
    "Create a copy of board where player p is moved in direction d."
    lines = [line for line in board.board] # shallow copy
    (y1,x1) = board.find(p)
    (y2,x2) = board.rel(d, (y1,x1))
    lines[y1] = set_char(lines[y1], x1, tron.WALL)
    lines[y2] = set_char(lines[y2], x2, p)
    return tron.Board(board.width, board.height, lines)

def opponent(player):
    "Determine the opposite player."
    if player == tron.ME:
        return tron.THEM
    else:
        return tron.ME

def points_around(board, coords, around=adjacent_floor):
    "All the open spaces around coords."
    # http://mail.python.org/pipermail/image-sig/2005-September/003559.html
    count = 0
    edge = [coords]
    seen = set()
    while edge:
        newedge = []
        for tile in edge:
            for adj in around(board, tile):
                if adj not in seen:
                    count += 1
                    seen.add(adj)
                    newedge.append(adj)
        edge = newedge
    return seen

def count_around(board, coords, around=adjacent_floor):
    "Count of all spaces around coords."
    return len(points_around(board, coords, around))

#_____________________________________________________________________
# AIMA Alpha-Beta Search Interface
#

# TODO: Need to find a reliable way to test this without
#       putting something in place that I constantly have
#       to modify. Maybe record some scenarios like I
#       started before and write the test cases against it.

def ab_cutoff(state, depth):
    need_to_hurry = env.need_to_hurry()
    if depth > config.depth or game.terminal_test(state) or need_to_hurry:
        logging.debug('cutoff at depth %d, need to hurry %s', depth, need_to_hurry)
        return True
    else:
        return False

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
        try:
            p1_pos = board.find(tron.ME)
            p2_pos = board.find(tron.THEM)
            p1_room = self.count_around(p1_pos)
            p2_room = self.count_around(p2_pos)
            total = p1_room + p2_room
            if total == 0.0:
                score = 0.0
            else: 
                score = float(p1_room) / float(total) * 2.0 - 1.0
        except KeyError:
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
# Shortest Path
#

class DijkstraNeighbors():
    "Adapter for Dijkstra algorithm implementation. Dict of neighbors."
    
    def __init__(self, neighbors):
        self.neighbors = neighbors
        
    def __iter__(self):
        return self.neighbors.__iter__()
    
    def __getitem__(self, coords):
        return 1 # all neighbors are 1 square away in Tron
        
class DijkstraGraph():
    "Adapter for Dijkstra algorithm implementation. Graph of tiles."

    def __init__(self, board, test):
        self.board = board
        self.test = test

    def __getitem__(self, coords):
        return DijkstraNeighbors(adjacent(self.board, coords, self.test))

def shortest_path(board, start, end, test=is_nonwall):
    "Return the shortest path between two points on the board."
    return dijkstra.shortestPath(DijkstraGraph(board, test), start, end)

def moves_between(path):
    "Number of moves it would take for two players to traverse the path."
    return len(path) - 2

class Adjacent():
    "Dictionary for adjacent tiles on a Tron board."
    def __init__(self, board, test):
        self.board = board
        self.test = test
    def __getitem__(self, coords):
        return adjacent(self.board, coords, self.test)

def brandes(V, A):
    "Compute betweenness centrality in an unweighted graph."
    # Brandes algorithm
    # see http://www.cs.ucc.ie/~rb4/resources/Brandes.pdf
    C = dict((v,0) for v in V)
    for s in V:
        S = []
        P = dict((w,[]) for w in V)
        g = dict((t, 0) for t in V); g[s] = 1
        d = dict((t,-1) for t in V); d[s] = 0
        Q = deque([])
        Q.append(s)
        while Q:
            v = Q.popleft()
            S.append(v)
            for w in A[v]:
                if d[w] < 0:
                    Q.append(w)
                    d[w] = d[v] + 1
                if d[w] == d[v] + 1:
                    g[w] = g[w] + g[v]
                    P[w].append(v)
        e = dict((v, 0) for v in V)
        while S:
            w = S.pop()
            for v in P[w]:
                e[v] = e[v] + (g[v]/g[w]) * (1 + e[w])
                if w != s:
                    C[w] = C[w] + e[w]
    return C

def centrality(board):
    "Compute betweenness centrality for the floor of a Tron board."
    V = tiles_matching(board, is_floor)
    A = Adjacent(board, is_floor)
    return brandes(V, A)

def articulation_points(V, A):
    S = []
    pass

def depth_first_search(board, coords):
    pass

#_____________________________________________________________________
# Environment Recognition
#

# TODO: add a test for this
def find_walls(board):
    "Find all the walls (contingous series of wall tiles)."
    wall_tiles_remaining = set(tiles_matching(board, is_wall))
    walls = []
    while wall_tiles_remaining:
        wall = set()
        rest_of_wall = [wall_tiles_remaining.pop()]
        while rest_of_wall:
            another = rest_of_wall.pop()
            wall.add(another)
            adjacent_walls = adjacent(board, another, is_wall)
            for x in adjacent_walls:
                if x not in wall:
                    rest_of_wall.append(x)
                    if x in wall_tiles_remaining:
                        wall_tiles_remaining.remove(x)
        walls.append(wall)
    return walls

# TODO: find a way to test this (its non-deterministic)
def heat_map(board, paths=20, dump=False):
    "Identify hotspots by counting coordinate hits on random paths."
    points = [p for p in points_around(board, board.me())]
    heat = {}
    max_heat = 0
    for v in points:
        heat[v] = 0
    for i in range(paths):
        a = random.choice(points)
        b = random.choice(points)
        p = shortest_path(board, a, b, is_floor)
        for v in p:
            heat[v] += 1
            if heat[v] > max_heat:
                max_heat = heat[v]
    if dump:
        for y in xrange(board.height):
            for x in xrange(board.width):
                if (y,x) in heat:
                    print int((float(heat[y,x]) / max_heat) * 9.0),
                else:
                    print board[y,x],
            print
    return heat

def distance_map(board, coords):
    "Find the distance to all floor tiles from coords."
    seen = set(coords)
    q = deque([coords])
    d = { coords: 0 }
    while q:
        p = q.popleft()
        for a in adjacent(board, p, is_floor):
            if a not in seen:
                seen.add(a)
                q.append(a)
                d[a] = d[p] + 1
    return d

def same_distance(board, a, b):
    "Return all points equidistant from a and b."
    m = distance_map(board, a)
    n = distance_map(board, b)
    keys = set(m.keys()).intersection(set(n.keys()))
    return [k for k in keys if m[k] == n[k]]

#_____________________________________________________________________
# Strategy Definition
#

# Create a single instance of the game implementation to
# use in interfacing to the AIMA alpha-beta search routine.
game = TronGame() 

def random_strategy(board):
    # For now, choose a legal move randomly.
    # Note that board.moves will produce [NORTH] if there are no
    # legal moves available.
    return random.choice(board.moves())

def most_open_strategy(board):
    coords = board.me()
    best_move = tron.NORTH
    highest = 0
    for move in board.moves():
        next = try_move(board, tron.ME, move)
        count = count_around(next, board.rel(move, coords))
        if count >= highest:
            highest = count
            best_move = move
    return best_move

def free_strategy(board):
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

# preference order of directions
ORDER = list(tron.DIRECTIONS)
random.shuffle(ORDER)

def wall_strategy(state):
    board = state.board

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

def alphabeta_strategy(state):
    "Find a move based on an alpha-beta search of the game tree."
    stats = utils.Struct(nodes=0, max_depth=0)
    def cutoff(state, depth):
        stats.nodes += 1
        stats.max_depth = max(stats.max_depth, depth)
        return ab_cutoff(state, depth)
    eval_fn = lambda state: state.score()
    d = games.alphabeta_search(state, game, cutoff_test=cutoff, eval_fn=eval_fn)
    logging.debug('alphabeta %s (%s)', d, stats)
    return d

def heatseeker_strategy(state):
    "Use hotspots to identify and find targets."
    board = state.board
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
        return alphabeta_strategy(state)

def closecall_strategy(state):
    "Get close to the opponent then solve with alphabeta."
    board = state.board
    try:
        path = shortest_path(board, board.me(), board.them())
        n = moves_between(path)
        if (n <= 3):
            return alphabeta_strategy(board)
        else:
            return move_made(board.me(), path[1])
    except KeyError:
        return alphabeta_strategy(board)

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
# Cache, Analysis, History, etc...
#

class Environment():
    "Simple container for agent data."

    def __init__(self, timed=True):
        self.reset(timed)

    def reset(self, timed=True):
        time_limit = 2.0
        self.first_move = True   # is this our first move or not?
        self.walls = []          # a list of the walls on this board
        self.bh = []             # history of all boards received
        self.mph = []            # my position history
        self.eph = []            # enemy's position history
        self.mmh = []            # my move history
        self.emh = []            # enemy's move history

        self.mfm = deque()       # my future moves
        self.ofm = deque()       # my opponents future moves

        self.nmoves = 0          # number of moves seen

        self.start_time = 0      # start time for this move
        self.times = []          # time taken for each move
        self.timed = timed
        self.time_limit = time_limit    # initial time limit
        
    def update(self, board):

        self.nmoves += 1
        self.start_time = time.time()
        
        # record board history for pattern recognition
        self.bh.append(board)
        
        self.mph.append(board.me())
        self.eph.append(board.them())

        # capture initial info about the board on the first move
        if self.first_move == True:
            self.walls = find_walls(board)
            self.first_move = False
        else:
            self.mmh.append(move_made(self.mph[-2], self.mph[-1]))
            self.emh.append(move_made(self.eph[-2], self.eph[-1]))

    def elapsed(self):
        return time.time() - self.start_time
            
    def record_time(self):
        elapsed = self.elapsed()
        self.times.append(elapsed)
        return elapsed

    def time_remaining(self):
        return self.time_limit - self.elapsed()

    def need_to_hurry(self):
        return self.timed and self.time_remaining() < config.hurry
            
env = Environment()

#_____________________________________________________________________
# Main Decision Routine
#

def main_strategy(state):
    "Determine which move to make given the current board state."
    board = state.board
    
    # fill in your code here. it must return one of the following directions:
    #   tron.NORTH, tron.EAST, tron.SOUTH, tron.WEST

    # record history and other facts about the board for use throughout


    # shortest path between me and my enemy, or none if we're disconnected
    cpath = None
    cdist = None
    try:
        cpath = shortest_path(board, board.me(), board.them())
        cdist = moves_between(cpath)
    except KeyError:
        cpath = None

    # calculate future moves
    if env.mfm:
        if not board.passable(board.rel(env.mfm[0], board.me())):
            env.mfm = deque()
    if not env.mfm and cpath:
        for i in xrange(cdist):
            env.mfm.append(move_made(cpath[i], cpath[i+1]))

    # in some cases we will be asked to move when there is no
    # move available: it doesn't matter, just return NORTH
    if cdist > 3 and env.mfm:
        logging.debug('using cached path')
        my_move = env.mfm.popleft()
    else:
        # determine which move I should make
        logging.debug('using close call')
        my_move = closecall_strategy(board)

    return my_move

def enable_logging(logfile, level=logging.DEBUG):
    "Enable logging to the specified logfile."
    logging.basicConfig(filename=logfile, level=level, filemode='w')

def mainloop():
    root = state = None
    for board in tron.Board.generate():
        if env.first_move:
            root = state = TronState.make_root(board, tron.ME)
            state.actual = True
        else:
            their_move = move_made(state.board.them(), board.them())
            logging.debug('them: %s, %s', state.board.them(), board.them())
            logging.debug('their move was %s', DIR_NAMES[their_move])
            state = state.make_move(their_move)
            state.actual = True
        env.update(board)
        logging.debug('move %d', env.nmoves)
        my_move = tron.NORTH # default if no moves available
        if adjacent_floor(board, board.me()):
            my_move = which_move(state)
        else:
            logging.debug('no legal moves remaining')
            logging.debug('bypassing strategy')
        logging.debug('chose %s', DIR_NAMES[my_move])
        logging.debug("took %0.3f seconds", env.record_time())
        state = state.make_move(my_move)
        state.actual = True
        logging.debug('my new pos: %s', state.board.me())
        tron.move(my_move)

if __name__ == "__main__":
    config, args = argp.parse_args()
    if config.logfile:
        enable_logging(config.logfile)
    logging.debug('config: %s', config)
    which_move = globals()['%s_strategy' % config.strategy]
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
