import sqlite3
import csv
import pandas as pd
import os
import pandas as pd
from fpdf import FPDF

# Chemin dynamique vers la base à la racine
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'gestion_etudiants.db')

def importer_csv(file_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    ajoutes = 0
    doublons = 0

    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Vérification du matricule pour éviter les doublons
                cursor.execute("SELECT matricule FROM etudiants WHERE matricule=?", (row['matricule'],))
                if cursor.fetchone():
                    doublons += 1
                else:
                    cursor.execute("""
                        INSERT INTO etudiants (matricule, nom, prenom, email, telephone, date_inscription)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (row['matricule'], row['nom'], row['prenom'], row['email'], row['telephone'], row.get('date_inscription', '2024-01-01')))
                    ajoutes += 1
        conn.commit()
        return True, f"Import terminé : {ajoutes} ajoutés, {doublons} doublons ignorés."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def exporter_excel(dest_path):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM etudiants", conn)
        df.to_excel(dest_path, index=False)
        conn.close()
        return True, "Fichier Excel généré avec succès !"
    except Exception as e:
        return False, str(e)
    
def exporter_classement_excel(classement, path):
    try:
        df = pd.DataFrame(classement)
        df.to_excel(path, index=False)
        return True, "Classement exporté en Excel avec succès."
    except Exception as e:
        return False, str(e)
    
def exporter_classement_pdf(classement, path):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        pdf.cell(0, 10, "Classement des étudiants", ln=True)

        for e in classement:
            ligne = (
                f"{e['rang']} - {e['nom']} {e['prenom']} | "
                f"Moyenne : {e['moyenne']} | Mention : {e['mention']}"
            )
            pdf.multi_cell(0, 8, ligne)

        pdf.output(path)
        return True, "Classement exporté en PDF avec succès."
    except Exception as e:
        return False, str(e)
