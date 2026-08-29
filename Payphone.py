import pandas as pd

df = pd.read_csv("dataset.csv", dtype=str)

class Payphone:
    '''in the csv: id,phone_number,cli,address,locality,postcode,latitude,longitude
    these will be stored in the Payphone class as:
    id: str
    phone_number: -
    cli: str
    address: str
    locality: str
    postcode: int
    latitude: float
    longitude: float
    '''

    def __init__(self, number):
        self.number = number

        row = df[df["phone_number"] == number]
        # row = df[df["cli"] == number]

        self.id = row["id"].iloc[0]
        self.address = row["address"].iloc[0]
        self.locality = row["locality"].iloc[0]
        self.postcode = int(row["postcode"].iloc[0])
        self.latitude = float(row["latitude"].iloc[0])
        self.longitude = float(row["longitude"].iloc[0])
        self.recording = None
        self.has_recording = False

    def get_id(self):
        return self.id

    def get_recording(self):
        return self.recording

    def set_recording(self, new_recording):
        self.recording = new_recording

def check_number(set, number):
    '''
    checks if the number calling is a valid payphone against the set
    '''

    if number in set:
        return True
    return False

def get_info():
    '''
    creating the set of valid payphone numbers
    '''

    # numbers = df.phone_number.to_list()
    numbers = df.cli.to_list()

    set = set(numbers)
    return set