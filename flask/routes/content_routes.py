from flask import Blueprint, jsonify
from utils.decorators import permission_required, hour_required

# Criação do Blueprint para rotas de conteúdo
content_routes = Blueprint('content_routes', __name__)

# Rota de visualização de conteúdo (todos os papéis podem ver)
@content_routes.route('/view', methods=['GET'])
@permission_required('view')  # Todos com permissão de 'view' podem acessar
def view_content():
    return jsonify({"message": "Conteúdo visualizado com sucesso"}), 200

# Rota de criação de conteúdo (somente admin e editor podem criar)
@content_routes.route('/create', methods=['POST'])
@hour_required()  # Verificar se está dentro do horário comercial
@permission_required('create')  # Admin e Editor permitidos
def create_content():
    return jsonify({"message": "Conteúdo criado com sucesso"}), 201

# Rota de edição de conteúdo (somente admin e editor podem editar)
@content_routes.route('/edit', methods=['POST'])
@permission_required('edit')  # Admin e Editor permitidos
def edit_content():
    return jsonify({"message": "Conteúdo editado com sucesso"}), 200

# Rota de exclusão de conteúdo (somente admin pode excluir)
@content_routes.route('/delete', methods=['POST'])
@permission_required('delete')  # Somente Admin permitido
def delete_content():
    return jsonify({"message": "Conteúdo excluído com sucesso"}), 200
