# Critica Tecnica Senior — Sprint 42 (v4.0)

> Analise feita por Tech Lead Senior
> O plano v4.0 tem problemas estruturais graves que comprometem a execucao

---

## VEREDITO: PLANO v4.0 NAO ESTA PRONTO

O plano v4.0 parece completo superficialmente (263 tasks), mas tem **problemas fundamentais de metodologia** que um desenvolvedor junior nao perceberia.

**Sintomas de plano junior:**
- Tasks sao "criar arquivo X" em vez de "entregar feature Y verificavel"
- Testes sao afterthought (no final de cada wave)
- Observabilidade e reativa (Wave 8)
- Seguranca e add-on (Wave 9)
- Nao ha fase de design/arquitetura
- Nao ha Definition of Done real

---

## PROBLEMAS ESTRUTURAIS IDENTIFICADOS

### PS-01: Tasks sao Features, nao Entregas

**Problema:** O plano lista "S42-BE-001: Criar modulo app/mac/" como task.

**Por que esta errado:** Uma task deveria ser uma entrega COMPLETA, incluindo:
- Codigo
- Testes unitarios
- Testes de integracao
- Documentacao inline
- Code review aprovado
- Metricas/logs configurados

**Impacto:** Developer vai "completar" a task criando o arquivo vazio e marcando como done.

**Correcao Senior:**
```
Task: Implementar MacEngine com evaluate() e costs calculation
Criterios de Aceite:
- [ ] MacEngine.evaluate() implementado
- [ ] 15+ testes unitarios (happy path + edge cases + error paths)
- [ ] Testes de integracao com PolicyLoader
- [ ] Metricas: mac_evaluation_duration_seconds
- [ ] Logs estruturados com correlation_id
- [ ] Docstrings completas
- [ ] Code review aprovado por 2 reviewers
- [ ] Coverage >= 95% para este modulo
```

---

### PS-02: Ausencia de Phase 0 (Architecture & Design)

**Problema:** O plano pula direto para implementacao (W0: Fundacao MAC).

**Por que esta errado:** Antes de escrever codigo, um senior exigiria:
- ADRs (Architecture Decision Records) para decisoes criticas
- Design docs para componentes complexos
- Spike/PoC para validar abordagens arriscadas
- API contracts definidos (OpenAPI) ANTES de implementar
- Data models revisados por equipe
- Threat modeling para security

**Impacto:** Equipe vai implementar, descobrir problemas, refatorar, perder tempo.

**Correcao Senior:**
```
Phase 0: Architecture & Design (PRE-REQUISITO)
- ADR-001: Separacao SimulationStore vs TruthDB
- ADR-002: Estrategia de determinismo (seed + ordering)
- ADR-003: RBAC model para MI exposure
- ADR-004: Batch execution (sync vs async vs jobs)
- SPIKE-001: PoC de replay deterministico
- SPIKE-002: PoC de streaming de batch progress
- CONTRACT-001: OpenAPI spec draft para todos endpoints
- THREAT-001: Threat modeling para MI exposure
```

---

### PS-03: Testes como Afterthought

**Problema:** Testes aparecem no final de cada wave (S42-TST-*).

**Por que esta errado:**
- TDD/BDD exige testes ANTES ou JUNTO com codigo
- Criterios de aceite devem DEFINIR os testes
- Testes separados = testes esquecidos

**Impacto:**
- Testes escritos depois do codigo testam implementacao, nao comportamento
- Coverage artificial (testa o que foi escrito, nao o que deveria existir)
- Bugs escapam porque testes nao cobrem edge cases

**Correcao Senior:**
Cada task de implementacao INCLUI seus testes:
```
Task: MacEngine.evaluate()
Inclui:
- test_evaluate_happy_path
- test_evaluate_policy_not_found
- test_evaluate_signals_expired
- test_evaluate_timeout
- test_evaluate_determinism (100 replays)
- test_evaluate_costs_calculation
- test_evaluate_hard_cap_triggered
- ...
```

---

### PS-04: Observabilidade Reativa

**Problema:** Wave 8 (Observability Advanced) vem DEPOIS da implementacao.

**Por que esta errado:**
- Observabilidade deve ser built-in, nao bolt-on
- Cada feature deve ter suas metricas DEFINIDAS no design
- Alertas devem ser pensados JUNTO com a feature

**Impacto:**
- Sistema vai para producao sem metricas
- Incidentes nao sao detectados
- Debug impossivel

**Correcao Senior:**
```
Cada task de implementacao INCLUI:
- Metricas Prometheus definidas
- Logs estruturados com correlation
- Spans de tracing
- Alertas correspondentes
```

---

### PS-05: Seguranca como Add-on

**Problema:** Wave 9 (Security Hardening) e separada.

