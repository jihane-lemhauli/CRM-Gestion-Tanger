import sqlite3
import mysql.connector

# Connexion MySQL (Local)
mysql_conn = mysql.connector.connect(host="localhost", user="root", password="jihanejiji", database="GestionClients_Tanger")
mysql_cursor = mysql_conn.cursor()

# Création SQLite (Fichier)
sqlite_conn = sqlite3.connect('database.db')
sqlite_cursor = sqlite_conn.cursor()

# Création de la table Clients dans SQLite
sqlite_cursor.execute("""
CREATE TABLE IF NOT EXISTS Clients (
    id_client INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_client TEXT, telephone TEXT, email TEXT, type_client TEXT, adresse TEXT
)
""")


mysql_cursor.execute("SELECT nom_client, telephone, email, type_client, adresse FROM Clients")
for row in mysql_cursor.fetchall():
    sqlite_cursor.execute("INSERT INTO Clients (nom_client, telephone, email, type_client, adresse) VALUES (?,?,?,?,?)", row)

sqlite_conn.commit()
print("✅ Fichier database.db créé avec succès !")