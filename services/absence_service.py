import sqlite3

DB = "gestion_etudiants.db"

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def enregistrer_absence(etudiant_id, module_id, date_absence, seance, motif=""):
    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO absences (etudiant_id, module_id, date_absence, seance, motif, justifiee)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (etudiant_id, module_id, date_absence, seance, motif))
        conn.commit()
        return True, "Absence enregistrée."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def recuperer_absences_etudiant(etudiant_id):
    conn = get_db_connection()
    # On fait une jointure pour avoir le nom du module au lieu de juste l'ID
    query = """
        SELECT a.date_absence, m.nom as module_nom, a.seance, a.justifiee, a.motif 
        FROM absences a 
        JOIN modules m ON a.module_id = m.id 
        WHERE a.etudiant_id = ?
        ORDER BY a.date_absence DESC
    """
    absences = conn.execute(query, (etudiant_id,)).fetchall()
    conn.close()
    return absences

def justifier_absence(etudiant_id, date_abs, module_nom):
    """Met à jour le statut d'une absence en 'Justifiée'."""
    conn = get_db_connection()
    try:
        # On utilise l'id étudiant, la date et le nom du module pour trouver la bonne ligne
        conn.execute("""
            UPDATE absences 
            SET justifiee = 1 
            WHERE etudiant_id = ? AND date_absence = ? 
            AND module_id = (SELECT id FROM modules WHERE nom = ?)
        """, (etudiant_id, date_abs, module_nom))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur justification: {e}")
        return False
    finally:
        conn.close()

def recuperer_stats_absences():
    """Compte les absences par module pour toute l'école"""
    conn = get_db_connection()
    query = """
        SELECT m.nom, COUNT(a.id) as total 
        FROM modules m 
        LEFT JOIN absences a ON m.id = a.module_id 
        GROUP BY m.nom
        ORDER BY total DESC
    """
    stats = conn.execute(query).fetchall()
    conn.close()
    return stats