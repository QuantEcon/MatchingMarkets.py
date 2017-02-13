import numpy as np

from matchingmarkets.algorithms import arbitraryMatch

# Meta Algorithms define the time of matching
# They also dictate who gets passed into a matching algorithm
# Inputs are a Market object
# output is a dict of directed matches


def meta_Always(Market, match=arbitraryMatch):
    """
    Attempts everyone, every period
    """
    return match(Market, Market.Agents)


def meta_Patient(Market, a=np.inf, match=arbitraryMatch):
    """
    Patient(a) algorithm from Akbarpour et al. (2016)
    a is default set to infinity, so patient() algorithm by default
    Attempts match if agent is critical or if his sojourn==a
    """
    AgentList = [ag for ag in Market.Agents if ag.is_critical or
                 ag.sojourn == a]
    return match(Market, AgentList)

def meta_Greedy(Market, match=arbitraryMatch):
    """
    Attempts match if agent is entering market
    """
    AgentList = [ag for ag in Market.Agents if ag.sojourn == 0]
    return match(Market, AgentList)