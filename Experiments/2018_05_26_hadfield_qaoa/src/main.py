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
    # 1D cases:
    # ARRAY 1: [0 - 1 - 2], symmetrical
    # nodes_array = np.array([[0, 0], [0, 10], [0, 20]])
    # # ARRAY 2: [0 - 2 - 1], symmetrical
    # nodes_array = np.array([[0, 0], [0, 20], [0, 10]])
    # # ARRAY 3: [2 - 1 - 0], symmetrical
    # nodes_array = np.array([[0, 20], [0, 10], [0, 0]])
    # # ARRAY 4: [0 - 1 - 2] assymetrical
    # nodes_array = np.array([[0, 0], [0, 1], [0, 10]])
    # # ARRAY 5: [2 - 0 - 1] assymetrical
    # nodes_array = np.array([[0, 1], [0, 0], [0, 10]])

    # # 2D cases:
    # # ARRAY 1: equilateral triangle
    nodes_array = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2]])
    # # ARRAY 2: symetrical triangle [0 - 2 - 1]
    # nodes_array = np.array([[-5, 0], [5, 0], [0, 1]])
    # # ARRAY 3: asymetrical triangle [0 - 2 - 1]
    # nodes_array = np.array([[0, 0], [15, 0], [0, 1]])
    # # ARRAY 4: random array
    # nodes_array = None

    file_time = time.time()
    file_tag = "2d_1"
    results_file = open(file_tag + "_results_" + str(file_time) + ".csv", 'w')
    angles_file = open(file_tag + "_angles_" + str(file_time) + ".csv", 'w')
    results_file.write("steps,tol,time,valid_prob,best_valid,optimal_cost,forest_cost,best_sol_prob\n")
    csv_writer = csv.writer(results_file)
    csv_writer_angles = csv.writer(angles_file)

    possible_steps = [3, 2, 1]
    possible_xtol = [1e-4, 1e-3, 1e-2]
    if is_random:
        while True:
            steps = random.choice(possible_steps)
            xtol = random.choice(possible_xtol)

            if nodes_array is None:
                nodes_list = []
                for i in range(number_of_nodes):
                    nodes_list.append(np.random.rand(2) * 10)
                scaled_nodes_array = np.array(nodes_list)
            else:
                scaled_nodes_array = nodes_array * np.random.rand() * 5 + 5 * (np.random.rand() - 0.5)
            run_single_tsp(scaled_nodes_array, csv_writer, csv_writer_angles, steps, xtol)
    else:
        for steps in possible_steps:
            for xtol in possible_xtol:
                for i in range(10):
                    run_single_tsp(nodes_array, csv_writer, csv_writer_angles, steps, xtol)
    results_file.close()

def run_single_tsp(nodes_array, csv_writer, csv_writer_angles, steps, xtol):
    params = [steps, xtol]
    print(steps, xtol)
    ftol = xtol
    start_time = time.time()
    forest_solver = ForestTSPSolver(nodes_array, steps=steps, xtol=xtol, ftol=ftol)
    
    [betas, gammas] = forest_solver.find_angles()
    print(betas)
    print(gammas)

    forest_solver.betas = betas
    forest_solver.gammas = gammas
    results = forest_solver.get_results()
    end_time = time.time()
    calculation_time = end_time - start_time
    metrics = calculate_metrics(results, calculation_time)


    brute_force_solution = TSP_utilities.solve_tsp_brute_force(nodes_array)
    cost_matrix = TSP_utilities.get_tsp_matrix(nodes_array)
    optimal_cost = TSP_utilities.calculate_cost(cost_matrix, brute_force_solution)

    solution = forest_solver.get_solution()
    forest_cost = TSP_utilities.calculate_cost(cost_matrix, solution)
    best_solution_probability = results[0][1]

    row = params + metrics + [optimal_cost, forest_cost, best_solution_probability]
    print(row)
    print("Best results", results[:10])
    print("Worst results", results[-10:])

    if csv_writer is not None:
        csv_writer.writerow(row)
        csv_writer_angles.writerow(row)
        csv_writer_angles.writerow(nodes_array)
        csv_writer_angles.writerow(results)
        csv_writer_angles.writerow(betas)
        csv_writer_angles.writerow(gammas)
        csv_writer_angles.writerow("\n")
    sys.stdout.flush()


def check_if_solution_is_valid(solution):
    solution = list(solution)
    number_of_nodes = int(np.sqrt(len(solution)))
    time_groups = [solution[number_of_nodes*i:number_of_nodes*(i+1)] for i in range(number_of_nodes)]
    for group in time_groups:
        if np.sum(group) != 1:
            return False
        if time_groups.count(group) != 1:
            return False
    return True


def calculate_metrics(results, calculation_time):
    valid_results_probability = 0
    for entry in results:
        if check_if_solution_is_valid(entry[0]):
            valid_results_probability += entry[1]

    best_result = results[0][0]
    best_result_valid = check_if_solution_is_valid(best_result)
    return [calculation_time, valid_results_probability, best_result_valid]


def main():
    run_testing_sequence(number_of_nodes=3)


if __name__ == '__main__':
    main()
