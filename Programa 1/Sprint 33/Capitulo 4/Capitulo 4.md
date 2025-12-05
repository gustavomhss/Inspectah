# Sprint 33 — Capítulo 4

## Execução, evidências e plano operacional da Sprint 33

Este capítulo traduz a especificação da Sprint 33 em um plano de execução concreto: quem faz o quê, em que ordem, com quais artefatos de entrada e saída, e como as evidências serão coletadas para sustentar os gates e a ORR operacional.

A regra aqui é simples: **se não está refletido em código, scripts, scorecards e evidências, a S33 não aconteceu**. O Capítulo 4 é o manual de como fazer a S33 acontecer de forma reprodutível, tanto localmente quanto no CI.

---

## 4.1 Estratégia de execução da S33

A S33 é uma sprint de **camada de operação**. Para não se perder em refactors infinitos, a execução segue alguns princípios operacionais:

1. **Ordem orientada a gates**  
   A execução é guiada pela sequência lógica dos gates G0 → G1 → G2 → G3 → G4 → G5. Isso não significa que o código será escrito estritamente em série, mas que **ninguém “fecha” uma etapa sem ter condições de passar o gate correspondente**.

2. **Backend antes de cosmética de UI**  
   Primeiro se consolida domínio, serviços e API (Capítulo 3, Bloco 2). Só depois o cockpit é preenchido com dados reais. Protótipos de UI podem existir, mas não contam como entrega até estarem conectados ao backend OracleOps.

3. **Uso intenso de scripts de gates**  
   Sempre que possível, o time codifica as verificações de cada gate como scripts em `bin/`, de forma que **rodar a S33 localmente seja tão simples quanto disparar um ou dois comandos**.

4. **Evidência desde o início**  
   Em vez de deixar captura de logs, prints e bundles para o fim, o time coleta evidências ao longo da execução: cada gate rodado gera artefatos em `out/evidence/` desde a primeira passagem.

5. **Ciclos curtos backend ↔ frontend ↔ operação**  
   A S33 não é puramente técnica; ela se mede por usabilidade operacional. Por isso, são previstos ciclos curtos com alguém no papel de operador testando o cockpit e os runbooks à medida que surgem.

---

## 4.2 Plano tático por gate (G0–G5)

### 4.2.1 G0 — Escopo e baseline de operação definidos

Passos principais:
- Consolidar **proposta** de `programa 1/Epico 28/Sprint 33/s33_scope_ops.md` com o recorte de fontes, pipelines, APIs e SLOs.
- Preencher **proposta** de `programa 1/Epico 28/Sprint 33/s33_components_map.yaml` com os componentes monitorados e seus metadados.
- Implementar o script `bin/s33_g0_scope_and_baseline.sh` para:
  - validar formato e consistência desses anexos (se versionados);
  - gerar `out/scorecards/S33_G0_scope_and_baseline.json`;
  - armazenar evidências em `out/evidence/S33_G0_scope_and_baseline/`.

Critério de avanço:
- script G0 roda limpo localmente;
- scorecard marca PASS;
- Ops + Engenharia assinam o recorte (via registro simples em doc ou comentário em PR).

### 4.2.2 G1 — Modelo de Incident e domínio de operação coerente

Passos principais:
- Implementar/ajustar o domínio de Incident (modelo, lifecycle, invariantes) em `app/ops/incidents.py` (proposta) e migration associada.
- Escrever testes de domínio em `tests/ops/test_incidents_model.py` (ou equivalente), cobrindo criação, transições, timestamps, vínculos com componentes/SLOs.
- Implementar o script `bin/s33_g1_incidents_domain.sh` que:
  - roda os testes de domínio;
  - extrai resultados relevantes;
  - gera `out/scorecards/S33_G1_incidents_domain.json` e evidências em `out/evidence/S33_G1_incidents_domain/`.

Critério de avanço:
- todos os testes de domínio passam localmente e no CI;
- scorecard G1 em PASS;
- Ops revisa uma amostra de incidentes de teste e confirma que a modelagem faz sentido para o recorte.

### 4.2.3 G2 — OracleOps Cockpit v1 navegável e conectado

Passos principais:
- Backend (proposta):
  - finalizar `app/ops/components.py`, `app/ops/health_summary.py`, `app/ops/slo_evaluator.py` (pelo menos na parte mínima para overview);
  - expor os endpoints base em `app/api/ops_cockpit_routes.py` e schemas em `app/schemas/ops_cockpit.py`.
- Frontend (proposta):
  - implementar `OverviewPage`, `ComponentHealthTable`, cliente `opsCockpitClient` com `fetchOverview` e `fetchComponents` em `frontend/inspectah-ui/src/features/oracleops/`;
  - integrar rotas do cockpit no roteador principal.
