import sqlite3
import pandas as pd
from fpdf import FPDF

DB = "gestion_etudiants.db"

def calculer_classement(filiere=None, niveau=None, groupe=None, annee="2023-2024"):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    query = """
        SELECT
            e.id,
            e.nom,
            e.prenom,
            i.groupe,
            SUM(n.note * n.coefficient) / SUM(n.coefficient) AS moyenne
        FROM inscriptions i
        JOIN etudiants e ON e.id = i.etudiant_id
        JOIN notes n ON n.etudiant_id = e.id
        JOIN modules m ON m.id = n.module_id
        WHERE i.annee_academique = ?
          AND n.annee_academique = ?
    """
    params = [annee, annee]

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

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    classement = []
    rang_affiche = 0
    dernier_moyenne = None

    for index, (eid, nom, prenom, grp, moyenne) in enumerate(rows, start=1):
        if moyenne != dernier_moyenne:
            rang_affiche = index
            dernier_moyenne = moyenne

        classement.append({
            "rang": rang_affiche,
            "nom": nom,
            "prenom": prenom,
            "moyenne": round(moyenne, 2),
            "mention": calculer_mention(moyenne),
            "groupe": grp
        })

    return classement


def calculer_mention(moyenne):
    if moyenne >= 16:
        return "Excellent"
    elif moyenne >= 14:
        return "Très Bien"
    elif moyenne >= 12:
        return "Bien"
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

    pdf.cell(0, 10, "CLASSEMENT DES ÉTUDIANTS", ln=True)
    pdf.ln(5)

    for e in classement:
        ligne = (
            f"Rang {e['rang']} - {e['nom']} {e['prenom']} "
            f"({e['groupe']}) : {e['moyenne']} / 20 - {e['mention']}"
        )
        pdf.multi_cell(0, 8, ligne)

    pdf.output(path)
