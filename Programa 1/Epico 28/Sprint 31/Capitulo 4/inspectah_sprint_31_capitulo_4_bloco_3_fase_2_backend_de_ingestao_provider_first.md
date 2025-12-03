# Inspectah — Sprint 31 (E28-S3)
## Capítulo 4 — Bloco 3: Fase 2 — Backend de Ingestão Provider-first

### 4.11 Escopo exato da Fase 2

A Fase 2 pega o esqueleto de dados criado na Fase 1 e coloca músculo e sistema nervoso em cima dele:

> Fazer perfis de ingestão realmente **rodarem** contra providers externos, gerando `ContentItem` com proveniência completa, com métricas e logs mínimos.

Escopo incluído:

- implementação dos **clients de provider** (news e social);
- implementação de **serviços de normalização** e **dedupe**;
- implementação do **`profile_runner`** (motor de ingestão por perfil);
- implementação de **jobs e scheduler** para transformar perfis em runs reais;
- instrumentação de **métricas** e **logs estruturados** por perfil;
- execução de ingestão piloto para pelo menos dois perfis (news BR e social BR);
- gate **S31-G2** rodando, com evidências e scorecard.

Escopo explicitamente fora desta fase:

- telas de Console (UI) para operar providers/perfis;
- APIs de Console;
- integração com Programas 2–3;
- plano de legado detalhado (isso entra mais forte na Fase 4).

---

### 4.12 Ordem de trabalho recomendada na Fase 2

Para evitar virar “scriptland”, a sequência sugerida é:

1. **Clientes de provider em modo isolado**
   - Implementar `base_client` com autenticação, retries e tratamento de erros genérico.
   - Implementar `news_provider_client` e `social_provider_client` mapeando filtros de `IngestionProfile` → parâmetros de API.
   - Criar testes unitários focados em:
     - montagem de URLs/parâmetros correta;
     - comportamento em respostas de erro (rate limit, auth, 5xx).

2. **Normalização & tipos brutos**
   - Definir tipos intermediários `RawNewsItem` e `RawSocialItem` (classe ou dataclass simples) representando o JSON do provider de forma amigável.
   - Implementar `normalizer` com mapeamento `Raw*` → `ContentItem`:
     - título, corpo, URL, timestamps;
     - campos de proveniência (`provider_id`, `ingestion_profile_id`, `external_id`, `source_domain`, `ingested_at`).
   - Testar normalização com amostras reais de payload (salvas em fixtures).

3. **Dedupe service**
   - Implementar `dedupe_service` com estratégia mínima:
     - chave primária `(provider_id, external_id)` quando houver `external_id` confiável;
     - fallback com `source_domain + title + published_at` e/ou hash de conteúdo.
   - Escrever testes que garantam que itens repetidos não criam novos `ContentItem`, apenas atualizam metadados.

4. **Profile runner**
   - Implementar `profile_runner.run_profile(profile_id, window=None)`:
     - carregar `IngestionProfile` e provider;
     - checar status (ACTIVE/PAUSED/EXPERIMENTAL);
     - aplicar controle simples de budget (`budget_limit_calls`);
     - chamar o client apropriado para obter `Raw*` no intervalo desejado;
     - passar itens por `normalizer` + `dedupe_service`;
     - registrar métrica e log de run;
     - devolver um `RunResult` com contagens e erros.
   - Testar `run_profile` em modo mockado:
     - provider client mockado devolvendo N itens;
     - verificando contagens, dedupe e persistência de `ContentItem`.

5. **Jobs & scheduler**
   - Implementar job `INGEST_PROFILE::<profile_id>` em `app/jobs/provider_ingestion.py`:
     - consumir mensagem da fila;
     - chamar `profile_runner.run_profile`;
     - atualizar metadados de última execução do perfil;
     - logar resultado.
   - Implementar `scheduler` em `app/jobs/scheduler.py`:
     - buscar perfis `ACTIVE`;
     - decidir se é hora de rodar (com base em schedule/último run);
     - enfileirar jobs por perfil.
   - Testar pelo menos em modo “dry-run”:
     - scheduler gerando jobs com base em perfis de teste;
     - job consumindo e produzindo `RunResult`.

6. **Instrumentação de métricas e logs**
   - Integrar `profile_runner` com:
     - `app/metrics/ingestion_provider_metrics.py` (calls, itens, ContentItems, erros, dedupe_ratio, budget_usage);
     - `app/logging/ingestion_provider_logger.py` (logs estruturados por run).
   - Validar via testes simples que:
     - cada run gera pelo menos um evento de log;
     - métricas são incrementadas nas labels corretas (`profile_id`, `provider_id`, etc.).

7. **Rodar ingestão piloto real**
   - Usar os perfis definidos na Fase 1 (ex.: `BR_PT_HARD_NEWS` + um social BR) em ambiente de desenvolvimento.
   - Rodar manually (via script ou CLI) uma execução de `run_profile` para cada um.
   - Confirmar que:
     - `ContentItem` foram criados com proveniência completa;
     - não houve explosão absurda de registros duplicados;
     - logs e métricas refletem o run.

8. **Rodar gate S31-G2 em modo local**
   - Executar `bin/s31_g2_provider_ingestion.sh` e conferir logs/scorecard.

---

### 4.13 Comportamento esperado de `bin/s31_g2_provider_ingestion.sh`

O gate G2 é o exame de sangue da ingestão provider-first em backend. O script deve, no mínimo:

