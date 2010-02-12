// MyTronBot.java
// Author: your name goes here

import java.util.*;

class MyTronBot {
    public static String MakeMove() {
	int x = Map.MyX();
	int y = Map.MyY();
	List<String> validMoves = new ArrayList<String>();
	if (!Map.IsWall(x,y-1)) {
	    validMoves.add("North");
	}
	if (!Map.IsWall(x+1,y)) {
	    validMoves.add("East");
	}
	if (!Map.IsWall(x,y+1)) {
	    validMoves.add("South");
	}
	if (!Map.IsWall(x-1,y)) {
	    validMoves.add("West");
	}
	if (validMoves.size() == 0) {
	    return "North"; // Hopeless. Might as well go North!
	} else {
	    Random rand = new Random();
	    int whichMove = rand.nextInt(validMoves.size());
	    return validMoves.get(whichMove);
	}	
    }

    // Ignore this method. It's just doing boring stuff like communicating
    // with the contest tournament engine.
    public static void main(String[] args) {
	while (true) {
	    Map.Initialize();
	    Map.MakeMove(MakeMove());
	}
    }
}
