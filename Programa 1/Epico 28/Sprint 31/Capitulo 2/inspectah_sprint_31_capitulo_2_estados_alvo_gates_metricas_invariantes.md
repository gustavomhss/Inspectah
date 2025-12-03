# Inspectah — Sprint 31 (E28-S3)
## Capítulo 2 — Estados-Alvo, Gates, Métricas & Invariantes

### 2.0 Função deste capítulo

Este capítulo traduz o contexto da Sprint 31 (Cap.1) em coisas verificáveis:

- **Estados-alvo (SA)**: o que precisa ser verdade ao final da S31, do ponto de vista de produto e operação.
- **Gates (G)**: scripts e checks que provam, de forma mecânica, que esses estados foram atingidos.
- **Métricas & scorecards**: como medir qualidade/custo/comportamento da ingestão provider-first.
- **Invariantes**: regras que não podem ser quebradas sem acionar NO-GO, mesmo que todo o resto pareça verde.

A numeração desta sprint segue o padrão `S31-SA-0N` e `S31-GN`, com scripts em `bin/` e evidências em `out/evidence/S31_*` e `out/scorecards/S31_*.json`.

---

### 2.1 Estados-alvo (SA)

#### S31-SA-01 — Provider-first de verdade no Data Hub (triângulo Provider → Profile → ContentItem)

Ao final da S31, o Data Hub precisa tratar ingestão provider-first como **caminho padrão** para notícias e social no domínio piloto. Isso significa:

- existem entidades `Provider` persistidas e funcionais (pelo menos 1 news_provider + 1 social_provider reais);
- existem **Perfis de Ingestão** que combinam provider + filtros (país, idioma, tema, keywords) + frequência + budget;
- ContentItems criados a partir desses perfis trazem proveniência completa: provider_id, profile_id, source/domain e identificadores externos.

**Verificação**
- rodar `bin/s31_g1_models_and_migrations.sh` e `bin/s31_g2_provider_ingestion.sh` em ambiente de teste;
- inspecionar amostras de ContentItems gerados pelos perfis piloto, confirmando campos de proveniência preenchidos e coerentes.

---

#### S31-SA-02 — Ingestão via providers operando fim a fim em perfis-piloto

Ao final da S31, a plataforma consegue rodar ingestão fim a fim, via fila/worker, para um conjunto pequeno mas crítico de perfis:

- pelo menos 1 perfil `BR_PT_HARD_NEWS` (Brasil, PT, política + economia);
- pelo menos 1 perfil internacional piloto (por exemplo, Latam ES ou EUA/UE EN);
- pelo menos 1 perfil `social` relevante para narrativa política/econômica.

Para cada perfil, é possível:

- disparar ingestão (agendada ou manual);
- buscar conteúdo real junto ao provider;
- normalizar em ContentItems canônicos;
- registrar logs e métricas básicas de execução.

**Verificação**
- rodar `bin/s31_g2_provider_ingestion.sh` em ambiente de teste/staging;
- checar, via queries e painéis, que há ContentItems novos associados aos perfis piloto, sem explosão de duplicatas nem erros silenciosos.

---

#### S31-SA-03 — Console de Fontes v2: Providers & Perfis como cidadãos de primeira classe

Ao final da S31, o Console de Fontes precisa refletir o modelo mental provider-first. Um operador, sem abrir código, consegue:

- listar Providers configurados (news/social), com estado (ativo/inativo) e informações básicas;
- criar/editar Perfis de Ingestão (provider + filtros + frequência + budget) via UI;
- ver status e últimas execuções dos perfis (sucesso/erro, volume de itens) e acionar rodadas manuais de teste.

**Verificação**
- rodar `bin/s31_g3_console_and_observability.sh` (incluindo testes de frontend/end-to-end mínimos);
- executar um fluxo manual: criar/editar perfil piloto → acionar ingestão via UI → ver resultado em métricas e itens ingestados.

---

#### S31-SA-04 — Observabilidade & budgets v1 para perfis de ingestão

Ao final da S31, os perfis-piloto de ingestão precisam estar **instrumentados** o suficiente para que o time não opere no escuro. Para cada perfil, deve ser possível ver, em painéis e/ou scorecards:

- quantas chamadas ao provider foram feitas num intervalo (dia/semana);
- quantos itens brutos foram retornados e quantos viraram ContentItems novos (dedupe visível);
- quantos erros ocorreram (por tipo);
- qual é o budget configurado (chamadas/dia ou volume-alvo) e se está sendo respeitado.

**Verificação**
- rodar `bin/s31_g3_console_and_observability.sh` e abrir o painel de ingestão via providers;
- validar scorecards `out/scorecards/S31_G3_observabilidade.json` com métricas agregadas por profile.

---

#### S31-SA-05 — Legado encaixado, não pendurado (coexistência controlada)

Ao final da S31, a plataforma precisa ter uma história clara sobre como providers convivem com fontes diretas e scrapers legados. Isso implica:

