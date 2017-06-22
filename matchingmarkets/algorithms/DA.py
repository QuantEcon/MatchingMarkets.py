import random
import copy
from copy import deepcopy
import numpy as np
from numpy.random import randn
import networkx as nx


"""
Collection of variations on the Gale-Shapley Deffered Acceptance algo

!!!IMPORTANT!!!
    all variations should have m and f be inputted else undefined behavior
"""


def gale_shapley(Mrkt, Agents, verbose=False,
                 m=None, f=None,
                 m_order=lambda x: (x.time_to_critical - x.sojourn),
                 f_order=lambda x: (x.time_to_critical - x.sojourn)
                 ):

    """
    Gale-Shapley deffered acceptance algorithm
    Agents sequentially propose their top preference according to an ordering

    The ordering is a function f(agent) -> float
    The agents are sorted in INCREASING order
        of return value of the ordering fct

    Proven Properties: Strategyproof

    Arguments
    ---------
    Mrkt: mm.Market object
        The market in which the matches are made
    Agents: list
        list of agents initiating matches
    m: agent type or list<agent type>
        the type of the proposers (males in stable marriage)
    f: agent type or list<agent type>
        the type of the acceptors (females in stable marriage)
    m_order: function(mm.Agent) -> Real
        a function that assigns a number to an agent
        Used to create the sorting on which agents are used
        Default uses time left in the market before perishing
    f_order: function(mm.Agent) -> Real
        a function that assigns a number to an agent
        Used to create the sorting on which agents are used
        Default uses time left in the market before perishing
    verbose: bool
        Whether algorithm prints information on action
    Returns
    -------
    dict { agent.name : agent.name } of matches
    """
    if verbose:
        print("\Gale-Shapley Deferred Acceptance Algorithm\n")
        print("Agents to match ", [a.name for a in Agents], "\n")

    # Get males and females for bipartite graph
    agentTypes = set([a.type for a in Agents])
    if m is None and f is None:
        print("\nERROR: Gale-Shapley running without \
                defined males and female agent types")
        return
    if type(m) is not list:
        m = [m]
    if type(f) is not list:
        f = [f]
    if len(m) == 0:
        m = [a for a in agentTypes if a not in f]
    if len(f) == 0:
        f = [a for a in agentTypes if a not in m]
    if verbose:
        print("\nMales: ", [a.name for a in m])
        print("\nFemales: ", [a.name for a in f])

    # Sort Agents
    m.sort(key=m_order)
    f.sort(key=f_order)
    if verbose:
        print("\nSorted Males ", m)
        print("\nSorted Females ", f)

    # copy list of agents to match to delete on while iterating
    men = [a for a in Agents if a.name in m]
    fem = [a for a in Agents if a.name in f]

    # track rejections for males
    rejections = dict()
    for a in m:
        rejections[a] = []

    matches = dict()  # Return value of the algorithm

    iter_num = 0
    # While unmatched persons, iterate
    while len(matches) != len(men) and len(matches) != len(fem):
        iter_num += 1
        if verbose:
            print("\n\n-------------------\G-S Iteration ",
                  iter_num, "\n\tTo Match males:", to_match_names_m,
                  "\n\tFemales: ",
                  to_match_names_f)

        # dict of proposals from men to women
        # for this iteration
        proposals = {}

        # men propose
        for man in men:
            potential_matches = {f_name: man.match_util[f_name]
                                 for f_name in fem
                                 if f_name not in rejections[man]}
            proposals[man] = max(potential_matches, key=potential_matches.get)

        # woman choose the top proposition
        for woman in fem:
            myproposals = {man: proposals[man] for man, v in proposals
                           if proposals[man] == woman}
            my_preferred = max(myproposals, key=myproposals.get)
            matches[woman.name] = my_preferred.name
            matches[my_preferred.name] = woman.name

            for loser in myproposals:
                if loser != my_preferred:
                    rejections[loser].append(woman)

    if verbose:
        print("\n\n++++++\nGale-Shapley Done\n+++++++\n\n")
    return matches
