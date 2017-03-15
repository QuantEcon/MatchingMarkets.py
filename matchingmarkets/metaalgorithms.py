import numpy as np

from matchingmarkets.algorithms.algorithms import arbitraryMatch

# Meta Algorithms define the time of matching
# They also dictate who gets passed into a matching algorithm
# Inputs are a Market object
# output is a dict of directed matches


def meta_always(Market, match=arbitraryMatch, **kwargs):
    """
    Attempts everyone, every period
    """
    return match(Market, Market.Agents, **kwargs)


def meta_periodic(Market, match=arbitraryMatch, period=1, **kwargs):
    """
    Attempts matches on everyone every x periods
    """

    # dislike the hack here
    # Shouldn't correct period input if < 1

    if -1 < period and period < 1:
        period = 1
    if period < -1:
        period = -period
    if Market.time % int(period) == 0:
        return match(Market, Market.Agents, **kwargs)
    else:
        return dict()


def meta_patient(Market, match=arbitraryMatch, a=np.inf, **kwargs):
    """
    Patient(a) algorithm from Akbarpour et al. (2014)
    a is default set to infinity, so patient() algorithm by default
    Attempts match if agent is critical or if his sojourn==a
    """
    AgentList = [ag for ag in Market.Agents if ag.is_critical or
                 ag.sojourn == a]
    return match(Market, AgentList, **kwargs)


def meta_greedy(Market, match=arbitraryMatch, **kwargs):
    """
    Attempts match if agent is entering market
    """
    AgentList = [ag for ag in Market.Agents if ag.sojourn == 0]
    return match(Market, AgentList, **kwargs)


def meta_agents_critical(Market, match=arbitraryMatch, agents=5,
                         num_critical=5, **kwargs):
    """
    Attempts matches on critical agents if number of critical agents above input
    Also attempts matches if certain number of agents in market, based on input
    """
    if len(Market.Agents) == agents:
        return match(Market, Market.Agents, **kwargs)
    if Market.critical() > num_critical:
        AgentList = [ag for ag in Market.Agents if ag.is_critical]
        return match(Market, AgentList, **kwargs)
    else:
        return dict()
