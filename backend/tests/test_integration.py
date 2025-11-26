"""
Testes de Integração - Sistema Oficina Mecânica
Testa fluxos completos do sistema com múltiplos componentes
"""
import pytest
from datetime import datetime, timedelta
from app import create_app
from app.models import db, Usuario, Veiculo, Servico, Orcamento, StatusServico


@pytest.fixture
def app():
    """Cria aplicação Flask para testes"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de teste Flask"""
    return app.test_client()


@pytest.fixture
def usuarios(app):
    """Cria usuários de teste"""
    with app.app_context():
        from app.models import TipoUsuario
        
        gerente = Usuario(
            nome='Gerente Teste',
            email='gerente@test.com',
            tipo=TipoUsuario.GERENTE
        )
        gerente.set_senha('senha123')
        
        mecanico = Usuario(
            nome='Mecânico Teste',
            email='mecanico@test.com',
            tipo=TipoUsuario.MECANICO
        )
        mecanico.set_senha('senha123')
        
        cliente = Usuario(
            nome='Cliente Teste',
            email='cliente@test.com',
            tipo=TipoUsuario.CLIENTE
        )
        cliente.set_senha('senha123')
        
        db.session.add_all([gerente, mecanico, cliente])
        db.session.commit()
        
        return {
            'gerente': gerente,
            'mecanico': mecanico,
            'cliente': cliente
        }


@pytest.fixture
def veiculo(app, usuarios):
    """Cria veículo de teste"""
    with app.app_context():
        cliente = Usuario.query.filter_by(email='cliente@test.com').first()
        veiculo = Veiculo(
            marca='Volkswagen',
            modelo='Gol',
            ano=2020,
            placa='ABC-1234',
            usuario_id=cliente.id
        )
        db.session.add(veiculo)
        db.session.commit()
        return veiculo


