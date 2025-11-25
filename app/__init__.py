import os
from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv

from app.models import db

# Carregar variáveis de ambiente
load_dotenv()

migrate = Migrate()


def create_app(config=None):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/mecanica_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hora
    
    # Configurações adicionais se fornecidas
    if config:
        app.config.update(config)
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Registrar blueprints
    with app.app_context():
        from app.routes import auth, veiculos, servicos, dashboard, usuarios
        
        app.register_blueprint(auth.bp)
        app.register_blueprint(usuarios.bp)
        app.register_blueprint(veiculos.bp)
        app.register_blueprint(servicos.bp)
        app.register_blueprint(dashboard.bp)
        
        # Criar tabelas
        db.create_all()
    
    @app.route('/')
    def index():
        return {
            'message': 'Sistema de Gerenciamento de Oficina Mecânica',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/auth',
                'usuarios': '/usuarios',
                'veiculos': '/veiculos',
                'servicos': '/servicos',
                'dashboard': '/dashboard'
            }
        }
    
    return app
