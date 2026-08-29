from pydub import AudioSegment

class AudioEdit:
    '''
    A module which can be used to apply needed changes to call recordings.

    The run_fix command cuts out the 

    Usage:
    audio = AudioEdit(<destination>)
    audio.run_fix(<phone number>)

    Additional useful function:
    AudioEdit.get_prev_time_for_number(<number>)
    '''
    BEEP_LOCATION = "phone_beep.wav"

    def __init__(self, file_dest):
        self.file_dest = file_dest

        self.audio = AudioSegment.from_wav(file_dest)

    def cut_first_section(self, milliseconds):
        self.audio = self.audio[milliseconds:]

    def save_audio(self, destination):
        self.audio.export(destination, format="wav")

    def add_beep(self):
        silence = AudioSegment.silent(duration=1000)
        beep = AudioSegment.from_wav(AudioEdit.BEEP_LOCATION)
        self.audio = self.audio + silence + beep

    def determine_destination(phone_number):
        return f"latest_recordings/{phone_number}.wav"

    def determine_previous_length(dest):
        try:
            prev_audio = AudioSegment.from_wav(dest)
            return len(prev_audio)
        except FileNotFoundError:
            return 0

    def get_prev_time_for_number(phone_number):
        '''
        Return value: length of previous clip for this phone number in seconds.
        Zero if that does not exist
        '''
        dest = AudioEdit.determine_destination(phone_number)
        return AudioEdit.determine_previous_length(dest) / 1000


    def run_fix(self, phone_number):
        dest = AudioEdit.determine_destination(phone_number)
        length = AudioEdit.determine_previous_length(dest)

        self.cut_first_section(length)
        self.add_beep()
        
        self.save_audio(dest)

def test_audio_edit():
    audio = AudioEdit("test.wav")
    audio.run_fix("123456789")

if __name__ == "__main__":
    test_audio_edit()
    