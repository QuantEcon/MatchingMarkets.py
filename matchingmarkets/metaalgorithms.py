import numpy as np
from copy import deepcopy
from matchingmarkets.algorithms.basic import arbitraryMatch

"""
Meta Algorithms define the time of matching
They also dictate who gets passed into a matching algorithm
Inputs are a Market object
output is a dict of directed matches
"""


def meta_always(Market, match=arbitraryMatch, verbose=False, **kwargs):
    """
    Attempts everyone, every period
    """
    if verbose:
        print("meta_always")
    return match(Market, Market.Agents, verbose=verbose, **kwargs)


def meta_periodic(Market, match=arbitraryMatch, period=1,
                  verbose=False, **kwargs):
    """
    Attempts matches on everyone every x periods
    """
    if verbose:
        print("meta_periodic")

    if -1 < period and period < 1:
        period = 1
    if period < -1:
        period = -period
    if Market.time % int(period) == 0:
        return match(Market, Market.Agents, verbose=verbose, **kwargs)
    else:
        return dict()


def meta_patient(Market, match=arbitraryMatch, a=np.inf,
                 verbose=False, **kwargs):
    """
    Patient(a) algorithm from Akbarpour et al. (2014)
    a is default set to infinity, so patient() algorithm by default
    Attempts match if agent is critical or if his sojourn==a
    """
    if verbose:
        print("meta_patient")
    AgentList = [ag for ag in Market.Agents if ag.is_critical or
                 ag.sojourn == a]
    return match(Market, AgentList, verbose=verbose, **kwargs)


def meta_greedy(Market, match=arbitraryMatch, verbose=False, **kwargs):
    """
    Attempts match if agent is entering market
    """
    if verbose:
        print("meta_greedy")
    AgentList = [ag for ag in Market.Agents if ag.sojourn == 0]
    return match(Market, AgentList, verbose=verbose, **kwargs)


def meta_agents_critical(Market, match=arbitraryMatch, agents=5,
                         num_critical=5, verbose=False, **kwargs):
    """
    Attempts matches on critical agents if number of critical agents above input
    Also attempts matches if certain number of agents in market, based on input
    """
    if verbose:
        print("meta_agents_critical")
    if len(Market.Agents) == agents:
        return match(Market, Market.Agents, verbose=verbose, **kwargs)
    if Market.critical() > num_critical:
        AgentList = [ag for ag in Market.Agents if ag.is_critical]
        return match(Market, AgentList, verbose=verbose, **kwargs)
    else:
        return dict()
