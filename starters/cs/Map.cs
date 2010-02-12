using System;

class Map
{
  // Stores the width and height of the Tron map.
  private static int width, height; 
  
  // Stores the actual contents of the Tron map.
  private static bool[,] walls;
  
  // Stores the locations of the two players.
  private static Point myLocation, opponentLocation;

  public static int Width()
  {
   return width;
  }
  
  public static int Height()
  {
   return height;
  }
  
  public static bool IsWall(int x, int y) 
  {
	if (x < 0 || y < 0 || x >= width || y >= height) 
	{
	    return true;
	} 
	else 
	{
	    return walls[ x, y ];
	}
  }
  
  // My X location.
  public static int MyX() 
  {
	    return (int)myLocation.X;
  }

  // My Y location.
  public static int MyY() 
  {
	    return (int)myLocation.Y;
  }  
  
  // The opponent's X location.
  public static int OpponentX() 
  {
	    return (int)opponentLocation.X;
  }

  // The opponent's Y location.
  public static int OpponentY() 
  {
	    return (int)opponentLocation.Y;
  }
  
  // Transmit a move to the game engine. 'direction' can be any sort of
  // string that indicates a direction. For example, "north", "North",
  // "n", "N".
  public static void MakeMove(string direction) 
  {
   if (direction.Length <= 0) {
	    Console.Error.WriteLine("FATAL ERROR: empty direction string. You " +
			       "must specify a valid direction in which " +
			       "to move.");
	    Environment.Exit(1);
   }
   string temp = direction.Substring(0, 1).ToUpper(); 
   int firstChar = (int)temp[0];
   
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
	    Console.Error.WriteLine("FATAL ERROR: invalid move string. The string must " +
			       "begin with one of the characters 'N', 'E', 'S', or " +
			       "'W' (not case sensitive).");
	    Environment.Exit(1);
	    break;
	}
  }
  
     // Reads the map from standard input (from the console).
  public static void Initialize() 
  {
   string firstLine = "";
   try {
	     int c;
	     while ((c = Console.Read()) >= 0) 
	     {
		  if (c == '\n') {
		    break;
		  }
		  firstLine += (char)c;
	    }
	} 
	catch (Exception e) 
	{
	    Console.Error.WriteLine("Could not read from stdin.");
	    Environment.Exit(1);
	}
	firstLine = firstLine.Trim();
	if (firstLine.Equals("") || firstLine.Equals("exit")) 
	{
	    Environment.Exit(1); // If we get EOF or "exit" instead of numbers
	                    // on the first line, just exit. Game is over.
	}
	string[] tokens = firstLine.Split(' ');
	if (tokens.Length != 2) {
	    Console.Error.WriteLine("FATAL ERROR: the first line of input should " +
			       "be two integers separated by a space. " +
			       "Instead, got: " + firstLine);
	    Environment.Exit(1);
	}
	try {
	    width = Convert.ToInt32(tokens[0]);
	    height = Convert.ToInt32(tokens[1]);
	} catch (Exception e) {
	    Console.Error.WriteLine("FATAL ERROR: invalid map dimensions: " +
			       firstLine);
	    Environment.Exit(1);
	}
	walls = new bool[width,height];
	bool foundMyLocation = false;
	bool foundHisLocation = false;
	int numSpacesRead = 0;
	int x = 0, y = 0;
	while (y < height) {
	    int c = 0;
	    try {
		 c = Console.Read();
	} catch (Exception e) {
		Console.Error.WriteLine("FATAL ERROR: exception while reading " +
				   "from stdin.");
		Environment.Exit(1);
	}
	if (c < 0) {
		break;
	}
	switch (c) 
	{
	case '\n':
	if (x != width) {
	   Console.Error.WriteLine("Invalid line length: " + x + "(line " + y + ")");
		Environment.Exit(1);
   }
	++y;
	x = 0;
	continue;
	case '\r':
	continue;
	case ' ':
	walls[x,y] = false;
	break;
	case '#':
	walls[x,y] = true;
	break;
	case '1':
	if (foundMyLocation) {
	   Console.Error.WriteLine("FATAL ERROR: found two locations " +
			                     "for player " +
				                  "1 in the map! First location is (" +
				                  myLocation.X + "," +
				                  myLocation.Y +
				                  "), second location is (" + x + "," +
				                  y + ").");
		Environment.Exit(1);
   }
	walls[x,y] = true;
	myLocation = new Point(x, y);
	foundMyLocation = true;
	break;
	case '2':
	if (foundHisLocation) {
	    Console.Error.WriteLine("FATAL ERROR: found two locations for player " +
				       "2 in the map! First location is (" +
				       opponentLocation.X + "," +
				       opponentLocation.Y + "), second location " +
				       "is (" + x + "," + y + ").");
		 Environment.Exit(1);
	}
	walls[x,y] = true;
	opponentLocation = new Point(x, y);
	foundHisLocation = true;
	break;
	default:
	Console.Error.WriteLine("FATAL ERROR: invalid character received. " +
				   "ASCII value = " + c);
   Environment.Exit(1);
   break;
	}
	 ++x;
	 ++numSpacesRead;
	}
	if (numSpacesRead != width * height) {
	    Console.Error.WriteLine("FATAL ERROR: wrong number of spaces in the map. " +
			       "Should be " + (width * height) + ", but only found " +
			       numSpacesRead + " spaces before end of stream.");
	    Environment.Exit(1);
	}
	if (!foundMyLocation) {
	    Console.Error.WriteLine("FATAL ERROR: did not find a location for player 1!");
	    Environment.Exit(1);
	}
	if (!foundHisLocation) {
	    Console.Error.WriteLine("FATAL ERROR: did not find a location for player 2!");
	    Environment.Exit(1);
	}
 }
// Writes the given integer (direction code) to stdout.
    //   1 -- North
    //   2 -- East
    //   3 -- South
    //   4 -- West
 private static void MakeMove(int direction) {
	       Console.WriteLine(direction);
 }
}

class Point{
public int X, Y;
public Point(int x, int y)
{
 X = x;
 Y = y;
}
}
