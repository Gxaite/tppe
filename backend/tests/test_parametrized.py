"""
Testes Parametrizados - Sistema Oficina Mecânica
Utiliza @pytest.mark.parametrize para testar múltiplos cenários
"""
import pytest
from app import create_app
from app.models import db, Usuario, Veiculo, Servico, TipoUsuario, StatusServico


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
    """Cliente de teste Flask"""
    return app.test_client()


class TestValidacaoRegistro:
    """Testes parametrizados para validação de registro de usuário"""

    @pytest.mark.parametrize(
        "nome,email,senha,tipo,expected_status,expected_message",
        [
            # Casos de sucesso
            (
                "João Silva",
                "joao@email.com",
                "senha123",
                "cliente",
                201,
                "Usuário registrado com sucesso",
            ),
            (
                "Maria Santos",
                "maria@email.com",
                "senha456",
                "mecanico",
                201,
                "Usuário registrado com sucesso",
            ),
            (
                "Admin User",
                "admin@email.com",
                "admin123",
                "gerente",
                201,
                "Usuário registrado com sucesso",
            ),
            # Casos de erro - tipo inválido
            (
                "Nome Teste",
                "tipo@email.com",
                "senha123",
                "invalido",
                400,
                "Tipo de usuário inválido",
            ),
            (
                "Nome Teste",
                "admin2@email.com",
                "senha123",
                "supervisor",
                400,
                "Tipo de usuário inválido",
            ),
        ],
    )
    def test_validacao_registro(
        self, client, nome, email, senha, tipo, expected_status, expected_message
    ):
        """Testa diferentes cenários de registro de usuário"""
        import random

        unique_email = email.replace("@", f"{random.randint(1000,9999)}@")

        response = client.post(
            "/auth/registro",
            json={"nome": nome, "email": unique_email, "senha": senha, "tipo": tipo},
        )

        assert response.status_code == expected_status
        if expected_message:
            data = response.get_json()
            assert expected_message in data.get("message", "")

    @pytest.mark.parametrize(
        "payload,campo_ausente",
        [
            (
                {"email": "test@email.com", "senha": "senha123", "tipo": "cliente"},
                "nome",
            ),
            ({"nome": "Teste", "senha": "senha123", "tipo": "cliente"}, "email"),
            ({"nome": "Teste", "email": "test@email.com", "tipo": "cliente"}, "senha"),
            ({"nome": "Teste", "email": "test@email.com", "senha": "senha123"}, "tipo"),
        ],
    )
    def test_registro_campo_obrigatorio(self, client, payload, campo_ausente):
        """Testa que campos obrigatórios são validados no registro"""
        import random

        if "email" in payload:
            payload = payload.copy()
            payload["email"] = payload["email"].replace(
                "@", f"{random.randint(1000,9999)}@"
            )

        response = client.post("/auth/registro", json=payload)
        assert response.status_code == 400
        assert campo_ausente in response.get_json().get("message", "")


