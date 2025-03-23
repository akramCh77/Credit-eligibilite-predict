import numpy as np
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
import pickle
import logging
import os
from datetime import datetime

# Configuration de l'application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_flash_messages')

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Chargement du modèle
try:
    model = pickle.load(open('model.pkl', 'rb'))
    logger.info("Modèle chargé avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement du modèle: {str(e)}")
    model = None

# Dictionnaires pour convertir les entrées catégoriques en nombres
GENDER_MAP = {"male": 1, "female": 0, "homme": 1, "femme": 0}
MARRIED_MAP = {"yes": 1, "no": 0, "oui": 1, "non": 0}
EDUCATION_MAP = {"graduate": 1, "not graduate": 0, "diplômé": 1, "non diplômé": 0}
SELF_EMPLOYED_MAP = {"yes": 1, "no": 0, "oui": 1, "non": 0}
PROPERTY_AREA_MAP = {"urban": 2, "semiurban": 1, "rural": 0, "urbaine": 2, "semi-urbaine": 1, "rurale": 0}
CREDIT_HISTORY_MAP = {1: 1, 0: 0, "satisfaisant": 1, "non satisfaisant": 0}

@app.route('/')
def home():
    """Page d'accueil - Affiche le formulaire de prédiction"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Traite les données du formulaire et renvoie une prédiction
    
    Returns:
        Template avec le résultat de la prédiction ou message d'erreur
        Les valeurs du formulaire sont conservées
    """
    if model is None:
        flash("Erreur: Le modèle n'a pas pu être chargé.", "danger")
        return render_template('index.html')
    
    try:
        # Récupération et prétraitement des données formulaire
        features = extract_features_from_form(request.form)
        
        # Validation des données
        if not validate_features(features):
            flash("Erreur: Certaines entrées sont invalides.", "warning")
            return render_template('index.html')
        
        # Préparation des données pour la prédiction
        final_features = [np.array(features)]
        
        # Prédiction
        prediction = model.predict(final_features)
        output = int(prediction[0])  # Convertir en entier pour éviter les problèmes de comparaison

        # Déterminer le texte de la prédiction
        prediction_text = (
        "Cette personne est éligible à un crédit bancaire"
        if output == 1 
        else "Cette personne n'est pas éligible à un crédit bancaire"
        )

        # Logging de la prédiction
        logger.info(f"Prédiction effectuée: {output} - {prediction_text}")

        # Renvoyer le template avec les résultats et les données du formulaire
        return render_template(
        'index.html', 
         prediction_text=prediction_text,
         timestamp=datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
        )

        
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {str(e)}")
        flash(f"Une erreur s'est produite lors du traitement: {str(e)}", "danger")
        return render_template('index.html')

@app.route('/reset', methods=['GET'])
def reset_form():
    """
    Réinitialise le formulaire en redirigeant vers la page d'accueil
    
    Returns:
        Redirection vers la page d'accueil avec formulaire vide
    """
    return redirect(url_for('home'))

