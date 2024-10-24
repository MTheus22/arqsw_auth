import jwt
from config import config  
from functools import wraps
from datetime import datetime
from flask import request, jsonify
from services.permission_policy import get_policy

# Decorador para verificar o token JWT no cookie
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')  # Buscar o token no cookie
        if not token:
            return jsonify({'message': 'Token ausente!'}), 403

        try:
            # Decodificar o token JWT usando a chave secreta definida em config.py
            jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 403

        return f(*args, **kwargs)
    return decorated

# Decorador para verificar permissões baseadas no papel do usuário
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.cookies.get('token')
            if not token:
                return jsonify({'message': 'Token ausente!'}), 403

            try:
                # Decodificar o token para obter o papel do usuário usando a chave secreta de config.py
                data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
                user_role = data['role']

                # Obter a política de permissões para o papel do usuário
                policy, role = get_policy(user_role)

                # Verificar se o papel do usuário tem a permissão necessária
                if not policy.is_allowed(role, permission):
                    return jsonify({'message': 'Acesso negado!'}), 403

            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token expirado!'}), 403
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Token inválido!'}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator

# Decorador para verificar restrições baseadas no horário comercial (ABAC)
def hour_required():
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.cookies.get('token')
            if not token:
                return jsonify({'message': 'Token ausente!'}), 403

            try:
                # Decodificar o token para obter o papel do usuário
                data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])

                # Verificar se está dentro do horário permitido
                current_hour = datetime.now().hour
                if not (0 <= current_hour <= 23):  # Horário comercial das 9h às 17h
                    return jsonify({'message': 'Acesso negado: fora do horário permitido!'}), 403

            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token expirado!'}), 403
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Token inválido!'}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator
