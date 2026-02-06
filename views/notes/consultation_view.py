import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ConsultationNotesView:
    def __init__(self, parent_frame, etudiant_id=None, user_id=None):
        """
        :param parent_frame: Frame parent pour l'affichage
        :param etudiant_id: ID de l'étudiant à afficher
        :param user_id: ID de l'utilisateur connecté pour les logs
        """
        self.frame = parent_frame
        self.etudiant_id = etudiant_id
        self.user_id = user_id
        self.entry_edit = None
        self.setup_ui()

    def setup_ui(self):
        # Filtre par module
        filter_frame = tk.Frame(self.frame, bg="white")
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Filtrer par module :", bg="white").pack(side="left")
        self.module_var = tk.StringVar()
        self.combo_module = ttk.Combobox(filter_frame, textvariable=self.module_var, state="readonly")
        self.combo_module.pack(side="left", padx=5)
        self.combo_module.bind("<<ComboboxSelected>>", lambda e: self.charger_notes())

        # Tableau des notes
        table_frame = tk.Frame(self.frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        colonnes = ("module", "type_eval", "note", "coefficient", "moyenne")
        self.tree = ttk.Treeview(table_frame, columns=colonnes, show="headings")
        for col in colonnes:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=120)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-1>", self.editer_cellule)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Bouton pour sauvegarder les modifications
        tk.Button(self.frame, text="Enregistrer les modifications", bg="#27ae60", fg="white",
                  command=self.sauvegarder_notes).pack(pady=10)

        # Charger modules et notes
        self.charger_modules()
        self.charger_notes()

    def charger_modules(self):
        """Charge la liste des modules disponibles pour l'étudiant"""
        try:
            conn = sqlite3.connect("gestion_etudiants.db")
            cursor = conn.cursor()
            if self.etudiant_id:
                cursor.execute("""
                    SELECT DISTINCT m.nom 
                    FROM modules m
                    JOIN notes n ON n.module_id = m.id
                    WHERE n.etudiant_id = ?
                """, (self.etudiant_id,))
            else:
                cursor.execute("SELECT nom FROM modules")
            modules = [row[0] for row in cursor.fetchall()]
            conn.close()
            self.combo_module['values'] = modules
            if modules:
                self.combo_module.set(modules[0])
        except Exception as e:
            messagebox.showerror("Erreur BDD", str(e))

    def charger_notes(self):
        """Charge les notes filtrées et calcule la moyenne"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            conn = sqlite3.connect("gestion_etudiants.db")
            cursor = conn.cursor()

            query = """
                SELECT m.nom, n.type_evaluation, n.note, n.coefficient
                FROM notes n
                JOIN modules m ON m.id = n.module_id
                WHERE 1=1
            """
            params = []
            if self.etudiant_id:
                query += " AND n.etudiant_id=?"
                params.append(self.etudiant_id)
            if self.module_var.get():
                query += " AND m.nom=?"
                params.append(self.module_var.get())

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            total_coef = sum(row[3] for row in rows) if rows else 0
            total_note = sum(row[2]*row[3] for row in rows) if rows else 0
            moyenne = round(total_note/total_coef, 2) if total_coef else 0

            for row in rows:
                self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], moyenne))

            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur BDD", str(e))

    def editer_cellule(self, event):
        """Permet d'éditer la cellule 'note' au double clic"""
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not item or col != "#3":  # colonne 'note'
            return
        x, y, width, height = self.tree.bbox(item, col)
        value = self.tree.set(item, column=col)

        self.entry_edit = tk.Entry(self.tree)
        self.entry_edit.place(x=x, y=y, width=width, height=height)
        self.entry_edit.insert(0, value)
        self.entry_edit.focus()
        self.entry_edit.bind("<Return>", lambda e: self.valider_modification(item, col))
        self.entry_edit.bind("<FocusOut>", lambda e: self.entry_edit.destroy())

    def valider_modification(self, item, col):
        """Valide et met à jour la cellule éditée, recalcul de la moyenne"""
        nouvelle_val = self.entry_edit.get()
        try:
            nouvelle_val_float = float(nouvelle_val)
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour la note.")
            self.entry_edit.destroy()
            return
        self.tree.set(item, column=col, value=nouvelle_val_float)
        self.entry_edit.destroy()
        self.recalculer_moyenne()

    def recalculer_moyenne(self):
        """Recalcule la moyenne pour toutes les lignes affichées"""
        total_coef = sum(float(self.tree.set(i, "coefficient")) for i in self.tree.get_children())
        total_note = sum(float(self.tree.set(i, "note"))*float(self.tree.set(i, "coefficient")) for i in self.tree.get_children())
        moyenne = round(total_note/total_coef, 2) if total_coef else 0
        for i in self.tree.get_children():
            self.tree.set(i, "moyenne", moyenne)

    def sauvegarder_notes(self):
        """Enregistre les modifications et trace les changements"""
        try:
            conn = sqlite3.connect("gestion_etudiants.db")
            cursor = conn.cursor()
            for item in self.tree.get_children():
                vals = self.tree.item(item)['values']
                module_nom, type_eval, note, coefficient, _ = vals
                cursor.execute("SELECT id FROM modules WHERE nom=?", (module_nom,))
                module_id = cursor.fetchone()[0]
                cursor.execute("""
                    UPDATE notes SET note=?, coefficient=?
                    WHERE etudiant_id=? AND module_id=? AND type_evaluation=?
                """, (float(note), float(coefficient), self.etudiant_id, module_id, type_eval))
                # Log complet avec user_id si disponible
                cursor.execute("""
                    INSERT INTO logs (user_id, action, table_affectee, enregistrement_id, details)
                    VALUES (?, ?, 'notes', ?, ?)
                """, (self.user_id, "Modification note via ConsultationNotesView", module_id, f"{type_eval}={note}"))
            conn.commit()
            conn.close()
            messagebox.showinfo("Succès", "Notes mises à jour avec succès !")
            self.charger_notes()
        except Exception as e:
            messagebox.showerror("Erreur BDD", str(e))
