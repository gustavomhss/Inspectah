# Inspectah — Sprint 30 — Capítulo 4 — Bloco 1
## Propósito do Capítulo 4 e Fases de Execução da Sprint 30

Este bloco abre o Capítulo 4 deixando cristalino **como** a Sprint 30 vai sair do papel e virar realidade no repositório, no console e na observabilidade.

Capítulos anteriores responderam:
- **Cap. 1:** o que a S30 quer tornar verdade (objetivos, escopo, riscos, cenários‑núcleo).
- **Cap. 2:** como vamos provar que isso é verdade (gates, métricas, DoD, CI/ORR).
- **Cap. 3:** onde tudo isso mora na arquitetura e no filemap (módulos, APIs, UI, scripts, artefatos).

O Capítulo 4 responde à pergunta final:

> “O que exatamente precisamos fazer, em que ordem, para chegar lá com evidência sólida e sprint em GO?”

Bloco 1 foca em:
- desenhar as **fases macro** da execução da S30;
- amarrar cada fase aos artefatos importantes (código, scripts, scorecards, evidências);
- evitar o clássico anti‑padrão “cada dev faz o que quer e a gente vê no fim”.

---

## 4.1 Fases de Execução da Sprint 30

A Sprint 30 é organizada em **5 fases práticas**. Elas não são uma waterfall rígida, mas formam o esqueleto da execução: se alguma fase ficar manca, o resultado final tende a sair torto.

### Fase 0 — Setup de Sprint e Gate G0

**Objetivo:** garantir que a sprint começa com o terreno estável, alinhada ao Épico E28 e sem buracos de especificação.

**O que acontece aqui:**
- Consolidar todos os capítulos da S30 em `docs/sprint_30_cap_*.md` (Cap. 1–4), sem TODO/FIXME.
- Revisar o documento do Épico E28 e validar que o contrato da S30 está bem refletido.
- Implementar o script `bin/s30_g0_scope_and_alignment.sh`, que deve:
  - checar existência dos docs obrigatórios da sprint;
  - varrer TODO/FIXME/TBD em Cap. 1–4;
  - confirmar que há links consistentes para o doc do Épico E28.
- Rodar G0 localmente até ficar verde;
- Integrar G0 no workflow `.github/workflows/s30-gates.yml` e garantir primeira execução verde no CI.

**Saídas concretas da Fase 0:**
- `docs/sprint_30_cap_1_contexto_problemas_objetivos.md` preenchido;
- `docs/sprint_30_cap_2_gates_metricas_dod.md` preenchido;
- `docs/sprint_30_cap_3_arquitetura_filemap.md` preenchido;
- `docs/sprint_30_cap_4_execucao_evidencias.md` (este capítulo) já em rascunho avançado;
- `bin/s30_g0_scope_and_alignment.sh` implementado;
- `out/scorecards/S30_G0_scope_and_alignment.json` com `status = "PASS"`;
- `out/evidence/S30_G0_scope_and_alignment/` com logs/relatórios da checagem inicial.

A sprint só segue para o resto com G0 verde. Se G0 estiver vermelho, significa que estamos tentando construir um prédio em cima de um terreno ainda esburacado.

---

### Fase 1 — Domínio de Fluxos v1.5 (Backend + Migrations)

**Objetivo:** consolidar o modelo de Fluxos v1.5 e deixar o backend pronto para sustentar o fluxo‑pivô de notícias.

**O que acontece aqui:**
- Implementar/ajustar entidades v1.5 em `app/flows/models.py`:
  - `Flow`, `FlowStep`, `FlowExecution`, `FlowStepExecution`, `FlowTemplate`, `FlowOperationLog`;
- Criar a migration principal da sprint: `migrations/versions/0030_s30_flow_model_v15.py`;
- Se necessário, criar migration de seed de templates (por exemplo, `0031_s30_flow_templates_seed.py`);
- Implementar `app/flows/service.py` com operações centrais:
  - `create_flow_from_template`;
  - `set_flow_state` com regras de transição;
  - `replace_agent_for_step`;
  - `route_event_to_flow` para eventos `noticia_texto`;
  - `reprocess_items` com limites e validações;
- Implementar `app/flows/routing_policy.py` com política de roteamento por estado e tipo de entrada;
- Implementar/ajustar `app/flows/execution_engine.py` conectando com a camada de agentes.

**Ligação com gates:**
- Implementar `bin/s30_g1_flow_model_and_templates.sh` para:
  - aplicar migrations em banco vazio e banco pós‑S29;
  - validar templates obrigatórios, especialmente o de notícias;
  - checar topologias (sem loops proibidos, etapas órfãs, ausência de decisão final).

**Saídas concretas da Fase 1:**
- Código de domínio de fluxos v1.5 implementado;
- Migrations de S30 criadas e rodando limpo;
- Scorecard `out/scorecards/S30_G1_flow_model_and_templates.json` em `PASS`;
- Evidências em `out/evidence/S30_G1_flow_model_and_templates/` (logs de migrations, relatório de templates/topologias).

---

### Fase 2 — Console de Fluxos (APIs + Frontend)

