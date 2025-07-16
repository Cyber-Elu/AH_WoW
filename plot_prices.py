import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# Connexion à la base
DB_PATH = "auctions.db"
conn = sqlite3.connect(DB_PATH)

# 1. Charger les données en fusionnant avec le nom de l'objet
query = """
SELECT 
    a.item_id,
    i.item_name,
    a.unit_price,
    a.buyout,
    a.scraped_at
FROM auctions a
JOIN items i ON i.item_id = a.item_id
WHERE a.unit_price IS NOT NULL
ORDER BY a.scraped_at ASC
"""

df = pd.read_sql_query(query, conn)
conn.close()

# 2. Convertir les dates en datetime
df['scraped_at'] = pd.to_datetime(df['scraped_at'])

# 3. Grouper les items à afficher (exemple : 1 seul ou top N)
items = df['item_name'].value_counts().head(5).index.tolist()

# 4. Afficher les graphes pour ces items
for item in items:
    sub_df = df[df['item_name'] == item]
    plt.figure(figsize=(10, 5))
    plt.plot(sub_df['scraped_at'], sub_df['unit_price'], marker='o', label='Prix unitaire')
    if sub_df['buyout'].notnull().any():
        plt.plot(sub_df['scraped_at'], sub_df['buyout'], marker='x', label='Prix achat immédiat')

    plt.title(f"Évolution du prix - {item}")
    plt.xlabel("Date")
    plt.ylabel("Prix (cuivre)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
