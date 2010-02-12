import System.IO
import Data.List
import Debug.Trace

setBuffers = do
    hSetBuffering stdin LineBuffering
    hSetBuffering stdout LineBuffering

main = playBot testBot startingValue

playBot :: ([[Spot]] -> a -> (Move, a)) -> a -> IO ()
playBot bot starting = do
    setBuffers
    interact ((playTurns bot starting) . lines)

readInt :: String -> Int
readInt a = read a

readSpot '#' = Wall
readSpot ' ' = Blank
readSpot '1' = Player
readSpot '2' = Enemy

makeMove North = "1"
makeMove East = "2"
makeMove South = "3"
makeMove West = "4"

playTurns bot pastValue [] = ""
playTurns bot pastValue str = (makeMove move) ++ "\n" ++ playTurns bot history (drop (h+1) str)
    where [w,h] = map readInt (words $ head str)
          tronMap = map (map readSpot) (take h (tail str))
	  (move, history) = bot tronMap pastValue

data Spot = Wall | Blank | Player | Enemy deriving Eq
data Move = North | East | South | West deriving Eq

startingValue = ()

--testBot :: [[Spot]] -> a -> (Move, a)
me tronMap = (maybe 0 id (findIndex (== Player) (head $ filter (any (== Player)) tronMap)), maybe 0 id (findIndex (any (== Player)) tronMap))

canMove move (x,y) tronMap
    | move == North	= if y == 0 then False else (Blank == ((tronMap !! (y-1)) !! x))
    | move == East	= if x+1 == (length (head tronMap)) then False else (Blank == ((tronMap !! y) !! (x+1)))
    | move == South	= if y+1 == (length tronMap) then False else (Blank == ((tronMap !! (y+1)) !! x))
    | move == West	= if x == 0 then False else (Blank == ((tronMap !! y) !! (x-1)))

testBot tronMap b = (head possibleMoves, b)
    where possibleMoves = (filter (\a -> canMove a (me tronMap) tronMap) [North, East, South, West]) ++ [North]
