import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from services.absence_service import enregistrer_absence
# Assure-toi que cette fonction existe dans ton service académique ou absence
from services.academique_service import justifier_absence, recuperer_absences_injustifiees

class EnregistrementAbsenceView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
        self.setup_ui()

    def setup_ui(self):
        # --- PARTIE 1 : ENREGISTREMENT ---
        tk.Label(self, text="Enregistrement d'une Absence", 
                 font=("Arial", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=10)
        
        form_container = tk.Frame(self, bg="white", padx=20, pady=10, highlightbackground="#bdc3c7", highlightthickness=1)
        form_container.pack(pady=5)

        tk.Label(form_container, text="ID Étudiant :", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_eid = tk.Entry(form_container, width=20)
        self.ent_eid.grid(row=0, column=1, padx=10)

        tk.Label(form_container, text="ID Module :", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_mid = tk.Entry(form_container, width=20)
        self.ent_mid.grid(row=1, column=1, padx=10)

        tk.Label(form_container, text="Date (AAAA-MM-JJ) :", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_date = tk.Entry(form_container, width=20)
        self.ent_date.insert(0, "2024-02-06")
        self.ent_date.grid(row=2, column=1, padx=10)

        tk.Button(self, text="Enregistrer l'absence", command=self.sauver, 
                  bg="#e74c3c", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

        # --- PARTIE 2 : LISTE ET JUSTIFICATION ---
        tk.Label(self, text="Absences non justifiées", font=("Arial", 12, "bold"), bg="white").pack(pady=(10, 0))
        
        # Tableau pour voir les absences et les sélectionner
        columns = ("ID", "Étudiant", "Module", "Date", "Statut")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        
        self.tree.pack(fill="x", padx=20, pady=5)

        tk.Button(self, text="Justifier l'absence sélectionnée", 
                  command=self.preparer_justification, 
                  bg="#3498db", fg="white", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.charger_absences()

    def charger_absences(self):
        """Remplit le tableau avec les absences non justifiées"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Appel au service pour récupérer les données (justifiee = 0)
        absences = recuperer_absences_injustifiees()
        for abs in absences:
            self.tree.insert("", "end", values=(abs['id'], abs['etudiant'], abs['module'], abs['date'], "Non Justifié"))

    def sauver(self):
        eid = self.ent_eid.get()
        mid = self.ent_mid.get()
        date = self.ent_date.get()
        if not eid or not mid:
            messagebox.showwarning("Attention", "Veuillez remplir les ID Étudiant et Module.")
            return

        ok, msg = enregistrer_absence(eid, mid, date, "Séance", "Non justifié")
        if ok:
            messagebox.showinfo("Succès", "Absence enregistrée.")
            self.charger_absences() # Rafraîchir le tableau
            self.ent_eid.delete(0, tk.END)
            self.ent_mid.delete(0, tk.END)
        else:
            messagebox.showerror("Erreur", msg)

    def preparer_justification(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une absence dans le tableau.")
            return
        
        id_absence = self.tree.item(selection[0])['values'][0]
        self.ouvrir_fenetre_justification(id_absence)

    def ouvrir_fenetre_justification(self, id_absence):
        popup = tk.Toplevel(self)
        popup.title("Justifier une absence")
        popup.geometry("400x320")
        popup.grab_set() # Rend la fenêtre modale

        tk.Label(popup, text=f"Justification Absence n°{id_absence}", font=("Arial", 10, "bold")).pack(pady=10)
        
        tk.Label(popup, text="Motif de l'absence :").pack(pady=5)
        ent_motif = tk.Entry(popup, width=40)
        ent_motif.pack(pady=5)

        self.chemin_doc = ""

        def selectionner_fichier():
            self.chemin_doc = filedialog.askopenfilename(
                title="Sélectionner le document justificatif",
                filetypes=[("Documents", "*.pdf *.jpg *.png *.docx")]
            )
            lbl_fichier.config(text=self.chemin_doc.split('/')[-1] if self.chemin_doc else "Aucun fichier")

        tk.Button(popup, text="📎 Joindre un document", command=selectionner_fichier).pack(pady=10)
        lbl_fichier = tk.Label(popup, text="Aucun fichier sélectionné", fg="gray", wraplength=350)
        lbl_fichier.pack()

        def confirmer():
            motif = ent_motif.get()
            if motif and self.chemin_doc:
                success, msg = justifier_absence(id_absence, motif, self.chemin_doc)
                if success:
                    messagebox.showinfo("Succès", msg)
                    popup.destroy()
                    self.charger_absences()
                else:
                    messagebox.showerror("Erreur", msg)
            else:
                messagebox.showwarning("Incomplet", "Motif et document obligatoires.")

        tk.Button(popup, text="Valider la justification", bg="#27ae60", fg="white", 
                  font=("Arial", 10, "bold"), command=confirmer).pack(pady=20)