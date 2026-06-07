-- Query 1 — Customer summary

-- All customers including those with no orders
-- Columns: customer_id, customer_name, total_orders, total_spend, has_null_amount
-- total_orders: 0 for customers with no orders
-- total_spend: 0 for customers with no orders
-- has_null_amount: true only if customer has an order with NULL amount, false otherwise including no-order customers

SELECT 
c. customer_id, 
c.name as customer_name, 
COUNT(o.order_id) AS total_orders, 
COALESCE(SUM(o.amount),0) as total_spend, 
BOOL_OR(o.order_id IS NOT NULL AND o.amount IS NULL) as has_null_amount
FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;

-- Query 2 — Running total

-- All orders with a running spend total per customer
-- Columns: order_id, customer_id, amount, created_at, running_total
-- Running total must step row by row — no ties collapsing
-- NULLs contribute nothing to the running total

SELECT 
o.order_id,
c.customer_id,
o.amount,
o.created_at,
SUM(o.amount) OVER (PARTITION BY c.customer_id ORDER BY o.order_id) AS running_total
FROM orders o JOIN customers c ON o.customer_id = c.customer_id;

-- Query 3 — Deduplication

-- Use orders_dupes table (recreate it first — you know how)
-- Return one row per order_id, keeping the earliest created_at
-- Columns: all columns from orders_dupes

WITH numbered AS (
    SELECT *,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY created_at) AS rn
    FROM orders_dupes
)
SELECT * FROM numbered
WHERE rn = 1;


-- Query 4 — Highest order per customer

-- One row per customer showing their single highest value order
-- Tiebreak: earliest created_at wins
-- NULL amounts must lose to any real amount
-- Columns: customer_id, customer_name, order_id, amount, created_at

WITH numbered AS (
    SELECT 
    c.customer_id, 
    c.name as customer_name, 
    o.order_id, 
    o.amount, 
    o.created_at,
    ROW_NUMBER() OVER (PARTITION BY c.customer_id ORDER BY o.amount DESC NULLS LAST, o.created_at) AS rn
    FROM
    customers c JOIN orders o ON c.customer_id = o.customer_id
)
SELECT customer_id, customer_name, order_id, amount, created_at
FROM numbered
WHERE rn = 1;


-- Deduplication Template
-- <natural_key> is the column(s) that define duplicates (e.g. order_id) - Which column to check for duplicates
-- <tiebreaker> is the column(s) that determine which duplicate to keep (e.g. created_at with earliest wins)
-- <table_with_duplicates> is the name of the table that contains duplicates

-- WITH numbered AS (
--     SELECT *, 
--            ROW_NUMBER() OVER (PARTITION BY <natural_key> ORDER BY <tiebreaker>) AS rn
--     FROM <table_with_duplicates>
-- )
-- SELECT * FROM numbered WHERE rn = 1;