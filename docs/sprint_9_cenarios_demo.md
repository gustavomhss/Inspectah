# Inspectah — Sprint 9
## Cenários oficiais de demo (C1–C3)

Este documento descreve os três cenários oficiais da Sprint 9 usados em gates, demos e auditorias. Todos foram adaptados de casos reais acompanhados pela equipe de inteligência de preços e de fatos públicos, e seguem os invariantes Inv1–Inv4.

### Visão geral rápida

| ID | Tipo | Problema real que inspirou | Fontes oficiais (>=2) | Resultados esperados |
|----|------|---------------------------|-----------------------|----------------------|
| C1 | Preço médio (agregação) | Monitorar a cesta básica "Ministério da Cidadania" em supermercados paulistas | (1) Painel de Preços SEAE (CSV semanal); (2) encarte digital Pão de Açúcar (API interna); (3) Coletor mobile Inspectah (opcional para auditoria) — fixtures em `tests/fixtures/s9_preco_medio/*.json` | Valor médio atualizado da cesta + intervalo, nº de fontes, confiança |
| C2 | Comparação simples | Operação de abastecimento do governo do RJ avaliando onde comprar gás GLP 13kg | (1) ANP Preços (planilha semanal); (2) Sindigás Monitor (JSON público); (3) Registro local da Secretaria — fixtures em `tests/fixtures/s9_comparacao/*.json` | Ranking com valor por fornecedor/local e justificativa do melhor custo |
| C3 | Checagem factual | Checar fala do Dep. Federal Carla Fontes: "o diesel caiu 12% em BH nos últimos 30 dias" | (1) Diário Oficial de BH (RSS consolidado); (2) Portal Transparência Minas (API); (3) Dados ANP (mesmo período) — fixtures em `tests/fixtures/s9_checagem_factual/*.json` | Verdadeiro/Falso/Indeterminado + explicação textual + trilha de evidências |

Todas as execuções oficiais devem salvar o triplo `QueryLog` ↔ `EvidenceBundle` ↔ `UserResponse` em `out/evidence/s9_logs|s9_bundles|s9_responses`. `meta.num_sources` precisa ser ≥ 2 e divergências entre fontes devem ser refletidas na confiança.

---

### C1 — Preço médio da cesta básica paulista

- **Objetivo**: responder quanto custa a cesta básica (arroz 5kg, feijão 2kg, leite 12 un, óleo 4 un, carne 6kg, pão 6kg) entre supermercados de SP, última semana fechada.
- **Personas**: Operador do Observatório de Preços e analista de comunicação interna.
- **Fontes**:
  1. `Painel_SEAE_cesta.csv` (extraído da base pública SEAE, atualizado semanalmente).
  2. `pao_de_acucar_grocery_api.json` (API privada usada pelo time comercial para promoções).
  3. Opcional para auditoria: `inspectah_mobile_samples.csv` (coletas pontuais dos estagiários).
- **Cadência/fixtures**: arquivos ficam em `tests/fixtures/s9_preco_medio/`. Admin deve manter no mínimo as duas primeiras fontes ativas; a terceira entra como fallback.
- **Query canônica**: `"Qual é o preço médio atual da cesta básica padrão em São Paulo?"` (`info_type=C1`, `location=SP`, `window_days=7`).
- **Expectativa de resposta**:
  - Texto principal com valor médio e variação vs. semana anterior.
  - `summary_structured`: `value`, `interval_low/high`, `num_sources`, `confidence`, `timeframe`.
  - `evidence_top`: referências para os dois datasets principais com timestamp.
- **Sinais observáveis**:
  - Métricas: incremento em `inspectah_s9_user_queries_total{info_type="C1"}` e registro de latência.
  - Se uma fonte falhar, Admin exibe badge vermelho com o último erro.

### C2 — Comparação simples de GLP 13kg (RJ)

- **Objetivo**: determinar onde comprar 1.000 botijões GLP 13kg para estoque emergencial do RJ, escolhendo o fornecedor mais barato entre capital e Baixada.
- **Fontes**:
  1. `anp_glp_rj_semana.csv` (dataset semanal publicado pela ANP, transformado em fixture).
  2. `sindigas_monitor.json` (coleta automatizada do boletim Sindigás com preços por revenda).
  3. `secretaria_abastecimento_custos.csv` (histórico local usado para validação cruzada).
- **Fixtures**: `tests/fixtures/s9_comparacao/` guarda os snapshots e metadados de ingestão.
- **Query canônica**: `"Onde o botijão de gás 13kg está mais barato nesta semana, capital ou Baixada Fluminense?"` (`info_type=C2`, `window_days=7`, `metric=median`).
- **Resposta esperada**:
  - Texto com ranking (1º lugar + diferença percentual).
  - `summary_structured`: `best_location`, `best_price`, `runner_up`, `price_delta_pct`, `num_sources`, `confidence`.
  - Explicação da divergência entre fontes quando >5%.
- **Observações**:
  - Divergências acentuadas devem reduzir confiança e aparecer explicitamente.
  - Métricas de Admin informam quando um dataset não carregou.

### C3 — Checagem factual sobre queda do diesel em BH

- **Objetivo**: verificar a afirmação pública de que o preço médio do diesel em Belo Horizonte caiu 12% nos últimos 30 dias.
- **Fontes**:
  1. `diario_oficial_bh_diesel.xml` (feed XML consolidado pelo time jurídico, com reajustes publicados).
  2. `portal_transparencia_mg_combustivel.json` (API estadual com notas fiscais eletrônicas). 
  3. `anp_diesel_bh_30d.csv` (dados da ANP filtrados para BH e janela de 30 dias).
- **Fixtures**: `tests/fixtures/s9_checagem_factual/` contém snapshots assinados pelo Product Owner.
- **Query canônica**: `"O preço médio do diesel caiu 12% em Belo Horizonte nos últimos 30 dias?"` (`info_type=C3`, `claim_value=-12%`, `window_days=30`).
- **Resposta esperada**:
  - Texto declarando `Verdadeiro`, `Falso` ou `Indeterminado`, sempre explicando limites.
  - `summary_structured`: `claim`, `verdict`, `observed_delta_pct`, `num_sources`, `confidence`, `limitations`.
  - Evidências apontando para pelo menos dois registros (ex.: DO + ANP) e indicando eventuais lacunas na API estadual.
- **Observações**:
  - Falhas na leitura do Diário Oficial precisam ser refletidas para o usuário e logadas como `route="core"`, `kind="source_failure"`.
  - Se nenhuma fonte comprovar a queda, resposta deve marcar `Indeterminado` e detalhar a razão nos campos estruturados.

---

### Uso em gates

- **T4**: os goldens de `tests/goldens/s9_*.json` devem usar exatamente as queries acima e fixtures declaradas.
- **T5**: `scripts/s9_perf_runner.py` utiliza estes cenários para medir latência/p95 e throughput (30+ consultas por cenário).
- **T6**: `scripts/s9_evidence_auditor.py` percorre os ids gerados para cada cenário e verifica `meta.num_sources >= 2`.

Qualquer alteração estrutural em C1–C3 deve atualizar este arquivo, os fixtures correspondentes e os capítulos 1–4. Sem isso, o gate T0 falha automaticamente.