**Por que esta errado:**
- Security-by-design exige seguranca desde o inicio
- Threat modeling deve vir ANTES da implementacao
- Cada feature deve ter seus requisitos de seguranca

**Impacto:**
- Vulnerabilidades introduzidas e descobertas tarde
- Refatoracao cara
- Risco real em producao

**Correcao Senior:**
```
Phase 0 inclui:
- THREAT-001: Threat modeling completo
- SEC-REQ-001: Requisitos de seguranca por feature

Cada task inclui:
- Requisitos de seguranca especificos
- Testes de seguranca correspondentes
```

---

### PS-06: Falta de Contract-First Design

**Problema:** APIs sao definidas "conforme implementacao".

**Por que esta errado:**
- Contract-first: define API, depois implementa
- Permite desenvolvimento paralelo (FE + BE)
- Garante estabilidade de contratos
- Consumer-driven contracts

**Impacto:**
- FE espera BE
- Contratos mudam durante implementacao
- Breaking changes nao detectados

**Correcao Senior:**
```
Phase 0 inclui:
- OpenAPI spec COMPLETA para todos endpoints
- JSON Schemas para todos payloads
- Contract tests baseline

Implementacao valida contra spec, nao o contrario.
```

---

### PS-07: Falta de Feature Flags

**Problema:** Tudo e "implementa e deploy".

**Por que esta errado:**
- Gradual rollout reduz risco
- Feature flags permitem kill switch
- A/B testing requer flags
- Canary deployment requer flags

**Impacto:**
- Deploy e tudo-ou-nada
- Rollback e redeploy
- Incidentes afetam todos usuarios

**Correcao Senior:**
```
Cada feature nova requer:
- Feature flag definida
- Gradual rollout plan (1% -> 10% -> 50% -> 100%)
- Kill switch documentado
- Metricas de rollout
```

---

### PS-08: Falta de Chaos Engineering

**Problema:** Testes sao "funciona" ou "erro esperado".

**Por que esta errado:**
- Sistemas falham de formas inesperadas
- Chaos testing descobre modos de falha
- Resilience testing valida recuperacao

**Impacto:**
- Sistema falha em producao de formas nao testadas
- Recovery nao funciona
- Cascading failures

**Correcao Senior:**
```
Chaos Tests:
- CHAOS-001: Database connection lost mid-batch
- CHAOS-002: Policy file corrupted during load
- CHAOS-003: Memory pressure durante batch grande
- CHAOS-004: Network partition entre servicos
- CHAOS-005: Clock skew entre nodes
```

---

### PS-09: Load Testing Arbitrario

**Problema:** "100 req/s" sem justificativa.

**Por que esta errado:**
- Numeros devem vir de capacity planning
- Baseado em uso esperado + margem
- Diferentes tipos de teste (load, stress, soak, spike)

**Impacto:**
- Sistema pode estar over ou under-provisioned
- Performance issues descobertos em producao

**Correcao Senior:**
```
Capacity Planning:
- Usuarios esperados: X
- Requests/usuario/hora: Y
- Peak multiplier: Z
- Target: X * Y * Z req/s com headroom

Load Tests:
- LOAD-001: Sustained load (baseline)
- STRESS-001: 2x baseline (stress)
- SOAK-001: Baseline por 24h (soak)
- SPIKE-001: 10x por 1min (spike)
```

---

### PS-10: Data Governance Ausente

**Problema:** Datasets mencionados sem governanca.

**Por que esta errado:**
- Dados precisam de lineage
- Data quality checks
- Data cataloging
- Retention policies
- GDPR/LGPD compliance

**Impacto:**
- Dados de origem desconhecida
- Qualidade nao verificada
- Compliance issues

**Correcao Senior:**
```
Data Governance:
- DATA-GOV-001: Data catalog para datasets
- DATA-GOV-002: Data quality checks automaticos
- DATA-GOV-003: Lineage tracking
- DATA-GOV-004: Retention policy por tipo
- DATA-GOV-005: PII scanning automatico
```

---

### PS-11: Incident Readiness Superficial

**Problema:** Runbooks sao stubs.

**Por que esta errado:**
- Runbooks devem ser testados (runbook drills)
- Incident response plan completo
- Escalation paths definidos
- Post-mortem templates
- On-call rotation

**Impacto:**
- Incidente acontece, ninguem sabe o que fazer
- Debug por tentativa e erro
- MTTR alto

**Correcao Senior:**
```
Incident Readiness:
- INC-001: Incident response plan
- INC-002: Escalation matrix
- INC-003: On-call rotation setup
- INC-004: Runbook drills (testar runbooks)
- INC-005: Post-mortem templates
- INC-006: Communication templates
```

---

### PS-12: Dependency Management Ausente

**Problema:** Dependencias externas nao mapeadas.

