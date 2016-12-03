import numpy as np

class Trainer():
    def train_multiple_times(policy, budget, prices):
        num_tries = 10
        final_portfolios = list()
        for i in range(num_tries):
            final_portfolio = train(policy, budget, prices) #policy, 2400, 0, 1000 prices, 200
            final_portfolios.append(final_portfolio)
        avg, std = np.mean(final_portfolios), np.std(final_portfolios)
        return avg, std

def train(policy, initial_budget, prices, debug=False):
    fee = 10.14
    budget = initial_budget
    howManyShares = 0
    share_value = 0
    transitions = list()

    for i in range(len(prices)-1):
        if i % 100 == 0:
            print('progress {:.2f}%'.format(float(100 * i) / len(prices) ))

        listofPrices = prices[i]
        current_state = np.asmatrix(np.hstack((listofPrices, budget, howManyShares)))
        current_portfolio = budget + howManyShares * share_value
        action = policy.select_action(current_state, i)

        ndrry_row =prices[i,:]
        open = ndrry_row[0]
        high = ndrry_row[1]
        low = ndrry_row[2]
        close = ndrry_row[3]

        share_value =float("{0:.2f}".format(float((open + high + low + close) /4)))  # open + high + low + close + volume + timestamp + myshare_no + my_budget_left
        share_value = share_value/100

        if action == 'Buy' and budget >= share_value:
            budget -= fee
            howManyShares = budget // share_value
            budget -= howManyShares * share_value

        elif action == 'Sell' and howManyShares > 0:
            budget -= fee
            budget += share_value * howManyShares
            howManyShares = 0
        else:
            action = 'Hold'
        new_portfolio = budget + (howManyShares * share_value)
        reward = new_portfolio - current_portfolio
        next_state = np.asmatrix(np.hstack((prices[i + 1], budget, howManyShares)))
        transitions.append((current_state, action, reward, next_state))
        policy.update_q(current_state, action, reward, next_state)

    portfolio = budget + howManyShares * share_value
    if debug:
        print('${}\t{} shares'.format(budget, howManyShares))
    return portfolio
