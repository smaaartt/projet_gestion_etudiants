import tkinter as tk
from tkinter import ttk, messagebox
from services.academique_service import (
    obtenir_enseignants, 
    obtenir_modules, 
    attribuer_enseignant_module,
    recuperer_affectations_detaillees,
    supprimer_affectation
)

class AttributionProfView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
        # Chargement des données initiales
        self.profs = obtenir_enseignants()
        self.modules = obtenir_modules()
        self.setup_ui()

    def setup_ui(self):
        # --- TITRE ---
        tk.Label(self, text="Attribution des Enseignants aux Modules", 
                 font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        # --- FORMULAIRE (Partie Haute) ---
        form = tk.LabelFrame(self, text="Nouvelle Affectation", bg="white", padx=10, pady=10)
        form.pack(fill="x", padx=20, pady=10)

        tk.Label(form, text="Enseignant :", bg="white").grid(row=0, column=0, sticky="w")
        self.combo_prof = ttk.Combobox(form, values=[f"{p['nom']} {p['prenom']}" for p in self.profs], width=30)
        self.combo_prof.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Module :", bg="white").grid(row=1, column=0, sticky="w")
        self.combo_module = ttk.Combobox(form, values=[m['nom'] for m in self.modules], width=30)
        self.combo_module.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="Groupe :", bg="white").grid(row=0, column=2, padx=(20, 5))
        self.ent_groupe = tk.Entry(form, width=10)
        self.ent_groupe.insert(0, "G1")
        self.ent_groupe.grid(row=0, column=3)

        tk.Label(form, text="Année :", bg="white").grid(row=1, column=2, padx=(20, 5))
        self.ent_annee = tk.Entry(form, width=15)
        self.ent_annee.insert(0, "2025-2026")
        self.ent_annee.grid(row=1, column=3)

        tk.Button(form, text="Confirmer l'affectation", bg="#2980b9", fg="white", 
                  command=self.valider_affectation, font=("Arial", 9, "bold")).grid(row=0, column=4, rowspan=2, padx=20)

        # --- TABLEAU DE VISUALISATION (Partie Basse) ---
        tk.Label(self, text="Affectations enregistrées (Table 11)", 
                 font=("Arial", 11, "bold"), bg="white").pack(pady=(10, 0))

        # Configuration du tableau
        columns = ("ID", "Prof", "Module", "Groupe", "Année")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        
        # En-têtes centrés
        self.tree.heading("ID", text="ID")
        self.tree.heading("Prof", text="Enseignant")
        self.tree.heading("Module", text="Module")
        self.tree.heading("Groupe", text="Groupe")
        self.tree.heading("Année", text="Année Académique")

        # Design des colonnes
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Prof", width=200, anchor="center")
        self.tree.column("Module", width=200, anchor="center")
        self.tree.column("Groupe", width=80, anchor="center")
        self.tree.column("Année", width=120, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=20, pady=5)

        # Bouton de suppression
        tk.Button(self, text="Supprimer l'affectation sélectionnée", bg="#e74c3c", fg="white", 
                  command=self.supprimer_selection).pack(pady=10)

        self.charger_affectations()

    def charger_affectations(self):
        """Remplit le tableau avec les données de la Table 11"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in recuperer_affectations_detaillees():
            self.tree.insert("", "end", values=(row['id'], row['prof'], row['module'], row['groupe'], row['annee_academique']))

    def valider_affectation(self):
        p_idx = self.combo_prof.current()
        m_idx = self.combo_module.current()
        grp = self.ent_groupe.get()
        ann = self.ent_annee.get()

        if p_idx != -1 and m_idx != -1 and grp:
            success, msg = attribuer_enseignant_module(self.profs[p_idx]['id'], self.modules[m_idx]['id'], grp, ann)
            if success:
                messagebox.showinfo("Succès", msg)
                self.charger_affectations() # Mise à jour auto du tableau
            else:
                messagebox.showerror("Erreur", msg)
        else:
            messagebox.showwarning("Incomplet", "Veuillez remplir tous les champs.")

    def supprimer_selection(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez une ligne à supprimer.")
            return
        
        id_aff = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirmation", f"Supprimer l'affectation ID {id_aff} ?"):
            if supprimer_affectation(id_aff):
                messagebox.showinfo("OK", "Affectation supprimée.")
                self.charger_affectations()