import csv
import pandas as pd

with open("final_output.csv", "r", encoding="utf-8") as read:
    reader = csv.reader(read)

    with open("dataset.csv", "w", encoding="utf-8") as write:
        writer = csv.writer(write)

        for row in reader:
            if row[1]!="":
                writer.writerow(row)