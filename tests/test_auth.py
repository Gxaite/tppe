def test_registro_usuario(client):
    """Testa o registro de um novo usuário"""
    response = client.post('/auth/registro', json={
        'nome': 'Novo Cliente',
        'email': 'novo@teste.com',
        'senha': 'senha123',
        'tipo': 'cliente'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'token' in data
    assert data['usuario']['email'] == 'novo@teste.com'


def test_registro_email_duplicado(client, usuario_cliente):
    """Testa registro com email já existente"""
    response = client.post('/auth/registro', json={
        'nome': 'Outro Cliente',
        'email': 'cliente@teste.com',
        'senha': 'senha123',
        'tipo': 'cliente'
    })
    assert response.status_code == 409


def test_login_sucesso(client, usuario_cliente):
    """Testa login com credenciais válidas"""
    response = client.post('/auth/login', json={
        'email': 'cliente@teste.com',
        'senha': 'senha123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert data['usuario']['email'] == 'cliente@teste.com'


def test_login_senha_incorreta(client, usuario_cliente):
    """Testa login com senha incorreta"""
    response = client.post('/auth/login', json={
        'email': 'cliente@teste.com',
        'senha': 'senha_errada'
    })
    assert response.status_code == 401


def test_login_email_inexistente(client):
    """Testa login com email não cadastrado"""
    response = client.post('/auth/login', json={
        'email': 'nao_existe@teste.com',
        'senha': 'senha123'
    })
    assert response.status_code == 401


def test_perfil_autenticado(client, auth_headers_cliente):
    """Testa acesso ao perfil com autenticação"""
    response = client.get('/auth/perfil', headers=auth_headers_cliente)
    assert response.status_code == 200
    data = response.get_json()
    assert data['email'] == 'cliente@teste.com'


def test_perfil_sem_autenticacao(client):
    """Testa acesso ao perfil sem token"""
    response = client.get('/auth/perfil')
    assert response.status_code == 401
