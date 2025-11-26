# Diagrama de Casos de Uso - Sistema Oficina Mecânica

## Visão Geral

Sistema de gerenciamento de oficina mecânica com três tipos de atores principais.

---

## Atores do Sistema

| Ator | Descrição | Responsabilidades |
|------|-----------|-------------------|
| **Cliente** | Proprietário de veículos | Cadastrar veículos, solicitar serviços, acompanhar status |
| **Mecânico** | Profissional técnico | Executar serviços, atualizar status, criar orçamentos |
| **Gerente** | Administrador | Gerenciar usuários, atribuir serviços, controlar operações |

---

## Diagrama de Casos de Uso

```mermaid
flowchart TB
    subgraph Atores
        C((Cliente))
        M((Mecânico))
        G((Gerente))
    end

    subgraph Sistema["Sistema Oficina Mecânica"]
        subgraph Auth["Autenticação"]
            UC01[UC01: Fazer Login]
            UC02[UC02: Registrar-se]
            UC03[UC03: Fazer Logout]
        end

        subgraph Veiculos["Gestão de Veículos"]
            UC04[UC04: Cadastrar Veículo]
            UC05[UC05: Listar Veículos]
            UC06[UC06: Editar Veículo]
            UC07[UC07: Excluir Veículo]
        end

        subgraph Servicos["Gestão de Serviços"]
            UC08[UC08: Solicitar Serviço]
            UC09[UC09: Listar Serviços]
            UC10[UC10: Ver Detalhes Serviço]
            UC11[UC11: Atualizar Status]
            UC12[UC12: Atribuir Mecânico]
        end

        subgraph Orcamentos["Gestão de Orçamentos"]
            UC13[UC13: Criar Orçamento]
            UC14[UC14: Visualizar Orçamento]
            UC15[UC15: Aprovar Orçamento]
        end

        subgraph Usuarios["Gestão de Usuários"]
            UC16[UC16: Listar Usuários]
            UC17[UC17: Criar Usuário]
            UC18[UC18: Editar Usuário]
            UC19[UC19: Excluir Usuário]
        end

        subgraph Dashboard["Dashboards"]
            UC20[UC20: Ver Dashboard Cliente]
            UC21[UC21: Ver Dashboard Mecânico]
            UC22[UC22: Ver Dashboard Gerente]
        end
    end

    %% Cliente
    C --> UC01
    C --> UC02
    C --> UC03
    C --> UC04
    C --> UC05
    C --> UC06
    C --> UC07
    C --> UC08
    C --> UC09
    C --> UC10
    C --> UC14
    C --> UC20

    %% Mecânico
    M --> UC01
    M --> UC03
    M --> UC09
    M --> UC10
    M --> UC11
    M --> UC13
    M --> UC14
    M --> UC21

    %% Gerente
    G --> UC01
    G --> UC03
    G --> UC05
    G --> UC09
    G --> UC10
    G --> UC11
    G --> UC12
    G --> UC13
    G --> UC14
    G --> UC15
    G --> UC16
    G --> UC17
    G --> UC18
    G --> UC19
    G --> UC22
```

---

## Especificações de Casos de Uso

### UC01 - Fazer Login

| Campo | Descrição |
|-------|-----------|
| **Ator** | Cliente, Mecânico, Gerente |
| **Pré-condição** | Usuário cadastrado no sistema |
| **Pós-condição** | Usuário autenticado com sessão ativa |

**Fluxo Principal:**
```mermaid
sequenceDiagram
    actor U as Usuário
    participant S as Sistema
    participant DB as Banco de Dados

    U->>S: Acessa página de login
    S->>U: Exibe formulário
    U->>S: Informa email e senha
    S->>DB: Valida credenciais
    DB->>S: Retorna dados do usuário
    S->>S: Gera token JWT
    S->>U: Redireciona para dashboard
```

**Fluxo Alternativo:**
- **FA01**: Credenciais inválidas → Exibe mensagem de erro

---

### UC04 - Cadastrar Veículo

| Campo | Descrição |
|-------|-----------|
| **Ator** | Cliente |
| **Pré-condição** | Usuário autenticado como cliente |
| **Pós-condição** | Veículo registrado no sistema |

**Fluxo Principal:**
```mermaid
sequenceDiagram
    actor C as Cliente
    participant S as Sistema
    participant DB as Banco de Dados

    C->>S: Acessa formulário de veículo
    S->>C: Exibe formulário
    C->>S: Preenche dados (placa, modelo, marca, ano)
    S->>S: Valida dados
    S->>DB: Verifica se placa existe
    alt Placa não existe
        S->>DB: Salva veículo
        S->>C: Exibe confirmação
    else Placa já cadastrada
        S->>C: Exibe erro de duplicidade
    end
```

