import matchingmarkets as mm
import numpy.random as rng
import random
import numpy as np
import copy
from collections import defaultdict


quantity_stddev = 0.1 # make HIGH as there is big spread on things
price_stddev = 0.03
num_currencies = 3

# tuple represents price in USD, median transaction size in unit of coin
currency_dict = {} # key=ID -> Tupe(price, media transaction_size)
currency_dict[0] = (11000.0, 0.057) #BTC
currency_dict[1] = (460.0, 1.0) #ETH
currency_dict[2] = (1.0, 500) #USD

p_vals = [0.05, 0.8, 0.15] #BTC and ETH, BTC and USD, ETH and USD (probability of exchange between two currencies)

p_dict = {} # mapping from index in p_vals to the ID's of the currencies val is tuple of ID of currency from p_val
counter = 0
# init p_dict and populate
for i in range(num_currencies):
    for j in range(num_currencies):
        if i != j:
            p_dict[counter] = (i, j)
            counter += 1

# Takes any int
# 
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

# newsim = mm.simulation(time_per_run=100, max_agents=5000,
#                        arrival_rate=15, success_prob=lambda: 0.3,
#                        typetypeGenGenerator=,
#                        # compatFct=mm.stochastic_neighborSameType,
#                        algorithm=current_exchange,
#                        # algorithm=mm.max_weight_matching,
#                        # compatFct=current_exchange,
#                        crit_input=3, numTypes=5)

# Make sure matplotlib is __not__ inline for this
# newsim.graph(plot_time=0.8)


# ---------------------
# Current Crypto Exchange Mechanism
# ---------------------

# SECTION I: Generating Agents

def sort_order_in_dict(dict_pos, agent_obj, have, want):
    if have < want:
        dict_pos[0].append(agent_obj)
    else:
        dict_pos[1].append(agent_obj)

def generate_agents(num_of_agents):
    # key (currency1, currency2) -> list of two lists [[have_x][want_x]]
    # Elements of each sublist are typles of (agent_name, have, quantity_to_sell, quantity_to_sell/desired_price)
    matching_groups = defaultdict(list)
    agents = []
    for i in xrange(num_of_agents):
        agent_name = i # creation time, add expiration date!!!
        have, quantity_to_sell, want, priced_amount = typeGen(1)
        agents.append([agent_name, have, quantity_to_sell, want, priced_amount])

    # Creat dict of agents {type -> agent_id}
    for agent in agents:
        agent_name, have, quantity_to_sell, want, amount = agent
        first_elm, second_elm = max(have, want), min(have, want)
        # Name, have, q_to_sell, want, desired_price
        agent_obj = [agent_name, have, quantity_to_sell, amount/quantity_to_sell]
        
        if (first_elm, second_elm) in matching_groups:
            sort_order_in_dict(matching_groups[(first_elm, second_elm)],agent_obj, have, want)
        else: 
            matching_groups[(first_elm, second_elm)] = [[],[]] # Two separate groups. HAVE min then HAVE max
            sort_order_in_dict(matching_groups[(first_elm, second_elm)],agent_obj, have, want)

    return matching_groups

# Call to generate a list of 20 agents
# print generate_agents(10)

# SECTION II: Matching Agents

def match_order(offers, order):
    order_name,order_quantity_to_sell, order_desired_price = order[0], order[2], order[3]  # Order agent
    sorted_offers = sorted(offers, key=lambda x: x[3]) # smaller desired price is better to match with
    temp_matches = []
    i = 0
    completed_orders = 0

    for i in xrange(len(sorted_offers)):
        offer_name, _,offer_quantity_to_sell, offer_desired_price = sorted_offers[i]
        
        if order_desired_price <= 1/offer_desired_price:
            offer_quantity = offer_quantity_to_sell * offer_desired_price
            temp_matches.append((order_name,offer_name))
            
            if offer_quantity > order_quantity_to_sell: # order is filled
                # Update offer quantity
                order_quantity_to_sell = 0
                sorted_offers[i][1] = (offer_quantity - order_quantity_to_sell) * (1/offer_desired_price)
                completed_orders += 1
                break; 
            elif offer_quantity == order_quantity_to_sell: # order and offer are done
                order_quantity_to_sell = 0
                sorted_offers[i] = None # delete offer
                completed_orders += 2
                break;
            elif offer_quantity < order_quantity_to_sell: # offer is done 
                # update order
                order_quantity_to_sell = order_quantity_to_sell - offer_quantity
                sorted_offers[i] = None
                completed_orders += 1

    if order_quantity_to_sell == 0:
        offers = sorted(filter(None, sorted_offers), key=lambda x: x[0])        
        return (offers, temp_matches, completed_orders)
    else: # order can't be matched, remove it from the list
        return (False, False, False)

# Matches agents according to the current crypto exchange markets.
# Returns a dict of matches. Key=Agent_name -> val= list of tuples (match_name, from, to, quantity?)
def current_exchange(matching_groups):
    completed_orders_counter = 0
    matches = defaultdict(list)
    
    for key, val in matching_groups.iteritems():
        
        group1, group2 = val[0], val[1]
        
        while len(group1) != 0 and len(group2) != 0:
            first_g1, first_g2 = group1[0][0], group2[0][0]

            if first_g1 > first_g2: # Match g2's oldest order
                offers, new_matches, new_comp_orders = match_order(group1,group2[0]) # (offers, order)
                del group2[0]
            else: # Match g1's oldest order
                offers, new_matches, new_comp_orders = match_order(group2,group1[0]) # (offers, order)
                del group1[0]
            
            if offers != False and new_matches != False:
                completed_orders_counter += new_comp_orders
                
                for match in new_matches:
                    agent1, agent2 = match
                    matches[agent1].append(agent2)
                    matches[agent2].append(agent1)
                
                if first_g1 > first_g2:
                    group1 = offers
                else:
                    group2 = offers

    return (matches, completed_orders_counter)

# Call to generate matches and run current crypto exchange matching algorithm
# Returns tuple of dict of matches and number of fullfilled agents
# current_exchange(generate_agents(100))

# SECTION III: Data Analytics

all_matches, num_comp_orders =  current_exchange(generate_agents(100))
# print "Matches: ", all_matches
print "General Information"
print "-------------------"
print "Number of Orders: "
print "Number of Currencies being exchanged: "
print "Number of exchange groups: "
print
print "-------------------"
print "Order Completion Rates"
print "Number of Completed Orders: ", num_comp_orders
print "Percentage of orders 100'%' fulfilled: "
print "Percentage of orders 50'%'-99'%' fulfilled: "
print "Percentage of orders 25'%'-49'%' fulfilled: "
print
print "-------------------"
print "Total Number of Transactions: "
print "Estimated Total Transaction Fees: "

























