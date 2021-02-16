"""
Runs tests on main classes
AgentTest, MarketTest, SimulationTest
"""
import matchingmarkets as mm
import numpy.random as rng
import unittest


class TestMarkets(unittest.TestCase):
    def test_agent(self):
        """
        Agent Tests
        """
        AgentList = list()
        numTypes = rng.randint(1, 25)
        for i in range(5):
            new_discount = rng.random_sample()
            new_time_to_crit = int(10*rng.random_sample())
            new_type = mm.randomType(numTypes)
            newAgent = mm.Agent(name=len(AgentList),
                                discount_rate=new_discount,
                                time_to_critical=new_time_to_crit,
                                myType=new_type)
            AgentList.append(newAgent)
        for agent in AgentList:
            self.assertGreaterEqual(agent.name, 0)
            self.assertGreaterEqual(agent.discount_rate, 0)
            self.assertGreaterEqual(agent.type, 0)
            self.assertGreaterEqual(agent.time_to_critical, 0)

    def test_markets(self):
        """
        Market Test
        """
        n = 5
        m = 50
        MarketList = list()
        for i in range(n):
            newMarket = mm.Market(arrival_rate=rng.randint(2**(i+1), 3**(i+1)),
                            success_prob=lambda: rng.random(),
                            max_agents=rng.randint(150)
                            )
            MarketList.append(newMarket)

        for market in MarketList:
            for i in range(m):
                market.update(discount=rng.random_sample,
                            typeGenerator=rng.randint,
                            numTypes=5, verbose=False
                            )

    def test_simulation(self):
        """
        Simulation Test
        """
        sim = mm.simulation(time_per_run=5000, runs=3, logAllData=True,
                        arrival_rate=rng.randint(50),
                        success_prob=lambda: rng.random(),
                        discount=lambda: rng.random_sample(),
                        typeGenerator=lambda x: rng.randint(x),
                        numTypes=5)
        sim.run()
        sim.stats()
        sim.time_per_run = 75
        arrival_r = rng.randint(1, 5)
        lossTest = sim.single_run(0, objective=lambda x: x.loss)
        welfareTest = sim.single_run(0, objective=lambda x: x.welfare)
        matchTest = sim.single_run(0, objective=lambda x: len(x.matched))
        arrival_r = rng.randint(1, 5)
        welfareTest1 = sim.single_run(
            [2], metaParamNames=["period"], objective=lambda x: x.welfare)
        welfareTest2 = sim.single_run(
            [2], metaParamNames=["period"], objective=lambda x: x.welfare)
        welfareTest3 = sim.single_run(
            [2], metaParamNames=["period"], objective=lambda x: x.welfare)
        sim.time_per_run = 5
        res = sim.brute_search(
            [(1, 3)], metaParamNames=["period"],
            objective=lambda x: x.welfare,
            stochastic_objective=False,
            stochastic_samples=5,
            stochastic_precision=1.,
        )

    def test_plotting(self):
        """
        Market Plotting Test
        """
        # Modify number of runs here
        n = 2  # Markets
        m = 3  # Periods per market
        MarketList = list()
        for i in range(n):
            newMarket = mm.Market(
                arrival_rate=rng.randint(2**(i+1), 3**(i+1)),
                success_prob=lambda: rng.random(),
                max_agents=rng.randint(1, 15000), plots=True,
                plot_time=0.000001
            )
            MarketList.append(newMarket)
        for market in MarketList:
            for i in range(m):
                market.update(
                    discount=rng.random_sample,
                    typeGenerator=rng.randint,
                    compatFct=mm.neighborSameType,
                    crit_input=5,
                    numTypes=5
                )

if __name__ == '__main__':
    unittest.main()