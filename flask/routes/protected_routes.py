from flask import Blueprint, render_template
from utils.decorators import token_required

# Criação do Blueprint para rotas protegidas
protected_routes = Blueprint('protected_routes', __name__)

# Rota de Dashboard após login bem-sucedido
@protected_routes.route('/dashboard')
@token_required  # Requer autenticação via JWT
def dashboard():
    return render_template('dashboard.html')  # Página com mensagem e botão

# Rota protegida que requer autenticação via JWT
@protected_routes.route('/protected')
@token_required  # Requer autenticação via JWT
def protected():
    return render_template('protected.html')
