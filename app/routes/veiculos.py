from flask import Blueprint, request, jsonify
from app.models import db, Veiculo, Usuario
from app.utils import token_required, requer_tipo_usuario

bp = Blueprint('veiculos', __name__)


@bp.route('', methods=['GET'])
@token_required
def listar_veiculos():
    """Lista veículos - cliente vê apenas os seus, gerente vê todos"""
    if request.tipo_usuario == 'gerente':
        veiculos = Veiculo.query.all()
    else:
        veiculos = Veiculo.query.filter_by(usuario_id=request.usuario_id).all()
    
    return jsonify({
        'veiculos': [v.to_dict() for v in veiculos],
        'total': len(veiculos)
    }), 200


@bp.route('/<int:veiculo_id>', methods=['GET'])
@token_required
def obter_veiculo(veiculo_id):
    """Obtém um veículo específico"""
    veiculo = Veiculo.query.get(veiculo_id)
    if not veiculo:
        return jsonify({'message': 'Veículo não encontrado'}), 404
    
    # Verificar permissão
    if request.tipo_usuario != 'gerente' and veiculo.usuario_id != request.usuario_id:
        return jsonify({'message': 'Acesso negado'}), 403
    
    return jsonify(veiculo.to_dict(include_servicos=True)), 200


@bp.route('', methods=['POST'])
@token_required
@requer_tipo_usuario('cliente', 'gerente')
def criar_veiculo():
    """Cria um novo veículo"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Dados não fornecidos'}), 400
    
    campos_obrigatorios = ['placa', 'modelo', 'marca', 'ano']
    for campo in campos_obrigatorios:
        if campo not in data:
            return jsonify({'message': f'Campo {campo} é obrigatório'}), 400
    
    # Verificar se placa já existe
    if Veiculo.query.filter_by(placa=data['placa']).first():
        return jsonify({'message': 'Placa já cadastrada'}), 409
    
    # Determinar dono do veículo
    if request.tipo_usuario == 'gerente' and 'usuario_id' in data:
        # Gerente pode criar veículo para qualquer usuário
        usuario_id = data['usuario_id']
        if not Usuario.query.get(usuario_id):
            return jsonify({'message': 'Usuário não encontrado'}), 404
    else:
        # Cliente cria para si mesmo
        usuario_id = request.usuario_id
    
    # Criar veículo
    veiculo = Veiculo(
        placa=data['placa'].upper(),
        modelo=data['modelo'],
        marca=data['marca'],
        ano=data['ano'],
        usuario_id=usuario_id
    )
    
    try:
        db.session.add(veiculo)
        db.session.commit()
        
        return jsonify({
            'message': 'Veículo cadastrado com sucesso',
            'veiculo': veiculo.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao cadastrar veículo: {str(e)}'}), 500


@bp.route('/<int:veiculo_id>', methods=['PUT'])
@token_required
def atualizar_veiculo(veiculo_id):
    """Atualiza um veículo"""
    veiculo = Veiculo.query.get(veiculo_id)
    if not veiculo:
        return jsonify({'message': 'Veículo não encontrado'}), 404
    
    # Verificar permissão
    if request.tipo_usuario != 'gerente' and veiculo.usuario_id != request.usuario_id:
        return jsonify({'message': 'Acesso negado'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Dados não fornecidos'}), 400
    
    # Atualizar campos
    if 'placa' in data:
        # Verificar se placa já existe para outro veículo
        veiculo_existente = Veiculo.query.filter_by(placa=data['placa']).first()
        if veiculo_existente and veiculo_existente.id != veiculo_id:
            return jsonify({'message': 'Placa já cadastrada'}), 409
        veiculo.placa = data['placa'].upper()
    
    if 'modelo' in data:
        veiculo.modelo = data['modelo']
    
    if 'marca' in data:
        veiculo.marca = data['marca']
    
    if 'ano' in data:
        veiculo.ano = data['ano']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Veículo atualizado com sucesso',
            'veiculo': veiculo.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar veículo: {str(e)}'}), 500


@bp.route('/<int:veiculo_id>', methods=['DELETE'])
@token_required
def deletar_veiculo(veiculo_id):
    """Deleta um veículo"""
    veiculo = Veiculo.query.get(veiculo_id)
    if not veiculo:
        return jsonify({'message': 'Veículo não encontrado'}), 404
    
    # Verificar permissão
    if request.tipo_usuario != 'gerente' and veiculo.usuario_id != request.usuario_id:
        return jsonify({'message': 'Acesso negado'}), 403
    
    try:
        db.session.delete(veiculo)
        db.session.commit()
        return jsonify({'message': 'Veículo deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar veículo: {str(e)}'}), 500
