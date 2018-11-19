import socket
import json
import sys

def recvline(conn):
    buf = b''
    while True:
        c = conn.recv(1)
        if c == b"\n":
            break
        buf += c
    return buf.decode()

def sendline(conn, s):
    b = (s + "\n").encode()
    conn.send(b)


conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((sys.argv[1], int(sys.argv[2])))

sendline(conn, json.dumps({
    "type": 'start_connection_client',
    "payload": {}}))
line = recvline(conn)
print(line)
sendline(conn, json.dumps({
    "type": "start_connection_ok",
    "payload": {}
    }))

init_state  = json.loads(recvline(conn))
sendline(conn, json.dumps({
    "type": "start_competition_ok_client",
    "payload": {
        "my_agent_id": init_state["payload"]["your_agent_id"]
    }}))
while True:
    turn_info = json.loads(recvline(conn))
    if turn_info["type"] == "end_competition":
        break
    print(turn_info)
    sendline(conn, json.dumps({
        "type": "action_information",
        "payload": {
            "my_agent_id": init_state["payload"]["your_agent_id"],
            "action_type": 0,
            "action_direction": 7
            }
        }))
