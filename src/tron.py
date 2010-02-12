# If you want to use this file, make sure to include it in your
# submission. You may modify it and submit the modified copy, or you
# may discard it and roll your own.

"""
Provided code for the Python starter package

See the example bots randbot.py and wallbot.py to get started.
"""

import sys, os

def invalid_input(message):
    """You do not need to call this function directly."""

    print >>sys.stderr, "Invalid input: %s" % message
    sys.exit(1)

def readline(buf):
    """You do not need to call this function directly."""

    while not '\n' in buf:
        tmp = os.read(0, 1024)
        if not tmp:
            break
        buf += tmp

    if not buf.strip():
        return None, buf
    if not '\n' in buf:
        invalid_input('unexpected EOF after "%s"' % buf)

    index = buf.find('\n')
    line = buf[0:index]
    rest = buf[index + 1:]
    return line, rest

class Board(object):
    """The Tron Board.

    The recommended way to use this class is as follows:

        def which_move(board):
            # figure this part out yourself
            return tron.NORTH

        for board in tron.Board.generate():
            tron.move(which_move(board))

    Feel free to add stuff to this class.
    """

    def __init__(self, width, height, board):
        """You do not need to call this method directly."""

        self.board = board
        self.height = height
        self.width = width
        self._me = None
        self._them = None

    @staticmethod
    def read(buf):
        """You do not need to call this method directly."""

        meta, buf = readline(buf)

        if not meta:
            return None, buf

        dim = meta.split(' ')

        if len(dim) != 2:
            invalid_input("expected dimensions on first line")

        try:
            width, height = int(dim[0]), int(dim[1])
        except ValueError:
            invalid_input("malformed dimensions on first line")

        lines = []

        while len(lines) != height:
            line, buf = readline(buf)
            if not line:
                invalid_input("unexpected EOF reading board")
            lines.append(line)

        board = [line[:width] for line in lines]

        if len(board) != height or any(len(board[y]) != width for y in xrange(height)):
            invalid_input("malformed board")

        return Board(width, height, board), buf

    @staticmethod
    def generate():
        """Generate board objects, once per turn.

        This method returns a generator which you may iterate over.
        Make sure to call tron.move() exactly once for every board
        generated, or your bot will not work.
        """

        buf = ''

        while True:
            board, buf = Board.read(buf)
            if not board:
                break
            yield board

        if buf.strip():
            invalid_input("garbage after last board: %s" % buf)

    def __getitem__(self, coords):
        """Retrieve the object at the specified coordinates.

        Use it like this:

            if board[3, 2] == tron.THEM:
                # oh no, the other player is at (3,2)
                run_away()

        Coordinate System:
            The coordinate (y, x) corresponds to row y, column x.
            The top left is (0, 0) and the bottom right is
            (board.height - 1, board.width - 1). Out-of-range
            coordinates are always considered walls.

        Items on the board:
            tron.FLOOR - an empty square
            tron.WALL  - a wall or trail of a bot
            tron.ME    - your bot
            tron.THEM  - the enemy bot
        """

        y, x = coords
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return WALL
        return self.board[y][x]

    def me(self):
        """Finds your position on the board.

        It is always true that board[board.me()] == tron.ME.
        """

        if not self._me:
            self._me = self.find(ME)
        return self._me

    def them(self):
        """Finds the other player's position on the board.

        It is always true that board[board.them()] == tron.THEM.
        """

        if not self._them:
            self._them = self.find(THEM)
        return self._them

    def find(self, obj):
        """You do not need to call this method directly."""

        for y in xrange(self.height):
            for x in xrange(self.width):
                if self[y, x] == obj:
                    return y, x
        raise KeyError("object '%s' is not in the board" % obj)

    def passable(self, coords):
        """Determine if a position in the board is passable.

        You can only safely move onto passable tiles, and only
        floor tiles are passable.
        """

        return self[coords] == FLOOR

    def rel(self, direction, origin=None):
        """Calculate which tile is in the given direction from origin.

        The default origin is you. Therefore, board.rel(tron.NORTH))
        is the tile north of your current position. Similarly,
        board.rel(tron.SOUTH, board.them()) is the tile south of
        the other bot's position.
        """

        if not origin:
            origin = self.me()
        y, x = origin
        if direction == NORTH:
            return y - 1, x
        elif direction == SOUTH:
            return y + 1, x
        elif direction == EAST:
            return y, x + 1
        elif direction == WEST:
            return y, x - 1
        else:
            raise KeyError("not a valid direction: %s" % direction)

    def adjacent(self, origin):
        """Calculate the four tiles that are adjacent to origin.

        Particularly, board.adjacent(board.me()) returns the four
        tiles to which you can move to this turn. This does not
        return tiles diagonally adjacent to origin.
        """

        return [self.rel(dir, origin) for dir in DIRECTIONS]

    def moves(self):
        """Calculate which moves are safe to make this turn.

        Any move in the returned list is a valid move. There
        are two ways moving to one of these tiles could end
        the game:

            1. At the beginning of the following turn,
               there are no valid moves off this tile.
            2. The other player also moves onto this tile,
               and you collide.
        """
        possible = dict((dir, self.rel(dir)) for dir in DIRECTIONS)
        passable = [dir for dir in possible if self.passable(possible[dir])]
        if not passable:
            # it seems we have already lost
            return [NORTH]
        return passable

NORTH = 1
EAST  = 2
SOUTH = 3
WEST  = 4

FLOOR = ' '
WALL  = '#'
ME    = '1'
THEM  = '2'

DIRECTIONS = (NORTH, EAST, SOUTH, WEST)

def move(direction):
    print  direction
    sys.stdout.flush()
