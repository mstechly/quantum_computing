import pyquil.api as api
import numpy as np
from grove.pyqaoa.qaoa import QAOA
from pyquil.paulis import PauliTerm, PauliSum
import TSP_utilities
import scipy.optimize
import pdb

def solve_tsp(nodes_array):
    qvm = api.QVMConnection()
    number_of_qubits = get_number_of_qubits(len(nodes_array))
    depth_of_circuit = 3
    steps = 1
    initial_theta = np.random.randn(number_of_qubits * depth_of_circuit)

    cost_operators = create_cost_operators(nodes_array)
    driver_operators = create_driver_operators(nodes_array)

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
    most_freq_string, sampling_results = qaoa_inst.get_string(
            betas, gammas)
    print(most_freq_string)

    quantum_order = TSP_utilities.binary_state_to_points_order(most_freq_string)

    return quantum_order


def create_cost_operators(nodes_array):
    cost_operators = []
    number_of_nodes = len(nodes_array)

    tsp_matrix = TSP_utilities.get_tsp_matrix(nodes_array)

    for i in range(number_of_nodes):
        for j in range(i, number_of_nodes):
            if tsp_matrix[i][j] != 0:
                cost_operators.append(PauliTerm("Z", i, 0.5)*PauliTerm("Z", j) + PauliTerm("I", 0, -0.5))

    return cost_operators


def create_driver_operators(nodes_array):
    driver_operators = []
    number_of_nodes = len(nodes_array)
    
    for i in range(number_of_nodes):
        driver_operators.append(PauliSum([PauliTerm("X", i, -1.0)]))

    return driver_operators


def print_fun(x):
    print(x)


def get_number_of_qubits(N):
    return (N-1)**2