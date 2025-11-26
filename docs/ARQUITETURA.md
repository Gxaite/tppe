# Arquitetura do Sistema - Oficina Mecânica

## Visão Geral

| Aspecto | Tecnologia |
|---------|------------|
| **Padrão** | Monolito em Camadas (Layered Architecture) |
| **Framework** | Flask 3.0 + Jinja2 |
| **Banco de Dados** | PostgreSQL 15 |
| **ORM** | SQLAlchemy 2.0 |
| **Containerização** | Docker Compose |
| **Autenticação** | JWT + Sessões |

---

## Diagrama de Arquitetura Geral

```mermaid
flowchart TB
    subgraph Cliente["🖥️ Cliente"]
        Browser["Browser/Frontend"]
        API["API Client"]
    end

    subgraph Container["🐳 Docker Compose"]
        subgraph App["Flask Application (Port 5000)"]
            subgraph Presentation["Camada de Apresentação"]
                Views["Views (Jinja2)"]
                Routes["API Routes"]
            end

            subgraph Business["Camada de Negócio"]
                Auth["Autenticação JWT"]
                Decorators["Decorators RBAC"]
                Utils["Utilitários"]
            end

            subgraph Data["Camada de Dados"]
                Models["SQLAlchemy Models"]
            end
        end

        subgraph DB["PostgreSQL 15 (Port 5432)"]
            Tables["Tabelas"]
        end
    end

    Browser -->|HTTP/HTML| Views
    API -->|REST/JSON| Routes
    Views --> Business
    Routes --> Business
    Business --> Data
    Data -->|SQL| DB
```

---

## Arquitetura em Camadas

```mermaid
flowchart TD
    subgraph L1["🎨 Camada de Apresentação"]
        direction LR
        T1["Templates Jinja2"]
        T2["CSS/JS Estático"]
        T3["API REST"]
    end

    subgraph L2["⚙️ Camada de Negócio"]
        direction LR
        B1["Blueprints"]
        B2["Decorators"]
        B3["Validações"]
        B4["JWT Manager"]
    end

    subgraph L3["💾 Camada de Dados"]
        direction LR
        D1["Models SQLAlchemy"]
        D2["Migrations Alembic"]
        D3["Queries"]
    end

    subgraph L4["🗄️ Camada de Persistência"]
        direction LR
        P1["PostgreSQL"]
        P2["Volumes Docker"]
    end

    L1 --> L2
    L2 --> L3
    L3 --> L4
```

---

## Estrutura do Projeto

```mermaid
flowchart LR
    subgraph Root["📁 tppe/"]
        subgraph App["📁 app/"]
            Init["__init__.py<br/>(Factory)"]
            Models["models.py<br/>(SQLAlchemy)"]
            Utils["utils.py<br/>(JWT, Decorators)"]

            subgraph Routes["📁 routes/"]
                Auth["auth.py"]
                Views["views.py"]
                Usuarios["usuarios.py"]
                Veiculos["veiculos.py"]
                Servicos["servicos.py"]
                Dashboard["dashboard.py"]
            end

            subgraph Templates["📁 templates/"]
                Base["base.html"]
                Dashboards["dashboard_*.html"]
                Forms["*_form.html"]
                Lists["*_list.html"]
            end

            subgraph Static["📁 static/"]
                CSS["css/style.css"]
                JS["js/main.js"]
            end
        end

        subgraph Tests["📁 tests/"]
            Conftest["conftest.py"]
            TestAuth["test_auth.py"]
            TestInt["test_integration.py"]
            TestParam["test_parametrized.py"]
        end

        subgraph Docs["📁 docs/"]
            Arquitetura["ARQUITETURA.md"]
            Backlog["BACKLOG.md"]
            CasosUso["CASOS_DE_USO.md"]
            ER["ER_FISICO.md"]
        end

        Docker["docker-compose.yml"]
        Dockerfile["Dockerfile"]
        Reqs["requirements.txt"]
    end
```

