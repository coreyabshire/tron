// Map.java
// Author: Jeff Cameron (jeff@jpcameron.com)
//
// The Map class stores the state of a game of Tron.

import java.io.*;

class Map {
    // Stores the width and height of the Tron map.
    private int width, height;

    // Stores the actual contents of the Tron map.
    private boolean[][] walls;

    // Stores the locations of the two players.
    private java.awt.Point playerOneLocation, playerTwoLocation;

    // Constructor. Makes a blank map.
    public Map() {
	// Do nothing.
    }

    // Constructor. Reads the map from a text file.
    public Map(String mapFilename) {
	ReadFromFile(mapFilename);
    }

    // Returns the width of the Tron map.
    public int Width() {
	return width;
    }

    // Returns the height of the Tron map.
    public int Height() {
	return height;
    }

    // Returns whether or not the given space is a wall. The coordinates are
    // zero-based. Spaces outside the Tron map are deemed to be walls.
    public boolean IsWall(int x, int y) {
	if (x < 0 || y < 0 || x >= width || y >= height) {
	    return true;
	} else {
	    return walls[x][y];
	}
    }

    // Player one's X coordinate (zero-based).
    public int PlayerOneX() {
	return (int)playerOneLocation.getX();
    }

    // Player one's Y coordinate (zero-based).
    public int PlayerOneY() {
	return (int)playerOneLocation.getY();
    }

    // Player two's X coordinate (zero-based).
    public int PlayerTwoX() {
	return (int)playerTwoLocation.getX();
    }

    // Player two's Y coordinate (zero-based).
    public int PlayerTwoY() {
	return (int)playerTwoLocation.getY();
    }

    // Outputs an ASCII representation of the map to the given OutputStream.
    public void WriteToStream(OutputStream out) throws Exception {
	try {
	    String firstLine = "" + width + " " + height + "\n";
	    for (int i = 0; i < firstLine.length(); ++i) {
		out.write(firstLine.charAt(i));
	    }
	    for (int y = 0; y < height; ++y) {
		for (int x = 0; x < width; ++x) {
		    if (PlayerOneX() == x && PlayerOneY() == y) {
			out.write('1');
		    } else if (PlayerTwoX() == x && PlayerTwoY() == y) {
			out.write('2');
		} else {
			out.write(walls[x][y] ? '#' : ' ');
		    }
		}
		out.write('\n');
	    }
	    out.flush();
	} catch (Exception e) {
	    System.err.println("FATAL ERROR: failed to write to stream: " + e);
	    throw new Exception("One of the programs crashed!");
	}
    }

    // Outputs an ASCII representation of the map to the console.
    public void Print() {
	System.out.println("" + width + " " + height);
	for (int y = 0; y < height; ++y) {
	    for (int x = 0; x < width; ++x) {
		if (PlayerOneX() == x && PlayerOneY() == y) {
		    System.out.write('1');
		} else if (PlayerTwoX() == x && PlayerTwoY() == y) {
		    System.out.write('2');
		} else {
		    System.out.write(walls[x][y] ? '#' : ' ');
		}
	    }
	    System.out.write('\n');
	}
	System.out.flush();
    }

