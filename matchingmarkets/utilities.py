import numpy as np

# Various functions to simulate markets

#
# Agent Type Generating Functions
#


def randomType(numTypes):
    """
    TypeGenerator
    uniformly assigns agent's type
    input is number of categories
    """
    return np.random.randint(numTypes)


def alternatingType(numTypes):
    """
    TypeGenerator
    ------Should only be used for testing-------
    Based on a horrible hack using a global var
    Assigns types alternating starting from 0
    Based on the agent's name (expected to be int ordered to market entry)
    """
    global alternatingTypeCount
    if 'alternatingTypeCount' not in globals():
        alternatingTypeCount = -1
    alternatingTypeCount += 1
    if alternatingType == 0:
        return 0
    return alternatingTypeCount % numTypes


#
# Neighbor Functions
# Creates edge weights in the potential match graph
#


def neighborSameType(agent, otherAgent, cutoff):
    """
    neighborFct overload
    returns 1 if types are same
    """
    result = agent.type == otherAgent.type \
        and agent.name != otherAgent.name
    return result


def neighborSameTypeWithSelf(agent, otherAgent, cutoff):
    """
    neighborFct overload
    returns 1 if types are same
    """
    return agent.type == otherAgent.type


def stochastic_neighborSameType(agent, otherAgent, cutoff):
    """
    neighborFct overload
    returns 1 if types are same
    """
    result = agent.type == otherAgent.type \
        and agent.name != otherAgent.name
    draw = np.random.random()
    if draw > cutoff:
        return 0
    else:
        return 1*result


def rngDraw(agent, otherAgent, cutoff=0):
    """
    neighborFct overload
    used as standard
    returns 1 if rng < cutoff
    else 0
    cutoff in [0,1]
    """
    draw = np.random.random()
    if draw > cutoff:
        return 0
    else:
        return 1


#
# Match Utility functions
# Returns the utility of a match between two agents
#


def utilSameType(agent, otherAgent, cutoff):
    """
    matchUtilFct overload
    utility = 1 if same type,
    0 if self or otherwise
    """
    result = agent.type == otherAgent.type \
        and agent.name != otherAgent.name
    return result


def utilSameTypeWithSelf(agent, otherAgent, cutoff):
    """
    matchUtilFct overload
    utility = 1 if same type, 0 otherwise
    NOTE: Can match with self here
    """
    return agent.type == otherAgent.type
