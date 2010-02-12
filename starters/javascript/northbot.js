var tron = require('./tron');

/*
 * Always move north.
 */

function which_move(board) {
    return tron.NORTH;
}

/*
 * You do not need to modify this part.
 */
tron.play(which_move);