class TestValidacaoLogin:
    """Testes parametrizados para validação de login"""

    @pytest.fixture
    def usuario_cadastrado(self, app):
        """Cria um usuário para testes de login"""
        with app.app_context():
            usuario = Usuario(
                nome="Usuario Teste", email="teste@login.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

    @pytest.mark.parametrize(
        "email,senha,expected_status",
        [
            # Login correto
            ("teste@login.com", "senha123", 200),
            # Senha incorreta
            ("teste@login.com", "senhaerrada", 401),
            # Email não cadastrado
            ("naoexiste@login.com", "senha123", 401),
        ],
    )
    def test_validacao_login(
        self, client, usuario_cadastrado, email, senha, expected_status
    ):
        """Testa diferentes cenários de login"""
        response = client.post("/auth/login", json={"email": email, "senha": senha})

        assert response.status_code == expected_status


class TestValidacaoVeiculo:
    """Testes parametrizados para validação de veículo"""

    @pytest.fixture
    def auth_token(self, app, client):
        """Cria usuário e retorna token de autenticação"""
        import random

        email = f"cliente_veiculo{random.randint(1000,9999)}@teste.com"
        with app.app_context():
            usuario = Usuario(
                nome="Cliente Veiculo", email=email, tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

        response = client.post(
            "/auth/login", json={"email": email, "senha": "senha123"}
        )
        token = response.get_json()["token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.parametrize(
        "placa,modelo,marca,ano,expected_status",
        [
            # Casos de sucesso
            ("ABC1234", "Civic", "Honda", 2020, 201),
            ("DEF5678", "Corolla", "Toyota", 2019, 201),
            ("GHI9012", "Gol", "Volkswagen", 2018, 201),
        ],
    )
    def test_validacao_veiculo(
        self, client, auth_token, placa, modelo, marca, ano, expected_status
    ):
        """Testa diferentes cenários de criação de veículo"""
        import random

        unique_placa = f"{placa[:3]}{random.randint(1000,9999)}"

        response = client.post(
            "/api/veiculos",
            headers=auth_token,
            json={"placa": unique_placa, "modelo": modelo, "marca": marca, "ano": ano},
        )

        assert response.status_code == expected_status

    @pytest.mark.parametrize("campo_ausente", ["placa", "modelo", "marca"])
    def test_veiculo_campo_obrigatorio(self, client, auth_token, campo_ausente):
        """Testa que campos obrigatórios são validados na criação de veículo"""
        import random

        payload = {
            "placa": f"TST{random.randint(1000,9999)}",
            "modelo": "Teste",
            "marca": "Marca Teste",
            "ano": 2020,
        }
        del payload[campo_ausente]

        response = client.post("/api/veiculos", headers=auth_token, json=payload)
        assert response.status_code == 400


class TestValidacaoServico:
    """Testes parametrizados para validação de serviço"""

    @pytest.fixture
    def setup_servico(self, app, client):
        """Cria usuário, veículo e retorna token de autenticação"""
        import random

        suffix = random.randint(1000, 9999)

        with app.app_context():
            # Criar cliente e veículo
            cliente = Usuario(
                nome="Cliente Servico",
                email=f"cliente_servico{suffix}@teste.com",
                tipo=TipoUsuario.CLIENTE,
            )
            cliente.set_senha("senha123")
            db.session.add(cliente)
            db.session.commit()

            veiculo = Veiculo(
                placa=f"SVC{suffix}",
                modelo="Fit",
                marca="Honda",
                ano=2020,
                usuario_id=cliente.id,
            )
            db.session.add(veiculo)
            db.session.commit()
            veiculo_id = veiculo.id
            cliente_email = cliente.email

        # Login como cliente (cliente pode criar serviço)
        response = client.post(
            "/auth/login", json={"email": cliente_email, "senha": "senha123"}
        )
        token = response.get_json()["token"]

        return {
            "headers": {"Authorization": f"Bearer {token}"},
            "veiculo_id": veiculo_id,
        }

    @pytest.mark.parametrize(
        "descricao,expected_status",
        [
            # Casos de sucesso
            ("Troca de óleo", 201),
            ("Revisão completa", 201),
            ("Alinhamento e balanceamento", 201),
        ],
    )
    def test_validacao_servico(self, client, setup_servico, descricao, expected_status):
        """Testa diferentes cenários de criação de serviço"""
        response = client.post(
            "/api/servicos",
            headers=setup_servico["headers"],
            json={"descricao": descricao, "veiculo_id": setup_servico["veiculo_id"]},
        )

        assert response.status_code == expected_status


class TestValidacaoStatusServico:
    """Testes parametrizados para transições de status de serviço"""

    @pytest.fixture
    def servico_setup(self, app, client):
        """Cria estrutura completa para testes de status"""
        import random

        suffix = random.randint(1000, 9999)

        with app.app_context():
            # Criar gerente
            gerente = Usuario(
                nome="Gerente Status",
                email=f"gerente_status{suffix}@teste.com",
                tipo=TipoUsuario.GERENTE,
            )
            gerente.set_senha("senha123")
            db.session.add(gerente)

            # Criar cliente e veículo
            cliente = Usuario(
                nome="Cliente Status",
                email=f"cliente_status{suffix}@teste.com",
                tipo=TipoUsuario.CLIENTE,
            )
            cliente.set_senha("senha123")
            db.session.add(cliente)
            db.session.commit()

            veiculo = Veiculo(
                placa=f"STS{suffix}",
                modelo="City",
                marca="Honda",
                ano=2021,
                usuario_id=cliente.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(
                descricao="Serviço teste status",
                veiculo_id=veiculo.id,
                status=StatusServico.PENDENTE,
            )
            db.session.add(servico)
            db.session.commit()
            servico_id = servico.id
            gerente_email = gerente.email

        # Login como gerente
        response = client.post(
            "/auth/login", json={"email": gerente_email, "senha": "senha123"}
        )
        token = response.get_json()["token"]

        return {
            "headers": {"Authorization": f"Bearer {token}"},
            "servico_id": servico_id,
        }

    @pytest.mark.parametrize(
        "novo_status,expected_status",
        [
            # Transições válidas
            ("em_andamento", 200),
            ("concluido", 200),
            ("cancelado", 200),
            ("aguardando_orcamento", 200),
            ("orcamento_aprovado", 200),
        ],
    )
    def test_transicao_status(
        self, client, servico_setup, novo_status, expected_status
    ):
        """Testa diferentes transições de status de serviço"""
        response = client.put(
            f'/api/servicos/{servico_setup["servico_id"]}',
            headers=servico_setup["headers"],
            json={"status": novo_status},
        )

        assert response.status_code == expected_status


class TestFormatacaoPlaca:
    """Testes parametrizados para validação de formato de placa"""

    @pytest.mark.parametrize(
        "placa,valida",
        [
            # Placas válidas (formato antigo)
            ("ABC1234", True),
            ("XYZ9876", True),
            # Placas válidas (formato Mercosul)
            ("ABC1D23", True),
            ("XYZ9A99", True),
            # Placas com hífen
            ("ABC-1234", True),
            # Placas inválidas
            ("AB12345", False),
            ("ABCD123", False),
            ("123ABCD", False),
            ("", False),
        ],
    )
    def test_validacao_formato_placa(self, placa, valida):
        """Testa diferentes formatos de placa"""
        import re

        # Regex para placa brasileira (antigo e Mercosul)
        padrao = r"^[A-Z]{3}[-]?[0-9][A-Z0-9][0-9]{2}$"
        resultado = bool(re.match(padrao, placa.upper())) if placa else False
        assert resultado == valida


class TestCalculoValorServico:
    """Testes parametrizados para cálculo de valor de serviço"""

    @pytest.mark.parametrize(
        "orcamentos,expected_total",
        [
            # Sem orçamentos
            ([], 0.0),
            # Um orçamento
            ([100.0], 100.0),
            # Múltiplos orçamentos
            ([100.0, 200.0], 300.0),
            ([50.0, 75.0, 125.0], 250.0),
            # Valores decimais
            ([99.99, 100.01], 200.0),
            ([33.33, 33.33, 33.34], 100.0),
        ],
    )
    def test_calculo_valor_total(self, app, orcamentos, expected_total):
        """Testa cálculo do valor total do serviço baseado em orçamentos"""
        with app.app_context():
            from app.models import Orcamento

            # Criar usuário e veículo
            usuario = Usuario(
                nome="Teste Calculo",
                email=f"calc_{len(orcamentos)}@teste.com",
                tipo=TipoUsuario.CLIENTE,
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa=f"CAL{len(orcamentos):04d}",
                modelo="Teste",
                marca="Teste",
                ano=2020,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(descricao="Serviço cálculo", veiculo_id=veiculo.id)
            db.session.add(servico)
            db.session.commit()

            # Adicionar orçamentos
            for valor in orcamentos:
                orcamento = Orcamento(
                    descricao="Item", valor=valor, servico_id=servico.id
                )
                db.session.add(orcamento)
            db.session.commit()

            # Verificar valor total
            assert abs(servico.valor_total - expected_total) < 0.01


class TestDashboardAPI:
    """Testes parametrizados para API do Dashboard"""

    @pytest.fixture
    def setup_dashboard(self, app, client):
        """Cria estrutura para testes de dashboard"""
        import random

        suffix = random.randint(1000, 9999)

        with app.app_context():
            gerente = Usuario(
                nome="Gerente Dashboard",
                email=f"gerente_dash{suffix}@teste.com",
                tipo=TipoUsuario.GERENTE,
            )
            gerente.set_senha("senha123")

            mecanico = Usuario(
                nome="Mecânico Dashboard",
                email=f"mecanico_dash{suffix}@teste.com",
                tipo=TipoUsuario.MECANICO,
            )
            mecanico.set_senha("senha123")

            cliente = Usuario(
                nome="Cliente Dashboard",
                email=f"cliente_dash{suffix}@teste.com",
                tipo=TipoUsuario.CLIENTE,
            )
            cliente.set_senha("senha123")

            db.session.add_all([gerente, mecanico, cliente])
            db.session.commit()

            return {
                "gerente_email": gerente.email,
                "mecanico_email": mecanico.email,
                "cliente_email": cliente.email,
            }

    @pytest.mark.parametrize(
        "tipo_usuario,email_key",
        [
            ("gerente", "gerente_email"),
            ("mecanico", "mecanico_email"),
            ("cliente", "cliente_email"),
        ],
    )
    def test_dashboard_api_por_tipo(
        self, client, setup_dashboard, tipo_usuario, email_key
    ):
        """Testa que dashboard API retorna dados para cada tipo de usuário"""
        response = client.post(
            "/auth/login",
            json={"email": setup_dashboard[email_key], "senha": "senha123"},
        )
        token = response.get_json()["token"]

        response = client.get(
            "/api/dashboard", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


class TestUsuariosAPI:
    """Testes parametrizados para API de Usuários"""

    @pytest.fixture
    def gerente_token(self, app, client):
        """Cria gerente e retorna token"""
        import random

        suffix = random.randint(1000, 9999)

        with app.app_context():
            gerente = Usuario(
                nome="Gerente Usuarios",
                email=f"gerente_usuarios{suffix}@teste.com",
                tipo=TipoUsuario.GERENTE,
            )
            gerente.set_senha("senha123")
            db.session.add(gerente)
            db.session.commit()
            gerente_email = gerente.email

        response = client.post(
            "/auth/login", json={"email": gerente_email, "senha": "senha123"}
        )
        return response.get_json()["token"]

    @pytest.mark.parametrize(
        "rota,metodo,expected_status",
        [
            ("/api/usuarios", "GET", 200),
        ],
    )
    def test_usuarios_api_gerente(
        self, client, gerente_token, rota, metodo, expected_status
    ):
        """Testa rotas de usuários como gerente"""
        headers = {"Authorization": f"Bearer {gerente_token}"}
        if metodo == "GET":
            response = client.get(rota, headers=headers)
        assert response.status_code == expected_status


class TestServicosAPICRUD:
    """Testes parametrizados para CRUD de Serviços via API"""

    @pytest.fixture
    def setup_servicos_crud(self, app, client):
        """Setup para testes de CRUD de serviços"""
        import random

        suffix = random.randint(1000, 9999)

        with app.app_context():
            gerente = Usuario(
                nome="Gerente CRUD",
                email=f"gerente_crud{suffix}@teste.com",
                tipo=TipoUsuario.GERENTE,
            )
            gerente.set_senha("senha123")

            cliente = Usuario(
                nome="Cliente CRUD",
                email=f"cliente_crud{suffix}@teste.com",
                tipo=TipoUsuario.CLIENTE,
            )
            cliente.set_senha("senha123")

            db.session.add_all([gerente, cliente])
            db.session.commit()

            veiculo = Veiculo(
                placa=f"CRD{suffix}",
                modelo="Teste CRUD",
                marca="Marca CRUD",
                ano=2022,
                usuario_id=cliente.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(
                descricao="Serviço para testes CRUD",
                veiculo_id=veiculo.id,
                status=StatusServico.PENDENTE,
            )
            db.session.add(servico)
            db.session.commit()

            return {
                "gerente_email": gerente.email,
                "cliente_email": cliente.email,
                "veiculo_id": veiculo.id,
                "servico_id": servico.id,
            }

    @pytest.mark.parametrize(
        "status_novo",
        [
            "pendente",
            "em_andamento",
            "aguardando_orcamento",
            "orcamento_aprovado",
            "concluido",
            "cancelado",
        ],
    )
    def test_atualizar_status_servico(self, client, setup_servicos_crud, status_novo):
        """Testa atualização de diferentes status de serviço"""
        response = client.post(
            "/auth/login",
            json={"email": setup_servicos_crud["gerente_email"], "senha": "senha123"},
        )
        token = response.get_json()["token"]

        response = client.put(
            f'/api/servicos/{setup_servicos_crud["servico_id"]}',
            headers={"Authorization": f"Bearer {token}"},
            json={"status": status_novo},
        )
        assert response.status_code == 200
