import socket
import json
import sys
from multiprocessing import Pool
from q_example import Agent
from datetime import datetime

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


def agentFactory():
    # create Agent
    LEARNING_RATE = 0.1
    DISCOUNT_RATE = 0.3
    EPSILON = 0.1
    agent = Agent(LEARNING_RATE, DISCOUNT_RATE, EPSILON)
    return agent

def learning(server_host, server_port, agent):
    # create TCP socket and connect to server -- host:port
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server_host, server_port))

    # send client connection request
    sendline(conn, json.dumps({
        "type": 'start_connection_client',
        "payload": {}}))

    # receive ok response (!)
    line = recvline(conn)

    # return ok response
    sendline(conn, json.dumps({
        "type": "start_connection_ok",
        "payload": {}
        }))

    #get competition start alert
    init_state  = json.loads(recvline(conn))
    agent.set_initial_status(init_state["payload"])

    # response ok with agent id
    sendline(conn, json.dumps({
        "type": "start_competition_ok_client",
        "payload": {
            "my_agent_id": agent.agent_id
        }}))

    # first turn info
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

    return agent



def main():
    agents = [agentFactory() for i in range(4)]

    for c in range(10):
        pool = Pool(processes=4)
        rs = []
        for i in range(4):
            # r = pool.apply_async(learning, args=('localhost', 9999, agents[i]))
            r = pool.apply_async(learning, args=(sys.argv[1], int(sys.argv[2]), agents[i]))
            rs.append(r)
        pool.close()
        pool.join()

        agents = []
        for r in rs:
            agents.append(r.get())  # throw exception
        print("episode {} done".format(c))

    ts = datetime.now().timestamp()
    for i, a in enumerate(agents):
        with open("{}_{}.json".format(ts, i), "w") as f:
            f.write(a.dump())


if __name__ == '__main__':
    main()


