from functools import wraps
from flask import request, jsonify
from flask import current_app
import jwt
from datetime import datetime, timedelta

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token manquant'}), 401
        
        try:
            print("Authorization header:", auth_header)
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            from hello import db 
            # Vérifier si l'utilisateur existe dans la collection administrators
            admin = db.administrators.find_one({'email': payload['email']})
            if not admin:
                return jsonify({'error': 'Non autorisé'}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token invalide'}), 401
            
        return f(*args, **kwargs)
    return decorated_function