- modelo de dados compatível (novos campos não quebram ingestão existente);
- scripts e pipelines antigos rodando normalmente ou explicitamente marcados como “legado controlado”;
- lista mínima registrada de classes de fontes legadas: o que já foi migrado; o que ficará de pé por necessidade; o que está marcado para aposentadoria em sprints futuras.

**Verificação**
- rodar `bin/s31_g4_legacy_and_compat.sh` para executar sanity de ingestão antiga + nova;
- conferir doc em `docs/sprint_31_capitulo_4_execucao_e_evidencias.md` com tabela de coexistência/migração aprovada pelo Spec Office.

---

#### S31-SA-06 — Conexão explícita entre perfis de ingestão e pipelines de Programa 2–3

Ao final da S31, pelo menos um domínio piloto (por exemplo, política BR) precisa estar **amarrado** de ponta a ponta:

- perfis de ingestão responsáveis por alimentar esse domínio estão definidos e documentados;
- o pipeline de interpretação (Programa 2) sabe explicitamente quais perfis o alimentam;
- ContentItems oriundos desses perfis já entram no ClaimGraph e em um caso piloto;
- existe, para esse caso piloto, trilha de origem Provider → Perfil → ContentItem → Claim → FactBlock.

**Verificação**
- rodar `bin/s31_g5_p2_p3_integration.sh` para executar testes de pipeline com caso piloto;
- abrir um caso piloto em ambiente de teste e caminhar a trilha de origem com passos reprodutíveis (documentados como evidência).

---

### 2.2 Gates & testes (G)

Os gates da S31 são o mecanismo mecânico para provar que os estados-alvo foram alcançados. Todos devem produzir evidências e scorecards.

#### S31-G0 — Scope & Baseline

**Script**: `bin/s31_g0_scope_and_baseline.sh`

**Função**
- garantir que Cap.1, Cap.2 e Cap.3 da Sprint 31 existem, estão no repositório, e foram congelados para execução;
- verificar que os arquivos de configuração mínimos para providers/perfis estão presentes (YAML/JSON, .env.example atualizado);
- registrar um snapshot de “escopo congelado” em `out/evidence/S31_G0_scope/`.

**Cobre**
- S31-SA-01 (pré-condição), S31-SA-02 (pré-condição).

---

#### S31-G1 — Modelos & migrations provider-first

**Script**: `bin/s31_g1_models_and_migrations.sh`

**Função**
- rodar migrations da S31 (criação de `Provider`, campos em `Source`/`ContentItem`);
- rodar testes de modelo (unitários) garantindo integridade e relações;
- validar que dados pré-existentes continuam íntegros.

**Evidências**
- `out/evidence/S31_G1_models_and_migrations/migrations.log`;
- `out/evidence/S31_G1_models_and_migrations/tests.log`.

**Cobre**
- S31-SA-01, S31-SA-05.

---

#### S31-G2 — Ingestão via providers (news + social)

**Script**: `bin/s31_g2_provider_ingestion.sh`

**Função**
- disparar jobs `INGEST_NEWS_*` e `INGEST_SOCIAL_*` para os perfis-piloto;
- validar que jobs concluem com exit 0, criam ContentItems e registram logs estruturados;
- checar amostra de deduplicação (sem múltiplos ContentItems idênticos para o mesmo conteúdo).

**Evidências**
- `out/evidence/S31_G2_provider_ingestion/jobs.log`;
- `out/evidence/S31_G2_provider_ingestion/dedupe_sample.json`.

**Cobre**
- S31-SA-01, S31-SA-02.

---

#### S31-G3 — Console de Fontes v2 & Observabilidade

**Script**: `bin/s31_g3_console_and_observability.sh`

**Função**
- rodar testes de frontend (unit + e2e mínimo) para telas de Providers e Perfis;
- validar que o Console permite criar/editar perfis e disparar ingestão de teste;
- coletar métricas de ingestão por profile e consolidar em scorecards.

**Evidências**
- `out/evidence/S31_G3_console/front_tests.log`;
- `out/evidence/S31_G3_console/e2e_run.log`;
- `out/scorecards/S31_G3_observabilidade.json`.

**Cobre**
- S31-SA-03, S31-SA-04.

---

#### S31-G4 — Legado & compatibilidade

**Script**: `bin/s31_g4_legacy_and_compat.sh`

**Função**
- rodar um subconjunto representativo de fluxos de ingestão antigos (RSS, APIs diretas, scrapers);
- validar que continuam funcionando após migrations e inclusão de providers;
- gerar tabela comparativa de fontes (legado vs provider) e plano de migração inicial.

**Evidências**
- `out/evidence/S31_G4_legacy/legacy_jobs.log`;
- `out/evidence/S31_G4_legacy/migration_plan.md`.

**Cobre**
- S31-SA-05.

---

#### S31-G5 — Integração com Programas 2–3 (caso piloto)

**Script**: `bin/s31_g5_p2_p3_integration.sh`

