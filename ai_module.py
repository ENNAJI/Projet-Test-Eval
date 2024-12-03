import openai
import os
from dotenv import load_dotenv
from flask import current_app
import time
from typing import List, Dict

# Charger les variables d'environnement du fichier .env
load_dotenv()

# Configurer la clé API OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

if not openai.api_key:
    raise ValueError("La clé API OpenAI n'est pas configurée. Veuillez vérifier votre fichier .env")

# Questions de secours par défaut
DEFAULT_QUESTIONS = {
    "Communication": [
        "Décrivez une situation où vous avez dû expliquer un concept technique complexe à un non-expert.",
        "Comment gérez-vous les désaccords dans une équipe ?",
        "Parlez d'une présentation que vous avez faite et qui a été particulièrement réussie."
    ],
    "Leadership": [
        "Décrivez une situation où vous avez dû prendre l'initiative sur un projet.",
        "Comment motivez-vous les membres de votre équipe ?",
        "Parlez d'un conflit que vous avez résolu dans votre équipe."
    ],
    "Adaptabilité": [
        "Comment réagissez-vous face à un changement imprévu dans un projet ?",
        "Décrivez une situation où vous avez dû apprendre rapidement une nouvelle technologie.",
        "Comment gérez-vous le stress dans des situations complexes ?"
    ]
}

def initialize_openai():
    pass

def generate_personalized_questions(candidate_profile, competence):
    """
    Génère des questions personnalisées basées sur le profil du candidat et la compétence.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Vous êtes un expert en évaluation des soft skills pour les formateurs en ingénierie."},
                {"role": "user", "content": f"""
                Générez une question d'évaluation pertinente pour la compétence '{competence.nom}' 
                adaptée au profil suivant :
                - Expérience : {candidate_profile.get('experience', 'Non spécifié')}
                - Domaine : {candidate_profile.get('domaine', 'Non spécifié')}
                - Niveau : {candidate_profile.get('niveau', 'Non spécifié')}
                
                La question doit être basée sur un scénario réaliste et permettre d'évaluer 
                efficacement la compétence.
                """}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la génération de questions : {str(e)}")
        return None

def analyze_responses(candidate_responses, competence):
    """
    Analyse les réponses du candidat pour une compétence donnée et fournit une évaluation détaillée.
    """
    try:
        # Formatage des réponses pour l'analyse
        responses_text = "\n".join([
            f"Q: {resp.question.texte}\nR: {resp.reponse_texte}"
            for resp in candidate_responses
        ])

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Vous êtes un expert en évaluation des soft skills."},
                {"role": "user", "content": f"""
                Analysez les réponses suivantes pour la compétence '{competence.nom}' :
                
                {responses_text}
                
                Fournissez :
                1. Un score sur 5 (format numérique)
                2. Une analyse détaillée des points forts
                3. Des recommandations d'amélioration
                
                Format de réponse : JSON
                {{
                    "score": X,
                    "points_forts": ["point1", "point2", ...],
                    "recommandations": ["rec1", "rec2", ...],
                    "analyse_detaillee": "texte"
                }}
                """}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'analyse des réponses : {str(e)}")
        return None

def generate_specialty_questions(specialite: str, competence: str, num_questions: int = 3) -> List[str]:
    """
    Génère des questions spécialisées pour une compétence donnée.
    Inclut la gestion des erreurs et un système de fallback.
    """
    try:
        # Tentative de génération de questions via l'API OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Vous êtes un expert en évaluation de soft skills."},
                {"role": "user", "content": f"Générez {num_questions} questions d'entretien pour évaluer la compétence '{competence}' pour un candidat en {specialite}. Les questions doivent être spécifiques au domaine."}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        # Extraction et formatage des questions
        questions = response.choices[0].message['content'].strip().split('\n')
        questions = [q.strip('123456789.- ') for q in questions if q.strip()]
        return questions[:num_questions]

    except openai.error.RateLimitError:
        # En cas de dépassement de limite, utiliser les questions par défaut
        print(f"Rate limit atteint pour OpenAI API. Utilisation des questions par défaut pour {competence}")
        return DEFAULT_QUESTIONS.get(competence, DEFAULT_QUESTIONS["Communication"])[:num_questions]
    
    except Exception as e:
        print(f"Erreur lors de la génération des questions: {str(e)}")
        return DEFAULT_QUESTIONS.get(competence, DEFAULT_QUESTIONS["Communication"])[:num_questions]

def analyze_response(specialite: str, competence: str, reponse: str) -> str:
    """
    Analyse la réponse d'un candidat avec gestion des erreurs.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Vous êtes un expert en évaluation de soft skills."},
                {"role": "user", "content": f"Analysez la réponse suivante pour la compétence '{competence}' d'un candidat en {specialite}. Réponse: {reponse}"}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message['content'].strip()

    except openai.error.RateLimitError:
        # En cas de dépassement de limite, retourner une analyse générique
        return f"L'analyse n'a pas pu être effectuée en raison des limites de l'API. Veuillez évaluer la réponse manuellement."
    
    except Exception as e:
        print(f"Erreur lors de l'analyse de la réponse: {str(e)}")
        return "Une erreur est survenue lors de l'analyse. Veuillez évaluer la réponse manuellement."
