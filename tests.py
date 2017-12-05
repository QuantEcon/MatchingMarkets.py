import matchingmarkets as mm
import numpy.random as rng

newsim = mm.simulation(time_per_run=100, max_agents=5000,
                       arrival_rate=15, average_success_prob=lambda: 0.3,
                       typeGenerator=rng.randint,
                       compatFct=mm.stochastic_neighborSameType,
                       crit_input=3, numTypes=5)

# Make sure matplotlib is __not__ inline for this
newsim.graph(plot_time=0.8)