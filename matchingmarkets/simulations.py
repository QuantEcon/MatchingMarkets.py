import numpy as np
from numpy.random import random
from scipy.stats import poisson
from scipy import optimize


from matchingmarkets.agent import Agent
from matchingmarkets.metaalgorithms import *
from matchingmarkets.algorithms import *
from matchingmarkets.market import Market
from matchingmarkets.generators.basic import *


class simulation:
    def __init__(self, runs=10, time_per_run=1, max_agents=1000,
                 verbose=False,
                 logAllData=False,
                 arrival_rate=7,
                 metaAlgorithm=meta_always,
                 algorithm=arbitraryMatch,
                 compatFct=std_compat,
                 discount=lambda: 1,
                 matchUtilFct=lambda x, y, **kwarg: 1,
                 time_to_crit=lambda x: poisson.rvs(x),
                 crit_input=0,
                 typeGenerator=lambda x: 1,
                 typeGen2=lambda x: 1,
                 algoParams=dict(),
                 numTypes=1, selfMatch=False,
                 success_prob=lambda: 1 if random() > 0.5 else 0,
                 arrival_fct=lambda x: poisson.rvs(x)):
        """
        Initializes a simulation object

        MonteCarlo simulation parameters
        --------------------
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
        verbose: bool
            if true, prints output internal details at every iteration

        Market Simulation Arguments
        --------------------------
        arrival_rate: int
            average number of new agents per period
            the lambda in a poisson distribution
        success_prob: f() -> float[0,1]
            cutoff value passed in compatFct
            1 - pr(failure of match) for average of mrkt
        algorithm: f(list<agent>) -> dict{agent.name : agent.name}
            Matching Algorithm
            takes current agents in market as input
            returns a list of matches
            see algorithms.py for details
        arrival_fct: fct(float) -> int
            function that returns number of arrival this period
            poisson distribution draw by default
        crit_input:int
            input in time_to_crit, usually param in a rng fct
        discount: fct() -> [0,1]
            function generating agent discount rate
        matchUtilFct: fct(agent1, agent2, float) -> float
            returns utility for agent1 of matching to agent2
        metaAlgorithm: f(market, algorithm, **kwargs)
                            -> dict{agent.name : agent.name}
            Algorithm responsible for timing decisions
            Decides when to match, and who participates
            in the matching algorithm
        algoParams: dict{string: value}
            kwargs passed into the metaAlgorithm
            This can then be passed into the Algorithm
        compatFct: fct(agent1, agent2, float) -> float
            rng function returning agents who are
            compatible matches based on input
            float parameter is a cutoff value for rng
        numTypes: int
            input in typeGenerator
            usually # of types
        utilityFctInput: float
            input for matchUtilFct (usually rng cutoff value)
        selfMatch: bool
            true if an agent can match himself
            ex: House market
            false if an agent has to match another
            ex: marriage market
        time_to_crit: fct() -> int
            function generating agent time to crit
        typeGenerator: fct(int) -> int
            function generating agent type
        """
        # Montecarlo information
        self.logAllData = logAllData
        self.runs = runs
        self.time_per_run = time_per_run
        self.verbose = verbose

        # Simulation parameters
        self.max_agents = max_agents
        self.arrival_rate = arrival_rate
        self.success_prob = success_prob
        self.metaAlgorithm = metaAlgorithm
        self.algorithm = algorithm
        self.compatFct = compatFct
        self.discount = discount
        self.matchUtilFct = matchUtilFct
        self.time_to_crit = time_to_crit
        self.crit_input = crit_input
        self.algoParams = algoParams
        self.typeGenerator = typeGenerator
        self.typeGen2 = typeGen2
        self.numTypes = numTypes
        self.selfMatch = selfMatch
        self.arrival_fct = arrival_fct

        # Collected stats on a run
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

    def run(self):
        """
        Runs a simulation
        Default simulation is a one period market
        with 50 entrants on average, half compatible with each other
        utility is 1 for a match by default
        Arguments
        ---------
        (void)
        runs based on simulation object attributes
        Returns
        -----------
        Nothing. Writes to attributes of the simulation object.
                 Note that using run() multiple times, the
                 simulation object will only store the results of
                 the latest one.
        """
        # parallelize this for loop
        for i in range(self.runs):
            newMarket = Market(arrival_rate=self.arrival_rate,
                               success_prob=self.success_prob,
                               selfMatch=self.selfMatch,
                               max_agents=self.max_agents)
            for j in range(self.time_per_run):
                newMarket.update(metaAlgorithm=self.metaAlgorithm,
                                 algorithm=self.algorithm,
                                 compatFct=self.compatFct,
                                 discount=self.discount,
                                 matchUtilFct=self.matchUtilFct,
                                 time_to_crit=self.time_to_crit,
                                 crit_input=self.crit_input,
                                 algoParams=self.algoParams,
                                 typeGenerator=self.typeGenerator,
                                 typeGen2=self.typeGen2,
                                 numTypes=self.numTypes,
                                 arrival_fct=self.arrival_fct,
                                 verbose=self.verbose)
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

    def graph(self, period=None, plot_time=0.35):
        """
        Plots the interactive graph of a run with qt5agg
        NOTE: rendering engine has problem on markets where
              more than 500 agents are present at the same time
        graphing Arguments
        ---------------
        plot_time: float
            time a frame stays on screen
        period: int
            number of periods to run the graph for
            default is the attribute of the simulation object
        """
        newMarket = Market(arrival_rate=self.arrival_rate,
                           success_prob=self.success_prob,
                           max_agents=self.max_agents,
                           graph=True, plots=True,
                           selfMatch=self.selfMatch,
                           plot_time=plot_time)
        if period is None:
            run_time = self.time_per_run
        else:
            run_time = period
        for j in range(run_time):
                newMarket.update(metaAlgorithm=self.metaAlgorithm,
                                 algorithm=self.algorithm,
                                 compatFct=self.compatFct,
                                 discount=self.discount,
                                 matchUtilFct=self.matchUtilFct,
                                 time_to_crit=self.time_to_crit,
                                 crit_input=self.crit_input,
                                 algoParams=self.algoParams,
                                 typeGenerator=self.typeGenerator,
                                 typeGen2=self.typeGen2,
                                 numTypes=self.numTypes,
                                 verbose=self.verbose,
                                 arrival_fct=self.arrival_fct)

    def single_run(self, weights, metaParamNames=list(),
                   objective=lambda x: x.matches):
        """
        Performs one simulation run
        Non-stochastic default parameters
        returns one parameter from created market as specified by "objective"
            default is market.loss

        Doesn't take algoParams dict for meta algorithm kwargs
            instead takes weights array and metaParamNames list of strings
            which combined creates dict

        Arguments
        ------------
        metaParamNames: list<string>
            names of kwargs passed
        weights: values
            values attached to metaParamNames
            Weights and metaparamNames together would form the
            algoParams dict in a normal simulation
        objective: function(Market) -> float
            objective function
            by default number of matches
            can be changed to loss, for example, by
                "objective=lambda x: x.loss"
        Returns
        -----------
        Objective function after specified number of runs
        So for welfare it would return market welfare after one run
        """
        # Create new meta-algorithm kwargs dict
        params = dict()
        # this refactors weights input
        if type(weights) == np.ndarray:
            if weights.shape == ():
                weights = [weights]
        for i in range(len(metaParamNames)):
            params[metaParamNames[i]] = weights[i]
        # Create new Market for simulation
        newMarket = Market(arrival_rate=self.arrival_rate,
                           success_prob=self.success_prob,
                           selfMatch=self.selfMatch,
                           max_agents=self.max_agents)
        # Run simulation
        for i in range(self.time_per_run):
                newMarket.update(metaAlgorithm=self.metaAlgorithm,
                                 algorithm=self.algorithm,
                                 compatFct=self.compatFct,
                                 discount=self.discount,
                                 matchUtilFct=self.matchUtilFct,
                                 time_to_crit=self.time_to_crit,
                                 crit_input=self.crit_input,
                                 algoParams=self.algoParams,
                                 typeGenerator=self.typeGenerator,
                                 typeGen2=self.typeGen2,
                                 numTypes=self.numTypes,
                                 arrival_fct=self.arrival_fct,
                                 verbose=self.verbose)
        return objective(newMarket)

    def brute_search(self, weights, metaParamNames=list(),
                     objective=lambda x: x.loss,
                     negative_objective=False,
                     stochastic_objective=True,
                     stochastic_samples=25,
                     stochastic_precision=0.01,
                     ):
        """
        Uses BFS to find optimal simulation hyperparameters
        Note:
            You want runs passed in the solver to have __no randomness__
            Solving a stochastic simulation will cause problems with solver

        Arguments
        ---------
        Weights: list<floats>
                 weights to be optimized on
        metaParamName: list<string>
                 list of names of arguments to be optimized on
                 the index respects the weights argument above
                 the strings should be the same as in a simulation run input
                 Weights and metaparamNames together would form the
                 algoParams dict in a normal simulation
        objective: function(Market) -> float
            objective function
            by default number of matches
            can be changed to loss, for example, by
                "objective=lambda x: x.loss"
        returns
        -------
        np.array of weights where function is minimized
                if negative_objective=True, where maximized
        """
        def this_run(w):
            # note - sign here
            # TODO fix negative sign
            sign = 1 if negative_objective else -1
            if stochastic_objective:
                result = 0
                # If objective stochastic, make montecarlo draws & average
                for i in range(stochastic_samples):
                    result += sign * \
                            self.single_run(w,
                                            metaParamNames=metaParamNames,
                                            objective=objective)
                # Average montecarlo draws
                result = result/stochastic_samples
                # Tune precision for convergence
                result = int(result/stochastic_precision)*stochastic_precision
                return result
            else:
                return sign*self.single_run(w,
                                            metaParamNames=metaParamNames,
                                            objective=objective)
        # res = []
        # for i in range(10):
        #    res.append(this_run(weights))
        res = optimize.brute(this_run, weights, full_output=True, disp=True,
                             finish=optimize.fmin
                             )
        return res[0]
