# **Assignment 2**
Completed by: Brad Cooley (bwcooley@iu.edu), McKenzie Quinn (mckquinn@iu.edu)

### _Opening Remarks_

This project consisted of three parts found in this [project description document](/a2-fa21.pdf) with my partner and I's implementation documented in a report-style format below.

_The code in this project is not perfect and optimizations can always be found. I would love to have a discussion about potential optimizations! Feel free to contact me (Brad Cooley) at my IU email above._

## **Part 1: Raichu**
_Implemented by Brad Cooley_

### _General Process and Implementation_

When first reading through this problem, the game of Raichu sounded like a combination of chess and checkers; indeed it is just that, but in an `N` dimensional space. So, using this understanding of the game, it was clear that how I structured the underlying game was going to be crucial to the performance of my minimax algorithm. So, I took an object oriented approach with the following design decisions:

- A parent `GamePiece` class, which stored information about a piece on the board like its coordinates, rank (for jumping), and color.
- Three child classes of `GamePiece`, `Pichu`, `Pikachu`, and `Raichu`.
- A `Board` class, which stored information about the current state of the board along with characteristics of the game like current pieces, who's turn it is, and the size of the board.
- Separate functions for each stage of the minimax algorithm.

Along with this design approach, I needed to figure out how to make my game play efficiently and effectively. This is where the decision of minimax comes in. Obviously minimax was the best choice for a game playing algorithm in this case. However, improvements could be made to the algorithm, like alpha-beta pruning. So, I implemented my minimax with alpha-beta pruning in order to allow minimax to search deeper (more moves ahead).

The overall implementation of the game just yields valid boards in an infinite loop with the depth of the minimax increasing by one with each iteration of the loop. That way, I didn't have to worry about a timeout since the program will be killed automatically by the grader and my program would (hopefully) output the best move, assuming a *best move* will always be given by a deeper and deeper tree.

### _Challenges_

While my object oriented approach was the right way to design this problem, it did come with many challenges. The funny thing is that the challenges it posed were not due to lack of understanding of the actual AI content I was trying to implement, but rather my lack of familiarity/comfortableness with OO design patterns and best practices. That is to say, the majority of issues that arose during development of this project were related to the object oriented design and not the actual AI and game playing algorithm I was implementing. There were a lot of edge/corner cases in this assignment as the game has many different mechanics and situations. Some problems faced consist of:

- Trying to implement minimax as a feature of the `Board` class instead of strictly making the `Board` class deal with its attributes and operations on the board (like `move`) and letting minimax live outside of that scope.
- Type checking errors. **_Lots_** of type checking errors.
- Understanding generators and their use in this assignment.
- and many more...

## **Part 2: The Game of Quintris**

_Implemented by McKenzie Quinn_

### _General Overview and Implementation_

In looking at this portion of the assignment, it was easily recognizable as a game we've played before, Tetris. This made understanding the game pretty simple, however when it comes to creating an algorithm that a computer would play off of proved to be challenging. In determining a possible solution, we utilized the following approach:

- Making copies of each game board to simulate moves on.
    - In order to simulate a move, we generated all possible piece moves (rotations and flips) starting at the leftmost column and continuing until the rightmost edge of the board.
    - We then took these moves and created a move sequence from them (a string of valid moves the game could interpret).
- After simulating the moves, we built our minimax tree with each node being a board with a different move.
    - The biggest challenge with this was determining a good evaluation function for ranking and scoring each of the boards.

### _Challenges_

As previously mentioned, creating an algorithm proved to be a challenge. We were able to figure out we would need to implement a expectiminimax but with no adversary, building a tree proved to be difficult.

In determining a way to evaluate our search, we started by looking at only the bottom row and finding the missing cells within that bottom row which helped determining if our code was operating the way we thought. After some debugging, we looked to find ways to improve our evaluation function. The next evaluation function tested calculated the amount of columns that were occupied by a piece. That seemed to do worse than our previous evaluation. But, when we combined the two and added in the state score, we were able to clear 1 row in testing.

We know this isn't the ideal implementation as the chance nodes in the tree should be based on the distribution of pieces and trying to predict a piece beyond the next piece to be played. However, we couldn't formulate a clear way to represent this in the code and the overall implementation of the algorithm.

## Part 3: Truth be Told

_Implementation by Brad Cooley and McKenzie Quinn_

### _General Process and Implementation_

In looking to tackle this problem, we broke the problem down into digestible pieces. To get started we wanted to identify the corpus of words within our training set. The following are the feature engineering tasked performed on our data:

- Making all text lower case
- Removed punctuation
- Removing stop words (frequently used words used little meaning)
- Removed any numbers

From there we looked to get word counts within the entire training set, the training set classified as truthful and the training set classified as deceptive. These counts allowed us to calculate the probability of a word, the probability of the word given a class and the probability of a class which are all components of determining the probability of the class given the words in the sentence. When calculating these probabilities, we took the log of the probabilities and summed them up for each word as we can run into errors with really small numbers in python.

Since our training set is a representation of our data and our test data may have words that are not included in our training set, we set the probability of words not found in our training set to .00001. We cannot set that value to 0 because it would 0 our probabilities.

We also attempted to implement a TF-IDF in place of counts as a way to improve model performance, however we ran out of time to get it working properly within our code. Regardless, we were able to obtain an accuracy of 85% on our test data.