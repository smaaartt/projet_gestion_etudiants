import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class SaisieNotesModule:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.modules_map = {}

        self.setup_ui()
        self.charger_modules()
        self.charger_groupes()
        self.charger_etudiants()

    def setup_ui(self):
        # Titre
        tk.Label(
            self.frame,
            text="SAISIE DES NOTES",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=10)

        # --- FILTRES ---
        filtres_frame = tk.LabelFrame(self.frame, text="Paramètres de saisie", bg="white")
        filtres_frame.pack(fill="x", padx=20, pady=10)

        # Module
        tk.Label(filtres_frame, text="Module :", bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.combo_module = ttk.Combobox(filtres_frame, state="readonly", width=30)
        self.combo_module.grid(row=0, column=1, padx=5, pady=5)

        # Groupe
        tk.Label(filtres_frame, text="Groupe :", bg="white").grid(row=0, column=2, padx=5, pady=5)
        self.combo_groupe = ttk.Combobox(filtres_frame, state="readonly", width=20)
        self.combo_groupe.grid(row=0, column=3, padx=5, pady=5)

        # Session
        tk.Label(filtres_frame, text="Session :", bg="white").grid(row=0, column=4, padx=5, pady=5)
        self.combo_session = ttk.Combobox(
            filtres_frame,
            values=["Normale", "Rattrapage"],
            state="readonly",
            width=15
        )
        self.combo_session.grid(row=0, column=5, padx=5, pady=5)
        self.combo_session.set("Normale")

        # Type d'évaluation
        tk.Label(filtres_frame, text="Type évaluation :", bg="white").grid(row=0, column=6, padx=5, pady=5)
        self.combo_type_eval = ttk.Combobox(
            filtres_frame,
            values=["CC", "TP", "Examen", "Final"],
            state="readonly",
            width=15
        )
        self.combo_type_eval.grid(row=0, column=7, padx=5, pady=5)
        self.combo_type_eval.set("Final")

        # Bindings
        self.combo_module.bind("<<ComboboxSelected>>", lambda e: self.charger_groupes())
        self.combo_groupe.bind("<<ComboboxSelected>>", lambda e: self.charger_etudiants())
        self.combo_type_eval.bind("<<ComboboxSelected>>", lambda e: self.charger_etudiants())
        self.combo_session.bind("<<ComboboxSelected>>", lambda e: self.charger_etudiants())

        # --- TABLEAU DE SAISIE ---
        table_frame = tk.Frame(self.frame, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        colonnes = ("matricule", "nom", "note")
        self.tree = ttk.Treeview(table_frame, columns=colonnes, show="headings")

        self.tree.heading("matricule", text="Matricule")
        self.tree.heading("nom", text="Nom")
        self.tree.heading("note", text="Note /20")

        self.tree.column("matricule", width=150)
        self.tree.column("nom", width=250)
        self.tree.column("note", width=100, anchor="center")

        # Tag pour couleurs
        self.tree.tag_configure("faible", background="#f8d7da")   # Rouge clair
        self.tree.tag_configure("excellente", background="#d4edda")  # Vert clair

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.editer_note)

        # --- BOUTON ---
        tk.Button(
            self.frame,
            text="ENREGISTRER LES NOTES",
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.enregistrer_notes
        ).pack(pady=15)

    def enregistrer_notes(self):
        module_label = self.combo_module.get()
        module_id = self.modules_map.get(module_label)
        session = self.combo_session.get()
        type_eval = self.combo_type_eval.get()
        annee = "2023-2024"

        if not module_id:
            messagebox.showwarning("Attention", "Module non sélectionné")
            return

        conn = sqlite3.connect("gestion_etudiants.db")
        cursor = conn.cursor()

        try:
            for item in self.tree.get_children():
                etudiant_id = int(item)
                note = self.tree.item(item, "values")[2]

                if note == "":
                    continue

                # INSERT ou UPDATE si déjà existant
                cursor.execute("""
                    INSERT INTO notes (
                        etudiant_id, module_id, type_evaluation,
                        note, coefficient, date_examen,
                        session, annee_academique
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(etudiant_id, module_id, type_evaluation, annee_academique, session)
                    DO UPDATE SET note=excluded.note, date_examen=excluded.date_examen
                """, (
                    etudiant_id,
                    module_id,
                    type_eval,
                    float(note),
                    1.0,
                    datetime.now().date(),
                    session,
                    annee
                ))

            conn.commit()
            messagebox.showinfo("Succès", "Notes enregistrées")
            self.charger_etudiants()  # Recharger pour mise en couleur

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erreur", str(e))
        finally:
            conn.close()

    def charger_modules(self):
        try:
            conn = sqlite3.connect("gestion_etudiants.db")
            cursor = conn.cursor()

            cursor.execute("SELECT id, code, nom FROM modules")
            modules = cursor.fetchall()
            conn.close()

            valeurs = []
            for module_id, code, nom in modules:
                label = f"{code} - {nom}"
                valeurs.append(label)
                self.modules_map[label] = module_id

            self.combo_module["values"] = valeurs
            if valeurs:
                self.combo_module.set(valeurs[0])

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les modules : {e}")

    def charger_groupes(self):
        try:
            module_label = self.combo_module.get()
            module_id = self.modules_map.get(module_label)
            if not module_id:
                self.combo_groupe["values"] = []
                return

            conn = sqlite3.connect("gestion_etudiants.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT i.groupe
                FROM inscriptions i
                JOIN modules m ON i.filiere_id = m.filiere_id AND i.niveau_id = m.niveau_id
                WHERE m.id = ?
            """, (module_id,))
            groupes = [row[0] for row in cursor.fetchall()]
            conn.close()

            self.combo_groupe["values"] = groupes
            if groupes:
                self.combo_groupe.set(groupes[0])
                self.charger_etudiants()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les groupes : {e}")

    def charger_etudiants(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        module_label = self.combo_module.get()
        module_id = self.modules_map.get(module_label)
        groupe = self.combo_groupe.get()
        type_eval = self.combo_type_eval.get()
        session = self.combo_session.get()
        annee = "2023-2024"

        if not module_id or not groupe:
            return

        try:
            conn = sqlite3.connect("gestion_etudiants.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT e.id, e.matricule, e.nom || ' ' || e.prenom,
                    n.note
                FROM inscriptions i
                JOIN etudiants e ON e.id = i.etudiant_id
                JOIN modules m ON m.filiere_id = i.filiere_id AND m.niveau_id = i.niveau_id
                LEFT JOIN notes n ON n.etudiant_id = e.id AND n.module_id = m.id
                    AND n.type_evaluation=? AND n.session=? AND n.annee_academique=?
                WHERE m.id = ? AND i.groupe = ?
            """, (type_eval, session, annee, module_id, groupe))

            for etu_id, matricule, nom_complet, note in cursor.fetchall():
                valeurs = (matricule, nom_complet, note if note is not None else "")
                tag = ""
                if note is not None:
                    if note < 10:
                        tag = "faible"
                    elif note >= 18:
                        tag = "excellente"
                self.tree.insert("", "end", values=valeurs, iid=etu_id, tags=(tag,))

            conn.close()

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les étudiants : {e}")

    def editer_note(self, event):
        item_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)

        if col != "#3" or not item_id:
            return

        x, y, width, height = self.tree.bbox(item_id, col)
        valeur_actuelle = self.tree.item(item_id, "values")[2]

        entry = tk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, valeur_actuelle)
        entry.focus()

        def valider(event):
            try:
                note = float(entry.get())
                if not 0 <= note <= 20:
                    raise ValueError
                valeurs = list(self.tree.item(item_id, "values"))
                valeurs[2] = note
                tag = ""
                if note < 10:
                    tag = "faible"
                elif note >= 18:
                    tag = "excellente"
                self.tree.item(item_id, values=valeurs, tags=(tag,))
                entry.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Note invalide (0–20)")
                entry.focus()

        entry.bind("<Return>", valider)
        entry.bind("<FocusOut>", lambda e: entry.destroy())
