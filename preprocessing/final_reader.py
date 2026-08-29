import csv
import pandas as pd

with open("payphones.csv", "r", encoding="utf-8") as read:
    reader = csv.reader(read)

    with open("final_output.csv", "w", encoding="utf-8") as write:
        writer = csv.writer(write)
        writer.writerow(["id", "phone_number", "cli", "address", "locality", "postcode", "latitude", "longitude"])
# cabinet_id,phone,cli,fnn,address_info,street_number,street_name,street_type,locality,state,postcode,latitude,longitude,tty,indigenous_site,product_code,payphones_at_site,locator_address,attributes

        for row in reader:
            if row[9]=="NSW":
                writer.writerow([row[0], row[1], row[2], f"{row[5]} {row[6]} {row[7]}", row[8], row[10], row[11], row[12]])
            # if row[9]=="NSW" and row[1]=="":
            #     print(f"{row[0]} {row[5]} {row[6]} {row[7]} {row[8]} {row[9]} {row[10]}")


    #     df = pd.read_csv('final_output.csv', keep_default_na=False, 
    # on_bad_lines='error', # This will fail and tell you exactly which line is broken
    # dtype=str)

    #     # Sort by a single column (change 'column_name' to your actual column name)
    #     sorted_df = df.sort_values(by='postcode', ascending=True)

    #     # Save the sorted data back to a new CSV file
    #     sorted_df.to_csv('sorted_file.csv', index=False)
