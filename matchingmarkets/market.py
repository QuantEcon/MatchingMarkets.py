from scipy.stats import poisson
import numpy as np

from matchingmarkets.agent import Agent
from matchingmarkets.algorithms import arbitraryMatch
from matchingmarkets.metaalgorithms import meta_Greedy
from matchingmarkets.utilities import rngDraw


class Market:
    """
    Contains a matching market
    Attributes
    ----------
    Agents: list<agent>
        container for agents
    arrival_rate: int or float
        expected number of arrivals between t and t+1
        Usually the lambda in a poisson process
        0 < a_rate < 1 in continuous time
        0< a_rate in discrete time
    acceptable_set: list<(agent.name, agent.name)>
        list of tuples
        of acceptable bilateral transactions
    average_prob: float
        average fraction of neighbors to an agent
        conditional on agents' types matching
    max_agents: int
        maximum number of agents in market overtime
    time: int
        # of periods since market start
    Welfare: float
        cumul sum of utility of succesful matches
    Perished: list
        container of permanently perished agents
    Matched: list
        container of matched agents
    total_agents: int
        total distinct agents who ever entered market
    """
    def __init__(self, arrival_rate=1, average_prob=lambda: 1,
                 max_agents=1000):
        """
        Generate new market
        """
        self.Agents = list()
        self.arrival_rate = arrival_rate
        self.acceptable_prob = average_prob()
        self.max_agents = max_agents
        self.perished = list()
        self.matched = list()
        self.matched_dict = dict()
        self.time = 0
        self.welfare = 0
        self.total_agents = 0
        self.loss = 0

    def update(self, metaAlgorithm=meta_Greedy, algorithm=arbitraryMatch,
               neighborFct=rngDraw, discount=lambda: 0,
               matchUtilFct=lambda x, y, z: 1, utilityFctInput=0,
               time_to_crit=lambda x: 0, crit_input=1,
               typeGenerator=lambda x: 1, numTypes=1, selfMatch=False):
        """
        Updates the market to a new time period
        Acts on the matching algorithm
            Updates time, creates new agents,
            updates agents attributes, implements matching,
            removes matched/perished agents from Agents
            places matched agents in self.Matched
            places perished agents in self.Perished
            Updates market statistics
        Arguments
        ---------
        algorithm: Matching Algorithm
            takes current market as input
            returns a list of matches
        neighborFct: fct(agent1, agent2, float) -> float
            random function returning agents
            being compatible matches based on input
        discount: fct() -> [0,1]
            function generating agent discount rate
        matchUtilFct: fct(agent1, agent2, float) -> float
            returns utility for agent1 of matching to agent2
        utilityFctInput: float
            input for matchUtilFct (usually rng cutoff value)
        time_to_crit: fct() -> int
            function generating agent time to crit
        crit_input:int
            input in above, usually param in rng fct
        typeGenerator: fct(int) -> int
            function generating agent type
        numTypes: int
            input in typeGenerator
            usually # of types
        """
        # Check if market full, if not get new arrivals
        if self.total_agents < self.max_agents:
            new_agents = poisson.rvs(self.arrival_rate)
            # Create new agents to market
            for i in range(new_agents):
                new_discount = discount()
                new_time_to_crit = time_to_crit(crit_input)
                new_type = typeGenerator(numTypes)
                newAgent = Agent(name=self.total_agents,
                                 discount_rate=new_discount,
                                 time_to_critical=new_time_to_crit,
                                 myType=new_type)
                self.Agents.append(newAgent)
                self.total_agents += 1
            # Add new agents to existings' preference maps
            for oldAgent in self.Agents[:-new_agents]:
                for newAgent in self.Agents[-new_agents:]:
                    oldAgent.addNewToMap(
                                newAgent,
                                utilityResult=matchUtilFct(oldAgent,
                                                           newAgent,
                                                           utilityFctInput),
                                failProbResult=neighborFct(oldAgent,
                                                           newAgent,
                                                           self.acceptable_prob
                                                           )
                                         )
            # Fill preference maps of new agents
            for newAgent in self.Agents[-new_agents:]:
                for otherAgent in [x for i, x
                                   in enumerate(self.Agents) if i != newAgent]:
                        newAgent.addNewToMap(
                                    otherAgent,
                                    utilityResult=matchUtilFct(newAgent,
                                                               otherAgent,
                                                               utilityFctInput
                                                               ),
                                    failProbResult=neighborFct(
                                                        newAgent,
                                                        otherAgent,
                                                        self.acceptable_prob
                                                            )
                                             )
        # update time on agents
        self.time += 1
        for agent in self.Agents:
            agent.update()
        # perform Matching
        matches = metaAlgorithm(self, match=algorithm)
        # If self matches not allowed, clean up
        if selfMatch is False:
            matchCopy = dict(matches)
            for source in matchCopy.keys():
                if matchCopy[source] == source:
                    del matches[source]
        self.matched_dict.update(matches)
        to_remove = list()
        # Update market's success matches to matches
        self.matched_dict.update(matches)
        to_remove = list()
        # Update market state based on matches
        for agent in self.Agents:
            if agent.name in matches.keys():
                self.welfare += agent.utilFct()
                self.matched.append(agent)
                to_remove.append(agent)
                continue
            if agent.is_critical and agent not in matches:
                self.perished.append(agent)
                to_remove.append(agent)
        for agent in to_remove:
            self.Agents.remove(agent)
        # update total Loss
        if self.time > 10:
            self.loss = len(self.perished)/self.total_agents

    def critical(self):
        """
        Returns:
            # of critical agents in market at current time
        """
        counter = 0
        for i in self.agents:
            if i.is_critical:
                counter += 1
        return counter
