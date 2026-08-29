import csv
import json

data = []

with open("dataset.csv", "r", encoding="utf-8-sig", newline="") as read:
    reader = csv.DictReader(read)

    for row in reader:
        record = {
            "id": str(row["id"]),
            "phone_number": str(row["phone_number"]),
            "cli": str(row["cli"]),
            "name": str(row["address"]),
            "locality": str(row["locality"]),
            "postcode": int(row["postcode"]),
            "lat": float(row["latitude"]),
            "lng": float(row["longitude"]),
        }

        data.append(record)

with open("dataset2.json", "w", encoding="utf-8") as write:
    json.dump(data, write, indent=4, ensure_ascii=False)