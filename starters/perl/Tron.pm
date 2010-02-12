# function overview
# Tron Package
# MakeMove( direction ) -- takes a direction and writes it to the tron game
#                          game engine using the standard error stream
#
# Map object
# new Map() -- instantiate map object
# Member Functions
# ReadFromFile() -- map member function parses incoming map and
#                   populates map object state, must be called at the
#                   begining of each turn.
# IsWall(x, y) -- returns true if position x,y is a wall

#main Tron Communications package
package Tron;
use strict;
use warnings;
our $VERSION = 1.00;

#auto flush buffers
$|++;

# takes your move and sends it to the contest engine.
# Your Move can make 4 possible moves
#   * NORTH -- Negative Y direction
#   * EAST  -- Positive X direction
#   * SOUTH -- Positive Y direction
#   * WEST  -- Negative X direction
# string Matchings are case insentive
# You can also send and integer in the range 1 through 4
# Where the corresponding directions are
#  * 1 -- NORTH
#  * 2 -- EAST
#  * 3 -- SOUTH
#  * 4 -- WEST
# Sending an invalid string or number will result in a crash

sub MakeMove{
    my ($direction) = @_;
    if( not defined $direction ){
        die "need to provide a direction to makeMove\n";
    }
    if( $direction =~ /^[1-4]$/ ){
        print   "$direction\n";
    }elsif( $direction =~ /NORTH/i){
        print   "1\n";
    }elsif( $direction =~ /SOUTH/i ){
        print   "3\n";
    }elsif( $direction =~ /EAST/i ){
        print "2\n";
    }elsif( $direction =~ /WEST/i ){
        print   "4\n";
    }else{
        die "invalid move $direction\n";
    }
}

# definition of Map object storing game state
package Map;

# instantiate a new Map object
# returns a Map class with members width and height set to zero
# the map state and player positions will be populated in the
# ReadFromFile method
#
# The final state of the Map object is
#   $self = {
#       width       => board width
#       height      => board height
#       myPos       => ( x, y )
#       opponentPos => ( x, y )
#       _map => ( list of rows of the board any entry which is not ' '
#                is considered to be a wall)
#       }
#
#   example map
#    X ->
#   ##########
# Y #1       #
# | #        #
# v #       2#
#   #        #
#   ##########
#
#   You will access the player positions though the
#   $self->{myPos} and $self->{opponentPos} accessors
#
#   Wall positions are best accessed through the IsWall member function
#
#   If you wish to store old states you can create a new Map object
#   and copy the _map, opponentPos and myPos reference onto the new object
sub new{
    my $class = shift;
    my %self = (
        width => 0,
        height => 0,
        myPos => [ 0, 0 ],
        opponentPos => [ 0, 0],
        _map => [],
        );

    bless( \%self, $class);
    return \%self;
}

# Parses an incoming map file and overwrite the map data
# in the current Map object with new Map array, player tuples
#
# IMPORTANT: It is critical that you call this function at the
#            begining of each turn to bring your game state up
#            to see the result of the previous turns moves
#
# Once the function has been called all data in the Map object
# will be lost if not already copied else where.
#
# ReadFromFile takes an optional File name but defaults
# to reading from the standard input stream, Your submissions will
# want to leave it reading from the standard in.  However, passing
# in files could be useful for testing specific scenarios.
#
# Map file consists of 1 line with two ints specifiying x and y dimentions
# followed by y lines of x characters representing the map.  The players
# position is represented by a 1 and the oponent by a 2
# example
#    6 4
#    ######
#    #1# 2#
#    #   ##
#    ######
sub ReadFromFile {
    my ($self, $file) = @_;
    my $fh;
#check to see if an input file has been specified
    if( defined $file){
        open $fh, "<", $file;
    }else{
        $fh = *STDIN;
    }

#reset self hash
    $self->{_map} = [];
    $self->{myPos} = [];
    $self->{opponentPos} = [];
    $self->{width} = 0;
    $self->{height} = 0;

    my $line = <$fh>;

    if (not defined $line) {
        exit 0;
    }

    chomp $line;

    ($self->{width}, $self->{height})= split(/ /, $line );
    my $row = 0;

#keep reading while we have not seen all the expected rows
    while(  ($row < $self->{height})){
        $line = <$fh> ;
        chomp($line);
#break the string into a list of characters and add it to the
# end of the map
        push( @{ $self->{_map}->[$row] }, split(//, $line ) );

        if( length($line) != $self->{width} ){
            die "invalid line width on line $row, length is ".length($line)." expected $self->{width}\n";
        }
#check to see if the players position is on this line
        if( index( $line, '1') > 0 ){
            if( @{$self->{myPos}} ){
                die "found a second definition of my position on $row\n";
            }
            $self->{myPos}->[0] = index( $line, '1');
            $self->{myPos}->[1] = $row;  
        }
#check to see if the opponents position is on this line
        if( index( $line, '2' ) > 0 ){
            if( @{$self->{opponentPos}} ){
                die "found a second definition of opponents position on $row\n";
            }
            $self->{opponentPos}->[0] = index( $line, '2');
            $self->{opponentPos}->[1] = $row;
        }
        ++$row;
    }
    if( $row != $self->{height} ){
        die "wrong number of row in map, expected $self->{height}, got $row\n";
    }

}

# takes an X,Y coordinte and returns true if is the location
# of a wall, else returns false.  
#
# The Fuction will perform range checks to ensure that
# provided coordinates are valid board positions
# and will print warnings if the coordinates are not.
# Invalid parameters will generally result a true
# value being returned. 
# 
# The function will do range checks

sub IsWall{
    my ($self, $x, $y) = @_;
#check for invalid parameters
    if(  not defined $self ){
        print  STDERR "self is undefined.  This function needs to be called on a map object\n";
        return 1;
    }elsif( $#_ != 2 ){
        die "called IsWall without an x y coordinate\n";
    }
    if( $x < 0 || $x >= $self->{width} ){
        print STDERR "x value $x is out of range, board has width of $self->{width}\n";
        return 1;
    }
    if( $y < 0 || $y >= $self->{height} ){
        print STDERR "y value $y is out of range.  board has a height of $self->{height}\n";
        return 1;
    }

    return ($self->{_map}->[$y][$x] ne ' ');

}

1; #module must return a true value when included