---

## Blueprints e Rotas

```mermaid
flowchart LR
    subgraph Blueprints["Flask Blueprints"]
        direction TB
        BP1["views<br/>(Frontend)"]
        BP2["auth<br/>(/auth)"]
        BP3["usuarios<br/>(/api/usuarios)"]
        BP4["veiculos<br/>(/api/veiculos)"]
        BP5["servicos<br/>(/api/servicos)"]
        BP6["dashboard<br/>(/api/dashboard)"]
    end

    subgraph Rotas["Principais Rotas"]
        direction TB
        R1["/ → login"]
        R2["/dashboard"]
        R3["/veiculos/*"]
        R4["/servicos/*"]
        R5["/usuarios/*"]
        R6["/api/* (REST)"]
    end

    BP1 --> R1
    BP1 --> R2
    BP1 --> R3
    BP1 --> R4
    BP1 --> R5
    BP2 --> R6
    BP3 --> R6
    BP4 --> R6
    BP5 --> R6
    BP6 --> R6
```

---

## Fluxo de Autenticação

```mermaid
sequenceDiagram
    actor U as Usuário
    participant F as Frontend
    participant A as Auth Route
    participant J as JWT Manager
    participant S as Session
    participant DB as Database

    U->>F: Acessa /login
    F->>U: Formulário de login
    U->>F: Email + Senha
    F->>A: POST /login
    A->>DB: Busca usuário
    DB->>A: Dados do usuário
    A->>A: Verifica senha (bcrypt)
    alt Senha válida
        A->>J: Gera token JWT
        J->>A: Token
        A->>S: Cria sessão
        A->>F: Redirect /dashboard
        F->>U: Dashboard
    else Senha inválida
        A->>F: Erro 401
        F->>U: Mensagem de erro
    end
```

---

## Fluxo de Requisição API

```mermaid
sequenceDiagram
    participant C as Cliente API
    participant M as Middleware
    participant D as Decorator
    participant R as Route
    participant B as Business
    participant DB as Database

    C->>M: Request + JWT Token
    M->>D: @token_required
    D->>D: Valida JWT
    alt Token válido
        D->>D: @requer_tipo_usuario
        alt Permissão OK
            D->>R: Executa rota
            R->>B: Lógica de negócio
            B->>DB: Query
            DB->>B: Resultado
            B->>R: Dados processados
            R->>C: Response JSON 200
        else Sem permissão
            D->>C: 403 Forbidden
        end
    else Token inválido
        D->>C: 401 Unauthorized
    end
```

---

## Padrões de Design Utilizados

```mermaid
mindmap
  root((Padrões))
    Factory
      create_app()
      Configuração dinâmica
      Testes isolados
    Blueprint
      Modularização
      Separação de responsabilidades
      Prefixos de URL
    Decorator
      @token_required
      @requer_tipo_usuario
      @login_required
    Repository
      SQLAlchemy ORM
      Abstração de dados
      Queries reutilizáveis
    MVC
      Models - SQLAlchemy
      Views - Jinja2
      Controllers - Routes
```

---

## Modelo de Dados Resumido

```mermaid
erDiagram
    USUARIO ||--o{ VEICULO : possui
    USUARIO ||--o{ SERVICO : atende
    VEICULO ||--o{ SERVICO : recebe
    SERVICO ||--o{ ORCAMENTO : tem

    USUARIO {
        int id PK
        string nome
        string email UK
        string senha_hash
        enum tipo
    }

    VEICULO {
        int id PK
        string placa UK
        string modelo
        string marca
        int ano
        int usuario_id FK
    }

    SERVICO {
        int id PK
        text descricao
        enum status
        decimal valor
        int veiculo_id FK
        int mecanico_id FK
    }

    ORCAMENTO {
        int id PK
        text descricao
        decimal valor
        int servico_id FK
    }
```

---

## Containerização Docker

