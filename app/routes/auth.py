from flask import Blueprint, request, jsonify
from app.models import db, Usuario, TipoUsuario
from app.utils import gerar_token

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/registro', methods=['POST'])
def registro():
    """Registra um novo usuário"""
    data = request.get_json()

    # Validações
    if not data:
        return jsonify({'message': 'Dados não fornecidos'}), 400

    campos_obrigatorios = ['nome', 'email', 'senha', 'tipo']
    for campo in campos_obrigatorios:
        if campo not in data:
            return jsonify({'message': f'Campo {campo} é obrigatório'}), 400

    # Verificar se email já existe
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email já cadastrado'}), 409

    # Validar tipo de usuário
    try:
        tipo = TipoUsuario(data['tipo'])
    except ValueError:
        return jsonify({'message': 'Tipo de usuário inválido. Use: cliente, gerente ou mecanico'}), 400

    # Criar usuário
    usuario = Usuario(
        nome=data['nome'],
        email=data['email'],
        tipo=tipo
    )
    usuario.set_senha(data['senha'])

    try:
        db.session.add(usuario)
        db.session.commit()

        # Gerar token
        token = gerar_token(usuario.id, usuario.tipo.value)

        return jsonify({
            'message': 'Usuário registrado com sucesso',
            'usuario': usuario.to_dict(),
            'token': token
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao registrar usuário: {str(e)}'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """Realiza login de usuário"""
    data = request.get_json()

    if not data or 'email' not in data or 'senha' not in data:
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400

    # Buscar usuário
    usuario = Usuario.query.filter_by(email=data['email']).first()

    if not usuario or not usuario.verificar_senha(data['senha']):
        return jsonify({'message': 'Email ou senha incorretos'}), 401

    # Gerar token
    token = gerar_token(usuario.id, usuario.tipo.value)

    return jsonify({
        'message': 'Login realizado com sucesso',
        'usuario': usuario.to_dict(),
        'token': token
    }), 200


@bp.route('/perfil', methods=['GET'])
def perfil():
    """Retorna informações do perfil do usuário autenticado"""
    from app.utils import token_required

    @token_required
    def get_perfil():
        usuario = Usuario.query.get(request.usuario_id)
        if not usuario:
            return jsonify({'message': 'Usuário não encontrado'}), 404

        return jsonify(usuario.to_dict(include_veiculos=True)), 200

    return get_perfil()
