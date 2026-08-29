import json
import csv

with open("australian_postcodes.csv", "r", encoding="utf-8") as read:
    reader = csv.reader(read)

    with open("nsw_postcodes.csv", "w", encoding="utf-8") as write:
        writer = csv.writer(write)
        writer.writerow(next(reader))

        for row in reader:
            if row[3]=="NSW":
                writer.writerow(row)