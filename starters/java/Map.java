// The Map class gets the Tron map from the game engine, and provides some
// methods that allow you to look at it.
//
// You should not change any of the code in this file. It's just here for
// your convenience, to do the boring parts for you.

import java.io.*;

class Map {
    // Stores the width and height of the Tron map.
    private static int width, height;

    // Stores the actual contents of the Tron map.
    private static boolean[][] walls;

    // Stores the locations of the two players.
    private static java.awt.Point myLocation, opponentLocation;

    // Returns the width of the Tron map.
    public static int Width() {
	return width;
    }

    // Returns the height of the Tron map.
    public static int Height() {
	return height;
    }

    // Returns whether or not the given space is a wall. The coordinates are
    // zero-based. Spaces outside the Tron map are deemed to be walls.
    public static boolean IsWall(int x, int y) {
	if (x < 0 || y < 0 || x >= width || y >= height) {
	    return true;
	} else {
	    return walls[x][y];
	}
    }

    // My X location.
    public static int MyX() {
	return (int)myLocation.getX();
    }

    // My Y location.
    public static int MyY() {
	return (int)myLocation.getY();
    }

    // The opponent's X location.
    public static int OpponentX() {
	return (int)opponentLocation.getX();
    }

    // The opponent's Y location.
    public static int OpponentY() {
	return (int)opponentLocation.getY();
    }

    // Transmit a move to the game engine. 'direction' can be any sort of
    // string that indicates a direction. For example, "north", "North",
    // "n", "N".
    public static void MakeMove(String direction) {
	if (direction.length() <= 0) {
	    System.err.println("FATAL ERROR: empty direction string. You " +
			       "must specify a valid direction in which " +
			       "to move.");
	    System.exit(1);
	}
	int firstChar = (int)direction.substring(0, 1).toUpperCase().charAt(0);
	switch (firstChar) {
	case 'N':
	    MakeMove(1);
	    break;
	case 'E':
	    MakeMove(2);
	    break;
	case 'S':
	    MakeMove(3);
	    break;
	case 'W':
	    MakeMove(4);
	    break;
	default:
	    System.err.println("FATAL ERROR: invalid move string. The string must " +
			       "begin with one of the characters 'N', 'E', 'S', or " +
			       "'W' (not case sensitive).");
	    System.exit(1);
	    break;
	}
    }

    // Reads the map from standard input (from the console).
    public static void Initialize() {
	String firstLine = "";
	try {
	    int c;
	    while ((c = System.in.read()) >= 0) {
		if (c == '\n') {
		    break;
		}
		firstLine += (char)c;
	    }
	} catch (Exception e) {
	    System.err.println("Could not read from stdin.");
	    System.out.flush();
	    System.exit(1);
	}
	firstLine = firstLine.trim();
	if (firstLine.equals("") || firstLine.equals("exit")) {
	    System.exit(1); // If we get EOF or "exit" instead of numbers
	                    // on the first line, just exit. Game is over.
	}
	String[] tokens = firstLine.split(" ");
	if (tokens.length != 2) {
	    System.err.println("FATAL ERROR: the first line of input should " +
			       "be two integers separated by a space. " +
			       "Instead, got: " + firstLine);
	    System.err.flush();
	    System.exit(1);
	}
	try {
	    width = Integer.parseInt(tokens[0]);
	    height = Integer.parseInt(tokens[1]);
	} catch (Exception e) {
	    System.err.println("FATAL ERROR: invalid map dimensions: " +
			       firstLine);
	    System.err.flush();
	    System.exit(1);
	}
	walls = new boolean[width][height];
	boolean foundMyLocation = false;
	boolean foundHisLocation = false;
	int numSpacesRead = 0;
	int x = 0, y = 0;
	while (y < height) {
	    int c = 0;
	    try {
		c = System.in.read();
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
		if (x != width) {
		    System.err.println("Invalid line length: " + x +
				       "(line " + y + ")");
		    System.exit(1);
		}
		++y;
		x = 0;
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
				       "for player " +
				       "1 in the map! First location is (" +
				       myLocation.getX() + "," +
				       myLocation.getY() +
				       "), second location is (" + x + "," +
				       y + ").");
		    System.exit(1);
		}
		walls[x][y] = true;
		myLocation = new java.awt.Point(x, y);
		foundMyLocation = true;
		break;
	    case '2':
		if (foundHisLocation) {
		    System.err.println("FATAL ERROR: found two locations for player " +
				       "2 in the map! First location is (" +
				       opponentLocation.getX() + "," +
				       opponentLocation.getY() + "), second location " +
				       "is (" + x + "," + y + ").");
		    System.exit(1);
		}
		walls[x][y] = true;
		opponentLocation = new java.awt.Point(x, y);
		foundHisLocation = true;
		break;
	    default:
		System.err.println("FATAL ERROR: invalid character received. " +
				   "ASCII value = " + c);
		System.exit(1);
	    }
	    ++x;
	    ++numSpacesRead;
	}
	if (numSpacesRead != width * height) {
	    System.err.println("FATAL ERROR: wrong number of spaces in the map. " +
			       "Should be " + (width * height) + ", but only found " +
			       numSpacesRead + " spaces before end of stream.");
	    System.exit(1);
	}
	if (!foundMyLocation) {
	    System.err.println("FATAL ERROR: did not find a location for player 1!");
	    System.exit(1);
	}
	if (!foundHisLocation) {
	    System.err.println("FATAL ERROR: did not find a location for player 2!");
	    System.exit(1);
	}
    }

    // Writes the given integer (direction code) to stdout.
    //   1 -- North
    //   2 -- East
    //   3 -- South
    //   4 -- West
    private static void MakeMove(int direction) {
	System.out.println(direction);
	System.out.flush();
    }
}