- Script `bin/s33_g2_cockpit_sanity.sh` para:
  - subir o backend em modo de teste (local ou em container leve);
  - chamar os endpoints principais e validar payloads e consistência com o `components_map`;
  - gerar `out/scorecards/S33_G2_cockpit_ui.json` e evidências em `out/evidence/S33_G2_cockpit_ui/`.

Critério de avanço:
- overview e lista de componentes funcionam de ponta a ponta, com dados minimamente realistas;
- uma pessoa de fora da implementação consegue navegar o cockpit básico sem erros graves.

### 4.2.4 G3 — SLOs e observabilidade aplicada

Passos principais:
- Consolidar **proposta** de `programa 1/Epico 28/Sprint 33/s33_slos.md` com SLOs da sprint (definições coerentes com o recorte de G0).
- Implementar/ajustar `ops/slos.py` + `ops/slo_evaluator.py` para ler essas definições e executar consultas na stack de observabilidade (ou mocks estruturados em ambiente de dev).
- Configurar dashboards básicos e regras de alerta em `observability/dashboards/` e `observability/alerts/` (quando versionadas em arquivo).
- Implementar `bin/s33_g3_slos_sanity.sh` para:
  - avaliar todos os SLOs da S33;
  - registrar estado atual e possíveis falhas;
  - gerar `out/scorecards/S33_G3_slos_and_observability.json` e evidências em `out/evidence/S33_G3_slos_and_observability/`.

Critério de avanço:
- todas as consultas de SLO rodam sem erro;
- pelo menos um SLO crítico tem alerta testado (mesmo que em canal de teste);
- SLOs relevantes aparecem no cockpit (SloSummaryPanel) com estados coerentes.

### 4.2.5 G4 — Runbooks, bundles e fluxo de aprendizado

Passos principais:
- Redigir runbooks da S33 em `docs/runbooks/` (proposta de prefixo `S33_*.md`), seguindo estrutura padrão (contexto, sinais, diagnóstico, mitigação, critérios de sucesso).
- Integrar runbooks à UI via `RunbookLinks` em ComponentDetails e IncidentDetails.
- Simular pelo menos um incidente relevante, seguindo runbook a partir do cockpit, e registrar evidência em `out/evidence/S33_G4_incidents/`.
- Implementar `bin/s33_g4_runbooks_and_evidence.sh` para:
  - checar presença e estrutura de runbooks;
  - validar bundles de evidência mínimos;
  - gerar `out/scorecards/S33_G4_runbooks_and_evidence.json`.

Critério de avanço:
- runbooks escritos e versionados;
- bundle de evidência completo para pelo menos um incidente;
- script G4 em PASS.

### 4.2.6 G5 — ORR operacional da S33

Passos principais:
- Definir o roteiro de ORR com base no Capítulo 2 (perguntas, passos, papéis);
- Agendar sessão de ORR com operador convidado e facilitador;
- Executar a ORR com o estado mais recente do sistema (branch da sprint, migrations aplicadas, cockpit funcional);
- Registrar evidências (roteiro preenchido, tempos, prints, notas) em `out/evidence/S33_G5_orr_operacional/`;
- Preencher `out/scorecards/S33_G5_orr_operacional.json` com resultado (PASS/NO_GO) e observações.

Critério de avanço:
- ORR executada e registrada;
- operador convidado consegue operar o recorte sem depender totalmente de autores;
- feedbacks relevantes registrados em `s33_incidents_learnings.md` e backlog.

---

## 4.3 Fluxo de Git, branches, PRs e CI

Para manter coerência com o restante do projeto, a S33 segue o fluxo padrão de Git/CI com algumas ênfases específicas:

1. **Branch da sprint**  
   Criar uma branch dedicada para a S33, por exemplo:
   - `feature/s33_oracleops_v1`

2. **Branches temáticas curtas**  
   Dentro da branch principal da sprint, criar branches menores para tópicos específicos, por exemplo:
   - `feature/s33_backend_incidents`
   - `feature/s33_backend_ops_components`
   - `feature/s33_frontend_cockpit_overview`
   - `feature/s33_slos_and_observability`

3. **Pull Requests pequenos e revisados**  
   Cada PR deve:
   - referenciar a parte da especificação que está implementando (por exemplo, "S33 Cap. 3 Bloco 2 — backend OracleOps");
   - incluir evidências mínimas em forma de logs de testes, prints do cockpit ou links para artifacts do CI;
   - ser revisado por pelo menos uma pessoa que não implementou aquele trecho.

4. **Integração com CI**  
   O CI deve incluir um workflow específico (por exemplo, `.github/workflows/s33-gates.yml`) que:
   - aplique migrations;
   - rode testes relevantes para S33 (domínio de Incident, serviços de operação, cockpit);
   - execute scripts G0–G4, gerando scorecards e artifacts;
   - falhe o job se qualquer gate não estiver em PASS.

