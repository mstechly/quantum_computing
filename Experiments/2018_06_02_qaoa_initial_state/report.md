# Hadfield QAOA - initial states

## Introduction

The goal of this experiment was to check how implementation of Hadfield's QAOA works when initialized with various initial states.

## Dependencies

As a main engine for solving TSP I'm code from this repository: https://github.com/BOHRTECHNOLOGY/quantum_tsp, imported as a subtree.

I was using pyquil and grove.
Pyquil: commit hash: `26ae363e9f5c85dc3aab298daebc9ec5023a32a1`
Grove: commit hash: `e3fd7b9f3188e820dd19ff487dbf56c8faf43822`

The exact versions of these repositories are commited to this project.

## Tests

TODO

## Appendix - City placement

Here is a list of the city placement I was using. Below I describe them with the following information:
- Symmetrical/Asymmetrical
- Order of the optimal route: e.g. [0 -> 1 -> 2]. In all cases at least two orderings were correct, since we don't specify the starting point.
- Coordinates e.g.: [[0, 0], [0, 10], [0, 20]]
- 1D / 2D - were all the points on one line or not.


The coordinates were randomly scaled and shifted, so those listed here are just an example.

0. 1D, Symmetrical, [0 -> 1 -> 2] 
[[0, 0], [0, 10], [0, 20]] 

1. 1D, Symmetrical [0 -> 2 -> 1]
[[0, 0], [0, 20], [0, 10]]

2. 1D, Symmetrical [1 -> 0 -> 2]
[[0, 10], [0, 20], [0, 0]]

3. 1D, Asymmetrical [0 -> 1 -> 2]
[[0, 0], [0, 1], [0, 10]]

4. 1D, Asymmetrical [2 -> 0 -> 1]
[[0, 1], [0, 0], [0, 10]]

5. 2D, Symmetrical (equilateral angle), all orderings are the same
[[0, 0], [1, 0], [0.5, np.sqrt(3)/2]]

6. 2D, Symmetrical triangle [0 -> 2 -> 1]
[[-5, 0], [5, 0], [0, 1]]

7. 2D, Assymetrical triangle [0 -> 2 -> 1]
[[0, 0], [15, 0], [0, 1]]

8. 2D, random triangle
In this case it was just a set of random points, so each case was different.