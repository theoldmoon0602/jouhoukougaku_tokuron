import socket
import json
import sys
from montecarlo import Agent as Montecarlo
from random_example import Agent as Random
# from q_example import Agent
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

    yield

    #get competition start alert
    init_state  = json.loads(recvline(conn))
    agent.set_initial_status(init_state["payload"])

    # response ok with agent id
    sendline(conn, json.dumps({
        "type": "start_competition_ok_client",
        "payload": {
            "my_agent_id": agent.agent_id
        }}))

    yield

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

        yield None

        # receive turn infomation or end competition alert
        turn_info = json.loads(recvline(conn))
        if turn_info["type"] == "end_competition":
            s1, s2 = turn_info["payload"]["scores"]
            yield s1 > s2
            # agent.get_reward( s1 - s2 if agent.agent_id <= 1 else s2 - s1, turn_info["payload"])

    raise Exception("A")



def main():
    agents = []

    # ここで各自のエージェントをロードする
    agent1 = Montecarlo(0.1)
    agent2 = Montecarlo(0.1)
    # 学習したデータの読み込み
    agent1.load(open(sys.argv[3]).read())
    agent2.load(open(sys.argv[3]).read())

    agents.append(agent1)
    agents.append(agent2)

    # 残り2体はランダムに行動するエージェント
    agents.append(Random())
    agents.append(Random())

    win = 0
    lose = 0

    for c in range(100):
        rs = []
        for i in range(4):
            r = learning(sys.argv[1], int(sys.argv[2]), agents[i])
            rs.append(r)

        cont = True
        iswin = None
        while cont:
            for i in range(4):
                r = next(rs[i])
                if r is not None and i == 0:
                    print(r)
                    if r:
                        win += 1
                    else:
                        lose += 1
                    cont = False
        print("episode {} done".format(c))

    print("win: {}times, lose: {}times, win-rate: {:.2f}%".format(win, lose, win / (win + lose)))


if __name__ == '__main__':
    main()


