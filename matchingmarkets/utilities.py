import numpy as np

# Various functions to simulate markets


def randomType(numTypes):
    """
    uniformly assigns agent's type
    input is number of categories
    """
    return np.random.randint(numTypes)


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
