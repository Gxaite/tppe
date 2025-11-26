from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()


class TipoUsuario(str, Enum):
    CLIENTE = "cliente"
    GERENTE = "gerente"
    MECANICO = "mecanico"


class StatusServico(str, Enum):
    PENDENTE = "pendente"
    AGUARDANDO_ORCAMENTO = "aguardando_orcamento"
    ORCAMENTO_APROVADO = "orcamento_aprovado"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    endereco = db.Column(db.String(200), nullable=True)
    tipo = db.Column(db.Enum(TipoUsuario), nullable=False, default=TipoUsuario.CLIENTE)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Aliases para compatibilidade
    @property
    def criado_em(self):
        return self.data_cadastro

    @property
    def tipo_usuario(self):
        return self.tipo.value

    # Relacionamentos
    veiculos = db.relationship(
        'Veiculo', backref='proprietario', lazy=True, cascade='all, delete-orphan'
    )
    servicos_como_mecanico = db.relationship(
        'Servico', backref='mecanico', lazy=True, foreign_keys='Servico.mecanico_id'
    )

    def set_senha(self, senha):
        """Hash da senha usando bcrypt"""
        self.senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verificar_senha(self, senha):
        """Verifica se a senha está correta"""
        return bcrypt.checkpw(senha.encode('utf-8'), self.senha_hash.encode('utf-8'))

    def to_dict(self, include_veiculos=False):
        data = {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'endereco': self.endereco,
            'tipo': self.tipo.value,
            'data_cadastro': self.data_cadastro.isoformat()
        }
        if include_veiculos:
            data['veiculos'] = [v.to_dict() for v in self.veiculos]
        return data

    def __repr__(self):
        return f'<Usuario {self.email} - {self.tipo.value}>'


class Veiculo(db.Model):
    __tablename__ = 'veiculos'

    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False, index=True)
    modelo = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    cor = db.Column(db.String(30), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    servicos = db.relationship('Servico', backref='veiculo', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_servicos=False):
        data = {
            'id': self.id,
            'placa': self.placa,
            'modelo': self.modelo,
            'marca': self.marca,
            'ano': self.ano,
            'cor': self.cor,
            'usuario_id': self.usuario_id,
            'criado_em': self.criado_em.isoformat()
        }
        if include_servicos:
            data['servicos'] = [s.to_dict() for s in self.servicos]
        return data

    def __repr__(self):
        return f'<Veiculo {self.placa} - {self.marca} {self.modelo}>'


class Servico(db.Model):
    __tablename__ = 'servicos'

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(StatusServico), nullable=False, default=StatusServico.PENDENTE)
    valor = db.Column(db.Numeric(10, 2), nullable=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    mecanico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    data_previsao = db.Column(db.DateTime, nullable=True)
    data_conclusao = db.Column(db.DateTime, nullable=True)

    # Relacionamentos
    orcamentos = db.relationship('Orcamento', backref='servico', lazy=True, cascade='all, delete-orphan')

    @property
    def valor_total(self):
        """Retorna o valor total do serviço incluindo orçamentos"""
        if self.valor:
            return float(self.valor)
        # Soma valores dos orçamentos se não houver valor definido
        if self.orcamentos:
            return sum(float(o.valor) for o in self.orcamentos)
        return 0.0

    @property
    def status_display(self):
        """Retorna o status formatado para exibição"""
        status_map = {
            'pendente': 'Pendente',
            'aguardando_orcamento': 'Aguardando Orçamento',
            'orcamento_aprovado': 'Orçamento Aprovado',
            'em_andamento': 'Em Andamento',
            'concluido': 'Concluído',
            'cancelado': 'Cancelado'
        }
        return status_map.get(self.status.value, self.status.value)

    @property
    def status_class(self):
        """Retorna a classe CSS para o status"""
        status_class_map = {
            'pendente': 'warning',
            'aguardando_orcamento': 'info',
            'orcamento_aprovado': 'primary',
            'em_andamento': 'primary',
            'concluido': 'success',
            'cancelado': 'danger'
        }
        return status_class_map.get(self.status.value, 'secondary')

    def to_dict(self, include_orcamentos=False):
        data = {
            'id': self.id,
            'descricao': self.descricao,
            'observacoes': self.observacoes,
            'status': self.status.value,
            'valor': float(self.valor) if self.valor else None,
            'valor_total': self.valor_total,
            'veiculo_id': self.veiculo_id,
            'mecanico_id': self.mecanico_id,
            'criado_em': self.criado_em.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat(),
            'data_previsao': self.data_previsao.isoformat() if self.data_previsao else None,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None
        }
        if include_orcamentos:
            data['orcamentos'] = [o.to_dict() for o in self.orcamentos]
        return data

    def __repr__(self):
        return f'<Servico {self.id} - {self.status.value}>'


class Orcamento(db.Model):
    __tablename__ = 'orcamentos'

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def valor_total(self):
        """Alias para valor para compatibilidade"""
        return float(self.valor)

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'valor': float(self.valor),
            'valor_total': self.valor_total,
            'servico_id': self.servico_id,
            'criado_em': self.criado_em.isoformat()
        }

    def __repr__(self):
        return f'<Orcamento {self.id} - R$ {self.valor}>'
