import socket, time, sys, os
import json

def send_command(sock, command):
    obj = json.dumps({"command": command}).encode()

    # netstring format:
    # <length>:<data>,
    packet = str(len(obj)).encode() + b":" + obj + b","

    print("sending:", packet)
    sock.sendall(packet)

s = socket.socket()
s.connect(('127.0.0.1', 4444))

print("brih")

send_command(s, "reginfo")

while True:
    data = s.recv(4096).decode(errors='ignore')

    json_text = data.split(":", 1)[1][:-1]  # remove "<length>:" and trailing ","
    obj = json.loads(json_text)

    print("received", json_text)

    if "type" in obj and obj["type"] == "CALL_INCOMING":
        break

send_command(s, "accept")
print("answering")

CALL_TIME = 10
time.sleep(CALL_TIME)

send_command(s, "hangup")
s.close()

print("finished")