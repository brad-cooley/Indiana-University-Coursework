# **Assignment 0**
Completed by: Brad Cooley (bwcooley@iu.edu)

### _Project Description_

This project consisted of three parts found in this [project description document](/a0-fa21.pdf) with my implementation documented in a report-style format below.

_The code in this project is not perfect and optimizations can always be found. I would love to have a discussion about potential optimizations! Feel free to contact me at my IU email above._

## **Part 1: Routing Pichu**

### _Overview_

For routing Pichu, I choose to start off with an A* approach. I chose this because I knew that for larger boards, an algorithm like BFS or DFS was going to be quite slow. However, as I began to formulate my thoughts about edge cases and potential optimizations, I realized that I my heuristic would matter as well as how I went about pruning my search tree.

### _Problems Faced_

The toughest part of this assignment for me was figuring out how to track the path once we found the goal location. At first, I was trying to do this while the search was occurring. After seeing pseudocode on [Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm), I realized that I could not do it while searching, but rather had to keep track of the moves I was making, and then construct the optimal path at the end of the search. This was really the only major problem I faced during the development of this problem on the homework.

### _Optimizations_

As mentioned before, I had a realization that with choosing A* I was going to need to choose a good heuristic and potentially make some other small tweaks to the algorithm to get some desireable performance. For my heuristic, I originally went with a Manhattan Distance heuristic because the math was simpler, but I also experimented with a simple Euclidean distance for the heuristic as well. In the end, I saw no major difference between the two, so I went with my original approach of the Manhattan Distance.

Now that I had my heuristic, I needed a way to prune my search tree. While this wouldn't give me a major advantage time wise, it would help my algorithm be more lean memory wise. I decided to implement a set that would keep track of states we have visited so we don't explore them again. I chose a set in this instance because I wanted a constant time lookup to not bog my algorithm down. After all, if it's going to be an optimization, it can't increase it's time or space complexity! While thinking through this implementation, another optimization dawned on me.

I chose to implement the fringe as a priority queue with the Manhattan Distance (heuristic) as the dequeue factor. This way, I could guarantee that the move with the shortest distance to our goal state would always be explored before any other state. Now, this only holds for instances where there are no elements in the fringe that have the same distance to the goal state, but that was a trade off that I was willing to make. This optimization not only found my optimal path quicker, it also pruned my search tree inadvertently; a _true_ win-win!

### _Problem Specific Questions_

**Q: Why does the program often fail to find a solution?**

**A:** The original implementation that was given to us would often fail to find a solution for a multitude of reasons.

1. It always returns the same answer... so, um... well that is problematic.
2. There is no safeguard against visiting a state over and over again, causing an infinite loop.
3. The distance is never actually being calculated, it just always grows by 1 for each successor state we add. There is no way for us to every reach the goal state, unless by pure chance or the overall layout of the board being small enough for the agent to _rarely_ revisit states/the number of states it could revisit is small.

## **Part 2: Arranging Pichus**

### _Overview_

For arranging multiple Pichus on the same board, I immediately thought of the n-queens problem, just now we have obstacles and a board that isn't guaranteed to be square. These small nuances weren't huge roadblocks in terms of my approach, but I chose to do the simplest algorithm I knew, **B**readth **F**irst **S**earch.

### _Problems Faced_

I had a hard time thinking about how to start this problem because I wanted to use some sort of more complex search algorithm like simulated annealing, but I couldn't figure out how to turn my knowledge of it into code. I spent a couple days thinking about what I should do and I ended up just deciding to implement an algorithm I knew.

### _Optimizations_

I tried to apply a similar thought process to the one I had in part 1; was there a way to track visited states to try and prune the tree? The answer was **yes**, and I implemented it the same way I did in part 1. I used a set (immutable and constant lookup time), and stored states I had seen before as I explored them. While I'm not entirely sure how much of an impact this optimization had on a BFS approach, it was something to _hopefully_ speed up the search.

### _Problem Specific Questions_

**Q: What search abstraction did you use?**

**A:** I used BFS with some small optimizations.

<br>

**Q: What is the state space?**

**A:** The state space consists of all boards where one or more pichus are positioned in a way where they cannot see (attack) another pichu.

<br>

**Q: What is the initial state?**

**A:** The initial state is the map with one pichu on it.

<br>

**Q: What is the goal state?**

**A:** The goal state is a map that has _k_ number of pichus all in positions where they cannot see (attack) each other.

<br>

**Q: What is the successor function?**

**A:** The successor function is the action of adding a pichu onto the map until the desired number of pichus are present on the board in a valid manner.

<br>

**Q: What is the cost function?**

**A:** The cost function does not matter here as we are not keeping track of a cost per step taken.

## **Resources**

Other things not explicitly mentioned as resources in this report:

- [My own Google Sheet to visualize maps and how my agent was moving through the state space](https://docs.google.com/spreadsheets/d/1ug_j8y07_nl3S0-9aca4YZz-RmQe1A9PVFCvDBEChg4/edit?usp=sharing)
- The textbook, specifically pages 97-109
- The class Q&A forum
