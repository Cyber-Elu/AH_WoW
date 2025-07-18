from dotenv import load_dotenv
import os
import pymysql
import pymysql.cursors
import datetime

# Load .env variables
load_dotenv()

# Database connection
conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    db=os.getenv('DB_NAME'),
    cursorclass=pymysql.cursors.DictCursor
)

today = datetime.date.today()

query = """
INSERT INTO item_daily_prices (item_id, date, avg_price, total_available)
SELECT
    a.item_id,
    %s as date,
    AVG(a.price) as avg_price,
    SUM(a.quantity) as total_available
FROM auctions a
GROUP BY a.item_id
ON DUPLICATE KEY UPDATE avg_price=VALUES(avg_price), total_available=VALUES(total_available);
"""

with conn.cursor() as cur:
    cur.execute(query, (today,))
    conn.commit()
conn.close()
