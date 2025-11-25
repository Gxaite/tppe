# Casos de Uso

## Atores

- **Cliente:** Proprietário de veículos
- **Mecânico:** Executa serviços
- **Gerente:** Administra sistema

## Casos de Uso Principais

### Cliente
1. UC001 - Registrar/Login
2. UC002 - CRUD Veículos
3. UC003 - Solicitar Serviço
4. UC004 - Visualizar Serviços
5. UC005 - Dashboard Cliente

### Mecânico
1. UC001 - Login
2. UC006 - Ver Serviços Atribuídos
3. UC007 - Atualizar Status
4. UC008 - Dashboard Mecânico

### Gerente
1. UC001 - Login
2. UC009 - Gerenciar Usuários
3. UC010 - Gerenciar Veículos/Serviços
4. UC011 - Criar Orçamentos
5. UC012 - Atribuir Mecânicos
6. UC013 - Dashboard Gerencial

```
┌─────────────────────────────────────────────────────────────┐
│                         GERENTE                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          │
                          ▼
                    ┌──────────┐
                    │  Login   │
                    └──────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Gerenciar     │  │Gerenciar     │  │Gerenciar     │
│Usuários      │  │Veículos      │  │Serviços      │
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Criar/Editar/ │  │Ver Todos os  │  │Criar         │
│Deletar       │  │Veículos      │  │Orçamentos    │
│Funcionários  │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │Atribuir      │
                                    │Mecânico      │
                                    └──────────────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │Ver Dashboard │
                                    │Gerencial     │
                                    └──────────────┘
```

**Casos de Uso:**
1. UC002 - Fazer Login
2. UC015 - Listar Todos os Usuários
3. UC016 - Criar Funcionário
4. UC017 - Editar Usuário
5. UC018 - Deletar Usuário
6. UC019 - Ver Todos os Veículos
7. UC020 - Ver Todos os Serviços
8. UC021 - Criar Orçamento
9. UC022 - Atribuir Mecânico ao Serviço
10. UC023 - Ver Dashboard Gerencial

---

## Especificações Principais

### UC003 - Solicitar Serviço
**Ator:** Cliente  
**Pré-condição:** Autenticado, possui veículo  
**Fluxo:**
1. Cliente seleciona veículo e descreve problema
2. Sistema cria serviço (status: pendente)
3. Gerente recebe notificação

### UC007 - Atualizar Status
**Ator:** Mecânico  
**Pré-condição:** Serviço atribuído  
**Fluxo:**
1. Mecânico altera status (pendente → em andamento → concluído)
2. Sistema atualiza registro
3. Cliente visualiza atualização

### UC011 - Criar Orçamento
**Ator:** Gerente  
**Pré-condição:** Serviço existe  
**Fluxo:**
1. Gerente preenche descrição e valor
2. Sistema vincula ao serviço
3. Cliente recebe orçamento

### UC012 - Atribuir Mecânico
**Ator:** Gerente  
**Pré-condição:** Serviço pendente, mecânico disponível  
**Fluxo:**
1. Gerente seleciona mecânico
2. Sistema atualiza serviço (status: em andamento)
3. Mecânico recebe notificação

---

## Matriz RBAC

| Caso de Uso | Cliente | Mecânico | Gerente |
|-------------|---------|----------|---------|
| CRUD Veículos | Próprios | ❌ | Todos |
| Solicitar Serviço | ✅ | ❌ | ✅ |
| Ver Serviços | Próprios | Atribuídos | Todos |
| Atualizar Status | ❌ | ✅ | ✅ |
| Criar Orçamento | ❌ | ❌ | ✅ |
| Atribuir Mecânico | ❌ | ❌ | ✅ |
| Gerenciar Usuários | ❌ | ❌ | ✅ |

## Workflow de Serviço

```
Cliente cadastra veículo
  ↓
Cliente solicita serviço (Pendente)
  ↓
Gerente cria orçamento
  ↓
Gerente atribui mecânico (Em Andamento)
  ↓
Mecânico executa trabalho
  ↓
Mecânico finaliza (Concluído)
  ↓
Cliente visualiza conclusão
```
