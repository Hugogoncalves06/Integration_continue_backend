from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import jwt
from middleware import admin_required


app = Flask(__name__)
CORS(app)
app.config['FORCE_JSON'] = True
# Configuration de l'application Flask
# Ajouter une clé secrète pour JWT
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'votre_clé_secrète_par_défaut')

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://admin:password@localhost:27017/'))
db = client.users_db
users_collection = db.users

@app.route("/")
def hello_world():
    return {"message": "API is running"}

@app.route("/api/users", methods=['POST'])
def create_user():
    try:
        user_data = request.json
        # Vérifier les données requises
        required_fields = ['firstName', 'lastName', 'email', 'birthDate', 'city', 'postalCode']
        for field in required_fields:
            if field not in user_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Vérifier si l'email existe déjà
        if users_collection.find_one({"email": user_data['email']}):
            return jsonify({"error": "Email already exists"}), 409

        # Insérer l'utilisateur
        result = users_collection.insert_one(user_data)
        user_data['_id'] = str(result.inserted_id)
        
        return jsonify(user_data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/users", methods=['GET'])
def get_users():
    try:
        users = list(users_collection.find())
        # Convertir les ObjectId en strings pour la sérialisation JSON
        return json.loads(str(users)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/login", methods=['POST'])
def login():
    try:
        print("Login endpoint called")
        login_data = request.json
        if not login_data or 'email' not in login_data or 'password' not in login_data:
            return jsonify({"error": "Email et mot de passe requis"}), 400
        # Vérifier si l'utilisateur existe
        admin = db.administrators.find_one({
            "email": login_data['email'],
            "password": login_data['password']
        })
        if not admin:
            return jsonify({"error": "Email ou mot de passe incorrect"}), 401
            
        # Générer le token JWT
        token = jwt.encode({
            'email': admin['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "token": token,
            "email": admin['email']
        }), 200
        
    except Exception as e:
        print("Error during login:", str(e))
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/users/<user_id>", methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        # Vérifier si l'utilisateur existe
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        print("User found:", user)
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404
        # Supprimer l'utilisateur
        users_collection.delete_one({"_id": ObjectId(user_id)})
        return jsonify({"message": "Utilisateur supprimé avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)