@app.route('/predict_api', methods=['POST'])
def predict_api():
    if model is None:
        return jsonify({"error": "Le modèle n'a pas pu être chargé"}), 500

    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "Aucune donnée reçue"}), 400

        # Gestion des valeurs catégoriques
        gender_value = data.get("Gender", "")
        gender_mapped = GENDER_MAP.get(gender_value.lower() if isinstance(gender_value, str) else "", 0)

        married_value = data.get("Married", "")
        married_mapped = MARRIED_MAP.get(married_value.lower() if isinstance(married_value, str) else "", 0)

        dependents = data.get("Dependents", "0")
        if isinstance(dependents, str):
            dependents = dependents.replace("3+", "3")
        try:
            dependents = int(dependents)
        except ValueError:
            return jsonify({"status": "error", "message": "Valeur invalide pour Dependents"}), 400

        education_mapped = EDUCATION_MAP.get(data.get("Education", "").lower(), 0)
        self_employed_mapped = SELF_EMPLOYED_MAP.get(data.get("Self_Employed", "").lower(), 0)

        credit_history_value = data.get("Credit_History", 0)
        if isinstance(credit_history_value, str):
            credit_history_mapped = CREDIT_HISTORY_MAP.get(credit_history_value.lower(), 0)
        else:
            credit_history_mapped = CREDIT_HISTORY_MAP.get(int(credit_history_value), 0)

        property_area_mapped = PROPERTY_AREA_MAP.get(data.get("Property_Area", "").lower(), 0)

        # Gestion des valeurs numériques
        try:
            applicant_income = float(data.get("ApplicantIncome", 0))
            coapplicant_income = float(data.get("CoapplicantIncome", 0))
            loan_amount = float(data.get("LoanAmount", 0))
            loan_amount_term = float(data.get("Loan_Amount_Term", 0))
        except ValueError:
            return jsonify({"status": "error", "message": "Valeurs numériques invalides"}), 400

        # Construction des features
        features = [
            gender_mapped,
            married_mapped,
            dependents,
            education_mapped,
            self_employed_mapped,
            applicant_income,
            coapplicant_income,
            loan_amount,
            loan_amount_term,
            credit_history_mapped,
            property_area_mapped,
        ]

        # Prédiction
        prediction = model.predict([np.array(features)])
        output = int(prediction[0])

        response = {
            "status": "success",
            "prediction": output,
            "message": "Cette personne est éligible à un crédit bancaire" if output == 1 else "Cette personne n'est pas éligible à un crédit bancaire",
            "timestamp": datetime.now().isoformat()
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Erreur API: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


def extract_features_from_form(form_data):
    """
    Extrait et convertit les caractéristiques du formulaire
    
    Args:
        form_data: Données du formulaire
        
    Returns:
        list: Liste des caractéristiques extraites et converties
    """
    features = []
    
    # Traitement de chaque champ du formulaire
    features.append(GENDER_MAP.get(form_data.get("Gender", "").lower(), 0))
    features.append(MARRIED_MAP.get(form_data.get("Married", "").lower(), 0))
    
    # Gestion des personnes à charge
    dependents = form_data.get("Dependents", "0").lower()
    if dependents == "3+":
        features.append(3)
    else:
        try:
            features.append(int(dependents))
        except ValueError:
            features.append(0)
    
    features.append(EDUCATION_MAP.get(form_data.get("Education", "").lower(), 0))
    features.append(SELF_EMPLOYED_MAP.get(form_data.get("Self_Employed", "").lower(), 0))
    features.append(CREDIT_HISTORY_MAP.get(int(form_data.get("Credit_History", 0)), 0))

    
    # Conversion des valeurs numériques
    numeric_fields = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term"]
    for field in numeric_fields:
        try:
            features.append(float(form_data.get(field, 0)))
        except ValueError:
            features.append(0)
    
    features.append(PROPERTY_AREA_MAP.get(form_data.get("Property_Area", "").lower(), 0))
    
    return features

def validate_features(features):
    """
    Valide les caractéristiques extraites
    
    Args:
        features: Liste des caractéristiques à valider
        
    Returns:
        bool: True si valide, False sinon
    """
    # Vérification de la longueur attendue
    expected_length = 11  # Ajustez selon votre modèle
    if len(features) != expected_length:
        logger.warning(f"Nombre de caractéristiques incorrect: {len(features)} au lieu de {expected_length}")
        return False
    
    # Vérification des valeurs numériques
    for i, feature in enumerate(features[6:10]):  # indices des caractéristiques numériques
        if feature < 0:
            logger.warning(f"Valeur négative détectée à l'indice {i+6}: {feature}")
            return False
    
    return True

# Routes supplémentaires
@app.route('/about')
def about():
    """Page d'information sur l'application"""
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    """Gestion des erreurs 404"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Gestion des erreurs 500"""
    logger.error(f"Erreur serveur: {str(e)}")
    return render_template('500.html'), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'True') == 'True')