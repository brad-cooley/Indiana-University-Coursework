#!/usr/local/bin/python3
# solver2021.py : 2021 Sliding tile puzzle solver
#
# Code by: Brad Cooley <redacted>, McKenzie Quinn <redacted>
#
# Based on skeleton code by D. Crandall & B551 Staff, September 2021
#

import heapq, sys
from copy import deepcopy

ROWS=5
COLS=5


def printable_board(board):
    '''generate a printable board.
    Input: 
        board(tuple): tuple of a board
    Return:
        (list): list of strings formatted propperly 
    '''
    return [ ('%3d ')*COLS  % board[j:(j+COLS)] for j in range(0, ROWS*COLS, COLS) ]

def move_left(board, row):
    '''Move row to the left. When grid is transposed, it will move "up"
    Input:
        board: inital board
        row(int): row number
    Return: 
        board(list): list where elements have shifted to the right.
    '''
    new_board = deepcopy(board)
    new_board[row-1] = new_board[row-1][1:] + new_board[row-1][:1]
    return new_board

def move_right(board, row):
    '''Move row to the right. When grid is transposed, it will move "down"
    Input:
        board: inital board
        row(int): row number
    Return: 
       board(list): list where elements have shifted to the right.
    '''
    #deep copy due to call by refrence error
    new_board = deepcopy(board)
    new_board[row-1] = new_board[row-1][-1:] + new_board[row-1][:-1]
    return new_board

#Transposed grid to reuse left and right moves ans up and down movements.
def transpose_board(board):
    '''Transpose grid.
    Input: 
        board(list): grid with a list of lists 
    Return:
        (list): A transposed list of lists
    '''
    #deep copy due to call by refrence error
    new_board = deepcopy(board)
    return [[new_board[r][c] for r in range(len(new_board))] for c in range(len(new_board[0]))]

def rotate_clockwise(board):
    #deep copy due to call by refrence error
    new_board = deepcopy(board)
    #move last shift element to top row
    top_row = new_board[1][0]
    #remove extra element from row and save to use in the future
    extra = new_board[0].pop()
    new_board[0].insert(0, top_row)
    new_board = transpose_board(new_board)
    new_board[-1].insert(1, extra)
    extra = new_board[-1].pop()
    new_board = transpose_board(new_board)
    new_board[-1].insert(-1, extra)
    extra = new_board[-1].pop(0)
    new_board = transpose_board(new_board)
    new_board[0].insert(-1, extra)
    new_board[0].pop(0)
    new_board = transpose_board(new_board)

    return new_board

def rotate_counterclockwise(board):
    #deep copy due to call by refrence bug
    new_board = deepcopy(board)
    #move last shift element to top row
    top_row = new_board[1][-1]
    #remove extra element from row and save to use in the future
    extra = new_board[0].pop(0)
    new_board[0].append(top_row)
    new_board = transpose_board(new_board)
    new_board[0].insert(1, extra)
    extra = new_board[0].pop()
    new_board = transpose_board(new_board)
    new_board[-1].insert(1, extra)
    extra = new_board[-1].pop()
    new_board = transpose_board(new_board)
    new_board[-1].insert(-1, extra)
    new_board[-1].pop(0)
    new_board = transpose_board(new_board)

    return new_board

def get_inner(board):
    inner = board[1:-1]
    inner = [row[1:-1] for row in inner]
    return inner

def replace_inner(board, inner):
    new_board = deepcopy(board)
    for row in range(len(board)):
        if row in (1,2,3):
            new_board[row][1:-1] = inner[row-1]
    return new_board

def add_board(board, move):
    if move[0] == 'R':
        board = move_right(board, int(move[1]))
    elif move[0] == 'L':
        board = move_left(board, int(move[1]))
    elif move[0] == 'U':
        board = transpose_board(board)
        board = move_left(board, int(move[1]))
        board = transpose_board(board)
    elif move[0] == 'D':
        board = transpose_board(board)
        board = move_right(board, int(move[1]))
        board = transpose_board(board)
    elif move == 'Icc':
        inner_board = get_inner(board)
        inner_board = rotate_counterclockwise(inner_board)
        board = replace_inner(board, inner_board)
    elif move == 'Ic':
        inner_board = get_inner(board)
        inner_board = rotate_clockwise(inner_board)
        board = replace_inner(board, inner_board)
    elif move == 'Oc':
        board = rotate_clockwise(board)
    elif move == 'Occ':
        board = rotate_counterclockwise(board)
    else: 
        raise(Exception('invalid move.'))

    return board

def calculate_misplaced_tiles(board_coords): 
    goal_state_coord = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (0, 3),5: (0, 4), 6: (1, 0),
    7: (1, 1),8: (1, 2),9: (1, 3),10: (1, 4),11: (2, 0),12: (2, 1),
    13: (2, 2),14: (2, 3),15: (2, 4),16: (3, 0),17: (3, 1),18: (3, 2),
    19: (3, 3),20: (3, 4),21: (4, 0),22: (4, 1),23: (4, 2),24: (4, 3),
    25: (4, 4)}
    misplaced_tiles = 0 
    for i in range(1,26):
        if board_coords.get(i) != goal_state_coord.get(i):
            misplaced_tiles += 1
    #dividing by 16 since that is the maximum amount of tiles that can be changed in 1 move.
    return misplaced_tiles/16 

def manhattan_distance(goal_coord, current_coord):
    return abs(goal_coord[0] - current_coord[0]) + abs(goal_coord[1] -  current_coord[1])

def get_state_coords(board):
    board_coords = dict()
    for x in range(len(board)):
        for y in range(len(board[0])):
           board_coords[board[x][y]] = (x,y)
    return board_coords
    
