from scipy.stats import poisson
import numpy as np
import networkx as nx

from matchingmarkets.agent import Agent
from matchingmarkets.metaalgorithms import meta_always
from matchingmarkets.generators.basic import *
from matchingmarkets.algorithms.basic import *

import matplotlib
try:
    matplotlib.use('qt5agg')
    CANT_PLOT = False
except ImportError as ie:
    CANT_PLOT = True
    print(f"Can't import plotting backend: \n {ie}")
import matplotlib.pyplot as plt
import matplotlib.cm as cm


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
        0 < a_rate in discrete time
    success_prob: float
        average fraction of neighbors to an agent
        conditional on agents' types matching
    Matched: list
        container of matched agents
    max_agents: int
        maximum number of agents in market overtime
    Perished: list
        container of permanently perished agents
    time: int
        # of periods since market start
    Welfare: float
        cumul sum of utility of succesful matches
    total_agents: int
        total distinct agents who ever entered market
    """
    def __init__(self, arrival_rate=1, success_prob=lambda: 1,
                 max_agents=1000, graph=True, plots=False,
                 plot_time=0.5, selfMatch=False,):
        """
        Generate new market object
        Arguments
        -----------
        arrival_rate: int or f()->int
            rate of arrival in the Market
            parameter passed in a statistical distribution when advancing time
        success_prob: int or f()->int
            probability of match success
            parameter passed in a match probability function
        max_agents: int
            maximum number of agents over all periods in Market
        graph: bool
            store network of potential matches in a NetworkX DiGraph object
            necessary for graph plotting
        plots: bool
            output network graph plots 3 times per update
        plot_time: float
            time per frame on plot
        graph: bool
            if True, market maintains a networkX DiGraph object
            nodes are agents, directed edges are compatibility
            edge weight is expected match utility
                so match utility * match success probability
        max
        """
        self.Agents = list()
        self.arrival_rate = arrival_rate
        self.acceptable_prob = success_prob
        self.max_agents = max_agents
        self.perished = list()
        self.matched = list()
        self.matched_dict = dict()
        self.time = 0
        self.welfare = 0
        self.total_agents = 0
        self.loss = 0
        self.has_graph = graph
        self.plots_on = plots
        self.selfMatch = selfMatch
        if self.has_graph:
            if self.selfMatch:
                self.Graph = nx.MultiDiGraph()
            else:
                self.Graph = nx.DiGraph()
        if self.plots_on:
            if CANT_PLOT:
                print("WARNING: Cant plot dur to qt5agg backend import error")
                self.plots_on = False
            plt.ion()  # Interactive plotting
            self.has_graph = True
            self.Graph = nx.DiGraph()
            self.graph_labels = dict()
            self.color_map = dict()
            self.graph_colors = list()
            self.plot_time = plot_time
            self.graph_pos = dict()




    #TODO implement initial agents in market here
    #   def initial_agents(Agents)






    def update(self, metaAlgorithm=meta_always, algorithm=arbitraryMatch,
               compatFct=std_compat, discount=lambda: 1, algoParams=dict(),
               matchUtilFct=lambda x, y, **kwarg: 1, utilityFctInput=1,
               time_to_crit=lambda x: poisson.rvs(x), crit_input=0,
               typeGenerator=lambda x: 1, typeGen2=lambda x: 1, numTypes=1,
               verbose=False, arrival_fct=lambda x: poisson.rvs(x)
               ):
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
        verbose: bool
            print on relevant actions in update
        """
        # If verbose, welcome message
        if verbose:
            print("\n\n--------------------Verbose Update--------------------")
            print("Time: ", self.time, " Total Agents: ", self.total_agents,
                  " Max: ", self.max_agents)
            print("Current Pool ", [a.name for a in self.Agents])
        #
        # Plot state coming in
        #
        if self.plots_on:
            # Fill color dict
            if self.time == 0:
                # Draw from type generator to fill type names
                # Only way to ensure we get proper type names
                # Since they can be arbitrarily user defined
                type_names = set()
                for i in range(10000):
                    type_names.add(typeGenerator(numTypes))
                colors = iter(cm.rainbow(np.linspace(0, 1, len(type_names))))
                for i in type_names:
                    self.color_map[i] = next(colors)
            if self.time != 0:
                # clear figure to update instead of producing new & draw
                plt.clf()
                for a in self.graph_labels:
                    self.graph_labels[a] = \
                            a.time_to_critical - a.sojourn - 1
                # Make colors for nodes
                new_colors = [self.color_map.get(node.type, 0.45)
                              for node in self.Graph.nodes()]
                # Draw
                nx.draw_networkx(self.Graph, pos=self.graph_pos,
                                 font_size=7.5, font_weight='bold',
                                 labels=self.graph_labels, arrows=False,
                                 node_color=new_colors,
                                 node_size=200)
                plt.axis('off')
                plt.plot()
                plt.title("Period " + str(self.time) + " end     "
                          "\nMatches " + str(len(self.matched)) +
                          " || Perished " + str(len(self.perished)) +
                          " || Loss% " + "%.3f" % (100*self.loss)
                          )
                plt.show()
                plt.pause(self.plot_time)
        #
        # Check if market full, if not get new arrivals
        #
        if self.total_agents < self.max_agents:
            new_agents = arrival_fct(self.arrival_rate)
            if verbose:
                print("New Agents: ", new_agents)
            # Create new agents to market
            for i in range(new_agents):
                new_discount = discount()
                new_time_to_crit = time_to_crit(crit_input)
                new_type = typeGenerator(numTypes)
                new_type2 = typeGen2(numTypes)
                newAgent = Agent(name=self.total_agents,
                                 discount_rate=new_discount,
                                 time_to_critical=new_time_to_crit,
                                 myType=new_type, myType2=new_type2)
                self.Agents.append(newAgent)
                # Update DiGraph with new nodes
                if self.has_graph:
                    self.Graph.add_node(newAgent)
                    if self.plots_on:
                        self.graph_labels[newAgent] = \
                             newAgent.time_to_critical - newAgent.sojourn
                self.total_agents += 1
            if verbose:
                print("\nAdding new agents to existings' preference maps")
            # Add new agents to existings' preference maps
            for oldAgent in self.Agents[:-new_agents]:
                for newAgent in self.Agents[-new_agents:]:
                    oldAgent.addNewToMap(
                                newAgent,
                                utilityResult=matchUtilFct(oldAgent,
                                                           newAgent,
                                                           cutoff=utilityFctInput),
                                failProbResult=compatFct(oldAgent,
                                                         newAgent,
                                                         cutoff=self.acceptable_prob()
                                                         )
                                         )
                    # Add new edge to nx Graph
                    if self.has_graph:
                        if oldAgent.match_fail_prob[newAgent.name] > 0:
                            self.Graph.add_edge(
                                    oldAgent, newAgent,
                                    weight=oldAgent.match_fail_prob[newAgent.name] *
                                    oldAgent.match_util[newAgent.name])
                if verbose:
                    print("\nAgent ", oldAgent.name, "( type", oldAgent.type,
                          ") Life left",
                          oldAgent.time_to_critical - oldAgent.sojourn,
                          "-------------------------\n\tMatch Util ",
                          oldAgent.match_util, "\n\tMatch Fail Prob ",
                          oldAgent.match_fail_prob)
            if verbose:
                print("\nFilling preference maps of new agents")
            # Fill preference maps of new agents
            for newAgent in self.Agents[-new_agents:]:
                for otherAgent in [x for i, x
                                   in enumerate(self.Agents) if i != newAgent]:
                        newAgent.addNewToMap(
                                    otherAgent,
                                    utilityResult=matchUtilFct(newAgent,
                                                               otherAgent,
                                                               cutoff=utilityFctInput
                                                               ),
                                    failProbResult=compatFct(
                                                        newAgent,
                                                        otherAgent,
                                                        cutoff=self.acceptable_prob()
                                                            )
                                             )
                        # If self matches not allowed, clean maps
                        if self.selfMatch is not True:
                            newAgent.match_util[newAgent.name] = 0
                            newAgent.match_fail_prob[newAgent.name] = 0
                        # Add new edge to nx Graph
                        if self.has_graph:
                            if newAgent.match_fail_prob[otherAgent.name] > 0:
                                self.Graph.add_edge(
                                    newAgent, otherAgent,
                                    weight=newAgent.match_fail_prob[otherAgent.name] *
                                    newAgent.match_util[otherAgent.name]
                                                    )
                if verbose:
                    print("\nAgent ", newAgent.name, " ( type", newAgent.type,
                          ") Life Left:",
                          newAgent.time_to_critical - newAgent.sojourn,
                          "-------------------------\n\tMatch Util ",
                          newAgent.match_util, "\n\tMatch success Prob ",
                          newAgent.match_fail_prob)
        #
        # update time on agents
        #
        self.time += 1
        for agent in self.Agents:
            agent.update()

        #
        # plot new arrivals
        #
        if self.plots_on:
            plt.clf()
            plt.axis('off')
            self.graph_pos = nx.spring_layout(self.Graph,
                                              k=(1/(0.9*np.sqrt(len(
                                                      self.Graph.nodes()
                                                      ))))
                                              )
            for a in self.graph_labels:
                self.graph_labels[a] = \
                        a.time_to_critical - a.sojourn
            # Make colors for nodes
            new_colors = [self.color_map.get(node.type, 0.45)
                          for node in self.Graph.nodes()]
            # Draw
            nx.draw_networkx(self.Graph, pos=self.graph_pos, arrows=False,
                             labels=self.graph_labels, font_size=7.5,
                             font_weight='bold',
                             node_color=new_colors,
                             node_size=200)
            plt.plot()
            plt.title("Period " + str(self.time) + " arrivals"
                      "\nMatches " + str(len(self.matched)) +
                      " || Perished " + str(len(self.perished)) +
                      " || Loss% " + "%.3f" % (100*self.loss)
                      )
            plt.show()
            plt.pause(self.plot_time)

        #
        # perform Matching
        #
        if verbose:
            print("\nPerforming matches ")
            print("Current Pool ", [a.name for a in self.Agents])
            print("algoParams: ", algoParams)
        #
        # Call metaAlgorithm(algorithm) with optional parameters
        #
        matches = metaAlgorithm(self, match=algorithm,
                                verbose=verbose, **algoParams)

        if verbose:
            print("\nMatches: ", matches)

        self.matched_dict.update(matches)

        #
        # color matched edges and plot before deleting
        #
        if self.plots_on:
            edge_colors = []
            edge_list = []
            for e in self.Graph.edges():
                if e[0].name in matches.keys() and \
                   matches[e[0].name] == e[1].name:
                    edge_colors.append((1, 0.3, 0.3))
                    edge_list.append(e)
            for a in self.graph_labels:
                self.graph_labels[a] = \
                        a.time_to_critical - a.sojourn
            # Make colors for nodes
            new_colors = [self.color_map.get(node.type, 0.45)
                          for node in self.Graph.nodes()]
            # Draw
            nx.draw_networkx_edges(self.Graph, self.graph_pos,
                                   edgelist=edge_list, font_size=7.5,
                                   labels=self.graph_labels,
                                   font_weight='bold', width=2,
                                   node_color=new_colors,
                                   edge_color=edge_colors, node_size=200)
            plt.axis('off')
            plt.plot()
            plt.title("Period " + str(self.time) + " matches"
                      "\nMatches " + str(len(self.matched)) +
                      " || Perished " + str(len(self.perished)) +
                      " || Loss% " + "%.3f" % (100*self.loss)
                      )
            plt.show()
            plt.pause(self.plot_time)

        to_remove = list()

        #
        # Update market's success matches to matches
        #
        self.matched_dict.update(matches)
        if verbose:
            print("\nMatched dict ", self.matched_dict)
        to_remove = list()

        #
        # Update market state based on matches
        #
        for agent in self.Agents:
            if agent.name in matches.keys():
                before = self.welfare
                self.welfare += agent.utilFct(t=agent.sojourn,
                                              matchUtility=agent.match_util[
                                                  matches[agent.name]]
                                              )
                if verbose:
                    print("\nUtility ", agent.name, " ", self.welfare-before, " sojourn ", agent.sojourn)

                # TODO Add fct param of utilFct in update() and into simulation parameters


                self.matched.append(agent)
                to_remove.append(agent)
                continue
            # Fill list of agents to remove
            if agent.is_critical and agent not in matches:
                self.perished.append(agent)
                to_remove.append(agent)
        #
        # Remove matched and perished agents
        #
        for agent in to_remove:
            if self.has_graph:
                self.Graph.remove_node(agent)
                if self.plots_on:
                    if agent in self.graph_labels:
                        del self.graph_labels[agent]
            self.Agents.remove(agent)
        if verbose:
            print("Perished: ")
        perishedList = [agent.name for agent in self.perished]
        if verbose:
            print(perishedList)
            print("Matched: ")
        matchedList = [agent.name for agent in self.matched]
        if verbose:
            print(matchedList)
            print("Surviving: ")
            print([a.name for a in self.Agents])
        #
        # update total Loss
        #
        if self.time > 5:
            if self.total_agents == 0:
                self.loss = 0
            else:
                self.loss = len(self.perished)/self.total_agents
            if verbose:
                print("Loss ", self.loss)

    def critical(self):
        """
        Returns:
            # of critical agents in market at current time
        """
        counter = 0
        for i in self.Agents:
            if i.is_critical:
                counter += 1
        return counter
