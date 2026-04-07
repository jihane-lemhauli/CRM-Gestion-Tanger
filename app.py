import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# 1️⃣ CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="CRM Tanger Pro", layout="wide")

# ---------------------------------------------------------
# 2️⃣ CONNEXION À LA BASE DE DONNÉES (SQLite pour le Cloud)
# ---------------------------------------------------------
def obtenir_connexion():
    try:
        # Connexion au fichier local database.db
        return sqlite3.connect('database.db', check_same_thread=False)
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        return None

# -------------------------
# 3️⃣ AUTHENTIFICATION
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def check_login(username, password):
    return username == "admin" and password == "pass1234"

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🔐 Connexion au Système CRM</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        user = st.text_input("Nom d'utilisateur")
        pwd = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter", use_container_width=True):
            if check_login(user, pwd):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("⚠️ Identifiants incorrects")
    st.stop()

# -------------------------
# 4️⃣ DESIGN CSS
# -------------------------
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%); }
.carte-client {
    background: white; padding: 30px; border-radius: 15px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    border-top: 5px solid #2563eb; margin-top: 20px; color: #1e293b;
}
.titre-metric { color: #64748b; font-size: 14px; font-weight: bold; text-transform: uppercase; }
.valeur-metric { font-size: 28px; font-weight: bold; color: #1e293b; }
</style>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🏙️ CRM : Gestion des Clients - Tanger")

# ---------------------------------------------------------
# 5️⃣ CHARGER LA LISTE DES CLIENTS
# ---------------------------------------------------------
conn = obtenir_connexion()
clients_list = []
if conn:
    try:
        df_list = pd.read_sql("SELECT nom_client FROM Clients ORDER BY nom_client ASC", conn)
        clients_list = df_list['nom_client'].tolist()
    finally:
        conn.close()

# ---------------------------------------------------------
# 6️⃣ RECHERCHE ET AFFICHAGE
# ---------------------------------------------------------
st.subheader("🔍 Consultation Rapide")
nom_recherche = st.selectbox("Sélectionnez un client :", options=[""] + clients_list)

if nom_recherche != "":
    conn = obtenir_connexion()
    if conn:
        try:
            # Note: SQLite utilise '?' au lieu de '%s'
            requete = """
            SELECT c.*, 
                   COALESCE(SUM(f.montant), 0) AS total_ventes,
                   COALESCE(SUM(CASE WHEN f.statut='En attente' THEN f.montant ELSE 0 END), 0) AS montant_en_attente
            FROM Clients c
            LEFT JOIN Factures f ON c.nom_client = f.nom_client_ref
            WHERE c.nom_client = ?
            GROUP BY c.id_client;
            """
            df = pd.read_sql(requete, conn, params=(nom_recherche,))
            if not df.empty:
                ligne = df.iloc[0]
                st.markdown(f"""
                <div class="carte-client">
                    <h2 style="color: #1e3a8a;">📋 {ligne['nom_client']}</h2>
                    <div style="display: flex; gap: 40px; margin-bottom: 25px; background: #f8fafc; padding: 20px; border-radius: 10px;">
                        <div style="flex:1;">
                            <div class="titre-metric">Total facturé</div>
                            <div class="valeur-metric">{ligne['total_ventes']:,.2f} DH</div>
                        </div>
                        <div style="flex:1; border-left:2px solid #e2e8f0; padding-left:20px;">
                            <div class="titre-metric" style="color:#f59e0b;">Montant en attente</div>
                            <div class="valeur-metric" style="color:#f59e0b;">{ligne['montant_en_attente']:,.2f} DH</div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <p><b>📞 Tél :</b> {ligne['telephone']} | <b>✉️ Email :</b> {ligne['email']}</p>
                        <p><b>🏢 Type :</b> {ligne['type_client']} | <b>📍 Adresse :</b> {ligne['adresse']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        finally:
            conn.close()

st.divider()

# ---------------------------------------------------------
# 7️⃣ AJOUTER UN NOUVEAU CLIENT
# ---------------------------------------------------------
st.subheader("➕ Ajouter un nouveau client")
with st.form("form_ajout", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        new_nom = st.text_input("Nom du client")
        new_tel = st.text_input("Téléphone")
    with c2:
        new_email = st.text_input("Email")
        new_type = st.selectbox("Type", ["PME", "Particulier", "Grande Entreprise", "Commune"])
    new_adr = st.text_area("Adresse")
    
    if st.form_submit_button("Enregistrer le client"):
        if new_nom:
            conn = obtenir_connexion()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Clients (nom_client, telephone, email, type_client, adresse) VALUES (?,?,?,?,?)",
                                   (new_nom, new_tel, new_email, new_type, new_adr))
                    conn.commit()
                    st.success(f"✅ {new_nom} ajouté avec succès !")
                    st.rerun()
                except Exception as e: st.error(e)
                finally: conn.close()
        else: st.warning("Le nom est obligatoire.")

st.divider()

# ---------------------------------------------------------
# 8️⃣ MODIFIER / SUPPRIMER UN CLIENT
# ---------------------------------------------------------
st.subheader("✏️ Gérer les clients existants")
nom_cible = st.selectbox("Choisir un client à modifier/supprimer :", options=[""] + clients_list, key="edit_select")

if nom_cible != "":
    conn = obtenir_connexion()
    if conn:
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Clients WHERE nom_client = ?", (nom_cible,))
            c = cursor.fetchone()
            if c:
                with st.form("form_edit"):
                    st.info(f"Édition de : {c['nom_client']}")
                    n_nom = st.text_input("Nom", c['nom_client'])
                    n_tel = st.text_input("Tél", c['telephone'])
                    n_mail = st.text_input("Email", c['email'])
                    n_adr = st.text_input("Adresse", c['adresse'])
                    
                    col_b1, col_b2 = st.columns(2)
                    if col_b1.form_submit_button("💾 Sauvegarder"):
                        cursor.execute("UPDATE Clients SET nom_client=?, telephone=?, email=?, adresse=? WHERE id_client=?",
                                       (n_nom, n_tel, n_mail, n_adr, c['id_client']))
                        conn.commit()
                        st.success("Modifications enregistrées !")
                        st.rerun()
                    
                    if col_b2.form_submit_button("🗑️ Supprimer"):
                        cursor.execute("DELETE FROM Clients WHERE id_client=?", (c['id_client'],))
                        conn.commit()
                        st.warning("Client supprimé !")
                        st.rerun()
        finally:
            conn.close()