**Por que esta errado:**
- Servicos dependem de outros
- SLAs precisam ser definidos
- Fallback strategies para cada dependencia
- Circuit breakers configurados

**Impacto:**
- Dependencia falha, sistema inteiro falha
- Cascading failures
- Timeout chains

**Correcao Senior:**
```
Dependency Map:
- DEP-001: Policy service (SLA: 99.9%, timeout: 500ms, fallback: cache)
- DEP-002: Signals service (SLA: 99.5%, timeout: 1s, fallback: stale)
- DEP-003: Database (SLA: 99.99%, timeout: 100ms, fallback: none)
- DEP-004: MI service (SLA: 99%, timeout: 2s, fallback: empty)
```

---

### PS-13: Accessibility como Afterthought

**Problema:** A11y e uma task isolada (S42-FE-026).

**Por que esta errado:**
- Accessibility-by-design
- Cada componente deve ser acessivel desde o inicio
- Retrofitting a11y e caro e incompleto

**Impacto:**
- Componentes inacessiveis
- Retrofit caro
- Usuarios excluidos

**Correcao Senior:**
```
Cada componente UI inclui:
- aria-labels definidos
- Keyboard navigation
- Color contrast (WCAG AA)
- Screen reader testing
- Focus management
```

---

### PS-14: Internationalization Ignorada

**Problema:** PT-BR hardcoded.

**Por que esta errado:**
- i18n deve ser considerada desde o inicio
- Strings externalizadas
- Locale-aware formatting

**Impacto:**
- Quando precisar de outro idioma, refatoracao massiva
- Strings espalhadas pelo codigo

**Correcao Senior:**
```
i18n Framework:
- I18N-001: Setup de i18n framework
- I18N-002: Strings externalizadas (mesmo so PT-BR)
- I18N-003: Date/number formatting locale-aware
- I18N-004: RTL consideration (futuro)
```

---

### PS-15: Technical Debt Tracking Ausente

**Problema:** Nao ha registro de shortcuts.

**Por que esta errado:**
- Debt acontece, precisa ser rastreado
- Remediation plan necessario
- Debt compound interest

**Impacto:**
- Debt acumula invisivel
- Sistema fica unmaintainable
- Velocity cai

**Correcao Senior:**
```
Tech Debt Register:
- DEBT-001: [HIGH] Usar cache em vez de recalcular
- DEBT-002: [MED] Refatorar batch runner para async
- DEBT-003: [LOW] Melhorar naming em models
...
Com: Severidade, Remediation plan, Deadline
```

---

## RESUMO DOS PROBLEMAS

| ID | Problema | Severidade | Correcao |
|----|----------|------------|----------|
| PS-01 | Tasks sao features, nao entregas | CRITICO | DoD real por task |
| PS-02 | Sem Phase 0 (Architecture) | CRITICO | Adicionar Phase 0 |
| PS-03 | Testes afterthought | ALTO | Testes em cada task |
| PS-04 | Observabilidade reativa | ALTO | Built-in desde inicio |
| PS-05 | Seguranca add-on | CRITICO | Security-by-design |
| PS-06 | Sem contract-first | ALTO | OpenAPI primeiro |
| PS-07 | Sem feature flags | MEDIO | Gradual rollout |
| PS-08 | Sem chaos testing | ALTO | Chaos engineering |
| PS-09 | Load testing arbitrario | MEDIO | Capacity planning |
| PS-10 | Data governance ausente | ALTO | Data catalog + quality |
| PS-11 | Incident readiness superficial | ALTO | IR plan completo |
| PS-12 | Dependencies nao mapeadas | ALTO | Dependency map + fallbacks |
| PS-13 | A11y afterthought | MEDIO | A11y-by-design |
| PS-14 | i18n ignorada | BAIXO | i18n framework |
| PS-15 | Tech debt nao rastreado | MEDIO | Debt register |

---

## RECOMENDACAO

**O plano v4.0 precisa ser REESTRUTURADO, nao apenas "mais tasks adicionadas".**

Estrutura correta:

```
Phase 0: Architecture & Design (OBRIGATORIA)
  - ADRs
  - Design Docs
  - Spikes/PoCs
  - OpenAPI Contracts
  - Threat Model
  - Data Governance Plan
  - Dependency Map

Phase 1-N: Implementation (por Feature, nao por Layer)
  - Cada feature inclui:
    - Codigo
    - Testes (unit + integration + contract)
    - Observabilidade (metrics + logs + tracing)
    - Seguranca (requirements + tests)
    - Documentacao
    - Feature flag
    - Rollout plan

Phase Final: Hardening
  - Chaos testing
  - Load/stress/soak testing
  - Security audit
  - Incident readiness
  - Runbook drills
```

---

*Critica gerada por Tech Lead Senior*
*15 problemas estruturais identificados*
*Plano v4.0 requer reestruturacao fundamental*