5. **Merge para main**  
   Só ocorre quando:
   - scorecards G0–G4 estão em PASS no CI;
   - a ORR operacional (G5) foi executada com PASS (ou, em caso de NO_GO, há plano explícito para correção imediata);
   - o Capítulo 4 está atualizado, refletindo o estado real de filemap, scripts e CI.

---

## 4.4 Rotina diária de execução da S33

Para evitar acúmulo de risco no fim da sprint, recomenda‑se uma rotina diária simples:

- **Início do dia**  
  - rodar rapidamente os scripts G0–G3 localmente ou via CI de branch;
  - verificar se algum commit recente quebrou gates ou testes.

- **Blocos de foco**  
  - bloco 1: backend (domínio e serviços) → validar com testes;
  - bloco 2: frontend (cockpit) → validar com uso manual e, quando possível, testes automatizados;
  - bloco 3: runbooks e evidências → simular incidentes pequenos e enriquecer bundles.

- **Fim do dia**  
  - registrar avanços no Capítulo 4 (se houver mudanças relevantes em filemap ou plano);
  - garantir que `bin/s33_g*_*.sh` rodam sem erro em ambiente de desenvolvimento.

Essa disciplina reduz a probabilidade de descobrir gaps estruturais apenas na véspera da ORR.

---

## 4.5 Evidências, bundles e alinhamento com o DoD

A coleta de evidências é parte essencial da S33. O plano é:

- **Evidências de scripts e testes**  
  - logs, relatórios e artefatos gerados pelos scripts de gates são armazenados nas pastas `out/evidence/S33_G*/`.

- **Bundles de incidente (G4)**  
  - cada incidente usado como caso de estudo gera um subdiretório em `out/evidence/S33_G4_incidents/` com:
    - recortes de logs;
    - export de gráficos de observabilidade;
    - captura de tela do cockpit;
    - timeline textual do incidente;
    - link para runbook utilizado.

- **Evidências de ORR (G5)**  
  - roteiro preenchido da ORR com tempos, dificuldades, melhorias;
  - prints do cockpit em diferentes momentos;
  - síntese de feedback do operador convidado.

Essas evidências são a base para afirmar que o **DoD operacional** (Capítulo 2, Bloco 4) foi cumprido. Sem elas, o gate correto é NO_GO, mesmo que o código pareça "bom".

---

## 4.6 Riscos principais e estratégias de mitigação

A S33 tem alguns riscos específicos:

1. **Escopo invisível ou mal recortado (G0 fraco)**  
   Mitigação: investir tempo suficiente no `s33_scope_ops.md` e no `components_map`, com validação conjunta de Ops + Engenharia antes de começar a codar cockpit.

2. **Domínio de Incident subestimado**  
   Mitigação: tratar Incident como entidade real, com testes de domínio; usar exemplos concretos de incidentes da história do projeto para validar o lifecycle.

3. **Cockpit bonito, mas desconectado**  
   Mitigação: não considerar UI "pronta" enquanto não estiver alimentada pelos serviços de operação e pela API de OracleOps; usar G2 como barreira explícita.

4. **SLOs "de papel"**  
   Mitigação: só marcar SLO como pronto quando houver query operacional e, idealmente, um alerta testado; usar G3 e scripts de sanity para vigiar isso.

5. **Runbooks teóricos, não testados**  
   Mitigação: sempre testar runbooks com incidentes simulados, atualizando o texto à medida que fricções aparecem.

6. **ORR tratada como formalidade**  
   Mitigação: encarar a ORR como o momento de verdade; se o operador convidado não conseguir operar, o resultado correto é NO_GO, com plano de correção.

---

## 4.7 Checklist de encerramento da Sprint 33

Antes de declarar a S33 como concluída, o time deve ser capaz de responder "sim" para todas as perguntas abaixo:

1. G0–G4 possuem scorecards `S33_G*_*.json` em PASS e evidências em `out/evidence/S33_G*/`?
2. A ORR operacional (G5) foi executada, com scorecard preenchido e evidências armazenadas?
3. O operador convidado conseguiu usar o cockpit para inspecionar saúde, enxergar incidentes, acessar runbooks e entender bundles de evidência?
4. Os anexos opcionais (`s33_scope_ops.md`, `s33_components_map.yaml`, `s33_slos.md`, lifecycle/learnings) estão versionados em `programa 1/Epico 28/Sprint 33/` (ou explicitamente marcados como fora do repo) e são referenciados pelos scripts?
5. O código em backend e frontend corresponde à arquitetura descrita no Capítulo 3 (módulos, rotas, clientes, componentes)?
6. O workflow de CI específico da S33 roda os scripts de gate e falha quando algum deles está em NO_GO?
7. Os aprendizados da sprint (especialmente da ORR) foram refletidos em `s33_incidents_learnings.md` e convertidos em backlog?

Somente quando todas as respostas forem "sim" a Sprint 33 pode ser considerada **operacionalmente DONE**, com OracleOps v1 de pé e utilizável para o recorte que ela se propôs a cobrir.
