import json
import csv

with open("2022-08-30_auspayphones.geojson", "r", encoding="utf-8") as read:
    data = json.load(read)

with open("2022-08-30_auspayphones_as_csv.csv", "w", newline="", encoding="utf-8") as output:
    writer = csv.writer(output)

    writer.writerow(["id", "phone_number", "address"])

    for feature in data["features"]:
        properties = feature["properties"]

        phone_id = properties["Cabinet_Id"]
        if properties["PhoneNumber"] != None:
            phone_number = properties["PhoneNumber"].replace(" PH:", "").strip()
        else:
            phone_number = "NONE"
        address = properties["Address"].strip()

        writer.writerow([phone_id, phone_number, address])