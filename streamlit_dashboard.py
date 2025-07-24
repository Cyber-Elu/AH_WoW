import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os
import altair as alt

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def format_price(copper):
    gold = copper // 10000
    silver = (copper % 10000) // 100
    copper = copper % 100
    return f"{gold} PO {silver} PA {copper} PC"

st.title("📈 Suivi des prix - Hôtel des ventes")

# Connexion + sélection d’objet
conn = get_db_connection()
item_df = pd.read_sql("SELECT DISTINCT item_id, name FROM items ORDER BY name", conn)
selected_name = st.selectbox("Choisissez un objet :", item_df['name'])
selected_id = item_df.loc[item_df['name'] == selected_name, 'item_id'].iat[0]

# Récupération des enchères
query = f"""
SELECT created_at, unit_price, buyout_price
FROM auctions
WHERE item_id = {selected_id}
ORDER BY created_at ASC
"""
df = pd.read_sql(query, conn)
conn.close()

if df.empty:
    st.warning("Aucune donnée trouvée pour cet objet.")
    st.stop()

# On ne garde que le prix unitaire (ou le buyout si unitaire = 0)
df['price'] = df['unit_price'].where(df['unit_price'] > 0, df['buyout_price'])

# Conversion datetime + extraction de la date
df['created_at'] = pd.to_datetime(df['created_at'])
df['date'] = df['created_at'].dt.date

# Agrégations par jour
daily = (
    df
    .groupby('date')['price']
    .agg(mean_price='mean', min_price='min', max_price='max')
    .reset_index()
)

# Ajout d'un slider pour définir le seuil de filtrage
threshold = st.slider("Seuil de filtrage des prix (en pourcentage de la moyenne)", 0, 100, 30)

# Calcul des seuils pour filtrer les outliers
threshold_factor = threshold / 100
daily['min_threshold'] = daily['mean_price'] * (1 - threshold_factor)
daily['max_threshold'] = daily['mean_price'] * (1 + threshold_factor)

# Remplacement des valeurs extrêmes par NaN
daily.loc[daily['min_price'] < daily['min_threshold'], 'min_price'] = None
daily.loc[daily['max_price'] > daily['max_threshold'], 'max_price'] = None

# On convertit en “PO” pour l’axe Y (optionnel)
daily['mean_po'] = daily['mean_price'] / 10000
daily['min_po'] = daily['min_price'] / 10000
daily['max_po'] = daily['max_price'] / 10000

# Construction du graphique Altair
base = alt.Chart(daily).encode(
    x=alt.X('date:T', title='Date')
)

mean_line = base.mark_line(color='#1f77b4', strokeWidth=2).encode(
    y=alt.Y('mean_po:Q', title='Prix moyen (PO)')
)

min_points = base.mark_point(color='green', size=60, shape='triangle-down').encode(
    y='min_po:Q',
    tooltip=[
        alt.Tooltip('date:T', title='Date'),
        alt.Tooltip('min_po:Q', title='Prix min (PO)', format='.2f')
    ]
)

max_points = base.mark_point(color='red', size=60, shape='triangle-up').encode(
    y='max_po:Q',
    tooltip=[
        alt.Tooltip('date:T', title='Date'),
        alt.Tooltip('max_po:Q', title='Prix max (PO)', format='.2f')
    ]
)

chart = (mean_line + min_points + max_points).properties(
    width=700,
    height=400,
    title="Évolution quotidienne du prix (moyenne + min / max)"
).interactive()

st.altair_chart(chart, use_container_width=True)

# Affichage du dernier prix enregistré
last_row = df.sort_values('created_at').iloc[-1]
st.success(f"Dernier prix relevé ({last_row['created_at']}): **{format_price(int(last_row['price']))}**")
