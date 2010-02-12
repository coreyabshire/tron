// Template for your tron bot

var tron = require('./tron');

// Return one element of the array a at random

function randomChoice(a) {
    return a[Math.floor(Math.random() * a.length)];
}

function which_move(board) {

    // fill in your code here. it must return one of the following directions:
    //   tron.NORTH, tron.EAST, tron.SOUTH, tron.WEST

    // For now, choose a legal move randomly.
    // Note that board.moves will produce [NORTH] if there are no
    // legal moves available.

    return randomChoice(board.moves());
}

// you do not need to modify this part
tron.play(which_move);
