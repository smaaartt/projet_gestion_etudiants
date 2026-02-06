import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime

from PIL import Image, ImageTk

# --- MODULE ETUDIANTS ---
class EtudiantModule:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.photo_path = ""
        self.photo_img = None
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.frame, text="INSCRIPTION ADMINISTRATIVE ESILV", font=("Arial", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=10)

        # --- SECTION 1 : INFOS PERSONNELLES ---
        group_perso = tk.LabelFrame(self.frame, text="1. État Civil", bg="white", padx=10, pady=10)
        group_perso.pack(fill="x", padx=20, pady=5)
        
        # Nom et Prénom sur la même ligne
        tk.Label(group_perso, text="Nom *:", bg="white").grid(row=0, column=0, sticky="w")
        self.ent_nom = tk.Entry(group_perso, width=30)
        self.ent_nom.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(group_perso, text="Prénom *:", bg="white").grid(row=0, column=2, sticky="w")
        self.ent_prenom = tk.Entry(group_perso, width=30)
        self.ent_prenom.grid(row=0, column=3, padx=5, pady=5)

        # Sexe et Contact
        tk.Label(group_perso, text="Sexe:", bg="white").grid(row=1, column=0, sticky="w")
        self.combo_sexe = ttk.Combobox(group_perso, values=["Masculin", "Féminin"], state="readonly")
        self.combo_sexe.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(group_perso, text="Email:", bg="white").grid(row=1, column=2, sticky="w")
        self.ent_email = tk.Entry(group_perso, width=30)
        self.ent_email.grid(row=1, column=3, padx=5, pady=5)

        # --- SECTION 2 : PHOTO & MATRICULE ---
        group_img = tk.LabelFrame(self.frame, text="2. Photo & Matricule", bg="white", padx=10, pady=10)
        group_img.pack(fill="x", padx=20, pady=5)

        self.matricule_auto = self.generer_matricule()
        tk.Label(group_img, text=f"Matricule : {self.matricule_auto}", font=("Arial", 10, "bold"), fg="#e67e22").grid(row=0, column=0, padx=10)

        self.lbl_photo = tk.Label(group_img, text="Pas de photo", bg="#f0f0f0", width=12, height=5, relief="groove")
        self.lbl_photo.grid(row=0, column=1, padx=10)
        tk.Button(group_img, text="Choisir photo", command=self.choisir_photo).grid(row=0, column=2)

        # --- SECTION 3 : AFFECTATION ESILV (DYNAMIQUE) ---
        group_acad = tk.LabelFrame(self.frame, text="3. Affectation Académique", bg="white", padx=10, pady=10)
        group_acad.pack(fill="x", padx=20, pady=5)

        # Filière
        tk.Label(group_acad, text="Filière / MSc *:", bg="white").grid(row=0, column=0, sticky="w")
        self.combo_filiere = ttk.Combobox(group_acad, values=self.recuperer_db("filieres"), state="readonly", width=40)
        self.combo_filiere.grid(row=0, column=1, padx=5, pady=5)
        self.combo_filiere.bind("<<ComboboxSelected>>", self.maj_options_dynamiques)

        # Niveau
        tk.Label(group_acad, text="Niveau *:", bg="white").grid(row=0, column=2, sticky="w")
        self.combo_niveau = ttk.Combobox(group_acad, values=self.recuperer_db("niveaux"), state="readonly", width=20)
        self.combo_niveau.grid(row=0, column=3, padx=5, pady=5)

        # Groupe (Type de cursus)
        tk.Label(group_acad, text="Cursus / Groupe *:", bg="white").grid(row=1, column=0, sticky="w")
        self.combo_groupe = ttk.Combobox(group_acad, values=[], state="readonly", width=40)
        self.combo_groupe.grid(row=1, column=1, padx=5, pady=5)

        # --- BOUTON FINAL ---
        tk.Button(self.frame, text="VALIDER L'INSCRIPTION FINALE", bg="#27ae60", fg="white", 
                  font=("Arial", 12, "bold"), command=self.sauvegarder_etudiant, pady=10).pack(pady=20)

    def recuperer_db(self, table):
        conn = sqlite3.connect('gestion_etudiants.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT nom FROM {table}")
        res = [row[0] for row in cursor.fetchall()]
        conn.close()
        return res

    def maj_options_dynamiques(self, event):
        """Filtre les niveaux et les groupes selon la filière choisie"""
        filiere_choisie = self.combo_filiere.get()
        
        # --- LOGIQUE POUR LES NIVEAUX ---
        tous_les_niveaux = self.recuperer_db("niveaux")
        niveaux_filtres = []

        if "MSc" in filiere_choisie:
            # Si c'est un MSc : seulement MSc Year 1 et 2
            niveaux_filtres = [n for n in tous_les_niveaux if "MSc" in n]
            
        elif "Cycle Préparatoire" in filiere_choisie:
            # Si c'est la prépa : seulement ING 1 et 2 (Bac+1 / Bac+2)
            niveaux_filtres = [n for n in tous_les_niveaux if "Année 1" in n or "Année 2" in n]
            
        else:
            # Si c'est une Majeure (DIA, IOT, etc.) : seulement ING 3, 4 et 5
            niveaux_filtres = [n for n in tous_les_niveaux if any(x in n for x in ["Année 3", "Année 4", "Année 5"])]

        # Mise à jour de la liste des niveaux
        self.combo_niveau['values'] = niveaux_filtres
        if niveaux_filtres:
            self.combo_niveau.set(niveaux_filtres[0]) # Sélectionne le premier par défaut

        # --- LOGIQUE POUR LES GROUPES ---
        if "MSc" in filiere_choisie:
            groupes = ["International (English Course)", "Alternance (Apprenticeship)"]
        elif "Cycle Préparatoire" in filiere_choisie:
            groupes = ["Section Française Classique"]
        else:
            groupes = ["Cursus Initial", "Cursus Alternance"]
            
        
        self.combo_groupe['values'] = groupes
        self.combo_groupe.set(groupes[0])

    def generer_matricule(self):
        try:
            conn = sqlite3.connect('gestion_etudiants.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM etudiants")
            count = cursor.fetchone()[0]
            conn.close()
            return f"ESILV-{datetime.now().year}-{(count + 1):04d}"
        except: return "ESILV-TEMP-0000"

    def choisir_photo(self):
        file = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png")])
        if file:
            self.photo_path = file
            img = Image.open(file).resize((100, 100))
            self.photo_img = ImageTk.PhotoImage(img)
            self.lbl_photo.config(image=self.photo_img, text="")

    def sauvegarder_etudiant(self):
        if not self.ent_nom.get() or not self.combo_filiere.get():
            messagebox.showerror("Erreur", "Veuillez remplir les champs obligatoires.")
            return

        try:
            conn = sqlite3.connect('gestion_etudiants.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO etudiants (matricule, nom, prenom, sexe, email, photo_path, date_inscription, statut)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'actif')
            """, (self.matricule_auto, self.ent_nom.get().upper(), self.ent_prenom.get(), 
                  self.combo_sexe.get(), self.ent_email.get(), self.photo_path, 
                  datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            messagebox.showinfo("Succès", f"Étudiant inscrit !\nGroupe : {self.combo_groupe.get()}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
