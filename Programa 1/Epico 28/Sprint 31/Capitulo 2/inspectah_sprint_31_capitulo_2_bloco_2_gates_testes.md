# Inspectah — Sprint 31 (E28-S3)
## Capítulo 2 — Bloco 2: Gates, Testes e Evidências

### 2.8 Papel deste bloco

Este bloco descreve **como** a Sprint 31 prova que atingiu os estados-alvo definidos no Bloco 1. Cada gate é um conjunto de scripts, testes e evidências que convertem promessas em sinais binários: PASS ou FAIL. Se o código parece pronto, mas o gate não passa, a sprint ainda não chegou lá.

Os gates desta sprint seguem o padrão:

- `S31-G0` a `S31-G5`: gates técnicos focados em escopo, modelo, ingestão, console, legado e integração com Programas 2–3.
- `S31-ORR`: uma revisão operacional e de risco que consolida os resultados e emite um GO/NO-GO para expansão.

Cada gate deve gerar evidências em `out/evidence/S31_*` e pelo menos um scorecard JSON em `out/scorecards/S31_*.json`.

---

### 2.9 S31-G0 — Scope & Baseline

**Objetivo**
Garantir que a sprint começa sobre uma base alinhada e auditável: docs certos no repo, configs mínimas de providers/perfis presentes, e escopo congelado.

**Script principal**
`bin/s31_g0_scope_and_baseline.sh`

**Responsabilidades do gate**
- Verificar a existência e a consistência dos documentos da sprint:
  - `docs/sprint_31_capitulo_1_contexto.md` (ou equivalente);
  - `docs/sprint_31_capitulo_2_gates_e_scorecards.md`;
  - `docs/sprint_31_capitulo_3_filemap.md`.
- Checar se arquivos de configuração mínimas de providers e perfis existem (por exemplo `config/providers.yml`, `config/ingestion_profiles.yml` ou equivalentes) e estão bem formados.
- Dump de um snapshot de escopo da sprint (hash de arquivos críticos, versão do repositório, lista de scripts da sprint) para comparação futura.

**Evidências esperadas**
- `out/evidence/S31_G0_scope/structure_check.log` com saída dos checks;
- `out/evidence/S31_G0_scope/scope_snapshot.json` com hashes/versões;
- `out/scorecards/S31_G0_scope_and_baseline.json` com status final do gate.

**Estados-alvo cobertos**
- Pré-condição para S31-SA-01, S31-SA-02, S31-SA-03.

---

### 2.10 S31-G1 — Modelos & Migrations Provider-first

**Objetivo**
Validar que o modelo de dados provider-first está refletido corretamente no banco e no código, sem quebrar o mundo legado.

**Script principal**
`bin/s31_g1_models_and_migrations.sh`

**Responsabilidades do gate**
- Aplicar migrations da S31 em um ambiente de teste limpo, incluindo:
  - criação da tabela `Provider` (ou equivalente);
  - adição de FKs opcionais `provider_id` e `profile_id` em `Source`/`ContentItem`;
  - ajustes em índices e constraints necessários para dedupe/proveniência.
- Rodar testes unitários de modelos para garantir:
  - integridade referencial (Providers ↔ Sources ↔ ContentItems);
  - comportamento esperado de criação de ContentItem com e sem provider/profile;
  - compatibilidade com registros antigos.
- Validar que migrations podem ser aplicadas em banco com dados reais (migração forward) sem perda ou corrupção de dados.

**Evidências esperadas**
- `out/evidence/S31_G1_models_and_migrations/migrations.log` com saída detalhada das migrations;
- `out/evidence/S31_G1_models_and_migrations/tests.log` com resultados de testes unitários;
- `out/scorecards/S31_G1_models_and_migrations.json` com status e resumo.

**Estados-alvo cobertos**
- S31-SA-01 (Provider-first no Data Hub);
- S31-SA-05 (Legado encaixado, não pendurado).

---

### 2.11 S31-G2 — Ingestão via Providers (News + Social)

