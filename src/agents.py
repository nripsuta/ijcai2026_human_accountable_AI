import numpy as np
from numpy.testing import assert_almost_equal


class Player():
    
    def __init__(self, id, N, num_of_agents, num_of_opps):
        
        self.id = id
        self.N = N
        self.num_of_agents = num_of_agents
        self.num_of_opps = num_of_opps

    def _get_info_state(self, obs, prev_action, prev_info_state):

        raise NotImplementedError

    def policy(self, info_state):

        raise NotImplementedError


class Agent(Player):
    
    def __init__(self, id, N, num_of_agents, num_of_opps):
        
        super().__init__(id, N, num_of_agents, num_of_opps)
        self.type = 'agent'

    def _get_info_state(self, obs, prev_action, prev_info_state):
        """
        Agents' info-states include their hand, the current prize and if they are winning or not
        """
        info_state = {}
        info_state['hand'] = obs['hand']
        info_state['prize'] = obs['prize']
        score = obs['score']
        info_state['winning'] = score['agents'] > score['opponents']

        return info_state

    def policy(self, info_state):
        """
        Each agent has a different deterministic policy (0, 1)
        """
        hand = info_state['hand']
        prize = info_state['prize']
        winning = info_state['winning']
        
        # common policy for both agents
        if prize in hand: return prize
        gre = [x for x in hand if x > prize]
        le = [x for x in hand if x < prize]
        if (winning and le) or not gre: return max(le)
        return min(gre)

        # # policy of agent 0
        # if self.id == 0:
        #     if prize in hand: return prize
        #     gre = [x for x in hand if x > prize]
        #     le = [x for x in hand if x < prize]
        #     if (winning and le) or not gre: return max(le)
        #     return min(gre)
        # # policy of agent 1
        # else:
        #     if prize > sum(hand)/len(hand) - winning: return max(hand)
        #     return min(hand)


class Opponent(Player):
    
    def __init__(self, id, N, num_of_agents, num_of_opps):
        
        super().__init__(id, N, num_of_agents, num_of_opps)
        self.type = 'opponent'

    def _get_info_state(self, obs, prev_action, prev_info_state):
        """
        Opponents' info-states include their hand, the current prize and if they are winning or not
        """
        info_state = {}
        info_state['hand'] = obs['hand']
        info_state['prize'] = obs['prize']
        score = obs['score']
        info_state['winning'] = score['agents'] < score['opponents']

        return info_state

    def policy(self, info_state):
        """
        All opponents have the same stochastic policy
        """
        hand = info_state['hand']
        prize = info_state['prize']
        winning = info_state['winning']

        greq = [x for x in hand if x >= prize]
        leq = [x for x in hand if x <= prize]
        if (winning and leq) or not greq:
            probs = [1/len(leq)] * len(leq) + [0] * len([x for x in greq if x != prize])
        else:
            probs = [0] * len([x for x in leq if x != prize]) + [1/len(greq)] * len(greq)

        assert_almost_equal(np.sum(probs), 1)    
        
        return probs