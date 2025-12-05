# Sprint 33 — Capítulo 4

## Bloco 2 — Plano tático por gate (G0–G5) e sequência de trabalho

Este bloco traduz a filosofia da S33 em um **plano tático por gate**, descendo ao nível de tarefas concretas, entradas, saídas e ordem sugerida de execução. A ideia é que qualquer pessoa da equipe consiga pegar este bloco, abrir o repositório e saber em que ordem atacar o trabalho sem violar o desenho da sprint.

O foco é responder, para cada gate G0–G5:
- o que precisa existir para considerar o gate pronto;
- quais arquivos e módulos são afetados;
- como os scripts em `bin/` e os scorecards em `out/scorecards/` entram no fluxo;
- qual é a sequência natural de dependências entre atividades.

---

### 4.2.1 G0 — Escopo e baseline de operação definidos

**Objetivo de G0:** congelar o recorte operacional da S33 de forma explícita e verificável.

#### Entradas
- Decisão de produto/roadmap sobre o recorte da S33 (quais fontes, pipelines, APIs internas, SLOs serão cobertos).
- Contexto vindo dos capítulos 1 e 2 (problemas a resolver, metas de operação, limites de escopo).

#### Saídas mínimas
- `programa 1/Epico 28/Sprint 33/s33_scope_ops.md` preenchido com:
  - lista de fontes em escopo (IDs, tipo, criticidade);
  - lista de pipelines e APIs em escopo;
  - justificativa rápida de por que esse recorte é relevante para operação.
- `programa 1/Epico 28/Sprint 33/s33_components_map.yaml` contendo:
  - `component_id`, tipo (SOURCE/PIPELINE/API/WORKER/OTHER), criticidade;
  - links de observabilidade padrão (quando existirem);
  - tags úteis (ex.: `programa:1`, `truth-db`, `core-ingestion`).
- Script `bin/s33_g0_scope_and_baseline.sh` implementado.
- Scorecard `out/scorecards/S33_G0_scope_and_baseline.json` gerado com PASS.
- Evidências em `out/evidence/S33_G0_scope_and_baseline/` (logs do script, versão dos arquivos de escopo, snapshots se necessário).

#### Passos táticos
1. Redigir a primeira versão de `s33_scope_ops.md` com base no Capítulo 1.
2. Derivar o `s33_components_map.yaml` a partir do escopo (um objeto por componente monitorado).
3. Implementar `bin/s33_g0_scope_and_baseline.sh` para:
   - validar sintaxe do YAML/Markdown (por exemplo, via `yamllint` e checks simples de heading);
   - garantir unicidade de `component_id`;
   - verificar que todos os componentes citados no scope aparecem no mapa.
4. Rodar o script localmente e corrigir inconsistências.
5. Gerar o primeiro scorecard G0 + evidências.
6. Fazer revisão conjunta Produto + Engenharia + Ops, ajustando o mapa se necessário.

#### Ordem e dependências
- G0 deve ser atacado **logo no início da sprint**; G1–G3 dependem diretamente desse recorte.
- Qualquer mudança relevante em escopo após G0 exigirá:
  - atualização de docs;
  - reexecução do script;
  - novo scorecard G0.

---

### 4.2.2 G1 — Domínio de Incident e operação coerente

**Objetivo de G1:** estabelecer Incident como entidade real, com lifecycle, ligações com componentes e SLOs, e testes robustos.

#### Entradas
- `programa 1/Epico 28/Sprint 33/s33_incidents_lifecycle.md` (estados, transições, regras de negócio de Incident).
- `programa 1/Epico 28/Sprint 33/s33_components_map.yaml` (para vínculos entre incidentes e componentes).

#### Saídas mínimas
- Modelo de Incident implementado em `app/domain/incidents.py` (e/ou camada ORM equivalente).
- Migration correspondente em `migrations/versions/xxxx_s33_incident_model.py`.
- Testes de domínio em `tests/domain/test_incidents_model.py` (ou namespace equivalente).
- Script `bin/s33_g1_incidents_domain.sh` implementado.
- Scorecard `out/scorecards/S33_G1_incidents_domain.json` em PASS.
- Evidências em `out/evidence/S33_G1_incidents_domain/` (logs de testes, dumps de exemplo, prints de lifecycle se útil).

#### Passos táticos
1. Elaborar o lifecycle de Incident no doc (`s33_incidents_lifecycle.md`), incluindo:
   - estados válidos;
   - transições permitidas;
   - regras para timestamps e severidade.
2. Implementar/ajustar o modelo `Incident` com base nesse lifecycle.
3. Implementar regras de transição e validações em funções de domínio (ex.: `transition_incident`).
4. Escrever testes cobrindo:
   - criação em estado inicial;
   - transições válidas e inválidas;
   - coerência de timestamps;
   - ligações com componentes (`component_ids` devem existir em `ops_components`).
