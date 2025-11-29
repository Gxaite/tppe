from flask import Blueprint, request, jsonify
from app.models import db, Servico, Veiculo, Usuario, Orcamento, StatusServico
from app.utils import token_required, requer_tipo_usuario

bp = Blueprint("servicos", __name__)


@bp.route("", methods=["GET"])
@token_required
def listar_servicos():
    """Lista serviços baseado no tipo de usuário"""
    if request.tipo_usuario == "gerente":
        # Gerente vê todos
        servicos = Servico.query.all()
    elif request.tipo_usuario == "mecanico":
        # Mecânico vê apenas os atribuídos a ele
        servicos = Servico.query.filter_by(mecanico_id=request.usuario_id).all()
    else:
        # Cliente vê apenas dos seus veículos
        veiculos_ids = [
            v.id for v in Veiculo.query.filter_by(usuario_id=request.usuario_id).all()
        ]
        servicos = Servico.query.filter(Servico.veiculo_id.in_(veiculos_ids)).all()

    return (
        jsonify(
            {
                "servicos": [s.to_dict(include_orcamentos=True) for s in servicos],
                "total": len(servicos),
            }
        ),
        200,
    )


@bp.route("/<int:servico_id>", methods=["GET"])
@token_required
def obter_servico(servico_id):
    """Obtém um serviço específico"""
    servico = db.session.get(Servico, servico_id)
    if not servico:
        return jsonify({"message": "Serviço não encontrado"}), 404

    # Verificar permissão
    if request.tipo_usuario == "cliente":
        veiculo = db.session.get(Veiculo, servico.veiculo_id)
        if veiculo.usuario_id != request.usuario_id:
            return jsonify({"message": "Acesso negado"}), 403
    elif request.tipo_usuario == "mecanico":
        if servico.mecanico_id != request.usuario_id:
            return jsonify({"message": "Acesso negado"}), 403

    return jsonify(servico.to_dict(include_orcamentos=True)), 200


@bp.route("", methods=["POST"])
@token_required
@requer_tipo_usuario("cliente", "gerente")
def criar_servico():
    """Cria uma nova solicitação de serviço"""
    data = request.get_json()

    if not data:
        return jsonify({"message": "Dados não fornecidos"}), 400

    if "descricao" not in data or "veiculo_id" not in data:
        return jsonify({"message": "Descrição e veículo são obrigatórios"}), 400

    # Verificar se veículo existe
    veiculo = db.session.get(Veiculo, data["veiculo_id"])
    if not veiculo:
        return jsonify({"message": "Veículo não encontrado"}), 404

    # Cliente só pode criar serviço para seus veículos
    if request.tipo_usuario == "cliente" and veiculo.usuario_id != request.usuario_id:
        return jsonify({"message": "Acesso negado"}), 403

    # Criar serviço
    servico = Servico(
        descricao=data["descricao"],
        veiculo_id=data["veiculo_id"],
        status=StatusServico.PENDENTE,
    )

    try:
        db.session.add(servico)
        db.session.commit()

        return (
            jsonify(
                {"message": "Serviço criado com sucesso", "servico": servico.to_dict()}
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao criar serviço: {str(e)}"}), 500


@bp.route("/<int:servico_id>", methods=["PUT"])
@token_required
def atualizar_servico(servico_id):
    """Atualiza um serviço"""
    servico = db.session.get(Servico, servico_id)
    if not servico:
        return jsonify({"message": "Serviço não encontrado"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "Dados não fornecidos"}), 400

    # Gerente pode atualizar tudo
    if request.tipo_usuario == "gerente":
        if "descricao" in data:
            servico.descricao = data["descricao"]
        if "valor" in data:
            servico.valor = data["valor"]
        if "status" in data:
            try:
                servico.status = StatusServico(data["status"])
            except ValueError:
                return jsonify({"message": "Status inválido"}), 400
        if "mecanico_id" in data:
            # Verificar se mecânico existe
            mecanico = db.session.get(Usuario, data["mecanico_id"])
            if not mecanico or mecanico.tipo.value != "mecanico":
                return jsonify({"message": "Mecânico inválido"}), 400
            servico.mecanico_id = data["mecanico_id"]

    # Mecânico pode atualizar apenas status
    elif request.tipo_usuario == "mecanico":
        if servico.mecanico_id != request.usuario_id:
            return jsonify({"message": "Acesso negado"}), 403

        if "status" in data:
            try:
                servico.status = StatusServico(data["status"])
            except ValueError:
                return jsonify({"message": "Status inválido"}), 400

    else:
        return jsonify({"message": "Acesso negado"}), 403

    try:
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Serviço atualizado com sucesso",
                    "servico": servico.to_dict(),
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao atualizar serviço: {str(e)}"}), 500


@bp.route("/<int:servico_id>/orcamento", methods=["POST"])
@token_required
@requer_tipo_usuario("gerente")
def criar_orcamento(servico_id):
    """Cria um orçamento para um serviço (apenas gerente)"""
    servico = db.session.get(Servico, servico_id)
    if not servico:
        return jsonify({"message": "Serviço não encontrado"}), 404

    data = request.get_json()
    if not data or "descricao" not in data or "valor" not in data:
        return jsonify({"message": "Descrição e valor são obrigatórios"}), 400

    orcamento = Orcamento(
        descricao=data["descricao"], valor=data["valor"], servico_id=servico_id
    )

    try:
        db.session.add(orcamento)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Orçamento criado com sucesso",
                    "orcamento": orcamento.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao criar orçamento: {str(e)}"}), 500
