"""
Runs tests on main classes
AgentTest, MarketTest, SimulationTest
"""
import matchingmarkets as mm
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
    new_type = mm.randomType(numTypes)
    newAgent = mm.Agent(name=len(AgentList),
                        discount_rate=new_discount,
                        time_to_critical=new_time_to_crit,
                        myType=new_type)
    AgentList.append(newAgent)

for agent in AgentList:
    print("\nname: ", agent.name)
    print("discount rate: ", agent.discount_rate)
    print("Type:  ", agent.type)
    print("time to crit: ", agent.time_to_critical)

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
    newMarket = mm.Market(arrival_rate=rng.randint(2**(i+1), 3**(i+1)),
                          average_prob=lambda: rng.random(),
                          max_agents=rng.randint(150)
                          )
    MarketList.append(newMarket)

for market in MarketList:
    print("\nOK\n+++++++")
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

print("\n\nSimulation Test\n")

sim = mm.simulation(time_per_run=5000, runs=10, logAllData=True)

print("Regular Run\n")

sim.run(arrival_rate=rng.randint(50),
        average_success_prob=lambda: rng.random(),
        discount=lambda: rng.random_sample(),
        typeGenerator=lambda x: rng.randint(x),
        numTypes=5
        )

sim.stats()

print("\n\nVerbose Run tests \n")

sim.time_per_run = 75

arrival_r = rng.randint(1, 5)
print("Arrival rate: ", arrival_r)

lossTest = sim.single_run(0, arrival_rate=arrival_r,
                          average_success_prob=lambda: rng.random(),
                          discount=lambda: rng.random_sample(),
                          typeGenerator=lambda x: rng.randint(x),
                          numTypes=5, verbose=True, objective=lambda x: x.loss
                          )
print("Objective: loss ", lossTest)

welfareTest = sim.single_run(0, arrival_rate=arrival_r,
                             average_success_prob=lambda: rng.random(),
                             discount=lambda: rng.random_sample(),
                             typeGenerator=lambda x: rng.randint(x),
                             numTypes=5, objective=lambda x: x.welfare,
                             verbose=True
                             )
print("Objective: welfare ", welfareTest)

matchTest = sim.single_run(0, arrival_rate=arrival_r,
                           average_success_prob=lambda: rng.random(),
                           discount=lambda: rng.random_sample(),
                           typeGenerator=lambda x: rng.randint(x),
                           numTypes=5, objective=lambda x: len(x.matched),
                           verbose=True
                           )
print("Objective: matches ", matchTest)

print("\n\nSolver Test\n")

arrival_r = rng.randint(1, 5)
print("Arrival rate: ", arrival_r)


welfareTest1 = sim.single_run([2], metaParamNames=["period"],
                              arrival_rate=arrival_r,
                              average_success_prob=lambda: 1,
                              discount=lambda: 1,
                              time_to_crit=lambda x: x, crit_input=5,
                              typeGenerator=mm.randomType,
                              numTypes=5, metaAlgorithm=mm.meta_periodic,
                              objective=lambda x: x.welfare
                              )

welfareTest2 = sim.single_run([2], metaParamNames=["period"],
                              arrival_rate=arrival_r,
                              average_success_prob=lambda: 1,
                              discount=lambda: 1,
                              time_to_crit=lambda x: x, crit_input=5,
                              typeGenerator=mm.randomType,
                              numTypes=5, metaAlgorithm=mm.meta_periodic,
                              objective=lambda x: x.welfare
                              )

welfareTest3 = sim.single_run([2], metaParamNames=["period"],
                              arrival_rate=arrival_r,
                              average_success_prob=lambda: 1,
                              discount=lambda: 1,
                              time_to_crit=lambda x: x, crit_input=5,
                              typeGenerator=mm.randomType,
                              numTypes=5, metaAlgorithm=mm.meta_periodic,
                              objective=lambda x: x.welfare
                              )

print("RunTest 1: ", welfareTest1)
print("RunTest 2: ", welfareTest2)
print("RunTest 3: ", welfareTest3)
print("Ok")

sim.time_per_run = 75

print("\nNon-Stochastic brute search")

res = sim.brute_search([(1, 10)], metaParamNames=["period"], arrival_rate=arrival_r,
                       average_success_prob=lambda: 1,
                       discount=lambda: 1,
                       time_to_crit=lambda x: x, crit_input=5,
                       typeGenerator=mm.alternatingType,
                       numTypes=5, metaAlgorithm=mm.meta_periodic,
                       objective=lambda x: x.welfare,
                       stochastic_objective=False
                       )
print("Results: ", res)
print("\nStochastic multivariate brute force search")
print("(this can take a while)")
res = sim.brute_search([slice(1, 6), slice(1, 6)],
                       metaParamNames=["agents", "num_critical"],
                       arrival_rate=arrival_r,
                       average_success_prob=lambda: 1,
                       stochastic_precision=3,
                       discount=rng.random_sample,
                       time_to_crit=lambda x: rng.randint(x),
                       crit_input=5,
                       typeGenerator=mm.randomType,
                       numTypes=5,
                       metaAlgorithm=mm.meta_agents_critical,
                       objective=lambda x: x.welfare,
                       stochastic_samples=10
                       )
print("Results: ", res)

#
# Market Plotting Test
#

print("\nPlotting Tests\n")

# Modify number of runs here
n = 4  # Markets
m = 20  # Periods per market

MarketList = list()

for i in range(n):
    newMarket = mm.Market(arrival_rate=rng.randint(2**(i+1), 3**(i+1)),
                          average_prob=lambda: rng.random(),
                          max_agents=rng.randint(1, 15000), plots=True,
                          plot_time=0.000001
                          )
    MarketList.append(newMarket)

for market in MarketList:
    print("\n+++++++")
    for i in range(m):
        market.update(discount=rng.random_sample,
                      typeGenerator=rng.randint,
                      neighborFct=mm.neighborSameType,
                      crit_input=5,
                      numTypes=5
                      )
    print("iteration done")

print("\nPlotting Tests complete")
print("============================")


print("Tests Passed")