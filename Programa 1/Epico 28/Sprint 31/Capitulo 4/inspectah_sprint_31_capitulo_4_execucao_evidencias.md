# Inspectah — Sprint 31 (E28-S3)
## Capítulo 4 — Execução, Comandos & Evidências

### 4.0 Papel deste capítulo

Este capítulo traduz os capítulos 1–3 em **plano de execução concreto**:

- define a ordem de trabalho em fases e ondas;
- explicita quais comandos devem ser usados em ambiente local e CI;
- amarra cada etapa às evidências que precisam ser produzidas em `out/evidence` e aos scorecards em `out/scorecards`;
- fixa a **Definition of Done** da Sprint 31.

É o documento que um dev ou o Codex deve seguir para implementar e validar a S31 sem improviso.

---

### 4.1 Estratégia geral de execução da Sprint 31

A Sprint 31 segue uma estratégia em **quatro fases**:

1. Fundação de dados e modelo (Provider, IngestionProfile, ajustes em ContentItem/Source).
2. Ingestão provider-first em backend (clients, runner, jobs) com observabilidade mínima.
3. Console de Fontes v2 (frontend + APIs) apoiado em providers/perfis.
4. Integração com Programas 2–3, convivência com legado e fechamento de gates/ORR.

Cada fase gera artefatos específicos, aciona gates e produz evidências.

---

### 4.2 Fase 1 — Fundação de dados & migrations

Objetivo: colocar o modelo provider-first de pé sem quebrar o mundo existente.

Escopo da fase:

- criar modelos `Provider` e `IngestionProfile`;
- ajustar `ContentItem` e `Source` para suportar proveniência;
- criar migrations correspondentes;
- preparar arquivos de config `providers.yml` e `ingestion_profiles.yml` com perfis-piloto;
- garantir que migrations rodam em banco limpo e em banco com dados reais.

Passos recomendados:

1. Implementar modelos em `app/models/provider.py` e `app/models/ingestion_profile.py`, seguindo o desenho do Capítulo 3.
2. Ajustar `app/models/content_item.py` para incluir campos de proveniência (`provider_id`, `ingestion_profile_id`, `external_id`, `source_domain`, `ingested_at`) e índices.
3. Ajustar `app/models/source.py` para suportar mapeamento de domínios a `Source`.
4. Gerar migrations correspondentes em `migrations/versions/31xx_*.py`.
5. Criar configuração mínima em `config/providers.yml` e `config/ingestion_profiles.yml` com:
   - pelo menos 1 provider de news e 1 de social;
   - perfis-piloto `BR_PT_HARD_NEWS` e um social (ex.: `SOCIAL_BR_POLITICA_TIMELINE`).

Comandos típicos (ambiente local):

- criação/atualização de migrations;
- aplicação de migrations em banco de desenvolvimento;
- sanity rápido de modelo (tests básicos).

Gate acionado nesta fase:

- `S31-G1` (Models & Migrations) — deve ser possível rodar `bin/s31_g1_models_and_migrations.sh` e obter PASS em ambiente local.

Evidências esperadas:

- `out/evidence/S31_G1_models_and_migrations/migrations.log`;
- `out/evidence/S31_G1_models_and_migrations/tests.log`;
- `out/scorecards/S31_G1_models_and_migrations.json` com status inicial (mesmo que ainda não definitivo de CI).

---

### 4.3 Fase 2 — Backend de ingestão provider-first

Objetivo: conseguir rodar ingestão via providers fim a fim para perfis-piloto em ambiente de desenvolvimento.

Escopo:

- implementar clients de provider (news/social);
- implementar serviços `profile_runner`, `normalizer`, `dedupe_service`;
- implementar jobs/scheduler para transformar perfis em execuções;
- instrumentar métricas e logs básicos para perfis-piloto;
- rodar ingestão de teste para perfis-piloto.

Passos recomendados:

1. Implementar clients em `app/ingestion/providers/base_client.py`, `news_provider_client.py`, `social_provider_client.py`, com assinatura alinhada ao Capítulo 3.
2. Implementar `app/ingestion/normalizer.py` e `app/ingestion/dedupe_service.py`.
3. Implementar `app/ingestion/profile_runner.py`, com função principal `run_profile(profile_id, window)`.
4. Implementar jobs em `app/jobs/provider_ingestion.py` e `app/jobs/scheduler.py`.
5. Integrar métricas e logs:
   - `app/metrics/ingestion_provider_metrics.py`;
   - `app/logging/ingestion_provider_logger.py`.
