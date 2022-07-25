# **Assignment 1**
Completed by: Brad Cooley (bwcooley@iu.edu), McKenzie Quinn (mckquinn@iu.edu)

### _Opening Remarks_

This project consisted of three parts found in this [project description document](/a1-fa21.pdf) with my partner and I's implementation documented in a report-style format below.

_The code in this project is not perfect and optimizations can always be found. I would love to have a discussion about potential optimizations! Feel free to contact me (Brad Cooley) at my IU email above._

## **Part 1: The 2021 Puzzle**
_Implemented by McKenzie Quinn_

### _Overview_

The goal of this problem is to find the least amount of moves that get you from our initial state to our goal state. We can break down our problem into the following abstraction:

- Our state space are the different configurations of a 5x5 board numbered 1 to 25.
- Our initial state is the 5x5 board whose tiles are labeled 1 to 25 in any order given by our input file
- Our goal state a transformed 5x5 board that is in order from the top left corner (1) to the bottom right (25).
- Our successor function is creating a new board based on each possible movement. Each movement could be to the right, left, up or down for any row or column or an outer or inner ring rotation clockwise or counterclockwise.
- Our cost function in this problem is simply 1 move.

In solving this problem, the following assumptions were made:

- There is always a possible solution based on the comments in the code. 
- The initial state is valid, meaning there are 25 elements from our file being read in.

To begin solving this problem, we worked out the code to make the different transformations. Once we got the left and right movements down, we realized by transposing the board we could reuse our left and right movements as up and down movements respectively. The function to transpose the board would also be useful in our outer and inner rotations in a similar matter. Unfortunately we figured this out before we learned we could use the test code for assistance.

Once that was figured out we needed to create our successor function to get all our successors given the different moves. From there we implemented search algorithm 3. When it came to determining our heuristic, it took a couple trips to office hours, however we ended up finding the amount of misplaced tiles / 16 and finding the manhattan distance / 16. We took the max between these two calculations as our heuristic. We are dividing by 16 because the largest amount of tiles moved at a given state is 16 (our outer clockwise or counter clockwise movements).

### _Problems Faced_

The biggest problem faced was determining the best heuristic to solve our problem. The trick being that not just one heuristic would do the trick, we needed to take the max of two heuristics to find the solution in a reasonable amount of time.

### _Optimizations_

Initially when calculating our heuristic, we had our goal state in a 2D array so it required a nested for loop to iterate through and make our calculations and this was done multiple times. This ate up time. Instead we put our state and goal state into their own hash tables for easy look up and the least amount of nested for loops.

Initially our heuristic functions were calculated in their own functions, requiring multiple loops that were not necessary.

### _Problem Specific Questions_

**Q: What is the branching factor of the search tree?**

**A:** The branching factor of this search tree is 23 since each node has 24 possible next states but there is always one successor that brings you to your previous state.

<br>

**Q: If the solution can be reached in 7 moves, about how many states would we need to explore before we found it if we used BFS instead of A\* search?**

**A:** If a solution can be reached in 7 moves using A* search, to find the same solution using BFS would require us to visit $24^{28}$ states (a lot!) since each state has 24 possible successor states and all states will be visited and evaluated.

## **Part 2: Road Trip!**

_Implemented by Brad Cooley_

### _Overview_

Our goal here was to find the shortest/fastest route between two cities for the following cost functions:

1) `Segments` - finds the route with the shortest number of segments between the two cities.

2) `Distance` - finds the route with the shortest distance (in miles) between the two cities.

3) `Time` - finds the fastest route with respect to time (in hours) betweenn the two cities.

4) `Delivery` - finds the fastest route with respect to delivery time (in hours) which is calculated by `t_road + p*2*(t_road + t_trip)` where `p` is determined by the speed of the road (if `p >= 50`, `p = tanh(l/1000)` where `l` is the length of the road, if `p < 50`, `p = 0`).

### _Problems Faced_

There was one major problem that I faced when solving this problem:

