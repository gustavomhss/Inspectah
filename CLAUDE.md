# Inspectah - Claude Instructions

## Regras Obrigatórias

### 1. Cobertura de Testes: MÍNIMO 97%

**ANTES de finalizar qualquer tarefa:**

```bash
PYTHONPATH=. .venv/bin/python -m pytest --cov=app --cov-report=term-missing
```

Se a cobertura estiver abaixo de 97%, você DEVE criar testes adicionais antes de entregar.

### 2. Verificação Obrigatória

Antes de qualquer commit/merge:
- [ ] Todos os testes passam
- [ ] Cobertura >= 97%
- [ ] Novos testes criados para código novo

---

## Comandos Rápidos

```bash
# Rodar todos os testes
PYTHONPATH=. .venv/bin/python -m pytest

# Verificar cobertura (DEVE ser >= 97%)
PYTHONPATH=. .venv/bin/python -m pytest --cov=app --cov-report=term-missing

# Ver módulos abaixo de 100%
PYTHONPATH=. .venv/bin/python -m pytest --cov=app 2>&1 | grep -v "100%"

# Rodar teste específico
PYTHONPATH=. .venv/bin/python -m pytest tests/module/test_file.py::TestClass::test_method -v
```

---

## Documentação de Testes

- **Padrões**: `docs/testing/TESTING_STANDARDS.md`
- **Checklist PR**: `docs/testing/PR_CHECKLIST.md`
- **Instruções Agentes**: `.claude/AGENT_INSTRUCTIONS.md`

---

## Estrutura de Testes

```
tests/
├── conftest.py              # Fixtures globais
├── agents/                  # Testes de agentes
├── api/                     # Testes de rotas
├── claims/                  # Testes de claims
├── core/                    # Testes core
├── flows/                   # Testes de flows
├── guardian/                # Testes guardian
├── sources/                 # Testes fontes
├── truth/                   # Testes truth/DSL
└── sprint_*/                # Testes específicos
```

---

## Métricas Atuais

| Métrica | Valor |
|---------|-------|
| Cobertura | 97% |
| Testes | 1961 |
| Módulos 100% | 117/187 |

---

## Workflow

1. **Criar código** → Criar testes correspondentes
2. **Verificar cobertura** → Deve ser >= 97%
3. **Rodar todos os testes** → Todos devem passar
4. **Commit/PR** → Incluir output de cobertura
