from dotenv import load_dotenv
import os
import pymysql
import pymysql.cursors
import datetime

# Load .env
load_dotenv()

# DB connection
conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    db=os.getenv('DB_NAME'),
    cursorclass=pymysql.cursors.DictCursor
)

# Replace with the day you want to analyze
today = datetime.date.today()

# Aggregate price and total_available (using buyout_price)
query = """
INSERT INTO item_daily_prices (item_id, date, avg_price, total_available)
SELECT
    item_id,
    %s as date,
    AVG(buyout_price) as avg_price,
    SUM(quantity) as total_available
FROM auctions
WHERE DATE(created_at) = %s
GROUP BY item_id
ON DUPLICATE KEY UPDATE avg_price=VALUES(avg_price), total_available=VALUES(total_available);
"""

with conn.cursor() as cur:
    cur.execute(query, (today, today))
    conn.commit()
conn.close()
