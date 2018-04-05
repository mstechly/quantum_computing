import numpy as np
import pandas as pd
import pdb
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def analyze_results_for_all_ones_testing():
    data_1 = pd.read_csv("results_all_ones_minus_1.csv")
    data_2 = pd.read_csv("results_all_ones_minus_2.csv")
    valid_prob_1 = np.mean(data_1.valid_prob)
    valid_prob_2 = np.mean(data_2.valid_prob)
    best_valid_1 = np.mean(data_1.best_valid)
    best_valid_2 = np.mean(data_2.best_valid)
    print("minus 1")
    print(valid_prob_1, best_valid_1)

    print("minus 2")
    print(valid_prob_2, best_valid_2)
    pdb.set_trace()

def analyze_results_for_parameters_testing():
    data = pd.read_csv("results_3_nodes.csv")

    aggregation_list = []

    for steps, data_steps in data.groupby('steps'):
        print("Number of steps:", steps)
        for tol, group in data_steps.groupby('tol'):
            results = [steps, tol, np.mean(group.time), np.mean(group.valid_prob), np.sum(group.best_valid) / len(group), len(group)]
            print(results)
            aggregation_list.append(results)

    aggregation_list = np.array(aggregation_list)

    fig, ax = plt.subplots()
    ax.set_yscale('log')
    scatter_plot = ax.scatter(aggregation_list[:,0], aggregation_list[:, 1], c=aggregation_list[:, 2], cmap='plasma')
    cbar = fig.colorbar(scatter_plot)
    ax.set_xlabel("steps")
    ax.set_ylabel("tol")
    ax.set_title("Calculation time for different parameters")
    plt.savefig("time_per_parameters.png")
    plt.clf()

    fig, ax = plt.subplots()
    ax.set_yscale('log')
    scatter_plot = ax.scatter(aggregation_list[:,0], aggregation_list[:, 1], c=aggregation_list[:, 3], cmap='plasma')
    cbar = fig.colorbar(scatter_plot)
    ax.set_xlabel("steps")
    ax.set_ylabel("tol")
    ax.set_title("Mean probability of valid result for different parameters")
    plt.savefig("valid_prob_per_parameters.png")
    plt.clf()

    fig, ax = plt.subplots()
    ax.set_yscale('log')
    scatter_plot = ax.scatter(aggregation_list[:,0], aggregation_list[:, 1], c=aggregation_list[:, 4], cmap='plasma')
    cbar = fig.colorbar(scatter_plot)
    ax.set_xlabel("steps")
    ax.set_ylabel("tol")
    ax.set_title("Percentage of correct results for different parameters")
    plt.savefig("best_valid_per_parameters.png")
    plt.clf()


def main():
    analyze_results_for_parameters_testing()
    analyze_results_for_all_ones_testing()

if __name__ == '__main__':
    main()