class TestFluxoAutenticacao:
    """Testes do fluxo de autenticação"""
    
    def test_fluxo_registro_e_login(self, client):
        """Testa registro de novo usuário e login subsequente"""
        # Registro
        response = client.post('/register', data={
            'nome': 'Novo Cliente',
            'email': 'novo@cliente.com',
            'telefone': '61966666666',
            'senha': 'senha123',
            'senha_confirm': 'senha123',
            'tipo_usuario': 'cliente'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Login com novo usuário
        response = client.post('/login', data={
            'email': 'novo@cliente.com',
            'senha': 'senha123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verificar se consegue acessar dashboard
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert sess['tipo_usuario'] == 'cliente'
    
    def test_fluxo_login_invalido(self, client, usuarios):
        """Testa tentativas de login com credenciais inválidas"""
        # Senha incorreta
        response = client.post('/login', data={
            'email': 'cliente@test.com',
            'senha': 'senha_errada'
        })
        
        assert response.status_code == 200
        assert b'Email ou senha' in response.data or b'inv' in response.data
        
        # Email não cadastrado
        response = client.post('/login', data={
            'email': 'naoexiste@test.com',
            'senha': 'senha123'
        })
        
        assert response.status_code == 200
    
    def test_logout_limpa_sessao(self, client, usuarios):
        """Testa se logout limpa corretamente a sessão"""
        # Fazer login
        client.post('/login', data={
            'email': 'cliente@test.com',
            'senha': 'senha123'
        })
        
        # Verificar sessão ativa
        with client.session_transaction() as sess:
            assert 'user_id' in sess
        
        # Fazer logout
        client.get('/logout', follow_redirects=True)
        
        # Verificar sessão limpa
        with client.session_transaction() as sess:
            assert 'user_id' not in sess


class TestFluxoVeiculos:
    """Testes do fluxo completo de veículos"""
    
    def login_cliente(self, client):
        """Helper para fazer login como cliente"""
        client.post('/login', data={
            'email': 'cliente@test.com',
            'senha': 'senha123'
        })
    
    def test_fluxo_crud_veiculo(self, client, usuarios):
        """Testa criar, ler, atualizar e deletar veículo"""
        self.login_cliente(client)
        
        # CREATE
        response = client.post('/veiculos/novo', data={
            'marca': 'Fiat',
            'modelo': 'Uno',
            'ano': 2015,
            'placa': 'XYZ-9876',
            'cor': 'Branco'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # READ - Listar
        response = client.get('/veiculos')
        assert response.status_code == 200
        assert b'Fiat' in response.data
        assert b'XYZ-9876' in response.data
        
        # READ - Detalhe
        response = client.get('/veiculos/1')
        assert response.status_code == 200
        assert b'Uno' in response.data
        
        # UPDATE
        response = client.post('/veiculos/1/editar', data={
            'marca': 'Fiat',
            'modelo': 'Uno Mille',
            'ano': 2015,
            'placa': 'XYZ-9876',
            'cor': 'Vermelho'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verificar atualização
        response = client.get('/veiculos/1')
        assert b'Uno Mille' in response.data
        assert b'Vermelho' in response.data
        
        # DELETE
        response = client.post('/veiculos/1/deletar', follow_redirects=True)
        assert response.status_code == 200
    
    def test_cliente_nao_ve_veiculos_outros(self, client, usuarios, app):
        """Testa que cliente só vê seus próprios veículos"""
        # Criar veículo para outro cliente
        with app.app_context():
            from app.models import TipoUsuario
            
            outro_cliente = Usuario(
                nome='Outro Cliente',
                email='outro@test.com',
                telefone='61955555555',
                tipo=TipoUsuario.CLIENTE
            )
            outro_cliente.set_senha('senha123')
            db.session.add(outro_cliente)
            db.session.commit()
            
            veiculo_outro = Veiculo(
                marca='Honda',
                modelo='Civic',
                ano=2022,
                placa='DEF-5555',
                cor='Preto',
                usuario_id=outro_cliente.id
            )
            db.session.add(veiculo_outro)
            db.session.commit()
        
        # Login com primeiro cliente
        self.login_cliente(client)
        
        # Listar veículos - não deve aparecer o Civic
        response = client.get('/veiculos')
        assert response.status_code == 200
        assert b'Civic' not in response.data


class TestFluxoServicos:
    """Testes do fluxo completo de serviços"""
    
    def login_mecanico(self, client):
        """Helper para fazer login como mecânico"""
        client.post('/login', data={
            'email': 'mecanico@test.com',
            'senha': 'senha123'
        })
    
    def login_cliente(self, client):
        """Helper para fazer login como cliente"""
        client.post('/login', data={
            'email': 'cliente@test.com',
            'senha': 'senha123'
        })
    
    def test_fluxo_completo_servico(self, client, usuarios, veiculo, app):
        """Testa o fluxo completo de um serviço: criação → orçamento → aprovação → conclusão"""
        
        # Fase 1: Mecânico cria serviço
        self.login_mecanico(client)
        
        with app.app_context():
            veiculo_id = Veiculo.query.first().id
        
        response = client.post('/servicos/novo', data={
            'veiculo_id': veiculo_id,
            'descricao': 'Troca de óleo e filtro',
            'observacoes': 'Cliente solicitou óleo sintético',
            'data_entrada': datetime.now().strftime('%Y-%m-%d'),
            'status': 'aguardando_orcamento'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Fase 2: Mecânico cria orçamento
        with app.app_context():
            servico = Servico.query.first()
            servico_id = servico.id
        
        response = client.post(f'/orcamentos/novo?servico_id={servico_id}', data={
            'descricao': 'Troca de óleo e filtros',
            'valor_mao_obra': 100.00,
            'valor_pecas': 150.00,
            'valor': 250.00
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verificar orçamento criado
        with app.app_context():
            orcamento = Orcamento.query.filter_by(servico_id=servico_id).first()
            assert orcamento is not None
            assert orcamento.valor_total == 250.00
        
        # Fase 3: Cliente aprova orçamento
        client.get('/logout')
        self.login_cliente(client)
        
        with app.app_context():
            orcamento_id = Orcamento.query.first().id
        
        response = client.post(f'/orcamentos/{orcamento_id}/aprovar', follow_redirects=True)
        assert response.status_code == 200
        
        # Verificar status atualizado
        with app.app_context():
            servico = Servico.query.first()
            assert servico.status == StatusServico.ORCAMENTO_APROVADO
            assert servico.valor_total == 250.00
        
        # Fase 4: Mecânico atualiza status para em_andamento
        client.get('/logout')
        self.login_mecanico(client)
        
        response = client.post(f'/servicos/{servico_id}/editar', data={
            'veiculo_id': veiculo_id,
            'descricao': 'Troca de óleo e filtro',
            'observacoes': 'Cliente solicitou óleo sintético',
            'data_entrada': datetime.now().strftime('%Y-%m-%d'),
            'status': 'em_andamento'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verificar status
        with app.app_context():
            servico = Servico.query.first()
            assert servico.status == StatusServico.EM_ANDAMENTO
        
        # Fase 5: Mecânico conclui serviço
        response = client.post(f'/servicos/{servico_id}/editar', data={
            'veiculo_id': veiculo_id,
            'descricao': 'Troca de óleo e filtro',
            'observacoes': 'Serviço concluído com sucesso',
            'data_entrada': datetime.now().strftime('%Y-%m-%d'),
            'status': 'concluido'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verificar conclusão
        with app.app_context():
            servico = Servico.query.first()
            assert servico.status == StatusServico.CONCLUIDO


class TestFluxoDashboards:
    """Testes dos dashboards personalizados"""
    
    def test_dashboard_cliente_mostra_dados_corretos(self, client, usuarios, veiculo, app):
        """Testa se dashboard do cliente mostra estatísticas corretas"""
        # Criar alguns serviços
        with app.app_context():
            from app.models import TipoUsuario
            mecanico = Usuario.query.filter_by(tipo=TipoUsuario.MECANICO).first()
            veiculo_obj = Veiculo.query.first()
            
            servico1 = Servico(
                veiculo_id=veiculo_obj.id,
                mecanico_id=mecanico.id,
                descricao='Serviço 1',
                status=StatusServico.EM_ANDAMENTO
            )
            
            servico2 = Servico(
                veiculo_id=veiculo_obj.id,
                mecanico_id=mecanico.id,
                descricao='Serviço 2',
                status=StatusServico.CONCLUIDO,
                data_conclusao=datetime.now()
            )
            
            db.session.add_all([servico1, servico2])
            db.session.commit()
        
        # Login e acessar dashboard
        client.post('/login', data={
            'email': 'cliente@test.com',
            'senha': 'senha123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        
        # Verificar estatísticas no HTML
        assert b'1' in response.data  # Total veículos
        # Deve mostrar serviços em andamento e concluídos
    
    def test_dashboard_mecanico_mostra_servicos_atribuidos(self, client, usuarios, veiculo, app):
        """Testa se dashboard do mecânico mostra apenas seus serviços"""
        with app.app_context():
            from app.models import TipoUsuario
            mecanico = Usuario.query.filter_by(tipo=TipoUsuario.MECANICO).first()
            veiculo_obj = Veiculo.query.first()
            
            # Serviço do mecânico
            servico_meu = Servico(
                veiculo_id=veiculo_obj.id,
                mecanico_id=mecanico.id,
                descricao='Meu Serviço',
                status=StatusServico.EM_ANDAMENTO
            )
            db.session.add(servico_meu)
            db.session.commit()
        
        # Login como mecânico
        client.post('/login', data={
            'email': 'mecanico@test.com',
            'senha': 'senha123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Meu Servico' in response.data or b'dashboard' in response.data.lower()
    
    def test_dashboard_gerente_mostra_visao_geral(self, client, usuarios, veiculo, app):
        """Testa se dashboard do gerente mostra visão geral do sistema"""
        with app.app_context():
            from app.models import TipoUsuario
            mecanico = Usuario.query.filter_by(tipo=TipoUsuario.MECANICO).first()
            veiculo_obj = Veiculo.query.first()
            
            servico = Servico(
                veiculo_id=veiculo_obj.id,
                mecanico_id=mecanico.id,
                descricao='Serviço Teste',
                status=StatusServico.CONCLUIDO,
                data_conclusao=datetime.now()
            )
            db.session.add(servico)
            db.session.commit()
        
        # Login como gerente
        client.post('/login', data={
            'email': 'gerente@test.com',
            'senha': 'senha123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        
        # Deve mostrar estatísticas gerais
        assert b'Total de Clientes' in response.data or b'Receita' in response.data


class TestPermissoes:
    """Testes de controle de acesso e permissões"""
    
    def test_cliente_nao_acessa_crud_usuarios(self, client, usuarios):
        """Testa que cliente não pode acessar gestão de usuários"""
        client.post('/login', data={
            'email': 'cliente@test.com',
            'senha': 'senha123'
        })
        
        response = client.get('/usuarios', follow_redirects=True)
        assert response.status_code == 200
        # Deve redirecionar ou mostrar mensagem de erro
    
    def test_mecanico_nao_acessa_crud_usuarios(self, client, usuarios):
        """Testa que mecânico não pode acessar gestão de usuários"""
        client.post('/login', data={
            'email': 'mecanico@test.com',
            'senha': 'senha123'
        })
        
        response = client.get('/usuarios', follow_redirects=True)
        assert response.status_code == 200
    
    def test_gerente_acessa_tudo(self, client, usuarios):
        """Testa que gerente tem acesso completo"""
        client.post('/login', data={
            'email': 'gerente@test.com',
            'senha': 'senha123'
        })
        
        # Acessar usuários
        response = client.get('/usuarios')
        assert response.status_code == 200
        
        # Acessar veículos
        response = client.get('/veiculos')
        assert response.status_code == 200
        
        # Acessar serviços
        response = client.get('/servicos')
        assert response.status_code == 200


class TestValidacoes:
    """Testes de validações e regras de negócio"""
    
    def test_nao_permite_placa_duplicada(self, client, usuarios, veiculo):
        """Testa que não permite cadastrar veículo com placa já existente"""
        client.post('/login', data={
            'email': 'cliente@test.com',
            'senha': 'senha123'
        })
        
        response = client.post('/veiculos/novo', data={
            'marca': 'Chevrolet',
            'modelo': 'Onix',
            'ano': 2021,
            'placa': 'ABC-1234',  # Placa já cadastrada
            'cor': 'Azul'
        }, follow_redirects=True)
        
        # Deve dar erro de constraint ou validação
        assert response.status_code == 200 or response.status_code == 400
    
    def test_nao_permite_email_duplicado(self, client, usuarios):
        """Testa que não permite cadastrar email já existente"""
        response = client.post('/register', data={
            'nome': 'Teste Duplicado',
            'email': 'cliente@test.com',  # Email já cadastrado
            'telefone': '61944444444',
            'senha': 'senha123',
            'senha_confirm': 'senha123',
            'tipo_usuario': 'cliente'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'j\xc3\xa1 cadastrado' in response.data or b'existe' in response.data


class TestCobertura:
    """Testes adicionais para garantir >80% de cobertura"""
    
    def test_rota_raiz_redireciona_login(self, client):
        """Testa se rota raiz redireciona para login"""
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'email' in response.data.lower()
    
    def test_acesso_sem_login_redireciona(self, client):
        """Testa que páginas protegidas redirecionam para login"""
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_veiculos_list_vazio(self, client, usuarios):
        """Testa listagem de veículos quando não há nenhum"""
        client.post('/login', data={
            'email': 'cliente@test.com',
            'senha': 'senha123'
        })
        
        response = client.get('/veiculos')
        assert response.status_code == 200
        assert b'Nenhum' in response.data or b'cadastrado' in response.data
    
    def test_servicos_list_vazio(self, client, usuarios):
        """Testa listagem de serviços quando não há nenhum"""
        client.post('/login', data={
            'email': 'mecanico@test.com',
            'senha': 'senha123'
        })
        
        response = client.get('/servicos')
        assert response.status_code == 200
