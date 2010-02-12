// MyTronBot.go
//
// This is the code file that you will modify in order to create your entry.

package main

func MakeMove(board *Board) int {
	x, y := board.MyXY()
	if board.IsPassable(x, y-1) {
		return NORTH
	}
	if board.IsPassable(x+1, y) {
		return EAST
	}
	if board.IsPassable(x, y+1) {
		return SOUTH
	}
	if board.IsPassable(x-1, y) {
		return WEST
	}
	return NORTH
}

// Ignore this function. It is just handling boring stuff for you, like
// communicating with the Tron tournament engine.
func main() {
	for {
		SendMove(MakeMove(NewBoard()))
	}
}