def calculate_manhattan_heuristic(board_coords):
    sum_manhattan = 0
    goal_state_coord = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (0, 3),5: (0, 4), 6: (1, 0),
    7: (1, 1),8: (1, 2),9: (1, 3),10: (1, 4),11: (2, 0),12: (2, 1),
    13: (2, 2),14: (2, 3),15: (2, 4),16: (3, 0),17: (3, 1),18: (3, 2),
    19: (3, 3),20: (3, 4),21: (4, 0),22: (4, 1),23: (4, 2),24: (4, 3),
    25: (4, 4)}
    for i in range(1,26):
        goal_coord = goal_state_coord.get(i)
        current_coord = board_coords.get(i)
        sum_manhattan += manhattan_distance(goal_coord, current_coord)
    return sum_manhattan/16

def calculate_heuristic(board_coords):
    possible_heuristics = list()
    goal_state_coord = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (0, 3),5: (0, 4), 6: (1, 0),
    7: (1, 1),8: (1, 2),9: (1, 3),10: (1, 4),11: (2, 0),12: (2, 1),
    13: (2, 2),14: (2, 3),15: (2, 4),16: (3, 0),17: (3, 1),18: (3, 2),
    19: (3, 3),20: (3, 4),21: (4, 0),22: (4, 1),23: (4, 2),24: (4, 3),
    25: (4, 4)}
    sum_manhattan = 0 
    misplaced_tiles = 0 
    for i in range(1,26):
        goal_coord = goal_state_coord.get(i)
        current_coord = board_coords.get(i)
        sum_manhattan += manhattan_distance(goal_coord, current_coord)
        if board_coords.get(i) != goal_state_coord.get(i):
            misplaced_tiles += 1
    #dividing by 16 since that is the maximum amount of tiles that can be changed in 1 move.
    possible_heuristics = [misplaced_tiles/16 , sum_manhattan/16]

    #calculate misplaced_tiles
    #misplaced_tiles = calculate_misplaced_tiles(board_coords)
    #possible_heuristics.append(misplaced_tiles)
    #calculate manhattan distance 
    #manhattan_distance = calculate_manhattan_heuristic(board_coords)
    #possible_heuristics.append(manhattan_distance)

    return max(possible_heuristics)

# return a list of possible successor states
def successors(state):
    possible_moves = ['R1','R2','R3','R4','R5','L1','L2','L3','L4','L5','U1','U2','U3','U4','U5','D1',
'D2','D3','D4','D5','Ic','Icc','Oc','Occ']
    return [[add_board(state, i), i] for i in possible_moves]

# check if we've reached the goal
def is_goal(state):
    '''check if current state is the goal state
    Input: 
        state(list): list of lists with current state
    Return:
        (bool): True if current state is the goal state, False otherwise
    '''
    goal_state = [[1,2,3,4,5],
                  [6,7,8,9,10],
                  [11,12,13,14,15],
                  [16,17,18,19,20],
                  [21,22,23,24,25]]
    if state == goal_state:
        return True
    return False

def transform_board(initial_board):
    '''Transform initial board in tuple form to a list of lists.
    Input: 
        initial_board(tuple): tuple with length 25 
    Return: 
        board(list): list of list to mimic a grid of 5x5
    '''
    board = list()
    row = list()
    for i in initial_board:
        row.append(i)
        if len(row) == 5:
            board.append(row)
            row = list()
    return board

def in_fringe_and_larger(new_node, fringe):
    for node in fringe:
        if (node[1] == new_node[1]) and (node[0] < new_node[0]):
            return True
    return False 


def solve(initial_board):
    """
    1. This function should return the solution as instructed in assignment, consisting of a list of moves like ["R2","D2","U1"].
    2. Do not add any extra parameters to the solve() function, or it will break our grading and testing code.
       For testing we will call this function with single argument(initial_board) and it should return 
       the solution.
    3. Please do not use any global variables, as it may cause the testing code to fail.
    4. You can assume that all test cases will be solvable.
    5. The current code just returns a dummy solution.
    """
    '''Solve...
    Input: 
        initial_board(tuple): tuple of element being read in
    '''
    initial_board = transform_board(initial_board)
    #iniital board is the goal state
    if is_goal(initial_board):
        #return an empty list since no moves have been made.
        return list()
    #fringe elements (heuristic_value, board, move)
    fringe = [(0, initial_board, list())]

    while fringe:
        #Normally need a condition to check for failure... but based on comments, 
        #we can assume all test cases will be solved.
        state = heapq.heappop(fringe)
        closed = list()
        if is_goal(state[1]):
            #if state is goal, return solution
            return state[2]
        for s in successors(state[1]):
            path = state[2] + [s[1]]
            state_coords = get_state_coords(s[0])
            heuristic = state[0] + calculate_heuristic(state_coords)
            new_node = (heuristic, s[0], path)
            if s in closed:
                #state already visited
                continue
            elif in_fringe_and_larger(new_node, fringe): 
                #smaller cost with same map already in fringe
                continue 
            else:
                #add new node 
                heapq.heappush(fringe, new_node)
                closed.append(state)


    

# Please don't modify anything below this line
#
if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise(Exception("Error: expected a board filename"))

    start_state = []
    with open(sys.argv[1], 'r') as file:
        for line in file:
            start_state += [ int(i) for i in line.split() ]

    if len(start_state) != ROWS*COLS:
        raise(Exception("Error: couldn't parse start state file"))

    print("Start state: \n" +"\n".join(printable_board(tuple(start_state))))

    print("Solving...")
    route = solve(tuple(start_state))
    print(route)
    print("Solution found in " + str(len(route)) + " moves:" + "\n" + " ".join(route))
