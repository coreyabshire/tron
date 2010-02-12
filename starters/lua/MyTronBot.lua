-- some useful constants.
local WALL, OPEN, ME, ENEMY = string.byte("# 12", 1, 4)
local moves = {N = '1', n = '1', E = '2', e = '2',
   S = '3', s = '3', W = '4', w = '4'}

function play_tron()
   -- Build and return an iterator over successive game states.

   -- Three accessor functions are included in the game state table.
   local function is_wall(self, x, y)
      -- Indexing outside the board returns true.
      return not (self.board[y] and self.board[y][x] == OPEN)
   end

   local function my_xy(self)
      return self.player1[1], self.player1[2]
   end

   local function enemy_xy(self)
      return self.player2[1], self.player2[2]
   end

   local function read_board()
      -- Read and return a board state from standard input
      -- or return nil if input is empty.
      local first_line = io.read()
      if first_line == nil or first_line == "" then return nil end
      local width, height = first_line:match('(%d*) (%d*)')
      width = tonumber(width)
      height = tonumber(height)

      -- Build the map. Find player positions.
      local map = {}
      local player1, player2
      for i = 1, height do
         local line = io.read()
         assert(#line == width, string.format(
            'unexpected line length: %d %s', i, line))
         local tbl = {}
         for i = 1, #line do
            table.insert(tbl, line:byte(i))
         end
         table.insert(map, tbl)
         local p1, p2 = line:find('1'), line:find('2')
         if p1 then player1 = {p1, i} end
         if p2 then player2 = {p2, i} end
      end

      -- Wrap it all up in a table.
      return {board = map, player1 = player1, player2 = player2,
         width = width, height = height, is_wall = is_wall,
         my_xy = my_xy, enemy_xy = enemy_xy}
   end

   -- The function read_board is the iterator.
   return read_board
end

function make_move(move)
   -- Send the move to standard output. Only the first letter counts.
   local initial = string.sub(move, 1, 1)
   if moves[initial] then
      io.write(moves[initial] .. '\n')
      io.flush()
   else
      error('illegal move: ' .. move)
   end
end

-- An example bot. It moves into first open position in NESW, or N by default.
function run_my_bot(game_state)
   local x, y = game_state:my_xy()
   local move
   if not game_state:is_wall(x, y-1) then move = 'NORTH'
   elseif not game_state:is_wall(x+1, y) then move = 'EAST'
   elseif not game_state:is_wall(x, y+1) then move = 'SOUTH'
   elseif not game_state:is_wall(x-1, y) then move = 'WEST'
   else move = 'NORTH' end
   return move
end

-- This loop runs the bot for as long as new boards come in.

-- The game state table contains the following fields:
--   board : table of tables containing either WALL, OPEN, ME, or ENEMY
--   player1, player2: x y pairs of positions, player2 is the enemy bot
--   width, height: the width and height of the board
--   is_wall(x, y): queries whether there is a wall at position
--   my_xy(): returns two values, the x and y coordinates of your bot
--   enemy_xy(): return two values, the x and y coordinates of the enemy bot

for game_state in play_tron() do
   local move = run_my_bot(game_state)
   make_move(move)
end
