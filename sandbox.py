import matchingmarkets as mm
import numpy.random as rng
import random
import numpy as np

quantity_stddev = 0.1
price_stddev = 0.03
num_currencies = 3

# tuple represents price in USD, median transaction size in unit of coin
currency_dict = {}
currency_dict[0] = (11000.0, 0.057) #BTC
currency_dict[1] = (460.0, 1.0) #ETH
currency_dict[2] = (1.0, 500) #USD

p_vals = [0.05, 0.8, 0.15] #BTC and ETH, BTC and USD, ETH and USD

p_dict = {}
counter = 0
for i in range(num_currencies):
    for j in range(num_currencies):
        if i != j:
            p_dict[counter] = (i, j)
            counter += 1

def typeGen(_numtypes):
    draw_from_dist = rng.multinomial(1, p_vals)
    draw_from_dist = draw_from_dist.tolist()
    pair_index = draw_from_dist.index(1)

    crypto1, crypto2 = p_dict[pair_index]

    direction = random.choice(["1_for_2", "2_for_1"])
    if direction == "1_for_2": # have 1, want 2
        have, want = crypto1, crypto2
    else:
        have, want = crypto2, crypto1

    price_per_unit = currency_dict[want][0] / currency_dict[have][0]
    median_quantity = currency_dict[have][1]
    desired_price = rng.normal(price_per_unit, price_per_unit * price_stddev)
    quantity_to_sell = rng.normal(median_quantity, median_quantity * quantity_stddev)
    return (have, quantity_to_sell, want, quantity_to_sell / desired_price)

for i in range(100):
    print(typeGen(1))

# newsim = mm.simulation(time_per_run=100, max_agents=5000,
#                        arrival_rate=15, success_prob=lambda: 0.3,
#                        typeGenerator=typeGen,
#                        compatFct=mm.stochastic_neighborSameType,
#                        crit_input=3, numTypes=5)
#
# # Make sure matplotlib is __not__ inline for this
# newsim.graph(plot_time=0.8)
