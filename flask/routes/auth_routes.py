from flask import Blueprint, request, jsonify, redirect, url_for
from services.auth_service import AuthService

auth_routes = Blueprint('auth_routes', __name__)

# Instância do serviço de autenticação
auth_service = AuthService()

@auth_routes.route('/login', methods=['POST'])
def login():
    return auth_service.login(request)

@auth_routes.route('/register', methods=['POST'])
def register():
    return auth_service.register(request)
