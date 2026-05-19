import numpy as np
import copy
import itertools


class TSNode():
    
    def __init__(self, parent, parent_agents_actions, state, c, t, num_of_agents, num_of_opps):
        
        self.parent = parent
        self.parent_agents_actions = parent_agents_actions
        self.state = state
        self.c = c
        self.t = t
        self.agents_info_states = [None] * num_of_agents
        self.opps_info_states = [None] * num_of_opps
        self.opps_actions = [None] * num_of_opps
        self.children = {}
        self.interventions_set = []

class Actual_Causation():
    
    def __init__(self, env, traj ,kappa):
        
        self.env = env
        self.traj = traj
        self.kappa = kappa
        self.horizon = len(traj['agents_actions'])
        self.interventions_sets = []
        proxy_node = TSNode(None, [None] * env.num_of_agents, None, -1, -1, env.num_of_agents, env.num_of_opps)
        self.root_node = TSNode(proxy_node, [None] * env.num_of_agents, traj['states'][0], 0, 0, env.num_of_agents, env.num_of_opps) 

##################### Tree Search ########################
##########################################################

    def tree_search(self, node):
        
        env = self.env
        kappa = self.kappa

        parent = node.parent
        t = node.t
        c = node.c
        state = node.state

        # final state
        if t == self.horizon:
            if state['score']['agents'] > state['score']['opponents']:
                node.interventions_set[-1]['id'] = len(self.interventions_sets)
                self.interventions_sets.append(node.interventions_set)
            return

        # what would have happened
        # counterfactual observations
        cf_agents_obs = env._get_ag_obs(state)
        cf_opps_obs = env._get_opp_obs(state)

        # counterfactual info-states and actions
        opps_gumbels = self.traj['opponents_gumbels'][t]

        cf_agents_info_states = [
            ag._get_info_state(
                cf_agents_obs[ag.id], 
                node.parent_agents_actions[ag.id], 
                parent.agents_info_states[ag.id]
            )
            for ag in env.agents
        ]
        cf_agents_actions = [
            ag.policy(cf_agents_info_states[ag.id]) 
            for ag in env.agents
        ]
        cf_opps_info_states = [
            opp._get_info_state(
                cf_opps_obs[opp.id], 
                parent.opps_actions[opp.id],  
                parent.opps_info_states[opp.id]
            )
            for opp in env.opps
        ]
        with np.errstate(divide='ignore'):
            cf_opps_actions = [
                state['opponents_hands'][opp.id][np.argmax(np.log(opp.policy(cf_opps_info_states[opp.id])) + opps_gumbels[opp.id])] 
                for opp in env.opps
            ]
        node.agents_info_states = cf_agents_info_states
        node.opps_info_states = cf_opps_info_states
        node.opps_actions = cf_opps_actions

        # under no intervention
        # counterfactual next state
        cf_next_state = env._get_next_state(state, cf_agents_actions, cf_opps_actions)

        node.children[tuple(cf_agents_actions)] = TSNode(node, cf_agents_actions, cf_next_state, c, t+1, env.num_of_agents, env.num_of_opps)
        node.children[tuple(cf_agents_actions)].interventions_set = copy.deepcopy(node.interventions_set)
        self.tree_search(node.children[tuple(cf_agents_actions)])

        # under intervention(s)
        if c < kappa:
            for agents_actions in [list(tup) for tup in itertools.product(*state['agents_hands'])]:
                if agents_actions == cf_agents_actions:
                    continue
                num_of_new_interventions = len([a for a, b in zip(cf_agents_actions, agents_actions) if a!=b])                
                if c + num_of_new_interventions > kappa:
                    continue
                next_state = env._get_next_state(state, agents_actions, cf_opps_actions)
                node.children[tuple(agents_actions)] = TSNode(node, agents_actions, next_state, c + num_of_new_interventions, t+1, env.num_of_agents, env.num_of_opps)
                self.record_interventions(node, agents_actions, cf_agents_actions, t)
                self.tree_search(node.children[tuple(agents_actions)])

        return


    def record_interventions(self, node, agents_actions, cf_agents_actions, t):
        """
        Keeps record of the interventions happened so far in the taken path; characterizes an intervention as
        part of the actual cause or part of the contingency (according to definitions HP and TR)
        """
        env = self.env
        node.children[tuple(agents_actions)].interventions_set = copy.deepcopy(node.interventions_set)
        for ag in env.agents:
            if agents_actions[ag.id] != cf_agents_actions[ag.id]:  
                node.children[tuple(agents_actions)].interventions_set.append({
                    't' : t,
                    'agent' : ag.id,
                    'cf_action' : cf_agents_actions[ag.id],
                    'new_action' : agents_actions[ag.id],
                    # contingency according to the TR definition
                    'tr_contingency' : node.agents_info_states[ag.id] != self.traj['agents_info_states'][t][ag.id],
                    # contingency according to the TR definition where info_state is considered the agent's hand only
                    'tr_hand_contingency' : node.agents_info_states[ag.id]['hand'] != self.traj['agents_info_states'][t][ag.id]['hand'],
                    # contingency according to the HP definition
                    'hp_contingency' : agents_actions[ag.id] == self.traj['agents_actions'][t][ag.id]
                })
                
        return
    
####################### Causes ###########################
##########################################################

    def compute_BFCs(self):
        """
        Compute But-For causes
        """
        interventions_sets = copy.deepcopy(self.interventions_sets)
        bf_causes = list(filter(
            lambda f: not any(
                set((i['t'], i['agent']) for i in f) > set((i['t'], i['agent']) for i in g) 
                for g in self.interventions_sets 
            ), interventions_sets
        ))
        for bf_cause in bf_causes:
            for i in bf_cause:
                i['contingency'] = False
                i.pop('hp_contingency')
                i.pop('tr_contingency')
                i.pop('tr_hand_contingency')

        return bf_causes

    def compute_HPCs(self):
        """
        Compute actual causes (HP defintion)
        """
        interventions_sets = copy.deepcopy(self.interventions_sets)
        hp_causes = list(filter(
            lambda f: not any(
                set((i['t'], i['agent']) for i in f if not i['hp_contingency']) > set((i['t'], i['agent']) for i in g if not i['hp_contingency']) 
                for g in self.interventions_sets
            ), interventions_sets
        ))
        for hp_cause in hp_causes:
            for i in hp_cause:
                i['contingency'] = i.pop('hp_contingency')
                i.pop('tr_contingency')
                i.pop('tr_hand_contingency')

        return hp_causes

    def compute_TRCs(self):
        """
        Compute actual causes (TR definition)
        """
        interventions_sets = copy.deepcopy(self.interventions_sets)
        tr_causes = list(filter(
            lambda f: not any(
                set((i['t'], i['agent']) for i in f) > set((i['t'], i['agent']) for i in g) 
                for g in self.interventions_sets 
            ), interventions_sets
        ))
        for tr_cause in tr_causes:
            for i in tr_cause:
                i['contingency'] = i.pop('tr_contingency')
                i.pop('hp_contingency')
                i.pop('tr_hand_contingency')

        return tr_causes