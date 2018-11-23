import sys
import random
import json

class Agent():
    """
    Agent class you should implement this
    """

    def __init__(self, rate, discount, epsilon):
        """
        initialize this agent
        """
        self.q_values = {}
        self.rate = rate
        self.discount = discount
        self.epsilon = epsilon

    def dump(self):
        d = {}
        for k, v in self.q_values.items():
            dd = {}
            for kk, vv in v.items():
                dd["{},{}".format(*kk)] = vv
            d[k] = dd
        return json.dumps(d)

    def load(self, qvalues):
        d = json.loads(qvalues)
        for k, v in d.items():
            self.q_values[k] = {}
            for kk, vv in v.items():
                kkk = tuple(map(int, kk.split(",")))
                self.q_values[k][kkk] = vv



    def set_initial_status(self, initial_status):
        self.initial_status = initial_status
        self.agent_id = int(initial_status["your_agent_id"])
        self.field = initial_status["field"]

    def _getxy(self, x, y, arr, default):
        """
        private method (prefixed with _)
        """
        if x < 0 or y < 0 or y >= len(arr) or x >= len(arr[y]):
            return default
        return arr[y][x]


    def make_hash(self, status):
        """
        (x,y )を中心に3x3マスで雑hashをとる
        一意っぽくなれば何でもいい
        """
        x, y = status["agents"][self.agent_id]
        owners = status["owners"]

        h = ""
        for dy in range(-1, 1):
            for dx in range(-1, 1):
                # ascii code のどまんなか + fieldの点数
                p = int((0x20 + 0x7f) / 2) + self._getxy(x + dx, y + dy, self.field, 17)
                o = str(self._getxy(x + dx, y + dy, owners, 0))
                h = h + chr(p) + o

        return h

    def getQ(self, status, action):
        """
        get Q value from status and action
        """
        status_hash = self.make_hash(status)
        action_tuple = tuple(action)
        if status_hash not in self.q_values:
            return 0
        if action_tuple not in self.q_values[status_hash]:
            return 0
        return self.q_values[status_hash][action_tuple]

    def getQValues(self, status):
        """
        get Q values from status
        """
        status_hash = self.make_hash(status)
        if status_hash not in self.q_values:
            return []
        return self.q_values[status_hash]

    def getMaxQ(self, status):
        """
        get max Q value from status
        """
        status_hash = self.make_hash(status)
        if status_hash not in self.q_values:
            return 0
        return max(self.q_values[status_hash].values())

    def setQ(self, status, action, v):
        """
        set Q value to status and action
        """
        status_hash = self.make_hash(status)
        action_tuple = tuple(action)
        if status_hash not in self.q_values:
            self.q_values[status_hash] = {}
        self.q_values[status_hash][action_tuple] = v


    def get_reward(self, reward, next_status):
        """
        get reward from environment per turn/episode
        """
        self.setQ(self.last_status, self.last_action,
                  (1 - self.rate) * self.getQ(self.last_status, self.last_action) +
                        self.rate * (reward + self.discount * self.getMaxQ(next_status)))


    def action(self, current_status):
        """
        select action from current_status by epsilon-greedy method

        returns: [ action, direction  ]
        """

        # 考察：盤面を 90, 180, 270度回転しても同一に見えそう
        # 考察：他のエージェントの位置を考えていない
        # 考察：なんかあったけど忘れた

        actions_values = self.getQValues(current_status)
        if random.random() <= self.epsilon or len(actions_values) == 0:
            action = [ random.randint(0, 1), random.randint(1, 9) ]
        else:
            # get action which has max Q value
            max_v = self.getMaxQ(current_status)
            maxv_actions = [action for action, value in actions_values.items() if value == max_v]
            if len(maxv_actions) == 0:
                action = [ random.randint(0, 1), random.randint(1, 9) ]
            else:
                action = random.choice(maxv_actions)

        self.last_status = current_status
        self.last_action = action
        return action
