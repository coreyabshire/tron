#!/usr/bin/python

"""TronBot implementation by Corey Abshire."""

import tron, games, random, utils, dijkstra, math, numpy

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

def adjacent_nonwall(board, origin):
    "Return the positions around origin that are not walls."
    return [c for c in board.adjacent(origin) if board[c] != tron.WALL]

def adjacent_floor(board, origin):
    "Return the positions around origin that are floor spaces (open)."
    return [c for c in board.adjacent(origin) if board[c] == tron.FLOOR]

def surrounding_offset_array():
    z = [-1, 0, 1]
    return [(s,t) for t in z for s in z]

SOA = surrounding_offset_array()

def offset((y,x), (t,s)):
    return (y+t, x+s)

def surrounding_nonfloor(board, origin):
    a = [offset(origin, o) for o in SOA]
    return [c for c in a if board[c] != tron.FLOOR]

def move_made(board, a, b):
    "Return the move needed to get from a to b. Assumes adjacency."
    return [d for d in tron.DIRECTIONS if board.rel(d, a) == b][0]

def is_game_over(board):
    "Determine whether this board is at an end game state."
    return not adjacent_floor(board, board.me()) \
        or not adjacent_floor(board, board.them())

def print_board(board):
    "Print the board just like the engine does to stdout."
    print board.height, board.width
    print '\n'.join(board.board)

def win_lose_or_draw(board, player):
    "Did player on board is a win (1), lose (-1), or draw (0)."
    me_stuck = not adjacent_floor(board, board.me())
    them_stuck = not adjacent_floor(board, board.them())
    if me_stuck and them_stuck:
        return 0
    elif me_stuck or them_stuck:
        if player == tron.ME:
            return me_stuck and -1 or 1
        else:
            return me_stuck and 1 or -1
    else:
        return 0

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

#_____________________________________________________________________
# AIMA Alpha-Beta Search Interface
#

def make_state(board, to_move):
    "Encapsulate the board and next player in a state struct for AIMA."
    return utils.Struct(board=board, to_move=to_move)

class TronGame(games.Game):
    "A representation of Tron compatible with AIMA alpha-beta."

    def legal_moves(self, state):
        "Find all the moves possible from the current state."
        b = state.board # short-hand for the board in the current state
        c = b.find(state.to_move) # coords of current player
        return [d for d in tron.DIRECTIONS if b.passable(b.rel(d, c))]

    def make_move(self, move, state):
        "Return the new state resulting from making the given move."
        next_board = try_move(state.board, state.to_move, move)
        return make_state(next_board, opponent(state.to_move))

    def utility(self, state, player):
        "Determine the utility of the given terminal state for player."
        return win_lose_or_draw(state.board, player)

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

    def __init__(self, board):
        self.board = board

    def __getitem__(self, coords):
        return DijkstraNeighbors(adjacent_nonwall(self.board, coords))

def shortest_path(board, start, end):
    "Return the shortest path between two points on the board."
    return dijkstra.shortestPath(DijkstraGraph(board), start, end)

def moves_between(path):
    "Number of moves it would take for two players to traverse the path."
    return len(path) - 2

#_____________________________________________________________________
# Environment Recognition
#

def spaces_analysis(board):
    pass

#_____________________________________________________________________
# Strategy Definition
#

# Create a single instance of the game implementation to
# use in interfacing to the AIMA alpha-beta search routine.
game = TronGame() 

def random_decision(board):
    # For now, choose a legal move randomly.
    # Note that board.moves will produce [NORTH] if there are no
    # legal moves available.
    return random.choice(board.moves())

def free_decision(board):
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

def wall_decision(board):

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

def alphabeta_decision(board):
    "Find a move based on an alpha-beta search of the game tree."
    return games.alphabeta_search(make_state(board, tron.ME), game, d=6)

def closecall_decision(board):
    try:
        path = shortest_path(board, board.me(), board.them())
        n = moves_between(path)
        if (n <= 3):
            return alphabeta_decision(board)
        else:
            return move_made(board, board.me(), path[1])
    except KeyError:
        return alphabeta_decision(board)

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

def which_move(board):
    "Determine which move to make given the current board state."

    # fill in your code here. it must return one of the following directions:
    #   tron.NORTH, tron.EAST, tron.SOUTH, tron.WEST

    # in some cases we will be asked to move when there is no
    # move available: it doesn't matter, just return NORTH
    if not adjacent_floor(board, board.me()):
        return tron.NORTH

    return closecall_decision(board)

# you do not need to modify this part - much :) ...
if __name__ == "__main__":
    for board in tron.Board.generate():
        tron.move(which_move(board))
