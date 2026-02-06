import sqlite3

DB = "gestion_etudiants.db"

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# --- GESTION DES FILIÈRES ---
def ajouter_filiere(code, nom, description):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO filieres (code, nom, description) VALUES (?, ?, ?)",
                     (code, nom, description))
        conn.commit()
        return True, "Filière ajoutée."
    except sqlite3.IntegrityError:
        return False, "Ce code existe déjà."
    finally:
        conn.close()

def recuperer_filieres():
    conn = get_db_connection()
    filieres = conn.execute("SELECT * FROM filieres").fetchall()
    conn.close()
    return filieres

# --- GESTION DES NIVEAUX ---
def recuperer_niveaux():
    conn = get_db_connection()
    niveaux = conn.execute("SELECT * FROM niveaux ORDER BY ordre").fetchall()
    conn.close()
    return niveaux

# --- GESTION DES MODULES ---
def obtenir_modules(): # Changé de 'recuperer_modules' pour correspondre à l'import
    conn = get_db_connection()
    query = "SELECT m.*, f.nom as filiere_nom FROM modules m JOIN filieres f ON m.filiere_id = f.id"
    modules = conn.execute(query).fetchall()
    conn.close()
    return modules

def ajouter_module(code, nom, coeff, credits, semestre, filiere_id, niveau_id):
    conn = get_db_connection()
    try:
        conn.execute("""INSERT INTO modules (code, nom, coefficient, credits, semestre, filiere_id, niveau_id) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (code, nom, coeff, credits, semestre, filiere_id, niveau_id))
        conn.commit()
        return True, "Module ajouté !"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# --- GESTION DES AFFECTATIONS (Table 11) ---
def obtenir_enseignants(): # Changé de 'recuperer_enseignants' pour correspondre à l'import
    conn = get_db_connection()
    profs = conn.execute("SELECT id, nom, prenom FROM enseignants").fetchall()
    conn.close()
    return profs

def attribuer_enseignant_module(enseignant_id, module_id, groupe, annee):
    conn = get_db_connection()
    try:
        query = "INSERT INTO affectations (enseignant_id, module_id, groupe, annee_academique) VALUES (?, ?, ?, ?)"
        conn.execute(query, (enseignant_id, module_id, groupe, annee))
        conn.commit()
        return True, "Affectation enregistrée !"
    except Exception as e:
        return False, f"Erreur SQL : {e}"
    finally:
        conn.close()

# --- CALENDRIER / PARAMETRES (Table 12) ---
def recuperer_calendrier():
    """Récupère les données de la table parametres (Table 12)"""
    conn = get_db_connection()
    try:
        # On force le nom des colonnes pour être sûr
        query = "SELECT cle, valeur, description FROM parametres WHERE type_donnee = 'DATE'"
        return conn.execute(query).fetchall()
    except Exception as e:
        print(f"Erreur lecture Table Parametres : {e}")
        return []
    finally:
        conn.close()

def ajouter_evenement_calendrier(libelle, date_valeur, description):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO parametres (cle, valeur, description, type_donnee) VALUES (?, ?, ?, 'DATE')",
                     (libelle, date_valeur, description))
        conn.commit()
        return True, "Date enregistrée !"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

recuperer_modules = obtenir_modules
recuperer_enseignants = obtenir_enseignants 

def recuperer_affectations_detaillees():
    """Récupère les affectations avec les noms réels (Table 11)"""
    conn = get_db_connection()
    query = """
        SELECT a.id, e.nom || ' ' || e.prenom as prof, m.nom as module, a.groupe, a.annee_academique
        FROM affectations a
        JOIN enseignants e ON a.enseignant_id = e.id
        JOIN modules m ON a.module_id = m.id
    """
    res = conn.execute(query).fetchall()
    conn.close()
    return res

def supprimer_affectation(id_affectation):
    """Supprime une affectation de la base (Table 11)"""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM affectations WHERE id = ?", (id_affectation,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur suppression : {e}")
        return False
    finally:
        conn.close()

def recuperer_absences_injustifiees():
    """
    Récupère la liste des absences où justifiee = 0 (Table 9)
    Jointure avec étudiants et modules pour avoir les noms au lieu des IDs.
    """
    conn = get_db_connection()
    try:
        # On récupère l'ID de l'absence, le nom de l'étudiant, le module et la date
        query = """
            SELECT a.id, e.nom || ' ' || e.prenom as etudiant, m.nom as module, a.date_absence as date
            FROM absences a
            JOIN etudiants e ON a.etudiant_id = e.id
            JOIN modules m ON a.module_id = m.id
            WHERE a.justifiee = 0
        """
        return conn.execute(query).fetchall()
    except Exception as e:
        print(f"Erreur SQL absences : {e}")
        return []
    finally:
        conn.close()

def justifier_absence(absence_id, motif, doc_path):
    """
    Met à jour le statut, le motif et le document d'une absence (Table 9).
    """
    conn = get_db_connection()
    try:
        query = """
            UPDATE absences 
            SET justifiee = 1, motif = ?, document_path = ? 
            WHERE id = ?
        """
        conn.execute(query, (motif, doc_path, absence_id))
        conn.commit()
        return True, "L'absence a été justifiée avec succès."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()