import tkinter as tk
from tkinter import ttk, messagebox
from views.notes.consultation_view import ConsultationNotesView
from services.absence_service import recuperer_absences_etudiant
from services.absence_service import recuperer_absences_etudiant, justifier_absence

class FicheEtudiantView:
    def __init__(self, parent_frame, etudiant_data):
        self.frame = parent_frame
        self.vars = {} 
        self.mode_edition = False
        
        # --- LOGIQUE DE CONVERSION ---
        # Si on reçoit une liste/tuple (depuis la liste_view), on la transforme en dict
        if isinstance(etudiant_data, (list, tuple)):
            self.etudiant_data = {
                'id': etudiant_data[0],
                'matricule': etudiant_data[1],
                'nom': etudiant_data[2],
                'prenom': etudiant_data[3],
                'sexe': etudiant_data[4],
                'email': etudiant_data[5],
                'date_insc': etudiant_data[6]
            }
        else:
            self.etudiant_data = etudiant_data
            
        self.setup_ui()

    def setup_ui(self):
        # Maintenant .get() fonctionnera toujours car self.etudiant_data est forcément un dict
        nom_complet = f"{self.etudiant_data.get('nom', 'NOM')} {self.etudiant_data.get('prenom', 'Prénom')}"
        
        header_frame = tk.Frame(self.frame, bg="white")
        header_frame.pack(fill="x", padx=20, pady=10)

        nom_complet = f"{self.etudiant_data.get('nom', 'NOM')} {self.etudiant_data.get('prenom', 'Prénom')}"
        tk.Label(header_frame, text=nom_complet, font=("Arial", 18, "bold"), bg="white").pack(side="left")
        
        self.btn_edit = tk.Button(header_frame, text="Modifier les informations", bg="#f39c12", fg="white",
                                  command=self.toggle_edition)
        self.btn_edit.pack(side="right")

        # --- Système d'onglets (Notebook) ---
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Création des onglets
        self.tab_perso = tk.Frame(self.notebook, bg="white", padx=10, pady=10)
        self.tab_acad = tk.Frame(self.notebook, bg="white", padx=10, pady=10)
        self.tab_notes = tk.Frame(self.notebook, bg="white", padx=10, pady=10)
        self.tab_absences = tk.Frame(self.notebook, bg="white", padx=10, pady=10)

        self.notebook.add(self.tab_perso, text="Infos Personnelles")
        self.notebook.add(self.tab_acad, text="Parcours Académique")
        self.notebook.add(self.tab_notes, text="Notes & Résultats")
        self.notebook.add(self.tab_absences, text="Absences & Assiduité")

        if self.etudiant_data and 'id' in self.etudiant_data:
            ConsultationNotesView(self.tab_notes, etudiant_id=self.etudiant_data['id'])
        else:
            tk.Label(self.tab_notes, text="Aucune donnée étudiante pour afficher les notes.", fg="red").pack(pady=20)

        self.setup_tab_perso()
        self.setup_tab_acad()
        self.setup_tab_absences()  
        self.mode_edition = False

    def setup_tab_absences(self):
        """Contenu de l'onglet Absences & Assiduité avec Bouton"""
        # 1. Création du tableau (Treeview)
        columns = ("Date", "Module", "Séance", "Justifiée")
        self.tree_absences = ttk.Treeview(self.tab_absences, columns=columns, show="headings")
        
        for col in columns:
            self.tree_absences.heading(col, text=col)
            self.tree_absences.column(col, width=150, anchor="center")
        
        self.tree_absences.pack(fill="both", expand=True, pady=10)

        # 2. AJOUT DU BOUTON (Il manquait dans ton dernier message !)
        self.btn_justifier = tk.Button(
            self.tab_absences, 
            text="✅ Justifier l'absence sélectionnée", 
            bg="#3498db", 
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.valider_justification
        )
        self.btn_justifier.pack(pady=5)

        # 3. Charger les données
        self.actualiser_tableau_absences()
        
        # --- Absences ---
    def actualiser_tableau_absences(self):
        """Vide et remplit le tableau avec les données à jour"""
        # On vide le tableau avant de recharger
        for item in self.tree_absences.get_children():
            self.tree_absences.delete(item)
            
        # On récupère l'ID depuis le dictionnaire de données
        etudiant_id = self.etudiant_data.get('id')
        
        if etudiant_id:
            absences = recuperer_absences_etudiant(etudiant_id)
            for abs in absences:
                statut = "Oui" if abs['justifiee'] == 1 else "Non"
                self.tree_absences.insert("", "end", values=(
                    abs['date_absence'], 
                    abs['module_nom'], 
                    abs['seance'], 
                    statut
                ))
        else:
            # Si pas d'ID, on affiche un message dans le tableau ou la console
            print("Erreur : Impossible de charger les absences, ID manquant.")

    def valider_justification(self):
        """Action déclenchée par le bouton Justifier"""
        selection = self.tree_absences.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une absence dans la liste.")
            return

        # On récupère les infos de la ligne sélectionnée
        item = self.tree_absences.item(selection[0])
        valeurs = item['values']
        
        date_abs = valeurs[0]
        mod_nom = valeurs[1]
        etudiant_id = self.etudiant_data.get('id')

        if not etudiant_id:
            messagebox.showerror("Erreur", "ID étudiant introuvable.")
            return

        # Appel au service pour mettre à jour la base de données
        if justifier_absence(etudiant_id, date_abs, mod_nom):
            messagebox.showinfo("Succès", "L'absence a été marquée comme justifiée.")
            self.actualiser_tableau_absences() # On rafraîchit l'affichage
        else:
            messagebox.showerror("Erreur", "Impossible de mettre à jour la justification.")
        # Par défaut, tout est bloqué en lecture seule
        self.mode_edition = False

    def setup_tab_perso(self):
        """Contenu de l'onglet Informations Personnelles"""
        fields = [("Nom", "nom"), ("Prénom", "prenom"), ("Email", "email"), ("Téléphone", "telephone")]
        for i, (label, key) in enumerate(fields):
            tk.Label(self.tab_perso, text=f"{label} :", bg="white").grid(row=i, column=0, sticky="w", pady=5)
            var = tk.StringVar(value=self.etudiant_data.get(key, ""))
            entry = tk.Entry(self.tab_perso, textvariable=var, width=40, state="disabled")
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.vars[key] = (entry, var)

    def setup_tab_acad(self):
        """Contenu de l'onglet Parcours Académique"""
        tk.Label(self.tab_acad, text="Statut Académique :", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        
        self.statut_var = tk.StringVar(value=self.etudiant_data.get('statut', 'Actif'))
        self.combo_statut = ttk.Combobox(self.tab_acad, textvariable=self.statut_var, values=["Actif", "Redoublant", "Suspendu", "Diplômé"], state="disabled")
        self.combo_statut.grid(row=0, column=1, padx=10, pady=5)

    def toggle_edition(self):
        """Bascule entre le mode lecture et le mode édition"""
        if not self.mode_edition:
            #activ l'édition
            for entry, var in self.vars.values():
                entry.config(state="normal")
            self.combo_statut.config(state="readonly")
            self.btn_edit.config(text="Enregistrer les modifications", bg="#27ae60")
            self.mode_edition = True
        else:
            #save et bloquer
            self.sauvegarder_modifications()

    
    def sauvegarder_modifications(self):
        import sqlite3
    
    # 1. Récupération du matricule (clé primaire pour le WHERE)
        matricule = self.etudiant_data.get('matricule')
    
    # 2. Récupération des nouvelles valeurs depuis tes dictionnaires de variables
    # Note : Vérifie les clés dans ton dictionnaire self.vars
        try:
            nouvelles_infos = {
            'nom': self.vars['Nom'][1].get(),
            'prenom': self.vars['Prénom'][1].get(),
            'email': self.vars['Email'][1].get(),
            'telephone': self.vars['Téléphone'][1].get() if 'Téléphone' in self.vars else ""
            }
            nouveau_statut = self.combo_statut.get()

        # 3. Connexion et mise à jour SQL
            conn = sqlite3.connect('gestion_etudiants.db')
            cursor = conn.cursor()
        
            cursor.execute("""
            UPDATE etudiants 
            SET nom = ?, prenom = ?, email = ?, statut = ?
            WHERE matricule = ? """, (nouvelles_infos['nom'], nouvelles_infos['prenom'], 
              nouvelles_infos['email'], nouveau_statut, matricule))
        
            conn.commit()
            conn.close()

        # 4. Interface : Bloquer à nouveau les champs
            for entry, var in self.vars.values():
                entry.config(state="disabled")
                self.combo_statut.config(state="disabled")
                self.btn_edit.config(text="Modifier les informations", bg="#f39c12")
                self.mode_edition = False
        
                messagebox.showinfo("Succès", f"Les informations de {nouvelles_infos['nom']} ont été mises à jour.")

        except Exception as e:
            messagebox.showerror("Erreur SQL", f"Impossible de sauvegarder : {e}")