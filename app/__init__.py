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
        from app.routes import auth, veiculos, servicos, dashboard, usuarios, views
        
        app.register_blueprint(views.bp)  # Frontend (HTML)
        app.register_blueprint(auth.bp)   # API
        app.register_blueprint(usuarios.bp)
        app.register_blueprint(veiculos.bp)
        app.register_blueprint(servicos.bp)
        app.register_blueprint(dashboard.bp)
        
        # Criar tabelas
        db.create_all()
    
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('views.login'))
    
    return app
