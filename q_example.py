import socket
import json
import sys
import random

class Agent():
    """
    Agent class you should implement this
    """

    def __init__(self, initial_status, rate, discount, epsilon):
        """
        initialize this agent
        """
        self.initial_status = initial_status
        self.agent_id = int(initial_status["your_agent_id"])
        self.field = initial_status["field"]
        self.q_valeus = {}
        self.rate = rate
        self.discount = discount
        self.epsilon = epsilon

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
        if status_hash not in self.q_valeus:
            return 0
        if action_tuple not in self.q_valeus[status_hash]:
            return 0
        return self.q_valeus[status_hash][action_tuple]

    def getQValues(self, status):
        """
        get Q values from status
        """
        status_hash = self.make_hash(status)
        if status_hash not in self.q_valeus:
            return []
        return self.q_valeus[status_hash]

    def getMaxQ(self, status):
        """
        get max Q value from status
        """
        status_hash = self.make_hash(status)
        if status_hash not in self.q_valeus:
            return 0
        return max(self.q_valeus[status_hash].values())

    def setQ(self, status, action, v):
        """
        set Q value to status and action
        """
        status_hash = self.make_hash(status)
        action_tuple = tuple(action)
        if status_hash not in self.q_valeus:
            self.q_valeus[status_hash] = {}
        self.q_valeus[status_hash][action_tuple] = v


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
                print(maxv_actions)

        self.last_status = current_status
        self.last_action = action
        return action


def recvline(conn):
    """
    receive data from socket until newline
    """
    buf = b''
    while True:
        c = conn.recv(1)
        if c == b"\n":
            break
        buf += c
    return buf.decode()

def sendline(conn, s):
    """
    send data with newline
    """
    b = (s + "\n").encode()
    conn.send(b)


# create TCP socket and connect to server -- host:port
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# conn.connect((sys.argv[1], int(sys.argv[2])))
conn.connect(('localhost', 9999))

# send client connection request
sendline(conn, json.dumps({
    "type": 'start_connection_client',
    "payload": {}}))

# receive ok response (!)
line = recvline(conn)
print(line)

# return ok response
sendline(conn, json.dumps({
    "type": "start_connection_ok",
    "payload": {}
    }))


# wait for starting competition...

#get competition start alert
init_state  = json.loads(recvline(conn))

# create Agent
LEARNING_RATE = 0.1
DISCOUNT_RATE = 0.3
EPSILON = 0.1
agent = Agent(init_state["payload"], LEARNING_RATE, DISCOUNT_RATE, EPSILON)

# response ok with agent id
sendline(conn, json.dumps({
    "type": "start_competition_ok_client",
    "payload": {
        "my_agent_id": agent.agent_id
    }}))

turn_info = json.loads(recvline(conn))

# while competition continueing
while True:
    # print(turn_info)

    # thinking...
    next_action = agent.action(turn_info["payload"])
    # print(next_action)

    # send my action
    sendline(conn, json.dumps({
        "type": "action_information",
        "payload": {
            "my_agent_id": agent.agent_id,
            "action_type": next_action[0],
            "action_direction": next_action[1]
            }
        }))

    # receive turn infomation or end competition alert
    turn_info = json.loads(recvline(conn))
    if turn_info["type"] == "end_competition":
        break

    # add reward
    s1, s2 = turn_info["payload"]["scores"]
    agent.get_reward( s1 - s2 if agent.agent_id <= 1 else s2 - s1, turn_info["payload"])
print(turn_info)
