# quantum_computing
My code for quantum computing projects.

## Libraries used

### QISKit

QISKit is a programming language for quantum computers developed by IBM.
To run your code on the quantum virtual machine or quantum processor you need to add a `Qconfig.py` file, as described here:
https://github.com/QISKit/qiskit-sdk-py#executing-your-code-on-a-real-quantum-chip

### Pyquil

Pyquil is a library allowing you to create code for quantum computers to be executed using Rigetti Forest platform. It's developed by Rigetti Computing.
To run your code on the quantum virtual machine or quantum processor you need to configure file, as described here:
http://pyquil.readthedocs.io/en/latest/start.html#connecting-to-the-rigetti-forest

## Projects

### TSP

In this project I'm writing an algorithm for solving Traveling Salesman Problem with quantum computer.

It's based on: 

- QAOA paper: https://arxiv.org/abs/1411.4028
- Demo from IBM: https://nbviewer.jupyter.org/github/QISKit/qiskit-tutorial/blob/stable/4_applications/classical_optimization.ipynb

