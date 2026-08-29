import socket, time, sys, os, json
from pathlib import Path
from audio_edit import AudioEdit

CALL_TIME = 10 #seconds
CURR_RECORDING_PATH = next(Path("./curr_recording").glob("*.wav"))

def send_command(sock, command):
    obj = json.dumps({"command": command}).encode()

    # netstring format:
    # <length>:<data>,
    packet = str(len(obj)).encode() + b":" + obj + b","

    print("sending:", packet)
    sock.sendall(packet)

def wait_for_call(s: socket.socket):
    '''
    Waits for caller
    Returns the phone number of the caller
    '''
    while True:
        data = s.recv(4096).decode(errors='ignore')

        json_text = data.split(":", 1)[1][:-1]  # remove "<length>:" and trailing ","
        obj = json.loads(json_text)

        print("received", json_text)

        if "type" in obj and obj["type"] == "CALL_INCOMING":
            print([obj["peeruri"]])
            return "0" + obj["peeruri"].split("@")[0][6:]

def accept_call(s: socket.socket):
    send_command(s, "accept")

    time.sleep(CALL_TIME)

    send_command(s, "hangup")
    s.close()

def process_audio(phone_num: str):
    audio = AudioEdit(CURR_RECORDING_PATH)
    audio.run_fix(phone_num)

def main():
    s = socket.socket()
    s.connect(('127.0.0.1', 4444))
    send_command(s, "reginfo")

    phone_num = wait_for_call(s)
    # TODO: check number against database

    print(f"Accepting call from {phone_num}")
    accept_call(s)

    process_audio(phone_num)

if __name__ == "__main__":
    main()