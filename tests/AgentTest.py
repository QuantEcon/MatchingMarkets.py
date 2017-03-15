import matchingmarkets as mm
import numpy.random as rng

#
# Agent Tests
#
print("\n\nAgent Tests\n")
n = input('Enter # of runs: ')

AgentList = list()
numTypes = rng.randint(25)

for i in range(n):
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