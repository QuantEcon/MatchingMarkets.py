# matchingmarkets
Python toolbox for simulation of matching markets in economics.

`matchingmarkets` aims to be:

- Easy to use 
- Easy to extend
- Flexible to many types of markets
- Expressive

You can use the toolbox to produce simulations of fairly general matching markets. The markets can last one period, or can evolve over many time periods. Here is an example of a graph produced with the package of a market evolving over many periods:

![alt tag](https://raw.githubusercontent.com/VHRanger/matchingmarkets/master/matching%20graph%20example.gif)
    
In this plot, nodes are people, and color is their "type" (think blood type in organ transplants). Number on a node is periods of life left before death if not matched. An edge means they are compatible (it can be weighed if there's risk of failure). Edges get highlighted red before matches. In this simulation, only people of the same type can be compatible, and we naively match two compatible individuals at random. Our timing decision rule here is to naively try to match everyone each period.

This can be produced with this code:

    import matchingmarkets as mm
    import numpy.random as rng

    newsim = mm.simulation(time_per_run=100, max_agents=1000)
    
    # Make sure matplotlib is __not__ inline for this
    newsim.graph(arrival_rate=15, average_success_prob=lambda: 0.3,
                 typeGenerator=rng.randint,
                 neighborFct=mm.stochastic_neighborSameType,
                 crit_input=3, numTypes=5, plot_time=0.8)


# Use
----------------------------------------------------------------------
Please refer to the [tutorial notebook](https://github.com/VHRanger/matchingmarkets/blob/master/matchingmarkets%20package%20tutorial.ipynb) for more in depth instructions.

Download the package, change directory to the one containing it in your python console, and `import matchingmarkets as mm`.

Intended use is through the `simulation` object, as follows:

    newsim = mm.simulation(
                          # Simulation parameters here
                          )
    newsim.run(
               # Market parameters here
               )
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

      **runs:** int
            number of trials when runs

      **time_per_run:** int
          number of time periods in a run

      **max_agents:** int
              maximum number of agents over a run overall

      **logAllData:** bool
              log every single period on every iteration
              Takes much longer, but outputs pretty graphs
              if false, only logs final results on each run


When running a simulation, you can pass the following arguments to the **run function**:


            arrival_rate: int
                average number of new agents per period
                the lambda in a poisson distribution
                
            average_success_prob: f() -> float[0,1]
                cutoff value passed in neighborfct
                1 - pr(failure of match) for average of mrkt
                
            algorithm: f(list<agent>) -> dict{agent.name : agent.name}
                Matching Algorithm
                takes current agents in market as input
                returns a list of matches
                see algorithms.py for details
                
            arrival_fct: fct(float) -> int
                function that returns number of arrival this period
                poisson distribution draw by default
                
            crit_input:int
                input in time_to_crit, usually param in a rng fct
                
            discount: fct() -> [0,1]
                function generating agent discount rate
                
            matchUtilFct: fct(agent1, agent2, float) -> float
                returns utility for agent1 of matching to agent2
                
            metaAlgorithm: f(market, algorithm, **kwargs)
                                -> dict{agent.name : agent.name}
                Algorithm responsible for timing decisions
                Decides when to match, and who participates
                in the matching algorithm
                
            metaParams: dict{string: value}
                kwargs passed into the metaAlgorithm
                This can then be passed into the Algorithm
                
            neighborFct: fct(agent1, agent2, float) -> float
                rng function returning agents who are
                compatible matches based on input
                float parameter is a cutoff value for rng
                
            numTypes: int
                input in typeGenerator
                usually # of types

            utilityFctInput: float
                input for matchUtilFct (usually rng cutoff value)
                
            selfMatch: bool
                true if an agent can match himself
                ex: House market
                false if an agent has to match another
                ex: marriage market
                
            time_to_crit: fct() -> int
                function generating agent time to crit
                
            typeGenerator: fct(int) -> int
                function generating agent type
                
            verbose: bool
                print on relevant actions in update
