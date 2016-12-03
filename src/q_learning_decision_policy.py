import random

import numpy as np
import tensorflow as tf

from src.decision_policy import DecisionPolicy


class QLearningDecisionPolicy(DecisionPolicy):
    def __init__(self, actions, input_dim): # 8 = open + high + low + close + volume + timestamp + number of shares + my_budget_left
        self.epsilon = 0.9
        self.gamma = 0.001
        self.actions = actions
        output_dim = len(actions) #3(buy, sell, hold) + how many share sell or buy

        h1_dim = 8 #next layer dimension

        self.y = tf.placeholder(tf.float32, [output_dim]) #output tensor 4dimension

        self.x = tf.placeholder(tf.float32, [None, input_dim]) #input_dim => 8
        W1 = tf.Variable(tf.random_normal([input_dim, h1_dim]))
        b1 = tf.Variable(tf.constant(0.1, shape=[h1_dim]))
        h1 = tf.nn.relu(tf.matmul(self.x, W1) + b1) #next layer

        W2 = tf.Variable(tf.random_normal([h1_dim, output_dim]))
        b2 = tf.Variable(tf.constant(0.1, shape=[output_dim]))
        self.q = tf.nn.relu(tf.matmul(h1, W2) + b2) #output layer?

        loss = tf.square(self.y - self.q)
        self.train_op = tf.train.AdagradOptimizer(0.01).minimize(loss)
        self.sess = tf.Session()
        self.sess.run(tf.initialize_all_variables())

    def select_action(self, current_state, step):
        threshold = min(self.epsilon, step / 1000.)
        if random.random() < threshold:
            # Exploit best option with probability epsilon
            action_q_vals = self.sess.run(self.q, feed_dict={self.x: current_state})
            action_idx = np.argmax(action_q_vals)
            action = self.actions[action_idx]
        else:
            # Explore random option with probability 1 - epsilon
            action = self.actions[random.randint(0, len(self.actions) - 1)]
        return action

    def update_q(self, state, action, reward, next_state):

        action_q_vals = self.sess.run(self.q, feed_dict={self.x: state})
        first = action_q_vals[0,0]
        second = action_q_vals[0,1]
        third = action_q_vals[0,2]

        next_action_q_vals = self.sess.run(self.q, feed_dict={self.x: next_state})
        next_first = next_action_q_vals[0,0]
        next_second = next_action_q_vals[0,1]
        next_third = next_action_q_vals[0,2]
        next = next_action_q_vals

        index_next = np.argmax(next)
        something = reward + self.gamma * next[0, index_next]

        action_q_vals[0, index_next] = something
        first_ =action_q_vals[0,0]
        second_= action_q_vals[0,1]
        third_ = action_q_vals[0,2]

        updated_new_action_q_vals = np.squeeze(np.asarray(action_q_vals))
        self.sess.run(self.train_op, feed_dict={self.x: state, self.y: updated_new_action_q_vals})