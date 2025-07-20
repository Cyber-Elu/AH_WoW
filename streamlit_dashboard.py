import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

# Connexion BDD
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Formatage du prix
def format_price(copper):
    gold = copper // 10000
    silver = (copper % 10000) // 100
    copper = copper % 100
    return f"{gold} PO {silver} PA {copper} PC"

# Titre
st.title("📈 Suivi des prix - Hôtel des ventes")

# Sélection de l'objet
conn = get_db_connection()
item_df = pd.read_sql("SELECT DISTINCT item_id, name FROM items ORDER BY name", conn)
selected_name = st.selectbox("Choisissez un objet :", item_df['name'])

# Récupérer l’item_id
selected_id = item_df[item_df['name'] == selected_name]['item_id'].values[0]

# Récupération des enchères associées
query = f"""
SELECT created_at, unit_price, buyout_price
FROM auctions
WHERE item_id = {selected_id}
ORDER BY created_at ASC
"""
df = pd.read_sql(query, conn)
conn.close()

# Ajouter une colonne de prix à afficher (commodities = unit_price)
df['price'] = df['unit_price'].where(df['unit_price'] > 0, df['buyout_price'])
df['price_po'] = df['price'] / 10000

if df.empty:
    st.warning("Aucune donnée trouvée pour cet objet.")
else:
    st.line_chart(df.set_index('created_at')['price_po'])
    latest = df.iloc[-1]['price']
    st.success(f"Dernier prix : **{format_price(latest)}**")
