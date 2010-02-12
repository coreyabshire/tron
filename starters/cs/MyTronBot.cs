using System;
using System.Collections.Generic;

class MyTronBot{

   public static string MakeMove()
   {
    int x = Map.MyX();
    int y = Map.MyY();
    List<string> validMoves = new List<string>();
    
    if (!Map.IsWall(x,y-1)) {
	    validMoves.Add("North");
	 }
	 if (!Map.IsWall(x+1,y)) {
	    validMoves.Add("East");
	 }
	 if (!Map.IsWall(x,y+1)) {
	    validMoves.Add("South");
	 }
	 if (!Map.IsWall(x-1,y)) {
	    validMoves.Add("West");
	 }
	 if (validMoves.Count == 0) {
	    return "North"; // Hopeless. Might as well go North!
	 } else {
	    Random rand = new Random();
	    int whichMove = rand.Next(validMoves.Count);
	    return validMoves[whichMove];
	 }
   }
   
   public static void Main()
   {
    while (true) {
	    Map.Initialize();
	    Map.MakeMove(MakeMove());
	 }
   }
}
       
