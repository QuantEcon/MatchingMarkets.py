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


def blood_types(no_input):
    """
    TypeGenerator function
    Generates blood types
    Weighed according to US distribution
    Input: void. Input form included only for compatibility
    Returns a string (ex. "AB-" or "O+")
    """
    rndn = np.random.rand()
    if rndn < 0.374:
        return "O+"
    elif 0.374 < rndn < 0.731:
        return "A+"
    elif 0.731 < rndn < 0.816:
        return "B+"
    elif 0.816 < rndn < 0.85:
        return "AB+"
    elif 0.85 < rndn < 0.916:
        return "O-"
    elif 0.916 < rndn < 0.979:
        return "A-"
    elif 0.979 < rndn < 0.994:
        return "B-"
    elif rndn > 0.994:
        return "AB-"
    else:
        raise Exception("No Blood Type Found")


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

######################################################
#                                                    #
# Neighbor Functions                                 #
# Creates edge weights in the potential match graph  #
#                                                    #
######################################################


def neighborSameType(agent, otherAgent, cutoff=1):
    """
    compatFct overload
    returns 1 if types are same
    """
    result = agent.type == otherAgent.type \
        and agent.name != otherAgent.name
    return result


def neighborSameTypeWithSelf(agent, otherAgent, cutoff=1):
    """
    compatFct overload
    returns 1 if types are same
    """
    return agent.type == otherAgent.type


def stochastic_neighborSameType(agent, otherAgent, cutoff=1):
    """
    compatFct overload
    returns 1 if types are same
    """
    result = agent.type == otherAgent.type \
        and agent.name != otherAgent.name
    draw = np.random.random()
    if draw > cutoff:
        return 0
    else:
        return 1*result


def rngDraw(agent, otherAgent, cutoff=1):
    """
    compatFct overload
    used as standard
    returns 1 if rng < cutoff
    else 0
    cutoff in [0,1]
    """
    draw = np.random.random()
    if draw > cutoff:
        return 1
    else:
        return 0


def std_compat(agent, otherAgent, cutoff=1):
    """
    compatFct overload
    returns the value in cutoff as compatibility result
    """
    return cutoff

#####################################################
#                                                   #
# Match Utility functions                           #
# Returns the utility of a match between two agents #
#                                                   #
#####################################################


def utilSameType(agent, otherAgent, cutoff=1):
    """
    matchUtilFct overload
    utility = 1 if same type, 0 otherwise
    """
    return cutoff * (agent.type == otherAgent.type)


def utilRandom(agent, otherAgent, cutoff=1):
    """
    matchUtilFct
    returns random utility in [0,1]
    """
    return np.random.random()


#####################################################
#                                                   #
# Transplant functions                              #
# Can be used for both edge weights and match util  #
#                                                   #
#####################################################


def transplant_compatibility(agent, otherAgent, cutoff=1):
    """
    Looks for blood type compatibility
    Based kidney exchange compatibiity
    agent is assumed donor, otherAgent receiver
    cutoff input is the success probability
    """
    assert type(agent.type) is str,\
        "Types must be in string format for transplant compat"
    if agent.type2[0] == "O":
        return True * cutoff
    elif agent.type2[0] == "B":
        if otherAgent.type in ["AB+", "AB-", "B+", "B-"]:
            return True * cutoff
        else:
            return False
    elif agent.type2 == "A-" or agent.type2 == "A+":
        if otherAgent.type in ["AB+", "AB-", "A+", "A-"]:
            return True * cutoff
        else:
            return False
    elif agent.type2 == "AB-" or agent.type2 == "AB+":
        if otherAgent.type in ["AB+", "AB-"]:
            return True * cutoff
        else:
            return False
    else:
        raise Exception("Blood Type match error with ", agent.name, " and ",
                        otherAgent.name)


def blood_compatibility(agent, otherAgent, cutoff=1):
    """
    Looks for blood type compatibility
    Based on red cell compatibility
    agent is assumed donor, otherAgent receiver
    cutoff input is the success probability
    """
    assert type(agent.type) is str,\
        "Types must be in string format for transplant compat"
    if agent.type2 == "O-":
        return True * cutoff
    elif agent.type2 == "O+":
        if otherAgent.type in ["AB+", "A+", "B+", "O+"]:
            return True * cutoff
        else:
            return False
    elif agent.type2 == "B-":
        if otherAgent.type in ["AB+", "AB-", "B+", "B-"]:
            return True * cutoff
        else:
            return False
    elif agent.type2 == "B+":
        if otherAgent.type in ["AB+", "B+"]:
            return True * cutoff
        else:
            return False
    elif agent.type2 == "A-":
        if otherAgent.type in ["AB+", "AB-", "A+", "A-"]:
            return True * cutoff
        else:
            return False
    elif agent.type2 == "A+":
        if otherAgent.type in ["AB+", "A+", "B+", "O+"]:
            return True * cutoff
        else:
            return False
    elif agent.type2 == "AB-":
        if otherAgent.type in ["AB+", "AB-"]:
            return True * cutoff
        else:
            return False
    elif agent.type2 == "AB+":
        if otherAgent.type in ["AB+"]:
            return True * cutoff
        else:
            return False
    else:
        raise Exception("Blood Type match error with ", agent.name, " and ",
                        otherAgent.name)