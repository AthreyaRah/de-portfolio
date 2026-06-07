# Data Engineering — Phase 0 to 2 Revision Leaflet
> One rule before opening this: run EXPLAIN ANALYZE on a real work query first.

---

## Phase 0 — Python & Linux Fundamentals

### What a program is
A program is a sequence of instructions. The computer executes them top to bottom unless you tell it otherwise (loops, conditions, functions).

### Variables and types
```python
name = "Rahul"      # str
age = 28            # int
salary = 95000.50   # float
is_employed = True  # bool
```
Type matters — you can't add a string to an integer without converting first.

### Control flow
```python
if age > 18:
    print("adult")
elif age == 18:
    print("just turned")
else:
    print("minor")

for i in range(5):      # 0,1,2,3,4
    print(i)

while condition:
    do_something()
```

### Lists and dicts
```python
items = [1, 2, 3]          # ordered, indexed by position
items.append(4)
items[0]                    # → 1

person = {"name": "Rahul", "age": 28}   # key-value pairs
person["name"]              # → "Rahul"
person["city"] = "Bengaluru"            # add new key
```

### Functions
```python
def clean_row(row):
    return row.strip().lower()

result = clean_row("  Hello  ")   # → "hello"
```
Functions are reusable blocks. Input goes in, output comes out. Keep them small and single-purpose.

### Reading and writing files
```python
with open("data.csv", "r", encoding="utf-8") as f:
    for line in f:
        print(line)

with open("output.csv", "w", encoding="utf-8") as f:
    f.write("id,name\n1,Rahul\n")
```
Always specify encoding. Always use `with` — it closes the file automatically.

### Error handling
```python
try:
    result = int("abc")     # will fail
except ValueError as e:
    print(f"Bad value: {e}")
finally:
    print("always runs")
```
Real pipelines always have try/except. Silent failures are worse than loud ones.

### Linux basics
```bash
pwd                  # where am I?
ls -la               # list files with details
cd folder/           # move into folder
cd ..                # go up one level
cat file.csv         # print file contents
head -n 10 file.csv  # first 10 lines
tail -n 10 file.csv  # last 10 lines
grep "error" log.txt # find lines containing "error"
wc -l file.csv       # count lines
pipe: command1 | command2   # feed output of one into another
```

### Git basics
```bash
git init                    # start a repo
git add file.py             # stage a file
git commit -m "message"     # save a snapshot
git push origin main        # push to remote
git pull                    # pull latest
git log --oneline           # see history
```
Commit early, commit often. A commit message is a note to future you.

---

## Phase 1 — SQL Deeply

### The relational model
Data lives in tables (relations). Rows are records. Columns are attributes. Every table should have a primary key — a column that uniquely identifies each row.

### Joins — the core operation
```sql
-- INNER JOIN: only rows that match in both tables
SELECT o.order_id, c.name
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id;

-- LEFT JOIN: all rows from left, matched rows from right (NULLs if no match)
SELECT c.name, o.order_id
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id;
```
Intuition: INNER JOIN is the intersection. LEFT JOIN keeps everyone on the left, fills NULLs on the right where there's no match.

### NULL — three-valued logic
NULL means unknown. It is not zero, not empty string, not false.
```sql
NULL = NULL    → NULL (not TRUE)
NULL + 5       → NULL
NULL OR TRUE   → TRUE
NULL AND FALSE → FALSE

-- Always use IS NULL / IS NOT NULL
WHERE column IS NULL
WHERE column IS NOT NULL
```

### Aggregations
```sql
SELECT customer_id,
       COUNT(*)           AS total_orders,
       SUM(amount)        AS total_spent,
       AVG(amount)        AS avg_order,
       MAX(amount)        AS biggest_order
FROM orders
GROUP BY customer_id
HAVING SUM(amount) > 1000;   -- filter AFTER grouping (WHERE filters before)
```

### CTEs — readable SQL
```sql
WITH high_value AS (
    SELECT customer_id, SUM(amount) AS total
    FROM orders
    GROUP BY customer_id
    HAVING SUM(amount) > 1000
)
SELECT c.name, h.total
FROM high_value h
JOIN customers c ON h.customer_id = c.id;
```
CTEs are named subqueries. They make complex SQL readable. Use them always.

### Window functions — the senior skill
```sql
SELECT
    order_id,
    customer_id,
    amount,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at) AS order_num,
    SUM(amount)  OVER (PARTITION BY customer_id) AS customer_total,
    LAG(amount)  OVER (PARTITION BY customer_id ORDER BY created_at) AS prev_amount
FROM orders;
```
Window functions compute across a group WITHOUT collapsing rows. The `PARTITION BY` is the group. The `ORDER BY` inside OVER determines row sequence within the group.

