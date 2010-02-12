// Tron.java
// Author: Jeff Cameron (jeff@jpcameron.com)
//
// A program that runs a game of Tron between two bots.

class Tron {
    public static void main(String[] args) {
	if (args.length < 3) {
	    System.err.println("FATAL ERROR: not enough command-line " +
			       "arguments.\nUSAGE: java -jar Tron.jar " +
			       "map-filename " +
			       "command-to-start-player-one " +
			       "command-to-start-player-two " +
			       "[delay-between-turns] [max-move-time]");
	    System.exit(1);
	}
	String mapFilename = args[0];
	String playerOneCommand = args[1];
	String playerTwoCommand = args[2];
	int delayBetweenTurns = 1;
	if (args.length >= 4) {
	    delayBetweenTurns = Integer.parseInt(args[3]);
	}
	int maxMoveTime = 3;
	if (args.length >= 5) {
	    maxMoveTime = Integer.parseInt(args[4]);
	}
	Comm playerOne = null;
	Comm playerTwo = null;
	try {
	    playerOne = new Comm(playerOneCommand);
	} catch (Exception e) {
	    System.err.println("Problem while starting program 1: " + e);
	    System.exit(1);
	}
	try {
	    playerTwo = new Comm(playerTwoCommand);
	} catch (Exception e) {
	    System.err.println("Problem while starting program 2: " + e);
	    System.exit(1);
	}
	Map map = new Map(mapFilename);
	map.Print();
	while (true) {
	    try {
		Thread.sleep(delayBetweenTurns * 1000);
	    } catch (Exception e) {
		// Do nothing.
	    }
	    int playerOneMove = playerOne.GetMove(map, maxMoveTime);
	    int playerTwoMove = playerTwo.GetMove(map.SwapPlayers(),
						  maxMoveTime);
	    playerOneMove = map.MovePlayerOne(playerOneMove);
	    playerTwoMove = map.MovePlayerTwo(playerTwoMove);
	    if (map.PlayerOneX() == map.PlayerTwoX() &&
		map.PlayerOneY() == map.PlayerTwoY()) {
		System.out.println("Players collided. Draw!");
		break;
	    }
	    if (playerOneMove < 0 && playerTwoMove < 0) {
		System.out.println("Both players crashed. Draw!");
		break;
	    }
	    if (playerOneMove < 0) {
		System.out.println("Player Two Wins!");
		break;
	    }
	    if (playerTwoMove < 0) {
		System.out.println("Player One Wins!");
		break;
	    }
	    map.Print();
	}
    }
}
