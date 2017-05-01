import random
import copy
from copy import deepcopy
import numpy as np
import networkx as nx

# Matching algorithms should take a list of agents
# then return a dict of directed matches
# Bilateral matches should have both pointing to each other
# The concept of __initiation__ of a match is important
# input agents initiate match attempts with all agents in market
#      Arguments
#    ---------
#    Mrkt: mm.Market object
#        The market in which the matches are made
#    Agents: list
#        list of agents initiating matches
#    Returns
#    -------
#    dict { agent.name : agent.name } of matches


def arbitraryMatch(Mrkt, Agents, verbose=False):
    """
    Random __bilateral__ matches
        bilateral here means two agents strictly match each other
    Agents in input initiate matches
    Initiating agent can match with anyone else in the market
    Source: Same as one used in Akbarpour & al. (2014)
    Proven Properties: None. We're randomly matching; what did you expect
    Arguments
    ---------
    Mrkt: mm.Market object
        The market in which the matches are made
    Agents: list
        list of agents initiating matches
    verbose: bool
        Whether algorithm prints information on action
    Returns
    -------
    dict { agent.name : agent.name } of matches


    References: "Dynamic Matching Market Design", Akbarpour, Li & Gharan, 2014
    """
    if verbose:
        print("\n\n++++\nStarting Arbitrary Match Algo\n++++\n\n")
    matched = dict()
    allAgentNames = [a.name for a in Mrkt.Agents]
    if verbose:
        print("Agents to match ", [a.name for a in Agents], "\n")
    # copy list of agents to match
    # to delete on while iterating
    AgentCopy = list(Agents)
    for agent in Agents:
        # If not in pool, skip
        if agent not in AgentCopy:
            continue
        myNeighbors = agent.neighbors()
        if verbose:
            print("Trying:", agent.name, "in Pool",
                  [a.name for a in AgentCopy])
        # remove already matched neighbors
        localAgentNames = [a.name for a in AgentCopy]
        for neighborName in reversed(myNeighbors):
            if neighborName in allAgentNames and \
                      neighborName not in localAgentNames:
                myNeighbors.remove(neighborName)
        if verbose:
            if len(myNeighbors) == 0:
                print("\tNo Neighbors for ", agent.name)
            else:
                print("\tNeighbors", myNeighbors)
        # If neighbors, match at random
        if len(myNeighbors) > 0:
            match = random.choice(myNeighbors)
            matched[agent.name] = match
            matched[match] = agent.name
            if verbose:
                print("\tMatched ", agent.name, " with ",
                      match)
            # Clean up matched agents
            AgentCopy.remove(agent)
            for agent_match in AgentCopy:
                if agent_match.name == match:
                    AgentCopy.remove(agent_match)
                    break

    if verbose:
        print("\n\n++++++\nArbitrary Match Algorithm Done\n+++++++\n\n")
    return matched


def serialDictatorship(Mrkt, Agents, verbose=False,
                       order=lambda x: (x.time_to_critical - x.sojourn)
                       ):

    """
    Random __bilateral__ matches
        bilateral here means two agents strictly match each other
    Agents in input initiate matches
    Initiating agent can match with anyone else in the market
    Source: Same as one used in Akbarpour & al. (2014)
    Proven Properties: Strategyproof,

    Arguments
    ---------
    Mrkt: mm.Market object
        The market in which the matches are made
    Agents: list
        list of agents initiating matches
    order: function(mm.Agent) -> Real
        a function that assigns a number to an agent
        Used to create the sorting on which agents are used
        Default uses time left in the market before perishing
    verbose: bool
        Whether algorithm prints information on action
    Returns
    -------
    dict { agent.name : agent.name } of matches


    """
    allAgentNames = [a.name for a in Mrkt.Agents]
    AgentOrder = AgentCopy = list(Agents)
    if verbose:
        print("\nSerial Dictatorship Algorithm\n")
        print("Agents to match ", [a.name for a in AgentOrder], "\n")

    # Sort Agents
    AgentOrder.sort(key=order)
    if verbose:
        print("\nSorted Agents ", AgentOrder)

    # copy list of agents to match to delete on while iterating
    AgentCopy = list(Agents)
    result = dict()  # Return value of the algorithm

    # Implement matches
    for agent in AgentOrder:
        # If matched, skip
        if agent not in AgentCopy:
            continue
        localAgentNames = [a.name for a in AgentCopy]
        myNeighbors = agent.neighbors()
        if verbose:
            print("Trying:", agent.name, "in Pool",
                  [a.name for a in AgentCopy])
        # remove already matched neighbors
        localAgentNames = [a.name for a in AgentCopy]
        for neighborName in reversed(myNeighbors):
            if neighborName in allAgentNames and \
                      neighborName not in localAgentNames:
                myNeighbors.remove(neighborName)
        if verbose:
            if len(myNeighbors) == 0:
                print("\tNo Neighbors for ", agent.name)
            else:
                print("\tNeighbors", myNeighbors)

        # If neighbors, get match
        if len(myNeighbors) > 0:
            potential_matches = {name: agent.match_util[name]
                                 for name in agent.match_util
                                 if (name in myNeighbors and
                                     agent.match_fail_prob[name] > 0)}
            if verbose:
                print("Potential matches for ", agent.name,
                      potential_matches.keys())

            # Get preferred agent
            match = max(potential_matches,
                        key=potential_matches.get)
            result[agent.name] = match
            result[match] = agent.name
            if verbose:
                print("\tMatched ", agent.name, " with ",
                      match)
            # Clean up matched agents
            AgentCopy.remove(agent)
            for agent_match in AgentCopy:
                if agent_match.name == match:
                    AgentCopy.remove(agent_match)
                    break

    if verbose:
        print("\n\n++++++\nSerial Dictatorship Done\n+++++++\n\n")
    return result


