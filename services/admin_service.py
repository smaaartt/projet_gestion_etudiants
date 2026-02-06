import sqlite3
import os
import hashlib

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'gestion_etudiants.db')

def recuperer_tous_utilisateurs():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, statut, nom, prenom FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def changer_statut_utilisateur(user_id, nouveau_statut):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET statut = ? WHERE id = ?", (nouveau_statut, user_id))
    conn.commit()
    conn.close()

def creer_utilisateur(username, password, role, nom, prenom):
    # Hashage du mot de passe pour la sécurité (SHA-256)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, statut, nom, prenom)
            VALUES (?, ?, ?, 'actif', ?, ?)
        """, (username, password_hash, role, nom, prenom))
        conn.commit()
        return True, "Utilisateur créé avec succès"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()