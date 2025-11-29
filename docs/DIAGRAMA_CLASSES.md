# Diagrama de Classes

Este documento apresenta a estrutura de classes do sistema de gestão de oficina mecânica.

## Diagrama UML

```mermaid
classDiagram
    direction TB

    class TipoUsuario {
        <<enumeration>>
        CLIENTE
        GERENTE
        MECANICO
    }

    class StatusServico {
        <<enumeration>>
        PENDENTE
        AGUARDANDO_ORCAMENTO
        ORCAMENTO_APROVADO
        EM_ANDAMENTO
        CONCLUIDO
        CANCELADO
    }

    class Usuario {
        +int id
        +String nome
        +String email
        -String senha_hash
        +String telefone
        +String endereco
        +TipoUsuario tipo
        +DateTime criado_em
        +set_senha(senha)
        +verificar_senha(senha) bool
        +to_dict() dict
    }

    class Veiculo {
        +int id
        +String placa
        +String modelo
        +String marca
        +int ano
        +String cor
        +int usuario_id
        +DateTime criado_em
    }

    class Servico {
        +int id
        +String descricao
        +String observacoes
        +StatusServico status
        +Decimal valor
        +int veiculo_id
        +int mecanico_id
        +DateTime criado_em
        +DateTime atualizado_em
        +Date data_previsao
        +Date data_conclusao
        +valor_total() Decimal
        +status_display() String
        +status_class() String
    }

    class Orcamento {
        +int id
        +String descricao
        +Decimal valor
        +int servico_id
        +DateTime criado_em
        +valor_total() Decimal
    }

    Usuario "1" --> "*" Veiculo : possui
    Usuario "1" --> "*" Servico : executa
    Veiculo "1" --> "*" Servico : tem
    Servico "1" --> "*" Orcamento : contém
    Usuario ..> TipoUsuario : usa
    Servico ..> StatusServico : usa
```

## Descrição das Classes

| Classe | Descrição |
|--------|-----------|
| **Usuario** | Representa clientes, gerentes e mecânicos do sistema. Possui métodos para gerenciar senha e converter dados |
| **Veiculo** | Armazena informações dos veículos cadastrados. Cada veículo pertence a um usuário |
| **Servico** | Registro de serviços realizados na oficina. Vincula veículo e mecânico responsável |
| **Orcamento** | Itens do orçamento de um serviço. Pode haver vários itens por serviço |

## Enumerações

| Enum | Valores | Uso |
|------|---------|-----|
| **TipoUsuario** | CLIENTE, GERENTE, MECANICO | Define o perfil de acesso do usuário |
| **StatusServico** | PENDENTE, AGUARDANDO_ORCAMENTO, ORCAMENTO_APROVADO, EM_ANDAMENTO, CONCLUIDO, CANCELADO | Ciclo de vida de um serviço |

## Relacionamentos

| Origem | Destino | Cardinalidade | Descrição |
|--------|---------|---------------|-----------|
| Usuario | Veiculo | 1 : N | Um cliente pode ter vários veículos |
| Usuario | Servico | 1 : N | Um mecânico pode executar vários serviços |
| Veiculo | Servico | 1 : N | Um veículo pode ter vários serviços |
| Servico | Orcamento | 1 : N | Um serviço pode ter vários itens de orçamento |