6. Rodar ingestão de teste em ambiente local para perfis-piloto, verificando criação de ContentItems com proveniência completa.

Gate acionado nesta fase:

- `S31-G2` (Provider Ingestion) em modo local, via `bin/s31_g2_provider_ingestion.sh`.

Evidências esperadas:

- `out/evidence/S31_G2_provider_ingestion/jobs.log` com execuções de perfis-piloto;
- `out/evidence/S31_G2_provider_ingestion/dedupe_sample.json` com amostra de dedupe;
- `out/scorecards/S31_G2_provider_ingestion.json` com métricas iniciais.

---

### 4.4 Fase 3 — Console de Fontes v2 (backend + frontend)

Objetivo: tornar provider-first operável via Console, sem precisar de terminal.

Escopo backend:

- implementar APIs `console_providers` e `console_ingestion_profiles`;
- expor endpoints para listagem, detalhe, criação/edição de perfis e run-now;
- integrar APIs com serviços e modelos implementados na Fase 2.

Escopo frontend:

- criar telas de lista e detalhe de Providers;
- criar telas de lista, criação/edição e detalhe de Perfis;
- incluir ação "Rodar agora" em perfis-piloto;
- exibir métricas básicas (últimas execuções, uso de budget) usando dados dos endpoints.

Passos recomendados:

1. Implementar API em `app/api/console_providers.py`:
   - `GET /api/console/providers`;
   - `GET /api/console/providers/{id}`.
2. Implementar API em `app/api/console_ingestion_profiles.py`:
   - `GET /api/console/ingestion-profiles`;
   - `GET /api/console/ingestion-profiles/{id}`;
   - `POST /api/console/ingestion-profiles`;
   - `PATCH /api/console/ingestion-profiles/{id}`;
   - `POST /api/console/ingestion-profiles/{id}/run-now`.
3. Implementar telas React/Next conforme Capítulo 3 (Bloco 3):
   - lista de providers;
   - detalhe de provider;
   - lista de perfis;
   - detalhe de perfil (com últimas execuções);
   - formulário de criação/edição de perfil.
4. Criar testes unitários e e2e mínimos para essas telas.

Gate acionado nesta fase:

- `S31-G3` (Console & Observabilidade) — `bin/s31_g3_console_and_observability.sh` roda testes de UI, chama APIs e valida execução run-now.

Evidências esperadas:

- `out/evidence/S31_G3_console/front_tests.log`;
- `out/evidence/S31_G3_console/e2e_run.log`;
- `out/scorecards/S31_G3_observabilidade.json` (incluindo métricas básicas por perfil).

---

### 4.5 Fase 4 — Legado, Programa 2–3 e fechamento de gates

Objetivo: garantir que provider-first convive bem com legado e alimenta Programas 2–3 como desenhado, com todos os gates e ORR fechados.

Escopo:

- implementar `legacy_adapter` e consolidar plano de migração em doc;
- configurar pipelines mínimas de Programa 2 para consumir ContentItems de perfis-piloto;
- configurar fluxo de Programa 3 para montar pelo menos um caso piloto completo;
- executar todos os gates S31-G0..G5 e consolidar ORR.

Passos recomendados:

1. Criar `app/ingestion/legacy_adapter.py` com:
   - lista de fluxos legados críticos;
   - funções para rodá-los e produzir resultados em estrutura padronizada.
2. Produzir `docs/sprint_31_legacy_migration_plan.md` com catálogo de fluxos legados e relação com providers/perfis.
3. Integrar Programas 2–3:
   - ajustar pipelines de Programa 2 para consumir ContentItems filtrados por perfis do domínio piloto;
   - selecionar caso piloto e garantir trilha de origem completa até FactBlocks em Programa 3.
