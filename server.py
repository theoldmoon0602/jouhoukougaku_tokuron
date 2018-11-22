# coding: utf-8
import asyncio
import json
import subprocess
import sys
from enum import Enum

# グローバル変数
agents = []
viewers = []
game = None
GAME_BINARY = ""
N = 4

class Game():
    """
    ゲーム本体との通信をするクラス
    """

    def __init__(self, binary, max_turn):
        self.max_turn = max_turn
        self.binary = binary

        r = subprocess.run([binary, "init"], capture_output=True, encoding=sys.getdefaultencoding())
        output = r.stdout.split("\n")
        self.init_state = json.loads(output[0])
        self.game_state = json.loads(output[1])

    def do_action(self, agents):
        actions = []
        for agent in sorted(agents, key=lambda x: x.agent_id):
            actions.append(agent.next_action)

        stdin = json.dumps({
            "field_width": self.init_state["field_width"],
            "field_height": self.init_state["field_height"],
            "field": self.init_state["field"],
            "turn": self.game_state["turn"],
            "owners": self.game_state["owners"],
            "agents": self.game_state["agents"],
            })+ "\n" + json.dumps({"actions": actions}) + "\n"
        r = subprocess.Popen([self.binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding=sys.getdefaultencoding())
        output = r.communicate(stdin)[0].strip()
        self.game_state = json.loads(output)

class Viewer():
    def __init__(self, id, send):
        self.id = id
        self.send = send

    def send_init(self):
        self.send(json.dumps({
            "type": "start_connection_response",
            "payload": {}
        }))

    def send_start_comp(self, game):
        self.send(json.dumps({
            "type": "start_competition_viewer",
            "payload": {
                "max_turn_num": game.max_turn,
                "field_width": game.init_state["field_width"],
                "field_height": game.init_state["field_height"],
                "field": game.init_state["field"],
                "agents": game.init_state["agents"],
                "scores": game.game_state["scores"]
            }
        }))


    def send_turn_info(self, game):
        self.send(json.dumps({
            "type": "turn_infomation",
            "payload": {
                "turn": game.game_state["turn"],
                "owners": game.game_state["owners"],
                "agents": game.game_state["agents"],
                "scores": game.game_state["scores"]
                }
            }))


    def send_end_comp(self, game):
        self.send(json.dumps({
            "type": "end_competition",
            "payload": {
                "turn": game.game_state["turn"],
                "owners": game.game_state["owners"],
                "agents": game.game_state["agents"],
                "scores": game.game_state["scores"]
            }}))

class AgentState(Enum):
    """
    エージェントの状態を表す
    """
    INIT = 1
    INIT_OK = 2
    COMP_START = 3


class Agent():
    """
    各エージェントを表す
    """
    def __init__(self, id, send, agent_id):
        self.id = id
        self.send = send
        self.agent_id = agent_id
        self.stat = AgentState.INIT

    def send_init(self):
        self.send(json.dumps({
            "type": "start_connection_response",
            "payload": {}
        }))

    def send_start_comp(self, game):
        self.send(json.dumps({
            "type": "start_competition_client",
            "payload": {
                "max_turn_num": game.max_turn,
                "your_agent_id": self.agent_id,
                "field_width": game.init_state["field_width"],
                "field_height": game.init_state["field_height"],
                "field": game.init_state["field"],
                "agents": game.init_state["agents"],
                "scores": game.game_state["scores"]
            }
        }))

    def send_turn_info(self, game):
        self.send(json.dumps({
            "type": "turn_infomation",
            "payload": {
                "turn": game.game_state["turn"],
                "owners": game.game_state["owners"],
                "agents": game.game_state["agents"],
                "scores": game.game_state["scores"]
                }
            }))

    def send_end_comp(self, game):
        self.send(json.dumps({
            "type": "end_competition",
            "payload": {
                "turn": game.game_state["turn"],
                "owners": game.game_state["owners"],
                "agents": game.game_state["agents"],
                "scores": game.game_state["scores"]
            }}))


    def set_next_action(self, data):
        data.pop("my_agent_id", None)
        self.next_action = data


    def recv_init_ok(self):
        self.stat = AgentState.INIT_OK

    def recv_comp_ok(self):
        self.stat = AgentState.INIT_OK


def add_viewer(id, send):
    global viewers
    global game

    viewers.append(Viewer(id, send))
    viewers[-1].send_init()


def add_agent(id, send):
    global agents
    global game

    agents.append(Agent(id, send, len(agents)))
    agents[-1].send_init()
    print("[+]{}".format(id))

    if len(agents) == N:
        game = Game(GAME_BINARY, 40)  # 本来はターン数もランダムっぽい
        for agent in agents:
            agent.send_start_comp(game)
        for v in viewers:
            v.send_start_comp(game)

def start_ok(id):
    for agent in agents:
        if agent.id == id:
            agent.recv_init_ok()
            break


comp_ok_agents = set()
def competiton_ok(id):
    global comp_ok_count
    for agent in agents:
        if agent.id == id and id not in comp_ok_agents:
            comp_ok_agents.add(id)
            agent.recv_comp_ok()
            break

    if len(comp_ok_agents) == N:
        for agent in agents:
            agent.send_turn_info(game)

action_agents = set()
def action(id, data):
    global action_agents
    for agent in agents:
        if agent.id == id and id not in action_agents:
            action_agents.add(id)
            agent.set_next_action(data)
            break
    if len(action_agents) == N:
        game.do_action(agents)
        action_agents = set()

        if game.game_state["turn"] >= game.max_turn:
            for agent in agents:
                agent.send_end_comp(game)
            for v in viewers:
                v.send_end_comp(game)
            sys.exit()
        else:
            for agent in agents:
                agent.send_turn_info(game)
            for v in viewers:
                v.send_turn_info(game)


class EchoServer(asyncio.Protocol):
    """
    クライアントとのやり取りをするソケット部分
    """
    def connection_made(self, transport):
        self.transport = transport
        self.addr, self.port = self.transport.get_extra_info('peername')
        self.id = "{}:{}".format(self.addr, self.port)

    def send(self, data):
        b = (data + "\n").encode()
        self.transport.write(b)

    def data_received(self, data):
        # print("[+]{}".format(data))
        r = json.loads(data)
        if r["type"] == "start_connection_client":
            add_agent(self.id, self.send)
        if r["type"] == "start_connection_viewer":
            add_viewer(self.id, self.send)
        if r["type"] == "start_connection_ok":
            start_ok(self.id)
        if r["type"] == "start_competition_ok_client":
            competiton_ok(self.id)
        if r["type"] == "start_competition_ok_viewer":
            pass
        if r["type"] == "turn_information_ok":
            pass
        if r["type"] == "end_competition_ok":
            pass
        if r["type"] == "action_information":
            action(self.id, r["payload"])

    def connection_lost(self, exc):
        self.transport.close()



def main():
    global GAME_BINARY

    host = sys.argv[1]
    port = int(sys.argv[2])
    GAME_BINARY = sys.argv[3]

    ev_loop = asyncio.get_event_loop()

    factory = ev_loop.create_server(EchoServer, host, port)
    server = ev_loop.run_until_complete(factory)

    try:
        ev_loop.run_forever()
    finally:
        server.close()
        ev_loop.run_until_complete(server.wait_closed())
        ev_loop.close()


if __name__ == '__main__':
    main()
