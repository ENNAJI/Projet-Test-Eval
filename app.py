from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import openai

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'API OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configuration de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soft_skills.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Classe de base pour les modèles SQLAlchemy
class Base(DeclarativeBase):
    pass

# Initialisation de SQLAlchemy
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Ajout des méthodes de requête aux modèles
Base.query = db.session.query_property()

# Modèles de données
class SoftSkillCategorie(Base):
    __tablename__ = 'soft_skill_categorie'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    competences = db.relationship('Competence', backref='categorie', lazy=True)

class Competence(Base):
    __tablename__ = 'competence'
    id = db.Column(db.Integer, primary_key=True)
    categorie_id = db.Column(db.Integer, db.ForeignKey('soft_skill_categorie.id'), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    scores = db.relationship('ScoreDetaille', backref='competence', lazy=True)
    questions = db.relationship('Question', backref='competence', lazy=True)

class Question(Base):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    competence_id = db.Column(db.Integer, db.ForeignKey('competence.id'), nullable=False)
    texte = db.Column(db.Text, nullable=False)
    type_question = db.Column(db.String(50), default='choix_multiple')
    reponses = db.relationship('ReponseOption', backref='question', lazy=True)

class ReponseOption(Base):
    __tablename__ = 'reponse_option'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    texte = db.Column(db.Text, nullable=False)
    score_associe = db.Column(db.Float, nullable=False)

class Evaluateur(Base):
    __tablename__ = 'evaluateur'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50))
    evaluations = db.relationship('Evaluation', backref='evaluateur', lazy=True)

class Candidat(Base):
    __tablename__ = 'candidat'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    experience = db.Column(db.Integer)
    domaine = db.Column(db.String(100))
    niveau = db.Column(db.String(50))
    specialite = db.Column(db.String(100))
    evaluations = db.relationship('Evaluation', backref='candidat', lazy=True)

class Evaluation(Base):
    __tablename__ = 'evaluation'
    id = db.Column(db.Integer, primary_key=True)
    date_evaluation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    evaluateur_id = db.Column(db.Integer, db.ForeignKey('evaluateur.id'), nullable=False)
    candidat_id = db.Column(db.Integer, db.ForeignKey('candidat.id'), nullable=False)
    scores = db.relationship('Score', backref='evaluation', lazy=True)
    scores_detailles = db.relationship('ScoreDetaille', backref='evaluation', lazy=True)
    type_evaluation = db.Column(db.String(50), default='simple')
    commentaire_general = db.Column(db.Text)

class Score(Base):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluation.id'), nullable=False)
    competence = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    commentaire = db.Column(db.Text)

