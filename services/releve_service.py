import sqlite3
from fpdf import FPDF
from datetime import datetime
import os

DB = "gestion_etudiants.db"
LOGO_PATH = "assets/logo.png"

def generer_releve_pdf(etudiant_id, path):
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        # Infos étudiant
        cursor.execute("SELECT nom, prenom FROM etudiants WHERE id=?", (etudiant_id,))
        etu = cursor.fetchone()
        if not etu:
            return False, "Étudiant introuvable"
        nom, prenom = etu

        # Notes et modules
        cursor.execute("""
            SELECT m.nom, n.note, n.coefficient, m.credits
            FROM notes n
            JOIN modules m ON n.module_id = m.id
            WHERE n.etudiant_id=?
        """, (etudiant_id,))
        notes = cursor.fetchall()
        conn.close()

        pdf = FPDF()
        pdf.add_page()

        # ----- Logo -----
        if os.path.exists(LOGO_PATH):
            pdf.image(LOGO_PATH, x=10, y=8, w=30)

        # ----- Titre -----
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Relevé de Notes", ln=True, align="C")
        pdf.ln(5)

        # ----- Infos étudiant -----
        pdf.set_font("Arial", "", 12)
        pdf.ln(10)
        pdf.cell(0, 10, f"Nom : {nom}", ln=True)
        pdf.cell(0, 10, f"Prénom : {prenom}", ln=True)
        pdf.ln(5)

        # ----- Tableau de notes -----
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(70, 10, "Module", 1, 0, "C", 1)
        pdf.cell(30, 10, "Note", 1, 0, "C", 1)
        pdf.cell(30, 10, "Coef", 1, 0, "C", 1)
        pdf.cell(30, 10, "Crédits", 1, 1, "C", 1)

        pdf.set_font("Arial", "", 12)
        total_note = 0
        total_coef = 0
        for module, note, coef, credits in notes:
            pdf.cell(70, 10, module, 1)
            pdf.cell(30, 10, str(note), 1, 0, "C")
            pdf.cell(30, 10, str(coef), 1, 0, "C")
            pdf.cell(30, 10, str(credits), 1, 1, "C")
            total_note += note * coef
            total_coef += coef

        moyenne = round(total_note / total_coef, 2) if total_coef else 0
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Moyenne générale : {moyenne}", ln=True)

        # ----- Pied de page -----
        pdf.set_y(-30)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, f"Date : {datetime.today().strftime('%d/%m/%Y')}", ln=True, align="L")
        pdf.cell(0, 10, "Signature : ____________________", ln=True, align="R")

        pdf.output(path)
        return True, "Relevé PDF généré avec succès."
    except Exception as e:
        return False, str(e)
