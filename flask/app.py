import os
import jwt
import bcrypt
from functools import wraps
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, render_template

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__, static_url_path='/static')

# Conexão com o MongoDB usando URI do arquivo .env
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['auth_system']
users_collection = db['users']

# Configuração da chave secreta para JWT
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Dicionário de papéis e permissões
roles_permissions = {
    'admin': ['view', 'create', 'edit', 'delete'],
    'editor': ['view', 'create', 'edit'],
    'user': ['view'],
    'viewer': ['view']
}

# Políticas baseadas em atributos
def office_hours():
    """Verifica se o acesso está dentro do horário comercial (9h às 17h)."""
    current_hour = datetime.now().hour
    return 9 <= current_hour <= 17


# Decorador para verificar o token JWT no cookie
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')  # Buscar o token no cookie
        if not token:
            return jsonify({'message': 'Token ausente!'}), 403
        
        try:
            # Adicionar um print para verificar o conteúdo do token
            print(f"Token recebido: {token}")

            # Decodificar o token 
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 403
        
        return f(*args, **kwargs)
    return decorated

# Decorador para verificar o papel do usuário
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.cookies.get('token')
            if not token:
                return jsonify({'message': 'Token ausente!'}), 403

            try:
                # Decodificar o token para obter o papel do usuário
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                user_role = data['role']

                # Verificar se o usuário tem o papel necessário
                if permission not in roles_permissions.get(user_role, []):
                    return jsonify({'message': 'Acesso negado!'}), 403

            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token expirado!'}), 403
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Token inválido!'}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator

def hour_required():
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.cookies.get('token')
            if not token:
                return jsonify({'message': 'Token ausente!'}), 403

            try:
                # Decodificar o token para obter o papel do usuário
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                
                # Verificar as políticas baseadas em atributos
                if not office_hours():
                    return jsonify({'message': 'Acesso negado: fora do horário permitido!'}), 403

            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token expirado!'}), 403
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Token inválido!'}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator


# Rota padrão
@app.route('/')
def index():
    return render_template('login.html')

# Rota de Registro de Usuários
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    role = data.get('role', 'user')  # Papel padrão

    # Verifica se o usuário já existe
    if users_collection.find_one({'username': username}):
        return jsonify({"message": "User already exists"}), 400

    # Hash da senha com bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Inserir no banco de dados
    users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "role": role
    })

    return jsonify({"message": "User registered successfully"}), 201

# Rota de Login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Verificar se o usuário existe
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        # Gerar token JWT
        token = jwt.encode({
            'username': username,
            'role': user['role'],
            'exp': datetime.now(timezone.utc) + timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        # Redirecionar para o dashboard com o token no cabeçalho
        response = redirect(url_for('dashboard'))
        response.set_cookie('token', token, httponly=True)
        return response
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Rota de Dashboard após login bem-sucedido
@app.route('/dashboard')
@token_required
def dashboard():
    return render_template('dashboard.html')  # Página com mensagem e botão

# Rota protegida que requer autenticação via JWT
@app.route('/protected')
@token_required
def protected():
    return render_template('protected.html')

# Rota de visualização de conteúdo (todos os papéis podem ver)
@app.route('/view', methods=['GET'])
@permission_required('view')  # Todos com permissão de 'view' podem acessar
def view_content():
    return jsonify({"message": "Conteúdo visualizado com sucesso"}), 200

# Rota de criação de conteúdo (somente admin e editor podem criar)
@app.route('/create', methods=['POST'])
@hour_required()  # Verificar se está dentro do horário comercial
@permission_required('create')  # Admin e Editor permitidos
def create_content():
    return jsonify({"message": "Conteúdo criado com sucesso"}), 201

# Rota de edição de conteúdo (somente admin e editor podem editar)
@app.route('/edit', methods=['POST'])
@permission_required('edit')  # Admin e Editor permitidos
def edit_content():
    return jsonify({"message": "Conteúdo editado com sucesso"}), 200

# Rota de exclusão de conteúdo (somente admin pode excluir)
@app.route('/delete', methods=['POST'])
@permission_required('delete')  # Somente Admin permitido
def delete_content():
    return jsonify({"message": "Conteúdo excluído com sucesso"}), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
