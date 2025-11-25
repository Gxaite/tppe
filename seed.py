"""Script para popular o banco de dados com dados de teste"""
from app import create_app
from app.models import db, Usuario, Veiculo, Servico, Orcamento, StatusServico


def popular_banco():
    app = create_app()
    
    with app.app_context():
        # Limpar banco
        print("Limpando banco de dados...")
        db.drop_all()
        db.create_all()
        
        # Criar usuários
        print("Criando usuários...")
        
        # Gerente
        gerente = Usuario(
            nome='Maria Silva',
            email='gerente@oficina.com',
            tipo='gerente'
        )
        gerente.set_senha('senha123')
        db.session.add(gerente)
        
        # Mecânicos
        mecanico1 = Usuario(
            nome='João Mecânico',
            email='joao@oficina.com',
            tipo='mecanico'
        )
        mecanico1.set_senha('senha123')
        db.session.add(mecanico1)
        
        mecanico2 = Usuario(
            nome='Pedro Mecânico',
            email='pedro@oficina.com',
            tipo='mecanico'
        )
        mecanico2.set_senha('senha123')
        db.session.add(mecanico2)
        
        # Clientes
        cliente1 = Usuario(
            nome='Carlos Cliente',
            email='carlos@email.com',
            tipo='cliente'
        )
        cliente1.set_senha('senha123')
        db.session.add(cliente1)
        
        cliente2 = Usuario(
            nome='Ana Cliente',
            email='ana@email.com',
            tipo='cliente'
        )
        cliente2.set_senha('senha123')
        db.session.add(cliente2)
        
        cliente3 = Usuario(
            nome='Roberto Silva',
            email='roberto@email.com',
            tipo='cliente'
        )
        cliente3.set_senha('senha123')
        db.session.add(cliente3)
        
        db.session.commit()
        print(f"✓ {Usuario.query.count()} usuários criados")
        
        # Criar veículos
        print("Criando veículos...")
        
        veiculos_data = [
            {'placa': 'ABC1234', 'modelo': 'Civic', 'marca': 'Honda', 'ano': 2020, 'usuario': cliente1},
            {'placa': 'DEF5678', 'modelo': 'Corolla', 'marca': 'Toyota', 'ano': 2019, 'usuario': cliente1},
            {'placa': 'GHI9012', 'modelo': 'Gol', 'marca': 'Volkswagen', 'ano': 2018, 'usuario': cliente2},
            {'placa': 'JKL3456', 'modelo': 'Onix', 'marca': 'Chevrolet', 'ano': 2021, 'usuario': cliente2},
            {'placa': 'MNO7890', 'modelo': 'HB20', 'marca': 'Hyundai', 'ano': 2022, 'usuario': cliente3},
            {'placa': 'PQR1357', 'modelo': 'Uno', 'marca': 'Fiat', 'ano': 2015, 'usuario': cliente3},
        ]
        
        veiculos = []
        for v_data in veiculos_data:
            veiculo = Veiculo(
                placa=v_data['placa'],
                modelo=v_data['modelo'],
                marca=v_data['marca'],
                ano=v_data['ano'],
                usuario_id=v_data['usuario'].id
            )
            db.session.add(veiculo)
            veiculos.append(veiculo)
        
        db.session.commit()
        print(f"✓ {Veiculo.query.count()} veículos criados")
        
        # Criar serviços
        print("Criando serviços...")
        
        servicos_data = [
            {
                'descricao': 'Troca de óleo e filtros',
                'status': StatusServico.CONCLUIDO,
                'valor': 250.00,
                'veiculo': veiculos[0],
                'mecanico': mecanico1
            },
            {
                'descricao': 'Alinhamento e balanceamento',
                'status': StatusServico.EM_ANDAMENTO,
                'valor': 180.00,
                'veiculo': veiculos[1],
                'mecanico': mecanico1
            },
            {
                'descricao': 'Revisão completa',
                'status': StatusServico.PENDENTE,
                'valor': None,
                'veiculo': veiculos[2],
                'mecanico': None
            },
            {
                'descricao': 'Troca de pastilhas de freio',
                'status': StatusServico.EM_ANDAMENTO,
                'valor': 450.00,
                'veiculo': veiculos[3],
                'mecanico': mecanico2
            },
            {
                'descricao': 'Troca de bateria',
                'status': StatusServico.PENDENTE,
                'valor': None,
                'veiculo': veiculos[4],
                'mecanico': None
            },
            {
                'descricao': 'Diagnóstico elétrico',
                'status': StatusServico.CONCLUIDO,
                'valor': 320.00,
                'veiculo': veiculos[5],
                'mecanico': mecanico2
            },
        ]
        
        servicos = []
        for s_data in servicos_data:
            servico = Servico(
                descricao=s_data['descricao'],
                status=s_data['status'],
                valor=s_data['valor'],
                veiculo_id=s_data['veiculo'].id,
                mecanico_id=s_data['mecanico'].id if s_data['mecanico'] else None
            )
            db.session.add(servico)
            servicos.append(servico)
        
        db.session.commit()
        print(f"✓ {Servico.query.count()} serviços criados")
        
        # Criar orçamentos
        print("Criando orçamentos...")
        
        orcamentos_data = [
            {
                'descricao': 'Óleo sintético 5W30 + filtros de óleo, ar e combustível',
                'valor': 250.00,
                'servico': servicos[0]
            },
            {
                'descricao': 'Alinhamento 3D + balanceamento 4 rodas',
                'valor': 180.00,
                'servico': servicos[1]
            },
            {
                'descricao': 'Revisão de 60mil km - peças e mão de obra',
                'valor': 850.00,
                'servico': servicos[2]
            },
            {
                'descricao': 'Pastilhas + discos dianteiros',
                'valor': 450.00,
                'servico': servicos[3]
            },
        ]
        
        for o_data in orcamentos_data:
            orcamento = Orcamento(
                descricao=o_data['descricao'],
                valor=o_data['valor'],
                servico_id=o_data['servico'].id
            )
            db.session.add(orcamento)
        
        db.session.commit()
        print(f"✓ {Orcamento.query.count()} orçamentos criados")
        
        print("\n" + "="*50)
        print("Banco de dados populado com sucesso!")
        print("="*50)
        print("\nUsuários criados:")
        print(f"  Gerente: gerente@oficina.com / senha123")
        print(f"  Mecânico 1: joao@oficina.com / senha123")
        print(f"  Mecânico 2: pedro@oficina.com / senha123")
        print(f"  Cliente 1: carlos@email.com / senha123")
        print(f"  Cliente 2: ana@email.com / senha123")
        print(f"  Cliente 3: roberto@email.com / senha123")
        print("\n" + "="*50)


if __name__ == '__main__':
    popular_banco()
