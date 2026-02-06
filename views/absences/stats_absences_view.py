import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from services.absence_service import recuperer_stats_absences

class StatsAbsencesView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
        self.setup_ui()

    def setup_ui(self):
        # 1. Titre
        tk.Label(self, text="Analyse Statistique de l'Assiduité", 
                 font=("Arial", 18, "bold"), bg="white", fg="#2c3e50").pack(pady=10)

        # --- Zone du Tableau ---
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(fill="x", padx=20, pady=5)

        columns = ("Module", "Total") # On simplifie les noms internes
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
        
        # Configuration des titres (Headings)
        self.tree.heading("Module", text="Module / Matière")
        self.tree.heading("Total", text="Total Absences")
        
        # CONFIGURATION DU CENTRAGE ICI :
        # anchor="center" aligne le texte au milieu
        self.tree.column("Module", anchor="center", width=300)
        self.tree.column("Total", anchor="center", width=150)
        
        self.tree.pack(fill="x")

        # 3. Zone des Graphiques (Bas - Les deux l'un à côté de l'autre)
        self.graph_container = tk.Frame(self, bg="white")
        self.graph_container.pack(fill="both", expand=True, padx=10)

        self.afficher_graphiques()

    def afficher_graphiques(self):
        stats = recuperer_stats_absences()
        if not stats: return

        modules = [s['nom'] for s in stats]
        totaux = [s['total'] for s in stats]

        # Création d'une figure large pour mettre deux graphiques côte à côte
        # figsize=(10, 4) -> 10 de large, 4 de haut
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4)) 
        fig.patch.set_facecolor('white')

        # --- GRAPH 1 : BARRES (Gauches) ---
        ax1.bar(modules, totaux, color='#3498db')
        ax1.set_title("Comparaison par Module")
        plt.setp(ax1.get_xticklabels(), rotation=15, horizontalalignment='right', fontsize=8)

        # --- GRAPH 2 : CAMEMBERT (Droite) ---
        labels_pie = [m for m, t in zip(modules, totaux) if t > 0]
        values_pie = [t for t in totaux if t > 0]
        if values_pie:
            ax2.pie(values_pie, labels=labels_pie, autopct='%1.1f%%', startangle=140)
            ax2.set_title("Répartition (%)")

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Remplissage des données tableau
        for s in stats:
            self.tree.insert("", "end", values=(s['nom'], s['total']))