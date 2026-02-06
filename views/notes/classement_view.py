import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from services.classement_service import calculer_classement
from services.import_export_service import exporter_classement_excel, exporter_classement_pdf
import sqlite3

class ClassementView:

    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.classement = []
        self.setup_ui()

    def setup_ui(self):
        # ----- FILTRES -----
        filter_frame = tk.Frame(self.frame, bg="white")
        filter_frame.pack(fill="x", padx=10, pady=10)

        # Filière
        self.filiere_var = tk.StringVar()
        tk.Label(filter_frame, text="Filière :").pack(side="left", padx=5)
        self.combo_filiere = ttk.Combobox(filter_frame, textvariable=self.filiere_var, width=20)
        self.combo_filiere.pack(side="left", padx=5)

        # Niveau
        self.niveau_var = tk.StringVar()
        tk.Label(filter_frame, text="Niveau :").pack(side="left", padx=5)
        self.combo_niveau = ttk.Combobox(filter_frame, textvariable=self.niveau_var, width=20)
        self.combo_niveau.pack(side="left", padx=5)

        # Groupe
        self.groupe_var = tk.StringVar()
        tk.Label(filter_frame, text="Groupe :").pack(side="left", padx=5)
        self.combo_groupe = ttk.Combobox(filter_frame, textvariable=self.groupe_var, width=25)
        self.combo_groupe.pack(side="left", padx=5)

        # Bouton calcul classement
        tk.Button(filter_frame, text="Calculer classement", command=self.charger_classement).pack(side="left", padx=10)

        # ----- BOUTONS EXPORT -----
        btn_frame = tk.Frame(self.frame, bg="white")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Exporter Excel", bg="#2ecc71", fg="white", command=self.export_excel).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Exporter PDF", bg="#e74c3c", fg="white", command=self.export_pdf).pack(side="left", padx=5)

        # ----- TABLEAU -----
        colonnes = ("rang", "nom", "prenom", "moyenne", "mention", "groupe")
        self.tree = ttk.Treeview(self.frame, columns=colonnes, show="headings")
        for col in colonnes:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=130)
        self.tree.pack(fill="both", expand=True)

        # Charger les valeurs des filtres depuis la DB
        self.charger_valeurs_filtres()

    def charger_valeurs_filtres(self):
        conn = sqlite3.connect("gestion_etudiants.db")
        cursor = conn.cursor()

        # Filières
        cursor.execute("SELECT id, nom FROM filieres")
        filieres = ["Tous"] + [row[1] for row in cursor.fetchall()]
        self.combo_filiere['values'] = filieres
        self.combo_filiere.set("Tous")

        # Niveaux
        cursor.execute("SELECT id, nom FROM niveaux")
        niveaux = ["Tous"] + [row[1] for row in cursor.fetchall()]
        self.combo_niveau['values'] = niveaux
        self.combo_niveau.set("Tous")

        # Groupes
        groupes = ["Tous", "Cursus Initial", "Cursus Alternance", "International (English Course)", "Alternance (Apprenticeship)", "Section Française Classique"]
        self.combo_groupe['values'] = groupes
        self.combo_groupe.set("Tous")

        conn.close()


    def charger_classement(self):
        # Nettoyer le tableau
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect("gestion_etudiants.db")
        cursor = conn.cursor()

        # Récupérer IDs filière et niveau
        if self.filiere_var.get() == "Tous":
            filiere_id = None
        else:
            filiere_code = self.combo_filiere.get().split(" - ")[0]
            cursor.execute("SELECT id FROM filieres WHERE code=?", (filiere_code,))
            res = cursor.fetchone()
            filiere_id = res[0] if res else None

        # Niveau
        if self.niveau_var.get() == "Tous":
            niveau_id = None
        else:
            niveau_code = self.combo_niveau.get().split(" - ")[0]
            cursor.execute("SELECT id FROM niveaux WHERE code=?", (niveau_code,))
            res = cursor.fetchone()
            niveau_id = res[0] if res else None

        conn.close()

        # Calculer le classement
        classement = calculer_classement(
            filiere=filiere_id,
            niveau=niveau_id,
            groupe=None if self.groupe_var.get() == "Tous" else self.groupe_var.get()
        )
        # Filtrer par groupe si nécessaire
        groupe_choisi = self.combo_groupe.get()
        if groupe_choisi != "Tous":
            classement = [e for e in classement if e.get("groupe", "Cursus Initial") == groupe_choisi]

        self.classement = classement

        # Remplir le tableau
        for etu in classement:
            self.tree.insert(
                "",
                "end",
                values=(
                    etu["rang"],
                    etu["nom"],
                    etu["prenom"],
                    etu["moyenne"],
                    etu["mention"],
                    etu.get("groupe", "N/A")
                )
            )

    def export_excel(self):
        if not self.classement:
            messagebox.showwarning("Attention", "Calculez le classement avant d'exporter.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if path:
            ok, msg = exporter_classement_excel(self.classement, path)
            messagebox.showinfo("Export", msg) if ok else messagebox.showerror("Erreur", msg)

    def export_pdf(self):
        if not self.classement:
            messagebox.showwarning("Attention", "Calculez le classement avant d'exporter.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if path:
            ok, msg = exporter_classement_pdf(self.classement, path)
            messagebox.showinfo("Export", msg) if ok else messagebox.showerror("Erreur", msg)
