# Inspectah — Sprint 31 (E28-S3)
## Capítulo 5 — Bloco 1: Papel do Capítulo & Cenários End-to-End

### 5.0 Por que este capítulo existe

Nos Capítulos 1–4 a Sprint 31 respondeu:

- **Cap.1** — *O que* queremos mudar: objetivos, domínio piloto, estados-alvo.
- **Cap.2** — *Como* vamos medir: gates, métricas, invariantes, scorecards, ORR script.
- **Cap.3** — *Onde* cada peça vive: arquitetura, filemap, fluxos backend/frontend.
- **Cap.4** — *Em que ordem* construir: fases de execução, comandos, evidências por gate.

Faltava responder a pergunta final do Sprint Playbook para ORR:

> **“Quais filmes completos vamos rodar, e que provas vamos guardar, para dizer com seriedade: ‘isso está pronto (ou não) para operar’?”**

O Capítulo 5 existe para:

1. Definir **cenários end-to-end (E2E)** concretos que exercitam provider-first + Console v2 no domínio piloto.
2. Especificar **como** será conduzido o **ORR S31** (Operational Readiness Review) e que materiais precisam estar na mesa.
3. Fixar quais **runbooks** e **controles operacionais** são obrigatórios ao final da sprint.
4. Explicitar riscos, **feature flags** e **planos de rollback** que cercam a S31.

Este Bloco 1 foca na primeira peça: os **cenários E2E** que transformam a S31 de “código aprovado em CI” para “capacidade real verificada”. Os blocos seguintes tratam de ORR, runbooks, riscos e flags.

---

### 5.1 Papel dos cenários E2E na S31

No Sprint Playbook, cenários E2E não são testes unitários grandes; são **histórias operacionais** que atravessam as camadas do sistema:

> Input realista entra por uma porta legítima → atravessa modelos, serviços, gates e UI → produz um resultado útil, auditável e alinhado com o estado-alvo.

Na Sprint 31, cada cenário E2E precisa cruzar, pelo menos:

- camada de **Provider** (fonte externa via API);
- camada de **IngestionProfile** (configuração de escopo e budget);
- criação de **ContentItem** canônico com proveniência completa;
- visibilidade pelo **Console de Fontes v2** (listas, detalhe, métricas básicas);
- e, para pelo menos um cenário, passagem por **Programas 2–3** até um caso piloto em FactBlocks.

Esses cenários servem para:

- apoiar a decisão de GO/NO-GO na ORR;
- validar que o desenho de custos/sanidade da S31 funciona em “pista real” (domínio piloto);
- gerar evidências fortes para futuros épicos e sprints (referência de ouro do que significa “provider-first funcionando”).

---

### 5.2 Conjunto mínimo de cenários E2E da Sprint 31

A S31 define um conjunto mínimo de **4 cenários E2E** que precisam ser executados (pelo menos em staging) antes da ORR:

1. **Cenário 1 — Ingestão piloto BR_PT_HARD_NEWS via provider**  
2. **Cenário 2 — Fluxo "Rodar agora" via Console para perfil de news**  
3. **Cenário 3 — Conteúdo provider-first chegando em Programa 2–3 (caso piloto)**  
4. **Cenário 4 — Sanity legado vs provider (não-regressão)**

A seguir, este bloco descreve cada cenário de forma operacional: objetivo, passos, gates exercitados e evidências esperadas.

---

### 5.3 Cenário 1 — Ingestão piloto BR_PT_HARD_NEWS via provider

**Objetivo:** provar que um perfil de news BR/PT (ex.: `BR_PT_HARD_NEWS`) roda via provider, gera `ContentItem` com proveniência completa e aparece corretamente no Console v2.

**Fluxo esperado:**

1. Migrations da S31 aplicadas; configs mínimas carregadas (`Provider` + `IngestionProfile` BR_PT_HARD_NEWS).
2. Execução de ingestão do perfil em ambiente de dev/staging:
   - via `profile_runner.run_profile(profile_id="BR_PT_HARD_NEWS", window=…)`  
   - ou via job `INGEST_PROFILE::BR_PT_HARD_NEWS` enfileirado pelo scheduler.
3. Criação de `ContentItem` canônicos com:
   - `provider_id`, `ingestion_profile_id`, `external_id` (se existir);  
   - `source_domain`, `ingested_at`;  
   - título, URL, published_at coerentes.
4. Abertura do Console v2 em `/console/ingestion-profiles`:
   - localizar `BR_PT_HARD_NEWS`;  
   - abrir tela de detalhe;  
   - ver última execução refletida (timestamp, volume, status, uso básico de budget).

**Gates exercitados:**

- **G2** — Provider ingestion (jobs, dedupe, métricas técnicas).  
- **G3** — Console & observabilidade (UI mostra a verdade do backend).

**Evidências mínimas:**

- `out/evidence/S31_G2_provider_ingestion/contentitems_sample.json` com amostra de ContentItems do perfil.  
- `out/evidence/S31_G3_console/e2e_run.log` narrando a execução do cenário (comandos, respostas, checks).  
- (Opcional) Screenshot/dump da tela de detalhe do perfil em `out/evidence/S31_G3_console/ui_screenshots/`.

---

### 5.4 Cenário 2 — Fluxo "Rodar agora" via Console para perfil de news

**Objetivo:** provar que o Console v2 não é painel passivo: operador consegue disparar uma ingestão e ver o efeito, com feedback e métricas consistentes.

