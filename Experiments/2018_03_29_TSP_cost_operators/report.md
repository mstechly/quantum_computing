# TSP cost operators test

## Introduction

While working on the script for solving Traveling Salesman Problem with quantum computer, I encountered the following problems:

- the results were not consistent - for the same parameters I could got different results depending on how the final angles for QAOA.
- I've observed some correlaction between the QAOA parameters and quality of results, but I wasn't able to say how exactly changes in parameters influences time of computation and quality of the results.
- due to that it was hard to determine if the changes I've introduced to the cost_operators are actually helping to achieve desirable results.

Taking all of the above into the account I decided to take a more systematic approach.

The main goals of this experiment were:
- Create a setup for systematic testing different sets of parameters
- Find set of parameters that's working reasonably well
- Check what's the proper coefficient for all_ones_term 

## Dependencies

TODO

## Experiment description

The whole experiment was performed on a 3-nodes graph. 
The case of 2 nodes was trivial, and for 4 nodes the calculations took too much time.

### Phase 1

In the first phase I've created a script for running forest_tsp_solver with different parameters.
Parameters I was changing were: `steps` and `tol`.  `steps` is number of steps in the QAOA algorithms. `xtol` and `ftol` are parameters of the classical minizer used in QAOA, however I used the same value for both of them and called it `tol`.

Since running Forest code requires internet access and I didn't have access to reliable internet connection, I decided to use randomized choice of parameters. 
This way I was sure that even if the internet connection is broken, none set of parameters will be over or under represented in my results.

The best set of parameters was `steps=3` and `tol=1e-4`. The more detailed results can be found below.

### Phase 2

After finding a reasonably good set of parameters in Phase 1, I used it to find proper coefficients for all_ones_term in forest_tsp_solver.
This term is used to ban [1, 1, 1] groups in the TSP solution.

During the initial run I crossed out values of 1 and 2 of the coefficient and decided to test values of -1 and -2.

Both values gave very similar results - the proper solution was the most probable in about 73% of cases, and the mean number of correct solutions was about 3300/10000.
Since there was not huge difference between these values, I decided to use the value of -1.

### Phase 3

TODO

## Results

TODO