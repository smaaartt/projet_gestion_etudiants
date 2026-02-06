import sqlite3

def initialiser_bdd():
    # Connexion à la base de données (le fichier sera créé s'il n'existe pas)
    conn = sqlite3.connect('gestion_etudiants.db')
    cursor = conn.cursor()

    # Activation des clés étrangères pour SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Table Users (Administration et Sécurité)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT CHECK(role IN ('Administrateur', 'Enseignant', 'Secrétariat')),
        nom TEXT,
        prenom TEXT,
        email TEXT,
        date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
        statut TEXT DEFAULT 'actif'  
    )''')

    # 2. Table Etudiants
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS etudiants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matricule TEXT UNIQUE NOT NULL,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        date_naissance DATE,
        lieu_naissance TEXT,
        sexe TEXT,
        email TEXT,
        telephone TEXT,
        adresse TEXT,
        photo_path TEXT,
        date_inscription DATE,
        statut TEXT DEFAULT 'actif'
    )''') 

    # 3. Table Filieres
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS filieres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        nom TEXT NOT NULL,
        description TEXT,
        niveau_requis TEXT
    )''') 

    # 4. Table Niveaux
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS niveaux (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        nom TEXT NOT NULL,
        ordre INTEGER,
        duree_semestres INTEGER
    )''') 

    # 5. Table Specialites
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS specialites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filiere_id INTEGER,
        nom TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (filiere_id) REFERENCES filieres(id)
    )''')

    # 6. Table Modules
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        nom TEXT NOT NULL,
        coefficient REAL,
        credits INTEGER,
        semestre INTEGER,
        filiere_id INTEGER,
        niveau_id INTEGER,
        FOREIGN KEY (filiere_id) REFERENCES filieres(id),
        FOREIGN KEY (niveau_id) REFERENCES niveaux(id)
    )''') 

    # 7. Table Inscriptions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etudiant_id INTEGER,
        filiere_id INTEGER,
        niveau_id INTEGER,
        annee_academique TEXT,
        groupe TEXT,
        statut TEXT,
        date_inscription DATE,
        FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
        FOREIGN KEY (filiere_id) REFERENCES filieres(id),
        FOREIGN KEY (niveau_id) REFERENCES niveaux(id)
    )''') 

    # 8. Table Notes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etudiant_id INTEGER,
        module_id INTEGER,
        type_evaluation TEXT,
        note REAL CHECK(note >= 0 AND note <= 20),
        coefficient REAL,
        date_examen DATE,
        session TEXT,
        annee_academique TEXT,
        FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
        FOREIGN KEY (module_id) REFERENCES modules(id),
        UNIQUE(etudiant_id, module_id, type_evaluation, annee_academique, session)
    )
    ''')


    # 9. Table Absences
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS absences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etudiant_id INTEGER,
        module_id INTEGER,
        date_absence DATE,
        seance TEXT,
        justifiee INTEGER DEFAULT 0,
        motif TEXT,
        document_path TEXT,
        date_enregistrement DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
        FOREIGN KEY (module_id) REFERENCES modules(id)
    )''') 

    # 10. Table Enseignants
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS enseignants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matricule TEXT UNIQUE NOT NULL,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        specialite TEXT,
        email TEXT,
        telephone TEXT
    )''') 

    # 11. Table Affectations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS affectations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enseignant_id INTEGER,
        module_id INTEGER,
        groupe TEXT,
        annee_academique TEXT,
        FOREIGN KEY (enseignant_id) REFERENCES enseignants(id),
        FOREIGN KEY (module_id) REFERENCES modules(id)
    )''') 

    # 12. Table Parametres
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parametres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cle TEXT UNIQUE NOT NULL,
        valeur TEXT,
        description TEXT,
        type_donnee TEXT
    )''') 

    # 13. Table Logs (Traçabilité)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        table_affectee TEXT,
        enregistrement_id INTEGER,
        details TEXT,
        date_action DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''') 


    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès !")

if __name__ == "__main__":
    initialiser_bdd()