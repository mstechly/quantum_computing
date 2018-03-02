import time
import TSP_utilities

def main():
    start_time = time.time()
    nodes_array = TSP_utilities.create_nodes_array(6)
    TSP_utilities.get_tsp_matrix(nodes_array)
    solution = TSP_utilities.solve_tsp_brute_force(nodes_array)
    end_time = time.time()
    calculation_time = end_time - start_time
    print("Calculation time:", calculation_time)
    TSP_utilities.plot_solution(nodes_array, solution)

if __name__ == '__main__':
    main()