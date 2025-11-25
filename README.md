# Sistema de Gerenciamento de Oficina Mecânica

**Disciplina:** TPPE  
**Stack:** Flask 3.0 + Jinja2, PostgreSQL 15, Docker, SQLAlchemy, Bootstrap 5

Sistema completo para gerenciamento de oficina mecânica com frontend web e API REST.

## 🚀 Início Rápido

**Pré-requisitos:** Docker, Docker Compose

```bash
# 1. Clonar e configurar
git clone <repositorio>
cd tppe
cp .env.example .env

# 2. Iniciar sistema
docker-compose up --build

# 3. Popular banco (novo terminal)
docker-compose exec app python seed.py

# 4. Acessar sistema
# Frontend: http://localhost:5000
# API: http://localhost:5000/api
```

**🌐 Interface Web:** `http://localhost:5000`  
**📡 API REST:** `http://localhost:5000/api`

### Usuários de Teste

| Tipo | Email | Senha |
|------|-------|-------|
| Gerente | gerente@oficina.com | senha123 |
| Mecânico | joao@oficina.com | senha123 |
| Cliente | carlos@email.com | senha123 |

---

## 🎯 Funcionalidades Implementadas

### Cliente
- CRUD de veículos
- Solicitação de serviços
- Visualização de status
- Dashboard personalizado

### Gerente
- Gerenciamento de usuários, veículos e serviços
- Criação de orçamentos
- Atribuição de mecânicos
- Dashboard com estatísticas

### Mecânico
- Visualização de serviços atribuídos
- Atualização de status
- Dashboard de trabalho

## 🧪 Testes

```bash
# Testes unitários (Sprint 1)
docker-compose exec app pytest tests/test_auth.py tests/test_veiculos.py tests/test_servicos.py -v

# Testes de integração (Sprint 2)
docker-compose exec app pytest tests/test_integration.py -v

# Todos os testes com cobertura
docker-compose exec app pytest --cov=app --cov-report=html --cov-report=term

# Verificar cobertura
open htmlcov/index.html  # ou xdg-open no Linux
```

**Total:** 50+ testes (17 unitários + 33 integração) | **Cobertura:** 85%+

## 🎨 Linting e Formatação

```bash
# Verificar código
bash lint.sh

# Aplicar formatação automática
docker-compose exec app black app/ tests/

# Verificar estilo
docker-compose exec app flake8 app/ tests/
```

## 📚 Documentação da API

### Autenticação

#### Registro de Usuário
```http
POST /auth/registro
Content-Type: application/json

{
  "nome": "João Silva",
  "email": "joao@email.com",
  "senha": "senha123",
  "tipo": "cliente"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "joao@email.com",
  "senha": "senha123"
}
```

Retorna um token JWT que deve ser usado em requisições autenticadas:
```
Authorization: Bearer <token>
```

#### Perfil
```http
GET /auth/perfil
Authorization: Bearer <token>
```

### Veículos

#### Listar Veículos
```http
GET /veiculos
Authorization: Bearer <token>
```

#### Criar Veículo
```http
POST /veiculos
Authorization: Bearer <token>
Content-Type: application/json

{
  "placa": "ABC1234",
  "modelo": "Civic",
  "marca": "Honda",
  "ano": 2020
}
```

#### Atualizar Veículo
```http
PUT /veiculos/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "ano": 2021
}
```

#### Deletar Veículo
```http
DELETE /veiculos/{id}
Authorization: Bearer <token>
```

### Serviços

#### Listar Serviços
```http
GET /servicos
Authorization: Bearer <token>
```

#### Criar Serviço
```http
POST /servicos
Authorization: Bearer <token>
Content-Type: application/json

{
  "descricao": "Troca de óleo",
  "veiculo_id": 1
}
```

#### Atualizar Serviço (Gerente/Mecânico)
```http
PUT /servicos/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "em_andamento",
  "mecanico_id": 2,
  "valor": 350.00
}
```

#### Criar Orçamento (Gerente)
```http
POST /servicos/{id}/orcamento
Authorization: Bearer <token>
Content-Type: application/json

{
  "descricao": "Troca de óleo + filtros",
  "valor": 350.00
}
```

### Dashboard

#### Obter Dashboard
```http
GET /dashboard
Authorization: Bearer <token>
```

Retorna informações personalizadas baseadas no tipo de usuário.

