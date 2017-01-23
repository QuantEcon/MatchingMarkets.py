import random
import copy
import numpy as np

# Matching algorithms should take a list of agents
# then return a dict of directed matches
# Bilateral matches should have both pointing to each other
# The concept of __initiation__ of a match is important
# input agents initiate match attempts with all agents in market
#      Arguments
#    ---------
#    Agents: list
#        list of agents initiating matches
#    Returns
#    -------
#    dict { agent.name : agent.name } of matches


def arbitraryMatch(Mrkt, Agents):
    """
    Random __bilateral__ matches
    Agents in input initiate matches
    Initiating agent can match with anyone
    """
    matched = dict()
    allAgentNames = [a.name for a in Mrkt.Agents]
    # copy list of agents to match
    # to delete on while iterating
    AgentCopy = list(Agents)
    for agent in Agents:
        if agent not in AgentCopy:
            continue
        myNeighbors = agent.neighbors()
        # remove already matched neighbors
        localAgentNames = [a.name for a in AgentCopy]
        for neighborName in myNeighbors:
            if neighborName in allAgentNames and \
                      neighborName not in localAgentNames:
                myNeighbors.remove(neighborName)
        # If neighbors, match at random
        if len(myNeighbors) > 0:
            match = random.choice(myNeighbors)
            matched[agent.name] = match
            matched[match] = agent.name
            # Clean up matched agents
            AgentCopy.remove(agent)
            for agent_match in AgentCopy:
                if agent_match.name == match:
                    AgentCopy.remove(agent_match)
                    break
    return matched


def strongly_connected_components(graph):
    """
    Find the strongly connected components in a graph using
    Tarjan's algorithm.

    Implementation credit: http://www.logarithmic.net/pfh/blog/01208083168

    Used to find cycles in TTC algorithm
    Arguments
    --------
    graph: dict< node_name, list<node_name> >
         mapping node names to lists of successor nodes.

    Returns
    -------
    list of tuples of SCCs in graph
    """

    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    result = []

    def strongconnect(node):
        # set the depth index for this node to the smallest unused index
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)

        # Consider successors of `node`
        try:
            successors = graph[node]
        except:
            successors = []
        for successor in successors:
            if successor not in lowlinks:
                # Successor has not yet been visited; recurse on it
                strongconnect(successor)
                lowlinks[node] = min(lowlinks[node], lowlinks[successor])
            elif successor in stack:
                # the successor is in the stack
                # hence in the current strongly connected component (SCC)
                lowlinks[node] = min(lowlinks[node], index[successor])

        # If `node` is a root node, pop the stack and generate an SCC
        if lowlinks[node] == index[node]:
            connected_component = []

            while True:
                successor = stack.pop()
                connected_component.append(successor)
                if successor == node:
                    break
            component = tuple(connected_component)
            # storing the result
            result.append(component)

    for node in graph:
        if node not in lowlinks:
            strongconnect(node)

    return result


def TTC(Mrkt, Agents):
    """
    Top Trading Cycle algorithm
    Implements __strict__ ordered preference TTC
    Agents initiating cycles
    Agents can only point to __one__ house at any iteration
    NOTE: agents can match with themselves in TTC
          If selfMatch == False many will perish!!
    """
    matched = dict()
    market = list(Agents)
    # While agents unmatched, iterate
    while len(market) > 0:
        marketNames = [a.name for a in market]
        preference_graph = dict()
        # Ask each agent to indicate his "top" (most preferred) house.
        for agent in market:
            # Sort preferences in decreasing order
            preferenceList = sorted(agent.match_util,
                                    key=lambda k: agent.match_util[k],
                                    reverse=True)
            """
            remove preferences for non neighbors here
            """
            # Add top available preference to graph
            for preference in preferenceList:
                if preference in marketNames:
                    preference_graph[agent.name] = [preference]
                    break
        # Find cycles in graph
        cycles = strongly_connected_components(preference_graph)
        for cycle in cycles:
            # if cycle singleton, add to match if pointing to self
            if len(cycle) == 1:
                if preference_graph[cycle[0]] == [cycle[0]]:
                    matched[cycle[0]] = cycle[0]
                    to_remove_index = np.inf
                    for i in range(len(market)):
                        if market[i].name == cycle[0]:
                            to_remove_index = i
                            del market[to_remove_index]
                            break
                continue
            # else add members of cycle to result and clean market up
            for i in range(len(cycle)):
                matched[cycle[i-1]] = cycle[i]
            for i in range(len(cycle)):
                for agent in market:
                    if agent.name == cycle[i]:
                        market.remove(agent)
    return matched
