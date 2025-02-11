# Projet-Test-Eval

## 📌 Description du projet
**Projet-Test-Eval** est une application web éducative développée en **Python** avec **Flask**, destinée à l'évaluation et à l'analyse des **compétences non techniques (soft skills)** des ingénieurs. L'application permet aux utilisateurs de remplir un formulaire, d'envoyer leurs réponses pour analyse par un **module d'intelligence artificielle**, et de consulter les résultats.

### ✨ Fonctionnalités principales
- Interface web permettant aux utilisateurs de remplir un questionnaire d'évaluation.
- Analyse automatique des réponses grâce à un module d'IA (`AiModule`).
- Stockage des résultats dans une base de données SQLite (`softskills.db`).
- Affichage des résultats via une interface utilisateur simple et intuitive.

## 📂 Structure du projet
- **`app.py`** : Point d'entrée principal de l'application Flask.
- **`ai_module.py`** : Module d'IA utilisé pour analyser les réponses des utilisateurs.
- **`requirements.txt`** : Liste des dépendances Python nécessaires pour exécuter le projet.
- **`soft_skills_formation_ingenieur.md`** : Documentation sur les compétences non techniques évaluées.
- **`softskills.db`** : Base de données SQLite contenant les réponses des utilisateurs.
- **`base-de-donnees-des-scenarios.txt`** : Scénarios de test pour l'entraînement et l'analyse.
- **`templates/`** : Contient les fichiers HTML pour l'interface utilisateur.
- **`instance/`** : Dossier utilisé par Flask pour stocker des fichiers temporaires.
- **`venv/`** : Environnement virtuel Python (optionnel, recommandé).

## 🚀 Installation et utilisation

### 📥 1. Prérequis
Avant de commencer, assure-toi d'avoir installé **Python 3.x** et **pip** sur ton système.

### ⚙️ 2. Installation
1. **Clone ce dépôt** :
   ```bash
   git clone https://github.com/ENNAJI/Projet-Test-Eval.git
   cd Projet-Test-Eval
   ```
2. **Créer un environnement virtuel (recommandé)** :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur macOS/Linux
   venv\Scripts\activate  # Sur Windows
   ```
3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

### ▶️ 3. Lancer l'application
Exécute la commande suivante :
```bash
python app.py
```
L'application sera accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

### 🛠 4. Personnalisation et développement
- Pour modifier l'interface, édite les fichiers HTML dans le dossier `templates/`.
- Pour ajouter des fonctionnalités, mets à jour `app.py` ou `ai_module.py`.
- La base de données SQLite (`softskills.db`) peut être manipulée avec SQLite3.

## 📜 Licence
Ce projet est sous licence **MIT**. Tu es libre de l'utiliser et de le modifier.

## 🤝 Contribuer
Les contributions sont les bienvenues ! N'hésite pas à **forker** le projet et à proposer des améliorations via une **pull request**.

---

📧 **Contact** : Si tu as des questions, n'hésite pas à me contacter sur GitHub ou par email !

