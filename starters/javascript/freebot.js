var tron = require('./tron');

function which_move(board) {
    var bestcount = -1;
    var bestmove = tron.NORTH;
    var i, j, dir, dest, count, pos, adjacent;
    var moves = board.moves();
    var me = board.me();
    for (i = 0; i < moves.length; i++) {
        dir = moves[i];
        dest = board.rel(dir, me);
        count = 0;
        adjacent = board.adjacent(dest);
        for (j = 0; j < adjacent.length; j++) {
            pos = adjacent[j];
            if (board[pos] == tron.FLOOR) {
                count++;
            }
        }
        if (count > bestcount ) {
            bestcount = count;
            bestmove = dir;
        }
    }
    return bestmove;
}

// you do not need to modify this part
tron.play(which_move);

