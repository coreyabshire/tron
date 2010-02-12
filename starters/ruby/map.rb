# The Map class gets the Tron map from the game engine, and provides some
# methods that allow you to look at it.
#
# You should not change any of the code in this file. It's just here for
# your convenience, to do the boring parts for you.
#
# Copied from the Java example

class Map

	attr_reader :width, :height, :my_position, :opponent_position
	
	def initialize()
	
		@width = -1
		@height = -1
		@walls = []
		@my_position = [-1,-1]
		@opponent_position = [-1,-1]
		
		read_map
		
	end	
	
	def read_map
	
		begin
		
			#read the width and height from the first line
			firstline = $stdin.readline("\n")
			width, height = firstline.split(" ")
			@width = width.to_i
			@height = height.to_i
			
			#check for properly formatted width, height
			if height == 0 or width == 0
				p "OOPS!: invalid map dimensions: " + firstline
				exit(1)
			end
			
			#read the representation of the board
			lines = []
			@height.times do
				lines += [$stdin.readline("\n").strip]
			end
			board = lines.join("")
			
			#get the wall data
			@walls = board.split(//).map{|char| char == " " ? false : true}
			
			#get player starting locations
			p1start = board.index("1").to_i
			p2start = board.index("2").to_i
			
			if board.split(//).select{|char| char == "1"}.size > 1
				p "OOPS!: found more than 1 location for player 1"
				exit(1)
			end
			
			if board.split(//).select{|char| char == "2"}.size > 1
				p "OOPS!: found more than 1 location for player 2"
				exit(1)
			end
			
			p "OOPS!: Cannot find locations." if p1start == nil or p2start == nil
			
			pstartx = p1start % @width
			pstarty = (p1start / @width)
			@my_position = [pstartx, pstarty]
			
			pstartx = p2start % @width
			pstarty = (p2start / @width)
			@opponent_position = [pstartx, pstarty]
					
			
		rescue EOFError => e
			# Got EOF: tournament is finished.
			exit(0)
			
		rescue => e
			p  e
			exit(1)
		end
	
	end
	private :read_map
	
	def each(&proc)
		
		(0..@height-1).each{|y|
			(0..@width-1).each{|x|
				proc[x, y, wall?(x, y)]
			}
		}
		
	end
	
	
	def wall? (x, y)
		return true if x < 0 or y < 0 or x >= @width or y >= @height
		return @walls[x+@width*y]
	end
	
	def to_string()

		out = ""
		counter = 0
				
		@height.times do
			@width.times do
				out += @walls[counter] == true ? "#" : "-"
				counter+=1
			end
			out += "\n"
		end
		
		
		return out
		
	end



	def make_move(direction)
	
		$stdout << ({:NORTH=>1, :SOUTH=>3, :EAST=>2, :WEST=>4}[direction])
		$stdout << "\n"
		$stdout.flush
		
	end
	
end
