import json
import os

from src.env import Env
from src.raTools import compute_responsibilities


def generate_combinations_results(num_of_trajectories, N, num_of_agents, num_of_opps, biased_hand):
    """
    Generate vignettes for all ACxRA combinations
    """

    print("Finish generating results\n")

    env = Env(N, num_of_agents, num_of_opps, biased_hand)

    if not os.path.exists(f'combinations_results/biased_{biased_hand}/N{N}'):
        os.mkdir(f'combinations_results/biased_{biased_hand}/N{N}')

    # load trajectories
    with open(f'data/biased_{biased_hand}/N{N}/trajectories.json', 'r') as f:
        trajectories = json.load(f)
    # load but-for causes
    with open(f'data/biased_{biased_hand}/N{N}/bf_causes.json', 'r') as f:
        bf_causes = json.load(f)
    # load HP causes
    with open(f'data/biased_{biased_hand}/N{N}/hp_causes.json', 'r') as f:
        hp_causes = json.load(f)
    # load TR causes
    with open(f'data/biased_{biased_hand}/N{N}/tr_causes.json', 'r') as f:
        tr_causes = json.load(f)

    # BF
    # compute responsibility assignments based on bf causes
    bf_resps, bf_cause_ids = compute_responsibilities(bf_causes, num_of_agents, num_of_trajectories)

    # BFxCH (same as BFxTR)
    # readable file to store results for BFxCH
    f = open(f'combinations_results/biased_{biased_hand}/N{N}/BFxCH.txt', 'w')

    for traj_id in range(num_of_trajectories):
        trajectory = trajectories[traj_id]
        f.write(f"Trajectory {traj_id}\n")
        f.write("==\n")
        # compute
        for ag_id in range(num_of_agents):
            f.write(f"Agent {ag_id}\n")
            f.write(f"Degree of responsibility: {bf_resps[traj_id]['CH'][ag_id]}\n")
            if not bf_resps[traj_id]['CH'][ag_id]: continue
            sample_cause_id = bf_cause_ids[traj_id]['CH'][ag_id]
            assert sample_cause_id > -1
            for bf_cause in bf_causes[traj_id]: # if needed efficiency can be improved
                if bf_cause[-1]['id'] == sample_cause_id:
                    # store cause
                    f.write(f"Set of Interventions (id: {sample_cause_id})\n")
                    for intervention in bf_cause:
                        f.write(f"Time {intervention['t']}, Agent {intervention['agent']}, Old Action {intervention['cf_action']}, New Action {intervention['new_action']}\n")
                    f.write("\n")
                    # compute and store counterfactual trajectory
                    cf_trajectory = env.sample_cf_trajectory(trajectory, bf_cause)
                    cf_trajectory['cf_id'] = sample_cause_id
                    env.render_traj(cf_trajectory, f)
                    f.write("===\n\n")
                    break
                 
    f.close()

    # HP
    # compute responsibility assignments based on HP causes
    hp_resps, hp_cause_ids = compute_responsibilities(hp_causes, num_of_agents, num_of_trajectories)

    # HPxCH
    # readable file to store results for HPxCH
    f = open(f'combinations_results/biased_{biased_hand}/N{N}/HPxCH.txt', 'w')

    for traj_id in range(num_of_trajectories):
        trajectory = trajectories[traj_id]
        f.write(f"Trajectory {traj_id}\n")
        f.write("==\n")
        # compute
        for ag_id in range(num_of_agents):
            f.write(f"Agent {ag_id}\n")
            f.write(f"Degree of responsibility: {hp_resps[traj_id]['CH'][ag_id]}\n")
            if not hp_resps[traj_id]['CH'][ag_id]: continue
            sample_cause_id = hp_cause_ids[traj_id]['CH'][ag_id]
            assert sample_cause_id > -1
            for hp_cause in hp_causes[traj_id]: # if needed efficiency can be improved
                if hp_cause[-1]['id'] == sample_cause_id:
                    # store cause
                    f.write(f"Set of Interventions (id: {sample_cause_id})\n")
                    for intervention in hp_cause:
                        f.write(f"Time {intervention['t']}, Agent {intervention['agent']}, Old Action {intervention['cf_action']}, New Action {intervention['new_action']}\n")
                    f.write("\n")
                    # compute and store counterfactual trajectory
                    cf_trajectory = env.sample_cf_trajectory(trajectory, hp_cause)
                    cf_trajectory['cf_id'] = sample_cause_id
                    env.render_traj(cf_trajectory, f)
                    f.write("===\n\n")
                    break
                 
    f.close()

    # HPxTR
    # readable file to store results for HPxTR
    f = open(f'combinations_results/biased_{biased_hand}/N{N}/HPxTR.txt', 'w')

    for traj_id in range(num_of_trajectories):
        trajectory = trajectories[traj_id]
        f.write(f"Trajectory {traj_id}\n")
        f.write("==\n")
        # compute
        for ag_id in range(num_of_agents):
            f.write(f"Agent {ag_id}\n")
            f.write(f"Degree of responsibility: {hp_resps[traj_id]['TR'][ag_id]}\n")
            if not hp_resps[traj_id]['TR'][ag_id]: continue
            sample_cause_id = hp_cause_ids[traj_id]['TR'][ag_id]
            assert sample_cause_id > -1
            for hp_cause in hp_causes[traj_id]: # if needed efficiency can be improved
                if hp_cause[-1]['id'] == sample_cause_id:
                    # store cause
                    f.write(f"Set of Interventions (id: {sample_cause_id})\n")
                    for intervention in hp_cause:
                        f.write(f"Time {intervention['t']}, Agent {intervention['agent']}, Old Action {intervention['cf_action']}, New Action {intervention['new_action']}\n")
                    f.write("\n")
                    # compute and store counterfactual trajectory
                    cf_trajectory = env.sample_cf_trajectory(trajectory, hp_cause)
                    cf_trajectory['cf_id'] = sample_cause_id
                    env.render_traj(cf_trajectory, f)
                    f.write("===\n\n")
                    break
                 
    f.close()

    # TR
    # compute responsibility assignments based on TR causes
    tr_resps, tr_cause_ids = compute_responsibilities(tr_causes, num_of_agents, num_of_trajectories)

    # TRxCH
    # readable file to store results for TRxCH
    f = open(f'combinations_results/biased_{biased_hand}/N{N}/TRxCH.txt', 'w')

    for traj_id in range(num_of_trajectories):
        trajectory = trajectories[traj_id]
        f.write(f"Trajectory {traj_id}\n")
        f.write("==\n")
        # compute
        for ag_id in range(num_of_agents):
            f.write(f"Agent {ag_id}\n")
            f.write(f"Degree of responsibility: {tr_resps[traj_id]['CH'][ag_id]}\n")
            if not tr_resps[traj_id]['CH'][ag_id]: continue
            sample_cause_id = tr_cause_ids[traj_id]['CH'][ag_id]
            assert sample_cause_id > -1
            for tr_cause in tr_causes[traj_id]: # if needed efficiency can be improved
                if tr_cause[-1]['id'] == sample_cause_id:
                    # store cause
                    f.write(f"Set of Interventions (id: {sample_cause_id})\n")
                    for intervention in tr_cause:
                        f.write(f"Time {intervention['t']}, Agent {intervention['agent']}, Old Action {intervention['cf_action']}, New Action {intervention['new_action']}\n")
                    f.write("\n")
                    # compute and store counterfactual trajectory
                    cf_trajectory = env.sample_cf_trajectory(trajectory, tr_cause)
                    cf_trajectory['cf_id'] = sample_cause_id
                    env.render_traj(cf_trajectory, f)
                    f.write("===\n\n")
                    break
                 
    f.close()

    # TRxTR
    # readable file to store results for TRxTR
    f = open(f'combinations_results/biased_{biased_hand}/N{N}/TRxTR.txt', 'w')

    for traj_id in range(num_of_trajectories):
        trajectory = trajectories[traj_id]
        f.write(f"Trajectory {traj_id}\n")
        f.write("==\n")
        # compute
        for ag_id in range(num_of_agents):
            f.write(f"Agent {ag_id}\n")
            f.write(f"Degree of responsibility: {tr_resps[traj_id]['TR'][ag_id]}\n")
            if not tr_resps[traj_id]['TR'][ag_id]: continue
            sample_cause_id = tr_cause_ids[traj_id]['TR'][ag_id]
            assert sample_cause_id > -1
            for tr_cause in tr_causes[traj_id]: # if needed efficiency can be improved
                if tr_cause[-1]['id'] == sample_cause_id:
                    # store cause
                    f.write(f"Set of Interventions (id: {sample_cause_id})\n")
                    for intervention in tr_cause:
                        f.write(f"Time {intervention['t']}, Agent {intervention['agent']}, Old Action {intervention['cf_action']}, New Action {intervention['new_action']}\n")
                    f.write("\n")
                    # compute and store counterfactual trajectory
                    cf_trajectory = env.sample_cf_trajectory(trajectory, tr_cause)
                    cf_trajectory['cf_id'] = sample_cause_id
                    env.render_traj(cf_trajectory, f)
                    f.write("===\n\n")
                    break
                 
    f.close()

    print("Finish Generating Results\n")