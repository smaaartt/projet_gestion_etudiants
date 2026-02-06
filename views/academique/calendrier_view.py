import tkinter as tk
from tkinter import ttk, messagebox
from services.academique_service import recuperer_calendrier, ajouter_evenement_calendrier

class CalendrierView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self, text="Calendrier Académique (Paramètres)", font=("Arial", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=20)

        # --- Formulaire d'ajout (Adapté à la Table 12 : parametres) ---
        form = tk.LabelFrame(self, text="Ajouter une date clé (Semestre, Examen...)", bg="white", padx=10, pady=10)
        form.pack(fill="x", padx=20, pady=10)

        tk.Label(form, text="Nom/Clé :", bg="white").grid(row=0, column=0)
        self.ent_nom = tk.Entry(form)
        self.ent_nom.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Date (AAAA-MM-JJ) :", bg="white").grid(row=0, column=2)
        self.ent_debut = tk.Entry(form) # On utilise ce champ pour la valeur de la date
        self.ent_debut.grid(row=0, column=3, padx=5)

        tk.Label(form, text="Description :", bg="white").grid(row=0, column=4)
        self.ent_description = tk.Entry(form)
        self.ent_description.grid(row=0, column=5, padx=5)

        tk.Button(form, text="Enregistrer", bg="#27ae60", fg="white", command=self.enregistrer).grid(row=0, column=6, padx=10)

        # --- Tableau d'affichage (Colonnes de la Table parametres) ---
        self.tree = ttk.Treeview(self, columns=("Clé", "Valeur", "Description"), show="headings")
        self.tree.heading("Clé", text="Paramètre")
        self.tree.heading("Valeur", text="Date enregistrée")
        self.tree.heading("Description", text="Description")
        
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.charger_donnees()

    def charger_donnees(self):
        """Affiche les données de la table parametres"""
        for item in self.tree.get_children(): self.tree.delete(item)
        for ev in recuperer_calendrier():
            # ev contient les colonnes : cle, valeur, description
            self.tree.insert("", "end", values=(ev['cle'], ev['valeur'], ev['description']))

    def enregistrer(self):
        """Envoie les 3 arguments attendus par le service"""
        nom = self.ent_nom.get()
        date_val = self.ent_debut.get()
        desc = self.ent_description.get()

        if nom and date_val:
            # On appelle ajouter_evenement_calendrier(libelle, date_valeur, description)
            success, msg = ajouter_evenement_calendrier(nom, date_val, desc)
            if success:
                messagebox.showinfo("Succès", msg)
                self.charger_donnees()
                # Nettoyage
                self.ent_nom.delete(0, tk.END)
                self.ent_debut.delete(0, tk.END)
                self.ent_description.delete(0, tk.END)
            else: 
                messagebox.showerror("Erreur", msg)
        else:
            messagebox.showwarning("Attention", "Le nom et la date sont obligatoires.")