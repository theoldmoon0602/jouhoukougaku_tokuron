import socket
import json
import sys
import random

class Agent():
    """
    Agent class you should implement this
    """

    def __init__(self, initial_status):
        """
        initialize this agent
        """
        self.initial_status = initial_status
        self.agent_id = int(initial_status["your_agent_id"])
        self.field = initial_status["field"]
        # self.q_list = []

    def get_reward(self, reward):
        """
        get reward from environment per turn/episode
        """
        pass

    def action(self, current_status):
        """
        return action from current_status

        returns: [ action, direction  ]
        """
        my_x, my_y = current_status["agents"][self.agent_id]
        self.owners = current_status["owners"]
        return [ random.randint(0, 1), random.randint(1, 9) ]



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
agent = Agent(init_state["payload"])

# response ok with agent id
sendline(conn, json.dumps({
    "type": "start_competition_ok_client",
    "payload": {
        "my_agent_id": agent.agent_id
    }}))

turn_info = json.loads(recvline(conn))

# while competition continueing
while True:
    print(turn_info)

    # thinking...
    next_action = agent.action(turn_info["payload"])

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
    agent.get_reward( s1 - s2 if agent.agent_id <= 1 else s2 - s1 )
print(turn_info)
