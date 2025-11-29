# Casos de Uso - Sistema Oficina Mecânica

## Atores

| Ator | Descrição |
|------|-----------|
| **Cliente** | Cadastra veículos, solicita serviços, aprova orçamentos |
| **Mecânico** | Executa serviços, cria orçamentos, atualiza status |
| **Gerente** | Gerencia usuários, atribui mecânicos, controla operações |

## Diagrama de Casos de Uso

```mermaid
flowchart TB
    subgraph CLIENTE["Cliente"]
        C1[Cadastrar Veiculo]
        C2[Solicitar Servico]
        C3[Aprovar Orcamento]
        C4[Acompanhar Status]
    end

    subgraph MECANICO["Mecanico"]
        M1[Criar Orcamento]
        M2[Executar Servico]
        M3[Concluir Servico]
    end

    subgraph GERENTE["Gerente"]
        G1[Gerenciar Usuarios]
        G2[Atribuir Mecanico]
        G3[Visualizar Relatorios]
    end

    C1 --> C2
    C2 --> M1
    M1 --> C3
    C3 --> G2
    G2 --> M2
    M2 --> M3
    M3 --> C4
```

## Permissões (RBAC)

| Recurso | Cliente | Mecânico | Gerente |
|---------|:-------:|:--------:|:-------:|
| Veículos | CRUD | R | CRUD |
| Serviços | CR | RU | CRUD |
| Orçamentos | R | CRU | CRUD |
| Usuários | - | - | CRUD |

**Legenda:** C=Create, R=Read, U=Update, D=Delete

## Fluxo Principal

1. **Cliente** cadastra veículo → solicita serviço
2. **Mecânico** cria orçamento → aguarda aprovação
3. **Cliente** aprova orçamento
4. **Gerente** atribui mecânico
5. **Mecânico** executa → conclui serviço
6. **Cliente** acompanha resultado
