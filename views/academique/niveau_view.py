import tkinter as tk
from tkinter import ttk
from services.academique_service import recuperer_niveaux

class NiveauView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self, text="🎓 Gestion des Niveaux Académiques", 
                 font=("Arial", 14, "bold"), bg="white").pack(pady=20)

        # Tableau des niveaux
        columns = ("ID", "Code", "Nom Long")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Code", text="Code (ex: L1)")
        self.tree.heading("Nom Long", text="Libellé complet")
        
        self.tree.column("ID", width=50)
        self.tree.pack(fill="y", expand=True, padx=20, pady=10)
        
        self.charger_donnees()

    def charger_donnees(self):
        for n in recuperer_niveaux():
            self.tree.insert("", "end", values=(n['id'], n['code'], n['nom']))