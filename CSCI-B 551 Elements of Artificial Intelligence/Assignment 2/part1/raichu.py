#
# raichu.py : Play the game of Raichu
#
# Code by: Brad Cooley <redacted>, McKenzie Quinn <redacted>
#
# Based on skeleton code by D. Crandall, Oct 2021
#
import sys
import time
from enum import Enum
from itertools import permutations
class Color(Enum):
    '''
    Color enum that holds the vectors for each color.
    '''

    BLACK = [-1, -1]
    WHITE = [1, 1]

class GamePiece:
    '''
    GamePiece class that is the parent class for all the game piece types.
    '''
    def __init__(self, rank:int, color:Color, x, y, moves, jump_moves):
        # rank of the piece for jumping purposes
        self.__rank = rank 

        # piece color enforced as a Color type (enum above)
        self.__color = color

        # x & y coordinates for the piece
        self.__x = x
        self.__y = y

        # valid move directions that the piece can make (list)
        self.__moves = moves

        # valid jump move directions that the piece can make (list)
        self.__jump_moves = jump_moves

    ## GETTERS ##
    def get_rank(self):
        '''
        Method to return the rank of the GamePiece.
        '''
        return self.__rank

    def get_color(self):
        '''
        Method to return the color of the GamePiece.
        '''
        return self.__color

    def get_coords(self):
        '''
        Method to return the coordinates of the GamePiece, as a tuple.
        '''
        return (self.__x, self.__y)

    def get_moves(self):
        '''
        Method to return the move directions of the GamePiece, as a list.
        '''
        return self.__moves

    def get_jump_moves(self):
        '''
        Method to return the jump move directions of the GamePiece, as a list.
        '''
        return self.__jump_moves
    
    ## SETTERS ##
    def set_rank(self, rank:int):
        '''
        Method to set the rank of the GamePiece.
        '''
        self.__rank = rank
    
    def set_color(self, color:Color):
        '''
        Method to set the color of the GamePiece.
        '''
        self.__color = color

    def set_coords(self, coords):
        '''
        Method to set the coordinates of the GamePiece, taken in as a tuple.
        '''
        self.__x = coords[0]
        self.__y = coords[1]

    def set_moves(self, moves):
        '''
        Method to set the move directions of the GamePiece, taken as a list.
        '''
        self.__moves = moves

    def set_jump_moves(self, jump_moves):
        '''
        Method to set the jump move directions of the GamePiece, taken as a list.
        '''
        self.__jump_moves = jump_moves
    
    ## HELPERS ##
    def is_black(self):
        '''
        Method that returns a boolean value checking if the GamePiece is of Color BLACK.
        '''
        return self.__color == Color.BLACK

    def __move_prep__(self, moves, board):
        '''
        Private generator to prepare a piece for a move. Only used when trying to generate valid moves for a GamePiece.
        '''
        for move in moves:

            # Get my goal coordinates (where I want to move to)
            goal_x = self.__x + (move[0] * self.__color.value[0])
            goal_y = self.__y + (move[1] * self.__color.value[1])
            
            # Check if the move is within the bounds of the board
            if not board.is_in_bounds(goal_x, goal_y):
                continue

            # Check if the space isn't open
            if board.get_board_state()[goal_x][goal_y] not in '.':
                continue 
            
            # Calculate the slope of the line between the goal state and start state (for direction)
            slope = (goal_x - self.__x, goal_y - self.__y)

            # Calculate distance to goal (how many spaces)
            scalar = [x for x in [abs(slope[0]), abs(slope[1])] if x != 0][0] 

            # Create a unit vector for calculating the direction we have to head to reach the goal space
            unit = (int(slope[0] / scalar), int(slope[1] / scalar))

            yield ((goal_x, goal_y), scalar, unit)

    def gen_valid_moves(self, board):
        '''
        Generator that generates valid moves for a GamePiece.
        '''

        # Look at all valid moves for a piece
        for move in self.__move_prep__(self.__moves(board), board):
            goal = move[0]
            scalar = move[1]
            unit = move[2]

            clean_path = True

            # For each space between the start space and and the goal space
            for steps in range(1, scalar):

                # Get coordinates for the space we are checking/currently looking at
                check = (self.__x + (steps * unit[0]), self.__y + (steps * unit[1]))

                # Get the space at the coordinates we found above
                check_piece = board.get_board_state()[check[0]][check[1]]
                
                # Check if the space isn't open (a piece occupies it)
                if check_piece not in '.':

                    # The space isn't open, so we don't have a clear/clean path to get there
                    clean_path = False
                    break
            
            # If we have a clean path (no game pieces in our way), yield the move
            if clean_path:
                yield goal

        # Look at all valid jump moves (for Pichu and Pikachu, this is one space beyond their valid moves)
        for move in self.__move_prep__(self.__jump_moves(board), board):
            goal = move[0]
            scalar = move[1]
            unit = move[2]

            piece_count = 0
            clean_path = True

            # For each space between the start space and and the goal space
            for steps in range(1, scalar):
                # Get coordinates for the space we are checking/currently looking at
                check = (self.__x + (steps * unit[0]), self.__y + (steps * unit[1]))

                # Get the space at the coordinates we found above
                check_piece = board.get_board_state()[check[0]][check[1]]

                # Check if the space isn't open (a piece occupies it)
                if check_piece not in '.':
                    piece_count += 1

                # Check if there is more than one piece between the start space and goal space (can't jump)
                if piece_count > 1: 
                    clean_path = False
                    break
                
                # Check to make sure it isn't our own piece as we cannot jump ourselves
                if (self.is_black() and check_piece in 'bB$') or (not(self.is_black()) and check_piece in 'wW@'): # Same color (can't jump)
                    clean_path = False
                    break
                
                # Assign a rank to the piece
                rank = 1 if check_piece in 'bw' else (2 if check_piece in 'BW' else (3 if check_piece in '@$' else 0))

                # Check if the rank is higher than ours (can't jump that piece)
                if rank > self.__rank:
                    clean_path = False
                    break
            
            # Check if there are no pieces (meaning we can't make the max move because it is out of bounds of valid moves for our piece)
            if piece_count == 0:
                clean_path = False
            
            # If the path is clean (only one piece to jump), yield the move
            if clean_path:
                yield goal

