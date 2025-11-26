from flask import Blueprint, request, jsonify
from app.models import db, Usuario, TipoUsuario
from app.utils import token_required, requer_tipo_usuario

bp = Blueprint('usuarios', __name__)


@bp.route('', methods=['GET'])
@token_required
@requer_tipo_usuario('gerente')
def listar_usuarios():
    """Lista todos os usuários (apenas gerente)"""
    tipo_filtro = request.args.get('tipo')

    query = Usuario.query

    if tipo_filtro:
        try:
            tipo = TipoUsuario(tipo_filtro)
            query = query.filter_by(tipo=tipo)
        except ValueError:
            return jsonify({'message': 'Tipo de usuário inválido'}), 400

    usuarios = query.all()

    return jsonify({
        'usuarios': [u.to_dict() for u in usuarios],
        'total': len(usuarios)
    }), 200


@bp.route('/<int:usuario_id>', methods=['GET'])
@token_required
def obter_usuario(usuario_id):
    """Obtém um usuário específico"""
    # Gerente pode ver todos, outros apenas o próprio perfil
    if request.tipo_usuario != 'gerente' and request.usuario_id != usuario_id:
        return jsonify({'message': 'Acesso negado'}), 403

    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return jsonify({'message': 'Usuário não encontrado'}), 404

    return jsonify(usuario.to_dict(include_veiculos=True)), 200


@bp.route('/<int:usuario_id>', methods=['PUT'])
@token_required
def atualizar_usuario(usuario_id):
    """Atualiza um usuário"""
    # Gerente pode atualizar todos, outros apenas o próprio perfil
    if request.tipo_usuario != 'gerente' and request.usuario_id != usuario_id:
        return jsonify({'message': 'Acesso negado'}), 403

    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return jsonify({'message': 'Usuário não encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Dados não fornecidos'}), 400

    # Atualizar campos permitidos
    if 'nome' in data:
        usuario.nome = data['nome']

    if 'email' in data:
        # Verificar se email já existe para outro usuário
        usuario_existente = Usuario.query.filter_by(email=data['email']).first()
        if usuario_existente and usuario_existente.id != usuario_id:
            return jsonify({'message': 'Email já cadastrado'}), 409
        usuario.email = data['email']

    if 'senha' in data:
        usuario.set_senha(data['senha'])

    # Apenas gerente pode mudar tipo
    if 'tipo' in data and request.tipo_usuario == 'gerente':
        try:
            usuario.tipo = TipoUsuario(data['tipo'])
        except ValueError:
            return jsonify({'message': 'Tipo de usuário inválido'}), 400

    try:
        db.session.commit()
        return jsonify({
            'message': 'Usuário atualizado com sucesso',
            'usuario': usuario.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar usuário: {str(e)}'}), 500


@bp.route('/<int:usuario_id>', methods=['DELETE'])
@token_required
@requer_tipo_usuario('gerente')
def deletar_usuario(usuario_id):
    """Deleta um usuário (apenas gerente)"""
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return jsonify({'message': 'Usuário não encontrado'}), 404

    try:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar usuário: {str(e)}'}), 500
