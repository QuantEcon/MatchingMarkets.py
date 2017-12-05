import matchingmarkets as mm
import numpy.random as rng
import random
import numpy as np
import copy
from collections import defaultdict
import sys

# --------------------------------------------------
# Project: Crypto Network Fee Reduction Through TTC
# --------------------------------------------------

# ----------------------------------------------------------------------------------------
# SECTION I: General Agent Generation Mechanism (Called by both TTC and Workbook Settling)

quantity_stddev = 0.1
price_stddev = 0.03
num_currencies = 3

# tuple represents price in USD, median transaction size in unit of coin
# vary second parameter in order to experiment with different trade sizes
currencies = [
    (1.0, 500), #USD
    (11000.0, 500.0/11000.), #BTC
    (460.0, 500.0/460.0), #ETH
    (3000, 0.25), #random middle-price currency
    (100, 5), #low price
    (10, 100) #even lower price
]

# populate dictionary for currencies
currency_dict = {}
for i, currency in enumerate(currencies):
    currency_dict[i] = currency

# this will just have to be manually adjusted - only works for num_currnecies <= 3
# can randomize or something maybe. perhaps in the future, we have a relatively uniform distribution
p_vals = [0.05, 0.8, 0.15] #BTC and ETH, BTC and USD, ETH and USD

p_dict = {} # mapping from index in p_vals to the ID's of the currencies val is tuple of ID of currency from p_val
counter = 0

p_dict[0] = (0, 1)
p_dict[1] = (0, 2)
p_dict[2] = (1, 2)

# Takes any int
def typeGen(_numtypes):
    draw_from_dist = rng.multinomial(1, p_vals).tolist()
    pair_index = draw_from_dist.index(1)

    crypto1, crypto2 = p_dict[pair_index]

    direction = random.choice(["1_for_2", "2_for_1"])
    if direction == "1_for_2": # have 1, want 2
        have, want = crypto1, crypto2
    else:
        have, want = crypto2, crypto1

    price_per_unit = currency_dict[have][0] / currency_dict[want][0]
    median_quantity = currency_dict[have][1]
    # desired price is the price you are willing to pay for what you want, per unit of what you have
    desired_price = rng.normal(price_per_unit, price_per_unit * price_stddev)
    quantity_to_sell = rng.normal(median_quantity, median_quantity * quantity_stddev)
    # ID of cript you have, how much of that curr you want to cell, what currency you want, how much of the want crypto do you want
    return (have, quantity_to_sell, want, quantity_to_sell * desired_price)

# ---------------------------------------------
# Crypto Exchange: Workbook Settling Mechanism
# ---------------------------------------------

# ---------------------------------------------
# SECTION I: Generating Agents

# Appends the agent to the list where all agents have/want the same currincies
def sort_order_in_dict(dict_pos, agent_obj, have, want):
    if have < want:
        dict_pos[0].append(agent_obj)
    else:
        dict_pos[1].append(agent_obj)

# Takes an int num_of_agents and generates that many agents
def generate_agents(num_of_agents, combo_agents):
    # Returns a dictionary as such key (currency1, currency2) -> list of two lists [[have_x][want_x]]
    # Elements of each sublist are tuples of (agent_name, have, quantity_to_sell, quantity_to_sell/desired_price)
    matching_groups = defaultdict(list)
    agents = []

    if combo_agents == None:
        # Creates a list of agents
        for i in xrange(num_of_agents):
            agent_name = i # creation time
            have, quantity_to_sell, want, priced_amount = typeGen(1)
            agents.append([agent_name, have, quantity_to_sell, want, priced_amount])
    else:
        agents = combo_agents

    # Populates the matching_groups dictionary
    
    for agent in agents:
        agent_name, have, quantity_to_sell, want, amount = agent
        first_elm, second_elm = max(have, want), min(have, want)

        # Tuple of -> Name, have, quantity_to_sell, want, desired_price, indicator of where agent has been treated as an order or not
        agent_obj = [agent_name, have, quantity_to_sell, amount/quantity_to_sell, False]
        # Append agent to correct position in the matching_groups dict
        if (first_elm, second_elm) in matching_groups:
            sort_order_in_dict(matching_groups[(first_elm, second_elm)],agent_obj, have, want)
        else:
            matching_groups[(first_elm, second_elm)] = [[],[]] # Two separate groups lists, one for each group of orders that have/want the same currencies
            sort_order_in_dict(matching_groups[(first_elm, second_elm)],agent_obj, have, want)
    return matching_groups

# -----------------------------------------------
# SECTION II: Workbook Settling - Matching Agents

