# Credit Eligibility Prediction

## Description
Cette application web permet de prédire l'éligibilité d'une personne à un crédit bancaire en fonction de plusieurs critères tels que le revenu, l'historique de crédit, l'état matrimonial, etc. L'application est développée en Python avec Flask et utilise un modèle de machine learning entraîné pour faire les prédictions.

## Fonctionnalités
- Formulaire interactif pour saisir les informations du demandeur
- Prédiction de l'éligibilité au crédit en temps réel
- API REST pour effectuer des prédictions via des requêtes JSON
- Gestion des erreurs et affichage des messages appropriés
- Interface utilisateur simple et intuitive

## Technologies utilisées
- Python
- Flask
- NumPy
- Pickle (pour le modèle ML)
- HTML/CSS (pour l'interface utilisateur)
- Bootstrap (pour le design responsive)
- Logging (pour la gestion des logs)

## Installation et exécution
### Prérequis
- Python 3.x installé
- Pip installé

### Installation
1. Cloner le dépôt GitHub :
   ```sh
   git clone https://github.com/ton-utilisateur/credit-eligibility-prediction.git
   cd credit-eligibility-prediction
   ```

2. Créer un environnement virtuel et l'activer :
   ```sh
   python -m venv venv
   source venv/bin/activate  # Sur macOS/Linux
   venv\Scripts\activate  # Sur Windows
   ```

3. Installer les dépendances :
   ```sh
   pip install -r requirements.txt
   ```

### Exécution de l'application
1. Assurez-vous que `model.pkl` est bien présent dans le dossier du projet.
2. Lancer l'application Flask :
   ```sh
   python app.py
   ```
3. Ouvrir le navigateur et accéder à :
   ```
   http://127.0.0.1:5000/
   ```

## Utilisation de l'API REST
L'API REST permet d'envoyer des requêtes POST pour obtenir une prédiction.

### Exemple de requête
```sh
curl -X POST http://127.0.0.1:5000/predict_api -H "Content-Type: application/json" -d '{
    "Gender": "male",
    "Married": "yes",
    "Dependents": "0",
    "Education": "graduate",
    "Self_Employed": "no",
    "ApplicantIncome": 5000,
    "CoapplicantIncome": 0,
    "LoanAmount": 150,
    "Loan_Amount_Term": 360,
    "Credit_History": "1",
    "Property_Area": "urban"
}'
```

### Réponse attendue
```json
{
    "status": "success",
    "prediction": 1,
    "formatted_prediction": "Éligible au crédit",
    "timestamp": "2025-03-23T14:00:00"
}
```

## Déploiement sur un serveur
1. Configurer un serveur cloud (ex: AWS, Heroku, Render)
2. Mettre en place un fichier `requirements.txt` et un fichier `Procfile` (pour Heroku)
3. Pousser le projet sur GitHub et le connecter au service cloud choisi


---

N'hésite pas à modifier ce fichier pour ajouter des détails spécifiques à ton projet. 😊

