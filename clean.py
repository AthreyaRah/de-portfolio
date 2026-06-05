import csv

with open("messy.csv", "r") as file:
    reader = csv.reader(file)
    header = next(reader)

    rows = []
    for row in reader:
        rows.append(row)

seen = set()
clean_rows = []

for row in rows:
    if row[0] == "" and row[1] == "" and row[2] == "":
        continue

    row_tuple = tuple(row)
    if row_tuple in seen:
        continue
    seen.add(row_tuple)

    try:
        int(row[1])
    except ValueError:
        continue

    clean_rows.append(row)

with open("clean.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(clean_rows)

print("Done. Rows written:", len(clean_rows))