def match_order(offers, order):

    order_name, order_have, order_quantity_to_sell, order_desired_price = order[0], order[1], order[2], order[3]
    # Sort from most desired price to least desired price for the according to the order
    sorted_offers = sorted(offers, key=lambda x: x[3])
    matches = []
    completed_orders, number_of_transactions, dollars_transacted = 0, 0, 0

    # Attempt to fulfill a given order
    for i in xrange(len(sorted_offers)):
        # Offer details
        offer_name, offer_have, offer_quantity_to_sell, offer_desired_price, _ = sorted_offers[i]

        # Transact if the offer gives you at least a price as good as yours
        if order_desired_price <= 1/offer_desired_price:
            # Offer quantity in terms of the order currency
            offer_quantity = offer_quantity_to_sell * offer_desired_price
            # Keep track of the matches made
            matches.append((order_name,offer_name))
            # Order is completed
            if offer_quantity > order_quantity_to_sell:
                dollars_transacted += 2.0*order_quantity_to_sell*currencies[order_have][0] # change to $$
                # Update order and offer quantities
                order_quantity_to_sell = 0.0
                sorted_offers[i][2] = (offer_quantity - order_quantity_to_sell) * (1/offer_desired_price)
                # Keep track of number of completed orders and transactions
                completed_orders += 1
                number_of_transactions += 2
                break;
            elif offer_quantity == order_quantity_to_sell: # order and offer are done
                dollars_transacted += 2.0*order_quantity_to_sell*currencies[order_have][0] # change to $$
                order_quantity_to_sell = 0.0
                sorted_offers[i] = None # delete offer
                # Keep track of number of completed orders and transactions
                completed_orders += 2
                number_of_transactions += 2
                break;
            elif offer_quantity < order_quantity_to_sell: # offer is done
                dollars_transacted += 2.0*offer_quantity_to_sell*currencies[offer_have][0] # change to $$
                # Update order quantity
                order_quantity_to_sell = order_quantity_to_sell - offer_quantity
                sorted_offers[i] = None # delete offer
                # Keep track of number of completed orders and transactions
                completed_orders += 1
                number_of_transactions += 2
    # Sort offers based on name (aka time the offer has been placed)
    offers = sorted(filter(None, sorted_offers), key=lambda x: x[0])
    if order_quantity_to_sell == 0:
        return (offers, matches, completed_orders, number_of_transactions, True, dollars_transacted) # Order is filled
    else:
        return (offers, matches, completed_orders, number_of_transactions, False, dollars_transacted) # Order is not filled

# Matches agents according to the current crypto exchange markets.
# Returns a dict of matches. Key=Agent_name -> val= list of tuples (match_name, from, to, quantity?)
def settle_workbook(matching_groups):
    completed_orders_counter = 0
    num_transactions = 0
    total_dollars_transacted = 0
    matches = defaultdict(list)
    # Iterate of each matching group (agents that can transact with each other)
    for key, val in matching_groups.iteritems():
        # Split agents to two groups, want X and has X
        group1, group2 = val[0], val[1]

        # Attempt to match all agents
        while len(group1) != 0 and len(group2) != 0:
            # Find the the oldest element from each group that has not been placed as an order yet

            first_g1, first_g2 = None, None
            for item in group1:
                if item[4] == False: # then set min
                    first_g1 = item
                    break
            for item in group2:
                if item[4] == False: # then set min
                    first_g2 = item
                    break
            # if there are no agents in either one of the groups to transact with
            if first_g1 == None or first_g2 == None:
                break

            if first_g1[0] > first_g2[0]: # Match g2's oldest order
                group2[group2.index(first_g2)][4] = True
                offers, new_matches, new_comp_orders, new_num_trans, offer_status, dollars_transacted = match_order(group1,first_g2) # (offers, order)
                group1 = offers
                if offer_status:
                    del group2[group2.index(first_g2)]
            else: # Match g1's oldest order
                group1[group1.index(first_g1)][4] = True
                offers, new_matches, new_comp_orders, new_num_trans, offer_status, dollars_transacted = match_order(group2,first_g1) # (offers, order)
                group2 = offers
                if offer_status:
                    del group1[group1.index(first_g1)]

            # Count number of transactions and filled orders
            completed_orders_counter += new_comp_orders
            num_transactions += new_num_trans
            total_dollars_transacted += dollars_transacted

            # Add matched to dict
            for match in new_matches:
                agent1, agent2 = match
                matches[agent1].append(agent2)
                matches[agent2].append(agent1)
    return (matches, completed_orders_counter, num_transactions, total_dollars_transacted)

# -------------------------------------------------------------------
# SECTION III: Workbook Settling Mechanism Data Analysis & Simulation

