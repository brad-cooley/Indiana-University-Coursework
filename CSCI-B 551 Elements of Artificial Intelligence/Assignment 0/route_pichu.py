#!/usr/local/bin/python3
#
# route_pichu.py : a maze solver
#
# Submitted by : Brad Cooley <redacted>
#
# Based on skeleton code provided in CSCI B551, Fall 2021.

import sys, heapq

# Parse the map from a given filename
def parse_map(filename):
    with open(filename, "r") as f:
        return [[char for char in line] for line in f.read().rstrip("\n").split("\n")][3:]
          
# Check if a row,col index pair is on the map
def valid_index(pos, n, m):
    return 0 <= pos[0] < n  and 0 <= pos[1] < m

# Find the possible moves from position (row, col)
def moves(map, row, col):
    moves=((row+1,col), (row-1,col), (row,col-1), (row,col+1))

    # Return only moves that are within the house_map and legal (i.e. go through open space ".")
    return [ move for move in moves if valid_index(move, len(map), len(map[0])) and (map[move[0]][move[1]] in ".@" ) ]

# Find the location ((x, y) coordinates) of a given character in the map
def location_find(char, house_map):
    return [(row_i,col_i) for col_i in range(len(house_map[0])) for row_i in range(len(house_map)) if house_map[row_i][col_i]==str(char)][0]

# Calculate the Manhattan Distance between two (x, y) coordinates
def manhattan_distance(c1, c2):
    return (abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]))

# Classify a move in terms of direction
def move_classification(curr_move, new_move):
    if new_move[0] - curr_move[0] < 0:
        return 'U'
    elif new_move[0] - curr_move[0] > 0:
        return 'D'
    else:
        if new_move[1] - curr_move[1] < 0:
            return 'L'
        else:
            return 'R'

# Find the path taken to get from the start location to the end location
def path(prev, current):
    total_path = [current]

    while current in prev:
        current = prev[current]
        total_path.insert(0, current)

    # Remove the first element because we need to handle it differently for move_classification
    del total_path[0]
    return total_path

# Perform search on the map
#
# This function MUST take a single parameter as input -- the house map --
# and return a tuple of the form (move_count, move_string), where:
# - move_count is the number of moves required to navigate from start to finish, or -1
#    if no such route exists
# - move_string is a string indicating the path, consisting of U, L, R, and D characters
#    (for up, left, right, and down)

def search(house_map):

    # Find both start and goal location
    pichu_loc=location_find("p", house_map)
    goal_loc=location_find("@", house_map)

    # Define a fringe as a set with the distance to the goal state calculated via Manhattan Distance
    # stored with a location (in this case the starting location) as a tuple.
    fringe = [(manhattan_distance(pichu_loc, goal_loc), pichu_loc)]

    # Convert our fringe to a priority queue so we can implement a modified form of A* where
    # we grab the element with the smallest Manhattan Distance to the goal location
    heapq.heapify(fringe)

    # Implement a set to track visited states. A set chosen here because lookup time is O(1) and
    # it is immutable so we never have to worry about losing states we've visited
    visited = set()

    # Implement a dictionary to track moves we've made. We need this to figure out our path and how we got there
    tracked_moves = dict()

    # Loop until the fringe is empty
    while fringe:

        # Get an element from the fringe. Because the fringe is a priority queue, it will always be the one with the
        # smallest Manhattan Distance to the goal location
        (curr_dist, curr_move)=heapq.heappop(fringe)

        # Add our element's coordinates to states we've visited
        visited.add(curr_move)

        # Check if our current location is the same as the goal location
        if curr_move == goal_loc:

            # Find the path we took to get to the goal state
            pth = path(tracked_moves, curr_move)

            # Figure out what direction the first move was
            directional_moves = move_classification(pichu_loc, pth[0])

            # For all other moves, find what direction they were
            for i in range(0, len(pth)-1):
                directional_moves += move_classification(pth[i], pth[i+1])

            # Return how many moves we took along with each of the moves
            return [len(directional_moves), directional_moves]
        
        # Our current location is not the goal location, so generate all successor states (valid states)
        # and iterate through them
        for move in moves(house_map, *curr_move):

            # Check if our move has been visited (seen) before. This is an optimization to A*
            if move in visited:
                continue
        
            else:

                # Our move has not been visited yet, so add it to the fringe with the Manhattan Distance to the
                # goal location
                heapq.heappush(fringe, tuple([manhattan_distance(move, goal_loc), move]))

                # Add our current move (successor) to tracked moves at the index of the original move 
                tracked_moves[move] = curr_move

    # We didn't find a valid solution, so return -1
    return [-1, ""]

# Main Function
if __name__ == "__main__":
    house_map=parse_map(sys.argv[1])
    print("Shhhh... quiet while I navigate!")
    solution = search(house_map)
    print("Here's the solution I found:")
    print(str(solution[0]) + " " + solution[1])