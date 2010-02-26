#!/usr/bin/python

"""TronBot implementation by Corey Abshire."""

import optparse, logging, time, cProfile, tron
from tronutils import *
from tronmoves import *


argp = optparse.OptionParser()
argp.add_option("--log", default=None)
argp.add_option("--hurry", type="float", default=0.1)
argp.add_option("--profile", default=None)
argp.add_option("--time-limit", type="float", default=1.0)
argp.add_option("--considered-near", type="int", default=6)
argp.add_option("--same-dist-limit", type="int", default=5)


def which_move(board, start_time, same_dist):
    "Determine which move to make given the current board."

    # If I don't have any legal moves, its not even worth trying
    # one of the other strategies. This is done here to support
    # calling the other strategies from the command line.
    if not adjacent(board, board.me(), is_floor):
        logging.debug('no legal moves remaining; bypassign strategy')
        return surrender_move(board)

    # Calculate the shortest path from me to them. This is useful
    # for a couple of different strategies, plus, it tells me if
    # we are still connected or not.
    try:
        path_to_them = shortest_path(board, board.me(), board.them())
    except KeyError:
        path_to_them = None

    # If we're no longer connected, we do not need to consider
    # the opponents moves at all. Instead, we should just focus
    # on using as much of the board as possible. The best strategy
    # I have for that at the moment is the most open strategy.
    if not path_to_them:
        logging.debug('not connected, so using most open')
        return most_open_move(board, tron.DIRECTIONS)

    # If we're near enough that minimax (with alpha-beta pruning)
    # is practical, then we should use that. It should return the
    # absolute best move if it can see far enough ahead in terms
    # of board space.
    finish_by = start_time + config.time_limit - config.hurry
    if moves_between(path_to_them) <= config.considered_near:
        logging.debug('within threshold, so using alphabeta')
        return minimax_move(board, finish_by)

    # If there is a set of a few points that me and my opponent
    # are an equal distance from, then the are probably pretty
    # important on the board (such as for 'u' and for 'joust').
    # As such, go target those points. Once those points have
    # been achieved, just try to fill in the remaining space.
    # (I still have concerns about this one. Needs work.)
    if 1 <= len(same_dist) <= config.same_dist_limit:
        logging.debug('targeting first same dist tile')
        return same_dist_move(board, same_dist, tron.DIRECTIONS)

    # If all else fails, lets just charge the opponent by taking
    # the shortest path to them and try to let the minimax with
    # alpha-beta pruning get us a victory.
    logging.debug('using shortest path to opponent')
    return follow_path_move(board, path_to_them)


def mainloop():
    "The main TronBot game loop."

    move_number = 1
    first_move = True

    # Just keep iterating. The generator stops when the game is over.
    for board in tron.Board.generate():

        # Record exactly when we read the board to calculate time remaining.
        start_time = time.time()

        # Some statistics we need are only available on the first move.
        if first_move:
            same_dist = same_distance(board, board.me(), board.them())
            first_move = False

        logging.debug('move %d', move_number)

        # Call the configured strategy to determine the best move.
        # Then update the local state object and log a few details.
        # Finally, submit the move to the engine using the API.
        my_move = which_move(board, start_time, same_dist)

        # Log the move summary and elapsed time.
        elapsed = time.time() - start_time
        logging.debug('chose %s (took %0.3fs)', DIR_NAMES[my_move], elapsed)

        # Submit the move back to the game engine and move to the next.
        tron.move(my_move)
        move_number += 1


def enable_logging(logfile, level=logging.DEBUG):
    "Enable logging to the specified logfile."
    logging.basicConfig(filename=logfile, level=level, filemode='w')


if __name__ == "__main__":
    config, args = argp.parse_args()
    
    if config.log:
        enable_logging(config.log)

    logging.debug('config: %s', config)
        
    if config.profile:
        cProfile.run('mainloop()', config.profile)
    else:
        mainloop()

else:
    config, args = argp.parse_args() 
