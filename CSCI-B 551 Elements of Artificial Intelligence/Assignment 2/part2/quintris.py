# Simple quintris program! v0.2
#
# Code by: Brad Cooley <redacted>, McKenzie Quinn <redacted>
#
# D. Crandall, Sept 2021

from typing import _eval_type
from AnimatedQuintris import *
from SimpleQuintris import *
from kbinput import *
import time, sys, copy

class HumanPlayer:

    def get_moves(self, quintris):
        
        # super simple current algorithm: just randomly move left, right, and rotate a few times
        print("Type a sequence of moves using: \n  b for move left \n  m for move right \n  n for rotation\n  h for horizontal flip\nThen press enter. E.g.: bbbnn\n")
        moves = input()
        return moves

    def control_game(self, quintris):
        while 1:
            c = get_char_keyboard()
            commands =  { "b": quintris.left, "h": quintris.hflip, "n": quintris.rotate, "m": quintris.right, " ": quintris.down }
            commands[c]()

#####
# This is the part you'll want to modify!
# Replace our super simple algorithm with something better
#
class ComputerPlayer:

    piece_counts = {
        'cross': 0,
        'long': 0,
        'u': 0,
        'l': 0,
        't': 0,
        's': 0
    }

    cross = [[' x ', 'xxx', ' x ']]
    long = [
        ['xxxxx'], 
        ['x', 'x', 'x', 'x', 'x']
    ]
    u = [
        ['x x', 'xxx'],  
        ['xx', 'x ', 'xx'],
        ['xxx', 'x x'],
        ['xx', ' x', 'xx']
    ]
    l = [
        ['x   ', 'xxxx'], 
        ['xx', 'x ', 'x ', 'x '], 
        ['xxxx', '   x'],
        [' x', ' x', ' x', 'xx'],
        ['   x', 'xxxx'],
        ['x ', 'x ', 'x ', 'xx'],
        ['xxxx', 'x   '],
        ['xx', ' x', ' x', ' x']
    ]
    t = [
        ['  x ', 'xxxx'],
        ['x ', 'x ', 'xx', 'x '],
        ['xxxx', ' x  '],
        [' x', 'xx', ' x', ' x'],
        [' x  ', 'xxxx'],
        ['x ', 'xx', 'x ', 'x '],
        ['xxxx', '  x '],
        [' x', ' x', 'xx', ' x']
    ]
    s = [
        ['  xx', 'xxx '],
        ['x ', 'x ', 'xx', ' x'],
        [' xxx', 'xx  '],
        ['x ', 'xx', ' x', ' x'],
        ['xx  ', ' xxx'],
        [' x', 'xx', 'x ', 'x '],
        ['xxx ', '  xx'],
        [' x', ' x', 'xx', 'x ']
    ]

    def minimax_root(self, quintris, depth, is_maximizing):
                
        best_value = -99999
        best_board = None

        for move in self.gen_possible_moves(quintris):
            # print(move)
            new_q = copy.deepcopy(quintris)
            self.simulate_move_sequence(new_q, move)

            value = max(best_value, self.minimax(new_q, depth-1, -100000, 100000, not is_maximizing))

            if( value > best_value):
                best_value = value
                best_board = move
            
        return best_board

    def minimax(self, quintris, depth, alpha, beta, is_maximizing):

        if depth == 0:
            return -self.evaluation(quintris, is_maximizing)
        
        if is_maximizing:
            best_value = -99999
            for move in self.gen_possible_moves(quintris):
                # print(move)
                new_q = copy.deepcopy(quintris)
                self.simulate_move_sequence(new_q, move)

                best_value = max(best_value, self.minimax(new_q, depth-1, alpha, beta, not is_maximizing))
                if best_value >= beta:
                    # print('PRUNING in max')
                    return best_value
                alpha = max(alpha, best_value)
            return best_value
            
        else:
            best_value = 99999

            for move in self.gen_possible_moves(quintris):
                new_q = copy.deepcopy(quintris)
                self.simulate_move_sequence(new_q, move)

                best_value = min(best_value, self.minimax(new_q, depth-1, alpha, beta, not is_maximizing))
                
                if best_value <= alpha:
                    
                    return best_value
                beta = min(beta, best_value)
            return best_value

    def evaluation(self, quintris, is_maximizing):
        return (self.get_board_score(quintris) if is_maximizing else -self.get_board_score(quintris))


    def get_board_score(self, quintris):

        rows = quintris.get_board()
        count = 0
        for row in rows:
            # print(row)
            if ('x' or 'X') not in row:

                count+=1

        # print(count)


        empty_count = 0
        for x in range(count, 25):
            for char in rows[x]:
                if char not in ('x' or 'X'):
                    empty_count += 1
        
        return empty_count + quintris.get_score()

    # This function should generate a series of commands to move the piece into the "optimal"
    # position. The commands are a string of letters, where b and m represent left and right, respectively,
    # and n rotates. quintris is an object that lets you inspect the board, e.g.:
    #   - quintris.col, quintris.row have the current column and row of the upper-left corner of the 
    #     falling piece
    #   - quintris.get_piece() is the current piece, quintris.get_next_piece() is the next piece after that
    #   - quintris.left(), quintris.right(), quintris.down(), and quintris.rotate() can be called to actually
    #     issue game commands
    #   - quintris.get_board() returns the current state of the board, as a list of strings.
    #
    def chance_calc(self, piece_type):
        denom = sum(self.piece_counts.values())
        return self.piece_counts[piece_type]/denom

    def classify_piece(self, piece):
        i = 0
        count_increase = False
        while not count_increase:
            for x in self.cross:
                if piece == x:
                    self.piece_counts['cross'] += 1
                    # print('classified as a cross')
                    count_increase = True
                    return ('cross', 4-i)

            for x in self.long:
                if piece == x:
                    self.piece_counts['long'] += 1
                    # print('classified as a long')
                    count_increase = True
                    return ('long', 4-i)

            for x in self.u:
                if piece == x:
                    self.piece_counts['u'] += 1
                    # print('classified as a U')
                    count_increase = True
                    return ('u', 4-i)

            for x in self.l:
                if piece == x:
                    self.piece_counts['l'] += 1
                    # print('classified as a L')
                    count_increase = True
                    return ('l', 4-i)

            for x in self.t:
                if piece == x:
                    self.piece_counts['t'] += 1
                    # print('classified as a T')
                    count_increase = True
                    return ('t', 4-i)

            for x in self.s:
                if piece == x:
                    self.piece_counts['s'] += 1
                    # print('classified as a S')
                    count_increase = True
                    return ('s', 4-i)

    def reset_piece(self, quintris, diff):
        
        while diff > 0:
            quintris.rotate()
            diff-=1

    def simulate_move_sequence(self, quintris, move):
        
        for char in move:
            # print(char)
            if char in 'm':
                quintris.right()
            elif char in 'b':
                # print('made it to b')
                quintris.left()
            elif char in 'h':
                quintris.hflip()
            elif char in 'n':
                quintris.rotate()

        quintris.down()
        # time.sleep(0.5)
        # yield move

    def gen_possible_moves(self, quintris):
        
        new_q = quintris
        # new_q = copy.deepcopy(quintris)

        _, _, piece_y = new_q.get_piece()

        # Move to the far left
        moves = set()
        move = ''
        while piece_y > 0:
            move += 'b'
            new_q.left()
            piece_y - 1
            _, _, piece_y = new_q.get_piece()

        m_move = move
        moves.add(m_move)
        for piece_y in range(15):
            m_move += 'm'
            h_move = m_move
            moves.add(h_move)
            for horizontal_flip in [True, False]:
                if horizontal_flip:
                    h_move += 'h'
                temp_move = h_move
                for right_turn in range(3):
                    temp_move += 'n'
                    moves.add(temp_move)

        return moves

    def piece_to_string(self, piece):
        return "\n".join(piece)

    def get_moves(self, quintris):
        move = self.minimax_root(quintris, 2, True)
        
        return move

        # return random.choice("mnbh") * random.randint(1, 10)
       
    # This is the version that's used by the animted version. This is really similar to get_moves,
    # except that it runs as a separate thread and you should access various methods and data in
    # the "quintris" object to control the movement. In particular:
    #   - quintris.col, quintris.row have the current column and row of the upper-left corner of the 
    #     falling piece
    #   - quintris.get_piece() is the current piece, quintris.get_next_piece() is the next piece after that
    #   - quintris.left(), quintris.right(), quintris.down(), and quintris.rotate() can be called to actually
    #     issue game commands
    #   - quintris.get_board() returns the current state of the board, as a list of strings.
    #
    def control_game(self, quintris):
        # another super simple algorithm: just move piece to the least-full column
        while 1:
            time.sleep(0.1)

            board = quintris.get_board()
            column_heights = [ min([ r for r in range(len(board)-1, 0, -1) if board[r][c] == "x"  ] + [100,] ) for c in range(0, len(board[0]) ) ]
            index = column_heights.index(max(column_heights))

            if(index < quintris.col):
                quintris.left()
            elif(index > quintris.col):
                quintris.right()
            else:
                quintris.down()


###################
#### main program

(player_opt, interface_opt) = sys.argv[1:3]

try:
    if player_opt == "human":
        player = HumanPlayer()
    elif player_opt == "computer":
        player = ComputerPlayer()
    else:
        print("unknown player!")

    if interface_opt == "simple":
        quintris = SimpleQuintris()
    elif interface_opt == "animated":
        quintris = AnimatedQuintris()
    else:
        print("unknown interface!")

    quintris.start_game(player)

except EndOfGame as s:
    print("\n\n\n", s)