5. Implementar `bin/s33_g1_incidents_domain.sh` para rodar esses testes + checks de schema/migration.
6. Rodar localmente, gerar scorecard e evidência.

#### Ordem e dependências
- G1 depende de G0 (precisa de componentes para amarrar Incident).
- G2 e G4 dependem de G1 (cockpit e runbooks usam Incident como entidade central).

---

### 4.2.3 G2 — OracleOps Cockpit v1 navegável e conectado

**Objetivo de G2:** ter um cockpit navegável e funcional, conectado ao domínio e a dados de verdade (ou mocks estruturados).

#### Entradas
- Backend parcial pronto: `ops_components`, `ops_health_summary`, primeiros endpoints em `ops_cockpit_routes.py`.
- Frontend com estrutura básica da feature `oracleops` criada.

#### Saídas mínimas
- Endpoints principais do cockpit implementados (`overview`, `components`, `components/{id}`, `incidents` básicos).
- Páginas `OverviewPage` e `ComponentDetailsPage` consumindo a API.
- Cliente `opsCockpitClient` com métodos mínimos (`fetchOverview`, `fetchComponents`, `fetchComponentDetails`).
- Script `bin/s33_g2_cockpit_sanity.sh` implementado.
- Scorecard `out/scorecards/S33_G2_cockpit_ui.json` em PASS.
- Evidências em `out/evidence/S33_G2_cockpit_ui/` (respostas de API, screenshots do cockpit, logs de sanity).

#### Passos táticos
1. Backend:
   - finalizar o `ops_health_summary` para o recorte da S33;
   - expor `/api/ops/cockpit/overview` e `/api/ops/cockpit/components` com payload consistente.
2. Frontend:
   - implementar `opsCockpitClient` (overview + components);
   - construir `OverviewPage` com componentes por estado + lista de problemáticos;
   - construir `ComponentDetailsPage` com metadados, estado e incidentes básicos.
3. Implementar `bin/s33_g2_cockpit_sanity.sh` para:
   - subir app em modo de teste;
   - chamar endpoints de overview/components;
   - validar que todos os `component_id` do mapa aparecem na API.
4. Rodar o script, ajustar backend/frontend até scorecard PASS.
5. Fazer mini‑sessão de navegação com alguém no papel de operador.

#### Ordem e dependências
- G2 depende de G0 (componentes) e G1 (incidentes, pelo menos em nível de listagem).
- G3 e G4 se apoiam na UI de G2.

---

### 4.2.4 G3 — SLOs e observabilidade aplicada

**Objetivo de G3:** garantir que os SLOs da S33 existam como definições completas, tenham consultas executáveis e, em casos críticos, acionem alertas.

#### Entradas
- Lista de SLOs da S33 em `docs/s33/s33_slos.md`.
- Stack de observabilidade configurada (ou ambiente de teste/mocks definidos).

#### Saídas mínimas
- Módulo `ops_slos` preenchido com representação dos SLOs da S33.
- Serviço `ops_slo_evaluator` capaz de executar queries e retornar estados (OK/VIOLATED/NO_DATA).
- Configurações mínimas de dashboards e alertas versionadas (`observability/dashboards/`, `observability/alerts/`, quando aplicável).
- Integração básica com cockpit (painel `SloSummaryPanel` na overview e/ou detalhe de componente).
- Script `bin/s33_g3_slos_sanity.sh` implementado.
- Scorecard `out/scorecards/S33_G3_slos_and_observability.json` em PASS.
- Evidências em `out/evidence/S33_G3_slos_and_observability/` (resultados das consultas, logs de testes de alerta, prints de dashboards).

#### Passos táticos
1. Refinar `s33_slos.md` com:
   - targets claros;
   - métricas base reais;
   - queries iniciais.
2. Implementar/ajustar `ops_slos` para ler essas definições.
3. Implementar `ops_slo_evaluator` para rodar queries na stack de observabilidade.
4. Configurar 1–3 SLOs críticos com regras de alerta (mesmo que em canal de teste).
5. Integrar estados de SLO no cockpit via `SloSummaryPanel`.
6. Implementar `bin/s33_g3_slos_sanity.sh` para:
   - iterar sobre todos os SLOs da S33;
   - rodar queries;
   - registrar estados em evidência + scorecard.

#### Ordem e dependências
- G3 depende de G0 (componentes) e dos docs de SLO.
- Integração com cockpit (UI) idealmente ocorre em paralelo com G2, mas G3 não pode ser marcado PASS sem consulta real.

---

### 4.2.5 G4 — Runbooks, bundles de evidência e fluxo de aprendizado

**Objetivo de G4:** criar e validar um ciclo completo de resposta a incidentes para o recorte da S33.

#### Entradas
- Recorte de incidentes plausíveis da S33 (derivado do scope e de históricos anteriores).
- Modelo de Incident (G1) e cockpit funcional (G2/G3).

