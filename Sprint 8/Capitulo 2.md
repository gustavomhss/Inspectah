# Inspectah – Sprint 8 (Capítulo 2)
## Gates de Validação T0–T8 — Gargalo Máximo de Qualidade (v2)

---

### 0. One‑liner oficial do Capítulo 2

> **“Os gates T0–T8 da Sprint 8 são o gargalo leonino que transforma o Capítulo 1 em código vivo: só passa para ‘Done’ aquilo que prova, com evidência e scorecard, que Admin, Usuário e o fluxo Inspectah → Evidências → GPT → Resposta funcionam de ponta a ponta, sem alucinação e 100% rastreáveis.”**

Capítulo 2 converte a visão da Sprint 8 (Cap. 1 v4) em **contratos executáveis**. Cada gate T0–T8 tem:

- propósito único e bem definido
- pré‑condições e pós‑condições formais (Design by Contract)
- entradas e saídas esperadas (incluindo paths de arquivos)
- exemplo de comando para execução
- formato mínimo de `summary.json` e `scorecard`
- critério GO/NO‑GO binário

Se qualquer gate falhar, o estado da Sprint 8 é **NO‑GO** até que o problema seja corrigido, o gate reexecute e o scorecard volte a PASS.

---

### 1. Padrão geral de execução, evidência e scorecards

Todos os gates seguem o mesmo padrão operacional.

1. **Execução**

Cada gate tem um script único em `bin/`:

- `bin/s8_t0_scope_and_alignment.sh`
- `bin/s8_t1_static_quality.sh`
- `bin/s8_t2_unit_and_contracts.sh`
- `bin/s8_t3_property_and_edge_cases.sh`
- `bin/s8_t4_golden_flows.sh`
- `bin/s8_t5_perf_and_limits.sh`
- `bin/s8_t6_logs_and_evidence.sh`
- `bin/s8_t7_ci_pipeline.sh`
- `bin/s8_t8_go_no_go.sh`

Cada script deve:

- abortar com `exit != 0` se qualquer pré‑condição obrigatória falhar
- executar todos os checks do gate
- escrever evidências em `out/evidence/S8_T*/`
- escrever o scorecard em `out/scorecards/S8_T*.json`

Exemplo de execução isolada de um gate

```bash
PYTHONPATH=. bin/s8_t4_golden_flows.sh
```

2. **Estrutura de evidência**

Para cada gate Tn:

- pasta base: `out/evidence/S8_Tn_<nome>/`
- arquivos mínimos:
  - `summary.json`
  - `MANIFEST.json`

Exemplo mínimo de `summary.json`

```json
{
  "gate_id": "S8_T4_golden_flows",
  "status": "PASS",
  "checks_total": 12,
  "checks_passed": 12,
  "checks_failed": 0,
  "timestamp": "2025-xx-xxT12:34:56Z",
  "notes": [
    "cenarios: preco_medio, comparacao_simples, checagem_factual_simples",
    "tolerancias: apenas em datas/ids tecnicos"
  ]
}
```

Exemplo mínimo de `MANIFEST.json`

```json
{
  "gate_id": "S8_T4_golden_flows",
  "artifacts": [
    "tests/goldens/s8_preco_medio.json",
    "tests/goldens/s8_comparacao_simples.json",
    "tests/goldens/s8_checagem_factual.json",
    "out/evidence/s8_queries/demo_preco_medio.json"
  ]
}
```

3. **Estrutura de scorecard**

Scorecard mínimo por gate:

```json
{
  "gate_id": "S8_T4_golden_flows",
  "status": "PASS",
  "checks_total": 12,
  "checks_passed": 12,
  "checks_failed": 0,
  "inputs": {
    "branch": "feature/s8",
    "commit": "<sha>",
    "runner": "local"
  },
  "outputs": {
    "evidence_dir": "out/evidence/S8_T4_golden_flows",
    "summary_file": "out/evidence/S8_T4_golden_flows/summary.json"
  }
}
```

- `status` ∈ {`"PASS"`, `"FAIL"`}
- qualquer falha em check relevante obriga `status: "FAIL"` + `exit != 0`

---

### 2. Gate T0 — Scope & Alignment

Objetivo

Garantir que o time está alinhado com o escopo e que a Sprint 8 está ancorada em documentos estáveis (Cap. 1 v4 + este Cap. 2), com cenários de demo claramente descritos.

Cobertura de Cap. 1

- objetivos de S8 (Admin v0, Usuário v0, fluxo GPT ancorado, 3 demos)
- não‑objetivos explícitos (Truth‑DB completa, blockchain, comunidade, scheduler complexo)

Pré‑condições

