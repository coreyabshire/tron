# perl Random Bot for Tron

# module containing Tron library functions
use Tron;

#global variable storing the current state of the map
my $_map = new Map();

#Main loop 
#   1. Reads in the board and calls chooseMove to pick a random move
#   2. Selects a move at random (number in range 1 -4)
#   3. Calls Tron::MakeMove on the move to pass it to the game engine
while(1){
    $_map->ReadFromFile();
    $move = chooseMove();
    Tron::MakeMove($move);
}

# generates a random move in the range 1 to 4
# works out what my new position is.
# returns a tuple of ( move, new_X_pos, new_Y_pos )
sub randPos{
    my $move = int(rand(4));
    if( $move == 0){
        return ($move+1 ,$_map->{myPos}->[0], $_map->{myPos}->[1] -1)
    }elsif( $move == 1){
        return ($move+1 ,$_map->{myPos}->[0]+1, $_map->{myPos}->[1])
    }elsif( $move == 2){
        return ($move+1 ,$_map->{myPos}->[0], $_map->{myPos}->[1]+1)
    }elsif( $move == 3){
        return ($move+1 ,$_map->{myPos}->[0]-1, $_map->{myPos}->[1])
    }
}   

# generates a random move
# checks to see if its valid
# if it is valid return the move
# After 10 moves have been generated without finding
# a valid move return the last generated value anyway
# to prevent the bot from timing out if there is no valid
# move
sub chooseMove{
    @newMove = randPos();
    $count = 0; 
    while( ( $_map->IsWall( $newMove[1], $newMove[2] )) && ($count < 10) ){
        @newMove = randPos();
        $count++;
    }
    return $newMove[0];
}

