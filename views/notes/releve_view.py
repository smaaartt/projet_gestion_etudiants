import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from services.releve_service import generer_releve_pdf
import sqlite3

class ReleveView:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.setup_ui()

    def setup_ui(self):
        # ----- FILTRES -----
        filter_frame = tk.Frame(self.frame, bg="white")
        filter_frame.pack(fill="x", padx=10, pady=10)

        # Choix de l'étudiant
        tk.Label(filter_frame, text="Étudiant :").pack(side="left", padx=5)
        self.etudiant_var = tk.StringVar()
        self.combo_etudiant = ttk.Combobox(filter_frame, textvariable=self.etudiant_var, width=40)
        self.combo_etudiant.pack(side="left", padx=5)

        # Bouton génération PDF
        tk.Button(filter_frame, text="Générer relevé PDF", bg="#3498db", fg="white",
                  command=self.generer_pdf).pack(side="left", padx=10)

        # Charger la liste des étudiants
        self.charger_etudiants()

    def charger_etudiants(self):
        conn = sqlite3.connect("gestion_etudiants.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, prenom FROM etudiants ORDER BY nom")
        etudiants = [f"{row[0]} - {row[1]} {row[2]}" for row in cursor.fetchall()]
        self.combo_etudiant['values'] = etudiants
        if etudiants:
            self.combo_etudiant.set(etudiants[0])
        conn.close()

    def generer_pdf(self):
        etudiant_sel = self.etudiant_var.get()
        if not etudiant_sel:
            messagebox.showwarning("Attention", "Veuillez sélectionner un étudiant.")
            return

        etu_id = int(etudiant_sel.split(" - ")[0])

        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not path:
            return

        ok, msg = generer_releve_pdf(etu_id, path)
        messagebox.showinfo("Relevé", msg) if ok else messagebox.showerror("Erreur", msg)
