from matchingmarkets.agent import Agent
from matchingmarkets.market import Market
from matchingmarkets.simulations import simulation
from matchingmarkets.algorithms import *
from matchingmarkets.metaalgorithms import *
from matchingmarkets.generators.basic import *


def FullTest():
    """
    Runs tests on main classes
    AgentTest, MarketTest, SimulationTest
    """
    import numpy.random as rng

    #
    # Agent Tests
    #
    print("\n\nAgent Tests\n")

    AgentList = list()
    numTypes = rng.randint(1, 25)

    for i in range(5):
        new_discount = rng.random_sample()
        new_time_to_crit = int(10*rng.random_sample())
        new_type = randomType(numTypes)
        newAgent = Agent(name=len(AgentList),
                         discount_rate=new_discount,
                         time_to_critical=new_time_to_crit,
                         myType=new_type)
        AgentList.append(newAgent)

    print("\n\nAgent Tests complete")
    print("============================")

    #
    # Market Test
    #
    print("\nMarket Tests\n")
    n = 5
    m = 50

    MarketList = list()

    for i in range(n):
        newMarket = Market(arrival_rate=rng.randint(2**(i+1), 3**(i+1)),
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

    print("\n\nMarket Tests complete")
    print("============================")

    #
    # Simulation Test
    #

    print("\n\nSimulation Test\n5000 periods\n")

    sim = simulation(time_per_run=5000, runs=3, logAllData=True,
                     arrival_rate=rng.randint(50),
                     success_prob=lambda: rng.random(),
                     discount=lambda: rng.random_sample(),
                     typeGenerator=lambda x: rng.randint(x),
                     numTypes=5)

    print("Regular Run\n")

    sim.run()

    sim.stats()

    print("\n\nSingle Run tests \n")

    sim.time_per_run = 75

    arrival_r = rng.randint(1, 5)
    print("Arrival rate: ", arrival_r)

    lossTest = sim.single_run(0, objective=lambda x: x.loss)
    print("Objective: loss ", lossTest)

    welfareTest = sim.single_run(0, objective=lambda x: x.welfare)
    print("Objective: welfare ", welfareTest)

    matchTest = sim.single_run(0, objective=lambda x: len(x.matched))
    print("Objective: matches ", matchTest)

    print("\n\n\nBFS Test\n")

    arrival_r = rng.randint(1, 5)
    print("Arrival rate: ", arrival_r)

    welfareTest1 = sim.single_run([2], metaParamNames=["period"],
                                  objective=lambda x: x.welfare
                                  )

    welfareTest2 = sim.single_run([2], metaParamNames=["period"],
                                  objective=lambda x: x.welfare
                                  )

    welfareTest3 = sim.single_run([2], metaParamNames=["period"],
                                  objective=lambda x: x.welfare
                                  )

    print("RunTest 1: ", welfareTest1)
    print("RunTest 2: ", welfareTest2)
    print("RunTest 3: ", welfareTest3)
    print("Ok")

    sim.time_per_run = 75

    print("\n\n\nNon-Stochastic brute search")

    res = sim.brute_search([(1, 10)], metaParamNames=["period"],
                           objective=lambda x: x.welfare,
                           stochastic_objective=False
                           )
    print("Results: ", res)

    #
    # Market Plotting Test
    #

    print("\n\n\nPlotting Tests\n")
    print("\n---PLEASE VERIFY THAT GRAPHS ARE RENDERED ON YOUR SCREEN---\n")

    # Modify number of runs here
    n = 4  # Markets
    m = 20  # Periods per market

    MarketList = list()

    for i in range(n):
        newMarket = Market(arrival_rate=rng.randint(2**(i+1), 3**(i+1)),
                           success_prob=lambda: rng.random(),
                           max_agents=rng.randint(1, 15000), plots=True,
                           plot_time=0.000001
                           )
        MarketList.append(newMarket)

    for market in MarketList:
        print("\n+++++++")
        for i in range(m):
            market.update(discount=rng.random_sample,
                          typeGenerator=rng.randint,
                          compatFct=neighborSameType,
                          crit_input=5,
                          numTypes=5
                          )
        print("iteration done")

    print("\nPlotting Tests complete")
    print("============================")
    print("Pulp Test")

    pulp.pulpTestAll()

    print("\nNote: Only installed solvers can pass in PuLP test")

    print("+++++++++++++++++++++++")

    print("Please verify that graphs were plotted to a QT window")
    print("Tests Passed")
