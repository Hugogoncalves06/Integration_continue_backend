from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import mysql.connector
import os
import jwt
import time
from datetime import datetime, timedelta
from middleware import admin_required
import bcrypt

app = Flask(__name__)
CORS(app)
app.config['FORCE_JSON'] = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'votre_clé_secrète_par_défaut')

# MySQL connection
def get_db():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'admin'),
        password=os.getenv('MYSQL_PASSWORD', 'password'),
        database=os.getenv('MYSQL_DATABASE', 'users_db')
    )

def wait_for_db(max_retries=30, delay=2):
    retries = 0
    while retries < max_retries:
        try:
            conn = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                user=os.getenv('MYSQL_USER', 'admin'),
                password=os.getenv('MYSQL_PASSWORD', 'password'),
                database=os.getenv('MYSQL_DATABASE', 'users_db')
            )
            conn.close()
            return True
        except mysql.connector.Error as err:
            print(f"Tentative {retries + 1}/{max_retries} de connexion à la base de données... ({err})")
            retries += 1
            time.sleep(delay)
    return False

with app.app_context():
    get_db()

@app.route("/")
def hello_world():
    return {"message": "API is running"}

@app.route("/health")
def health_check():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        db.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": str(e)}), 500

@app.route("/api/users", methods=['POST'])
def create_user():
    try:
        user_data = request.json
        required_fields = ['firstName', 'lastName', 'email', 'birthDate', 'city', 'postalCode', 'password']
        for field in required_fields:
            if not user_data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400

        # Sécurité du mot de passe
        password = user_data['password']
        if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            return jsonify({'error': 'Le mot de passe doit contenir au moins 8 caractères, une majuscule et un chiffre.'}), 400
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        db = get_db()
        cursor = db.cursor()
        # Vérifier si l'email existe déjà
        cursor.execute("SELECT id FROM users WHERE email=%s", (user_data['email'],))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({'error': 'Cet email est déjà utilisé'}), 409
        # Insérer l'utilisateur
        cursor.execute("INSERT INTO users (firstName, lastName, email, password, birthDate, city, postalCode) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (user_data['firstName'], user_data['lastName'], user_data['email'], hashed_password, user_data['birthDate'], user_data['city'], user_data['postalCode']))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"email": user_data['email']}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/users", methods=['GET'])
def get_users():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/login", methods=['POST'])
def login():
    try:
        data = request.json
        print("Received login data:", data)  # Debugging line
        if not data:
            return jsonify({'error': 'Aucune donnée reçue'}), 400
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        db = get_db()
        cursor = db.cursor(dictionary=True)
        # Vérifier dans users
        cursor.execute("SELECT id, email, password, 'user' as role FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Générer un token (ici simplifié)
            token = os.urandom(24).hex()
            cursor.close()
            db.close()
            return jsonify({'token': token, 'email': user['email'], 'role': 'user'}), 200
        # Vérifier dans administrators
        cursor.execute("SELECT id, email, password, role FROM administrators WHERE email=%s", (email,))
        admin = cursor.fetchone()
        if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8')):
            token = os.urandom(24).hex()
            cursor.close()
            db.close()
            return jsonify({'token': token, 'email': admin['email'], 'role': admin['role']}), 200
        cursor.close()
        db.close()
        return jsonify({'error': 'Identifiants invalides'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/users/<int:user_id>", methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Utilisateur non trouvé"}), 404
            
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        
        cursor.close()
        db.close()
        return jsonify({"message": "Utilisateur supprimé avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/users/<int:user_id>", methods=['GET'])
@admin_required
def get_user(user_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admins", methods=['POST'])
@admin_required
def create_admin():
    try:
        admin_data = request.json
        required_fields = ['email', 'password', 'role']
        for field in required_fields:
            if not admin_data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        password = admin_data['password']
        if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            return jsonify({'error': 'Le mot de passe doit contenir au moins 8 caractères, une majuscule et un chiffre.'}), 400
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM administrators WHERE email=%s", (admin_data['email'],))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({'error': 'Cet email est déjà utilisé'}), 409
        cursor.execute("INSERT INTO administrators (email, password, role) VALUES (%s, %s, %s)",
            (admin_data['email'], hashed_password, admin_data['role']))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"email": admin_data['email']}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)