import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load env
load_dotenv()
HOST = os.getenv('DB_HOST')
USER = os.getenv('DB_USER')
PWD = os.getenv('DB_PASSWORD')
DB = os.getenv('DB_NAME')

# SQL Alchemy engine
engine = create_engine(f'mysql+pymysql://{USER}:{PWD}@{HOST}/{DB}')

@st.cache_data
def load_data():
    return pd.read_sql("""
        SELECT dp.date, dp.item_id, i.name as item_name, dp.avg_price, dp.total_available
        FROM item_daily_prices dp
        JOIN items i ON i.item_id = dp.item_id
        ORDER BY item_name, dp.date
    """, engine)

st.title("WoW Auction House - Item Price Dashboard")

df = load_data()
items = df['item_name'].unique()
selected_item = st.selectbox("Select Item", items)

item_data = df[df['item_name'] == selected_item].sort_values('date')

st.subheader(f"Price and Availability for {selected_item}")

st.line_chart(item_data.set_index('date')[['avg_price']], y_label="Average Price")
st.line_chart(item_data.set_index('date')[['total_available']], y_label="Total Available")
