import matchingmarkets as mm
import numpy.random as rng

#
# Market Test
#
print("\nMarket Tests\n")
n = int(input('Enter # of markets: '))
m = int(input("Enter # of runs per market: "))

MarketList = list()

for i in range(n):
    newMarket = mm.Market(arrival_rate=rng.randint(1, 20),
                          average_prob=lambda: rng.random(),
                          max_agents=rng.randint(1, 150)
                          )
    MarketList.append(newMarket)

for market in MarketList:
    print("\n+++++++")
    for i in range(m):
        market.update(discount=rng.random_sample,
                      typeGenerator=rng.randint,
                      numTypes=5, verbose=True
                      )

print("\n\nMarket Tests complete")
print("============================")