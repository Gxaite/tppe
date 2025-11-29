"""
Testes Unitários para Models - Sistema Oficina Mecânica
Testa os models SQLAlchemy e suas propriedades
"""
import pytest
from datetime import datetime
from app.models import (
    db,
    Usuario,
    Veiculo,
    Servico,
    Orcamento,
    TipoUsuario,
    StatusServico,
)


class TestUsuarioModel:
    """Testes para o model Usuario"""

    def test_criar_usuario_cliente(self, app):
        """Testa criação de usuário cliente"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente Teste", email="cliente@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            assert usuario.id is not None
            assert usuario.nome == "Cliente Teste"
            assert usuario.tipo == TipoUsuario.CLIENTE
            assert usuario.tipo_usuario == "cliente"

    def test_criar_usuario_mecanico(self, app):
        """Testa criação de usuário mecânico"""
        with app.app_context():
            usuario = Usuario(
                nome="Mecânico Teste",
                email="mecanico@test.com",
                tipo=TipoUsuario.MECANICO,
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            assert usuario.tipo == TipoUsuario.MECANICO
            assert usuario.tipo_usuario == "mecanico"

    def test_criar_usuario_gerente(self, app):
        """Testa criação de usuário gerente"""
        with app.app_context():
            usuario = Usuario(
                nome="Gerente Teste", email="gerente@test.com", tipo=TipoUsuario.GERENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            assert usuario.tipo == TipoUsuario.GERENTE
            assert usuario.tipo_usuario == "gerente"

    def test_verificar_senha_correta(self, app):
        """Testa verificação de senha correta"""
        with app.app_context():
            usuario = Usuario(
                nome="Teste", email="teste@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("minhasenha123")
            db.session.add(usuario)
            db.session.commit()

            assert usuario.verificar_senha("minhasenha123") is True

    def test_verificar_senha_incorreta(self, app):
        """Testa verificação de senha incorreta"""
        with app.app_context():
            usuario = Usuario(
                nome="Teste", email="teste2@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senhaCorreta")
            db.session.add(usuario)
            db.session.commit()

            assert usuario.verificar_senha("senhaErrada") is False

    def test_to_dict(self, app):
        """Testa serialização do usuário"""
        with app.app_context():
            usuario = Usuario(
                nome="Teste Dict",
                email="dict@test.com",
                tipo=TipoUsuario.CLIENTE,
                telefone="11999999999",
                endereco="Rua Teste, 123",
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            dados = usuario.to_dict()
            assert dados["nome"] == "Teste Dict"
            assert dados["email"] == "dict@test.com"
            assert dados["tipo"] == "cliente"
            assert dados["telefone"] == "11999999999"
            assert "senha_hash" not in dados

    def test_to_dict_com_veiculos(self, app):
        """Testa serialização do usuário com veículos"""
        with app.app_context():
            usuario = Usuario(
                nome="Teste Veiculos",
                email="veiculos@test.com",
                tipo=TipoUsuario.CLIENTE,
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="TST1234",
                modelo="Gol",
                marca="VW",
                ano=2020,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            dados = usuario.to_dict(include_veiculos=True)
            assert "veiculos" in dados
            assert len(dados["veiculos"]) == 1

    def test_repr(self, app):
        """Testa representação string do usuário"""
        with app.app_context():
            usuario = Usuario(
                nome="Teste Repr", email="repr@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            assert "repr@test.com" in repr(usuario)
            assert "cliente" in repr(usuario)

    def test_criado_em_alias(self, app):
        """Testa alias criado_em para data_cadastro"""
        with app.app_context():
            usuario = Usuario(
                nome="Teste Alias", email="alias@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            # criado_em e data_cadastro são preenchidos automaticamente
            assert usuario.criado_em is not None
            assert usuario.data_cadastro is not None


class TestVeiculoModel:
    """Testes para o model Veiculo"""

    def test_criar_veiculo(self, app):
        """Testa criação de veículo"""
        with app.app_context():
            usuario = Usuario(
                nome="Dono", email="dono@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="ABC1234",
                modelo="Civic",
                marca="Honda",
                ano=2022,
                cor="Preto",
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            assert veiculo.id is not None
            assert veiculo.placa == "ABC1234"
            assert veiculo.cor == "Preto"

    def test_to_dict(self, app):
        """Testa serialização do veículo"""
        with app.app_context():
            usuario = Usuario(
                nome="Dono Dict", email="dono_dict@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="DEF5678",
                modelo="Corolla",
                marca="Toyota",
                ano=2021,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            dados = veiculo.to_dict()
            assert dados["placa"] == "DEF5678"
            assert dados["modelo"] == "Corolla"
            assert dados["marca"] == "Toyota"

    def test_repr(self, app):
        """Testa representação string do veículo"""
        with app.app_context():
            usuario = Usuario(
                nome="Dono Repr", email="dono_repr@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="GHI9012",
                modelo="Onix",
                marca="Chevrolet",
                ano=2023,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            assert "GHI9012" in repr(veiculo)
            assert "Chevrolet" in repr(veiculo)


class TestServicoModel:
    """Testes para o model Servico"""

    def test_criar_servico(self, app):
        """Testa criação de serviço"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente Servico",
                email="cliente_servico@test.com",
                tipo=TipoUsuario.CLIENTE,
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="SRV1234",
                modelo="Fit",
                marca="Honda",
                ano=2020,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(
                descricao="Troca de óleo",
                veiculo_id=veiculo.id,
                status=StatusServico.PENDENTE,
            )
            db.session.add(servico)
            db.session.commit()

            assert servico.id is not None
            assert servico.status == StatusServico.PENDENTE

    def test_status_display(self, app):
        """Testa propriedade status_display"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente Display",
                email="display@test.com",
                tipo=TipoUsuario.CLIENTE,
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="DSP1234",
                modelo="HB20",
                marca="Hyundai",
                ano=2021,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(
                descricao="Teste Display",
                veiculo_id=veiculo.id,
                status=StatusServico.EM_ANDAMENTO,
            )
            db.session.add(servico)
            db.session.commit()

            assert servico.status_display == "Em Andamento"

    def test_status_class(self, app):
        """Testa propriedade status_class"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente Class", email="class@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="CLS1234",
                modelo="Sandero",
                marca="Renault",
                ano=2022,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(
                descricao="Teste Class",
                veiculo_id=veiculo.id,
                status=StatusServico.CONCLUIDO,
            )
            db.session.add(servico)
            db.session.commit()

            assert servico.status_class == "success"

    def test_valor_total_com_valor(self, app):
        """Testa cálculo de valor_total com valor definido"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente Valor", email="valor@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="VLR1234",
                modelo="Polo",
                marca="VW",
                ano=2020,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(
                descricao="Teste Valor",
                veiculo_id=veiculo.id,
                status=StatusServico.PENDENTE,
                valor=150.00,
            )
            db.session.add(servico)
            db.session.commit()

            assert servico.valor_total == 150.00

    def test_valor_total_com_orcamentos(self, app):
        """Testa cálculo de valor_total com orçamentos"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente Orcamento",
                email="orcamento@test.com",
                tipo=TipoUsuario.CLIENTE,
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="ORC1234",
                modelo="Kwid",
                marca="Renault",
                ano=2021,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(
                descricao="Teste Orçamento",
                veiculo_id=veiculo.id,
                status=StatusServico.PENDENTE,
            )
            db.session.add(servico)
            db.session.commit()

            orcamento1 = Orcamento(
                descricao="Peças", valor=100.00, servico_id=servico.id
            )
            orcamento2 = Orcamento(
                descricao="Mão de obra", valor=50.00, servico_id=servico.id
            )
            db.session.add_all([orcamento1, orcamento2])
            db.session.commit()

            assert servico.valor_total == 150.00

    def test_to_dict(self, app):
        """Testa serialização do serviço"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente Dict",
                email="servico_dict@test.com",
                tipo=TipoUsuario.CLIENTE,
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="DCT1234",
                modelo="Mobi",
                marca="Fiat",
                ano=2022,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(
                descricao="Teste Dict Servico",
                veiculo_id=veiculo.id,
                status=StatusServico.PENDENTE,
            )
            db.session.add(servico)
            db.session.commit()

            dados = servico.to_dict()
            assert dados["descricao"] == "Teste Dict Servico"
            assert dados["status"] == "pendente"


class TestOrcamentoModel:
    """Testes para o model Orcamento"""

    def test_criar_orcamento(self, app):
        """Testa criação de orçamento"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente Orcamento",
                email="criar_orcamento@test.com",
                tipo=TipoUsuario.CLIENTE,
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="ORC5678",
                modelo="Argo",
                marca="Fiat",
                ano=2023,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(descricao="Serviço para orçamento", veiculo_id=veiculo.id)
            db.session.add(servico)
            db.session.commit()

            orcamento = Orcamento(
                descricao="Orçamento teste", valor=200.00, servico_id=servico.id
            )
            db.session.add(orcamento)
            db.session.commit()

            assert orcamento.id is not None
            assert orcamento.valor == 200.00

    def test_valor_total_property(self, app):
        """Testa propriedade valor_total do orçamento"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente VT", email="vt@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="VTP1234",
                modelo="Uno",
                marca="Fiat",
                ano=2019,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(descricao="Serviço VT", veiculo_id=veiculo.id)
            db.session.add(servico)
            db.session.commit()

            orcamento = Orcamento(
                descricao="Orçamento VT", valor=350.50, servico_id=servico.id
            )
            db.session.add(orcamento)
            db.session.commit()

            assert orcamento.valor_total == 350.50

    def test_to_dict(self, app):
        """Testa serialização do orçamento"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente OD", email="od@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="ODT1234",
                modelo="Compass",
                marca="Jeep",
                ano=2024,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(descricao="Serviço OD", veiculo_id=veiculo.id)
            db.session.add(servico)
            db.session.commit()

            orcamento = Orcamento(
                descricao="Orçamento Dict", valor=500.00, servico_id=servico.id
            )
            db.session.add(orcamento)
            db.session.commit()

            dados = orcamento.to_dict()
            assert dados["descricao"] == "Orçamento Dict"
            assert dados["valor"] == 500.00
            assert dados["valor_total"] == 500.00

    def test_repr(self, app):
        """Testa representação string do orçamento"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente Repr", email="orc_repr@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="REP1234",
                modelo="Cruze",
                marca="Chevrolet",
                ano=2023,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            servico = Servico(descricao="Serviço Repr", veiculo_id=veiculo.id)
            db.session.add(servico)
            db.session.commit()

            orcamento = Orcamento(
                descricao="Orçamento Repr", valor=750.00, servico_id=servico.id
            )
            db.session.add(orcamento)
            db.session.commit()

            assert "750" in repr(orcamento)


class TestStatusServico:
    """Testes para o enum StatusServico"""

    def test_todos_status(self, app):
        """Testa todos os status disponíveis"""
        assert StatusServico.PENDENTE.value == "pendente"
        assert StatusServico.AGUARDANDO_ORCAMENTO.value == "aguardando_orcamento"
        assert StatusServico.ORCAMENTO_APROVADO.value == "orcamento_aprovado"
        assert StatusServico.EM_ANDAMENTO.value == "em_andamento"
        assert StatusServico.CONCLUIDO.value == "concluido"
        assert StatusServico.CANCELADO.value == "cancelado"

    def test_status_display_todos(self, app):
        """Testa status_display para todos os status"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente Status", email="status@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="STT1234",
                modelo="Tracker",
                marca="Chevrolet",
                ano=2024,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            # Testar cada status
            status_esperados = {
                StatusServico.PENDENTE: "Pendente",
                StatusServico.AGUARDANDO_ORCAMENTO: "Aguardando Orçamento",
                StatusServico.ORCAMENTO_APROVADO: "Orçamento Aprovado",
                StatusServico.EM_ANDAMENTO: "Em Andamento",
                StatusServico.CONCLUIDO: "Concluído",
                StatusServico.CANCELADO: "Cancelado",
            }

            for i, (status, display) in enumerate(status_esperados.items()):
                servico = Servico(
                    descricao=f"Teste status {i}", veiculo_id=veiculo.id, status=status
                )
                db.session.add(servico)
                db.session.commit()

                assert servico.status_display == display

    def test_status_class_todos(self, app):
        """Testa status_class para todos os status"""
        with app.app_context():
            usuario = Usuario(
                nome="Cliente Class", email="class2@test.com", tipo=TipoUsuario.CLIENTE
            )
            usuario.set_senha("senha123")
            db.session.add(usuario)
            db.session.commit()

            veiculo = Veiculo(
                placa="CLS5678",
                modelo="Renegade",
                marca="Jeep",
                ano=2023,
                usuario_id=usuario.id,
            )
            db.session.add(veiculo)
            db.session.commit()

            classes_esperadas = {
                StatusServico.PENDENTE: "warning",
                StatusServico.AGUARDANDO_ORCAMENTO: "info",
                StatusServico.ORCAMENTO_APROVADO: "primary",
                StatusServico.EM_ANDAMENTO: "primary",
                StatusServico.CONCLUIDO: "success",
                StatusServico.CANCELADO: "danger",
            }

            for i, (status, classe) in enumerate(classes_esperadas.items()):
                servico = Servico(
                    descricao=f"Teste class {i}", veiculo_id=veiculo.id, status=status
                )
                db.session.add(servico)
                db.session.commit()

                assert servico.status_class == classe


class TestTipoUsuario:
    """Testes para o enum TipoUsuario"""

    def test_todos_tipos(self, app):
        """Testa todos os tipos de usuário"""
        assert TipoUsuario.CLIENTE.value == "cliente"
        assert TipoUsuario.MECANICO.value == "mecanico"
        assert TipoUsuario.GERENTE.value == "gerente"
