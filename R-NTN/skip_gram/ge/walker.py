import random
import numpy as np
from tqdm import tqdm
from collections import defaultdict


class RandomWalker:
    def __init__(self, G, transaction_volume, transaction_volume_between):
        """
        :param G: 输入的图
        """
        self.G = G
        self.transaction_volume = transaction_volume
        self.transaction_volume_between = transaction_volume_between
        self.transition_probs = {}

    def preprocess_transition_probs(self):
        """
        预处理转移概率
        """
        for node in self.G.nodes():
            neighbors = list(self.G.neighbors(node))
            if len(neighbors) == 0:
                continue  # 如果没有邻居，则跳过该节点

            probs = []
            # print(f"变量 node 的数据类型: {type(node)}")
            # print(f"字典中键的值的数据类型: {type(next(iter(self.transaction_volume.values())))}")

            total_volume = self.transaction_volume[node]
            for neighbor in neighbors:
                prob = self.transaction_volume_between[node][neighbor] / total_volume if total_volume > 0 else 0
                probs.append(prob)
            # 归一化处理
            total_prob = sum(probs)
            if total_prob > 0:
                probs = [p / total_prob for p in probs]
            else:
                probs = [1 / len(neighbors)] * len(neighbors)  # 如果总概率为0，则均匀分布
            self.transition_probs[node] = probs

    def node2vec_walk(self, walk_length, start_node):
        G = self.G
        walk = [start_node]

        while len(walk) < walk_length:
            cur = walk[-1]
            cur_nbrs = list(G.neighbors(cur))
            if len(cur_nbrs) > 0:
                if len(walk) == 1:
                    next_node = self.next_node(cur, cur_nbrs)
                    walk.append(next_node)
                else:
                    prev = walk[-2]
                    next_node = self.next_node(cur, cur_nbrs, prev)
                    walk.append(next_node)
            else:
                break

        return walk

    def next_node(self, cur, cur_nbrs, prev=None):
        # 获取预处理的转移概率
        if cur in self.transition_probs:
            probs = self.transition_probs[cur]
        else:
            probs = [1 / len(cur_nbrs)] * len(cur_nbrs)  # 如果没有预处理的概率，则均匀分布

        # 根据转移概率选择下一个节点
        next_node = np.random.choice(cur_nbrs, p=probs)
        return next_node

    def simulate_walks(self, num_walks, walk_length, workers=1, verbose=0):
        walks = []
        nodes = list(self.G.nodes())
        for walk_iter in tqdm(range(num_walks), desc="Simulating walks"):
            random.shuffle(nodes)
            for node in nodes:
                walks.append(self.node2vec_walk(walk_length=walk_length, start_node=node))
        return walks