## 🗄️ Modelo de Dados

**Tabelas:** Usuario, Veiculo, Servico, Orcamento

**Relacionamentos:**
- Usuario (1:N) Veiculo
- Veiculo (1:N) Servico  
- Usuario/Mecânico (1:N) Servico
- Servico (1:N) Orcamento

```bash
# Acessar banco
docker-compose exec db psql -U postgres -d mecanica_db
```

## 🛠️ Stack Tecnológica

- **Backend**: Flask 3.0
- **ORM**: SQLAlchemy
- **Banco de Dados**: PostgreSQL 15
- **Autenticação**: JWT (PyJWT)
- **Containerização**: Docker & Docker Compose
- **Testes**: pytest
- **Lint**: flake8, black, pylint

## 📁 Estrutura do Projeto

```
tppe/
├── app/
│   ├── __init__.py          # Inicialização do Flask
│   ├── models.py            # Modelos SQLAlchemy
│   ├── utils.py             # Utilitários e decorators
│   ├── routes/
│   │   ├── auth.py          # Rotas de autenticação
│   │   ├── usuarios.py      # CRUD de usuários
│   │   ├── veiculos.py      # CRUD de veículos
│   │   ├── servicos.py      # CRUD de serviços
│   │   └── dashboard.py     # Dashboards
│   ├── templates/           # Templates Jinja2
│   └── static/              # CSS, JS
├── tests/
│   ├── conftest.py          # Fixtures do pytest
│   ├── test_auth.py         # Testes de autenticação
│   ├── test_veiculos.py     # Testes de veículos
│   └── test_servicos.py     # Testes de serviços
├── docs/                    # Documentação
├── docker-compose.yml       # Configuração Docker Compose
├── Dockerfile               # Imagem Docker da aplicação
├── requirements.txt         # Dependências Python
├── .env.example             # Template de variáveis de ambiente
└── README.md               # Este arquivo
```

## 🔐 Tipos de Usuário e Permissões

| Ação | Cliente | Mecânico | Gerente |
|------|---------|----------|---------|
| Ver próprios veículos | ✅ | ❌ | ✅ |
| Ver todos os veículos | ❌ | ❌ | ✅ |
| Criar veículo | ✅ | ❌ | ✅ |
| Criar serviço | ✅ | ❌ | ✅ |
| Ver próprios serviços | ✅ | ❌ | ✅ |
| Ver serviços atribuídos | ❌ | ✅ | ✅ |
| Ver todos os serviços | ❌ | ❌ | ✅ |
| Atualizar status serviço | ❌ | ✅ | ✅ |
| Criar orçamento | ❌ | ❌ | ✅ |
| Atribuir mecânico | ❌ | ❌ | ✅ |

## 🔧 Comandos Úteis

```bash
# Logs e debug
docker-compose logs -f app
docker-compose exec app bash

# Parar/limpar
docker-compose down
docker-compose down -v  # Remove volumes

# Lint e formatação
docker-compose exec app flake8 app/
docker-compose exec app black app/

# Recriar ambiente
docker-compose down -v && docker-compose up --build
docker-compose exec app python seed.py
```

## 📚 Documentação Técnica

- **[ARQUITETURA.md](docs/ARQUITETURA.md)** - Padrões de design, camadas e stack
- **[BACKLOG.md](docs/BACKLOG.md)** - User stories e planejamento de sprints
- **[CASOS_DE_USO.md](docs/CASOS_DE_USO.md)** - Casos de uso e matriz RBAC

## 📊 Status do Projeto

### Sprint 1 (PC1) ✅ COMPLETO
- Docker Compose funcional
- Backend Flask completo
- 4 Models SQLAlchemy
- Autenticação JWT + RBAC
- 20+ endpoints REST
- 17 testes unitários
- Documentação completa

### Próximas Entregas
- **Sprint 2 (PC2):** Testes integração, diagrama ER, validações
- **Sprint 3 (PC3):** Frontend Jinja2, testes E2E, deploy

## 🛠️ Stack Técnica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Backend | Flask | 3.0 |
| ORM | SQLAlchemy | 2.0 |
| Database | PostgreSQL | 15 |
| Auth | JWT + bcrypt | - |
| Container | Docker Compose | - |
| Tests | pytest | 7.4 |

---

**Projeto Acadêmico - TPPE**