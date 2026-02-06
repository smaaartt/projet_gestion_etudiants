import tkinter as tk
from tkinter import ttk

# On importe les vues qui correspondent à tes 13 tables
from views.academique.filiere_view import FiliereView
from views.academique.niveau_view import NiveauView
from views.academique.module_view import ModuleView
from views.academique.calendrier_view import CalendrierView
from views.academique.attribution_view import AttributionProfView

class AdminAcademiqueTabs(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)

        # Création des onglets
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # On ajoute chaque interface dans un onglet
        # Chaque onglet correspond à une de tes tables officielles
        self.notebook.add(FiliereView(self.notebook), text=" Filières ")
        self.notebook.add(NiveauView(self.notebook), text=" Niveaux ")
        self.notebook.add(ModuleView(self.notebook), text=" Modules ")
        self.notebook.add(CalendrierView(self.notebook), text=" Calendrier ")
        self.notebook.add(AttributionProfView(self.notebook), text=" Affectations ")