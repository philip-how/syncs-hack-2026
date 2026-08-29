import socket, time, sys, os
import json

CALL_TIME = 10 #seconds

def send_command(sock, command):
    obj = json.dumps({"command": command}).encode()

    # netstring format:
    # <length>:<data>,
    packet = str(len(obj)).encode() + b":" + obj + b","

    print("sending:", packet)
    sock.sendall(packet)

# waits for caller, returns the number of the caller
def wait_for_call(s: socket.socket):
    while True:
        data = s.recv(4096).decode(errors='ignore')

        json_text = data.split(":", 1)[1][:-1]  # remove "<length>:" and trailing ","
        obj = json.loads(json_text)

        print("received", json_text)

        if "type" in obj and obj["type"] == "CALL_INCOMING":
            return "0" + obj["peeruri"].split("@")[0][2:]

def accept_call(s: socket.socket):
    send_command(s, "accept")
    print("answering")

    time.sleep(CALL_TIME)

    send_command(s, "hangup")
    s.close()

def main():
    s = socket.socket()
    s.connect(('127.0.0.1', 4444))
    send_command(s, "reginfo")

    num = wait_for_call(s)
    # TODO: check number against database
    accept_call(s)

if __name__ == "__main__":
    main()