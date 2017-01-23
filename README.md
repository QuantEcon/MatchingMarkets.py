# matchingmarkets
Python toolbox for simulation of matching markets in economics. Markets can be single period or dynamic. The simulation toolbox is built to be flexible to user-defined algorithms

#Use
----------------------------------------------------------------------
Download the package, change directory to the one containing it in your python console, and `import matchingmarkets as mm`.

Intended use is through the `simulation` object, as follows:

    newsim = mm.simulation()
    newsim.run()
    newsim.stats()
    
    Simulation Results
    1  periods
    50  runs
    Stat      value  (std dev)
    ==================================
    Welfare:   50.04 ( 6.7675 )
    matches:   50.04  ( 6.7675 )
    perished:  0.0  ( 0.0000 )
    loss%:     0.0000  ( 0.0000 )
   
The simulation class has many attributes to simulate static (single period) or dynamic (multi-period) matching markets. 
When creating the **simulation** class, you can pass the following parameters:

>       runs: int
>             number of trials when runs
>       time_per_run: int
>           number of time periods in a run
>       max_agents: int
>           maximum number of agents over a run overall
>       logAllData: bool
>           log every single period on every iteration
>           Takes much longer, but outputs pretty graphs
>           if false, only logs final results on each run

When running a simulation, you can pass the following arguments to the **run function**:

>       arrival_rate: int
>           average number of new agents per period
>           the lambda in a poisson distribution
>       algorithm: f(list[agent]) -> dict{agent.name : agent.name}
>           Matching Algorithm
>           takes current agents in market as input
>           returns a list of matches
>           see algorithms.py for details
>       metaAlgorithm: f(market, algorithm)
>                           -> dict{agent.name : agent.name}
>           Algorithm responsible for timing decisions
>           Decides when to match, and who participates
>           in the matching algorithm
>       neighborFct: fct(agent1, agent2, float) -> float
>           rng function returning agents who are
>           compatible matches based on input
>           float parameter is a cutoff value for rng
>       discount: fct() -> [0,1]
>           rng function generating agent discount rate
>       matchUtilFct: fct(agent1, agent2, float) -> float
>           returns utility for agent1 of matching to agent2
>       time_to_crit: fct(x) -> int
>           function generating agent time to criticality
>       crit_input: int
>           input in above. Usually parameter in rng fct
>       typeGenerator: fct(int) -> int
>           function generating agent type
>       numTypes: int
>           input in typeGenerator
>           usually # of types
>       selfMatch: bool
>           true if an agent can match himself
>           ex: House market
>           false if an agent has to match another
>           ex: marriage market
>       one_minus_average_fail_prob: f() -> float[0,1]
>           cutoff value passed in neighborfct
>           1 - pr(failure of match) for average of mrkt

The defaults are for a one period market where **insert details**

-----------------------------------------------------------------------
#Tutorial

Let's replicate the dynamic market studied in [Akbarpour et al. 2016](https://arxiv.org/abs/1402.3643). The market is multi-period, and implements arbitrary matches according to various matching meta-algorithms (algorithms that decide on time of matching, but not the method of matching). Agents go critical according to draws from a poisson distribution, `time_to_crit=poisson.rvs` with a lambda of 10. Here, to add frictions, we made agents only get utility or be compatible with each other if they are the same type from the `matchUtilFct=mm.utilSameType, neighborFct=mm.neighborSameType` input parameters. Types are drawn at random from one to 5 with `typeGenerator=mm.randomType, numTypes=5`. We test the greedy meta-algorithm with `metaAlgorithm=mm.meta_Greedy`.

    sim = simulation(runs=5, time_per_run=3500, max_agents=5000)
    sim.run(arrival_rate=3, time_to_crit=poisson.rvs, crit_input=10, algorithm=mm.arbitraryMatch, 
            metaAlgorithm=mm.meta_Greedy, matchUtilFct=mm.utilSameType, neighborFct=mm.neighborSameType,
            typeGenerator=mm.randomType, numTypes=5)
    sim.stats()
    
    Simulation Results
    3500  periods
    5  runs
    Stat	  value	 (std dev)
    ==================================
    Welfare:   4977.0 ( 6.8411 )
    matches:   4977.0  ( 6.8411 )
    perished:  23.6  ( 7.2277 )
    loss%:     0.0047  ( 0.0014 )
