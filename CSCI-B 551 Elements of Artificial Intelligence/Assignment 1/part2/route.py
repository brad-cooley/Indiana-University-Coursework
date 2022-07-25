#!/usr/local/bin/python3
# route.py : Find routes through maps
#
# Code by: Brad Cooley <redacted>, McKenzie Quinn <redacted>
#
# Based on skeleton code by V. Mathur and D. Crandall, January 2021
#


# !/usr/bin/env python3

import sys, heapq, itertools, math

class Graph:
    """
    Graph class with usage:
        G = Graph()
            - creates an undirected graph

    Methods:
        add_node(node)
            - adds a node to the graph

        add_edge(node1, node2, weight)
            - adds an edge between two nodes in the graph
            - if either node does not exist, a node is created
            - edges are two directional (i.e. goes from node1 to node2 and node2 to node1)
            - weight can be anything including an object or a single value
        
        get_adjacent(node) --> list[strings]
            - get's all adjacent nodes for a given node
        
        get_edge(node1, node2) --> list[string, dictionary]
            - get's an edge and edge's weight between two nodes

        has_node(node) --> boolean
            - checks Graph for a given node
        
        size() --> dictionary{string:int, string:int}
            - gets the size of the Graph in both the number of nodes and edges it is comprised of

    """

    def __init__(self):
        self.__graph = {}
        self.__nodes = 0
        self.__edges = 0

    def add_node(self, n):
        if n not in self.__graph:
            self.__nodes += 1
            self.__graph[n] = []

    def add_edge(self, n1, n2, w):
        if n1 not in self.__graph:
            self.add_node(n1)
        
        if n2 not in self.__graph:
            self.add_node(n2)

        n1_to_n2 = [n2, w]
        n2_to_n1 = [n1, w]

        # Add edges both ways as the graph is undirected
        self.__graph[n1].append(n1_to_n2)
        self.__graph[n2].append(n2_to_n1)

        # increasing by 2 as there are two new edges added
        self.__edges += 2

    def get_adjacent(self, n):
        return self.__graph[n]

    def get_edge(self, n1, n2):
        for entry in self.__graph[n1]:
            if entry[0] == n2:
                return entry

        return []

    def has_node(self, n):
        try:
            if self.__graph[n]:
                return True
        except (KeyError):
            return False

    def size(self):
        return {'nodes':self.__nodes, 'edges':self.__edges}

def graph_creation():
    """
    Method to create a graph given the cities and road segments provided to us.

    Parameters:
        None

    Returns:
        cities --> dictionary{str:tuple(str, str)}
            - dictionary containing all cities with their associated latitude and longitude coordinates stored as a tuple of strings
        G --> Graph
            - Graph object containing all cities as nodes and the roadways connecting them as edges
        
    """

    gps = open('city-gps.txt', 'r')
    cities = gps.readlines()

    rm = open('road-segments.txt', 'r')
    segments = rm.readlines()

    G = Graph()
    ct = dict()

    for city in cities:
        line = city.split()
        ct[line[0]] = tuple([line[1], line[2]])
        G.add_node(line[0])

    for segment in segments:
        line = segment.split()
        G.add_edge(line[0], line[1], {'distance':int(line[2]), 'time':(int(line[2])/int(line[3])), 'speed':int(line[3]), 'name':line[4]})    

    return ct, G