4. Executar gates em sequência:
   - `bin/s31_g0_scope_and_baseline.sh`;
   - `bin/s31_g1_models_and_migrations.sh`;
   - `bin/s31_g2_provider_ingestion.sh`;
   - `bin/s31_g3_console_and_observability.sh`;
   - `bin/s31_g4_legacy_and_compat.sh`;
   - `bin/s31_g5_p2_p3_integration.sh`.
5. Executar `bin/s31_orr.sh` para consolidar scorecards em `S31_ORR_overview.json`.

Evidências esperadas:

- `out/evidence/S31_G4_legacy/legacy_jobs.log`;
- `out/evidence/S31_G4_legacy/migration_plan.md` (cópia ou link controlado do doc oficial);
- `out/evidence/S31_G5_p2_p3/pipeline_run.log`;
- `out/evidence/S31_G5_p2_p3/case_pilot_trace.json`;
- `out/scorecards/S31_G4_legacy_and_compat.json`;
- `out/scorecards/S31_G5_p2_p3_integration.json`;
- `out/evidence/S31_ORR/notes.md`;
- `out/scorecards/S31_ORR_overview.json`.

---

### 4.6 Integração com CI

A Sprint 31 deve ser coberta por um workflow de CI dedicado ou por uma extensão dos workflows de sprint existentes.

Expectativa mínima:

- existir um workflow (ex.: `.github/workflows/s31_gates.yml`) que execute pelo menos:
  - setup (instalação de dependências, migrations em banco de teste);
  - `bin/s31_g1_models_and_migrations.sh`;
  - `bin/s31_g2_provider_ingestion.sh` (com mocks ou quotas reduzidas, se necessário);
  - `bin/s31_g3_console_and_observability.sh` (tests de frontend);
  - `bin/s31_g4_legacy_and_compat.sh`;
  - `bin/s31_g5_p2_p3_integration.sh`;
  - `bin/s31_orr.sh`.

- ao final, artefatos `out/evidence/S31_*` e `out/scorecards/S31_*` devem ser upados como artifacts do job.

Critério: PR só pode ser mergeado se workflow S31 estiver verde.

---

### 4.7 Riscos, armadilhas e mitigação

Principais riscos da S31 e como mitigá-los:

1. **Explosão de custo por perfis mal configurados**  
   Mitigação: invariantes de budget, validações de formulário no Console, monitoramento de `budget_usage_ratio` e `provider_calls_total` em pilotos.

2. **Dedupe fraco gerando muitos ContentItems quase idênticos**  
   Mitigação: refinar chaves de dedupe, amostrar `dedupe_sample.json` em G2, ajustar heurísticas quando necessário.

3. **Migrations quebrando dados legados**  
   Mitigação: rodar G1 e G4 sempre em banco com dump de dados reais antes de promover para ambientes mais altos.

4. **Console divergindo da realidade**  
   Mitigação: ORR comparando docs e filemap com comportamento real, ajuste obrigatório de docs antes de GO.

5. **Integração frágil com Programas 2–3**  
   Mitigação: caso piloto bem escolhido, com trilha de origem clara e conferida manualmente pela equipe.

---

### 4.8 Definition of Done da Sprint 31

A Sprint 31 só pode ser considerada **entregue (GO)** se, ao mesmo tempo:

1. Todos os gates S31-G0..G5 estiverem em `status = PASS` ou, no máximo, `WARN` justificado em scorecards e notas de ORR.
2. `S31_ORR_overview.json` marcar `status` como `GO` ou `GO_WITH_WARNINGS`, com recomendações claras para próximos passos.
3. Pelo menos um domínio piloto (política/economia BR, ou equivalente) tiver trilha auditável completa:
   - Provider → Perfil → ContentItem → Claim → FactBlock.
4. Console de Fontes v2 permitir:
   - listar providers e perfis;
   - editar perfis-piloto;
   - acionar runs manuais de teste;
   - ver métricas básicas e uso de budget.
5. Fluxos legados críticos continuarem funcionando, com plano de migração documentado.
6. Todos os documentos da sprint (Capítulos 1–4, plano de legado) refletirem o estado real do sistema no branch de entrega.

Quando essas condições forem verdade, a S31 cumpre seu papel no Programa 1–3: transformar provider-first de hipótese em infraestrutura real, auditável e operável para o primeiro domínio de interesse do Inspectah.