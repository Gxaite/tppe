from flask import Blueprint, jsonify, request
from app.models import Servico, Veiculo, Usuario, StatusServico
from app.utils import token_required

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('', methods=['GET'])
@token_required
def dashboard():
    """Retorna dashboard baseado no tipo de usuário"""
    
    if request.tipo_usuario == 'gerente':
        return dashboard_gerente()
    elif request.tipo_usuario == 'mecanico':
        return dashboard_mecanico()
    else:  # cliente
        return dashboard_cliente()


def dashboard_gerente():
    """Dashboard para gerente"""
    # Estatísticas gerais
    total_clientes = Usuario.query.filter_by(tipo='cliente').count()
    total_mecanicos = Usuario.query.filter_by(tipo='mecanico').count()
    total_veiculos = Veiculo.query.count()
    total_servicos = Servico.query.count()
    
    # Serviços por status
    pendentes = Servico.query.filter_by(status=StatusServico.PENDENTE).count()
    em_andamento = Servico.query.filter_by(status=StatusServico.EM_ANDAMENTO).count()
    concluidos = Servico.query.filter_by(status=StatusServico.CONCLUIDO).count()
    
    # Serviços ativos (últimos 10)
    servicos_ativos = Servico.query.filter(
        Servico.status.in_([StatusServico.PENDENTE, StatusServico.EM_ANDAMENTO])
    ).order_by(Servico.criado_em.desc()).limit(10).all()
    
    return jsonify({
        'tipo_usuario': 'gerente',
        'estatisticas': {
            'total_clientes': total_clientes,
            'total_mecanicos': total_mecanicos,
            'total_veiculos': total_veiculos,
            'total_servicos': total_servicos,
            'servicos_pendentes': pendentes,
            'servicos_em_andamento': em_andamento,
            'servicos_concluidos': concluidos
        },
        'servicos_ativos': [s.to_dict() for s in servicos_ativos]
    }), 200


def dashboard_mecanico():
    """Dashboard para mecânico"""
    # Serviços atribuídos
    meus_servicos = Servico.query.filter_by(mecanico_id=request.usuario_id).all()
    
    # Por status
    pendentes = [s for s in meus_servicos if s.status == StatusServico.PENDENTE]
    em_andamento = [s for s in meus_servicos if s.status == StatusServico.EM_ANDAMENTO]
    concluidos = [s for s in meus_servicos if s.status == StatusServico.CONCLUIDO]
    
    return jsonify({
        'tipo_usuario': 'mecanico',
        'estatisticas': {
            'total_servicos': len(meus_servicos),
            'pendentes': len(pendentes),
            'em_andamento': len(em_andamento),
            'concluidos': len(concluidos)
        },
        'servicos_atribuidos': [s.to_dict() for s in meus_servicos]
    }), 200


def dashboard_cliente():
    """Dashboard para cliente"""
    # Veículos do cliente
    meus_veiculos = Veiculo.query.filter_by(usuario_id=request.usuario_id).all()
    veiculos_ids = [v.id for v in meus_veiculos]
    
    # Serviços dos veículos
    meus_servicos = Servico.query.filter(Servico.veiculo_id.in_(veiculos_ids)).all()
    
    # Por status
    pendentes = [s for s in meus_servicos if s.status == StatusServico.PENDENTE]
    em_andamento = [s for s in meus_servicos if s.status == StatusServico.EM_ANDAMENTO]
    concluidos = [s for s in meus_servicos if s.status == StatusServico.CONCLUIDO]
    
    return jsonify({
        'tipo_usuario': 'cliente',
        'estatisticas': {
            'total_veiculos': len(meus_veiculos),
            'total_servicos': len(meus_servicos),
            'servicos_pendentes': len(pendentes),
            'servicos_em_andamento': len(em_andamento),
            'servicos_concluidos': len(concluidos)
        },
        'meus_veiculos': [v.to_dict() for v in meus_veiculos],
        'meus_servicos': [s.to_dict() for s in meus_servicos]
    }), 200