**Função**
- alimentar pipeline de Programa 2 com ContentItems oriundos de perfis-piloto;
- gerar Claims, ClaimGraph e pelo menos um caso piloto com evidências no Truth-DB;
- validar trilha Provider → Perfil → ContentItem → Claim → FactBlock.

**Evidências**
- `out/evidence/S31_G5_p2_p3/case_pilot_trace.json`;
- `out/evidence/S31_G5_p2_p3/pipeline_run.log`.

**Cobre**
- S31-SA-06 (e reforça S31-SA-01/02).

---

#### S31-ORR — Revisão operacional & de risco

Além dos gates técnicos, a sprint terá uma pequena ORR específica:

**Script**: `bin/s31_orr.sh`

**Função**
- consolidar scorecards de todos os gates S31-G0..G5;
- revisar, com Spec Office + squads relevantes, se:
  - o recorte de perfis-piloto faz sentido;
  - os custos e riscos percebidos estão alinhados com o que foi medido;
  - há GO/NO-GO para expandir perfis em sprints seguintes.

**Evidências**
- `out/scorecards/S31_ORR_overview.json`;
- `out/evidence/S31_ORR/notes.md`.

---

### 2.3 Métricas & scorecards

Para a S31, as métricas principais não são de throughput absoluto, e sim de **sanidade e governabilidade** da ingestão via providers.

Mínimo de métricas por profile (news/social):

- `items_ingested_total` — número de itens que chegaram do provider num intervalo;
- `contentitems_created_total` — número de ContentItems únicos criados (após dedupe);
- `provider_calls_total` — número de chamadas à API do provider;
- `provider_errors_total` — número de chamadas com erro (por tipo);
- `dedupe_ratio` = `contentitems_created_total / items_ingested_total`;
- `budget_limit_calls` — limite configurado de chamadas/dia/mês;
- `budget_usage_ratio` = `provider_calls_total / budget_limit_calls`.

Scorecards

- Cada gate relevante (G2, G3, G5, ORR) deve gerar um scorecard JSON em `out/scorecards/S31_GN_*.json` com, no mínimo, os campos:
  - `gate_id` (ex.: `S31-G2`),
  - `status` (`PASS`, `FAIL`, `WARN`),
  - `metrics` (objeto com os valores principais),
  - `summary` (texto curto explicando o resultado),
  - `evidence_paths` (lista de arquivos em `out/evidence/...`).

Interpretação

- **GO**: todos os gates S31-G0..G5 em `PASS` e scorecards sem `WARN` em métricas críticas (dedupe_ratio não bizarro, budget_usage sob controle, erros em patamar aceitável para piloto).
- **GO com ressalva**: gates técnicos em `PASS`, mas ORR marcando `WARN` em riscos de custo, complexidade ou legado (expansão recomendada apenas sob certas condições).
- **NO-GO**: qualquer gate em `FAIL` em aspectos estruturais (migrations quebrando legado, ingestão instável, impossibilidade de rastrear proveniência, incapacidade de enxergar custos por perfil).

---

### 2.4 Invariantes & não-negociáveis da Sprint 31

Além de metas, a S31 tem **invariantes**: coisas que, se quebradas, derrubam a sprint independentemente de quantos testes passaram.

**Invariante 1 — Nenhum ContentItem de provider sem proveniência completa**

- Todo ContentItem vindo de providers deve ter: `provider_id`, `profile_id`, `source/domain`, identificador externo e timestamps consistentes.
- Gate que guarda: S31-G1 (modelo) + S31-G2 (ingestão).

**Invariante 2 — Provider-first não pode quebrar ingestão legada em produção**

- Nenhuma migration ou mudança de ingestão pode derrubar fluxos legados ainda marcados como críticos.
- Gate que guarda: S31-G1 (migrations) + S31-G4 (compatibilidade).

**Invariante 3 — Não operar perfis-piloto cegamente em relação a budget**

- Não é aceitável rodar perfis-piloto sem budget configurado ou sem métricas mínimas de uso/custo.
- Gate que guarda: S31-G3 (observabilidade) + S31-ORR (revisão de risco).

**Invariante 4 — Domínio piloto precisa ter trilha de origem auditável**

- Para o domínio piloto escolhido (ex.: política BR), é obrigatório que o time consiga reconstruir Provider → Perfil → ContentItem → Claim → FactBlock para pelo menos um caso piloto.
- Gate que guarda: S31-G5 (integração P2–P3) + S31-ORR.

**Invariante 5 — Nada entra em ClaimGraph invisível para o Console**

- Qualquer feed que alimente ClaimGraph no domínio piloto precisa estar representado em pelo menos um Perfil de Ingestão visível no Console.
- Gate que guarda: S31-G2 (ingestão) + S31-G3 (console) + S31-G5 (P2–P3).

Com estes estados-alvo, gates, métricas e invariantes, a Sprint 31 ganha uma superfície de verificação dura: ou o provider-first está de pé, observável e compatível, ou a sprint não é GO, por mais que o código “pareça pronto” em um PR isolado.

