# num of total trajectories to generate
num_of_trajectories = 1000
# list of environment sizes
N_lst = [5]
# number of agents
num_of_agents = 2
# number of opponents
num_of_opps = 2
# max num of interventions for cf reasoning
kappa = 2
# num of instances per component
num_of_instances = 5
# 
n_jobs = 1

mode = "combinations"   # ["combinations", "components"]
generate_new_data = True

# biased hand
# for example if biased_hand = 0 then Agent 0 gets the bad hand
biased_hands = [0, 1, "none", "both"] # [0, 1, "none", "both"]