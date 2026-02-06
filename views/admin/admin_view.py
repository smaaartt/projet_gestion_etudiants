import tkinter as tk
from tkinter import ttk, messagebox
from services.admin_service import recuperer_tous_utilisateurs, changer_statut_utilisateur, creer_utilisateur

class AdminView:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.frame, text="Gestion des Utilisateurs & Sécurité", 
                 font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        # --- SECTION : TABLEAU DES UTILISATEURS ---
        table_frame = tk.LabelFrame(self.frame, text=" Liste des Comptes ", padx=10, pady=10, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("id", "username", "role", "statut", "nom")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Identifiant")
        self.tree.heading("role", text="Rôle")
        self.tree.heading("statut", text="Statut")
        self.tree.heading("nom", text="Nom Complet")

        self.tree.column("id", width=30)
        self.tree.pack(fill="both", expand=True)

        # Boutons d'action sous le tableau
        btn_frame = tk.Frame(table_frame, bg="white")
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="Activer / Désactiver", bg="#f39c12", fg="white", 
                  command=self.basculer_statut).pack(side="left", padx=5)

        self.charger_donnees()

        # --- SECTION : CRÉATION DE COMPTE ---
        form_frame = tk.LabelFrame(self.frame, text=" Créer un nouvel utilisateur ", padx=10, pady=10, bg="white")
        form_frame.pack(fill="x", padx=20, pady=10)

        # Champs du formulaire (simplifiés pour l'exemple)
        tk.Label(form_frame, text="User:", bg="white").grid(row=0, column=0)
        self.entry_user = tk.Entry(form_frame)
        self.entry_user.grid(row=0, column=1, padx=5)

        tk.Label(form_frame, text="Pass:", bg="white").grid(row=0, column=2)
        self.entry_pass = tk.Entry(form_frame, show="*")
        self.entry_pass.grid(row=0, column=3, padx=5)

        tk.Label(form_frame, text="Rôle:", bg="white").grid(row=0, column=4)
        self.combo_role = ttk.Combobox(form_frame, values=["Administrateur", "Enseignant", "Secrétariat"])
        self.combo_role.grid(row=0, column=5, padx=5)

        tk.Button(form_frame, text="Créer le compte", bg="#27ae60", fg="white", 
                  command=self.ajouter_utilisateur).grid(row=0, column=6, padx=10)

    def charger_donnees(self):
        # Vide le tableau
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Remplit avec les données de la base
        for user in recuperer_tous_utilisateurs():
            # user = (id, username, role, statut, nom, prenom)
            nom_complet = f"{user[4]} {user[5]}"
            self.tree.insert("", "end", values=(user[0], user[1], user[2], user[3], nom_complet))

    def ajouter_utilisateur(self):
        u, p, r = self.entry_user.get(), self.entry_pass.get(), self.combo_role.get()
        if u and p and r:
            success, msg = creer_utilisateur(u, p, r, "Nouveau", "Utilisateur")
            if success:
                messagebox.showinfo("Succès", msg)
                self.charger_donnees()
            else:
                messagebox.showerror("Erreur", msg)
        else:
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs")

    def basculer_statut(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected)
        user_id = item['values'][0]
        statut_actuel = item['values'][3]
        
        nouveau = "inactif" if statut_actuel == "actif" else "actif"
        changer_statut_utilisateur(user_id, nouveau)
        self.charger_donnees()