```mermaid
flowchart TB
    subgraph DC["Docker Compose"]
        subgraph AppContainer["🐍 app"]
            Flask["Flask App"]
            Gunicorn["Gunicorn (Prod)"]
        end

        subgraph DBContainer["🐘 db"]
            Postgres["PostgreSQL 15"]
        end

        Volume["📦 postgres_data"]
        Network["🌐 bridge network"]
    end

    AppContainer <-->|5432| DBContainer
    DBContainer --> Volume
    AppContainer <--> Network
    DBContainer <--> Network

    External["🌍 Externo"]
    External -->|5000| AppContainer
```

### docker-compose.yml

```yaml
version: '3.8'
services:
  app:
    build: .
    ports: ["5000:5000"]
    depends_on: [db]
    environment:
      - DATABASE_URL
      - SECRET_KEY

  db:
    image: postgres:15
    volumes: [postgres_data:/var/lib/postgresql/data]
    environment:
      - POSTGRES_DB
      - POSTGRES_USER
      - POSTGRES_PASSWORD
```

---

## Segurança

```mermaid
flowchart LR
    subgraph Auth["🔐 Autenticação"]
        JWT["JWT Tokens<br/>(1h expiry)"]
        BCrypt["Bcrypt Hashing"]
        Session["Flask Sessions"]
    end

    subgraph Authz["🛡️ Autorização"]
        RBAC["RBAC<br/>(cliente/mecanico/gerente)"]
        Decorators["Route Decorators"]
        Ownership["Resource Ownership"]
    end

    subgraph Valid["✅ Validações"]
        Input["Input Sanitization"]
        Unique["Unique Constraints"]
        FK["Foreign Key Checks"]
    end

    Auth --> Authz
    Authz --> Valid
```

---

## Stack Técnica Completa

```mermaid
flowchart TB
    subgraph Backend
        Flask["Flask 3.0"]
        SQLAlchemy["SQLAlchemy 2.0"]
        PyJWT["PyJWT 2.8"]
        BCrypt["bcrypt"]
    end

    subgraph Frontend
        Jinja2["Jinja2 Templates"]
        Bootstrap["Bootstrap 5"]
        CSS["CSS Custom"]
    end

    subgraph Database
        PostgreSQL["PostgreSQL 15"]
        Alembic["Alembic Migrations"]
    end

    subgraph DevOps
        Docker["Docker"]
        Compose["Docker Compose"]
        Pytest["pytest + coverage"]
        Flake8["flake8 + black"]
    end

    Backend --> Database
    Frontend --> Backend
    DevOps --> Backend
    DevOps --> Database
```

---

## Estratégia de Testes

```mermaid
flowchart TD
    subgraph Pirâmide["Pirâmide de Testes"]
        E2E["🔺 E2E (Selenium)<br/>3-5 fluxos"]
        Int["🔷 Integração<br/>API + DB"]
        Unit["🟩 Unitários<br/>99 testes"]
    end

    subgraph Ferramentas
        Pytest["pytest"]
        Coverage["pytest-cov (79%)"]
        Fixtures["conftest.py"]
    end

    Unit --> Int
    Int --> E2E
    Pytest --> Pirâmide
    Coverage --> Pirâmide
    Fixtures --> Pirâmide
```

---

## Deploy

```mermaid
flowchart LR
    subgraph Local["💻 Local"]
        Dev["docker-compose up"]
    end

    subgraph CI["🔄 CI/CD"]
        Tests["pytest"]
        Lint["flake8"]
        Build["docker build"]
    end

    subgraph Prod["☁️ Produção"]
        Heroku["Heroku"]
        Render["Render"]
        Railway["Railway"]
    end

    Local --> CI
    CI --> Prod
```

**Variáveis de Ambiente:**
- `DATABASE_URL` - Conexão PostgreSQL
- `SECRET_KEY` - Chave de sessão Flask
- `JWT_SECRET_KEY` - Chave para tokens JWT
