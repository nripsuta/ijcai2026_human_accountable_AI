import numpy as np
import time
import json
from joblib import Parallel, delayed
import os

from src.env import Env
from src.acTools import Actual_Causation as AC


def generate_actual_causes(env, traj, kappa):
    """
    For a given trajectory, return candidate, bf_, hp_ and tr_ causes
    """
    ac = AC(env, traj, kappa)
    ac.tree_search(ac.root_node)
    candidate_causes = ac.interventions_sets
    bf_causes = ac.compute_BFCs()
    hp_causes = ac.compute_HPCs()
    tr_causes = ac.compute_TRCs()

    return candidate_causes, bf_causes, hp_causes, tr_causes

def generate_data(num_of_trajectories, N, num_of_agents, num_of_opps, biased_hand, kappa, n_jobs):
    """
    Generate trajectories and compute causes
    """
    assert num_of_trajectories > 0, "num_of_trajectories should be greater than 0"
    
    print("Begin Generating Data")
    start = time.time()

    env = Env(N, num_of_agents, num_of_opps, biased_hand)

    if not os.path.exists(f'data/biased_{biased_hand}/N{N}'):
        os.mkdir(f'data/biased_{biased_hand}/N{N}')

    # readable file to store trajectories
    f_traj = open(f'data/biased_{biased_hand}/N{N}/trajectories.txt', 'w')

    # Trajectories
    print("Begin generating tajectories")
    trajectories = []
    traj_id = 0
    seed = 1
    while traj_id < num_of_trajectories:
        rng = np.random.default_rng(seed)
        seed += 1
        traj = env.sample_trajectory(rng)

        # we only consider trajectories where agents don't win
        if traj['states'][-1]['score']['agents'] > traj['states'][-1]['score']['opponents']:
            continue
        traj['id'] = traj_id
        traj_id += 1
        trajectories.append(traj)
        env.render_traj(traj, f_traj)
    f_traj.close()
    # file that stores trajectories (json)
    with open(f'data/biased_{biased_hand}/N{N}/trajectories.json', 'w') as f:
        json.dump(trajectories, f)
    print("Finish generating tajectories")

    # Actual Causes
    print("Begin computing causes")
    causes = Parallel(n_jobs=min(n_jobs, num_of_trajectories))(delayed(generate_actual_causes)(env, traj, kappa) for traj in trajectories)
    # Candidate Causes
    candidate_causes = [tup[0] for tup in causes]
    # But-For causes
    bf_causes = [tup[1] for tup in causes]
    # HP causes
    hp_causes = [tup[2] for tup in causes]
    # TR causes
    tr_causes = [tup[3] for tup in causes]

    # file that stores candidate causes
    with open(f'data/biased_{biased_hand}/N{N}/candidate_causes.json', 'w') as f:
        json.dump(candidate_causes, f)
    # file that stores bf causes
    with open(f'data/biased_{biased_hand}/N{N}/bf_causes.json', 'w') as f:
        json.dump(bf_causes, f)   
    # file that stores hp causes
    with open(f'data/biased_{biased_hand}/N{N}/hp_causes.json', 'w') as f:
        json.dump(hp_causes, f)   
    # file that stores tr causes
    with open(f'data/biased_{biased_hand}/N{N}/tr_causes.json', 'w') as f:
        json.dump(tr_causes, f)  
    print("Finish computing causes")   

    end = time.time()
    print("Finish Generating Data")
    print(f"Time elapsed: {end - start}sec\n")

    return