class Pichu(GamePiece):
    def __init__(self, color, x, y):
        super().__init__(1, color, x, y, 
        lambda board: [
            [1, 1], # right diag
            [1, -1] # left diag
        ],
        lambda board: [
            [1, 1], # right diag 1
            [1, -1], # left diag 1
            [2, 2], # right diag 2
            [2, -2]  # left diag 2
        ])

class Pikachu(GamePiece):
    def __init__(self, color, x, y):
        super().__init__(2, color, x, y, 
        lambda board: [
            [1, 0], # forward 1
            [2, 0], # forward 2
            [0, -1], # left 1
            [0, -2], # left 2
            [0, 1], # right 1
            [0, 2] # right 2
        ],
        lambda board: [
            [1, 0], # forward 1
            [2, 0], # forward 2
            [3, 0], # forward 3
            [0, -1], # left 1
            [0, -2], # left 2
            [0, -3], # left 3
            [0, 1], # right 1
            [0, 2], # right 2
            [0, 3] # right 3
        ])

class Raichu(GamePiece):
    def __init__(self, color, x, y):
        super().__init__(3, color, x, y, self.gen_moves, self.gen_moves)

    def gen_moves(self, board):
        for dir in set(permutations([-1, -1, 0, 1, 1], 2)):
            for steps in range(1, board.get_size()):
                yield (steps * dir[0], steps * dir[1])