def max_weight_matching(Mrkt, Agents, verbose=False, maxcardinality=True):
    """
    Computes max-weight matching of graph of inputted agents
        based on the “blossom” method for finding augmenting paths
        and the “primal-dual” method for finding a matching of maximum weight,
        both methods invented by Jack Edmonds
    Implemented by NetworkX
    Runtime: O(n^3) for n nodes
    Arguments
    ---------
    Mrkt: mm.Market object
        The market in which the matches are made
    Agents: list
        list of agents initiating matches
    maxcardinality: bool
        if True, compute the maximum-cardinality matching
        with maximum weight among all maximum-cardinality matchings.
    verbose: bool
        Whether algorithm prints information on action
    Returns
    -------
    dict { agent.name : agent.name } of matches

    Reference:
        “Efficient Algorithms for Finding Maximum Matching in Graphs”,
        Zvi Galil, ACM Computing Surveys, 1986.
    """
    if verbose:
        print("\nMax Weight Match Algorithm\n")
        print("Agents to match ", [a.name for a in Agents], "\n")

    # If Agents not whole market, get subgraph
    if len(Mrkt.Graph.nodes()) != len(Agents):
        to_match = deepcopy(Mrkt.Graph.subgraph(Agents))
    else:
        to_match = Mrkt.Graph
    # Workaround of assertionerror in Nx verifyOptimum() function
    # Breaks around integer weights
    for u, v, d in to_match.edges(data=True):
        d['weight'] = float(d['weight'])

    mate = nx.max_weight_matching(to_match, maxcardinality=maxcardinality)

    result = {a.name: mate[a].name for a in mate}
    return result


def max_cardinality_matching(Mrkt, Agents, verbose=False):
    """
    Find a maximal cardinality matching in the graph.
    A matching is a subset of edges in which no node occurs more than once. 
    The cardinality of a matching is the number of matched edges.
    Implemented by NetworkX
    Runtime: O(e) for e edges

    The algorithm greedily selects a maximal matching M of the graph G
    (i.e. no superset of M exists). It runs in `O(|E|)` time.

    Arguments
    ---------
    Mrkt: mm.Market object
        The market in which the matches are made
    Agents: list
        list of agents initiating matches
    verbose: bool
        Whether algorithm prints information on action
    Returns
    -------
    dict { agent.name : agent.name } of matches

    """
    if verbose:
        print("\nMax Weight Match Algorithm\n")
        print("Agents to match ", [a.name for a in Agents], "\n")

    # If Agents not whole market, get subgraph
    if len(Mrkt.Graph.nodes()) != len(Agents):
        to_match = deepcopy(Mrkt.Graph.subgraph(Agents))
    else:
        to_match = Mrkt.Graph
    # Workaround of assertionerror in Nx verifyOptimum() function
    # Breaks around integer weights
    for u, v, d in to_match.edges(data=True):
        d['weight'] = float(d['weight'])

    mate = nx.maximal_matching(to_match)

    result = {a[0].name: a[1].name for a in mate}
    return result
