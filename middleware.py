from functools import wraps
from flask import request, jsonify
from flask import current_app
import jwt
from datetime import datetime, timedelta

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token manquant'}), 401
        try:
            from hello import get_db
            payload = jwt.decode(auth_header, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            db = get_db()
            # Vérifier si l'utilisateur existe dans la collection administrators
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM administrators WHERE email = %s", (payload['email'],))
            admin = cursor.fetchone()
            if (not admin or payload['role'] != admin['role']) and payload['role'] != 'admin':
                return jsonify({'error': 'Non autorisé'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token invalide'}), 401
            
        return f(*args, **kwargs)
    return decorated_function