class Board:

    def __init__(self, N:int, turn:Color):
        self.__size = N
        self.__turn = turn
        self.__white_pieces = []
        self.__black_pieces = []
        self.__board_state = [['.' for x in range(self.__size)] for y in range(self.__size)]
    
    ## GETTERS ##
    def get_size(self):
        return self.__size

    def get_turn(self):
        return self.__turn

    def get_white_pieces(self):
        return self.__white_pieces

    def get_black_pieces(self):
        return self.__black_pieces

    def get_board_state(self):
        return self.__board_state

    def get_board_as_string(self):
        str = ''
        for row in self.__board_state:
            for char in row:
                str += char

        return str

    ## SETTERS ##
    def set_size(self, size:int):
        self.__size = size

    def set_turn(self, turn:Color):
        self.__turn = turn

    def set_white_pieces(self, white_pieces):
        self.__white_pieces = white_pieces

    def set_black_pieces(self, black_pieces):
        self.__black_pieces = black_pieces

    def set_board_state(self, board_state):
        self.__board_state = board_state

    def set_board(self, board):
        x = 0

        self.__black_pieces = []
        self.__white_pieces = []

        for i in range(0, self.__size):
            for j in range(0, self.__size):
                self.__board_state[i][j] = board[x]
                
                color = None
                piece = None

                if board[x] in 'wW@':
                    color = Color.WHITE
                elif board[x] in 'bB$':
                    color = Color.BLACK
                elif board[x] in '.':
                    x += 1
                    continue

                if board[x] in 'wb':
                    piece = Pichu
                elif board[x] in 'WB':
                    piece = Pikachu
                elif board[x] in '@$':
                    piece = Raichu

                new_piece = piece(color, i, j)

                if new_piece.is_black():
                    self.__black_pieces.append(new_piece)
                else:
                    self.__white_pieces.append(new_piece)
                
                x+=1

    ## HELPERS ##
    def is_in_bounds(self, x, y):
        return (x >= 0 and y >= 0) and (x < self.__size and y < self.__size)

    def copy(self):
        new_board = Board(self.__size, self.__turn)
        new_board.set_board(self.get_board_as_string())

        return new_board

    def gen_white_moves(self):
        for piece in self.__white_pieces:
            for move in piece.gen_valid_moves(self):
                yield move
    
    def gen_black_moves(self):
        for piece in self.__black_pieces:
            for move in piece.gen_valid_moves(self):
                yield move

    def print_board(self):
        print(board_to_string(self.get_board_as_string(), self.__size))

    def update_board(self):

        for i in range(self.__size):
            for j in range(self.__size):
                self.__board_state[i][j] = "."
        for piece in self.__black_pieces:
            (x, y) = piece.get_coords()
            if isinstance(piece, Pichu):
                self.__board_state[x][y] = '$' if x == 0 else 'b'
                
            elif isinstance(piece, Pikachu):
                self.__board_state[x][y] = '$' if x == 0 else 'B'

            elif isinstance(piece, Raichu):
                self.__board_state[x][y] = '$'

        for piece in self.__white_pieces:
            (x, y) = piece.get_coords()
            if isinstance(piece, Pichu):
                self.__board_state[x][y] = '@' if x == self.__size-1 else 'w'

            elif isinstance(piece, Pikachu):
                self.__board_state[x][y] = '@' if x == self.__size-1 else 'W'

            elif isinstance(piece, Raichu):
                self.__board_state[x][y] = '@'

        self.set_board(self.get_board_as_string())

    def move(self, piece, move):

        if piece.is_black():
            for p in self.__black_pieces:
                if piece.get_coords() == p.get_coords():
                    new_piece = p
        else:
            for p in self.__white_pieces:
                if piece.get_coords() == p.get_coords():
                    new_piece = p        
        
        goal_x = move[0]
        goal_y = move[1]
        start_x = new_piece.get_coords()[0]
        start_y = new_piece.get_coords()[1]

        slope = (goal_x - start_x, goal_y - start_y)
        scalar = [x for x in [abs(slope[0]), abs(slope[1])] if x != 0][0] # Calculate distance to goal
        unit = (int(slope[0] / scalar), int(slope[1] / scalar)) # Calculate direction to goal

        check_piece_coords = (-1,-1)
        check_piece = ''

        for step in range(1, scalar):
            check = (start_x + (step * unit[0]), start_y + (step * unit[1]))
            check_piece = self.__board_state[check[0]][check[1]]

            if check_piece not in '.':
                # Found a piece, update coords
                check_piece_coords = (check[0], check[1])

        # moving my piece to goal cords
        new_piece.set_coords((goal_x, goal_y))

        # logic for jumping a piece
        if new_piece.is_black():
            for p in self.__white_pieces:
                if check_piece_coords == p.get_coords():
                    self.__white_pieces.remove(p)
                    break
                        
        else:
            for p in self.__black_pieces:
                if check_piece_coords == p.get_coords():
                    self.__black_pieces.remove(p)
                    break

        self.__board_state[start_x][start_y] = '.'
        self.update_board()
        if self.__turn == Color.WHITE:
            self.__turn = Color.BLACK 
        elif self.__turn ==  Color.BLACK:
            self.__turn = Color.WHITE