---

## Phase 2 — Query Execution & Indexes

### How PostgreSQL executes a query
1. Parse SQL → check syntax
2. Plan → build a query plan (the optimizer picks the cheapest path)
3. Execute → run the plan

### EXPLAIN ANALYZE — read this before tuning anything
```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 1234;
```
- `cost=X..Y` — estimated cost (X = startup, Y = total). Planner's guess.
- `actual time=X..Y` — real measured time in milliseconds
- `rows=N` — how many rows this step produced
- `loops=N` — how many times this node ran

**Read bottom to top.** The innermost node runs first. Work upward.

**The number to watch:** if `rows` estimate vs actual rows are wildly different, the planner made a bad guess and may have chosen a bad plan.

### The three scan types

| Scan | When | Mechanism |
|------|------|-----------|
| Seq Scan | Low selectivity or no index | Read entire table top to bottom |
| Index Scan | High selectivity, few rows | Walk B-tree → heap fetch per row (random I/O) |
| Bitmap Scan | Moderate rows | Walk B-tree → collect all pointers → sort → fetch in order (semi-sequential) |

### What a B-tree index actually is
A B-tree is a sorted, balanced tree stored on disk.
- **Root node** — entry point, says "go left or right"
- **Internal nodes** — routing nodes, narrow down the range
- **Leaf nodes** — hold the actual indexed value + a pointer (heap tuple ID) to the real row in the table
- **Balanced** — every leaf is the same number of jumps from root (usually 3-4 levels for millions of rows)
- **Sorted** — which is why range queries (`>`, `<`, `BETWEEN`) are fast

**Two steps every index lookup does:**
1. Walk the tree → find the matching leaf → get the pointer
2. Follow the pointer → jump to the actual row (heap fetch)

Step 2 is random I/O. This is why indexes lose for low-selectivity queries.

### Selectivity — the key judgment
> An index wins when it filters OUT most of the table.

- Fetching 0.1% of rows → index wins decisively
- Fetching 5-10% of rows → borderline, depends
- Fetching 25%+ of rows → seq scan wins

**Low-cardinality columns** (status, gender, boolean) → usually low selectivity → index often ignored.
**High-cardinality columns** (customer_id, email, order_id) → high selectivity → index usually used.

### Covering index — eliminating the heap fetch
```sql
CREATE INDEX idx_cover ON orders(customer_id, amount);

-- This query never touches the table:
SELECT amount FROM orders WHERE customer_id = 1234;
-- Heap Fetches: 0
```
If the index contains every column the query needs, PostgreSQL answers entirely from the index. No heap fetch. Watch for `Index Only Scan` and `Heap Fetches: 0` in the plan.

### Composite indexes and the leftmost prefix rule
```sql
CREATE INDEX idx ON orders(customer_id, amount);
```
The B-tree is sorted by `customer_id` first, then `amount` within each `customer_id`.

| Query | Index used? | Why |
|-------|-------------|-----|
| `WHERE customer_id = 1234` | ✓ Yes | Leftmost column present |
| `WHERE customer_id = 1234 AND amount > 100` | ✓ Yes | Both columns, left to right |
| `WHERE amount > 100` | ✗ No | Skips leftmost column — no entry point |

**The leftmost column is the entry point into the tree. Skip it and the index is useless.**

### When NOT to index
- **Low selectivity** — status, boolean, gender columns
- **Write-heavy tables** — every INSERT/UPDATE/DELETE must update the B-tree too
- **Small tables** — PostgreSQL will seq scan anyway; index adds overhead for nothing
- **Columns never used in WHERE, JOIN, or ORDER BY** — dead weight

---

## The Mental Model to Carry Forward

| Concept | One-line intuition |
|---------|-------------------|
| Index | A phonebook — sorted so you find entries in 3-4 jumps instead of reading every page |
| B-tree leaf | Holds the value + a pointer to the actual row |
| Heap fetch | The second step — following the pointer to the real row. Random I/O. |
| Covering index | Index holds everything the query needs. No second step. |
| Selectivity | What fraction of the table does this filter touch? Low fraction = index wins. |
| Leftmost prefix | The composite index is only useful if your query starts from the leftmost column |
| Seq scan | Sometimes the right answer — reading in order beats 125k random jumps |

---

*Next: Data Modeling — facts, dimensions, star schema, slowly changing dimensions.*
