from app.models import db, Veiculo


def test_criar_veiculo_cliente(client, app, auth_headers_cliente, usuario_cliente):
    """Testa criação de veículo por cliente"""
    response = client.post('/api/veiculos', 
        headers=auth_headers_cliente,
        json={
            'placa': 'ABC1234',
            'modelo': 'Civic',
            'marca': 'Honda',
            'ano': 2020
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['veiculo']['placa'] == 'ABC1234'


def test_listar_veiculos_cliente(client, app, auth_headers_cliente, usuario_cliente):
    """Testa listagem de veículos do cliente"""
    # Criar veículo
    with app.app_context():
        veiculo = Veiculo(
            placa='XYZ9876',
            modelo='Corolla',
            marca='Toyota',
            ano=2019,
            usuario_id=usuario_cliente['id']
        )
        db.session.add(veiculo)
        db.session.commit()
    
    response = client.get('/api/veiculos', headers=auth_headers_cliente)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['veiculos']) >= 1


def test_atualizar_veiculo_proprio(client, app, auth_headers_cliente, usuario_cliente):
    """Testa atualização de veículo próprio"""
    # Criar veículo
    with app.app_context():
        veiculo = Veiculo(
            placa='DEF5678',
            modelo='Gol',
            marca='Volkswagen',
            ano=2018,
            usuario_id=usuario_cliente['id']
        )
        db.session.add(veiculo)
        db.session.commit()
        veiculo_id = veiculo.id
    
    response = client.put(f'/api/veiculos/{veiculo_id}',
        headers=auth_headers_cliente,
        json={'ano': 2019}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['veiculo']['ano'] == 2019


def test_deletar_veiculo_proprio(client, app, auth_headers_cliente, usuario_cliente):
    """Testa exclusão de veículo próprio"""
    # Criar veículo
    with app.app_context():
        veiculo = Veiculo(
            placa='GHI9012',
            modelo='Uno',
            marca='Fiat',
            ano=2015,
            usuario_id=usuario_cliente['id']
        )
        db.session.add(veiculo)
        db.session.commit()
        veiculo_id = veiculo.id
    
    response = client.delete(f'/api/veiculos/{veiculo_id}', headers=auth_headers_cliente)
    assert response.status_code == 200


def test_criar_veiculo_placa_duplicada(client, app, auth_headers_cliente, usuario_cliente):
    """Testa criação de veículo com placa duplicada"""
    # Criar primeiro veículo
    with app.app_context():
        veiculo = Veiculo(
            placa='JKL3456',
            modelo='Palio',
            marca='Fiat',
            ano=2017,
            usuario_id=usuario_cliente['id']
        )
        db.session.add(veiculo)
        db.session.commit()
    
    # Tentar criar com mesma placa
    response = client.post('/api/veiculos',
        headers=auth_headers_cliente,
        json={
            'placa': 'JKL3456',
            'modelo': 'Outro',
            'marca': 'Outra',
            'ano': 2020
        }
    )
    assert response.status_code == 409
