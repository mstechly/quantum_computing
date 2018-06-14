import pyquil.api as api
import numpy as np
from grove.pyqaoa.hadfield_qaoa import QAOA as hadfield_QAOA
from grove.alpha.arbitrary_state.arbitrary_state import create_arbitrary_state
from pyquil.paulis import PauliTerm, PauliSum
import pyquil.quil as pq
from pyquil.gates import X
import itertools

import scipy.optimize
from . import TSP_utilities
import pdb

class ForestTSPSolver(object):
    """docstring for TSPSolver"""
    def __init__(self, full_nodes_array, steps=3, ftol=1.0e-4, xtol=1.0e-4, initial_state=[0, 1, 2], starting_node=0):
        reduced_nodes_array, costs_to_starting_node = self.reduce_nodes_array(full_nodes_array, starting_node)
        self.nodes_array = reduced_nodes_array
        self.starting_node = starting_node
        self.full_nodes_array = full_nodes_array
        self.costs_to_starting_node = costs_to_starting_node
        self.qvm = api.QVMConnection()
        self.steps = steps
        self.ftol = ftol
        self.xtol = xtol
        self.betas = None
        self.gammas = None
        self.qaoa_inst = None
        self.most_freq_string = None
        self.number_of_qubits = self.get_number_of_qubits()
        self.initial_state = initial_state

        cost_operators = self.create_cost_operators()
        # driver_operators = self.create_driver_operators()
        driver_operators = self.create_mixer()
        initial_state_program = self.create_initial_state_program()

        minimizer_kwargs = {'method': 'Nelder-Mead',
                                'options': {'ftol': self.ftol, 'xtol': self.xtol,
                                            'disp': False}}

        vqe_option = {'disp': print_fun, 'return_all': True,
                      'samples': None}

        self.qaoa_inst = hadfield_QAOA(self.qvm, list(range(self.number_of_qubits)), steps=self.steps, cost_ham=cost_operators,
                         ref_hamiltonian=driver_operators, driver_ref=initial_state_program, store_basis=True,
                         minimizer=scipy.optimize.minimize,
                         minimizer_kwargs=minimizer_kwargs,
                         vqe_options=vqe_option)
        
    def solve_tsp(self):
        self.find_angles()
        return self.get_solution()

    def find_angles(self):
        self.betas, self.gammas = self.qaoa_inst.get_angles()
        return self.betas, self.gammas

    def get_results(self):
        most_freq_string, sampling_results = self.qaoa_inst.get_string(self.betas, self.gammas, samples=10000)
        self.most_freq_string = most_freq_string
        return sampling_results.most_common()

    def get_solution(self):
        if self.most_freq_string is None:
            self.most_freq_string, sampling_results = self.qaoa_inst.get_string(self.betas, self.gammas, samples=10000)
        reduced_solution = TSP_utilities.binary_state_to_points_order_full(self.most_freq_string)
        full_solution = self.get_solution_for_full_array(reduced_solution)
        return full_solution

    def reduce_nodes_array(self, full_nodes_array, starting_node):
        reduced_nodes_array = np.delete(full_nodes_array, starting_node, 0)
        tsp_matrix = TSP_utilities.get_tsp_matrix(full_nodes_array)
        costs_to_starting_node = np.delete(tsp_matrix[:, starting_node], starting_node)
        return reduced_nodes_array, costs_to_starting_node

    def get_solution_for_full_array(self, reduced_solution):
        full_solution = reduced_solution
        for i in range(len(full_solution)):
            if full_solution[i] >= self.starting_node:
                full_solution[i] += 1
        full_solution.insert(0, self.starting_node)
        return full_solution

    def create_cost_operators(self):
        cost_operators = []
        cost_operators += self.create_phase_separator()
        # cost_operators += self.create_penalty_operators_for_bilocation()
        # cost_operators += self.create_penalty_operators_for_repetition()
        # cost_operators += self.create_weights_cost_operators()
        return cost_operators

    def create_phase_separator(self):
        cost_operators = []
        for t in range(len(self.nodes_array) - 1):
            for city_1 in range(len(self.nodes_array)):
                for city_2 in range(len(self.nodes_array)):
                    if city_1 != city_2:
                        tsp_matrix = TSP_utilities.get_tsp_matrix(self.nodes_array)
                        distance = tsp_matrix[city_1, city_2]
                        qubit_1 = t * len(self.nodes_array) + city_1
                        qubit_2 = (t + 1) * len(self.nodes_array) + city_2
                        cost_operators.append(PauliTerm("Z", qubit_1, distance) * PauliTerm("Z", qubit_2))

        for city in range(len(self.costs_to_starting_node)):
            distance_from_0 = -self.costs_to_starting_node[city]
            qubit = city
            cost_operators.append(PauliTerm("Z", qubit, distance_from_0))

        phase_separator = [PauliSum(cost_operators)]
        return phase_separator

    def create_penalty_operators_for_bilocation(self):
        # Additional cost for visiting more than one node in given time t
        cost_operators = []
        number_of_nodes = len(self.nodes_array)
        for t in range(number_of_nodes):
            range_of_qubits = list(range(t * number_of_nodes, (t + 1) * number_of_nodes))
            cost_operators += self.create_penalty_operators_for_qubit_range(range_of_qubits)
        return cost_operators

    def create_penalty_operators_for_repetition(self):
        # Additional cost for visiting given node more than one time
        cost_operators = []
        number_of_nodes = len(self.nodes_array)
        for i in range(number_of_nodes):
            range_of_qubits = list(range(i, number_of_nodes**2, number_of_nodes))
            cost_operators += self.create_penalty_operators_for_qubit_range(range_of_qubits)
        return cost_operators

    def create_penalty_operators_for_qubit_range(self, range_of_qubits):
        cost_operators = []
        tsp_matrix = TSP_utilities.get_tsp_matrix(self.nodes_array)
        weight = -100 * np.max(tsp_matrix)
        # weight = -0.5
        for i in range_of_qubits:
            if i == range_of_qubits[0]:
                z_term = PauliTerm("Z", i, weight)
                all_ones_term = PauliTerm("I", 0, 0.5 * weight) - PauliTerm("Z", i, 0.5 * weight)
            else:
                z_term = z_term * PauliTerm("Z", i)
                all_ones_term = all_ones_term * (PauliTerm("I", 0, 0.5) - PauliTerm("Z", i, 0.5))

        z_term = PauliSum([z_term])
        cost_operators.append(PauliTerm("I", 0, weight) - z_term - 2 * all_ones_term)

        return cost_operators

    def create_weights_cost_operators(self):
        cost_operators = []
        number_of_nodes = len(self.nodes_array)
        tsp_matrix = TSP_utilities.get_tsp_matrix(self.nodes_array)
        
        for i in range(number_of_nodes):
            for j in range(i, number_of_nodes):
                for t in range(number_of_nodes - 1):
                    weight = -tsp_matrix[i][j] / 2
                    if tsp_matrix[i][j] != 0:
                        qubit_1 = t * number_of_nodes + i
                        qubit_2 = (t + 1) * number_of_nodes + j
                        cost_operators.append(PauliTerm("I", 0, weight) - PauliTerm("Z", qubit_1, weight) * PauliTerm("Z", qubit_2))

        return cost_operators

    def create_driver_operators(self):
        driver_operators = []
        
        for i in range(self.number_of_qubits):
            driver_operators.append(PauliSum([PauliTerm("X", i, -1.0)]))

        return driver_operators


    def create_mixer(self):
        """
        Indexing here comes directly from 4.1.2 from paper 1709.03489, equations 54 - 58.
        """
        mixer_operators = []

        n = len(self.nodes_array)
        for t in range(n - 1):
            for city_1 in range(n):
                for city_2 in range(n):
                    i = t
                    u = city_1
                    v = city_2
                    first_part = 1
                    first_part *= self.s_plus(u, i)
                    first_part *= self.s_plus(v, i+1)
                    first_part *= self.s_minus(u, i+1)
                    first_part *= self.s_minus(v, i)

                    second_part = 1
                    second_part *= self.s_minus(u, i)
                    second_part *= self.s_minus(v, i+1)
                    second_part *= self.s_plus(u, i+1)
                    second_part *= self.s_plus(v, i)
                    mixer_operators.append(first_part + second_part)
        return mixer_operators

    def create_initial_state_program(self):
        """
        As an initial state I use state, where in t=i we visit i-th city.
        """
        initial_state = pq.Program()
        number_of_nodes = len(self.nodes_array)
        if type(self.initial_state) is list:
            for i in range(number_of_nodes):
                initial_state.inst(X(i * number_of_nodes + self.initial_state[i]))

        elif self.initial_state == "all":
            vector_of_states = np.zeros(2**self.number_of_qubits)
            list_of_possible_states = []
            initial_order = range(0, number_of_nodes)
            all_permutations = [list(x) for x in itertools.permutations(initial_order)]
            for permutation in all_permutations:
                coding_of_permutation = 0
                for i in range(len(permutation)):
                    coding_of_permutation += 2**(i * number_of_nodes + permutation[i])
                vector_of_states[coding_of_permutation] = 1
            initial_state = create_arbitrary_state(vector_of_states)

        return initial_state

    def get_number_of_qubits(self):
        return len(self.nodes_array)**2

    def s_plus(self, city, time):
        qubit = time * len(self.nodes_array) + city
        return PauliTerm("X", qubit) + PauliTerm("Y", qubit, 1j)

    def s_minus(self, city, time):
        qubit = time * len(self.nodes_array) + city
        return PauliTerm("X", qubit) - PauliTerm("Y", qubit, 1j)


def print_fun(x):
    print(x)