#### Saídas mínimas
- Runbooks escritos em `docs/runbooks/` (prefixo S33_*) para cenários críticos definidos no Cap. 2.
- Integração de `RunbookLinks` no cockpit (detalhe de componente e incidente).
- Pelo menos um incidente real/simulado percorrido com runbook a partir do cockpit.
- Bundle de evidência completo em `out/evidence/S33_G4_incidents/` para esse incidente.
- Script `bin/s33_g4_runbooks_and_evidence.sh` implementado.
- Scorecard `out/scorecards/S33_G4_runbooks_and_evidence.json` em PASS.

#### Passos táticos
1. Escolher 2–3 cenários prioritários (ex.: fonte crítica fora do ar, fila de ingestão saturada, atraso grave em Truth‑DB).
2. Escrever runbooks para esses cenários, com foco em:
   - sinais que disparam o runbook;
   - passos concretos (com comandos, painéis, logs);
   - critérios de sucesso.
3. Fazer o wire‑up dos runbooks na UI (`RunbookLinks`).
4. Simular um incidente típico da S33:
   - forçar a condição (em ambiente de teste);
   - acompanhar pelo cockpit;
   - seguir o runbook até a mitigação.
5. Montar o bundle de evidência (logs, prints, timeline, runbook usado) em `out/evidence/S33_G4_incidents/`.
6. Implementar `bin/s33_g4_runbooks_and_evidence.sh` para checar estrutura de runbooks e bundles.

#### Ordem and dependências
- G4 depende de G1 (Incident), G2 (cockpit) e G3 (idealmente, SLOs em uso).
- A simulação e o bundle de evidência alimentam diretamente o material da ORR (G5).

---

### 4.2.6 G5 — ORR operacional da S33

**Objetivo de G5:** provar, em sessão guiada, que o recorte da S33 é operável por alguém que não escreveu o código.

#### Entradas
- G0–G4 em PASS (ou, no mínimo, em estado estável de quase‑PASS com gaps mapeados).
- Ambiente de teste com a versão da S33 em execução (backend + frontend).

#### Saídas mínimas
- Sessão de ORR operacional executada com:
  - roteiro seguido (inspeção de saúde, exploração de componentes, cenário de incidente, consulta a SLOs);
  - papéis definidos (facilitador, operador, observador);
- Scorecard `out/scorecards/S33_G5_orr_operacional.json` preenchido (PASS/NO_GO + notas).
- Evidências em `out/evidence/S33_G5_orr_operacional/` (roteiro preenchido, prints, feedbacks).

#### Passos táticos
1. Redigir/ajustar o roteiro detalhado de ORR com base no Capítulo 2.
2. Escolher operador convidado e agendar a sessão.
3. Garantir que a versão da S33 (branch/commit) esteja implantada no ambiente de teste.
4. Conduzir a ORR seguindo os passos:
   - visão geral de saúde via OverviewPage;
   - exploração de um componente crítico;
   - detecção e tratamento de um incidente via cockpit + runbook;
   - consulta a SLOs relevantes.
5. Registrar tempos, dificuldades e feedbacks.
6. Preencher scorecard G5 e salvar evidências.
7. Atualizar `s33_incidents_learnings.md` com aprendizados da ORR.

#### Ordem e dependências
- G5 é sempre o último gate.
- Em caso de NO_GO, a S33 pode ser estendida ou complementada com uma mini‑sprint focada na correção dos pontos levantados.

---

### 4.2.7 Visão da sequência de trabalho ao longo da sprint

Resumindo a sequência tática, uma linha do tempo típica da S33 seria:

1. **Dias 1–2**  
   - Fechar G0 (escopo + components_map) e preparar doc de lifecycle de Incident.

2. **Dias 2–4**  
   - Implementar Incident + testes (G1).
   - Começar backend do cockpit (health summary, endpoints básicos).

3. **Dias 4–6**  
   - Fechar G1.
   - Construir OverviewPage e ComponentDetailsPage (G2 parcial).
   - Consolidar definições de SLOs e iniciar `ops_slos`.

4. **Dias 6–8**  
   - Fechar G2 (cockpit navegável conectado).
   - Implementar `ops_slo_evaluator` e integração básica de SLOs na UI (G3 parcial).

5. **Dias 8–10**  
   - Fechar G3 (SLOs avaliados, consulta e alerta mínimo).
   - Escrever runbooks, simular incidente e montar bundle G4.

6. **Dias 10–12**  
   - Fechar G4.
   - Rodar dry‑run interno da ORR com equipe.

7. **Dias 12–14**  
   - Executar ORR operacional oficial (G5); ajustar o que for crítico.
   - Atualizar docs, scorecards e evidências.

Este bloco deve ser usado como **roteiro de execução** para a S33. Qualquer desvio relevante (por exemplo, pular G3 para "ganhar tempo") deve ser tratado como decisão de risco consciente, registrada em doc e, idealmente, revertida o quanto antes.
