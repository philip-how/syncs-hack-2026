import socket, time, sys, os, json, shutil
from pathlib import Path
from audio_edit import AudioEdit

CALL_TIME = 15
LATEST_RECORDINGS_PATH = Path(__file__).parent / "latest_recordings"
LATEST_RECORDINGS_PATH = LATEST_RECORDINGS_PATH.resolve()

def send_command(sock, command, params=None):

    obj = {"command": command}

    if params:
        obj["params"] = params

    data = json.dumps(obj).encode()

    # netstring format:
    # <length>:<data>,
    packet = str(len(data)).encode() + b":" + data + b","

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
            return "0" + obj["peeruri"].split("@")[0][6:]

def accept_call(s: socket.socket, phone_num: str):
    send_command(s, "accept")
    time.sleep(1)
    send_command(s, "ausrc", f"aufile,{LATEST_RECORDINGS_PATH}/{phone_num}.wav")

    prev_call_time = AudioEdit.get_prev_time_for_number(phone_num)
    time.sleep(prev_call_time + CALL_TIME)

    send_command(s, "hangup")
    s.close()

def process_audio(phone_num: str):
    TMP_RECORDING_PATH = next(Path("./tmp").glob("*dec.wav"))
    audio = AudioEdit(TMP_RECORDING_PATH)
    audio.run_fix(phone_num)

def purge_temp_files():
    folder_path = Path("./tmp")
    for item in folder_path.iterdir():
        item.unlink()

def main():
    s = socket.socket()
    s.connect(('127.0.0.1', 4444))
    send_command(s, "reginfo")

    phone_num = wait_for_call(s)
    # TODO: check number against database

    print(f"Accepting call from {phone_num}")
    accept_call(s, phone_num)

    process_audio(phone_num)
    purge_temp_files()

if __name__ == "__main__":
    main()