def hav_form(n1, n2, cities):
    """
    Method to calculate the distance between latitude and longitude coordinates (Haversine formula)
    Based on code found here: https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula

    Parameters:
        n1 --> str
            - name of a node (city) in the Graph
            - used for lookup in cities dictionary
        n2 --> str
            - name of a node (city) in the Graph
            - used for lookup in cities dictionary
        cities --> dictionary
            - dictionary of all cities so latitude and longitude coordinates can be searched for

    Returns:
        dist --> float
            - distance between two latitude and longitude coordinates represented as a floating point number

    """

    # Try catch loop to handle if a city does not exist in our cities dictionary
    try:
        lat1 = float(cities[n1][0])
        long1 = float(cities[n2][0])
        lat2 = float(cities[n1][1])
        long2 = float(cities[n2][1])
    except (KeyError):

        # return 0 as 0 is always an admissible heuristic for a* (becomes Dijkstra's alg.)
        return 0

    # radius of the earth in miles
    r = 3958.8
    theta1 = math.sin((lat2-lat1)/2.0)**2
    theta2 = math.cos(lat1)*math.cos(lat2)*math.sin((long2-long1)/2)**2
    dist = float(2.0*r + math.asin(math.sqrt(theta1+theta2)))

    return dist

def human_path(path, G):
    """
    Method that takes a final path and creates it into a list of human readable directions

    Parameters:
        path --> list
            - an ordered list of cities visited
        G --> Graph
            - Graph object containing all cities as nodes and the roadways connecting them as edges

    Returns:
        result --> list
            - a parsed list containing tuples with the destination city of an edge and a string displaying the road taken and distance traveled

    """

    result = list()

    for i in range(0, len(path)-1):
        edge = G.get_edge(path[i], path[i+1])
        string = '{0} for {1} miles'.format(edge[1]['name'], edge[1]['distance'])
        result.append((edge[0], string))

    return result

def delivery_calculation(path, G):
    """
    Method to calculate the delivery cost of a certain path

    Parameters:
        path --> list
            - an ordered list of cities visited
        G --> Graph
            - Graph object containing all cities as nodes and the roadways connecting them as edges

    Returns:
        t_trip --> float
            - a floating point number that is the result of the delivery cost function calculation
        
    """

    t_trip = 0.0

    for i in range(0, len(path)-1):
        edge = G.get_edge(path[i], path[i+1])

        if not edge:
            continue
        if edge[1]['speed'] >= 50.0:
            prob = math.tanh(edge[1]['distance']/1000.0)
        else:
            prob = 0.0

        t_road = edge[1]['time']
        t_trip += t_road + (prob*(2.0*(t_road+t_trip)))

    return t_trip

def total_metric(path, G, metric):
    """
    Method to calculate the summation of a specific weight metric (distance, time, etc.)

    Parameters:
        path --> list
            - an ordered list of cities visited
        G --> Graph
            - Graph object containing all cities as nodes and the roadways connecting them as edges
        metric --> string
            - the name of the weight metric wanted to sum (distance, time, etc.)

    Returns:
        result --> float
            - a floating point number that is the summation of a specified edge weight metric
        
    """

    result = 0.0

    for i in range(0, len(path)-1):
        edge = G.get_edge(path[i], path[i+1])
        if not edge:
            continue
        result+= float(edge[1][str(metric)])

    return result

