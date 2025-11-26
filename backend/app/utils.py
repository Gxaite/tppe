from datetime import datetime, timedelta
import jwt
from functools import wraps
from flask import request, jsonify, current_app


def gerar_token(usuario_id, tipo_usuario):
    """Gera um token JWT para o usuário"""
    payload = {
        'usuario_id': usuario_id,
        'tipo': tipo_usuario,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    return token


def decodificar_token(token):
    """Decodifica e valida um token JWT"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator para proteger rotas que requerem autenticação"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Pegar token do header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Token inválido'}), 401

        if not token:
            return jsonify({'message': 'Token não fornecido'}), 401

        # Decodificar token
        payload = decodificar_token(token)
        if not payload:
            return jsonify({'message': 'Token inválido ou expirado'}), 401

        # Adicionar dados do usuário ao request
        request.usuario_id = payload['usuario_id']
        request.tipo_usuario = payload['tipo']

        return f(*args, **kwargs)

    return decorated


def requer_tipo_usuario(*tipos_permitidos):
    """Decorator para verificar o tipo de usuário"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'tipo_usuario'):
                return jsonify({'message': 'Autenticação necessária'}), 401

            if request.tipo_usuario not in tipos_permitidos:
                return jsonify({'message': 'Acesso negado para este tipo de usuário'}), 403

            return f(*args, **kwargs)

        return decorated

    return decorator