def settle_workbook_simulation(data, exchange_group, num_agents):
    all_matches, num_comp_orders, num_transactions, total_dollars_transacted =  data
    avg_transaction_size = 0
    if num_transactions > 0:
        avg_transaction_size = total_dollars_transacted/num_transactions
        
    print("-----Settle Workbook Mechanism-----")
    print
    print("GENERAL INFO")
    print("-------------------")
    print("Number of Orders: ", num_agents)
    print("Number of Currencies being exchanged: ", num_currencies)
    print("Number of currency exchange groups: ", exchange_group)
    print
    print("ORDER COMPLETION RATE")
    print("-------------------")
    print("Number of Completed Orders: ", num_comp_orders)
    print("Percentage of orders 100'%' fulfilled: ", str((num_comp_orders*100)/num_agents) + '%')
    print
    print("TRANSACTIONS")
    print("-------------------")
    print("Total Number of Transactions: ", num_transactions)
    print("Avg Transaction Size in USD:", avg_transaction_size)
    print("Avg Number of Transactions per agent: ", float(num_transactions) / float(num_agents))
    print

# ---------------------------------------------
# Crypto Exchange: Crypto Exchange Using TTC
# ---------------------------------------------

# ----------------------------------------------
# SECTION I: Agent Compatibility

def priceComparedToMarket(currency1, amount1, currency2, amount2):
    currency1_usd_price, _ = currency_dict[currency1]
    currency2_usd_price, _ = currency_dict[currency2]
    return (amount2 * currency2_usd_price)/(amount1 * currency1_usd_price)
# the higher the worse deal  is getting

def betweenInclusive(lower, upper, number):
    return number <= upper and number >= lower

def reasonableMatch(agent1, agent2, cutoff):
    agent1_has, agent1_has_quant, agent1_want, agent1_want_quant = agent1.type
    agent2_has, agent2_has_quant, agent2_want, agent2_want_quant = agent2.type
    reasonable_quant = betweenInclusive(agent2_has_quant * (1. - cutoff), agent2_has_quant * (1. + cutoff), agent1_want_quant)

    agent1_preferred_price = priceComparedToMarket(*agent1.type)
    agent2_preferred_price = priceComparedToMarket(*agent2.type)

    reasonable_price = betweenInclusive(agent2_preferred_price * (1. - cutoff), agent2_preferred_price * (1. + cutoff), agent1_preferred_price)

    return reasonable_quant and reasonable_price


def strictlyBilateralCompatibility(agent1, agent2, cutoff):
        agent1_has, agent1_has_quant, agent1_want, agent1_want_quant = agent1.type
        agent2_has, agent2_has_quant, agent2_want, agent2_want_quant = agent2.type

        if agent1_has == agent2_want and agent2_has == agent1_want:
            return 1
        else:
            return 0


def basicNoBilateralCompatibility(agent1, agent2, cutoff):
    agent1_has, agent1_has_quant, agent1_want, agent1_want_quant = agent1.type
    agent2_has, agent2_has_quant, agent2_want, agent2_want_quant = agent2.type

    # print(agent1_has_quant, agent2_want_quant)
    if agent1_want == agent2_has and agent1_has != agent2_want and reasonableMatch(agent1, agent2, 0.15):
        return 1
    else:
        return 0


def basicCompatibility(agent1, agent2, cutoff):
    agent1_has, agent1_has_quant, agent1_want, agent1_want_quant = agent1.type
    agent2_has, agent2_has_quant, agent2_want, agent2_want_quant = agent2.type

    # print(agent1_has_quant, agent2_want_quant)
    if agent1_want == agent2_has and reasonableMatch(agent1, agent2, 0.1):
        return 1
    else:
        return 0

# ------------------------------------------------------
# SECTION II: Agent Utility Functions

def basicMatchUtility(agent1, agent2, cutoff):
    agent1_willing_price = priceComparedToMarket(*agent1.type)
    agent2_willing_price = priceComparedToMarket(*agent2.type)

    agent1_has, agent1_has_quant, agent1_want, agent1_want_quant = agent1.type
    agent2_has, agent2_has_quant, agent2_want, agent2_want_quant = agent2.type

    # if abs(agent1_willing_price - agent2_willing_price) < 5:
    if agent1_has == agent2_want or agent1_want == agent2_has:
    # if(agent1_willing_price >= agent2_willing_price):
        return 1
    else:
        # return agent1_willing_price/agent2_willing_price
        return 0

def totalValueMatchUtility(agent1, agent2, cutoff):
    agent1_willing_price = priceComparedToMarket(*agent1.type)
    agent2_willing_price = priceComparedToMarket(*agent2.type)

    agent1_has, agent1_has_quant, agent1_want, agent1_want_quant = agent1.type
    agent2_has, agent2_has_quant, agent2_want, agent2_want_quant = agent2.type

    price1, _ =  currency_dict[agent1_has]
    price2, _ =  currency_dict[agent2_has]

    if agent1_has == agent2_want:
        return (price1 * agent1_has_quant - price2 * agent2_has_quant)/(price1 * agent1_has_quant)
    else:
        return 0

