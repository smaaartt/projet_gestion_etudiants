import tkinter as tk
from tkinter import ttk, messagebox
# Import direct du service (on vérifie que le chemin est bon)
from services.academique_service import ajouter_filiere, recuperer_filieres

class FiliereView(tk.Frame):
    def __init__(self, parent):
        # On s'assure que le parent est bien le cadre de MainWindow
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
        self.setup_ui()

    def setup_ui(self):
        # Titre pour confirmer que la vue est chargée
        tk.Label(self, text="Gestion des Filières", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        # --- Formulaire d'ajout ---
        form_frame = tk.LabelFrame(self, text="Nouvelle Filière", bg="white")
        form_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(form_frame, text="Code :", bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.ent_code = tk.Entry(form_frame)
        self.ent_code.grid(row=0, column=1, padx=5)

        tk.Label(form_frame, text="Nom :", bg="white").grid(row=0, column=2, padx=5)
        self.ent_nom = tk.Entry(form_frame)
        self.ent_nom.grid(row=0, column=3, padx=5)

        tk.Button(form_frame, text="Ajouter", command=self.valider_ajout, bg="#2ecc71", fg="white").grid(row=0, column=4, padx=10)

        # --- Tableau des filières (Treeview) ---
        # On définit les colonnes
        self.tree = ttk.Treeview(self, columns=("ID", "Code", "Nom", "Description"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Code", text="Code")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Description", text="Description")
        
        # Réglage de la largeur des colonnes
        self.tree.column("ID", width=50)
        self.tree.column("Code", width=100)
        self.tree.column("Nom", width=300)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Chargement initial des données
        self.actualiser_liste()

    def valider_ajout(self):
        code = self.ent_code.get()
        nom = self.ent_nom.get()
        if code and nom:
            success, msg = ajouter_filiere(code, nom, "")
            if success:
                messagebox.showinfo("Succès", msg)
                self.ent_code.delete(0, tk.END)
                self.ent_nom.delete(0, tk.END)
                self.actualiser_liste()
            else:
                messagebox.showerror("Erreur", msg)
        else:
            messagebox.showwarning("Champs requis", "Veuillez remplir le code et le nom.")

    def actualiser_liste(self):
        # 1. Nettoyage
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 2. Récupération des données via le service
        filieres = recuperer_filieres()
        
        # 3. Insertion
        if filieres:
            for f in filieres:
                desc = f['description'] if f['description'] else "" 
                self.tree.insert("", "end", values=(f['id'], f['code'], f['nom'], desc))
        else:
            print("Debug : Aucune filière trouvée dans la base de données.")