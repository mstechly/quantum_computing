import pyquil.api as api
import numpy as np
from grove.pyqaoa.qaoa import QAOA
from pyquil.paulis import PauliTerm, PauliSum
import scipy.optimize
import TSP_utilities
import pdb

def solve_tsp(nodes_array):
    qvm = api.QVMConnection()
    number_of_qubits = get_number_of_qubits(len(nodes_array))
    depth_of_circuit = 3
    steps = 1
    initial_theta = np.random.randn(number_of_qubits * depth_of_circuit)

    cost_operators = []
    cost_operators += create_cost_operators(nodes_array)

    for cost_op in cost_operators:
        print(cost_op)

    driver_operators = create_driver_operators(number_of_qubits)

    minimizer_kwargs = {'method': 'Nelder-Mead',
                            'options': {'ftol': 1.0e-2, 'xtol': 1.0e-2,
                                        'disp': False}}

    vqe_option = {'disp': print_fun, 'return_all': True,
                  'samples': None}

    qaoa_inst = QAOA(qvm, number_of_qubits, steps=steps, cost_ham=cost_operators,
                     ref_hamiltonian=driver_operators, store_basis=True,
                     minimizer=scipy.optimize.minimize,
                     minimizer_kwargs=minimizer_kwargs,
                     vqe_options=vqe_option)
    betas, gammas = qaoa_inst.get_angles()
    probs = qaoa_inst.probabilities(np.hstack((betas, gammas)))

    print("Most frequent bitstring from sampling")
    most_freq_string, sampling_results = qaoa_inst.get_string(betas, gammas, samples=10000)
    print(sampling_results)
    print(most_freq_string)
    pdb.set_trace()

def create_cost_operators(nodes_array):
    cost_operators = []
    # cost_operators += create_weights_cost_operators(nodes_array)
    cost_operators += create_penalty_operators_for_bilocation(nodes_array)
    cost_operators += create_penalty_operators_for_repetition(nodes_array)
    return cost_operators

def create_weights_cost_operators(nodes_array):
    cost_operators = []
    number_of_nodes = len(nodes_array)
    tsp_matrix = TSP_utilities.get_tsp_matrix(nodes_array)
    
    for i in range(number_of_nodes):
        for j in range(i, number_of_nodes):
            for t in range(number_of_nodes - 1):
                # weight = 1 / 2 (This holds if weight is 1)
                weight = tsp_matrix[i][j] / 2
                if tsp_matrix[i][j] != 0:
                    cost_operators.append(PauliSum([PauliTerm("Z", t * number_of_nodes + i, weight) * PauliTerm("Z", (t * number_of_nodes + 1) + j )]))

    return cost_operators


def create_penalty_operators_for_bilocation(nodes_array):
    cost_operators = []
    number_of_nodes = len(nodes_array)
    # Additional cost for visiting more than one node in given time t
    for t in range(number_of_nodes):
        range_of_qubits = list(range(t * number_of_nodes, (t + 1) * number_of_nodes))
        cost_operators += create_penalty_operators_for_qubit_range(nodes_array, range_of_qubits)
    return cost_operators

def create_penalty_operators_for_repetition(nodes_array):
    cost_operators = []
    number_of_nodes = len(nodes_array)
    # Additional cost for visiting more than one node in given time t
    for i in range(number_of_nodes):
        range_of_qubits = list(range(i, number_of_nodes**2, number_of_nodes))
        cost_operators += create_penalty_operators_for_qubit_range(nodes_array, range_of_qubits)
    return cost_operators


def create_penalty_operators_for_qubit_range(nodes_array, range_of_qubits):
    cost_operators = []
    tsp_matrix = TSP_utilities.get_tsp_matrix(nodes_array)
    weight = 100 * np.max(tsp_matrix)
    for i in range_of_qubits:
        if i == range_of_qubits[0]:
            z_term = PauliTerm("Z", i, weight)
            all_ones_term = PauliTerm("I", 0, 0.5 * weight) - PauliTerm("Z", i, 0.5 * weight)
        else:
            z_term = z_term * PauliTerm("Z", i, weight)
            all_ones_term = all_ones_term * (PauliTerm("I", 0, 0.5 * weight) - PauliTerm("Z", i, 0.5 * weight))

    z_term = PauliSum([z_term])
    cost_operators.append(z_term + 10 * all_ones_term)

    return cost_operators


def create_driver_operators(number_of_qubits):
    driver_operators = []
    
    for i in range(number_of_qubits):
        driver_operators.append(PauliSum([PauliTerm("X", i, -1.0)]))

    return driver_operators


def print_fun(x):
    print(x)

def get_number_of_qubits(N):
    return (N)**2

if __name__ == '__main__':
    solve_tsp(np.array([[0, 0], [0, 7], [0, 14]]))