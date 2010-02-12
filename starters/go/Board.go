// Board.go

package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

const (
	NORTH = 1 + iota
	EAST
	SOUTH
	WEST
)

var in = bufio.NewReader(os.Stdin)

// Handles the Tron map. Also handles communicating with the Tron game engine.
// You don't need to change anything in this file.

type Board struct {
	// Indicates whether or not each cell in the board is passable.
	is_passable []bool

	// The locations of both players.
	player_one_x, player_one_y int
	player_two_x, player_two_y int

	// Map dimensions.
	map_width, map_height int
}

// Returns the width of the Tron map.
func (b *Board) Width() int { return b.map_width }

// Returns the height of the Tron map.
func (b *Board) Height() int { return b.map_height }

// Returns whether or not the given cell is passable or not. true means it's
// a passible, FALSE means it's not passable. Any spaces that are
// not on the board are deemed to be walls.
func (b *Board) IsPassable(x, y int) bool {
	if x < 0 || x >= b.map_width || y < 0 || y >= b.map_height {
		return false
	}
	return b.is_passable[x+b.map_width*y]
}

// Get my X and Y position. These are zero-based.
func (b *Board) MyXY() (int, int) { return b.player_one_x, b.player_one_y }

// Get the opponent's X and Y position. These are zero-based.
func (b *Board) OpponentXY() (int, int) { return b.player_two_x, b.player_two_y }


// Sends your move to the contest engine. The four possible moves are
//   * 1 -- North. Negative Y direction.
//   * 2 -- East. Positive X direction.
//   * 3 -- South. Positive X direction.
//   * 4 -- West. Negative X direction.
func SendMove(move int) { fmt.Printf("%d\n", move) }

// Load a board from an open file handle. To read from the console, pass
// stdin, which is actually a (FILE*).
//   file_handle -- an open file handle from which to read.
//
// The file should be an ascii file. The first line contains the width and
// height of the board, separated by a space. subsequent lines contain visual
// representations of the rows of the board, using '#' and space characters.
// The starting positions of the two players are indicated by '1' and '2'
// characters. There must be exactly one '1' character and one '2' character
// on the board. For example:
// 6 4
// ######
// #1# 2#
// #   ##
// ######


// Constructs a Board by reading an ASCII representation from the console
// (stdin).
func NewBoard() *Board { return ReadBoardFromFile(in) }

func ReadBoardFromFile(r *bufio.Reader) *Board {
	line, err := r.ReadString('\n')
	if err != nil {
		os.Exit(0)
	}
	coords := strings.Split(strings.TrimSpace(line), " ", 0)
	if len(coords) != 2 {
		panic("Expected two coordinates")
	}
	map_width, err := strconv.Atoi(coords[0])
	if err != nil {
		panic("Could not read width")
	}
	map_height, err := strconv.Atoi(coords[1])
	if err != nil {
		panic("Could not read height")
	}
	is_passable := make([]bool, map_width*map_height)
	player_one_x, player_one_y := -1, -1
	player_two_x, player_two_y := -1, -1
	x := 0
	y := 0
	for y < map_height {
		c, err := r.ReadByte()
		if err != nil {
			panic("Unexpected error while reading array")
		}
		switch c {
		case '\r':
			break
		case '\n':
			if x != map_width {
				panic("x != width in Board_ReadFromStream\n")
			}
			y++
			x = 0
		case '#':
			if x >= map_width {
				panic("x >= width in Board_ReadFromStream\n")
			}
			x++
		case ' ':
			if x >= map_width {
				panic("x >= width in Board_ReadFromStream\n")
			}
			is_passable[x+map_width*y] = true
			x++
		case '1':
			if x >= map_width {
				panic("x >= width in Board_ReadFromStream\n")
			}
			player_one_x, player_one_y = x, y
			x++
		case '2':
			if x >= map_width {
				panic("x >= width in Board_ReadFromStream\n")
			}
			player_two_x, player_two_y = x, y
			x++
		default:
			panic("unexpected character in Board_ReadFromStream")
		}
	}
	return &Board{is_passable, player_one_x, player_one_y,
		player_two_x, player_two_y, map_width, map_height}
}