    // Reads the map from a text file.
    public void ReadFromFile(String filename) {
	BufferedReader in = null;
	try {
	    in = new BufferedReader(new FileReader(filename));
	    String firstLine = "";
	    try {
		int c;
		while ((c = in.read()) >= 0) {
		    if (c == '\n') {
			break;
		    }
		    firstLine += (char)c;
		}
	    } catch (Exception e) {
		System.err.println("Could not read from stdin.");
		System.exit(1);
	    }
	    String[] tokens = firstLine.split(" ");
	    if (tokens.length != 2) {
		System.err.println("FATAL ERROR: the first line of input " +
				   "should be two integers separated by a " +
				   "space. Instead, got: " + firstLine);
		System.exit(1);
	    }
	    try {
		width = Integer.parseInt(tokens[0]);
		height = Integer.parseInt(tokens[1]);
	    } catch (Exception e) {
		System.err.println("FATAL ERROR: invalid map dimensions: " +
				   firstLine);
		System.exit(1);
	    }
	    walls = new boolean[width][height];
	    boolean foundMyLocation = false;
	    boolean foundHisLocation = false;
	    int numSpacesRead = 0;
	    int x = 0, y = 0;
	    while (x < width && y < height) {
		int c = 0;
		try {
		    c = in.read();
		} catch (Exception e) {
		    System.err.println("FATAL ERROR: exception while reading " +
				       "from stdin.");
		    System.exit(1);
		}
		if (c < 0) {
		    break;
		}
		switch (c) {
		case '\n':
		case '\r':
		    continue;
		case ' ':
		    walls[x][y] = false;
		    break;
		case '#':
		    walls[x][y] = true;
		    break;
		case '1':
		    if (foundMyLocation) {
			System.err.println("FATAL ERROR: found two locations " +
					   "for player 1 in the map! First " +
					   "location is (" +
					   playerOneLocation.getX() +
					   "," + playerOneLocation.getY() +
					   "), second location is (" + x + "," +
					   y + ").");
			System.exit(1);
		    }
		    walls[x][y] = true;
		    playerOneLocation = new java.awt.Point(x, y);
		    foundMyLocation = true;
		    break;
		case '2':
		    if (foundHisLocation) {
			System.err.println("FATAL ERROR: found two locations " +
					   "for player 2 in the map! First " +
					   "location is (" +
					   playerTwoLocation.getX() + "," +
					   playerTwoLocation.getY() + "), " +
					   "second location is (" +
					   x + "," + y + ").");
			System.exit(1);
		    }
		    walls[x][y] = true;
		    playerTwoLocation = new java.awt.Point(x, y);
		    foundHisLocation = true;
		    break;
		default:
		    System.err.println("FATAL ERROR: invalid character " +
				       "received. ASCII value = " + c);
		    System.exit(1);
		}
		++x;
		++numSpacesRead;
		if (x >= width) {
		    ++y;
		    x = 0;
		}
	    }
	    if (numSpacesRead != width * height) {
		System.err.println("FATAL ERROR: wrong number of spaces in " +
				   "the map. Should be " + (width * height) +
				   ", but only found " + numSpacesRead +
				   " spaces before end of stream.");
		System.exit(1);
	    }
	    if (!foundMyLocation) {
		System.err.println("FATAL ERROR: did not find a location " +
				   "for player 1!");
		System.exit(1);
	    }
	    if (!foundHisLocation) {
		System.err.println("FATAL ERROR: did not find a location " +
				   "for player 2!");
		System.exit(1);
	    }
	} catch (Exception e) {
	    // Do nothing.
	} finally {
	    if (in != null) {
		try {
		    in.close();
		} catch (Exception e) {
		    // Do nothing.
		}
	    }
	}
    }

    // Moves player 1, given a move code returned by a client program.
    // If everything goes well, returns 0. If the player crashes, -1 is returned.
    public int MovePlayerOne(int move) {
	int x = PlayerOneX();
	int y = PlayerOneY();
	walls[x][y] = true;
	switch (move) {
	case 1:
	    playerOneLocation = new java.awt.Point(x, y-1);
	    break;
	case 2:
	    playerOneLocation = new java.awt.Point(x+1, y);
	    break;
	case 3:
	    playerOneLocation = new java.awt.Point(x, y+1);
	    break;
	case 4:
	    playerOneLocation = new java.awt.Point(x-1, y);
	    break;
	default:
	    return -1;
	}
	x = PlayerOneX();
	y = PlayerOneY();
	if (IsWall(x, y)) {
	    return -1;
	} else {
	    return 0;
	}
    }

    // Moves player 2, given a move code returned by a client program.
    // If everything goes well, returns 0. If the player crashes, -1 is returned.
    public int MovePlayerTwo(int move) {
	int x = PlayerTwoX();
	int y = PlayerTwoY();
	walls[x][y] = true;
	switch (move) {
	case 1:
	    playerTwoLocation = new java.awt.Point(x, y-1);
	    break;
	case 2:
	    playerTwoLocation = new java.awt.Point(x+1, y);
	    break;
	case 3:
	    playerTwoLocation = new java.awt.Point(x, y+1);
	    break;
	case 4:
	    playerTwoLocation = new java.awt.Point(x-1, y);
	    break;
	default:
	    return -1;
	}
	x = PlayerTwoX();
	y = PlayerTwoY();
	if (IsWall(x, y)) {
	    return -1;
	} else {
	    return 0;
	}
    }

    public Map SwapPlayers() {
	Map map = new Map();
	map.walls = this.walls;
	map.width = this.width;
	map.height = this.height;
	map.playerOneLocation = this.playerTwoLocation;
	map.playerTwoLocation = this.playerOneLocation;
	return map;
    }
}