---

### UC08 - Solicitar Serviço

| Campo | Descrição |
|-------|-----------|
| **Ator** | Cliente |
| **Pré-condição** | Cliente possui veículo cadastrado |
| **Pós-condição** | Serviço criado com status "aguardando_orcamento" |

**Fluxo Principal:**
```mermaid
sequenceDiagram
    actor C as Cliente
    participant S as Sistema
    participant DB as Banco de Dados

    C->>S: Acessa formulário de solicitação
    S->>DB: Busca veículos do cliente
    DB->>S: Retorna lista de veículos
    S->>C: Exibe formulário com veículos
    C->>S: Seleciona veículo e descreve problema
    S->>DB: Cria serviço (status: aguardando_orcamento)
    S->>C: Confirma solicitação
```

---

### UC11 - Atualizar Status do Serviço

| Campo | Descrição |
|-------|-----------|
| **Ator** | Mecânico, Gerente |
| **Pré-condição** | Serviço existe e está atribuído |
| **Pós-condição** | Status do serviço atualizado |

**Fluxo de Estados:**
```mermaid
stateDiagram-v2
    [*] --> Pendente: Serviço criado
    Pendente --> AguardandoOrcamento: Cliente solicita
    AguardandoOrcamento --> OrcamentoAprovado: Gerente aprova
    OrcamentoAprovado --> EmAndamento: Mecânico inicia
    EmAndamento --> Concluido: Mecânico finaliza
    Pendente --> Cancelado: Cliente cancela
    AguardandoOrcamento --> Cancelado: Cliente cancela
    Concluido --> [*]
    Cancelado --> [*]
```

---

### UC12 - Atribuir Mecânico

| Campo | Descrição |
|-------|-----------|
| **Ator** | Gerente |
| **Pré-condição** | Serviço pendente, mecânico disponível |
| **Pós-condição** | Mecânico atribuído ao serviço |

**Fluxo Principal:**
```mermaid
sequenceDiagram
    actor G as Gerente
    participant S as Sistema
    participant DB as Banco de Dados

    G->>S: Acessa detalhes do serviço
    S->>DB: Busca mecânicos disponíveis
    DB->>S: Lista de mecânicos
    S->>G: Exibe opções de mecânicos
    G->>S: Seleciona mecânico
    S->>DB: Atualiza serviço com mecânico_id
    S->>G: Confirma atribuição
```

---

## Matriz de Permissões (RBAC)

```mermaid
flowchart LR
    subgraph Permissões
        direction TB
        R[Visualizar]
        W[Criar/Editar]
        D[Deletar]
        A[Administrar]
    end

    subgraph Cliente
        CV[Veículos Próprios: R,W,D]
        CS[Serviços Próprios: R,W]
        CO[Orçamentos: R]
    end

    subgraph Mecânico
        MV[Veículos: R]
        MS[Serviços Atribuídos: R,W]
        MO[Orçamentos: R,W]
    end

    subgraph Gerente
        GV[Veículos: R,W,D]
        GS[Serviços: R,W,D,A]
        GO[Orçamentos: R,W,D]
        GU[Usuários: R,W,D,A]
    end
```

| Recurso | Cliente | Mecânico | Gerente |
|---------|:-------:|:--------:|:-------:|
| Veículos (próprios) | CRUD | R | CRUD |
| Veículos (todos) | - | R | CRUD |
| Serviços (próprios) | CR | - | - |
| Serviços (atribuídos) | - | RU | - |
| Serviços (todos) | - | - | CRUD |
| Orçamentos | R | CRU | CRUD |
| Usuários | - | - | CRUD |
| Dashboard | Próprio | Próprio | Completo |

**Legenda:** C=Create, R=Read, U=Update, D=Delete

---

## Workflow Completo do Serviço

```mermaid
flowchart TD
    A[Cliente cadastra veículo] --> B[Cliente solicita serviço]
    B --> C{Status: Aguardando Orçamento}
    C --> D[Gerente/Mecânico cria orçamento]
    D --> E{Cliente aprova?}
    E -->|Sim| F[Gerente atribui mecânico]
    E -->|Não| G[Serviço cancelado]
    F --> H{Status: Em Andamento}
    H --> I[Mecânico executa trabalho]
    I --> J[Mecânico registra conclusão]
    J --> K{Status: Concluído}
    K --> L[Cliente visualiza resultado]
    G --> M((Fim))
    L --> M
```
