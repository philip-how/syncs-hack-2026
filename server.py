import socket, time, sys, os, json, shutil
from pathlib import Path
from audio_edit import AudioEdit
from payphone import get_payphone_numbers

CALL_TIME = 15
APP_PATH = Path(__file__).parent
APP_PATH = APP_PATH.resolve()

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
    filepath = f"aufile,{APP_PATH}/latest_recordings/{phone_num}.wav"

    file_path = Path(filepath)
    if not file_path.is_file():
        filepath = f"aufile,{APP_PATH}/assets/test.wav"
        prev_call_time = 9
    else:
        prev_call_time = AudioEdit.get_prev_time_for_number(phone_num)

    send_command(s, "ausrc", filepath)
    time.sleep(prev_call_time + CALL_TIME)
    send_command(s, "hangup")

def decline_call(s):
    send_command(s, "accept")
    time.sleep(1)
    filepath = f"aufile,{APP_PATH}/assets/invalid_caller.wav"
    send_command(s, "ausrc", filepath)
    INVALID_CALLER_TIME = 4
    time.sleep(INVALID_CALLER_TIME)

    send_command(s, "hangup")

def process_audio(phone_num: str):
    TMP_RECORDING_PATH = next(Path("./tmp").glob("*dec.wav"))
    audio = AudioEdit(TMP_RECORDING_PATH)
    audio.run_fix(phone_num)

def purge_temp_files():
    folder_path = Path("./tmp")
    for item in folder_path.iterdir():
        item.unlink()

def server_loop(s: socket.socket):
    phone_num = wait_for_call(s)
    payphone_numbers = get_payphone_numbers()

    allowed_numbers = payphone_numbers.union({"0437701777", "0419272511"}) # for debugging
    print(list(allowed_numbers)[:5])

    if phone_num not in allowed_numbers:
        decline_call(s)
    
    print(f"Accepting call from {phone_num}")
    accept_call(s, phone_num)

    process_audio(phone_num)
    purge_temp_files()

def main():
    s = socket.socket()
    s.connect(('127.0.0.1', 4444))
    send_command(s, "reginfo")

    try:
        while True:
            server_loop(s)
    except KeyboardInterrupt:  
        s.close()

if __name__ == "__main__":
    main()