- arquivo `docs/sprint_8_capitulo_1.md` existe e é a versão v4 (hash esperado definido em constante do script)
- arquivo `docs/sprint_8_capitulo_2_gates.md` mapeia T0–T8 (hash esperado da v2)
- arquivo `docs/sprint_8_cenarios_demo.md` descreve claramente os 3 cenários oficiais

Pós‑condições (PASS)

- `summary.json` contém
  - hashes atuais de Cap. 1, Cap. 2 e `cenarios_demo`
  - veredito de compatibilidade (`"aligned": true`)
- `status` do scorecard T0 é `"PASS"`

Checks mínimos

- validação de presença e hash de cada doc
- verificação de que `docs/sprint_8_cenarios_demo.md` contém seções para
  - `preco_medio`
  - `comparacao_simples`
  - `checagem_factual_simples`

Comando típico

```bash
PYTHONPATH=. bin/s8_t0_scope_and_alignment.sh
```

GO/NO‑GO

- qualquer documento faltando ou hash divergente ⇒ `FAIL`
- não existe WARN; ou está alinhado, ou a sprint não inicia

---

### 3. Gate T1 — Static Quality (Árvore, Estilo, Segurança básica)

Objetivo

Garantir que a base de código da Sprint 8 é saudável (estrutura, imports, lint, segredos) antes de rodar qualquer fluxo dinâmico.

Pré‑condições

- T0 em `PASS`
- diretórios mínimos criados
  - `app/admin/`, `app/user/`, `app/core/`, `app/gpt_client/`, `bin/`, `out/`

Pós‑condições (PASS)

- árvore de diretórios bate com layout esperado (ao menos os módulos da S8)
- lint/format das partes da S8 roda sem erro
- não há segredos evidentes hardcoded (tokens, chaves privadas)

Checks mínimos

- script T1 executa, por exemplo:

```bash
python -m compileall app
ruff app  # ou flake8 equivalente
python scripts/scan_secrets.py  # heurística simples
```

- `summary.json` lista
  - ferramentas usadas
  - arquivos problemáticos (se houver)

Comando típico

```bash
PYTHONPATH=. bin/s8_t1_static_quality.sh
```

GO/NO‑GO

- qualquer erro de compilação/lint ou flag de segredo ⇒ `FAIL`

---

### 4. Gate T2 — Unit & Contracts (Pipeline Interno)

Objetivo

Validar que o pipeline interno “pergunta → classificação → busca interna → evidence bundle” respeita os contratos de entrada/saída definidos no Cap. 1 v4, sem envolver GPT.

Pré‑condições

- T1 em `PASS`
- módulos centrais implementados
  - `app/core/query_parser.py`
  - `app/core/search_internal.py`
  - `app/core/evidence_bundle_builder.py`

Contratos mínimos

- Pré
  - pergunta não vazia
  - idioma suportado (PT/EN)
- Pós
  - tipo de pergunta ∈ {`agregacao_simples`, `comparacao_simples`, `checagem_factual_simples`}
  - evidence bundle com
    - `evidence_bundle_id`
    - `query_type`
    - `filters` básicos
    - lista de itens por fonte (até N)

Checks mínimos

- test suite T2, ex.: `pytest tests/s8_t2_unit_contracts/` cobrindo
  - parsing de frases típicas e borderline
  - buscas em fixtures de fonte
  - formatação do evidence bundle

Exemplo de caso de teste esperado (alto nível)

- input: “Qual o preço médio do arroz em São Paulo?”
- output (parsing)
  - `query_type = "agregacao_simples"`
  - `produto = "arroz"`, `cidade = "São Paulo"`

Comando típico

```bash
PYTHONPATH=. bin/s8_t2_unit_and_contracts.sh
```

GO/NO‑GO

- qualquer teste relevante falhando ⇒ `FAIL`

---

### 5. Gate T3 — Property & Edge Cases (Anti‑Alucinação e Limites)

Objetivo

Exercitar o pipeline em cenários adversos para garantir comportamento seguro: dados insuficientes, conflitos extremos, perguntas fora de escopo.

Pré‑condições

- T2 em `PASS`

Propriedades alvo

- se `num_itens_relevantes == 0` ⇒ pipeline marca `dados_insuficientes` (ou equivalente) e **não** tenta gerar evidência enganosa
- se `num_fontes_total == 1` e fonte marcada como baixa confiabilidade (em fixture) ⇒ a saída de meta‑dados reflete baixa confiança
- se pergunta é claramente fora de escopo (previsão do futuro, opinião, etc.) ⇒ pipeline marca `fora_de_escopo`

Checks mínimos

