import sqlite3
import pandas as pd
from fpdf import FPDF

DB = "gestion_etudiants.db"

def calculer_classement(filiere=None, niveau=None, groupe=None):
    """
    Retourne le classement des étudiants filtré par filière, niveau et groupe.
    Si un filtre est None ou 'Tous', il n'est pas appliqué.
    """
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    query = """
        SELECT 
            e.id,
            e.nom,
            e.prenom,
            SUM(n.note * n.coefficient) / SUM(n.coefficient) AS moyenne,
            i.groupe
        FROM etudiants e
        JOIN notes n ON n.etudiant_id = e.id
        JOIN inscriptions i ON i.etudiant_id = e.id
        WHERE 1=1
    """
    params = []

    if filiere and filiere != "Tous":
        query += " AND i.filiere_id = ?"
        params.append(filiere)

    if niveau and niveau != "Tous":
        query += " AND i.niveau_id = ?"
        params.append(niveau)

    if groupe and groupe != "Tous":
        query += " AND i.groupe = ?"
        params.append(groupe)

    query += """
        GROUP BY e.id
        ORDER BY moyenne DESC
    """

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    classement = []
    rang = 1
    for r in rows:
        classement.append({
            "rang": rang,
            "nom": r[1],
            "prenom": r[2],
            "moyenne": round(r[3], 2),
            "mention": calculer_mention(r[3]),
            "groupe": r[4]
        })
        rang += 1

    return classement


def calculer_mention(moyenne):
    if moyenne >= 16:
        return "Très Bien"
    elif moyenne >= 14:
        return "Bien"
    elif moyenne >= 12:
        return "Assez Bien"
    elif moyenne >= 10:
        return "Passable"
    return "Ajourné"

def exporter_excel(classement, path):
    df = pd.DataFrame(classement)
    df.to_excel(path, index=False)

def exporter_pdf(classement, path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    for e in classement:
        ligne = f"{e['rang']} - {e['nom']} {e['prenom']} ({e['groupe']}) : {e['moyenne']} ({e['mention']})"
        pdf.cell(0, 10, ligne, ln=True)
    pdf.output(path)
