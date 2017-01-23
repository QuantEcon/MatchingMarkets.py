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
When creating the simulation class, you can pass the following parameters:

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
