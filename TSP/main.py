import time
import TSP_utilities
import qTSP_forest
import qTSP_qiskit
import pdb

def main():
    print("Brute Force solution")
    nodes_array = TSP_utilities.create_nodes_array(4)
    start_time = time.time()
    brute_force_solution = TSP_utilities.solve_tsp_brute_force(nodes_array)
    end_time = time.time()
    calculation_time = end_time - start_time
    print("Calculation time:", calculation_time)
    TSP_utilities.plot_solution(nodes_array, brute_force_solution)


if __name__ == '__main__':
    main()