**Objetivo**
Provar que jobs de ingestão via providers rodam fim a fim para os perfis-piloto, gerando ContentItems canônicos e deduplicados.

**Script principal**
`bin/s31_g2_provider_ingestion.sh`

**Responsabilidades do gate**
- Disparar jobs `INGEST_NEWS_*` e `INGEST_SOCIAL_*` para os perfis-piloto configurados (ex.: `BR_PT_HARD_NEWS`, `LATAM_ES_POLITICS`, `SOCIAL_BR_POLITICA_*`).
- Verificar que todos os jobs terminam com exit code 0 (sem falhas silenciosas).
- Amostrar a saída de ingestão para cada perfil, verificando:
  - quantidade de itens brutos recebidos do provider;
  - quantidade de ContentItems criados;
  - ausência de duplicatas óbvias (mesmo URL/corpo gerando múltiplos ContentItems).
- Checar que logs estruturados foram gerados, com provider, profile, contagens e erros por tipo.

**Evidências esperadas**
- `out/evidence/S31_G2_provider_ingestion/jobs.log` com a execução dos jobs;
- `out/evidence/S31_G2_provider_ingestion/dedupe_sample.json` com amostra de dedupe;
- `out/scorecards/S31_G2_provider_ingestion.json` com métricas básicas e status.

**Estados-alvo cobertos**
- S31-SA-01 (proveniência completa em ContentItems);
- S31-SA-02 (ingestão fim a fim em perfis-piloto).

---

### 2.12 S31-G3 — Console de Fontes v2 & Observabilidade

**Objetivo**
Garantir que o Console de Fontes e a stack de observabilidade suportam o modelo provider-first para os perfis-piloto.

**Script principal**
`bin/s31_g3_console_and_observability.sh`

**Responsabilidades do gate**
- Rodar testes de frontend (unitários e e2e mínimos) para:
  - tela/listagem de Providers;
  - tela/listagem/edição de Perfis de Ingestão;
  - fluxo de “rodar agora” um perfil de teste.
- Executar um teste e2e que faça:
  - criar ou editar um perfil-piloto de ingestão;
  - disparar um run de ingestão a partir do Console;
  - verificar, por meio de API interna/DB, que ContentItems novos foram criados.
- Coletar métricas por profile (calls, itens, erros, dedupe_ratio, uso de budget) e consolidar em scorecard.

**Evidências esperadas**
- `out/evidence/S31_G3_console/front_tests.log` com testes unitários de UI;
- `out/evidence/S31_G3_console/e2e_run.log` com fluxo ponta-a-ponta pelo Console;
- `out/scorecards/S31_G3_observabilidade.json` com métricas de ingestão por profile.

**Estados-alvo cobertos**
- S31-SA-03 (Console v2 com Providers & Perfis);
- S31-SA-04 (observabilidade e budgets v1 por perfil).

---

### 2.13 S31-G4 — Legado & Compatibilidade

**Objetivo**
Certificar que o provider-first não quebrou ingestão legada crítica e que existe ao menos um plano inicial de migração/coexistência.

**Script principal**
`bin/s31_g4_legacy_and_compat.sh`

**Responsabilidades do gate**
- Rodar um subconjunto representativo de fluxos de ingestão legados (RSS, API diretas, scrapers críticos) após as migrations e ajustes da S31.
- Verificar que esses fluxos ainda terminam com sucesso, trazendo itens conforme o esperado.
- Gerar uma tabela/relatório de coexistência, contendo para cada fonte ou classe de fonte:
  - se já tem equivalência em providers/perfis;
  - se permanece como fonte direta por necessidade;
  - se está marcada para desativação futura.

**Evidências esperadas**
- `out/evidence/S31_G4_legacy/legacy_jobs.log` com execução dos fluxos legados;
- `out/evidence/S31_G4_legacy/migration_plan.md` com o plano de migração/coexistência;
- `out/scorecards/S31_G4_legacy_and_compat.json` consolidando resultado.

**Estados-alvo cobertos**
- S31-SA-05 (legado encaixado, não pendurado).

