import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

# --- IMPORTS ETUDIANTS ---
from views.etudiants.fiche_view import FicheEtudiantView
from views.etudiants.import_export_view import ImportExportView
from views.etudiants.inscription_view import EtudiantModule
from views.etudiants.liste_view import ListeEtudiantModule
from services.etudiant_service import obtenir_premier_etudiant

# --- IMPORTS NOTES & RESULTATS ---
from views.notes.saisie_view import SaisieNotesModule
from views.notes.classement_view import ClassementView
from views.notes.statistiques_module import StatistiquesDashboard
from services.releve_service import generer_releve_pdf

# --- IMPORTS ABSENCES ---
from views.absences.enregistrement_view import EnregistrementAbsenceView
from views.absences.stats_absences_view import StatsAbsencesView

# --- IMPORTS ADMINISTRATION ---
from views.admin.admin_view import AdminView
# Import de la nouvelle vue regroupée à onglets
from views.academique.admin_academique_view import AdminAcademiqueTabs

class MainWindow:
    def __init__(self, root, role, nom_complet):
        self.root = root
        self.root.title("Système de Gestion Académique")
        self.root.geometry("1200x800")
        self.role = role 
        self.utilisateur_nom = nom_complet
        
        # 1. Création de la Sidebar
        self.sidebar = tk.Frame(self.root, bg="#34495e", width=220)
        self.sidebar.pack(side="left", fill="y")
        
        # 2. Zone de contenu
        self.content_area = tk.Frame(self.root, bg="white")
        self.content_area.pack(side="right", expand=True, fill="both")

        # 3. Construction du menu selon les rôles
        self.build_menu()

    def nettoyer_cadre(self):
        """Vide la zone centrale avant d'afficher une nouvelle vue"""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def build_menu(self):
        # Header Sidebar
        tk.Label(self.sidebar, text="MENU PRINCIPAL", font=("Arial", 12, "bold"), 
                 fg="white", bg="#34495e").pack(pady=20)

        # --- SECTION : CONSULTATION (TOUS ROLES) ---
        self.creer_titre_section("CONSULTATION")
        tk.Button(self.sidebar, text="Liste des Étudiants", command=self.ouvrir_liste_etudiants).pack(fill="x", pady=2, padx=10)
        tk.Button(self.sidebar, text="Stats Absences", command=self.ouvrir_stats_absences).pack(fill="x", pady=2, padx=10)
        tk.Button(self.sidebar, text="Classements", command=self.ouvrir_classement).pack(fill="x", pady=2, padx=10)

        # --- SECTION : SAISIE (PROFS & ADMIN) ---
        self.creer_titre_section("OPÉRATIONS")
        tk.Button(self.sidebar, text="Pointer Absences", command=self.ouvrir_enregistrement_absences).pack(fill="x", pady=2, padx=10)
        tk.Button(self.sidebar, text="Saisie des Notes", command=self.ouvrir_saisie_notes).pack(fill="x", pady=2, padx=10)
        tk.Button(self.sidebar, text="Générer Relevé PDF", command=self.ouvrir_releve).pack(fill="x", pady=2, padx=10)
        tk.Button(self.sidebar, text="Statistiques", command=self.ouvrir_statistiques).pack(fill="x", pady=2, padx=10)

        # --- SECTION : GESTION (SECRÉTARIAT & ADMIN) ---
        if self.role in ['Administrateur', 'Secrétariat']:
            self.creer_titre_section("ADMINISTRATION")
            # BOUTON UNIQUE POUR TOUTE LA CONFIG ACADEMIQUE (Onglets)
            tk.Button(self.sidebar, text="Config Académique", 
                      command=self.ouvrir_admin_academique,
                      bg="#2980b9", fg="white", font=("Arial", 10, "bold")).pack(fill="x", pady=5, padx=10)
            
            tk.Button(self.sidebar, text="Inscription Étudiant", command=self.ouvrir_module_etudiants).pack(fill="x", pady=2, padx=10)
            tk.Button(self.sidebar, text="Import / Export", command=self.ouvrir_import_export).pack(fill="x", pady=2, padx=10)

        # --- BOUTON EXCLUSIF SYSTEME ---
        if self.role == 'Administrateur':
            tk.Button(self.sidebar, text="🛡️ Sécurité Système", bg="#c0392b", fg="white", 
                      font=("Arial", 10, "bold"), command=self.ouvrir_admin).pack(fill="x", pady=20, padx=10)
        
        # Footer Sidebar (Infos utilisateur)
        footer = tk.Frame(self.sidebar, bg="#2c3e50")
        footer.pack(side="bottom", fill="x")
        tk.Label(footer, text=f"{self.utilisateur_nom}", fg="white", bg="#2c3e50", font=("Arial", 9, "bold")).pack(pady=2)
        tk.Label(footer, text=f"Rôle: {self.role}", fg="#bdc3c7", bg="#2c3e50", font=("Arial", 8)).pack(pady=5)

    def creer_titre_section(self, texte):
        tk.Label(self.sidebar, text=texte, font=("Arial", 8, "bold"), 
                 fg="#95a5a6", bg="#34495e").pack(pady=(15, 5), padx=10, anchor="w")

    # --- MÉTHODES DE NAVIGATION ---
    
    def ouvrir_admin_academique(self):
        """Ouvre l'interface à onglets regroupant toute la config académique"""
        self.nettoyer_cadre()
        AdminAcademiqueTabs(self.content_area)

    def ouvrir_module_etudiants(self):
        self.nettoyer_cadre()
        EtudiantModule(self.content_area)

    def ouvrir_liste_etudiants(self):
       self.nettoyer_cadre()
       ListeEtudiantModule(self.content_area, self)

    def ouvrir_fiche_etudiant(self, etudiant_data=None):
        self.nettoyer_cadre()
        import sqlite3
        if etudiant_data and isinstance(etudiant_data, (list, tuple)):
            matricule = etudiant_data[0]
            try:
                conn = sqlite3.connect('gestion_etudiants.db')
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM etudiants WHERE matricule = ?", (matricule,))
                res = cursor.fetchone()
                if res: etudiant_data = dict(res)
                conn.close()
            except Exception as e:
                print(f"Erreur SQL : {e}")

        if etudiant_data is None:
            etudiant_data = obtenir_premier_etudiant()

        FicheEtudiantView(self.content_area, etudiant_data=etudiant_data) 

    def ouvrir_import_export(self):
        self.nettoyer_cadre()
        ImportExportView(self.content_area)

    def ouvrir_saisie_notes(self):
        self.nettoyer_cadre()
        SaisieNotesModule(self.content_area)

    def ouvrir_admin(self):
        self.nettoyer_cadre()
        AdminView(self.content_area)

    def ouvrir_classement(self):
        self.nettoyer_cadre()
        ClassementView(self.content_area)

    def ouvrir_releve(self):
        etudiant_id = simpledialog.askinteger("Étudiant", "Entrez l'ID de l'étudiant :")
        if not etudiant_id: return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not path: return
        ok, msg = generer_releve_pdf(etudiant_id, path)
        if ok: messagebox.showinfo("Succès", msg)
        else: messagebox.showerror("Erreur", msg)

    def ouvrir_enregistrement_absences(self):
        self.nettoyer_cadre()
        EnregistrementAbsenceView(self.content_area)

    def ouvrir_stats_absences(self):
        self.nettoyer_cadre()
        StatsAbsencesView(self.content_area)

    def ouvrir_statistiques(self):
        self.nettoyer_cadre()
        StatistiquesDashboard(self.content_area)