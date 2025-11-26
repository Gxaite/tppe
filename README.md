# Sistema de Gerenciamento de Oficina Mecânica

Sistema web para gerenciamento de oficina mecânica com Flask, PostgreSQL e Docker.

## Pré-requisitos

- Docker
- Docker Compose

## Como Rodar

```bash
# Subir o sistema
docker compose up -d

# Popular banco com dados de teste
docker compose exec backend python seed.py

# Acessar: http://localhost:5000
```

## Usuários de Teste

| Tipo | Email | Senha |
|------|-------|-------|
| Gerente | gerente@oficina.com | senha123 |
| Mecânico | joao@oficina.com | senha123 |
| Cliente | carlos@email.com | senha123 |

## Testes

```bash
# Testes unitários e integração
docker compose exec backend pytest

# Com cobertura
docker compose exec backend pytest --cov=app --cov-report=term

# Testes E2E com Selenium (requer Chrome instalado localmente)
pip install selenium
pytest backend/tests/test_e2e_selenium.py -v
```

**125 testes unitários | ~80% cobertura**

## Lint

```bash
# Verificar código
docker compose exec backend flake8 app/ tests/

# Formatar código
docker compose exec backend black app/ tests/
```

## Estrutura

```
tppe/
├── backend/
│   ├── app/              # Código Flask
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── routes/       # Endpoints
│   │   └── utils.py      # Helpers
│   ├── tests/            # Testes pytest
│   ├── migrations/       # Alembic
│   └── requirements.txt
├── frontend/
│   ├── static/css/       # Estilos
│   └── templates/        # Jinja2
├── docs/                 # Documentação
└── docker-compose.yml
```

## Stack

- Flask 3.0 + SQLAlchemy 2.0
- PostgreSQL 15
- Docker Compose
- pytest + flake8 + black

## Funcionalidades

- **Cliente:** CRUD veículos, solicitar serviços, ver status
- **Mecânico:** Ver serviços atribuídos, atualizar status
- **Gerente:** Gerenciar tudo, criar orçamentos, atribuir mecânicos
