# projet_gestion_etudiants

Ce projet est une application de bureau développée en Python (Tkinter) pour la gestion d'un établissement d'enseignement supérieur. L'architecture repose sur un modèle modulaire séparant les vues (UI) des services (Logique SQL).

#### Fonctionnalités Principales
Gestion de la Structure
Configuration Filières et Niveaux : Paramétrage de l'organisation académique (Tables 3 et 4).

Modules et Affectations : Attribution des unités d'enseignement et gestion des intervenants (Tables 6 et 11).

Calendrier Académique : Gestion des dates clés et des paramètres système via la table Paramètres (Table 12).

Suivi des Étudiants et Absences
Administration : Inscription et gestion des fiches détaillées (Table 1).

#### Gestion des Absences :

Pointage par séance et par module.

Système de justification avec saisie du motif et stockage du chemin vers le document justificatif (Table 9).

#### Résultats et Statistiques
Saisie des Notes : Enregistrement des évaluations par module.

Reporting : Génération de bulletins de notes au format PDF.

Analyses : Visualisation des classements et des statistiques d'absentéisme par module.

#### Installation et Utilisation
Prérequis
Python 3.x

Bibliothèques requises : tkinter, sqlite3, matplotlib, reportlab

Lancement
Initialisation de la base de données (à n'exécuter qu'une fois) :

Bash: 
python database/init_db.py


Exécution de l'application :

Bash:
python main.py

Architecture du Projet

/views : Interfaces graphiques classées par module (Étudiants, Absences, Notes, Admin).

/services : Logique métier et requêtes SQL (CRUD).

/database : Scripts d'initialisation et fichier de base de données SQLite.

main.py : Point d'entrée de l'application avec gestion de l'authentification.

Auteure :
KAVUANSIKO Angelikia
CHLIQUI Leora
MISTRY Ekta
