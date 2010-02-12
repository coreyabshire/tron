# MyTronBot
# Author: <name>

require "map.rb"
require "printing.rb"

#NB: This AI communicates with the contest engine over
#standard out. printing.rb contains convenience methods
#which overload the puts, p and print methods such that
#they output to standard error instead.

class TronBot

	def makemove(map)
	
	
		x, y = map.my_position
		
		valid_moves = []
		valid_moves << :NORTH if not map.wall?(x, y-1)
		valid_moves << :SOUTH if not map.wall?(x, y+1)
		valid_moves << :WEST  if not map.wall?(x-1, y)
		valid_moves << :EAST  if not map.wall?(x+1, y)
		
		if(valid_moves.size == 0)
			map.make_move( :NORTH )
		else
			move = valid_moves[rand(valid_moves.size)]
			# uncomment to show move
			# puts move
			map.make_move( move )
		end
	
	end
	
	

	def initialize
	
		while(true)
		
			map = Map.new()
			makemove(map)
		
		end
	
	end
	
end

TronBot.new()
