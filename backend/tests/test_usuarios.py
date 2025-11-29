"""
Testes para API de Usuários
"""
import pytest
from app import create_app
from app.models import db, Usuario, TipoUsuario


@pytest.fixture
def app():
    """Cria aplicação Flask para testes"""
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret-key",
            "JWT_SECRET_KEY": "test-jwt-secret-key",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def setup_usuarios(app):
    """Cria usuários de teste"""
    import random

    suffix = random.randint(1000, 9999)

    with app.app_context():
        gerente = Usuario(
            nome="Gerente Teste",
            email=f"gerente{suffix}@teste.com",
            tipo=TipoUsuario.GERENTE,
        )
        gerente.set_senha("senha123")

        cliente = Usuario(
            nome="Cliente Teste",
            email=f"cliente{suffix}@teste.com",
            tipo=TipoUsuario.CLIENTE,
        )
        cliente.set_senha("senha123")

        mecanico = Usuario(
            nome="Mecânico Teste",
            email=f"mecanico{suffix}@teste.com",
            tipo=TipoUsuario.MECANICO,
        )
        mecanico.set_senha("senha123")

        db.session.add_all([gerente, cliente, mecanico])
        db.session.commit()

        return {
            "gerente": {"id": gerente.id, "email": gerente.email},
            "cliente": {"id": cliente.id, "email": cliente.email},
            "mecanico": {"id": mecanico.id, "email": mecanico.email},
        }


def get_token(client, email, senha="senha123"):
    """Helper para obter token de autenticação"""
    response = client.post("/auth/login", json={"email": email, "senha": senha})
    return response.get_json()["token"]


class TestListarUsuarios:
    """Testes para listagem de usuários"""

    def test_gerente_lista_todos_usuarios(self, client, setup_usuarios):
        """Gerente pode listar todos os usuários"""
        token = get_token(client, setup_usuarios["gerente"]["email"])

        response = client.get(
            "/api/usuarios", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "usuarios" in data
        assert data["total"] >= 3

    def test_gerente_filtra_por_tipo(self, client, setup_usuarios):
        """Gerente pode filtrar usuários por tipo"""
        token = get_token(client, setup_usuarios["gerente"]["email"])

        response = client.get(
            "/api/usuarios?tipo=cliente", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert all(u["tipo"] == "cliente" for u in data["usuarios"])

    def test_cliente_nao_lista_usuarios(self, client, setup_usuarios):
        """Cliente não pode listar todos os usuários"""
        token = get_token(client, setup_usuarios["cliente"]["email"])

        response = client.get(
            "/api/usuarios", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403


class TestObterUsuario:
    """Testes para obter usuário específico"""

    def test_gerente_obtem_qualquer_usuario(self, client, setup_usuarios):
        """Gerente pode ver qualquer usuário"""
        token = get_token(client, setup_usuarios["gerente"]["email"])

        response = client.get(
            f'/api/usuarios/{setup_usuarios["cliente"]["id"]}',
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_usuario_obtem_proprio_perfil(self, client, setup_usuarios):
        """Usuário pode ver próprio perfil"""
        token = get_token(client, setup_usuarios["cliente"]["email"])

        response = client.get(
            f'/api/usuarios/{setup_usuarios["cliente"]["id"]}',
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_usuario_nao_obtem_outro_perfil(self, client, setup_usuarios):
        """Usuário não pode ver perfil de outro"""
        token = get_token(client, setup_usuarios["cliente"]["email"])

        response = client.get(
            f'/api/usuarios/{setup_usuarios["mecanico"]["id"]}',
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_usuario_inexistente(self, client, setup_usuarios):
        """Retorna 404 para usuário inexistente"""
        token = get_token(client, setup_usuarios["gerente"]["email"])

        response = client.get(
            "/api/usuarios/99999", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestAtualizarUsuario:
    """Testes para atualização de usuário"""

    def test_usuario_atualiza_proprio_nome(self, client, setup_usuarios):
        """Usuário pode atualizar próprio nome"""
        token = get_token(client, setup_usuarios["cliente"]["email"])

        response = client.put(
            f'/api/usuarios/{setup_usuarios["cliente"]["id"]}',
            headers={"Authorization": f"Bearer {token}"},
            json={"nome": "Novo Nome Cliente"},
        )

        assert response.status_code == 200
        assert response.get_json()["usuario"]["nome"] == "Novo Nome Cliente"

    def test_gerente_atualiza_tipo_usuario(self, client, setup_usuarios):
        """Gerente pode atualizar tipo de usuário"""
        token = get_token(client, setup_usuarios["gerente"]["email"])

        response = client.put(
            f'/api/usuarios/{setup_usuarios["cliente"]["id"]}',
            headers={"Authorization": f"Bearer {token}"},
            json={"tipo": "mecanico"},
        )

        assert response.status_code == 200
        assert response.get_json()["usuario"]["tipo"] == "mecanico"

    def test_cliente_nao_atualiza_outro(self, client, setup_usuarios):
        """Cliente não pode atualizar outro usuário"""
        token = get_token(client, setup_usuarios["cliente"]["email"])

        response = client.put(
            f'/api/usuarios/{setup_usuarios["mecanico"]["id"]}',
            headers={"Authorization": f"Bearer {token}"},
            json={"nome": "Tentativa"},
        )

        assert response.status_code == 403

    def test_atualiza_sem_dados(self, client, setup_usuarios):
        """Atualização sem dados retorna erro"""
        token = get_token(client, setup_usuarios["gerente"]["email"])

        response = client.put(
            f'/api/usuarios/{setup_usuarios["cliente"]["id"]}',
            headers={"Authorization": f"Bearer {token}"},
            content_type="application/json",
        )

        assert response.status_code == 400


class TestDeletarUsuario:
    """Testes para deleção de usuário"""

    def test_gerente_deleta_usuario(self, client, setup_usuarios):
        """Gerente pode deletar usuário"""
        token = get_token(client, setup_usuarios["gerente"]["email"])

        response = client.delete(
            f'/api/usuarios/{setup_usuarios["cliente"]["id"]}',
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_cliente_nao_deleta_usuario(self, client, setup_usuarios):
        """Cliente não pode deletar usuário"""
        token = get_token(client, setup_usuarios["cliente"]["email"])

        response = client.delete(
            f'/api/usuarios/{setup_usuarios["mecanico"]["id"]}',
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_deleta_usuario_inexistente(self, client, setup_usuarios):
        """Deletar usuário inexistente retorna 404"""
        token = get_token(client, setup_usuarios["gerente"]["email"])

        response = client.delete(
            "/api/usuarios/99999", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
