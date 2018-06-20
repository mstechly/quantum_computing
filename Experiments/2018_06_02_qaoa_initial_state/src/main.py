import time
from qtsp_subtree.src import TSP_utilities 
from qtsp_subtree.src.forest_tsp_solver import ForestTSPSolver
from qtsp_subtree.src.forest_tsp_solver import visualize_cost_matrix
import numpy as np
import pdb
import csv
import sys
import random

def run_testing_sequence(number_of_nodes=3, is_random=True):
    file_time = time.time()
    file_tag = "initial_state_tests"
    results_file = open(file_tag + "_results_" + str(file_time) + ".csv", 'w')
    angles_file = open(file_tag + "_angles_" + str(file_time) + ".csv", 'w')
    results_file.write("case,initial_state,steps,tol,time,optimal_cost,forest_cost,best_sol_prob\n")

    possible_cases = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    possible_initial_states = [[2, 1, 0], [2, 0, 1], "all"]
    while True:
        steps = 2
        xtol = 1e-3
        case = random.choice(possible_cases)
        if number_of_nodes == 3:
            nodes_array = np.array([[0,0],[1,1],[2,2]])
            initial_state = [0,1,2]
        elif number_of_nodes == 4:
            nodes_array = np.array([[0,0],[1,1],[2,2],[3,3]])
            initial_state = [0,1,2,3]
        run_single_tsp(nodes_array, results_file, angles_file, steps, xtol, case, initial_state)
    results_file.close()

def run_single_tsp(nodes_array, results_file, angles_file, steps, xtol, case, initial_state):
    params = [steps, xtol]
    print(steps, xtol)
    ftol = xtol
    start_time = time.time()
    forest_solver = ForestTSPSolver(nodes_array, steps=steps, xtol=xtol, ftol=ftol, initial_state=initial_state)
    
    [betas, gammas] = forest_solver.find_angles()
    print(betas)
    print(gammas)

    forest_solver.betas = betas
    forest_solver.gammas = gammas
    results = forest_solver.get_results()
    end_time = time.time()
    calculation_time = end_time - start_time

    brute_force_solution = TSP_utilities.solve_tsp_brute_force(nodes_array)
    cost_matrix = TSP_utilities.get_tsp_matrix(nodes_array)
    optimal_cost = TSP_utilities.calculate_cost(cost_matrix, brute_force_solution)

    solution = forest_solver.get_solution()
    forest_cost = TSP_utilities.calculate_cost(cost_matrix, solution)
    best_solution_probability = results[0][1]

    row = [case, initial_state] + params + [calculation_time] + [optimal_cost, forest_cost, best_solution_probability]
    print(row)
    print("Results", results)

    csv_writer = csv.writer(results_file)
    csv_writer_angles = csv.writer(angles_file)

    csv_writer.writerow(row)
    csv_writer_angles.writerow(row)
    csv_writer_angles.writerow(nodes_array)
    csv_writer_angles.writerow(results)
    csv_writer_angles.writerow(betas)
    csv_writer_angles.writerow(gammas)
    csv_writer_angles.writerow("\n")
    results_file.flush()
    angles_file.flush()
    sys.stdout.flush()


def main():
    run_testing_sequence(number_of_nodes=4)


if __name__ == '__main__':
    main()
