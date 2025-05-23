from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import mysql.connector
import os
import jwt
import time
from datetime import datetime, timedelta
from middleware import admin_required

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
        required_fields = ['firstName', 'lastName', 'email', 'birthDate', 'city', 'postalCode']
        for field in required_fields:
            if field not in user_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        db = get_db()
        cursor = db.cursor()
        
        # Check if email exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (user_data['email'],))
        if cursor.fetchone():
            return jsonify({"error": "Email already exists"}), 409

        # Insert user
        sql = '''INSERT INTO users (firstName, lastName, email, birthDate, city, postalCode) 
                VALUES (%s, %s, %s, %s, %s, %s)'''
        values = (user_data['firstName'], user_data['lastName'], user_data['email'],
                user_data['birthDate'], user_data['city'], user_data['postalCode'])
        
        cursor.execute(sql, values)
        db.commit()
        user_data['id'] = cursor.lastrowid
        
        cursor.close()
        db.close()
        return jsonify(user_data), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        login_data = request.json
        if not login_data or 'email' not in login_data or 'password' not in login_data:
            return jsonify({"error": "Email et mot de passe requis"}), 400

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM administrators WHERE email = %s AND password = %s",
                      (login_data['email'], login_data['password']))
        admin = cursor.fetchone()
        
        if not admin:
            return jsonify({"error": "Email ou mot de passe incorrect"}), 401
            
        token = jwt.encode({
            'email': admin['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        cursor.close()
        db.close()
        return jsonify({
            "token": token,
            "email": admin['email']
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)