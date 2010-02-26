# Utilities library for a TronBot for the Google AI Challenge 2010
# Corey Abshire, February 2010

import os, sys, random, tron, dijkstra, brandes
from collections import deque

#_____________________________________________________________________
# Constants and Enumerations
#

# Dictionary for translating direction codes to names.
DIR_NAMES = { tron.NORTH : 'NORTH' ,
              tron.SOUTH : 'SOUTH' ,
              tron.EAST  : 'EAST'  ,
              tron.WEST  : 'WEST'  }

# Dictionary for translating direction codes to abbreviations.
DIR_ABBRS = dict(zip(DIR_NAMES.keys(), [s[0] for s in DIR_NAMES.values()]))

#_____________________________________________________________________
# Board File I/O
#

def read_board(filename):
    "Read a board from a map file."
    f = open(filename)
    width,height = [int(s) for s in f.readline().strip().split()]
    board = [s[:width] for s in f.readlines()]
    f.close()
    return tron.Board(width, height, board)

def write_board(board, filename):
    "Write the given board out to a file in the same format as the maps."
    f = open(filename, 'w')
    f.write('%d %d\n' % (board.width, board.height))
    for line in board.board:
        f.write('%s\n' % line)
    f.close()

def print_board(board):
    "Print the board to standard out in the same format as the maps."
    print board.width, board.height
    for line in board.board:
        print line

def list_files(path):
    "Lists all the files in path, including path as the prefix."
    return [path + filename for filename in os.listdir(path)]

#_____________________________________________________________________
# Board Manipulation and Querying
#

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
    "Create a function that returns the logical inverse of the given function."
    return lambda *args: not fn(*args)

is_wall = tile_is_a(tron.WALL)
is_floor = tile_is_a(tron.FLOOR)
is_nonwall = invert(tile_is_a(tron.WALL))

def tiles_matching(board, fn):
    "Collect all tiles on the board matching fn."
    tiles = []
    for y in xrange(board.height):
        for x in xrange(board.width):
            if fn(board, (y,x)):
                tiles.append((y,x))
    return tiles

def adjacent(board, coords, predicate):
    "Find all tiles on board adjacent to coords matching fn."
    return [a for a in board.adjacent(coords) if predicate(board, a)]

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

def run_fill(board, move_fn, player=tron.ME, max_len=sys.maxint):
    "Apply move_fn repeatedly to build a path on the board."
    path = []
    while not is_game_over(board) and len(path) < max_len:
        move = move_fn(board)
        board = try_move(board, player, move)
        coords = board.me()
        path.append(coords)
    return path
        
#_____________________________________________________________________
# Board Game Logic
#

def is_game_over(board):
    "Determine whether this board is at an end game state."
    try:
        return not adjacent(board, board.me(), is_floor) \
            or not adjacent(board, board.them(), is_floor)
    except KeyError:
        return True # one player disappears if they crash into each other

def win_lose_or_draw(board, player):
    "Did player on board is a win (1), lose (-1), or draw (-0.5)."
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

def opponent(player):
    "Determine the opposite player."
    if player == tron.ME:
        return tron.THEM
    else:
        return tron.ME

def move_made((y1,x1),(y2,x2)):
    "Return the move needed to get from a to b. Assumes adjacency."
    if   y2 < y1: return tron.NORTH
    elif y2 > y1: return tron.SOUTH
    elif x2 > x1: return tron.EAST
    else        : return tron.WEST

def distance((y1, x1), (y2, x2)):
    "Compute the distance in moves between two tiles."
    return abs(x2 - x1) + abs(y2 - y1)

#_____________________________________________________________________
# Board Analysis
#
    
def points_around(board, coords, predicate=is_floor):
    "All the open spaces around coords."
    # http://mail.python.org/pipermail/image-sig/2005-September/003559.html
    count = 0
    edge = [coords]
    seen = set()
    while edge:
        newedge = []
        for tile in edge:
            for adj in adjacent(board, tile, is_floor):
                if adj not in seen:
                    count += 1
                    seen.add(adj)
                    newedge.append(adj)
        edge = newedge
    return seen

def count_around(board, coords, predicate=is_floor):
    "Count of all spaces around coords."
    return len(points_around(board, coords, predicate))

def anticipate(board, coords, pattern, num_moves):
    pos = coords
    i = 0; j = 0
    while i < num_moves:
        pos = board.rel(pattern[j], pos)
        i += 1
        j += 1
        if j >= len(pattern):
            j = 0
    return pos

class Adjacent():
    "Dictionary for adjacent tiles on a Tron board."
    def __init__(self, board, test):
        self.board = board
        self.test = test
    def __getitem__(self, coords):
        return adjacent(self.board, coords, self.test)

