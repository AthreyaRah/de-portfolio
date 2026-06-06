import csv

file_name = input("Enter the file name to ingest: ")


def read_data(file_to_read):
    with open(file_to_read, "r") as file:
        reader = csv.reader(file)
        header = next(reader)
        rows = []

        for row in reader:
            rows.append(row)

    return header, rows


def clean_data(data_rows):
    seen_data = set()
    clean_rows = list()
    missing_amount=0
    missing_customer_name=0
    duplicates=0
    empty_rows=0
    invalid_amount = 0
    for row in data_rows:
        if (row[0] == "" and row[1] == "" and row[2] == ""):
            empty_rows += 1
            continue
        elif (row[1] == ""):
            missing_customer_name += 1
            continue
        elif row[2] == "":
            missing_amount += 1
            continue
        else :
            try: 
                float(row[2])
            except ValueError:
                invalid_amount += 1
                continue



        row_tuple = tuple([row[0], row[2]])
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

def write_data(header, clean_rows):
    with open("clean_orders.csv","w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(clean_rows)

    print("Done. Rows written:", len(clean_rows))



header, rows = read_data(file_name)
cleaned_data = clean_data(rows)
write_data(header, cleaned_data)

