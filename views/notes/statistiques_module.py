import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import os

DB = "gestion_etudiants.db"
LOGO_PATH = "assets/logo.png"

class StatistiquesDashboard:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.stats = {}
        self.figure = None
        self.canvas = None
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.frame, text="TABLEAU DE BORD STATISTIQUES", font=("Arial", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=10)

        # --- FILTRES ---
        filter_frame = tk.LabelFrame(self.frame, text="Filtres", bg="white")
        filter_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(filter_frame, text="Filière :").grid(row=0, column=0, padx=5, pady=5)
        self.combo_filiere = ttk.Combobox(filter_frame, state="readonly")
        self.combo_filiere.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Niveau :").grid(row=0, column=2, padx=5, pady=5)
        self.combo_niveau = ttk.Combobox(filter_frame, state="readonly")
        self.combo_niveau.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(filter_frame, text="Actualiser", bg="#3498db", fg="white", command=self.calculer_stats).grid(row=0, column=4, padx=10)

        # --- INDICATEURS CLÉS ---
        self.tree = ttk.Treeview(self.frame, columns=("indicateur", "valeur"), show="headings", height=8)
        self.tree.heading("indicateur", text="Indicateur")
        self.tree.heading("valeur", text="Valeur")
        self.tree.column("indicateur", width=250)
        self.tree.column("valeur", width=150, anchor="center")
        self.tree.pack(fill="x", padx=20, pady=10)

        # --- ZONE GRAPHIQUE ---
        self.graph_frame = tk.Frame(self.frame, bg="white")
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # --- BOUTONS EXPORT ---
        btn_frame = tk.Frame(self.frame, bg="white")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Exporter Excel", bg="#2ecc71", fg="white", command=self.export_excel).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Exporter PDF", bg="#e74c3c", fg="white", command=self.export_pdf).pack(side="left", padx=5)

        self.charger_filtres()

    def charger_filtres(self):
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        # Filières
        cursor.execute("SELECT nom FROM filieres")
        filieres = ["Tous"] + [row[0] for row in cursor.fetchall()]
        self.combo_filiere['values'] = filieres
        self.combo_filiere.set("Tous")

        # Niveaux
        cursor.execute("SELECT nom FROM niveaux")
        niveaux = ["Tous"] + [row[0] for row in cursor.fetchall()]
        self.combo_niveau['values'] = niveaux
        self.combo_niveau.set("Tous")

        conn.close()

    def calculer_stats(self):
        filiere = self.combo_filiere.get()
        niveau = self.combo_niveau.get()

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        query = """
            SELECT n.note
            FROM notes n
            JOIN inscriptions i ON n.etudiant_id = i.etudiant_id
            JOIN modules m ON n.module_id = m.id
            JOIN filieres f ON i.filiere_id = f.id
            JOIN niveaux l ON i.niveau_id = l.id
            WHERE 1=1
        """
        params = []
        if filiere != "Tous":
            query += " AND f.nom=?"
            params.append(filiere)
        if niveau != "Tous":
            query += " AND l.nom=?"
            params.append(niveau)

        cursor.execute(query, tuple(params))
        notes = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not notes:
            messagebox.showinfo("Statistiques", "Aucune donnée pour ces filtres.")
            return

        # Calcul des indicateurs
        taux_reussite = len([n for n in notes if n >= 10]) / len(notes) * 100
        moyenne = sum(notes)/len(notes)
        min_note = min(notes)
        max_note = max(notes)
        distribution = {
            "0-9": len([n for n in notes if n < 10]),
            "10-12": len([n for n in notes if 10 <= n < 12]),
            "12-14": len([n for n in notes if 12 <= n < 14]),
            "14-16": len([n for n in notes if 14 <= n < 16]),
            "16-20": len([n for n in notes if n >= 16])
        }

        self.stats = {
            "Taux de réussite (%)": round(taux_reussite, 2),
            "Moyenne générale": round(moyenne, 2),
            "Note minimale": min_note,
            "Note maximale": max_note,
            **distribution
        }

        # Affichage tableau
        for item in self.tree.get_children():
            self.tree.delete(item)
        for k, v in self.stats.items():
            self.tree.insert("", "end", values=(k, v))

        # --- Graphique intégré ---
        if self.figure:
            self.figure.clf()
            self.canvas.get_tk_widget().destroy()

        self.figure = plt.Figure(figsize=(6,3), dpi=100)
        ax = self.figure.add_subplot(111)
        ax.bar(distribution.keys(), distribution.values(), color="#3498db")
        ax.set_title("Distribution des notes")
        ax.set_xlabel("Intervalle")
        ax.set_ylabel("Nombre d'étudiants")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def export_excel(self):
        if not self.stats:
            messagebox.showwarning("Attention", "Calculez les statistiques avant d'exporter.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if path:
            df = pd.DataFrame(list(self.stats.items()), columns=["Indicateur", "Valeur"])
            df.to_excel(path, index=False)
            messagebox.showinfo("Export", f"Statistiques exportées en Excel : {path}")

    def export_pdf(self):
        if not self.stats:
            messagebox.showwarning("Attention", "Calculez les statistiques avant d'exporter.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if path:
            pdf = FPDF()
            pdf.add_page()
            if os.path.exists(LOGO_PATH):
                pdf.image(LOGO_PATH, x=10, y=8, w=30)
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Rapport Statistiques", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", "", 12)
            for k, v in self.stats.items():
                pdf.cell(0, 10, f"{k} : {v}", ln=True)
            pdf.output(path)
            messagebox.showinfo("Export", f"Statistiques exportées en PDF : {path}")
