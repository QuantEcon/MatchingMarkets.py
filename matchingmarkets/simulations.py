import numpy as np

from matchingmarkets.agent import Agent
from matchingmarkets.metaalgorithms import *
from matchingmarkets.algorithms import *
from matchingmarkets.market import Market
from matchingmarkets.utilities import *


class simulation:
    def __init__(self, runs=50, time_per_run=1, max_agents=1000,
                 logAllData=False):
        """
        Initializes a simulation object
        NOTE: Most simulation details are
              passed in the run() method
        Arguments
        ---------
        runs: int
             number of trials when runs
        time_per_run: int
            number of time periods in a run
        max_agents: int
            maximum number of agents over a run overall
        logAllData: bool
            log every single period on every iteration
            Takes much longer, but outputs pretty graphs
            if false, only logs final results on each run
        """
        self.logAllData = logAllData
        self.runs = runs
        self.time_per_run = time_per_run
        self.max_agents = max_agents
        self.welfare = 0
        self.loss = 0
        self.matches = 0
        self.perished = 0
        self.max_welfare = 0
        self.min_welfare = 0
        self.welfare_var = 0
        self.max_loss = 0
        self.min_loss = 0
        self.loss_var = 0
        self.max_matches = 0
        self.min_matches = 0
        self.matches_var = 0
        self.max_perished = 0
        self.min_perished = 0
        self.perished_var = 0
        self.welfare_matrix = np.zeros((self.runs, self.time_per_run))
        self.matches_matrix = np.zeros((self.runs, self.time_per_run))
        self.loss_matrix = np.zeros((self.runs, self.time_per_run))
        self.perished_matrix = np.zeros((self.runs, self.time_per_run))

    def run(self, arrival_rate=50, metaAlgorithm=meta_Greedy,
            algorithm=arbitraryMatch, neighborFct=rngDraw,
            discount=lambda: 0, matchUtilFct=lambda x, y, z: 1,
            time_to_crit=lambda x: 0, crit_input=1,
            typeGenerator=lambda x: 1,
            numTypes=0, selfMatch=False,
            one_minus_average_fail_prob=lambda: 0.5):
        """
        Runs a simulation
        Default simulation is a one period market
        with 50 entrants on average, half compatible with each other
        utility is 1 for a match by default
        Arguments
        ---------
        arrival_rate: int
            average number of new agents per period
            the lambda in a poisson distribution
        algorithm: f(list[agent]) -> dict{agent.name : agent.name}
            Matching Algorithm
            takes current agents in market as input
            returns a list of matches
            see algorithms.py for details
        metaAlgorithm: f(market, algorithm)
                            -> dict{agent.name : agent.name}
            Algorithm responsible for timing decisions
            Decides when to match, and who participates
            in the matching algorithm
        neighborFct: fct(agent1, agent2, float) -> float
            rng function returning agents who are
            compatible matches based on input
            float parameter is a cutoff value for rng
        discount: fct() -> [0,1]
            rng function generating agent discount rate
        matchUtilFct: fct(agent1, agent2, float) -> float
            returns utility for agent1 of matching to agent2
        time_to_crit: fct(x) -> int
            function generating agent time to criticality
        crit_input: int
            input in above. Usually parameter in rng fct
        typeGenerator: fct(int) -> int
            function generating agent type
        numTypes: int
            input in typeGenerator
            usually # of types
        selfMatch: bool
            true if an agent can match himself
            ex: House market
            false if an agent has to match another
            ex: marriage market
        one_minus_average_fail_prob: f() -> float[0,1]
            cutoff value passed in neighborfct
            1 - pr(failure of match) for average of mrkt
        """
        # parallel this for loop
        for i in range(self.runs):
            newMarket = Market(arrival_rate=arrival_rate,
                               average_prob=one_minus_average_fail_prob,
                               max_agents=self.max_agents)
            for j in range(self.time_per_run):
                newMarket.update(metaAlgorithm=metaAlgorithm,
                                 algorithm=algorithm, neighborFct=neighborFct,
                                 discount=discount, matchUtilFct=matchUtilFct,
                                 time_to_crit=time_to_crit,
                                 crit_input=crit_input,
                                 typeGenerator=typeGenerator,
                                 numTypes=numTypes,
                                 selfMatch=selfMatch)
                if self.logAllData is True:
                    self.welfare_matrix[i, j] = newMarket.welfare
                    self.matches_matrix[i, j] = len(newMarket.matched)
                    self.loss_matrix[i, j] = newMarket.loss
                    self.perished_matrix[i, j] = len(newMarket.perished)
                j += 1
            if self.logAllData is False:
                self.welfare_matrix[i, -1:] = newMarket.welfare
                self.matches_matrix[i, -1:] = len(newMarket.matched)
                self.loss_matrix[i, -1:] = newMarket.loss
                self.perished_matrix[i, -1:] = len(newMarket.perished)
            i += 1
        # update simulation stats
        self.welfare = np.average(self.welfare_matrix[:, -1:])
        self.matches = np.average(self.matches_matrix[:, -1:])
        self.loss = np.average(self.loss_matrix[:, -1:])
        self.perished = np.average(self.perished_matrix[:, -1:])
        self.max_welfare = np.max(self.welfare_matrix[:, -1:])
        self.min_welfare = np.min(self.welfare_matrix[:, -1:])
        self.max_matches = np.max(self.matches_matrix[:, -1:])
        self.min_matches = np.min(self.matches_matrix[:, -1:])
        self.max_loss = np.max(self.loss_matrix[:, -1:])
        self.min_loss = np.min(self.loss_matrix[:, -1:])
        self.max_perished = np.max(self.perished_matrix[:, -1:])
        self.min_perished = np.min(self.perished_matrix[:, -1:])
        self.welfare_var = np.var(self.welfare_matrix[:, -1:])
        self.loss_var = np.var(self.loss_matrix[:, -1:])
        self.matches_var = np.var(self.matches_matrix[:, -1:])
        self.perished_var = np.var(self.perished_matrix[:, -1:])

    def stats(self):
        """
        Prints market statistics
        """
        print("Simulation Results")
        print(self.time_per_run, " periods")
        print(self.runs, " runs")
        print("Stat\t", " value\t", "(std dev)")
        print("==================================")
        print("Welfare:  ", self.welfare, "(",
              "%.4f" % np.sqrt(self.welfare_var), ")")
        print("matches:  ", self.matches, " (",
              "%.4f" % np.sqrt(self.matches_var), ")")
        print("perished: ", self.perished, " (",
              "%.4f" % np.sqrt(self.perished_var), ")")
        print("loss%:    ", "%.4f" % self.loss, " (",
              "%.4f" % np.sqrt(self.loss_var), ")")
