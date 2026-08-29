import csv
import pandas as pd

old_phones = pd.read_csv(
    "2022-08-30_auspayphones_as_csv.csv",
    dtype=str
)

def search(search_value):    
    results = old_phones[old_phones["id"] == search_value]

    # if len(results) > 1:
    #     print("YES")
    if not results.empty:
        phone_number = results.iloc[0]["phone_number"]
        # address = results.iloc[0]["address"]
        # return phone_number, address
        return phone_number
    else:
        print(f"{search_value}: No matches found.")
        # return None, None
        return None

with open("payphone_register.csv", "r", encoding="utf-8") as read:
    reader = csv.reader(read)

    # with open("2022-08-30_auspayphones_as_csv.csv", "r", encoding="utf-8") as read:
    #     helper = csv.reader(read)

    with open ("output.csv", "w", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(["id", "phone_number", "address", "locality", "postcode", "latitude", "longitude"])

        for row in reader:
            # search("2022-08-30_auspayphones_as_csv.csv", row[0])
            if row[8]=="NSW":

                # phone_number, address = search(row[0])
                phone_number = search(row[0])
                if phone_number == "NONE":
                    print("yes")
                writer.writerow([row[0], phone_number, f"{row[4]} {row[5]} {row[6]}", row[7], row[10], row[12], row[13]])