# ------------------------------------------------------
# SECTION III: TTC Simulation

def ttc(num_of_agents, log_status, call_combo):
    newsim = mm.simulation(runs= 1, time_per_run=1, max_agents=10000,
                            logAllData=True,
                           arrival_rate=num_of_agents, success_prob=lambda: 1, # Change to input variable (Max 1,000)
                           time_to_crit=lambda x:10000,
                           algorithm=mm.TTC,
                           typeGenerator=typeGen,
                           matchUtilFct=basicMatchUtility,
                           compatFct=basicNoBilateralCompatibility,
                           crit_input=1000, numTypes=5)

    # newsim.verbose=True
    newsim.run()
    if log_status == True:
        ttc_data(newsim)
    if call_combo == True:
        combo(newsim, num_of_agents)

# ------------------------------------------------------
# SECTION IV: TTC Data Analytics

def ttc_data(newsim):
    print
    print("-----TTC Mechanism-----")
    print(newsim.stats())

# --------------------------------------------------------------------------------
# Crypto Exchange: Crypto Exchange using both TTC and Workbook Settling Mechanism
# --------------------------------------------------------------------------------

# In this section, we will run TTC on a given amount of agents (less than 1000)
# then we will take the unmatched agents from the TTC and input them
# to the Workbook Settling Mechanism

# ------------------------------------------------------
# SECTION I: Run the Simulation

def combo(newsim, num_of_agents):
    # ttc(num_of_agents, True)
    unmatched = []

    for agent in newsim.allAgents:
        if agent in newsim.record_matches:
            if newsim.record_matches[agent] == agent:
                unmatched.append(agent)
        else:
            unmatched.append(agent)
    # print(unmatched)

    settle_agents = []
    for agent in unmatched:
        formatted_agent = [agent.name] + list(agent.type)
        settle_agents.append(formatted_agent)
    
    num_ttc_matches = num_of_agents - len(settle_agents) # Change 100 to real number of agents
    agents_dict = generate_agents(len(settle_agents), settle_agents)
    data = settle_workbook(agents_dict)
    settle_workbook_simulation(data, len(agents_dict), len(settle_agents)) 
    analyze_combo(num_ttc_matches,data, num_of_agents)

# ------------------------------------------------------
# SECTION II: TTC + Workbook Settling Data Analytics
def analyze_combo(num_ttc_matches,data, num_of_agents):
    _, settle_num_comp_orders, settle_num_transactions, settle_total_dollars_transacted =  data
    total_completed_orders = num_ttc_matches+settle_num_comp_orders
    percent_completed_orders = (100.0*total_completed_orders)/num_of_agents
    print
    print("-----COMBO ANALYSIS-----")
    print("Total number of Transactions:", settle_num_transactions+num_ttc_matches)
    print("Total number of completed orders:", total_completed_orders )
    print("Percentage of completed orders: ", percent_completed_orders) 
    print

# --------------------------------------------------------------------------------
# USER_INPUT: RUN THE CODE
# --------------------------------------------------------------------------------

# Default Simulation is Workbook Settling with 100 agents
num_of_agents = 100
method = "settle"

# Validate Inputs
if len(sys.argv) == 3: # method and num_of_agents
    if int(sys.argv[2]) > 1:
        num_of_agents = int(sys.argv[2])
    else:
        print("Entered num_of_agents is incorrect, it defaulted to run with 100 agents")
    method = sys.argv[1]
elif len(sys.argv) == 2: # only method
    method = sys.argv[1]

def run_exchange(method, num_of_agents):
    if method == "settle":
        agents_dict = generate_agents(num_of_agents, None)
        settle_workbook_simulation(settle_workbook(agents_dict), len(agents_dict), num_of_agents) 
    elif method == "ttc": # run ttc algo on agents
        ttc(num_of_agents, True, False) # num_of_agents, show_log, do_combo
    elif method == "combo": # Run TTC then return list of unmatched agents, run settle_workbook on unmatched ttc agents
        ttc(num_of_agents, True, True) # num_of_agents, show_log, do_combo
    elif method == "race": # Runs ttc, settle_workbook, and combo on the same set of agents
        print("RAN RACE")
    else:
        print("You Entered Incorrect Arguments. Please enter the method (settle, ttc, combo, race) followed by the number of agents (0-1000)")

# Run the chosen simulation
run_exchange(method, num_of_agents)



