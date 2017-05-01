import pulp


"""
NOT IMPLEMENTED YET
NOT IMPLEMENTED YET
NOT IMPLEMENTED YET
"""


##########################################
#                                        #
#       Code used by all formulations    #
#                                        #
##########################################

def score(agent1, agent2):
    return agent1.match_util[agent2.name]


def update_solver_ndds(Market, verbose=False):
    """
    Translates NX graph to kidney-solver graph models
    If first period, initiate ndd agents list to Market object
    Then add new agents to ndd list every period

    Arguments
    ------------
    Market: mm.Market object
        NOTE kidney solvers assume that the agents in the market
        are patient/donor pairs.
        This assumes agents have they have both type and type2
            ex. patient_donor_pair.type = "ab+"
                patient_donor_pair.type2 = "O-"
        NOTE We only assume this structure, not specific types in the list
    """

    # If first period, initiate ndd and chain lists
    if Market.time < 2:
        if verbose:
            print("initiating kidney solver")
        Market.ndds = {}  # dict of ndds with {Agent : [outgoing edges]}

    """
    Clean up ndds from last iteration
    then
    Find ndds and input them here
    """


####################################################
#                                                  #
#                Uncapped formulation              #
#                                                  #
####################################################


def add_unlimited_vars_and_constraints(Market, ndds, m):
    """
    For each ndd
        add binary var in m for each outgoing edge
    add constraint to m that sum of used edges per ndd is <= 1

    for each paired donor edge
        add outgoing and incoming edges as binary var to m
    for each paired vertex
        add constraint to m that incoming edge sum is <= 1
    """
    directed_donors = [node for node in Market.Graph.nodes()
                       if node not in ndds]

    # Initiate directed donor solver constraint variables
    for v in Market.Graph.nodes():
        if v not in ndds:
            v.solver_vars_in = []
            v.solver_vars_out = []
    # Initiate edge solver variables
    Market.edge_vars = []

    for ndd in ndds:
        ndd_edge_vars = []
        for e in ndd.edges:
            edge_name = str(str(e[0].type) + "," + str(e[1].type))
            edge_var = LpVariable(edge_name, cat='Binary')
            m += edge_var
            e.edge_var = edge_var
            ndd_edge_vars.append(edge_var)
            e.target_v.solver_vars_in.append(edge_var)
        m += sum(ndd_edge_vars) <= 1

    # Add pair->pair edge variables
    for e in Market.Graph.edges(directed_donors):
        edge_name = str(str(e[0].type) + "," + str(e[1].type))
        edge_var = LpVariable(edge_name, cat='Binary')
        m += edge_var
        # Add constraint variables to keep track
        Market.edge_vars.append(edge_var)
        e[0].solver_vars_out.append(edge_var)
        e[1].solver_vars_in.append(edge_var)

    # Update constraints on LP model
    for v in Market.Graph.nodes():
        if len(v.solver_vars_in) > 1:
            m += sum(v.solver_vars_in) <= 1

    # Sum of edges into a vertex must be >= sum of edges out
    for v in Market.Graph.nodes():
        m.addConstr(quicksum(v.grb_vars_in) >= quicksum(v.grb_vars_out))


def optimise_uuef(cfg):
    """Optimise using the uncapped edge formulation.

    Args:
        cfg: an OptConfig object

    Returns:
        an OptSolution object
    """
    assert Market.acceptable_prob == 1, "uucef  does not support failure-aware matching."

    m = LpProblem("uucef", LpMaximize)

    add_unlimited_vars_and_constraints(cfg.digraph, cfg.ndds, m)

    m.objective = (sum(e.score * e.edge_var for ndd in cfg.ndds
                       for e in ndd.edges) +
                   sum(e.score * var for e in cfg.digraph.es for var in e.grb_vars))

    m.setObjective(obj_expr, GRB.MAXIMIZE)
    optimise(m, cfg)

    # Try all possible cycle start positions
    cycle_start_vv = range(cfg.digraph.n)

    cycle_next_vv = {}
    for e in cfg.digraph.es:
        for var in e.grb_vars:
            if var.x > 0.1:
                cycle_next_vv[e.src.id] = e.tgt.id

    return OptSolution(ip_model=m,
                       cycles=kidney_utils.selected_edges_to_cycles(
                                    cfg.digraph, cycle_start_vv, cycle_next_vv),
                       chains=kidney_utils.get_optimal_chains(cfg.digraph, cfg.ndds),
                       digraph=cfg.digraph)