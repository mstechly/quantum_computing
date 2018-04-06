import time
from qtsp_subtree.src import TSP_utilities 
from qtsp_subtree.src.forest_tsp_solver import ForestTSPSolver
import numpy as np
import pdb
import csv
import sys
import random

def run_testing_sequence(number_of_nodes=3):
    file_time = time.time()
    results_file = open("phase_1_results_" + str(file_time) + ".csv", 'w')
    angles_file = open("phase_1_angles_" + str(file_time) + ".csv", 'w')
    list_of_embeddings = np.genfromtxt("embeddings_3.csv")
    results_file.write("steps,tol,time,valid_prob,best_valid,optimal_cost,forest_cost,best_sol_prob\n")
    csv_writer = csv.writer(results_file)
    csv_writer_angles = csv.writer(angles_file)

    for flat_nodes_array in list_of_embeddings:
        nodes_array = np.reshape(flat_nodes_array, (number_of_nodes,2))
        steps = 3
        xtol = 10e-4
        run_single_tsp(nodes_array, csv_writer, csv_writer_angles, steps, xtol)
    results_file.close()


def run_single_tsp(nodes_array, csv_writer, csv_writer_angles, steps, xtol, all_ones=-2):
    params = [steps, xtol]
    print(steps, xtol)
    ftol = xtol
    start_time = time.time()
    forest_solver = ForestTSPSolver(nodes_array, steps=steps, xtol=xtol, ftol=ftol, all_ones_coefficient=all_ones)
    
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
    # [print(el) for el in forest_solver.create_cost_operators()]
    if csv_writer is not None:
        csv_writer.writerow(row)
        csv_writer_angles.writerow(row)
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
