from src.share_price_getter import SharePriceGetter as spg
from src.trainer import Trainer
from src.q_learning_decision_policy import QLearningDecisionPolicy

if __name__ == '__main__':
    s_price_getter = spg('LLOY')
    prices = s_price_getter.get_price_list('2000-01-01', '2016-10-28')
    actions = ['Buy', 'Sell', 'Hold']

    dimensions = 8  # open + high + low + close + volume + timestamp + myshare_no + my_budget_left
    policy = QLearningDecisionPolicy(actions, dimensions)

    budget = 2400.0
    num_stocks = 0
    avg, std = Trainer.train_multiple_times(policy, budget, num_stocks, prices)
    print(avg, std)

    # thread1 = real_time_decider(policy, budget, num_stocks).start()
    # thread1.join()
