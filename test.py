import tron, MyTronBot, unittest

#_____________________________________________________________________
# Board Helper Tests
#

class BoardHelperTestCase(unittest.TestCase):
    
    def test_read_board(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertEqual(board.width, 6, 'incorrect width')
        self.assertEqual(board.height, 4, 'incorrect height')
        self.assertEqual(board[1,1], tron.ME, 'expected ME')
        self.assertEqual(board[1,4], tron.THEM, 'expected THEM')
        self.assertEqual(board.me(), (1,1))
        self.assertEqual(board.them(), (1,4))
        self.assertEqual(board[1,2], tron.WALL, 'expected WALL')
        self.assertEqual(board[1,3], tron.FLOOR, 'expected FLOOR')

    def test_adjacent_nonwall(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertEqual(MyTronBot.adjacent_floor(board, board.me()), [(2,1)])
        self.assertEqual(MyTronBot.adjacent_floor(board, board.them()), [(1,3)])
        
    def test_adjacent_floor(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertEqual(MyTronBot.adjacent_floor(board, board.me()), [(2,1)])
        self.assertEqual(MyTronBot.adjacent_floor(board, board.them()), [(1,3)])

    def test_valid_coords(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertTrue(MyTronBot.valid_coords(board, (0,0)))
        self.assertTrue(MyTronBot.valid_coords(board, (0,5)))
        self.assertTrue(MyTronBot.valid_coords(board, (2,2)))
        self.assertTrue(MyTronBot.valid_coords(board, (3,0)))
        self.assertTrue(MyTronBot.valid_coords(board, (3,5)))
        self.assertFalse(MyTronBot.valid_coords(board, (-1,-1)))
        self.assertFalse(MyTronBot.valid_coords(board, (-1,0)))
        self.assertFalse(MyTronBot.valid_coords(board, (0,-1)))
        self.assertFalse(MyTronBot.valid_coords(board, (0,6)))
        self.assertFalse(MyTronBot.valid_coords(board, (6,6)))
        self.assertFalse(MyTronBot.valid_coords(board, (4,0)))

    def test_tile_is_a(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        is_wall = MyTronBot.tile_is_a(tron.WALL)
        is_floor = MyTronBot.tile_is_a(tron.FLOOR)
        known_wall = [(0,0),(0,5),(3,0),(3,5)]
        known_floor = [(2,1),(2,2),(2,3),(1,3)]
        for coords in known_wall:
            self.assertTrue(is_wall(board, coords))
            self.assertFalse(is_floor(board, coords))
        for coords in known_floor:
            self.assertFalse(is_wall(board, coords))
            self.assertTrue(is_floor(board, coords))
    
    def test_invert(self):
        true_fn = lambda: True
        false_fn = lambda: False
        inverse_true_fn = MyTronBot.invert(true_fn)
        inverse_false_fn = MyTronBot.invert(false_fn)
        self.assertTrue(true_fn())
        self.assertFalse(false_fn())
        self.assertFalse(inverse_true_fn())
        self.assertTrue(inverse_false_fn())

    def test_is_wall(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertTrue(MyTronBot.is_wall(board, (0,0)))
        self.assertFalse(MyTronBot.is_wall(board, (1,1)))
        self.assertFalse(MyTronBot.is_wall(board, (2,1)))

    def test_is_floor(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertFalse(MyTronBot.is_floor(board, (0,0)))
        self.assertFalse(MyTronBot.is_floor(board, (1,1)))
        self.assertTrue(MyTronBot.is_floor(board, (2,1)))

    def test_is_nonwall(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertFalse(MyTronBot.is_nonwall(board, (0,0)))
        self.assertTrue(MyTronBot.is_nonwall(board, (1,1)))
        self.assertTrue(MyTronBot.is_nonwall(board, (2,1)))

    def test_tiles_matching(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        wall  = MyTronBot.tiles_matching(board, MyTronBot.is_wall)
        floor = MyTronBot.tiles_matching(board, MyTronBot.is_floor)
        self.assertEquals(len(wall ), 18)
        self.assertEquals(len(floor), 4)
        
    def test_adjacent(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        coords = board.me()
        wall = MyTronBot.adjacent(board, coords, MyTronBot.is_wall)
        floor = MyTronBot.adjacent(board, coords, MyTronBot.is_floor)
        self.assertEquals(len(wall), 3)
        self.assertEquals(len(floor), 1)

    def test_surrounding_offset_array(self):
        soa = MyTronBot.surrounding_offset_array()
        self.assertEqual(len(soa), 9)
        self.assertEqual(soa[0], (-1,-1))
        self.assertEqual(soa[4], (0,0))
        self.assertEqual(soa[8], (1,1))

    def test_offset(self):
        self.assertEquals(MyTronBot.offset((1,1),(1,1)),(2,2))
        self.assertEquals(MyTronBot.offset((3,4),(-1,-1)),(2,3))
        self.assertEquals(MyTronBot.offset((3,2),(1,0)),(4,2))
    
    def test_surrounding_nonfloor(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertEquals(len(MyTronBot.surrounding_nonfloor(board,(1,2))),5)

    def test_move_made(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        fn = lambda a,b: MyTronBot.move_made(board, a, b)
        self.assertEquals(fn((1,1),(2,1)), tron.SOUTH)
        self.assertEquals(fn((2,1),(1,1)), tron.NORTH)
        self.assertEquals(fn((1,1),(1,2)), tron.EAST)
        self.assertEquals(fn((1,2),(1,1)), tron.WEST)
        
    def test_is_game_over(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertFalse(MyTronBot.is_game_over(board))
        board.board[2] = '######'
        self.assertTrue(MyTronBot.is_game_over(board))
        
    def test_win_lose_or_draw(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertEqual(MyTronBot.win_lose_or_draw(board, tron.ME), -0.5)
        self.assertEqual(MyTronBot.win_lose_or_draw(board, tron.THEM), -0.5)
        board.board[2] = '######'
        self.assertEqual(MyTronBot.win_lose_or_draw(board, tron.ME), -1)
        self.assertEqual(MyTronBot.win_lose_or_draw(board, tron.THEM), 1)

    def test_set_char(self):
        self.assertEqual(MyTronBot.set_char('abc',0,'d'), 'dbc')
        self.assertEqual(MyTronBot.set_char('abc',1,'d'), 'adc')
        self.assertEqual(MyTronBot.set_char('abc',2,'d'), 'abd')

    def test_try_move(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertEquals(board.me(), (1,1))
        self.assertEquals(board.them(), (1,4))
        self.assertEquals(board[2,1], tron.FLOOR, 'should be FLOOR')
        next = MyTronBot.try_move(board, tron.ME, tron.SOUTH)
        self.assertEquals(next.me(), (2,1), 'should have changed')
        self.assertEquals(next.them(), (1,4), 'should not have changed')
        self.assertEquals(next[1,1], tron.WALL, 'should now be WALL')
        self.assertEquals(board.me(), (1,1), 'should not have changed')
        self.assertEquals(board.them(), (1,4), 'should not have changed')
        self.assertEquals(board[2,1], tron.FLOOR, 'should still be FLOOR')

    def test_opponent(self):
        self.assertEquals(MyTronBot.opponent(tron.ME), tron.THEM)
        self.assertEquals(MyTronBot.opponent(tron.THEM), tron.ME)

    def test_count_around(self):
        board = MyTronBot.read_board('maps/u.txt')
        self.assertEquals(MyTronBot.count_around(board, board.me()), 97)
        board = MyTronBot.read_board('maps/ring.txt')
        self.assertEquals(MyTronBot.count_around(board, board.me()), 131)
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertEquals(MyTronBot.count_around(board, board.me()), 4)

#_____________________________________________________________________
# AIMA Alpha-Beta Interface Test
#

class AlphaBetaTestCase(unittest.TestCase):

    def setUp(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.game = MyTronBot.TronGame()
        self.state = MyTronBot.TronState(board, tron.ME)

    def test_legal_moves(self):
        self.assertEquals(self.game.legal_moves(self.state), [tron.SOUTH])
        next = self.game.make_move(tron.SOUTH, self.state)
        self.assertEquals(self.game.legal_moves(next), [tron.WEST])

    def test_make_move(self):
        next = self.state
        self.assertEquals(next.board.me(), (1,1))
        self.assertEquals(next.board.them(), (1,4))
        next = self.game.make_move(tron.SOUTH, next)
        self.assertEquals(next.board.me(), (1,1))
        self.assertEquals(next.board.them(), (1,4))
        next = self.game.make_move(tron.WEST, next)
        self.assertEquals(next.board.me(), (2,1))
        self.assertEquals(next.board.them(), (1,3))

    def test_utility(self):
        next = self.state
        self.assertEquals(self.game.utility(next, tron.ME), -0.5)
        self.assertEquals(self.game.utility(next, tron.THEM), -0.5)
        board = next.board
        board.board[2] = '######'
        self.assertEquals(self.game.utility(next, tron.ME), -1)
        self.assertEquals(self.game.utility(next, tron.THEM), 1)
        
    def test_terminal_test(self):
        next = self.state
        self.assertFalse(self.game.terminal_test(next))
        board = next.board
        board.board[2] = '######'
        self.assertTrue(self.game.terminal_test(next))

    def test_ab_eval(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        try_eval = lambda p: MyTronBot.ab_eval(MyTronBot.TronState(board, p))

        # very simple open board; should tie
        self.assertEquals(try_eval(tron.ME), 0.0)
        self.assertEquals(try_eval(tron.THEM), 0.0)

        # very simple closed board; should also tie
        board.board[2] = '# ####'
        self.assertEquals(try_eval(tron.ME), 0.0)
        self.assertEquals(try_eval(tron.THEM), 0.0)

        # advantage me
        board.board[2] = '#  ###'
        a = 1.0 / 3.0
        self.assertAlmostEqual(try_eval(tron.ME), a)
        self.assertAlmostEqual(try_eval(tron.THEM), -a)

        # advantage them
        board.board[2] = '# # ##'
        a = 1.0 / 3.0
        self.assertAlmostEqual(try_eval(tron.ME), -a)
        self.assertAlmostEqual(try_eval(tron.THEM), a)

        # I'm stuck
        board.board[2] = '######'
        self.assertEquals(try_eval(tron.ME), -1.0)
        self.assertEquals(try_eval(tron.THEM), 1.0)
        
        # they're stuck
        board.board[1] = '#1##2#'
        board.board[2] = '#   ##'
        self.assertEquals(try_eval(tron.ME), 1.0)
        self.assertEquals(try_eval(tron.THEM), -1.0)

        # both stuck - make sure doesn't divide by zero!
        board.board[1] = '#1##2#'
        board.board[2] = '######'
        self.assertEquals(try_eval(tron.ME), 0.0)
        self.assertEquals(try_eval(tron.THEM), 0.0)

#_____________________________________________________________________
# Shortest Path Tests
#

class ShortestPathTestCase(unittest.TestCase):

    def test_shortest_path(self):
        maps = { 'maps/u.txt': 27,
                 'maps/ring.txt': 15,
                 'maps/huge-room.txt': 93,
                 'maps/empty-room.txt': 23,
                 'maps/test-board.txt': 4 }
        for m in maps:
            board = MyTronBot.read_board(m)
            path = MyTronBot.shortest_path(board, board.me(), board.them())
            expected = maps[m]
            actual = MyTronBot.moves_between(path)
            self.assertEquals(actual, expected)

#_____________________________________________________________________
# Environment Recognition Tests
#

class EnvironmentRecognitionTestCase(unittest.TestCase):

    def test_find_walls(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        walls = MyTronBot.find_walls(board)
        self.assertEquals(len(walls), 1)
        self.assertEquals(len(walls[0]), 18)

    def test_distance_map(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        dmap = MyTronBot.distance_map(board, board.me())
        self.assertEquals(dmap[(2,1)], 1)
        self.assertEquals(dmap[(2,2)], 2)
        self.assertEquals(dmap[(2,3)], 3)

        board = MyTronBot.read_board('maps/quadrant.txt')
        dmap = MyTronBot.distance_map(board, board.me())
        self.assertEquals(dmap[(3,4)], 1)
        self.assertEquals(dmap[(4,3)], 1)
        self.assertEquals(dmap[(9,5)], 8)
        self.assertEquals(dmap[(13,13)], 20)
    
    def test_same_distance(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        points = MyTronBot.same_distance(board, board.me(), board.them())
        self.assertEquals(points, [])

        board = MyTronBot.read_board('maps/u.txt')
        points = set(MyTronBot.same_distance(board, board.me(), board.them()))
        self.assertEquals(points, set([(7,1),(7,2),(7,3)]))

        board = MyTronBot.read_board('maps/twin-rooms.txt')
        points = set(MyTronBot.same_distance(board, board.me(), board.them()))
        self.assertEquals(points, set([(12,11),(12,12),(12,13)]))

        board = MyTronBot.read_board('maps/huge-room.txt')
        points = MyTronBot.same_distance(board, board.me(), board.them())
        self.assertTrue((48,1) in points)
        self.assertTrue((1,48) in points)
        self.assertTrue((24,25) in points)
        self.assertTrue((25,24) in points)

#_____________________________________________________________________
# Run tests if script.
#

if __name__ == '__main__':
    unittest.main()