- tests property‑like, ex.: `pytest tests/s8_t3_property/`
- `summary.json` deve listar propriedades validadas

Comando típico

```bash
PYTHONPATH=. bin/s8_t3_property_and_edge_cases.sh
```

GO/NO‑GO

- qualquer violação de propriedade ⇒ `FAIL`

---

### 6. Gate T4 — Golden Flows (Demos oficiais da Sprint 8)

Objetivo

Garantir, de forma determinística, que os 3 roteiros oficiais de demo funcionam de ponta a ponta (Admin → ingestão → Usuário → GPT → resposta + evidências).

Pré‑condições

- T3 em `PASS`
- fixtures de fontes disponíveis, ex.:
  - `tests/fixtures/s8_preco_medio/*.json`
  - `tests/fixtures/s8_comparacao/*.json`
  - `tests/fixtures/s8_checagem_factual/*.json`

Escopo

- Cenário 1: Preço médio
- Cenário 2: Comparação simples
- Cenário 3: Checagem factual simples

Formato de golden

- goldens em JSON contendo:
  - campos principais da resposta textual (ou snapshot representativo)
  - resumo estruturado
  - meta‑dados de evidência importantes

Exemplos

- `tests/goldens/s8_preco_medio.json`
- `tests/goldens/s8_comparacao_simples.json`
- `tests/goldens/s8_checagem_factual.json`

Checks mínimos

- script T4 executa cada cenário de forma automatizada (usando mocks/APIs internas, não cliques manuais) e
  - compara saída atual com golden
  - permite tolerância apenas em campos marcados (ex.: datas técnicas, IDs)

Comando típico

```bash
PYTHONPATH=. bin/s8_t4_golden_flows.sh
```

GO/NO‑GO

- qualquer diff não justificado entre saída e golden ⇒ `FAIL`
- atualizar goldens só é permitido via processo revisado (PR + justificativa), nunca para mascarar bug

---

### 7. Gate T5 — Performance & Limites

Objetivo

Garantir que a experiência não seja sofrível: latência razoável e evidence bundles em tamanhos aceitáveis para os 3 cenários.

Pré‑condições

- T4 em `PASS`

Metas de exemplo (ajustáveis, mas fixadas em doc)

- p95 da latência total por cenário em ambiente local ≤ 5 s
- tamanho médio do evidence bundle ≤ X kB / Y itens (por tipo de pergunta)

Checks mínimos

- script T5 executa cada cenário N vezes (ex.: 5–10) e mede
  - tempo de
    - parsing + busca + bundle
    - chamada GPT
    - resposta renderizada
  - tamanho dos bundles

`summary.json` deve trazer

- p50/p95 de latência por cenário
- média de tamanho de bundle

Comando típico

```bash
PYTHONPATH=. bin/s8_t5_perf_and_limits.sh
```

GO/NO‑GO

- qualquer cenário com p95 muito acima da meta ou bundles descontrolados ⇒ `FAIL`

---

### 8. Gate T6 — Logs & Evidências (Rastreabilidade)

Objetivo

Garantir que cada pergunta relevante da Sprint 8 deixa trilha completa: pergunta, tipo, bundle, fontes/itens, resposta, timestamp, status.

Pré‑condições

- T5 em `PASS`

Estrutura mínima de storage

- `out/evidence/s8_queries/*.json`
- `out/evidence/s8_bundles/*.json`

Formato mínimo de registro de query

```json
{
  "query_id": "s8_demo_preco_medio_001",
  "user_query": "Qual o preço médio de X em Y?",
  "query_type": "agregacao_simples",
  "evidence_bundle_id": "bundle_abc123",
  "sources": ["fonte_precos_sp"],
  "items_used": ["item1", "item2", "item3"],
  "gpt_response_ref": "out/evidence/s8_queries_respostas/s8_demo_preco_medio_001.json",
  "timestamp": "2025-xx-xxT12:00:00Z",
  "status": "ok"
}
```

Checks mínimos

- para cada execução dos 3 cenários oficiais (em T4/T5), existe
  - 1 registro de query
  - 1 bundle correspondente
  - referência cruzada consistente entre query ↔ bundle ↔ resposta

Comando típico

```bash
PYTHONPATH=. bin/s8_t6_logs_and_evidence.sh
```

GO/NO‑GO

- qualquer buraco (query sem bundle, bundle sem resposta ou sem fontes) ⇒ `FAIL`

---

### 9. Gate T7 — CI Pipeline (Repetibilidade)

Objetivo

Garantir que T1–T6 podem ser repetidos de forma automatizada, em ambiente local e em CI remoto (ex.: GitHub Actions).

