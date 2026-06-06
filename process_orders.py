import csv

file_name = input("Enter the file name to ingest: ")


def read_data(file_to_read):
    with open(file_to_read, "r") as file:
        # reader = csv.reader(file)
        reader = csv.DictReader(file)
        # header = next(reader)
        rows = []

        for row in reader:
            rows.append(row)

    return rows


def clean_data(data_rows):
    seen_data = set()
    clean_rows = list()
    missing_amount=0
    missing_customer_name=0
    duplicates=0
    empty_rows=0
    invalid_amount = 0
    for row in data_rows:
        if (row["order_id"] == "" and row["customer_name"] == "" and row["amount"] == ""):
            empty_rows += 1
            continue
        elif (row["customer_name"] == ""):
            missing_customer_name += 1
            continue
        elif row["amount"] == "":
            missing_amount += 1
            continue
        else :
            try: 
                if row["amount"]:
                    float(row["amount"])
            except ValueError:
                invalid_amount += 1
                continue



        row_tuple = tuple([row["order_id"], row["amount"]])
        if row_tuple in seen_data:
            duplicates += 1
            continue
        seen_data.add(row_tuple)
        
        clean_rows.append(row)


    print(f"Skipped {missing_amount} rows : Missing Amount")
    print(f"Skipped {missing_customer_name} rows : Missing Customer Name")
    print(f"Skipped {duplicates} rows : Duplicates")
    print(f"Skipped {empty_rows} rows : Empty Rows")
    print(f"Skipped {invalid_amount} rows : Invalid Amount")
    
    return clean_rows

def write_data(clean_rows):
    with open("clean_orders.csv","w", newline="") as file:
        if clean_rows:
            writer = csv.DictWriter(file,fieldnames=clean_rows[0].keys())
            writer.writeheader()
            writer.writerows(clean_rows)

            print("Done. Rows written:", len(clean_rows))
        else:
            print("No valid data to write.")



rows = read_data(file_name)
cleaned_data = clean_data(rows)
write_data(cleaned_data)

