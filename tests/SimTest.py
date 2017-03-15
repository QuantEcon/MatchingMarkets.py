import matchingmarkets as mm
import numpy.random as rng

#
# Simulation Test
#

print("\n\nSimulation Test\n")

sim = mm.simulation(time_per_run=50, runs=10, logAllData=True)

print("Regular Run\n")

sim.run(arrival_rate=rng.randint(50),
        average_success_prob=lambda: rng.random(),
        discount=lambda: rng.random_sample(),
        typeGenerator=lambda x: rng.randint(x),
        numTypes=5
        )

sim.stats()

print("\n\nSingle Run tests \n")

arrival_r = rng.randint(1, 5)
print("Arrival rate: ", arrival_r)

lossTest = sim.single_run(0, arrival_rate=arrival_r,
                          average_success_prob=lambda: rng.random(),
                          discount=lambda: rng.random_sample(),
                          typeGenerator=lambda x: rng.randint(x),
                          numTypes=5
                          )
print("Objective: loss ", lossTest)

welfareTest = sim.single_run(0, arrival_rate=arrival_r,
                             average_success_prob=lambda: rng.random(),
                             discount=lambda: rng.random_sample(),
                             typeGenerator=lambda x: rng.randint(x),
                             numTypes=5, objective=lambda x: x.welfare,
                             )
print("Objective: welfare ", welfareTest)

matchTest = sim.single_run(0, arrival_rate=arrival_r,
                           average_success_prob=lambda: rng.random(),
                           discount=lambda: rng.random_sample(),
                           typeGenerator=lambda x: rng.randint(x),
                           numTypes=5, objective=lambda x: len(x.matched),
                           )
print("Objective: matches ", matchTest)

print("\n\nSolver Test\n")

arrival_r = rng.randint(1, 5)
print("Arrival rate: ", arrival_r)


welfareTest1 = sim.single_run([2], metaParamNames=["period"], arrival_rate=arrival_r,
                              average_success_prob=lambda: 1,
                              discount=lambda: 1,
                              time_to_crit=lambda x: x, crit_input=5,
                              typeGenerator=mm.alternatingType,
                              numTypes=5, metaAlgorithm=mm.meta_periodic,
                              objective=lambda x: x.welfare
                              )

welfareTest2 = sim.single_run([2], metaParamNames=["period"], arrival_rate=arrival_r,
                              average_success_prob=lambda: 1,
                              discount=lambda: 1,
                              time_to_crit=lambda x: x, crit_input=5,
                              typeGenerator=mm.alternatingType,
                              numTypes=5, metaAlgorithm=mm.meta_periodic,
                              objective=lambda x: x.welfare
                              )

welfareTest3 = sim.single_run([2], metaParamNames=["period"], arrival_rate=arrival_r,
                              average_success_prob=lambda: 1,
                              discount=lambda: 1,
                              time_to_crit=lambda x: x, crit_input=5,
                              typeGenerator=mm.alternatingType,
                              numTypes=5, metaAlgorithm=mm.meta_periodic,
                              objective=lambda x: x.welfare
                              )

print("RunTest 1: ", welfareTest1)
print("RunTest 2: ", welfareTest2)
print("RunTest 3: ", welfareTest3)
print("Non-Stochastic brute search")

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
print("(this can take a few minutes)")
res = sim.brute_search([slice(1, 6), slice(1, 6)],
                       metaParamNames=["agents", "num_critical"],
                       arrival_rate=arrival_r,
                       average_success_prob=lambda: 1,
                       stochastic_precision=1,
                       discount=rng.random_sample,
                       time_to_crit=lambda x: rng.randint(x),
                       crit_input=5,
                       typeGenerator=mm.randomType,
                       numTypes=5,
                       metaAlgorithm=mm.meta_agents_critical,
                       objective=lambda x: x.welfare,
                       stochastic_samples=55
                       )
print("Results: ", res)
