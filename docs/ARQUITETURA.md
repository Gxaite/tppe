# Arquitetura do Sistema

## Visão Geral

**Padrão:** Monolito em camadas  
**Framework:** Flask 3.0  
**Containerização:** Docker Compose

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENTE                             │
│                   (Browser / API Client)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLASK APPLICATION                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Routes (Blueprints)                     │  │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │  Auth   │ │Usuarios │ │ Veiculos │ │ Servicos │ │  │
│  │  └─────────┘ └─────────┘ └──────────┘ └──────────┘ │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │              Business Logic                          │  │
│  │            (Utils, Decorators, JWT)                  │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │            SQLAlchemy ORM (Models)                   │  │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │ Usuario │ │ Veiculo │ │ Servico  │ │Orcamento │ │  │
│  │  └─────────┘ └─────────┘ └──────────┘ └──────────┘ │  │
│  └──────────────────────┬───────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────┘
                          │ SQL
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL 15                            │
│                   (Banco de Dados)                          │
└─────────────────────────────────────────────────────────────┘
```

## Camadas

### 1. Apresentação (Routes/Blueprints)
- `auth.py` - Autenticação/Autorização
- `usuarios.py` - CRUD usuários
- `veiculos.py` - CRUD veículos
- `servicos.py` - CRUD serviços + orçamentos
- `dashboard.py` - Agregação de dados

### 2. Negócio (Utils)
- JWT token management
- Decorators: `@token_required`, `@requer_tipo_usuario`
- Validações e regras de negócio

### 3. Dados (Models/SQLAlchemy)
- `Usuario` - Autenticação, tipos (cliente/mecânico/gerente)
- `Veiculo` - Cadastro vinculado a usuário
- `Servico` - Workflow de serviços
- `Orcamento` - Orçamentos de serviços

### 4. Persistência (PostgreSQL 15)
- Relacionamentos 1:N
- Índices: email, placa
- ACID compliance

## Padrões de Design

**Factory Pattern** - `create_app()` para inicialização  
**Blueprint Pattern** - Modularização de rotas  
**Decorator Pattern** - `@token_required`, `@requer_tipo_usuario`  
**Repository Pattern** - SQLAlchemy ORM

## Fluxo de Exemplo

```
POST /servicos
  ↓
JWT Auth (decorator)
  ↓
Validação de permissões
  ↓
Validação de dados
  ↓
Criação no banco (SQLAlchemy)
  ↓
Retorno JSON
```

## Segurança

**Autenticação:**
- JWT com expiração (1h)
- Senhas: bcrypt hash

**Autorização:**
- RBAC: cliente, mecânico, gerente
- Decorators em endpoints

**Validações:**
- Unicidade: email, placa
- Relacionamentos verificados

## Containerização

```yaml
app:     # Flask
db:      # PostgreSQL
volumes: # postgres_data
network: # bridge
```

**Benefícios:** Ambiente reproduzível, fácil deploy, healthchecks

## Modelo de Dados

```
Usuario (1:N) → Veiculo (1:N) → Servico (1:N) → Orcamento
Usuario/Mecanico (1:N) → Servico
```

## Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| Backend | Flask 3.0, SQLAlchemy 2.0 |
| Database | PostgreSQL 15 |
| Auth | PyJWT 2.8, bcrypt |
| Container | Docker Compose |
| Tests | pytest 7.4 |
| Lint | flake8, black |

## Testes

**Estratégia:** Unitários + Integração  
**Fixtures:** Reutilizáveis (conftest.py)  
**Banco:** In-memory SQLite  
**Cobertura:** 80%+

## Deploy

**Plataformas:** Render, Railway, Fly.io, AWS ECS  
**Requisitos:** Docker, env vars (DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY)