def centrality(board):
    "Compute betweenness centrality for the floor of a Tron board."
    V = tiles_matching(board, is_floor)
    A = Adjacent(board, is_floor)
    return brandes.brandes(V, A)

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
    # The path includes both the players tiles, so we just subtract
    # those 2 from the length of the path to get the moves between.
    return len(path) - 2

def dijkstra_map(board, start, end, test=is_nonwall):
    "Run Dijkstra's algorithm and return the distance map."
    d, p = dijkstra.Dijkstra(DijkstraGraph(board, test), start, end)
    return d
    

#_____________________________________________________________________
# Depth First Search
#

def articulation_points(board, root):
    sys.setrecursionlimit(2500)
    V = set(); A = Adjacent(board, is_floor)
    L = {}; N = {}; c = [0]; P = {}; X = set()
    def f(v):
        V.add(v)
        c[0] += 1
        L[v] = N[v] = c[0]
        for w in A[v]:
            if w not in V:
                P[w] = v
                f(w)
                if v != root and L[w] >= N[v]:
                    X.add(v)
                L[v] = min(L[v], L[w])
            else:
                if v in P and P[v] != w:
                    L[v] = min(L[v], N[w])
    f(root)
    return X

def dfs2(root, A, visited = None, preorder_process = lambda x: None):
    "Given a starting vertex, root, do a depth-first search."
    # see http://en.wikipedia.org/wiki/Depth-first_search#Implementation_in_Python
    to_visit = []  # a list can be used as a stack in Python
    if visited is None: visited = set()
    to_visit.append(root) # Start with root
    while len(to_visit) != 0:
        v = to_visit.pop()
        if v not in visited:
            visited.add(v)
            preorder_process(v)
            to_visit.extend(A[v])

def touching(t):
    for c in t:
        p = set(p for p,d in c)
        if tron.ME in p and tron.THEM in p:
            return True
    return False

def dfs_count_around(board):
    N = [tron.ME, tron.THEM]
    A = Adjacent(board, is_floor)
    P = [board.me(), board.them()]
    C = [{} for p in P]
    T = []
    remaining = set(A[P[0]] + A[P[1]])
    while remaining:
        u = remaining.pop()
        V = set([])
        dfs2(u, A, V)
        c = len(V)
        t = []
        for i in range(len(P)):
            p = P[i]
            for a in A[p]:
                if a in V:
                    d = move_made(p, a)
                    C[i][d] = c
                    t.append((N[i],d))
                    if a in remaining:
                        remaining.remove(a)
        T.append(t)
    return C[0], C[1], T, touching(T)

def dfs(V,A):
    # see CLRS (2nd) p. 541
    WHITE, GRAY, BLACK = 0, 1, 2
    init = lambda x: dict((u, x) for u in V)
    color, pi, d, f = [init(x) for x in (WHITE, None, 0, 0)]
    time = [0]
    depth = [0]
    max_depth = [0]
    n = [0]
    def visit(u):
        depth[0] += 1
        n[0] += 1
        max_depth[0] = max(max_depth[0], depth[0])
        color[u] = GRAY
        time[0] += 1
        d[u] = time[0]
        for v in A[u]:
            if color[v] == WHITE:
                pi[v] = u
                visit(v)
        f[u] = time[0] = time[0] + 1
        depth[0] -= 1
    for u in V:
        if color[u] == WHITE:
            visit(u)
    return d, f, pi, max_depth[0], n[0]

def depth_first_search(board):
    V = tiles_matching(board, is_floor)
    A = Adjacent(board, is_floor)
    return dfs(V, A)

def components(board):
    A = Adjacent(board, is_floor)
    Va = tiles_matching(board, is_floor)
    d,f,pi = dfs(Va,A)
    Vb = f.keys()
    Vb.sort(key=lambda x: f[x])
    g,h,pi = dfs(Vb,A)
    return g,h,pi
    

#_____________________________________________________________________
# Environment Recognition
#

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

def heat_map(board, paths=20):
    "Identify hotspots by counting coordinate hits on random paths."
    points = [p for p in points_around(board, board.me())]
    heat = {}
    max_heat = 0
    for v in points:
        heat[v] = 0
    for i in xrange(paths):
        a = random.choice(points)
        b = random.choice(points)
        p = shortest_path(board, a, b, is_floor)
        for v in p:
            heat[v] += 1
            if heat[v] > max_heat:
                max_heat = heat[v]
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
    same = [k for k in keys if m[k] == n[k]]
    same.sort(key=lambda k: m[k])
    return same

