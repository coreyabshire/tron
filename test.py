import tron, MyTronBot, unittest

class MyTestCase(unittest.TestCase):
    
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

    def test_adjacent_floor(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertEqual(MyTronBot.adjacent_floor(board, board.me()), [(2,1)])
        self.assertEqual(MyTronBot.adjacent_floor(board, board.them()), [(1,3)])
        
    def test_terminal_test(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertFalse(MyTronBot.terminal_test(board))
        board.board[2] = '######'
        self.assertTrue(MyTronBot.terminal_test(board))
        
    def test_utility(self):
        board = MyTronBot.read_board('maps/test-board.txt')
        self.assertEqual(MyTronBot.utility(board, tron.ME), 0)
        self.assertEqual(MyTronBot.utility(board, tron.THEM), 0)
        board.board[2] = '######'
        self.assertEqual(MyTronBot.utility(board, tron.ME), -1)
        self.assertEqual(MyTronBot.utility(board, tron.THEM), 1)

if __name__ == '__main__':
    unittest.main(defaultTest='MyTestCase')
