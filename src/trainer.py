import numpy as np


class Trainer:
    def __init__(self, policy, budget, prices):
        self.policy = policy
        self.budget = budget
        self.prices = prices

    def train_multiple_times(self):
        num_tries = 10
        final_portfolios = list()
        for i in range(num_tries):
            final_portfolio = train(self.policy, self.budget, self.prices)  # policy, 2400, 0, 1000 prices, 200
            final_portfolios.append(final_portfolio)
        avg, std = np.mean(final_portfolios), np.std(final_portfolios)
        return avg, std


def train(policy, initial_budget, prices, debug=False):
    fee = 10.14
    budget = initial_budget
    how_many_shares = 0
    share_value = 0
    transitions = list()

    for i in range(len(prices) - 1):
        if i % 100 == 0:
            print('progress {:.2f}%'.format(float(100 * i) / len(prices)))

        listofPrices = prices[i]
        current_state = np.asmatrix(np.hstack((listofPrices, budget, how_many_shares)))
        current_portfolio = budget + how_many_shares * share_value
        action = policy.select_action(current_state, i)

        ndrry_row = prices[i, :]
        open = ndrry_row[0]
        high = ndrry_row[1]
        low = ndrry_row[2]
        close = ndrry_row[3]

        share_value = float("{0:.2f}".format(float((
                                                       open + high + low + close) / 4)))  # open + high + low + close + volume + timestamp + myshare_no + my_budget_left
        share_value /= 100

        if action == 'Buy' and budget >= share_value:
            budget -= fee
            how_many_shares = budget // share_value
            budget -= how_many_shares * share_value

        elif action == 'Sell' and how_many_shares > 0:
            budget -= fee
            budget += share_value * how_many_shares
            how_many_shares = 0
        else:
            action = 'Hold'
        new_portfolio = budget + (how_many_shares * share_value)
        reward = new_portfolio - current_portfolio
        next_state = np.asmatrix(np.hstack((prices[i + 1], budget, how_many_shares)))
        transitions.append((current_state, action, reward, next_state))
        policy.update_q(current_state, action, reward, next_state)

    portfolio = budget + how_many_shares * share_value
    if debug:
        print('${}\t{} shares'.format(budget, how_many_shares))
    return portfolio
