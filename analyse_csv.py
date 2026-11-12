
import pandas as pd

# Charger le fichier CSV
df = pd.read_csv("givaudan_sales_dataset.csv")

# Afficher les dimensions du dataset
print("Dimensions :", df.shape)

# Afficher les noms des colonnes
print("\nColonnes :")
print(df.columns.tolist())

# Afficher les 5 premières lignes
print("\nAperçu du dataset :")
print(df.head())

# Afficher les informations sur les colonnes
print("\nInformations générales :")
df.info()