Pré‑condições

- T6 em `PASS`

Requisitos

- script agregador

```bash
bin/s8_ci.sh
```

- esse script deve, no mínimo
  - rodar T1–T6 em sequência
  - falhar se qualquer gate falhar

- workflow de CI
  - arquivo em `.github/workflows/s8-ci.yml` ou equivalente
  - dispara em PRs/commits relevantes
  - executa `bin/s8_ci.sh`

Checks mínimos

- T7 roda `bin/s8_ci.sh` localmente e verifica
  - criação/atualização de scorecards T1–T6
  - status geral

Comando típico

```bash
PYTHONPATH=. bin/s8_t7_ci_pipeline.sh
```

GO/NO‑GO

- ausência de CI ou CI quebrado ⇒ `FAIL`

---

### 10. Gate T8 — GO/NO‑GO Final da Sprint 8

Objetivo

Consolidar o estado de T0–T7 e emitir um veredito final **binário** sobre a Sprint 8.

Pré‑condições

- T0–T7 executados e com scorecards presentes

Pós‑condições (PASS)

- `out/scorecards/S8_T0_scope.json` … `S8_T7_ci.json` existem e têm `status: "PASS"`
- `out/evidence/S8_T8_go_no_go/summary.json` contém
  - lista dos gates considerados
  - estado de cada gate
  - `decision: "GO"`

Regras de decisão

- se qualquer T0–T7 estiver em `"FAIL"` ⇒ `decision: "NO_GO"`
- não existe “GO com ressalvas”; ressalvas vão para backlog, mas não mudam o veredito

Comando típico

```bash
PYTHONPATH=. bin/s8_t8_go_no_go.sh
```

Exemplo de `summary.json` (T8)

```json
{
  "gate_id": "S8_T8_go_no_go",
  "status": "PASS",
  "decision": "GO",
  "gates": {
    "S8_T0_scope": "PASS",
    "S8_T1_static": "PASS",
    "S8_T2_unit_contracts": "PASS",
    "S8_T3_property": "PASS",
    "S8_T4_golden_flows": "PASS",
    "S8_T5_perf": "PASS",
    "S8_T6_logs_evidence": "PASS",
    "S8_T7_ci": "PASS"
  },
  "timestamp": "2025-xx-xxT18:00:00Z",
  "notes": [
    "demos executadas com sucesso",
    "nenhum buraco de rastreabilidade identificado"
  ]
}
```

---

### 11. Mapeamento objetivo → gate (checagem de cobertura)

Admin v0 funcional (cadastro de fontes, campos relevantes, status de ingestão)

- T1 — estrutura de código/Admin
- T2/T3 — comportamento de ingest/parse em testes
- T4 — demos que começam no Admin
- T6 — logs de ingestão

Usuário v0 funcional (pergunta NL + resposta + resumo + evidências)

- T2/T3 — pipeline interno e contratos
- T4 — goldens de fluxo completo
- T5 — latência aceitável
- T6 — rastreabilidade das respostas

Pipeline Inspectah → Evidências → GPT → Resposta (sem web, anti‑alucinação)

- T2 — contratos de entrada/saída
- T3 — edge cases e dados insuficientes
- T4 — comportamento real com GPT
- T6 — logs/bundles para auditoria

Três cenários de demo oficiais

- T0 — descrição formal
- T4 — goldens por cenário
- T5 — performance por cenário

Rastreabilidade & preparação para Truth‑DB/blockchain/comunidade

- T6 — evidências completas, IDs, bundles, paths
- T7 — CI garantindo repetibilidade
- T8 — veredito final baseado em scorecards

Nenhum objetivo crítico do Cap. 1 fica sem gate correspondente. Vários objetivos têm **sobreposição deliberada** de gates, para reduzir risco de cegueira.

---

### 12. Barra de qualidade específica do Capítulo 2 (v2)

- Rigor extremo: cada gate faz algo que nenhum outro gate faz, sem redundância inútil.
- Executabilidade: qualquer pessoa com acesso ao repo consegue implementar `bin/s8_t*.sh` e testes correspondentes apenas lendo este capítulo.
- Leoninidade real: gates são projetados para falhar rápido e com clareza; “passar raspando” não é aceitável.
- Alinhamento: qualquer mudança significativa no Cap. 1 exige revisão coordenada deste Cap. 2 e dos scripts, nunca apenas “gambiarras” no código.

Este Capítulo 2 v2 é a versão de referência para validação da Sprint 8. Ele deve ser tratado como **contrato de qualidade**: enquanto não houver scorecards T0–T8 em `PASS` baseados nesses critérios, a Sprint 8 não está concluída.

