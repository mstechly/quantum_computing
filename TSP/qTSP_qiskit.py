from qiskit import QuantumCircuit, QuantumProgram
import Qconfig
import numpy as np
from qiskit.tools.apps.optimization import trial_circuit_ry, SPSA_optimization, SPSA_calibration
from qiskit.tools.apps.optimization import Energy_Estimate, make_Hamiltonian, eval_hamiltonian, group_paulis
from qiskit.tools.qi.pauli import Pauli
import TSP_utilities
from scipy import linalg as la
from functools import partial

import pdb

def solve_tsp(nodes_array):
    Q_program = QuantumProgram()
    Q_program.set_api(Qconfig.APItoken, Qconfig.config['url'])
    coupling_map = None
    entangler_map = {0: [1], 1: [2], 2: [3], 3: [4], 4: [5], 5: [6], 6: [7], 7: [8]}
    initial_layout = None

    backend = 'local_qasm_simulator'
    max_trials = 200

    number_of_qubits = (len(nodes_array) - 1)**2
    depth_of_circuit = 3
    initial_theta = np.random.randn(number_of_qubits * depth_of_circuit)
    shots = 1

    initial_c = 0.1
    target_update=2 * np.pi * 0.1
    save_step = 1
    pauli_list = get_pauli_list(nodes_array)
    H = make_Hamiltonian(pauli_list)
    H=np.diag(H)

    if shots !=1:
        H=group_paulis(pauli_list) 

    SPSA_params = SPSA_calibration(partial(cost_function, Q_program, H, number_of_qubits, depth_of_circuit, entangler_map, 
                                           shots, backend), initial_theta, initial_c, target_update, 5)

    best_distance_quantum, best_theta, cost_plus, cost_minus, _, _ = SPSA_optimization(partial(cost_function, Q_program, H, number_of_qubits, depth_of_circuit, entangler_map, shots, backend),
                                                           initial_theta, SPSA_params, max_trials, save_step, 1);
    

    shots = 100
    circuits = ['final_circuit']   
    Q_program.add_circuit('final_circuit', trial_circuit_ry(number_of_qubits, depth_of_circuit, best_theta, entangler_map,None,True))
    result = Q_program.execute(circuits, backend=backend, shots=shots, coupling_map=coupling_map, initial_layout=initial_layout)
    data = result.get_counts('final_circuit')

    max_value = max(data.values())
    max_keys = [k for k, v in data.items() if v == max_value] # getting all keys containing the `maximum`
    x_quantum=np.zeros(number_of_qubits)
    for bit in range(number_of_qubits):
        if max_keys[0][bit]=='1':
            x_quantum[bit]=1

    quantum_order = TSP_utilities.binary_state_to_points_order(x_quantum)

    return quantum_order


def cost_function(Q_program, H, n, m, entangler_map, shots, device, theta):
    return eval_hamiltonian(Q_program, H, trial_circuit_ry(n, m, theta, entangler_map, None, False), shots, device).real


def get_pauli_list(nodes_array):
    n = (len(nodes_array) - 1)**2
    N = len(nodes_array)
    w = TSP_utilities.get_tsp_matrix(nodes_array)
    A = np.max(w)*100 # A parameter of cost function

    # takes the part of w matrix excluding the 0-th point, which is the starting one 
    wsave = w[1:N,1:N]
    # nearest-neighbor interaction matrix for the prospective cycle (p,p+1 interaction)
    shift = np.zeros([N-1,N-1])
    shift = la.toeplitz([0,1,0], [0,1,0])/2

    # the first and last point of the TSP problem are fixed by initial and final conditions 
    firststep = np.zeros([N-1])
    firststep[0] = 1;
    laststep = np.zeros([N-1])
    laststep[N-2] = 1;



    # Q defines the interactions between variables 
    Q = np.kron(shift,wsave) + np.kron(A*np.ones((N-1, N-1)), np.identity(N-1)) + np.kron(np.identity(N-1),A*np.ones((N-1, N-1)))
    # G defines the contribution from the individual variables 
    G = np.kron(firststep,w[0,1:N]) + np.kron(laststep,w[1:N,0]) - 4*A*np.kron(np.ones(N-1),np.ones(N-1))
    # M is the constant offset 
    M = 2*A*(N-1)

    # Defining the new matrices in the Z-basis 

    Iv=np.ones((N-1)**2)
    Qz = (Q/4)
    Gz =( -G/2-np.dot(Iv,Q/4)-np.dot(Q/4,Iv))
    Mz = (M+np.dot(G/2,Iv)+np.dot(Iv,np.dot(Q/4,Iv)))

    Mz = Mz + np.trace(Qz)
    Qz = Qz - np.diag(np.diag(Qz))


    pauli_list = []
    for i in range(n):
        if Gz[i] != 0:
            wp = np.zeros(n)
            vp = np.zeros(n)
            vp[i] = 1
            pauli_list.append((Gz[i],Pauli(vp,wp)))
    for i in range(n):
        for j in range(i):
            if Qz[i,j] != 0:
                wp = np.zeros(n)
                vp = np.zeros(n)
                vp[i] = 1
                vp[j] = 1
                pauli_list.append((2*Qz[i,j],Pauli(vp,wp)))
                
    pauli_list.append((Mz,Pauli(np.zeros(n),np.zeros(n))))
    return pauli_list