def print_board(board):
    print(board_to_string(board.get_board_as_string(), board.get_size()))

def minimax_root(depth, board, is_maximizing):
    possible_moves = []

    if board.get_turn() == Color.BLACK:
        for piece in board.get_black_pieces():
            possible_moves.extend((piece, move) for move in piece.gen_valid_moves(board))
    elif board.get_turn() == Color.WHITE:
        for piece in board.get_white_pieces():
            possible_moves.extend((piece, move) for move in piece.gen_valid_moves(board))
            
    best_move = -999999
    best_move_overall = (None, None)

    for piece, move in possible_moves:

        new_board = board.copy()
        new_board.move(piece, move)

        value = max(best_move, minimax(depth - 1, new_board, -1000000, 1000000, not is_maximizing)) # find the max value
        if( value > best_move):
            best_move = value
            best_move_overall = (piece, move)
    
    return best_move_overall

def minimax(depth, board, alpha, beta, is_maximizing):
    if(depth == 0):
        return -evaluation(board, board.get_turn())

    possible_moves = []
    for piece in board.get_white_pieces() if board.get_turn() == Color.WHITE else board.get_black_pieces():
        possible_moves.extend((piece, move) for move in piece.gen_valid_moves(board))
            
    if(is_maximizing):
        best_move = -999999
        for piece, move in possible_moves:

            new_board = board.copy()
            new_board.move(piece, move)
            
            best_move = max(best_move, minimax(depth - 1, new_board, alpha, beta, not is_maximizing)) # find the max value
            if best_move >= beta:
                return best_move
            alpha = max(alpha, best_move)
        return best_move

    else:
        best_move = 999999
        for piece, move in possible_moves:
            new_board = board.copy()
            new_board.move(piece, move)

            best_move = min(best_move, minimax(depth - 1, new_board, alpha, beta, not is_maximizing)) # find the max value
            if best_move <= alpha:
                return best_move
            beta = min(beta, best_move)
                
        return best_move

def evaluation(board, color_max):
    evaluation = 0

    for piece in board.get_black_pieces():
        evaluation += (get_piece_value(piece) if piece.get_color() is color_max else -get_piece_value(piece))

    for piece in board.get_white_pieces():
        evaluation += (get_piece_value(piece) if piece.get_color() is color_max else -get_piece_value(piece))
    return evaluation


def get_piece_value(piece):
    if(piece == None):
        return 0
    return piece.get_rank()

def board_to_string(board, N):
    return "\n".join(board[i:i+N] for i in range(0, len(board), N))

def find_best_move(board, N, player, timelimit):
    # This sample code just returns the same board over and over again (which
    # isn't a valid move anyway.) Replace this with your code!
    i = 1

    turn = Color.WHITE if player == 'w' else Color.BLACK

    while True:
        new_board = Board(N, turn)
        new_board.set_board(board)
        piece, move = minimax_root(i, new_board, True)
        new_board.move(piece, move)
        yield new_board.get_board_as_string()
        i+=1


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise Exception("Usage: Raichu.py N player board timelimit")
        
    (_, N, player, board, timelimit) = sys.argv
    N=int(N)
    timelimit=int(timelimit)
    if player not in "wb":
        raise Exception("Invalid player.")

    if len(board) != N*N or 0 in [c in "wb.WB@$" for c in board]:
        raise Exception("Bad board string.")

    print("Searching for best move for " + player + " from board state: \n" + board_to_string(board, N))
    print("Here's what I decided:")
    for new_board in find_best_move(board, N, player, timelimit):
        print(new_board)