import random
import copy
import numpy as np

# Matching algorithms should take a list of agents
# then return a dict of directed matches
# Bilateral matches should have both pointing to each other
# The concept of __initiation__ of a match is important
# input agents can initiate match attempts with all agents in market
#      Arguments
#    ---------
#    Agents: list
#        list of agents initiating matches
#    Returns
#    -------
#    dict { agent.name : agent.name } of matches


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


def TTC(Mrkt, Agents, verbose=False):
    """
    Top Trading Cycle algorithm
    Agents initiating cycles

    Preferences are weighed by expected utility
    That is, utility of 10 with 50% success rate
    is weighed as 5 utils by agent in ranking

    NOTE: Algorithm not guaranteed to be deterministic
          if preferences are not strict
    """
    matched = dict()
    to_match = list(Agents)
    iter_num = 0
    # While agents unmatched, iterate
    while len(to_match) > 0:
        iter_num += 1
        to_match_names = [a.name for a in to_match]

        if verbose:
            print("\n\n-------------------\nTTC Iteration ",
                  iter_num, "\n\tTo Match", to_match_names)

        preference_graph = dict()

        # If no neighbors, remove
        for agent in reversed(to_match):
            if len(set(agent.neighbors()).intersection(to_match_names)) == 0:
                to_match.remove(agent)
                to_match_names.remove(agent.name)
                if verbose:
                    print("\tremoved agent ", agent.name)
        # Now, get preferences and form graph
        for agent in to_match:
            # Sort preferences in decreasing order
            preferenceList = sorted(agent.match_util,
                                    key=lambda k: agent.match_util[k] *
                                    agent.match_fail_prob[k],
                                    reverse=True)
            # Add top available preference to graph
            for preference in preferenceList:
                if preference in to_match_names:
                    preference_graph[agent.name] = [preference]
                    break

        if verbose:
            print("\n\nPreference Graph\n\t", preference_graph)

        # Find cycles in graph
        cycles = strongly_connected_components(preference_graph)

        if verbose:
            print("\n\nCycles\n\t", cycles)

        for cycle in cycles:
            # if cycle singleton, add to match if pointing to self
            if len(cycle) == 1:
                if preference_graph[cycle[0]] == [cycle[0]]:
                    matched[cycle[0]] = cycle[0]
                    to_remove_index = np.inf
                    for i in range(len(to_match)):
                        if to_match[i].name == cycle[0]:
                            to_remove_index = i
                            del to_match[to_remove_index]
                            break
                continue
            # else add members of cycle to result and clean to_match up
            for i in range(len(cycle)):
                matched[cycle[i-1]] = cycle[i]
            for i in range(len(cycle)):
                for agent in to_match:
                    if agent.name == cycle[i]:
                        to_match.remove(agent)

    return matched
