import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from services.import_export_service import importer_csv, exporter_excel

class ImportExportView:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.setup_ui()

    def setup_ui(self):
        # Titre
        tk.Label(self.frame, text="Gestion des Données (Import/Export)", 
                 font=("Arial", 16, "bold"), bg="white").pack(pady=20)

        # --- SECTION IMPORT ---
        import_group = tk.LabelFrame(self.frame, text=" Importation (CSV) ", padx=20, pady=20, bg="white")
        import_group.pack(fill="x", padx=20, pady=10)

        tk.Label(import_group, text="Ajouter des étudiants massivement via un fichier .csv", bg="white").pack(anchor="w")
        tk.Button(import_group, text="Choisir un fichier CSV", bg="#3498db", fg="white",
                  command=self.lancer_import).pack(pady=10)

        # --- SECTION EXPORT ---
        export_group = tk.LabelFrame(self.frame, text=" Exportation (Excel) ", padx=20, pady=20, bg="white")
        export_group.pack(fill="x", padx=20, pady=10)

        tk.Label(export_group, text="Générer un tableau Excel (.xlsx) de tous les étudiants", bg="white").pack(anchor="w")
        tk.Button(export_group, text="Exporter vers Excel", bg="#2ecc71", fg="white",
                  command=self.lancer_export).pack(pady=10)

    def lancer_import(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            success, msg = importer_csv(file_path)
            if success:
                messagebox.showinfo("Succès", msg)
            else:
                messagebox.showerror("Erreur", msg)

    def lancer_export(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            success, msg = exporter_excel(file_path)
            if success:
                messagebox.showinfo("Succès", msg)
            else:
                messagebox.showerror("Erreur", msg)