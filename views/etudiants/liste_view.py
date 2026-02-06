import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# --- MODULE LISTE ÉTUDIANTS ---
class ListeEtudiantModule:
    def __init__(self, parent_frame, main_app):
        """
        :param parent_frame: Le cadre Tkinter où s'affiche ce module.
        :param main_app: Référence à l'instance de MainWindow pour la navigation.
        """
        self.frame = parent_frame
        self.main_app = main_app 
        self.setup_ui()

    def setup_ui(self):
        # Titre
        tk.Label(self.frame, text="RECHERCHE ET LISTE DES ÉTUDIANTS", 
                 font=("Arial", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=10)

        # --- BARRE DE RECHERCHE ---
        search_frame = tk.Frame(self.frame, bg="white")
        search_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(search_frame, text="Rechercher (Nom ou Matricule) :", bg="white").pack(side="left", padx=5)
        self.ent_search = tk.Entry(search_frame, width=30)
        self.ent_search.pack(side="left", padx=5)
        
        # Liaison de la touche "Entrée" à la recherche
        self.ent_search.bind("<Return>", lambda e: self.charger_donnees())

        tk.Button(search_frame, text="Rechercher", bg="#3498db", fg="white", 
                  command=self.charger_donnees).pack(side="left", padx=5)
        
        tk.Button(search_frame, text="Actualiser", bg="#95a5a6", fg="white", 
                  command=self.charger_donnees).pack(side="left", padx=5)

        # --- TABLEAU (TREEVIEW) ---
        table_frame = tk.Frame(self.frame, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Définition des colonnes
        colonnes = ("matricule", "nom", "prenom", "sexe", "email", "date_insc")
        self.tree = ttk.Treeview(table_frame, columns=colonnes, show="headings")

        self.tree.heading("matricule", text="Matricule")
        self.tree.heading("nom", text="Nom")
        self.tree.heading("prenom", text="Prénom")
        self.tree.heading("sexe", text="Sexe")
        self.tree.heading("email", text="Email")
        self.tree.heading("date_insc", text="Date Inscription")

        # Configuration de la taille des colonnes
        self.tree.column("matricule", width=100, anchor="center")
        self.tree.column("nom", width=150)
        self.tree.column("prenom", width=150)
        self.tree.column("sexe", width=80, anchor="center")
        self.tree.column("email", width=200)

        # Scrollbar verticale
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- ÉVÉNEMENT ---
        # Double-clic pour ouvrir la fiche détaillée
        self.tree.bind("<Double-1>", self.on_student_select)

        # Aide visuelle
        tk.Label(self.frame, text="💡 Double-cliquez sur un étudiant pour ouvrir sa fiche détaillée", 
                 font=("Arial", 9, "italic"), fg="gray", bg="white").pack(pady=5)

        # Charger les données initiales
        self.charger_donnees()

    def charger_donnees(self):
        """Récupère les données depuis la base SQLite."""
        # On vide le tableau avant de recharger
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_query = self.ent_search.get().strip()

        try:
            conn = sqlite3.connect('gestion_etudiants.db')
            cursor = conn.cursor()
            
            if search_query:
                # Recherche filtrée (Nom, Prénom ou Matricule)
                cursor.execute("""
                    SELECT matricule, nom, prenom, sexe, email, date_inscription 
                    FROM etudiants 
                    WHERE nom LIKE ? OR prenom LIKE ? OR matricule LIKE ?
                """, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
            else:
                # Tout afficher par défaut
                cursor.execute("SELECT matricule, nom, prenom, sexe, email, date_inscription FROM etudiants")
            
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur BDD", f"Impossible de charger les données : {e}")

    def on_student_select(self, event):
        """Récupère l'étudiant sélectionné et demande à MainWindow d'ouvrir sa fiche."""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        # Récupération des valeurs de la ligne cliquée
        student_data = self.tree.item(selected_item)['values']
        
        # Appel de la méthode dans MainWindow pour changer de vue
        # On passe les données au format attendu par FicheEtudiantView
        self.main_app.ouvrir_fiche_etudiant(student_data)