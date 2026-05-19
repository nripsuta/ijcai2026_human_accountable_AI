import numpy as np

def prepare_responsibility_data(causes, num_of_agents):
    """
    Compute all agents' m_j, k and k_j for each actual cause
    """
    data = []
    for cause in causes:
        d = {}
        d['id'] = cause[-1]['id']
        for ag_id in range(num_of_agents):
            d['m' + str(ag_id)] = len([
                i for i in cause if i['agent'] == ag_id and not i['contingency']
            ])
            d['k' + str(ag_id)] = len(cause) - len([
                i for i in cause if i['agent'] == ag_id and i['contingency']
            ])
        d['k'] = len(cause)
        data.append(d)

    return data
        
def attribute_responsibility_ch(data, num_of_agents):
    """
    CH method
    """
    resp = []
    cause_ids = []

    for ag_id in range(num_of_agents):
        if not data: r=0
        else: r = max([cause['m' + str(ag_id)]/cause['k'] for cause in data])
        if not r: cause_id = -1
        else:
            for cause in data:
                if cause['m' + str(ag_id)]/cause['k'] == r:
                    cause_id = cause['id']
                    break
        resp.append(r)
        cause_ids.append(cause_id)
    
    return resp, cause_ids

def attribute_responsibility_tr(data, num_of_agents):
    """
    TR method
    """
    resp = []
    cause_ids = []

    for ag_id in range(num_of_agents):
        if not data: r=0
        else: r = max([cause['m' + str(ag_id)]/cause['k' + str(ag_id)] for cause in data])
        if not r: cause_id = -1
        else:
            for cause in data:
                if cause['m' + str(ag_id)]/cause['k' + str(ag_id)] == r:
                    cause_id = cause['id']
                    break
        resp.append(r)
        cause_ids.append(cause_id)
    
    return resp, cause_ids

def compute_responsibilities(causes, num_of_agents, num_of_trajectories):
    """
    Compute responsibility assignments over all trajectories
    """
    lst_resp = []
    lst_cause_ids = []

    for traj_id in range(num_of_trajectories):
        resp, cause_ids = compute_responsibility(causes, num_of_agents, traj_id)
        lst_resp.append(resp)
        lst_cause_ids.append(cause_ids)

    return lst_resp, lst_cause_ids

def compute_responsibility(causes, num_of_agents, traj_id):
    """
    Compute responsibility assignment for one trajectory based on CH and TR methods
    """
    data = prepare_responsibility_data(causes[traj_id], num_of_agents)
    resp = {}
    cause_ids = {}

    resp['CH'], cause_ids['CH'] = attribute_responsibility_ch(data, num_of_agents)
    resp['TR'], cause_ids['TR'] = attribute_responsibility_tr(data, num_of_agents)

    return resp, cause_ids