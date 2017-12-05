import matchingmarkets as mm
import numpy.random as rng
import random
import numpy as np
import copy
from collections import defaultdict
import sys

quantity_stddev = 0.1
price_stddev = 0.03
num_currencies = 3

# if len(sys.argv) > 2 and int(sys.argv[2]) > 2:
#     num_currencies = int(sys.argv[1])


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
# init p_dict and populate
for i in range(num_currencies):
    for j in range(num_currencies):
        if i != j:
            p_dict[counter] = (i, j)
            counter += 1

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

# ----------------------------------
# Current Crypto Exchange Mechanism
# ----------------------------------

# SECTION I: Generating Agents

# Appends the agent to the list where all agents have/want the same currincies
def sort_order_in_dict(dict_pos, agent_obj, have, want):
    if have < want:
        dict_pos[0].append(agent_obj)
    else:
        dict_pos[1].append(agent_obj)

# Takes an int num_of_agents and generates that many agents
def generate_agents(num_of_agents):
    # Returns a dictionary as such key (currency1, currency2) -> list of two lists [[have_x][want_x]]
    # Elements of each sublist are tuples of (agent_name, have, quantity_to_sell, quantity_to_sell/desired_price)
    matching_groups = defaultdict(list)
    agents = []

    # Creates a list of agents
    for i in xrange(num_of_agents):
        agent_name = i # creation time
        have, quantity_to_sell, want, priced_amount = typeGen(1)
        agents.append([agent_name, have, quantity_to_sell, want, priced_amount])

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

# SECTION II: Matching Agents

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

# Call to generate matches and run current crypto exchange matching algorithm
# Returns tuple of dict of matches and number of fullfilled agents
# settle_workbook(generate_agents(100))

# SECTION III: Data Analysis

num_of_agents = 100
input_num_agents = int(sys.argv[1])

if len(sys.argv) > 1 and int(sys.argv[1]) > 1:
    num_of_agents = int(sys.argv[1])

agents_dict = generate_agents(num_of_agents)
all_matches, num_comp_orders, num_transactions, total_dollars_transacted =  settle_workbook(agents_dict)
avg_transaction_size = 0
if num_transactions > 0:
    avg_transaction_size = total_dollars_transacted/num_transactions

print "START"
print
print "GENERAL INFO"
print "-------------------"
print "Number of Orders: ", num_of_agents
print "Number of Currencies being exchanged: ", num_currencies
print "Number of currency exchange groups: ", len(agents_dict)
print
print "ORDER COMPLETION RATE"
print "-------------------"
print "Number of Completed Orders: ", num_comp_orders
print "Percentage of Completed Orders: ", str((num_comp_orders*100)/num_of_agents) + '%'
print
print "TRANSACTIONS"
print "-------------------"
print "Total Number of Transactions: ", num_transactions
print "Total Dollars Transacted: ", total_dollars_transacted
print "total_dollars_transacted/numberof_transactions (Avg transaction size): ", avg_transaction_size
print "Avg Number of Transactions per agent: ", float(num_transactions) / float(num_of_agents)
print 
print "END"


