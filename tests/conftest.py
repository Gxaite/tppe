import pytest
from app import create_app
from app.models import db, Usuario, Veiculo, Servico, Orcamento


@pytest.fixture
def app():
    """Cria uma instância da aplicação para testes"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de teste"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner para comandos CLI"""
    return app.test_cli_runner()


@pytest.fixture
def usuario_cliente(app):
    """Cria um usuário cliente para testes"""
    with app.app_context():
        usuario = Usuario(
            nome='Cliente Teste',
            email='cliente@teste.com',
            tipo='cliente'
        )
        usuario.set_senha('senha123')
        db.session.add(usuario)
        db.session.commit()
        return usuario


@pytest.fixture
def usuario_gerente(app):
    """Cria um usuário gerente para testes"""
    with app.app_context():
        usuario = Usuario(
            nome='Gerente Teste',
            email='gerente@teste.com',
            tipo='gerente'
        )
        usuario.set_senha('senha123')
        db.session.add(usuario)
        db.session.commit()
        return usuario


@pytest.fixture
def usuario_mecanico(app):
    """Cria um usuário mecânico para testes"""
    with app.app_context():
        usuario = Usuario(
            nome='Mecânico Teste',
            email='mecanico@teste.com',
            tipo='mecanico'
        )
        usuario.set_senha('senha123')
        db.session.add(usuario)
        db.session.commit()
        return usuario


@pytest.fixture
def auth_headers_cliente(client, usuario_cliente):
    """Headers de autenticação para cliente"""
    response = client.post('/auth/login', json={
        'email': 'cliente@teste.com',
        'senha': 'senha123'
    })
    token = response.get_json()['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def auth_headers_gerente(client, usuario_gerente):
    """Headers de autenticação para gerente"""
    response = client.post('/auth/login', json={
        'email': 'gerente@teste.com',
        'senha': 'senha123'
    })
    token = response.get_json()['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def auth_headers_mecanico(client, usuario_mecanico):
    """Headers de autenticação para mecânico"""
    response = client.post('/auth/login', json={
        'email': 'mecanico@teste.com',
        'senha': 'senha123'
    })
    token = response.get_json()['token']
    return {'Authorization': f'Bearer {token}'}
