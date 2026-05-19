import time

from src.generate_data import generate_data
from src.generate_components_results import generate_components_results
from src.generate_combinations_results import generate_combinations_results

from params import *


def main():

    print("Begin Experiment\n")    
    
    assert mode == "components" or mode == "combinations","Wrong mode inserted."
    assert N_lst == [5], "For now the biased hand implementation only supports N=5"

    # file that stores computation time
    f_time = open(f'data/time.txt', 'w')
    
    for biased_hand in biased_hands:
        f_time.write(f"Biased hand: {biased_hand}\n")
        print(f'Biased hand: {biased_hand}\n')
        for N in N_lst:
            start = time.time()
            print(f'Number of Cards: {N}\n')
            if generate_new_data:
                generate_data(num_of_trajectories, N, num_of_agents, num_of_opps, biased_hand, kappa, n_jobs)
            if mode == "components":
                generate_components_results(num_of_trajectories, N, num_of_instances, num_of_agents, num_of_opps) # not implements for biased hands
            else: # mode = combinations
                generate_combinations_results(num_of_trajectories, N, num_of_agents, num_of_opps, biased_hand)
            end = time.time()
            f_time.write(f"Total Time({N}): {end - start}sec\n")
    
    f_time.close()
    print("Finish Experiment")

if __name__ == '__main__':
    main()