import tkinter as tk
from tkinter import ttk, messagebox
from services.academique_service import recuperer_modules, ajouter_module, recuperer_filieres

class ModuleView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self, text="Gestion des Modules (Matières)", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        # --- Formulaire ---
        form = tk.LabelFrame(self, text="Nouveau Module", bg="white")
        form.pack(pady=10, padx=10, fill="x")

        tk.Label(form, text="Code:", bg="white").grid(row=0, column=0, padx=5)
        self.ent_code = tk.Entry(form, width=10)
        self.ent_code.grid(row=0, column=1)

        tk.Label(form, text="Nom:", bg="white").grid(row=0, column=2, padx=5)
        self.ent_nom = tk.Entry(form, width=20)
        self.ent_nom.grid(row=0, column=3)

        tk.Label(form, text="Coeff:", bg="white").grid(row=0, column=4, padx=5)
        self.ent_coeff = tk.Entry(form, width=5)
        self.ent_coeff.grid(row=0, column=5)

        tk.Button(form, text="Ajouter", command=self.valider, bg="#2ecc71", fg="white").grid(row=0, column=6, padx=10)

        # --- Tableau ---
        self.tree = ttk.Treeview(self, columns=("ID", "Code", "Nom", "Coeff", "Filière"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Code", text="Code")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Coeff", text="Coeff")
        self.tree.heading("Filière", text="Filière")
        
        for col in ("ID", "Coeff"): self.tree.column(col, width=50)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.actualiser()

    def actualiser(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for m in recuperer_modules():
            self.tree.insert("", "end", values=(m['id'], m['code'], m['nom'], m['coefficient'], m['filiere_nom']))

    def valider(self):
        code, nom, coeff = self.ent_code.get(), self.ent_nom.get(), self.ent_coeff.get()
        if code and nom and coeff:
            success, msg = ajouter_module(code, nom, coeff, 6, 1) # 6 crédits et filière 1 par défaut pour le test
            if success:
                messagebox.showinfo("Succès", msg)
                self.actualiser()
            else: messagebox.showerror("Erreur", msg)