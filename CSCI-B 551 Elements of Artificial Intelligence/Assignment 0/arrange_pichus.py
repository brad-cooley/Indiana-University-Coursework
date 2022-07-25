#!/usr/local/bin/python3
#
# arrange_pichus.py : arrange agents on a grid, avoiding conflicts
#
# Submitted by : Brad Cooley <redacted>
#
# Based on skeleton code in CSCI B551, Fall 2021.

import sys

# Parse the map from a given filename
def parse_map(filename):
	with open(filename, "r") as f:
		return [[char for char in line] for line in f.read().rstrip("\n").split("\n")][3:]

# Count total # of pichus on house_map
def count_pichus(house_map):
    return sum([ row.count('p') for row in house_map ] )

# Return a string with the house_map rendered in a human-pichuly format
def printable_house_map(house_map):
    return "\n".join(["".join(row) for row in house_map])

# Add a pichu to the house_map at the given position, and return a new house_map (doesn't change original)
def add_pichu(house_map, row, col):
    return house_map[0:row] + [house_map[row][0:col] + ['p',] + house_map[row][col+1:]] + house_map[row+1:]

# Get list of successors of given house_map state
def successors(house_map):
    return [ add_pichu(house_map, r, c) for r in range(0, len(house_map)) for c in range(0,len(house_map[0])) if house_map[r][c] == '.' ]

# check if house_map is a goal state
def is_goal(house_map, k):
    return count_pichus(house_map) == k

# Find the location ((x, y) coordinates) of a given character in the map
def location_find(char, house_map):
  return [(row_i,col_i) for col_i in range(len(house_map[0])) for row_i in range(len(house_map)) if house_map[row_i][col_i]==str(char)]

# Check if a row is valid (no pichu can see another pichu)
# row is a list of characters
# ex: ['.', 'X', 'p', '.']
def row_check(row):

    pichu_seen = False

    for pos in row:
        if pos == '.':
            continue
        elif pos == 'X':
            if pichu_seen:
                pichu_seen = False
            else:
                continue
        elif pos == 'p':
            if pichu_seen:
                return False
            else:
                pichu_seen = True

    return True

# Check if a column is valid (no pichu can see another pichu)
# col is an integer that is used as an index in map
def col_check(map, col):
    pichu_seen = False

    for i in range(0, len(map)):
        if map[i][col] == '.':
            continue
        elif map[i][col] == 'X' or map[i][col] == '@':
            if pichu_seen:
                pichu_seen = False
            else:
                continue
        elif map[i][col] == 'p':
            if pichu_seen:
                return False
            else:
                pichu_seen = True

    return True

# Check if all diagonals are valid (no pichu can see another pichu)
# loc is a tuple representing an (x, y) coordinate that is used for indices in the map
def diag_check(map, loc):

    i = loc[0] - 1
    j = loc[1] - 1

    # NW (left & up)
    while i >= 0 and j >=0:
        if map[i][j] == 'X' or map[i][j] == '@':
            break
        elif map[i][j] == 'p':
            return False
        else:
            i = i-1
            j = j-1
            continue

    i = loc[0] + 1
    j = loc[1] - 1

    # SW (left & down)
    while i < len(map) and j >=0:

        if map[i][j] == 'X' or map[i][j] == '@':
            break
        elif map[i][j] == 'p':
            return False
        else:
            i = i+1
            j = j-1
            continue

    i = loc[0] - 1
    j = loc[1] + 1

    # NE (right & up)
    while i >= 0 and j < len(map[0]):
        if map[i][j] == 'X' or map[i][j] == '@':
            break
        elif map[i][j] == 'p':
            return False
        else:
            i = i-1
            j = j+1
            continue

    i = loc[0] + 1
    j = loc[1] + 1

    # SE (right & down)
    while i < len(map) and j < len(map[0]):
        
        if map[i][j] == 'X' or map[i][j] == '@':
            break
        elif map[i][j] == 'p':
            return False
        else:
            i = i+1
            j = j+1
            continue

    return True

# Check if a map is valid (no pichu can see another pichu)
def valid_map(house_map):

    locs = location_find('p', house_map)

    for loc in locs:
        if not row_check(house_map[loc[0]]):
            return False
        if not col_check(house_map, loc[1]):
            return False
        if not diag_check(house_map, loc):
            return False

    return True

# Arrange agents on the map
#
# This function MUST take two parameters as input -- the house map and the value k --
# and return a tuple of the form (new_house_map, success), where:
# - new_house_map is a new version of the map with k agents,
# - success is True if a solution was found, and False otherwise.
#
def solve(initial_house_map,k):

    # Define a fringe as a set with the inital house_map (list of lists)
    fringe = [initial_house_map]

    # Implement a set to track visited states. A set chosen here because lookup time is O(1) and
    # it is immutable so we never have to worry about losing states we've visited
    visited = set()

    # Loop until the fringe is empty
    while fringe:

        # Get an element from the fringe. Because the fringe is a queue, it will always be the first
        # element in the list
        map = fringe.pop()

        # Add the map to visited states. We call printable_house_map here as it gives us a string, which
        # is a hashable item for our set
        visited.add(printable_house_map(map))

        # Generate all successor states (valid states) and iterate through them
        for new_house_map in successors(map):

            # Turn the map into a string so we can hash it and check if it is in visited
            state = printable_house_map(new_house_map)

            # Check if we've seen this state before
            if state in visited:
                continue
            
            # Check if our map is valid
            if valid_map(new_house_map):
                
                # If our map is valid, we now want to see if it meets our goal requirements in terms of
                # number of pichus on the map
                if is_goal(new_house_map,k):
                    return(new_house_map,True)
                
                # Our valid map does not meet the criteria we stated as the goal, so add it to the fringe
                fringe.append(new_house_map)

    return(house_map, False)

# Main Function
if __name__ == "__main__":
    house_map=parse_map(sys.argv[1])
    # This is k, the number of agents
    k = int(sys.argv[2])
    print ("Starting from initial house map:\n" + printable_house_map(house_map) + "\n\nLooking for solution...\n")
    solution = solve(house_map,k)
    print ("Here's what we found:")
    print (printable_house_map(solution[0]) if solution[1] else "False")