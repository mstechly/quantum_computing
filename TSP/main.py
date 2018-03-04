import time
import TSP_utilities
# import qTSP_forest
import qTSP_qiskit
import pdb

def main():
    seed = 5406
    nodes_array = TSP_utilities.create_nodes_array(4, seed=seed)

    print("Brute Force solution")
    start_time = time.time()
    brute_force_solution = TSP_utilities.solve_tsp_brute_force(nodes_array)
    end_time = time.time()
    calculation_time = end_time - start_time
    print("Calculation time:", calculation_time)
    TSP_utilities.plot_solution('brute_force', nodes_array, brute_force_solution)

    # print("QAOA solution - Forest")
    # start_time = time.time()
    # forest_solution = qTSP_forest.solve_tsp(nodes_array)
    # end_time = time.time()
    # calculation_time = end_time - start_time
    # print("Calculation time:", calculation_time)
    # TSP_utilities.plot_solution('forest', nodes_array, forest_solution)

    print("QAOA solution - QISKit")
    start_time = time.time()
    qiskit_solution = qTSP_qiskit.solve_tsp(nodes_array)
    end_time = time.time()
    calculation_time = end_time - start_time
    print("Calculation time:", calculation_time)
    TSP_utilities.plot_solution('qiskit', nodes_array, qiskit_solution)


if __name__ == '__main__':
    main()