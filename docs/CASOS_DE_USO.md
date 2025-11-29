# Casos de Uso - Sistema Oficina Mecânica

## Atores

| Ator | Descrição |
|------|-----------|
| **Cliente** | Cadastra veículos, solicita serviços, aprova orçamentos |
| **Mecânico** | Executa serviços, cria orçamentos, atualiza status |
| **Gerente** | Gerencia usuários, atribui mecânicos, controla operações |

## Diagrama de Casos de Uso

```mermaid
flowchart LR
    subgraph Atores
        C((Cliente))
        M((Mecanico))
        G((Gerente))
    end

    subgraph Sistema["Sistema Oficina Mecanica"]
        AUTH["Autenticacao"]
        VEIC["Gerenciar Veiculos"]
        SERV["Gerenciar Servicos"]
        ORCA["Gerenciar Orcamentos"]
        USER["Gerenciar Usuarios"]
        DASH["Visualizar Dashboard"]
    end

    C --> AUTH
    C --> VEIC
    C --> SERV
    C --> ORCA
    C --> DASH

    M --> AUTH
    M --> SERV
    M --> ORCA
    M --> DASH

    G --> AUTH
    G --> VEIC
    G --> SERV
    G --> ORCA
    G --> USER
    G --> DASH
```

## Permissões por Ator (RBAC)

| Recurso | Cliente | Mecânico | Gerente |
|---------|:-------:|:--------:|:-------:|
| Veículos próprios | CRUD | R | CRUD |
| Serviços próprios | CR | RU | CRUD |
| Orçamentos | R | CRU | CRUD |
| Usuários | - | - | CRUD |
| Dashboard | Próprio | Próprio | Completo |

**Legenda:** C=Create, R=Read, U=Update, D=Delete

## Fluxo Principal do Sistema

1. **Cliente** cadastra veículo e solicita serviço
2. **Mecânico** cria orçamento para o serviço
3. **Cliente** aprova ou rejeita orçamento
4. **Gerente** atribui mecânico ao serviço aprovado
5. **Mecânico** executa e conclui o serviço
6. **Cliente** visualiza resultado no dashboard