**Objetivo:** transformar o fluxo de notícias‑pivô em algo operável pelo console, sem depender de dev futucando banco ou código.

**O que acontece aqui (backend):**
- Implementar `app/api/flow_console_routes.py` com rotas:
  - lista de fluxos;
  - detalhe de fluxo;
  - criação a partir de template;
  - mudança de estado;
  - troca de agente;
  - listagem de execuções;
  - detalhe de execução;
  - reprocessamento limitado.
- Conectar rotas a `app/flows/service.py` (sem lógica de domínio nas rotas);
- Garantir autenticação e autorização corretas.

**O que acontece aqui (frontend):**
- Criar módulo `frontend/inspectah-ui/src/features/flows/` com componentes:
  - `FlowsListPage.tsx`;
  - `FlowDetailPage.tsx`;
  - `FlowExecutionDetailDrawer.tsx`;
  - `FlowCreateFromTemplateDialog.tsx`;
  - `FlowStateBadge.tsx` (+ `FlowOperationsBar.tsx` se adotado);
- Implementar hooks em `features/flows/api.ts` para todas as operações;
- Criar testes em `__tests__/flows_console.spec.tsx` cobrindo fluxos básicos.

**Ligação com gates:**
- Implementar `bin/s30_g2_flow_console_ops.sh`, que deve:
  - rodar lint, testes e build do frontend;
  - exercitar endpoints do console via HTTP com asserts claros;
  - falhar se qualquer parte do console de fluxos estiver quebrada.

**Saídas concretas da Fase 2:**
- Console de Fluxos funcional em ambiente de dev/teste;
- Scorecard `S30_G2_flow_console_ops.json` em `PASS`;
- Evidências em `out/evidence/S30_G2_flow_console_ops/` (logs de front, testes, curls de API).

---

### Fase 3 — Operações Seguras, Observabilidade e E2E

**Objetivo:** garantir que operar fluxos (pausar, retomar, testar, reprocessar) é seguro, observável e verificável de ponta a ponta.

**O que acontece aqui:**
- Endurecer `app/flows/service.py` com limites e validações para operações críticas (especialmente reprocessamento);
- Implementar `FlowOperationLog` e uso consistente em operações administrativas (set_state, reprocess, replace_agent);
- Criar `app/flows/instrumentation.py` com helpers de métricas e logs estruturados;
- Plugar instrumentação na `FlowExecutionEngine` e, se necessário, nos pontos de integração com ingestão;
- Ajustar/definir painel de métricas para fluxo de notícias (baseado em métricas `inspectah_flow_*`);
- Definir dataset de notícias sintéticas e scripts de teste end‑to‑end.

**Ligação com gates:**
- `bin/s30_g3_flow_operations_safety.sh` → prova que operações críticas são seguras;
- `bin/s30_g4_flow_observability.sh` → prova que fluxos são visíveis em métricas/logs;
- `bin/s30_g5_e2e_canonical_flow.sh` → prova que o fluxo‑pivô de notícias funciona de ponta a ponta.

**Saídas concretas da Fase 3:**
- Scorecards `S30_G3_*`, `S30_G4_*`, `S30_G5_*` todos em `PASS`;
- Evidências em `out/evidence/S30_G3_*`, `S30_G4_*`, `S30_G5_*` com logs, métricas, prints do console e dados de teste.

---

### Fase 4 — Métricas Agregadas, Bundle e ORR

**Objetivo:** condensar tudo que a S30 fez em um conjunto único de artefatos auditáveis e tomar uma decisão clara de GO/NO‑GO.

**O que acontece aqui:**
- Implementar `bin/s30_metrics_summary.sh` para ler scorecards de gates + dados auxiliares e gerar `out/scorecards/S30_metrics_summary.json`;
- Implementar `bin/s30_bundle.sh` para montar `out/bundles/inspectah_s30_evidence_bundle.zip` contendo:
  - todos os `out/scorecards/S30_G*.json`;
  - `S30_metrics_summary.json`;
  - todas as pastas `out/evidence/S30_G*`;
  - `out/evidence/S30_ORR_summary.txt` (resumo textual da sprint);
- Ajustar e rodar workflow `.github/workflows/s30-gates.yml` para executar, em sequência:
  - setup do ambiente;
  - G0–G5;
  - métricas agregadas;
  - bundle;
- Rodar o ritual de ORR em cima do bundle e dos scorecards.

**Saídas concretas da Fase 4:**
- `out/scorecards/S30_metrics_summary.json` com `status = "PASS"`;
- `out/bundles/inspectah_s30_evidence_bundle.zip` publicado como artifact de CI;
- `out/evidence/S30_ORR_summary.txt` com resumo da sprint e decisão de GO/NO‑GO documentada;
- Capítulo 4 atualizado com resultados finais da execução.

---

Com essas cinco fases, o Bloco 1 do Capítulo 4 entrega o mapa macro de execução da Sprint 30. Os próximos blocos descem o zoom para:
- detalhar tarefas por eixo (backend, frontend, observabilidade, gates);
- destrinchar cenários de teste por gate;
- descrever o ritual de ORR e o checklist de evidências que define, de forma binária, se a S30 está realmente DONE.

