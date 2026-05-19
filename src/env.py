import numpy as np

from src.agents import Agent, Opponent


class Env():

    def __init__(self, N, num_of_agents=2, num_of_opps=2, biased_hand="None"):
        
        self.N = N
        self.horizon = N
        self.num_of_agents = num_of_agents
        self.num_of_opps = num_of_opps
        self.biased_hand = biased_hand

        assert num_of_agents == num_of_opps, "Number of agents and number of opponents should be equal"

        self.agents = [Agent(id, N, num_of_agents, num_of_opps) for id in range(num_of_agents)]
        self.opps = [Opponent(id, N, num_of_agents, num_of_opps) for id in range(num_of_opps)]


    #################### Trajectory ########################
    ##########################################################

    def sample_trajectory(self, rng):
        """
        Samples a trajectory/instance of the game, using the given random generator
        """
        trajectory = {
            'states' : [],
            'agents_info_states' : [],
            'opponents_info_states' : [],
            'agents_actions' : [],
            'opponents_actions' : [],
            'opponents_gumbels' : []
        }
        
        # initial state
        state = {}
        deck = list(range(3, self.N + 3))
        rng.shuffle(deck)
        state['deck'] = deck
        state['score'] = {'agents' : 0, 'opponents' : 0}
        # agents hands
        if self.biased_hand == 0:
            # state['agents_hands'] = [list(range(1, self.N + 1)), list(range(5, self.N + 5))]
            state['agents_hands'] = [list(range(2, self.N + 2)), list(range(3, self.N + 3))]
        elif self.biased_hand == 1:
            # state['agents_hands'] = [list(range(5, self.N + 5)), list(range(1, self.N + 1))]
            state['agents_hands'] = [list(range(3, self.N + 3)), list(range(2, self.N + 2))]
        elif self.biased_hand == "both":
            state['agents_hands'] = [list(range(2, self.N + 2)), list(range(2, self.N + 2))]
        else: # biased_hand = None
            state['agents_hands'] = [list(range(3, self.N + 3)) for _ in range(self.num_of_agents)]
        # opponents hands
        state['opponents_hands'] = [list(range(3, self.N + 3)) for _ in range(self.num_of_opps)]

        # store data from the previous step, necessary for deicision making
        prev_agents_info_states = [None] * self.num_of_agents
        prev_opps_info_states = [None] * self.num_of_opps
        prev_agents_actions = [None] * self.num_of_agents
        prev_opps_actions = [None] * self.num_of_opps

        for t in range(self.horizon):
            # observations
            agents_obs = self._get_ag_obs(state)
            opps_obs = self._get_opp_obs(state)

            # info-states and actions
            opps_gumbels = rng.gumbel(size=(self.num_of_opps, len(state['deck'])))
            
            agents_info_states = [
                ag._get_info_state(agents_obs[ag.id], prev_agents_actions[ag.id], prev_agents_info_states[ag.id])
                for ag in self.agents
            ]
            # agents' policies are deterministic
            agents_actions = [
                ag.policy(agents_info_states[ag.id]) 
                for ag in self.agents
            ]
            opps_info_states = [
                opp._get_info_state(opps_obs[opp.id], prev_opps_actions[opp.id], prev_opps_info_states[opp.id])
                for opp in self.opps
            ]
            # opponents' policies are stochastic
            with np.errstate(divide='ignore'):
                opps_actions = [
                    state['opponents_hands'][opp.id][np.argmax(np.log(opp.policy(opps_info_states[opp.id])) + opps_gumbels[opp.id])] 
                    for opp in self.opps
                ]
            
            # update trajectory
            trajectory['states'].append(state)
            trajectory['agents_info_states'].append(agents_info_states)
            trajectory['opponents_info_states'].append(opps_info_states)
            trajectory['agents_actions'].append(agents_actions)
            trajectory['opponents_actions'].append(opps_actions)
            # jsonify gumbels
            opps_gumbels = opps_gumbels.tolist()
            trajectory['opponents_gumbels'].append(opps_gumbels)
            
            # next state
            state = self._get_next_state(state, agents_actions, opps_actions)

            prev_agents_info_states = agents_info_states
            prev_opps_info_states = opps_info_states
            prev_agents_actions = agents_actions
            prev_opps_actions = opps_actions
        
        # terminal state
        trajectory['states'].append(state)

        return trajectory
    
    def sample_cf_trajectory(self, trajectory, interventions_set):
        """
        Computes a counterfactual trajectory/instance of the game for a given set of interventions
        """
        cf_trajectory = {
            'states' : [],
            'agents_info_states' : [],
            'opponents_info_states' : [],
            'agents_actions' : [],
            'opponents_actions' : [],
            'opponents_gumbels' : []
        }
        
        # initial state
        state = {}
        state['deck'] = trajectory['states'][0]['deck']
        state['score'] = {'agents' : 0, 'opponents' : 0}
        state['agents_hands'] = trajectory['states'][0]['agents_hands']
        state['opponents_hands'] = trajectory['states'][0]['opponents_hands']

        # store data from the previous step, necessary for deicision making
        prev_agents_info_states = [None] * self.num_of_agents
        prev_opps_info_states = [None] * self.num_of_opps
        prev_agents_actions = [None] * self.num_of_agents
        prev_opps_actions = [None] * self.num_of_opps

        for t in range(self.horizon):
            # observations
            agents_obs = self._get_ag_obs(state)
            opps_obs = self._get_opp_obs(state)

            # info-states and actions
            opps_gumbels = np.array(trajectory['opponents_gumbels'][t])
            
            agents_info_states = [
                ag._get_info_state(agents_obs[ag.id], prev_agents_actions[ag.id], prev_agents_info_states[ag.id])
                for ag in self.agents
            ]
            # agents' policies are deterministic
            agents_actions = [
                ag.policy(agents_info_states[ag.id]) 
                for ag in self.agents
            ]
            # check for interventions
            for intervention in interventions_set:
                if intervention['t'] != t:
                    continue
                for ag in self.agents:
                    if intervention['agent'] == ag.id:
                        assert intervention['cf_action'] == agents_actions[ag.id]
                        assert intervention['new_action'] in state['agents_hands'][ag.id]
                        agents_actions[ag.id] = intervention['new_action']
            opps_info_states = [
                opp._get_info_state(opps_obs[opp.id], prev_opps_actions[opp.id], prev_opps_info_states[opp.id])
                for opp in self.opps
            ]
            # opponents' policies are stochastic
            with np.errstate(divide='ignore'):
                opps_actions = [
                    state['opponents_hands'][opp.id][np.argmax(np.log(opp.policy(opps_info_states[opp.id])) + opps_gumbels[opp.id])] 
                    for opp in self.opps
                ]
            
            # update trajectory
            cf_trajectory['states'].append(state)
            cf_trajectory['agents_info_states'].append(agents_info_states)
            cf_trajectory['opponents_info_states'].append(opps_info_states)
            cf_trajectory['agents_actions'].append(agents_actions)
            cf_trajectory['opponents_actions'].append(opps_actions)
            # jsonify gumbels
            opps_gumbels = opps_gumbels.tolist()
            cf_trajectory['opponents_gumbels'].append(opps_gumbels)
            
            # next state
            state = self._get_next_state(state, agents_actions, opps_actions)

            prev_agents_info_states = agents_info_states
            prev_opps_info_states = opps_info_states
            prev_agents_actions = agents_actions
            prev_opps_actions = opps_actions
        
        # terminal state
        cf_trajectory['states'].append(state)

        return cf_trajectory
    
    def render_traj(self, trajectory, f_traj):
        """
        Write a sampled trajectory on a .txt file
        """
        if 'id' in trajectory:
            f_traj.write(f"Trajectory: {trajectory['id']}\n\n")
        elif 'cf_id' in trajectory:
            f_traj.write(f"CF Trajectory: {trajectory['cf_id']}\n\n")
            
        for t in range(self.N):
            f_traj.write(f"Time-Step {t}\n")
            f_traj.write(f"Score: Agents {trajectory['states'][t]['score']['agents']}, Opponents {trajectory['states'][t]['score']['opponents']}\n")
            f_traj.write(f"Prize: {trajectory['states'][t]['deck'][-1]}\n")
            f_traj.write(f"Agents' hands: {trajectory['states'][t]['agents_hands']}\n")
            f_traj.write(f"Opponents' hands: {trajectory['states'][t]['opponents_hands']}\n")
            f_traj.write(f"Agents' actions: {trajectory['agents_actions'][t]}\n")
            f_traj.write(f"Opponents' actions: {trajectory['opponents_actions'][t]}\n")
        f_traj.write(f"Final score: Agents {trajectory['states'][-1]['score']['agents']}, Opponents {trajectory['states'][-1]['score']['opponents']}\n\n")

        return

    ####################### Utils ############################
    ##########################################################

    def _get_ag_obs(self, state):
        """
        Agents' observations include their hand, the current prize and score
        """
        agents_obs = [{
            'hand' : state['agents_hands'][ag.id], 
            'prize' : state['deck'][-1], 
            'score' : state['score']
        } for ag in self.agents
        ]

        return agents_obs

    def _get_opp_obs(self, state):
        """
        Opponents' observations include their hand, the current prize and score
        """
        opps_obs = [{
            'hand' : state['opponents_hands'][opp.id], 
            'prize' : state['deck'][-1], 
            'score' : state['score']
        } for opp in self.opps
        ]

        return opps_obs

    def _get_next_state(self, state, agents_actions, opps_actions):
        """
        States include the deck, the current score and all players' hands
        """
        next_state = {}
        next_state['deck'] = state['deck'][:-1]
        next_state['score'] = {
            'agents' : state['score']['agents'] + (sum(agents_actions) > sum(opps_actions)) * state['deck'][-1],
            'opponents' : state['score']['opponents'] + (sum(agents_actions) < sum(opps_actions)) * state['deck'][-1]
        }
        next_state['agents_hands'] = [
            [x for x in state['agents_hands'][ag.id] if x != agents_actions[ag.id]] 
            for ag in self.agents
        ]
        next_state['opponents_hands'] = [
            [x for x in state['opponents_hands'][opp.id] if x != opps_actions[opp.id]] 
            for opp in self.opps
        ]

        return next_state
