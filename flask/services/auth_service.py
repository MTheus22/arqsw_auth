import os
import jwt
import bcrypt
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import jsonify, redirect, url_for
from datetime import datetime, timezone, timedelta

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Conexão com o MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['auth_system']
users_collection = db['users']

# Chave secreta do JWT
SECRET_KEY = os.getenv('SECRET_KEY')

class AuthService:
    def __init__(self):
        self.users_collection = users_collection

    # Função de registro de usuário
    def register(self, request):
        data = request.get_json()
        username = data['username']
        password = data['password']
        role = data.get('role', 'user')  # Papel padrão

        # Verifica se o usuário já existe
        if self.users_collection.find_one({'username': username}):
            return jsonify({"message": "Usuário já existe"}), 400

        # Hash da senha com bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Inserir no banco de dados
        self.users_collection.insert_one({
            "username": username,
            "password": hashed_password,
            "role": role
        })

        return jsonify({"message": "Usuário registrado com sucesso"}), 201

    # Função de login de usuário
    def login(self, request):
        username = request.form['username']
        password = request.form['password']

        # Verificar se o usuário existe
        user = self.users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Gerar token JWT
            token = jwt.encode({
                'username': username,
                'role': user['role'],
                'exp': datetime.now(timezone.utc) + timedelta(hours=1)
            }, SECRET_KEY, algorithm="HS256")

            # Redirecionar para o dashboard com o token no cookie
            response = redirect(url_for('protected_routes.dashboard'))
            response.set_cookie('token', token, httponly=True)
            return response
        else:
            return jsonify({"message": "Credenciais inválidas"}), 401
