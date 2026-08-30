import socket, time, sys, os, json, shutil
from pathlib import Path
from audio_edit import AudioEdit
from payphone import get_payphone_numbers

CALL_TIME = 60
APP_PATH = Path(__file__).parent
APP_PATH = APP_PATH.resolve()
LATEST_RECORDINGS_PATH = APP_PATH / "latest_recordings"
ASSETS_PATH = APP_PATH / "assets"
TMP_PATH = APP_PATH / "tmp"

def aufile_source(path: Path):
    return f"aufile,{path}"

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

def caller_number_from_peeruri(peeruri: str):
    caller = peeruri.split("@", 1)[0]
    if caller.startswith("sip:"):
        caller = caller[4:]
    if caller.startswith("+"):
        caller = caller[1:]
    if caller.startswith("61"):
        return "0" + caller[2:]
    return caller

def wait_for_end(s: socket.socket, t: int):
    '''
    Waits for caller
    Returns the phone number of the caller
    '''
    deadline = time.time() + t
    buffer = b""
    original_timeout = s.gettimeout()

    try:
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                return

            s.settimeout(remaining)
            try:
                data = s.recv(4096)
            except TimeoutError:
                return

            if not data:
                raise ConnectionError("Baresip control socket closed")

            buffer += data

            while True:
                separator_index = buffer.find(b":")
                if separator_index == -1:
                    break

                message_length = int(buffer[:separator_index])
                message_start = separator_index + 1
                message_end = message_start + message_length
                packet_end = message_end + 1

                if len(buffer) < packet_end:
                    break

                json_text = buffer[message_start:message_end].decode(errors='ignore')
                buffer = buffer[packet_end:]

                obj = json.loads(json_text)

                print("received:", json_text)

                if "type" in obj and obj["type"] == "CALL_CLOSED":
                    return
    finally:
        s.settimeout(original_timeout)

def wait_for_call(s: socket.socket):
    '''
    Waits for caller
    Returns the phone number of the caller
    '''
    buffer = b""

    while True:
        data = s.recv(4096)
        if not data:
            raise ConnectionError("Baresip control socket closed")

        buffer += data

        while True:
            separator_index = buffer.find(b":")
            if separator_index == -1:
                break

            message_length = int(buffer[:separator_index])
            message_start = separator_index + 1
            message_end = message_start + message_length
            packet_end = message_end + 1

            if len(buffer) < packet_end:
                break

            json_text = buffer[message_start:message_end].decode(errors='ignore')
            buffer = buffer[packet_end:]

            obj = json.loads(json_text)

            print("received:", json_text)

            if "type" in obj and obj["type"] == "CALL_INCOMING":
                return caller_number_from_peeruri(obj["peeruri"])

def accept_call(s: socket.socket, phone_num: str):
    send_command(s, "accept")
    time.sleep(1)

    previous_recording_path = LATEST_RECORDINGS_PATH / f"{phone_num}.wav"
    if previous_recording_path.is_file():
        playback_path = previous_recording_path
    else:
        playback_path = ASSETS_PATH / "no_message_yet.wav"

    playback_time = int(AudioEdit.determine_previous_length(playback_path) / 1000)

    send_command(s, "ausrc", aufile_source(playback_path))
    wait_for_end(s, playback_time + CALL_TIME)
    send_command(s, "hangup")
    return int(playback_time * 1000)

def decline_call(s):
    send_command(s, "accept")
    time.sleep(1)
    filepath = f"aufile,{APP_PATH}/assets/invalid_caller.wav"
    send_command(s, "ausrc", filepath)
    INVALID_CALLER_TIME = 8
    wait_for_end(s, INVALID_CALLER_TIME)

    send_command(s, "hangup")

def process_audio(phone_num: str, intro_length_ms: int):
    TMP_RECORDING_PATH = next(TMP_PATH.glob("*dec.wav"))
    audio = AudioEdit(TMP_RECORDING_PATH)
    audio.run_fix(phone_num, intro_length_ms)

def purge_temp_files():
    for item in TMP_PATH.iterdir():
        item.unlink()

def server_loop(s: socket.socket):
    phone_num = wait_for_call(s)
    payphone_numbers = get_payphone_numbers()

    allowed_numbers = payphone_numbers.union({"0437701777", "0419272511"}) # for debugging
    print(list(allowed_numbers)[:5])

    if phone_num not in allowed_numbers:
        decline_call(s)
        return
    
    print(f"Accepting call from {phone_num}")
    intro_length_ms = accept_call(s, phone_num)

    process_audio(phone_num, intro_length_ms)
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
