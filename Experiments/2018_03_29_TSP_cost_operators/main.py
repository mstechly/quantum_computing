import time
from qtsp_subtree.src import TSP_utilities 
from qtsp_subtree.src.forest_tsp_solver import ForestTSPSolver
import numpy as np
import pdb
import csv
import sys

def main():
    # nodes_array = np.array([[0, 0], [0,5], [5,5], [5,0]])
    nodes_array = np.array([[0, 0], [0,5], [0,10]])
    # nodes_array = np.array([[0, 0], [0,5]])
    results_file = open("results_3_nodes_6.csv", 'w')

    results_file.write("steps,tol,id,valid_prob,almost_valid_prob,time,best_valid,best_almost_valid\n")
    wr = csv.writer(results_file)
    for steps in [3,2,1]:
        for xtol in [1e-4, 1e-3, 1e-2]:
            for i in range(10):
                # if i<5:
                #     continue
                params = [steps, xtol, i]
                print(steps, xtol, i)
                ftol = xtol
                start_time = time.time()
                forest_solver = ForestTSPSolver(nodes_array, steps=steps, xtol=xtol, ftol=ftol)
                [betas, gammas] = forest_solver.find_angles()
                # betas = np.array([1.40268584, 2.74136728, 2.76970739])
                # gammas = np.array([1.41543072, 1.56411558, 2.29933395])
                forest_solver.betas = betas
                forest_solver.gammas = gammas
                results = forest_solver.get_results()
                end_time = time.time()
                calculation_time = end_time - start_time
                metrics = calculate_metrics(results, calculation_time)
                row = params + metrics
                print(row)
                wr.writerow(row)
                sys.stdout.flush()
    results_file.close()


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


def check_if_solution_is_almost_valid(solution):
    solution = list(solution)
    number_of_nodes = int(np.sqrt(len(solution)))
    time_groups = [solution[number_of_nodes*i:number_of_nodes*(i+1)] for i in range(number_of_nodes)]
    for group in time_groups:
        if np.sum(group) != 1 or np.sum(group) != number_of_nodes:
            return False
        if np.sum(group) == 1 and time_groups.count(group) != 1:
            return False
    return True


def calculate_metrics(results, calculation_time):
    valid_results_probability = 0
    almost_valid_results_probability = 0
    for entry in results:
        if check_if_solution_is_valid(entry[0]):
            valid_results_probability += entry[1]
        elif check_if_solution_is_almost_valid(entry[0]):
            almost_valid_results_probability += entry[1]

    best_result = results[0][0]
    best_result_valid = check_if_solution_is_valid(best_result)
    best_result_almost_valid = check_if_solution_is_almost_valid(best_result)
    return [valid_results_probability, almost_valid_results_probability, calculation_time, best_result_valid, best_result_almost_valid]


if __name__ == '__main__':
    main()