**Fluxo esperado:**

1. Operador abre `/console/ingestion-profiles` e encontra o perfil `BR_PT_HARD_NEWS`.
2. Abre a página de detalhe desse perfil.
3. Clica em **"Rodar agora"**.
4. UI exibe feedback imediato:
   - mensagem de sucesso ou erro claro;  
   - se implementado, estado de “run em progresso”.
5. Após conclusão do job:
   - operador atualiza página;  
   - vê nova execução na lista (timestamp maior que o anterior);  
   - confere contagens de calls, itens brutos, ContentItems criados e erros.
6. Métricas internas registram o run:
   - `provider_calls_total` e `items_ingested_total` para o perfil aumentam;  
   - logs estruturados registram o run com `status=SUCCESS` ou erro bem descrito.

**Gates exercitados:**

- **G3** — Console & observabilidade (UI → API → job → métricas → UI).

**Evidências mínimas:**

- `out/evidence/S31_G3_console/front_tests.log` com teste E2E automatizado do fluxo ou, no mínimo, script documentando os passos.  
- `out/evidence/S31_G3_console/api_tests.log` mostrando chamada ao endpoint `run-now` e confirmação de enfileiramento.  
- Se possível, registro de métricas antes/depois em `metrics_snapshot.json`.

---

### 5.5 Cenário 3 — Conteúdo provider-first chegando em Programa 2–3 (caso piloto)

**Objetivo:** provar que o conteúdo capturado por providers não morre na entrada: ele alimenta a cadeia de interpretação e verdade (Programas 2–3) até um **caso piloto** auditável.

**Fluxo esperado:**

1. Escolher um evento concreto no domínio piloto (ex.: votação no Senado, decisão relevante de governo, medida econômica) coberto pelo provider.
2. Confirmar que o perfil `BR_PT_HARD_NEWS` (ou perfil adequado) capturou notícias sobre o evento:
   - buscar por palavras-chave, entidades ou URLs em `ContentItem` com `provider_id`.
3. Rodar pipeline de Programa 2 para esses ContentItems:
   - extrair Claims (declarações, números, promessas) com referência à origem (`content_item_id`).
4. Rodar pipeline de Programa 3:
   - montar um FactBlock/caso piloto que use pelo menos um Claim vindo de provider-first;  
   - garantir trilha: Provider → Perfil → ContentItem → Claim → FactBlock.
5. Registrar o caso piloto em evidência (mesmo que a UI de casos esteja embrionária).

**Gates exercitados:**

- **G5** — Integração Programas 2–3 (provider-first alimentando a camada de verdade).

**Evidências mínimas:**

- `out/evidence/S31_G5_p2_p3/case_pilot_trace.json` com a trilha completa (IDs, tipos, timestamps, fontes).  
- `out/evidence/S31_G5_p2_p3/pipeline_run.log` com a execução das pipelines sobre o caso piloto.  
- Referência cruzada no Cap.1/Cap.3 indicando qual caso piloto foi usado como “caso de demonstração S31”.

---

### 5.6 Cenário 4 — Sanity legado vs provider (não-regressão)

**Objetivo:** mostrar que a entrada de providers não quebrou ingestão legada crítica e que, para um recorte simples, as duas rotas captam o mesmo universo básico de fatos.

**Fluxo esperado:**

1. Selecionar um feed legado crítico (ex.: RSS de grande portal BR) listado em `docs/sprint_31_legacy_migration_plan.md` como `CRITICAL`.
2. Rodar ingestão via fluxo legado para uma janela curta (ex.: últimas 2–4 horas), gerando ContentItems legados.
3. Rodar ingestão via perfil provider-first que deve cobrir o mesmo recorte (mesmo país/idioma/tema) na mesma janela.
4. Comparar resultados de alto nível:
   - contagem de itens em cada rota;  
   - presença/ausência de notícias importantes;  
   - consistência geral de timestamps.
5. Registrar diferenças relevantes e, se necessário, ajustes de filtros/perfis no plano de migração.

**Gates exercitados:**

- **G4** — Legacy & compatibilidade (convivência segura, plano de migração).

**Evidências mínimas:**

- `out/evidence/S31_G4_legacy/legacy_jobs.log` com execuções legadas usadas no comparativo.  
- `out/evidence/S31_G4_legacy/migration_plan.md` atualizado, com notas sobre o comparativo legado vs provider.  
- JSON sintético (sem texto integral) ilustrando diferenças em cobertura `legacy_vs_provider_diff.json`.

---

### 5.7 Como estes cenários se conectam ao ORR

Na ORR da S31, o Conselho não olha só para gates isolados; ele olha para **filmes completos**. Estes quatro cenários são os filmes oficiais da sprint:

- Cenário 1 prova que **provider-first injeta conteúdo** no Data Hub de forma canônica.
- Cenário 2 prova que **operadores conseguem acionar e enxergar ingestão** via Console v2.
- Cenário 3 prova que **a camada de verdade (P2–P3) realmente consome providers** pelo menos em um caso piloto real.
- Cenário 4 prova que **não quebramos o legado** e que há um plano racional de migração.

Nos blocos seguintes do Capítulo 5, o plano de ORR, os runbooks e a matriz GO/NO-GO vão se apoiar diretamente nestes cenários. Eles são a âncora prática que separa S31 “no papel” de S31 “em operação controlada no domínio piloto.”

