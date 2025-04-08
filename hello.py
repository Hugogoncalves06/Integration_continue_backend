from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)