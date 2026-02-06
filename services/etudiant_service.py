import sqlite3
import os

def obtenir_premier_etudiant():
    # On définit le chemin absolu vers la racine
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'gestion_etudiants.db')
    
    print(f"DEBUG: Tentative de lecture de la base ici : {db_path}")

    if not os.path.exists(db_path):
        print("DEBUG: ERREUR - Le fichier .db n'existe pas à cet endroit !")
        return None

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM etudiants LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = dict(row)
            print(f"DEBUG: Étudiant trouvé : {data['nom']} {data['prenom']}")
            return data
        else:
            print("DEBUG: La table 'etudiants' est vide !")
            return None
    except Exception as e:
        print(f"DEBUG: Erreur SQL : {e}")
        return None