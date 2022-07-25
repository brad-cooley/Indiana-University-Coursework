import part1.raichu as raichu

def show_cells(board, piece, cells):
    print(" " + ("-" * board.get_size() * 2))
    for row in range(board.get_size()):
        s = "|"
        for col in range(board.get_size()):
            if (row, col) == (piece.get_coords()[0], piece.get_coords()[1]):
                s += 'O'
            elif (row, col) in cells:
                s += '*'
            else:
                s += board.get_board_state()[row][col].replace('.', ' ')
            s += ' '
        print(s + "|\n|" + (" " * board.get_size() * 2) + "|")
    print(" " + "-" * board.get_size() * 2)

def show_piece(piece, board):
    print(f"{type(piece).__name__} at ({piece.get_coords()[0]}, {piece.get_coords()[1]})")
    moves = []
    for move in piece.gen_valid_moves(board):
        moves.append(move)

    show_cells(board, piece, moves)
    print()

board = raichu.Board(8, raichu.Color.WHITE)
board.set_board('..........W.W.W.Ww.w.w.w................b.b.b.b..B.B.B.B........')

show_piece(board.get_white_pieces()[0], board)

board.print_board() # print the starting board
piece, move = raichu.minimax_root(3,board,True) # starts the root of the tree with depth 3, the board, and if we are maximizing (True for computers turn)
board.move(piece, move) # makes the move based on the move the tree returned
board.print_board() # print the board
print(board.get_board_as_string())