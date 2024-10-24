from config import config  # Importando configurações globais
from dotenv import load_dotenv
from flask import Flask, render_template
from routes.auth_routes import auth_routes  # Importando rotas de autenticação
from routes.content_routes import content_routes  # Importando rotas de conteúdo
from routes.protected_routes import protected_routes  # Importando rotas protegidas

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__, static_url_path='/static')

# Aplicar configurações globais do arquivo config.py
app.config.from_object(config)

# Registrar os Blueprints para as rotas
app.register_blueprint(auth_routes)  # Rotas de autenticação (login, registro)
app.register_blueprint(content_routes)  # Rotas de conteúdo (criação, edição, etc)
app.register_blueprint(protected_routes)  # Rotas protegidas (ex: dashboard)

# Rota padrão
@app.route('/')
def index():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