- The `Segments`, `Distance`, and `Time` cost functions were all relatively easy to implement. `Delivery` on the other hand was always giving me the second most optimal heuristic.
- After hours of debugging, I found the answer to my bug in [this community Q&A post](https://inscribe.education/main/indianau/6754110229500968/questions/6749461749628240?backToListTab=search&searchText=t_trip).
- The issue was I interpreted `t_trip` in the assignment writeup as the total time traveled as calculated by the summation of each edge's normal time, _not_ delivery time.
- Once I made this change to my code, the search algorithm was working.

### _Optimizations_

There weren't a lot of optimizations I used in my overall search algorithm. I was initially experiencing some slow performance with my `delivery` cost function and was contemplating caching delivery distance, but when I fixed my bug, it fixed the slowness of the cost function.

### _Problem Specific Questions_

**Q: What search abstraction did you use?**

**A:** I used a basic A* search with a few optimizations and different heuristics based on the cost function.

<br>

**Q: What is the state space?**

**A:** The state space is the set of all possible routes from the start city to the end city. This space gets narrowed down by our cost function and chosen heuristic.

<br>

**Q: What is the successor function?**

**A:** The successor function in this problem is built into my graph object. It is a function that explores all adjacent nodes to a specific node.

<br>

**Q: What are the edge weights?**

**A:** I designed my graph in such a way that it takes a dictionary with multiple edge weights so that all cost functions can be calculated entirely through the graph (with the exception of the delivery cost function).

<br>

**Q: What is the goal state?**

**A:** The goal state is the shortest/quickest route from the start city to the end city determined by the cost function.

<br>

**Q: What heuristics did you use and why are they admissible?**

**A:** I only used two heuristics for this assignment, mainly because I didn't see a need to use more than that. I'll explain the heuristic used based on the cost functions:

1) `Segments` - zero heuristic (Dijkstra's Algorithm)

    - This heuristic is admissible because a heuristic with a value of 0 will _always_ be admissible. I chose this heuristic for this cost function because Dijkstra's algorithm is guaranteed to always find the shortest distance between two nodes of a graph. While it can be inefficient at times, this heuristic/algorithm is the correct choice for this specific cost function.

2) `Distance` - Haversine Distance heuristic

    - This heuristic is not necessarily admissible by itself because the Haversine distance calculates the distance between two latitude and longitude coordinates. There is a possibility that this could overestimate the actual cost, so I multiply the result of the calculation by 0.01 to bring it into a range of values that will always underestimate the actual cost. Therefore, with this change to the heuristic, it will always be admissible.

3) `Time` - Haversine Distance heuristic

    - As explained above, I used the Haversine Distance again. I really didn't know what to use for this cost functions heuristic, so I contemplated using a heuristic of 0, as that is guaranteed to be admissible. However, it felt like I could use something a little more accurate and so I settled on using the Haversine Distance again.

4) `Delivery` - Haversine Distance heuristic

    - I chose to use this again because if it is admissible for the `time` cost function, then it will be admissible for the `delivery` cost function because the delivery time will always be greater than the normal travel time.

## **Part 3: Choosing Teams**

_Implemented by both Brad Cooley and McKenzie Quinn_

### _Overview_

Our goal here is to find the best grouping of students that will minimize the amount of time spent by the course staff. We can break down our problem into the following abstraction:

- The valid states in this problem are different groupings of all students where each grouping is of one, two, or three students.
- Our successor function (`assign.get_new_grouping()`) is creating new groupings of students in sizes of one, two, or three.
- Our cost function (`assign.cost_time()`)  is calculating the time spent on each set of groupings.
- Unlike previous problems our initial state was always given, however that is not the case here, so we set our initial state to be the state where everyone works on their own since that is always a possibility no matter the size of students.
- Our goal state is the set of groups of students that has the lowest cost to the staff.

Here we are assuming there is at least one student within our input file.

In determining how to solve the problem, we started by ensuring our cost function is performing accurately since this function is how we are evaluating the set of groups. The 3 main things we needed to keep track of was the desired group size for each student, the desired grouping of students and the undesired students each student has. To make looks up as quick as possible, all these preferences were put into a dictionary where the key was each students id and the value was a list of their preferences. This made preferences quick to look up.

Within the skeleton code there is a note stating that the solution will never be found, therefore we need to find the lowest possible option. With that being said, the code was written to find one grouping of all students at a time along with the cost associated with that group. If that cost is less than the previously yielded option, the new groping will be shown. This ensures the least time consuming set of groups found will be shown. Groups were randomly selected at random group sizes.  

### _Problems Faced_

The main problem faced was determining ways to dynamically select different sets of groups. We started by randomly selecting group sizes without taking preferences into account and letting the cost for a given set compared to a previous cost determine if the new set of groups should be viewed.  Otherwise the cost function is pretty straight forward since it boils down to counters and multiplication.

### _Optimizations_

A way for us to optimize our code would be to have a function were we take student preferences into account.

## **Resources**

Other things not explicitly mentioned as resources in this report:

- [Haversine Distance](https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula)