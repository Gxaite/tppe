# Product Backlog

## Épicos

1. Autenticação e Autorização
2. Gerenciamento de Usuários
3. Gerenciamento de Veículos
4. Gerenciamento de Serviços
5. Dashboard e Relatórios
6. Frontend Web

---

## Sprint 1 (PC1) ✅ COMPLETO

### US001 - Autenticação
**Como** usuário **quero** registrar/fazer login **para** acessar o sistema

**Implementado:**
- [x] Registro com nome, email, senha, tipo
- [x] Login com JWT (1h expiração)
- [x] Senha bcrypt
- [x] Email único

### US002 - CRUD Usuários
**Como** gerente **quero** gerenciar usuários **para** controlar acessos

**Implementado:**
- [x] Listar (filtro por tipo)
- [x] Visualizar, criar, atualizar, deletar
- [x] Permissões por role

### US003 - CRUD Veículos
**Como** cliente **quero** gerenciar veículos **para** solicitar serviços

**Implementado:**
- [x] CRUD completo (placa, modelo, marca, ano)
- [x] Placa única
- [x] Cliente vê só seus veículos, gerente vê todos

### US004 - CRUD Serviços
**Como** cliente **quero** solicitar serviços **para** consertar veículo

**Implementado:**
- [x] Criar solicitação (status: pendente)
- [x] Listar por permissão (cliente/mecânico/gerente)
- [x] Atualizar status
- [x] Gerente atribui mecânico e cria orçamentos

### US005 - Dashboards
**Como** usuário **quero** dashboard personalizado **para** acompanhar dados

**Implementado:**
- [x] Dashboard gerente (estatísticas gerais)
- [x] Dashboard mecânico (serviços atribuídos)
- [x] Dashboard cliente (veículos + serviços)

---

## Sprint 2 (PC2) 📋 PLANEJADO

### US006 - Testes de Integração
- [ ] Cobertura >80%
- [ ] Testes de fluxo completo
- [ ] CI/CD básico

### US007 - Validações Avançadas
- [ ] Validação de dados robusta
- [ ] Tratamento de erros
- [ ] Mensagens claras

### US008 - Diagrama ER
- [ ] Modelo físico do banco
- [ ] Documentação de relacionamentos

### US009 - Melhorias UX
- [ ] Notificações básicas
- [ ] Logs estruturados
- [ ] Paginação

---

## Sprint 3 (PC3) 🔮 FUTURO

### US010 - Frontend Web (Jinja2)
- [ ] Templates para cliente, mecânico, gerente
- [ ] Forms para CRUD
- [ ] Design responsivo básico

### US011 - Testes E2E
- [ ] Selenium (3-5 fluxos principais)
- [ ] Testes de integração completos
- [ ] Cobertura >80%

### US012 - Deploy
- [ ] Render/Railway/Fly.io
- [ ] Banco produção
- [ ] HTTPS
- [ ] Monitoramento básico

---

## Backlog Futuro

- Notificações (email/push)
- Agendamento de serviços
- Relatórios financeiros
- Histórico de manutenção
- Integração pagamento
- App mobile

---

## Resumo

**Sprint 1:** 5 US ✅ (Auth, CRUD completo, Dashboards)  
**Sprint 2:** 4 US 📋 (Testes, validações, ER)  
**Sprint 3:** 3 US 🔮 (Frontend, E2E, deploy)