1. **Preparar ambiente de teste**
   - garantir que migrations já foram aplicadas (ou rodar G1 como pré-requisito);
   - carregar configs mínimas de providers/perfis (ou verificar que existem);
   - preparar banco de teste isolado, se for o padrão.

2. **Rodar ingestão de teste para perfis-piloto**
   - executar `profile_runner.run_profile` (direto ou via job) para:
     - 1 perfil de news (BR/PT);
     - 1 perfil de social (BR).
   - usar janela de tempo controlada (ex.: última 1h ou pequeno intervalo) para evitar ingestão massiva.

3. **Coletar métricas e validar invariantes mínimos**
   - verificar que, para cada perfil:
     - `provider_calls_total` > 0;
     - `items_ingested_total` > 0;
     - `contentitems_created_total` > 0;
     - `dedupe_ratio` está dentro de uma faixa razoável (ex.: não 0% nem 99% sem explicação);
   - opcionalmente, checar que `budget_usage_ratio` para o run de teste é pequeno (sanity de budget).

4. **Gerar evidências**
   - salvar logs de execução em `out/evidence/S31_G2_provider_ingestion/jobs.log`;
   - salvar amostra de ContentItems e dedupe em algo como:
     - `out/evidence/S31_G2_provider_ingestion/contentitems_sample.json`;
     - `out/evidence/S31_G2_provider_ingestion/dedupe_sample.json`.

5. **Gerar scorecard G2**
   - escrever `out/scorecards/S31_G2_provider_ingestion.json` com campos mínimos:
     - `gate_id`: `"S31-G2"`;
     - `status`: `"PASS"`, `"WARN"` ou `"FAIL"`;
     - `profiles_tested`: lista de perfis exercitados;
     - `metrics_summary`: resumo de calls, itens, dedupe, erros;
     - `issues_detected`: lista (possivelmente vazia) de problemas;
     - `evidence_paths`: paths dos arquivos em `out/evidence`.

Critério:

- `PASS`: ingestão rodou para ambos perfis, métricas mínimas cumpridas, sem falhas graves;
- `WARN`: ingestão funcionou, mas com problemas localizados (ex.: dedupe agressivo demais), documentados e com plano de ajuste;
- `FAIL`: ingestão não roda, ou gera dados extremamente suspeitos, ou falha de forma não controlada.

---

### 4.14 Evidências mínimas da Fase 2

Ao final da Fase 2, espera-se encontrar no repo (ou nos artifacts do CI):

- `out/evidence/S31_G2_provider_ingestion/jobs.log`
  - logs de runs de perfis-piloto, com `profile_id`, `provider_id`, contagens e status.

- `out/evidence/S31_G2_provider_ingestion/contentitems_sample.json`
  - amostra (anonimizada se necessário) de ContentItems criados, mostrando proveniência completa.

- `out/evidence/S31_G2_provider_ingestion/dedupe_sample.json`
  - exemplos de itens brutos e seu mapeamento para ContentItems únicos.

- `out/scorecards/S31_G2_provider_ingestion.json`
  - scorecard com status e resumo de métricas.

Idealmente, haverá também:

- testes automatizados cobrindo clients, normalizer, dedupe e profile_runner (logs em `tests.log` ou equivalente);
- notas internas (em `docs/` ou `out/evidence/`) explicando peculiaridades do provider usado.

---

### 4.15 Riscos específicos desta fase e mitigação

1. **Client acoplado demais a um provider específico**  
   Sintoma: qualquer peculiaridade do provider vaza para o resto do código.
   
   Mitigação: manter mapeamentos específicos no client; usar `Raw*` + `normalizer` para abstrair diferenças; testes cobrindo contratos genéricos.

2. **Dedupe insuficiente ou agressivo demais**  
   - Insuficiente: gera enxurrada de duplicatas; bancos incham, métricas enganam.
   - Agressivo demais: conteúdos diferentes são colapsados em um só.
   
   Mitigação: avaliar amostras em `dedupe_sample.json`; ajustar chaves e heurísticas iterativamente; não exagerar na fase 2 — melhor errar para menos dedupe do que amputar conteúdo.

3. **Budget ignorado ou mal implementado**  
   Sintoma: runs em modo de teste já mostram `budget_usage_ratio` perto de 1 sem motivo.
   
   Mitigação: implementar budget como guarda mínima no `profile_runner`; usar perfis-piloto com limites bem conservadores; monitorar métricas.

4. **Erro silencioso em ingestão**  
   Sintoma: G2 passa, mas ninguém percebe que metade das chamadas falha sempre.
   
   Mitigação: logs estruturados registrando erros por tipo; G2 checando se a taxa de erro não é absurda (ex.: > 50%).

---

### 4.16 Resultado esperado ao fim da Fase 2

Quando a Fase 2 estiver concluída de verdade, o estado alvo é:

- `Provider` e `IngestionProfile` deixaram de ser só modelo estático e passaram a gerar ingestões reais;
- `profile_runner` consegue pegar um perfil-piloto e transformar em ContentItems canônicos com proveniência correta;
- dedupe funciona em nível razoável, evitando duplicatas grotescas;
- métricas e logs por perfil são gerados e podem ser visualizados (mesmo que ainda sem dashboards sofisticados);
- o gate S31-G2 está verde (ou, no máximo, WARN bem descrito), com evidências salvas;
- Cap.3 (backend) e Cap.4 (Bloco 3) descrevem fielmente o que está implementado.

A partir daqui, a Sprint 31 está pronta para subir um nível: expor esse backend via Console de Fontes v2 (Fase 3), permitindo que humanos operem providers/perfis sem tocar em scripts.