---

### 2.14 S31-G5 — Integração com Programas 2–3 (Caso Piloto)

**Objetivo**
Demonstrar que o provider-first não é só ingestão isolada: ele alimenta de forma clara e rastreável Programas 2 (Claims/Sinais) e 3 (Truth-DB/Sistema de Blocos) em um domínio piloto.

**Script principal**
`bin/s31_g5_p2_p3_integration.sh`

**Responsabilidades do gate**
- Alimentar o pipeline de Programa 2 com ContentItems oriundos dos perfis-piloto do domínio escolhido (por exemplo, política/economia BR).
- Gerar Claims e ClaimGraph para esse domínio, a partir desses ContentItems.
- Produzir pelo menos um caso piloto em Programa 3 com FactBlocks/EvidenceBlocks derivados desse ClaimGraph.
- Exportar uma trilha de origem completa para o caso piloto, incluindo:
  - provider(s) envolvidos;
  - perfis de ingestão usados;
  - ContentItems de origem;
  - Claims gerados;
  - FactBlocks associados.

**Evidências esperadas**
- `out/evidence/S31_G5_p2_p3/pipeline_run.log` com execução das pipelines;
- `out/evidence/S31_G5_p2_p3/case_pilot_trace.json` com a trilha de origem estruturada;
- `out/scorecards/S31_G5_p2_p3_integration.json` com status e breve análise.

**Estados-alvo cobertos**
- S31-SA-06 (domínio piloto amarrado Provider → Perfil → ContentItem → Claim → FactBlock);
- reforça S31-SA-01 e S31-SA-02.

---

### 2.15 S31-ORR — Revisão Operacional & de Risco

**Objetivo**
Consolidar os resultados dos gates S31-G0..G5 e emitir um juízo operacional sobre o quanto é seguro expandir o uso de providers para além dos perfis-piloto.

**Script principal**
`bin/s31_orr.sh`

**Responsabilidades do gate**
- Ler todos os scorecards S31-G0..G5 e verificar:
  - se há gates em FAIL;
  - se há WARNs relevantes em métricas de erro, dedupe ou budget;
  - se há riscos de custo/complexidade que recomendem expansão cautelosa.
- Produzir um scorecard consolidado `S31_ORR_overview.json` contendo:
  - `status` global da sprint (`GO`, `GO_WITH_WARNINGS`, `NO_GO`);
  - resumo executivo para Programas 1–4;
  - recomendações para S32+ (por exemplo: quais perfis expandir, quais scrapers matar primeiro, quais domínios evitar por enquanto).
- Registrar notas de revisão em `out/evidence/S31_ORR/notes.md`, incluindo decisões de Conselho/Spec Office.

**Evidências esperadas**
- `out/scorecards/S31_ORR_overview.json` com o veredito consolidado;
- `out/evidence/S31_ORR/notes.md` com discussões e decisões-chave.

---

### 2.16 Relação gates ↔ estados-alvo

De forma resumida, a matriz de cobertura fica assim:

- S31-G0: prepara terreno (escopo e baseline) para S31-SA-01/02/03.
- S31-G1: cobre S31-SA-01 e S31-SA-05 (modelo e compatibilidade de dados).
- S31-G2: cobre S31-SA-01 e S31-SA-02 (ingestão via providers, dedupe e logs).
- S31-G3: cobre S31-SA-03 e S31-SA-04 (Console v2 e observabilidade/budget).
- S31-G4: cobre S31-SA-05 (legado encaixado, com plano de migração).
- S31-G5: cobre S31-SA-06 (integração com Programas 2–3 e trilha de origem).
- S31-ORR: confirma se todos os estados-alvo estão maduros o bastante para permitir expansão e uso real dos perfis-piloto em roadmap.

Com isso, qualquer discussão sobre “a sprint está pronta?” deixa de ser subjetiva. A resposta passa a ser: **roda os gates, lê os scorecards, olha o ORR**. Se a combinação disso disser GO, é porque o provider-first deixou de ser slide e virou sistema.

