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
    
