import matchingmarkets as mm
import numpy.random as rng

#
# Market Plotting Test
#

print("\nPlotting Tests\n")

# Modify number of runs here
n = 1  # Markets
m = 10  # Periods per market

MarketList = list()

for i in range(n):
    newMarket = mm.Market(arrival_rate=15,
                          average_prob=lambda: 0.5,
                          max_agents=rng.randint(1, 15000), plots=True,
                          plot_time=0.5
                          )
    MarketList.append(newMarket)

for market in MarketList:
    print("\n+++++++")
    for i in range(m):
        market.update(discount=rng.random_sample,
                      typeGenerator=rng.randint,
                      neighborFct=mm.stochastic_neighborSameType,
                      crit_input=3, metaParams={'verbose': True},
                      numTypes=5, verbose=True
                      )
    print("iteration done")

print("\nPlotting Tests complete")
print("============================")