def a_star(start, end, cost):
    """
    Method that searches a graph using the A* search algorithm

    Parameters:
        start --> string
            - the starting city of the search
        end --> string
            - the ending or goal city of the search
        cost --> string
            - the name of the cost function used (optimization metric)

    Returns:
        list
            - a list containing the following information
                1. route-taken --> list
                    - a list of tuples containing a city and the road taken to get to that city and for how long
                2. total-miles --> float
                    - total number of miles travelled for the route
                3. total-hours --> float
                    - total number of hours taken for the route
                4. total-delivery-hours --> float
                    - total number of delivery hours taken for the route
        
    """

    cities, G = graph_creation()

    # cleaner and easier than using count+=1 at the end of the loop
    count = itertools.count()

    # priority, counter, node, cost, parent
    fringe = [(0, next(count), start, 0, None)]
    
    visited = dict()
    tracked_nodes = dict()

    # Loop until the fringe is empty
    while fringe:

        _, __, curr_node, distance, parent_node = heapq.heappop(fringe)

        # Check if our current location is the same as the goal location
        if curr_node == end:

            # Find the path we took to get to the goal state
            path = [curr_node]
            
            node = parent_node
            while node is not None:
                path.append(node)
                node = tracked_nodes[node]
            path.reverse()
            return [human_path(path, G), total_metric(path, G, 'distance'), total_metric(path, G, 'time'), delivery_calculation(path, G)]

        if curr_node in tracked_nodes:
            if tracked_nodes[curr_node] is None:
                continue

            # skip bad paths that were enqueued before finding a better one
            qcost, h = visited[curr_node]
            if qcost < distance:
                continue

        tracked_nodes[curr_node] = parent_node
    
        for move in G.get_adjacent(curr_node):

            neighbor = move[0]
            weight = move[1]

            if cost == 'segments':
                ncost = distance + 1
            elif cost == 'delivery':
                path1 = [neighbor]
                node = curr_node

                while node is not None:
                    path1.append(node)
                    node = tracked_nodes[node]
                path1.reverse()
                
                ncost = float(delivery_calculation(path1, G))
            else:
                ncost = distance + weight[cost]

            # Check if our move has been visited (seen) before
            if neighbor in visited:
                qcost, h = visited[neighbor]

                if qcost <= ncost:
                    continue
        
            else:
                if cost == 'segments':
                    h = 0 # Dijkstra's algorithm to find shortest path
                else:
                    h = hav_form(neighbor, end, cities) * 0.01
            visited[neighbor] = ncost, h
            heapq.heappush(fringe, (ncost + h, next(count), neighbor, ncost, curr_node))

    return None

def get_route(start, end, cost):
    
    """
    Find shortest driving route between start city and end city
    based on a cost function.

    1. Your function should return a dictionary having the following keys:
        -"route-taken" : a list of pairs of the form (next-stop, segment-info), where
           next-stop is a string giving the next stop in the route, and segment-info is a free-form
           string containing information about the segment that will be displayed to the user.
           (segment-info is not inspected by the automatic testing program).
        -"total-segments": an integer indicating number of segments in the route-taken
        -"total-miles": a float indicating total number of miles in the route-taken
        -"total-hours": a float indicating total amount of time in the route-taken
        -"total-delivery-hours": a float indicating the expected (average) time 
                                   it will take a delivery driver who may need to return to get a new package
    2. Do not add any extra parameters to the get_route() function, or it will break our grading and testing code.
    3. Please do not use any global variables, as it may cause the testing code to fail.
    4. You can assume that all test cases will be solvable.
    5. The current code just returns a dummy solution.
    """

    if cost == 'segments':
        route_taken, dst, time_taken, delivery_time = a_star(start, end, 'segments')
        
    elif cost == 'distance':
        route_taken, dst, time_taken, delivery_time = a_star(start, end, 'distance')

    elif cost == 'time':
        route_taken, dst, time_taken, delivery_time = a_star(start, end, 'time')
        
    elif cost == 'delivery':
        route_taken, dst, time_taken, delivery_time = a_star(start, end, 'delivery')
    
    elif cost == 'statetour':
        #TSP goes here
        return 0

    return {"total-segments" : len(route_taken), 
            "total-miles" : float(dst), 
            "total-hours" : float(time_taken), 
            "total-delivery-hours" : float(delivery_time), 
            "route-taken" : route_taken}

# Please don't modify anything below this line
#
if __name__ == "__main__":

    if len(sys.argv) != 4:
        raise(Exception("Error: expected 3 arguments"))

    (_, start_city, end_city, cost_function) = sys.argv
    if cost_function not in ("segments", "distance", "time", "delivery", "statetour"):
        raise(Exception("Error: invalid cost function"))

    result = get_route(start_city, end_city, cost_function)

    # Pretty print the route
    print("Start in %s" % start_city)
    for step in result["route-taken"]:
        print("   Then go to %s via %s" % step)

    print("\n          Total segments: %4d" % result["total-segments"])
    print("             Total miles: %8.3f" % result["total-miles"])
    print("             Total hours: %8.3f" % result["total-hours"])
    print("Total hours for delivery: %8.3f" % result["total-delivery-hours"])