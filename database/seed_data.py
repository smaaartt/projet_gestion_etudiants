import sqlite3
import os
from datetime import datetime
import hashlib

# Chemin vers la DB
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(base_dir, 'gestion_etudiants.db')

def reset_tables():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    tables = ["notes", "absences", "affectations", "enseignants", "inscriptions",
              "modules", "specialites", "niveaux", "filieres", "etudiants", "users"]
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()
    print("Toutes les tables nettoyées.")

def peupler_utilisateurs_securises():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users")

    # Liste des utilisateurs 
    utilisateurs = [
        ('admin', 'admin123', 'Administrateur', 'Mistry', 'Ekta'),
        ('secretaire1', 'pass123', 'Secrétariat', 'Kavuansiko', 'Angelikia'),
        ('prof1', 'prof123', 'Enseignant', 'Chriqui', 'Léora')
    ]

    for username, pwd, role, nom, prenom in utilisateurs:
        # Hachage SHA-256 du mot de passe
        pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, statut, nom, prenom)
            VALUES (?, ?, ?, 'actif', ?, ?)
        """, (username, pwd_hash, role, nom, prenom))

    conn.commit()
    conn.close()
    print("✅ Utilisateurs (Admin, Secrétariat, Enseignant) créés avec succès !")

def peupler_filieres_niveaux():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    filieres = [
        ('PREPA', 'Cycle Préparatoire Intégré'),
        ('IOT', 'Majeure IOT, Objets Connectés & Sécurité'),
        ('DIA', 'Majeure Data & Intelligence Artificielle'),
        ('IF', 'Majeure Ingénierie Financière'),
        ('MMN', 'Majeure Modélisation & Mécanique Numérique'),
        ('EVD', 'Majeure Énergie & Villes Durables'),
        ('SANTE', 'Majeure Santé Connectée'),
        ('MSC_CSDS', 'MSc Computer Science & Data Science'),
        ('MSC_CRCL', 'MSc Cyber Resilience & Crisis Leadership')
    ]
    cursor.executemany("INSERT INTO filieres (code, nom) VALUES (?, ?)", filieres)

    niveaux = [
        ('ING1', 'Ingénieur Année 1'), ('ING2', 'Ingénieur Année 2'),
        ('ING3', 'Ingénieur Année 3'), ('ING4', 'Ingénieur Année 4'),
        ('ING5', 'Ingénieur Année 5'), ('MSC1', 'MSc Year 1'), ('MSC2', 'MSc Year 2')
    ]
    cursor.executemany("INSERT INTO niveaux (code, nom) VALUES (?, ?)", niveaux)

    conn.commit()
    conn.close()
    print("Filières et niveaux injectés.")

def peupler_modules():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM filieres WHERE code='DIA'")
    filiere_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM niveaux WHERE code='ING3'")
    niveau_id = cursor.fetchone()[0]

    modules = [
        ('DIA301', 'Python Avancé', 2.0, 6, 1, filiere_id, niveau_id),
        ('DIA302', 'Machine Learning', 3.0, 8, 2, filiere_id, niveau_id),
        ('DIA303', 'Bases de Données', 2.0, 5, 1, filiere_id, niveau_id)
    ]
    cursor.executemany("""
        INSERT INTO modules (code, nom, coefficient, credits, semestre, filiere_id, niveau_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, modules)
    conn.commit()
    conn.close()
    print("Modules injectés.")

def peupler_etudiants_et_inscriptions():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    etudiants = [
        # matricule, nom, prenom, date_naissance, lieu_naissance, sexe, email, telephone, adresse, photo_path, date_inscription
        ('ESILV-2023-0001', 'DUPONT', 'Alice', '2000-05-01', 'Paris', 'Féminin', 'alice@esilv.fr', '0600000001', '', '', '2023-09-01'),
        ('ESILV-2023-0002', 'MARTIN', 'Bob', '2000-08-15', 'Lyon', 'Masculin', 'bob@esilv.fr', '0600000002', '', '', '2023-09-01'),
        ('ESILV-2023-0003', 'DURAND', 'Charlie', '2001-01-20', 'Marseille', 'Masculin', 'charlie@esilv.fr', '0600000003', '', '', '2023-09-01')
    ]
    cursor.executemany("""
        INSERT INTO etudiants (matricule, nom, prenom, date_naissance, lieu_naissance, sexe, email, telephone, adresse, photo_path, date_inscription)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, etudiants)

    cursor.execute("SELECT id FROM filieres WHERE code='DIA'")
    filiere_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM niveaux WHERE code='ING3'")
    niveau_id = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM etudiants")
    etu_ids = [row[0] for row in cursor.fetchall()]

    inscriptions = [(etu_id, filiere_id, niveau_id, '2023-2024', 'A', 'actif', '2023-09-01') for etu_id in etu_ids]
    cursor.executemany("""
        INSERT INTO inscriptions (etudiant_id, filiere_id, niveau_id, annee_academique, groupe, statut, date_inscription)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, inscriptions)

    conn.commit()
    conn.close()
    print("Étudiants et inscriptions injectés.")

def peupler_enseignants_et_affectations():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    enseignants = [
        ('ENS001', 'Legrand', 'Marie', 'Data Science', 'marie.legrand@esilv.fr', '0600000010'),
        ('ENS002', 'Petit', 'Luc', 'Python', 'luc.petit@esilv.fr', '0600000011')
    ]
    cursor.executemany("""
        INSERT INTO enseignants (matricule, nom, prenom, specialite, email, telephone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, enseignants)

    cursor.execute("SELECT id FROM modules WHERE code='DIA301'")
    module_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM enseignants WHERE matricule='ENS001'")
    ens_id = cursor.fetchone()[0]

    affectations = [(ens_id, module_id, 'A', '2023-2024')]
    cursor.executemany("""
        INSERT INTO affectations (enseignant_id, module_id, groupe, annee_academique)
        VALUES (?, ?, ?, ?)
    """, affectations)

    conn.commit()
    conn.close()
    print("Enseignants et affectations injectés.")

def peupler_notes_absences():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM etudiants")
    etu_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM modules WHERE code='DIA301'")
    module_id = cursor.fetchone()[0]

    notes = [(etu_id, module_id, 'DS1', 15.0, 2.0, '2024-01-15', 'Normale', '2023-2024') for etu_id in etu_ids]
    cursor.executemany("""
        INSERT INTO notes (etudiant_id, module_id, type_evaluation, note, coefficient, date_examen, session, annee_academique)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, notes)

    absences = [(etu_id, module_id, '2024-02-01', 'Seance1', 0, 'Malade', '', datetime.now()) for etu_id in etu_ids]
    cursor.executemany("""
        INSERT INTO absences (etudiant_id, module_id, date_absence, seance, justifiee, motif, document_path, date_enregistrement)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, absences)

    conn.commit()
    conn.close()
    print("Notes et absences injectées.")

if __name__ == "__main__":
    reset_tables()
    peupler_filieres_niveaux()
    peupler_modules()
    peupler_etudiants_et_inscriptions()
    peupler_enseignants_et_affectations()
    peupler_notes_absences()
    peupler_utilisateurs_securises()
    print("Seed complet terminé !")