class ScoreDetaille(Base):
    __tablename__ = 'score_detaille'
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluation.id'), nullable=False)
    competence_id = db.Column(db.Integer, db.ForeignKey('competence.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    commentaire = db.Column(db.Text)

class ReponseCandidat(Base):
    __tablename__ = 'reponse_candidat'
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluation.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    reponse_option_id = db.Column(db.Integer, db.ForeignKey('reponse_option.id'), nullable=True)
    reponse_texte = db.Column(db.Text, nullable=True)
    score_calcule = db.Column(db.Float, nullable=True)

# Liste des spécialités EMSI
SPECIALITES_EMSI = [
    "Génie Informatique",
    "Génie Industriel",
    "Génie Civil",
    "Génie Réseaux et Systèmes",
    "Génie Financier",
    "Cybersécurité",
    "Intelligence Artificielle",
    "Cloud Computing",
    "DevOps",
    "Big Data Analytics",
    "IoT et Systèmes Embarqués",
    "Développement Web et Mobile",
    "Architecture Logicielle",
    "Sécurité des Systèmes",
    "Management de Projets IT",
    "Innovation et Entrepreneuriat"
]

def test_openai_connection():
    """Test la connexion à l'API OpenAI"""
    try:
        # Test simple avec une requête minimale
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        return True
    except Exception as e:
        print(f"Erreur de connexion OpenAI: {str(e)}")
        return False

# Routes principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluation/nouvelle', methods=['GET', 'POST'])
def nouvelle_evaluation():
    if request.method == 'POST':
        try:
            # Création du candidat
            candidat = Candidat(
                nom=request.form['nom'],
                prenom=request.form['prenom'],
                email=request.form['email'],
                specialite=request.form['specialite']
            )
            db.session.add(candidat)
            db.session.flush()  # Pour obtenir l'ID du candidat

            # Création de l'évaluation
            evaluation = Evaluation(
                evaluateur_id=1,  # À modifier selon votre système d'authentification
                candidat_id=candidat.id
            )
            db.session.add(evaluation)
            db.session.flush()

            # Ajout des scores
            scores = [
                Score(
                    evaluation_id=evaluation.id,
                    competence='Communication',
                    score=float(request.form['comm_explication']),
                    commentaire=request.form['comm_commentaire']
                ),
                Score(
                    evaluation_id=evaluation.id,
                    competence='Pédagogie',
                    score=float(request.form['ped_structure']),
                    commentaire=request.form['ped_commentaire']
                ),
                Score(
                    evaluation_id=evaluation.id,
                    competence='Leadership',
                    score=float(request.form['lead_motivation']),
                    commentaire=request.form['lead_commentaire']
                )
            ]
            db.session.bulk_save_objects(scores)
            db.session.commit()

            flash('Évaluation enregistrée avec succès!', 'success')
            return redirect(url_for('resultats'))

        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de l\'enregistrement de l\'évaluation.', 'error')
            print(f"Erreur: {str(e)}")
            return render_template('evaluation_form.html')

    return render_template('evaluation_form.html')

@app.route('/evaluation_sans_ia', methods=['GET', 'POST'])
def evaluation_sans_ia():
    if request.method == 'POST':
        try:
            # Création du candidat
            candidat = Candidat(
                nom=request.form['nom'],
                prenom=request.form['prenom'],
                email=request.form['email'],
                specialite=request.form['specialite'],
                experience=request.form.get('experience'),
                niveau=request.form.get('niveau')
            )
            db.session.add(candidat)
            db.session.flush()

            # Création de l'évaluateur (à remplacer par un système d'authentification)
            evaluateur = Evaluateur.query.first()
            if not evaluateur:
                evaluateur = Evaluateur(
                    nom="Évaluateur Test",
                    email="evaluateur@test.com",
                    role="Professeur"
                )
                db.session.add(evaluateur)
                db.session.flush()

            # Création de l'évaluation
            evaluation = Evaluation(
                evaluateur_id=evaluateur.id,
                candidat_id=candidat.id,
                type_evaluation='detaillee_sans_ia'
            )
            db.session.add(evaluation)
            db.session.commit()

            flash('Candidat enregistré avec succès!', 'success')
            return redirect(url_for('evaluation', candidat_id=candidat.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'enregistrement : {str(e)}', 'danger')

    categories = SoftSkillCategorie.query.all()
    return render_template('evaluation_sans_ia.html', 
                         categories=categories,
                         specialites=SPECIALITES_EMSI)

@app.route('/evaluation_avec_ia', methods=['GET', 'POST'])
def evaluation_avec_ia():
    if request.method == 'POST':
        try:
            # Test de la connexion OpenAI
            if not test_openai_connection():
                flash('La connexion à l\'API OpenAI n\'est pas disponible. Redirection vers l\'évaluation sans IA.', 'warning')
                return redirect(url_for('evaluation_sans_ia'))

            # Création du candidat
            candidat = Candidat(
                nom=request.form['nom'],
                prenom=request.form['prenom'],
                email=request.form['email'],
                specialite=request.form['specialite'],
                experience=request.form.get('experience'),
                niveau=request.form.get('niveau')
            )
            db.session.add(candidat)
            db.session.flush()

            # Création de l'évaluateur (à remplacer par un système d'authentification)
            evaluateur = Evaluateur.query.first()
            if not evaluateur:
                evaluateur = Evaluateur(
                    nom="Évaluateur Test",
                    email="evaluateur@test.com",
                    role="Professeur"
                )
                db.session.add(evaluateur)
                db.session.flush()

            # Création de l'évaluation
            evaluation = Evaluation(
                evaluateur_id=evaluateur.id,
                candidat_id=candidat.id,
                type_evaluation='detaillee_avec_ia'
            )
            db.session.add(evaluation)
            db.session.commit()

            flash('Candidat enregistré avec succès!', 'success')
            return redirect(url_for('evaluation', candidat_id=candidat.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'enregistrement : {str(e)}', 'danger')
            return redirect(url_for('evaluation_sans_ia'))

    # Test de la connexion OpenAI avant d'afficher le formulaire
    if not test_openai_connection():
        flash('La connexion à l\'API OpenAI n\'est pas disponible. Redirection vers l\'évaluation sans IA.', 'warning')
        return redirect(url_for('evaluation_sans_ia'))

    return render_template('evaluation_avec_ia.html', specialites=SPECIALITES_EMSI)

@app.route('/evaluation/<int:candidat_id>', methods=['GET', 'POST'])
def evaluation(candidat_id):
    candidat = Candidat.query.get_or_404(candidat_id)
    if request.method == 'POST':
        # Récupération des réponses
        reponses = []
        for key, value in request.form.items():
            if key.startswith('question_'):
                question_id = int(key.split('_')[1])
                reponse = ReponseCandidat(
                    candidat_id=candidat_id,
                    question_id=question_id,
                    reponse_texte=value
                )
                reponses.append(reponse)
        
        # Création de l'évaluation
        evaluation = Evaluation(
            candidat_id=candidat_id,
            date_evaluation=datetime.now()
        )
        db.session.add(evaluation)
        
        # Analyse des réponses avec l'IA
        from ai_module import analyze_responses
        for competence in Competence.query.all():
            competence_reponses = [r for r in reponses if r.question.competence_id == competence.id]
            if competence_reponses:
                analyse = analyze_responses(competence_reponses, competence)
                if analyse:
                    score_detaille = ScoreDetaille(
                        evaluation_id=evaluation.id,
                        competence_id=competence.id,
                        score=analyse.get('score', 0),
                        commentaire=analyse.get('analyse_detaillee', '')
                    )
                    db.session.add(score_detaille)
        
        db.session.commit()
        return redirect(url_for('detail_evaluation', evaluation_id=evaluation.id))

    # Génération de questions personnalisées
    from ai_module import generate_personalized_questions
    competences = Competence.query.all()
    questions_personnalisees = {}
    candidate_profile = {
        'experience': candidat.experience,
        'domaine': candidat.domaine,
        'niveau': candidat.niveau
    }
    
    for competence in competences:
        question = generate_personalized_questions(candidate_profile, competence)
        if question:
            questions_personnalisees[competence.id] = question

    return render_template('evaluation_detaillee.html', 
                         candidat=candidat,
                         competences=competences,
                         questions_personnalisees=questions_personnalisees)

@app.route('/evaluation/<int:evaluation_id>')
def detail_evaluation(evaluation_id):
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    return render_template('detail_evaluation.html', evaluation=evaluation)

@app.route('/api/scores/<int:candidat_id>')
def get_scores(candidat_id):
    # Logique pour récupérer les scores d'un candidat
    pass

def get_competence_id(categorie, competence_nom):
    comp = Competence.query.join(SoftSkillCategorie).filter(
        SoftSkillCategorie.nom.ilike(f"%{categorie}%"),
        Competence.nom.ilike(f"%{competence_nom}%")
    ).first()
    return comp.id if comp else None

@app.route('/resultats')
def resultats():
    # Récupération des filtres
    specialite = request.args.get('specialite', '')
    periode = request.args.get('periode', 'all')

    # Construction de la requête de base
    query = db.session.query(Evaluation).join(Candidat)

    # Application des filtres
    if specialite:
        query = query.filter(Candidat.specialite == specialite)
    
    if periode != 'all':
        today = datetime.utcnow()
        if periode == 'month':
            delta = timedelta(days=30)
        elif periode == 'quarter':
            delta = timedelta(days=90)
        elif periode == 'year':
            delta = timedelta(days=365)
        query = query.filter(Evaluation.date_evaluation >= (today - delta))

    # Récupération des évaluations
    evaluations = query.order_by(Evaluation.date_evaluation.desc()).all()

    # Calcul des scores moyens pour chaque évaluation
    for evaluation in evaluations:
        scores = [score.score for score in evaluation.scores]
        evaluation.score_moyen = sum(scores) / len(scores) if scores else 0

    # Préparation des données pour les graphiques
    competences = ['Communication', 'Pédagogie', 'Leadership']
    scores_par_competence = {comp: [] for comp in competences}

    for evaluation in evaluations:
        for score in evaluation.scores:
            if score.competence in scores_par_competence:
                scores_par_competence[score.competence].append(score.score)

    # Données pour le graphique radar
    radar_data = {
        'competences': competences,
        'scores': [
            sum(scores_par_competence[comp]) / len(scores_par_competence[comp])
            if scores_par_competence[comp] else 0
            for comp in competences
        ]
    }

    # Données pour le box plot
    boxplot_data = [{
        'type': 'box',
        'name': comp,
        'y': scores,
        'boxpoints': 'outliers'
    } for comp, scores in scores_par_competence.items()]

    # Liste des spécialités pour le filtre
    specialites = db.session.query(Candidat.specialite).distinct().all()
    specialites = [s[0] for s in specialites if s[0]]

    return render_template('resultats.html',
                         evaluations=evaluations,
                         specialites=specialites,
                         selected_specialite=specialite,
                         radar_data=radar_data,
                         boxplot_data=boxplot_data)

@app.route('/evaluation_detaillee_scenario')
def evaluation_detaillee_scenario():
    return render_template('Evaluation_détaillée_avec_scenarion.html')

# Routes pour les scénarios
@app.route('/get-scenarios')
def get_scenarios():
    try:
        with open('base-de-donnees-des-scenarios.txt', 'r', encoding='utf-8') as file:
            scenarios = json.load(file)
        return jsonify(scenarios)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def init_database():
    """Initialise la base de données et ses données"""
    with app.app_context():
        print("Création des tables...")
        db.create_all()
        
        print("Vérification des données initiales...")
        if not SoftSkillCategorie.query.first():
            print("Initialisation des données de base...")
            init_soft_skills()
            print("Données initialisées avec succès!")
        else:
            print("Les données existent déjà.")

def reset_database():
    """Supprime et recrée la base de données avec les données initiales"""
    with app.app_context():
        print("Création des tables...")
        Base.metadata.drop_all(bind=db.engine)
        Base.metadata.create_all(bind=db.engine)
        
        print("Initialisation des données...")
        init_soft_skills()
        print("Base de données réinitialisée avec succès!")

def init_soft_skills():
    """Initialise les catégories de soft skills et leurs compétences"""
    print("Initialisation des soft skills...")
    
    # Catégorie 1: Communication
    communication = SoftSkillCategorie(
        nom="Communication",
        description="Capacité à transmettre des informations clairement et efficacement"
    )
    db.session.add(communication)
    db.session.flush()

    competences_communication = [
        Competence(
            categorie_id=communication.id,
            nom="Expression Orale",
            description="Capacité à s'exprimer clairement et de manière structurée"
        ),
        Competence(
            categorie_id=communication.id,
            nom="Écoute Active",
            description="Capacité à comprendre et à répondre de manière appropriée"
        ),
        Competence(
            categorie_id=communication.id,
            nom="Communication Écrite",
            description="Capacité à rédiger de manière claire et professionnelle"
        )
    ]
    db.session.add_all(competences_communication)

    # Catégorie 2: Leadership
    leadership = SoftSkillCategorie(
        nom="Leadership",
        description="Capacité à guider et motiver une équipe vers des objectifs communs"
    )
    db.session.add(leadership)
    db.session.flush()

    competences_leadership = [
        Competence(
            categorie_id=leadership.id,
            nom="Prise de Décision",
            description="Capacité à prendre des décisions éclairées et responsables"
        ),
        Competence(
            categorie_id=leadership.id,
            nom="Gestion d'Équipe",
            description="Capacité à coordonner et motiver une équipe"
        ),
        Competence(
            categorie_id=leadership.id,
            nom="Vision Stratégique",
            description="Capacité à définir et communiquer des objectifs à long terme"
        )
    ]
    db.session.add_all(competences_leadership)

    # Catégorie 3: Résolution de Problèmes
    problem_solving = SoftSkillCategorie(
        nom="Résolution de Problèmes",
        description="Capacité à analyser et résoudre des situations complexes"
    )
    db.session.add(problem_solving)
    db.session.flush()

    competences_problem_solving = [
        Competence(
            categorie_id=problem_solving.id,
            nom="Analyse Critique",
            description="Capacité à évaluer objectivement les situations"
        ),
        Competence(
            categorie_id=problem_solving.id,
            nom="Créativité",
            description="Capacité à proposer des solutions innovantes"
        ),
        Competence(
            categorie_id=problem_solving.id,
            nom="Gestion de Crise",
            description="Capacité à gérer efficacement les situations d'urgence"
        )
    ]
    db.session.add_all(competences_problem_solving)

    # Catégorie 4: Travail d'Équipe
    teamwork = SoftSkillCategorie(
        nom="Travail d'Équipe",
        description="Capacité à collaborer efficacement avec les autres"
    )
    db.session.add(teamwork)
    db.session.flush()

    competences_teamwork = [
        Competence(
            categorie_id=teamwork.id,
            nom="Collaboration",
            description="Capacité à travailler efficacement avec les autres"
        ),
        Competence(
            categorie_id=teamwork.id,
            nom="Gestion des Conflits",
            description="Capacité à résoudre les désaccords de manière constructive"
        ),
        Competence(
            categorie_id=teamwork.id,
            nom="Esprit d'Équipe",
            description="Capacité à contribuer positivement à la dynamique de groupe"
        )
    ]
    db.session.add_all(competences_teamwork)

    # Catégorie 5: Adaptabilité
    adaptability = SoftSkillCategorie(
        nom="Adaptabilité",
        description="Capacité à s'adapter aux changements et nouvelles situations"
    )
    db.session.add(adaptability)
    db.session.flush()

    competences_adaptability = [
        Competence(
            categorie_id=adaptability.id,
            nom="Flexibilité",
            description="Capacité à s'ajuster aux changements"
        ),
        Competence(
            categorie_id=adaptability.id,
            nom="Apprentissage Continu",
            description="Capacité à acquérir de nouvelles compétences"
        ),
        Competence(
            categorie_id=adaptability.id,
            nom="Gestion du Changement",
            description="Capacité à gérer et faciliter les transitions"
        )
    ]
    db.session.add_all(competences_adaptability)

    # Commit final
    try:
        db.session.commit()
        print("Données initiales ajoutées avec succès!")
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de l'initialisation des données : {str(e)}")
        raise

# Point d'entrée de l'application
if __name__ == '__main__':
    try:
        print("Réinitialisation complète de la base de données...")
        reset_database()
        print("Démarrage de l'application...")
        app.run(debug=True)
    except Exception as e:
        print(f"Erreur lors de l'initialisation : {str(e)}")
