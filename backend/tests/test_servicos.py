from app.models import db, Servico, Veiculo


def test_criar_servico_cliente(client, app, auth_headers_cliente, usuario_cliente):
    """Testa criação de serviço por cliente"""
    # Criar veículo primeiro
    with app.app_context():
        veiculo = Veiculo(
            placa="SRV1234",
            modelo="Civic",
            marca="Honda",
            ano=2020,
            usuario_id=usuario_cliente["id"],
        )
        db.session.add(veiculo)
        db.session.commit()
        veiculo_id = veiculo.id

    response = client.post(
        "/api/servicos",
        headers=auth_headers_cliente,
        json={"descricao": "Troca de óleo", "veiculo_id": veiculo_id},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["servico"]["descricao"] == "Troca de óleo"
    assert data["servico"]["status"] == "pendente"


def test_listar_servicos_cliente(client, app, auth_headers_cliente, usuario_cliente):
    """Testa listagem de serviços do cliente"""
    # Criar veículo e serviço
    with app.app_context():
        veiculo = Veiculo(
            placa="LST1234",
            modelo="Corolla",
            marca="Toyota",
            ano=2019,
            usuario_id=usuario_cliente["id"],
        )
        db.session.add(veiculo)
        db.session.commit()

        servico = Servico(descricao="Alinhamento", veiculo_id=veiculo.id)
        db.session.add(servico)
        db.session.commit()

    response = client.get("/api/servicos", headers=auth_headers_cliente)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["servicos"]) >= 1


def test_atualizar_servico_gerente(client, app, auth_headers_gerente, usuario_cliente):
    """Testa atualização de serviço por gerente"""
    # Criar veículo e serviço
    with app.app_context():
        veiculo = Veiculo(
            placa="UPD1234",
            modelo="Gol",
            marca="Volkswagen",
            ano=2018,
            usuario_id=usuario_cliente["id"],
        )
        db.session.add(veiculo)
        db.session.commit()

        servico = Servico(descricao="Revisão", veiculo_id=veiculo.id)
        db.session.add(servico)
        db.session.commit()
        servico_id = servico.id

    response = client.put(
        f"/api/servicos/{servico_id}",
        headers=auth_headers_gerente,
        json={"status": "em_andamento", "valor": 350.00},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["servico"]["status"] == "em_andamento"


def test_criar_orcamento_gerente(client, app, auth_headers_gerente, usuario_cliente):
    """Testa criação de orçamento por gerente"""
    # Criar veículo e serviço
    with app.app_context():
        veiculo = Veiculo(
            placa="ORC1234",
            modelo="Uno",
            marca="Fiat",
            ano=2015,
            usuario_id=usuario_cliente["id"],
        )
        db.session.add(veiculo)
        db.session.commit()

        servico = Servico(descricao="Troca de freios", veiculo_id=veiculo.id)
        db.session.add(servico)
        db.session.commit()
        servico_id = servico.id

    response = client.post(
        f"/api/servicos/{servico_id}/orcamento",
        headers=auth_headers_gerente,
        json={"descricao": "Pastilhas + discos", "valor": 800.00},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["orcamento"]["valor"] == 800.00
