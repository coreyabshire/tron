/* Follows the wall */

var tron = require('./tron');

/* Fisher-Yates shuffle
 */
function randomShuffle(a) {
    var i, j, temp;
    var len = a.length;
    for (i = len-1; i >= 1; i--) {
        j = Math.floor(Math.random() * i);
        temp = a[i];
        a[i] = a[j];
        a[j] = temp;
    }
}

// preference order of directions
var ORDER = tron.DIRECTIONS.slice(0); // Clone directions
randomShuffle(ORDER);

// if any wall adjacent to the location
function adjacentToWall(board, location) {
    var adj = board.adjacent(location);
    var j, pos;
    for (j = 0; j < adj.length; j++) {
        pos = adj[j];
        if (board.at(pos) == tron.WALL) {
            return true;
        }
    }
    return false;
}

function which_move(board) {
    var decision = board.moves()[0];
    var i, dir, dest;
    var me = board.me();

    for (i = 0; i < ORDER.length; i++) {
        dir = ORDER[i];

        // where we will end up if we move this way
        dest = board.rel(dir, me);

        // destination is passable?
        if (! board.passable(dest) ) {
            continue;
        }

        if (adjacentToWall(board, dest)) {
            decision = dir;
            break;
        }
    }
    return decision;
}

// you do not need to modify this part
tron.play(which_move);

