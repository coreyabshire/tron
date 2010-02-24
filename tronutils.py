import tron

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

def set_char(s, i, c):
    "Return a copy of s with the character at index i replaced with c."
    return s[:i] + c + s[i+1:]
    
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

def distance((y1,x1),(y2,x2)):
    return abs(x2-x1) + abs(y2-y1)
    
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


