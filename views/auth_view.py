import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib  
import os

from views.main_view import MainWindow

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion Académique - Connexion")
        self.root.geometry("400x500")

        frame = ttk.Frame(root, padding="30")
        frame.pack(expand=True, fill="both")
        ttk.Label(frame, text="AUTHENTIFICATION", font=("Arial", 16, "bold")).pack(pady=20)   
   
        ttk.Label(frame, text="Nom d'utilisateur :").pack(anchor="w")
        self.username_entry = ttk.Entry(frame, width=30)
        self.username_entry.pack(pady=5)
        
        ttk.Label(frame, text="Mot de passe :").pack(anchor="w")
        self.password_entry = ttk.Entry(frame, width=30, show="*")
        self.password_entry.pack(pady=5)
        
        ttk.Button(frame, text="Se connecter", command=self.verifier_connexion).pack(pady=30)

    def verifier_connexion(self):
        u, p = self.username_entry.get(), self.password_entry.get()
        
        # 1.HACHAGE DE MOT DE PASSE SAISI
        password_hache = hashlib.sha256(p.encode()).hexdigest()

        try:
            conn = sqlite3.connect('gestion_etudiants.db')
            cursor = conn.cursor()
            
            # 2.CHERCHE LE HASH DANS LA BDD (et on vérifie si l'utilisateur est actif)
            cursor.execute("""
                SELECT role, nom, prenom 
                FROM users 
                WHERE username=? AND password_hash=? AND statut='actif'
            """, (u, password_hache))
            
            user = cursor.fetchone()
            conn.close()

            if user:
                role, nom, prenom = user
                messagebox.showinfo("Succès", f"Bienvenue {prenom} {nom} ({role})")
                self.root.destroy()
                
                
                new_root = tk.Tk()
                MainWindow(new_root, role, f"{prenom} {nom}")
                new_root.mainloop()
            else:
                messagebox.showerror("Erreur", "Identifiants invalides ou compte désactivé.")
                
        except Exception as e:
            messagebox.showerror("Erreur BDD", f"Erreur de connexion : {str(e)}")