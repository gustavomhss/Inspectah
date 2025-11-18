# Inspectah — Sprint 9  
## Capítulo 2 — Gates de Validação (T0–T8), Scorecards e Evidências (v2)

---

### 0. Princípios dos gates da Sprint 9

Este capítulo define **como a Sprint 9 prova que cumpriu o Capítulo 1**. Cada gate é um gargalo leonino: se o gate não passar, a sprint **não está pronta**, independentemente de "sensação" de progresso.

Princípios centrais:

1. Os gates T0–T8 existem para garantir que todas as **invariantes globais da S9** (Cap. 1) sejam verdadeiras em produção interna:
   - **Inv1** — nenhuma resposta sem trilha completa de evidência (QueryLog ↔ EvidenceBundle ↔ UserResponse);
   - **Inv2** — nenhum cenário oficial usando fonte única (sempre `meta.num_sources >= 2`);
   - **Inv3** — nenhuma decisão GPT fora do bundle;
   - **Inv4** — nenhum erro crítico silencioso.
2. Nenhum gate aceita meio‑termo: cada scorecard tem `status` binário **"PASS"** ou **"FAIL"** — não existem estados neutros.
3. Todos os gates são **reprodutíveis**: dados um repositório limpo e os comandos definidos aqui, qualquer membro do time deve conseguir reproduzir o resultado.
4. O **T8 (GO/NO_GO)** é puramente mecânico: lê scorecards T0–T7, aplica condições do Cap. 1 e deste capítulo, e decide GO apenas se tudo estiver verde.

Cada seção de gate abaixo explicita **quais invariantes globais ele protege diretamente**.

---

### 1. Convenções globais de arquivos, scorecards e evidências

1. Diretórios de evidência
   - Raiz: `out/evidence/`
   - Cada gate da S9 escreve em um subdiretório dedicado:  
     `out/evidence/S9_T0_scope/`, `out/evidence/S9_T1_static/`, ..., `out/evidence/S9_T8_go_no_go/`.

2. Diretório de scorecards
   - Raiz: `out/scorecards/`
   - Arquivos de scorecard por gate:  
     `out/scorecards/S9_T0_scope.json`,  
     `out/scorecards/S9_T1_static_quality.json`,  
     `out/scorecards/S9_T2_unit_and_contracts.json`,  
     `out/scorecards/S9_T3_property_and_edge_cases.json`,  
     `out/scorecards/S9_T4_golden_flows.json`,  
     `out/scorecards/S9_T5_perf_and_limits.json`,  
     `out/scorecards/S9_T6_logs_and_evidence.json`,  
     `out/scorecards/S9_T7_ci_pipeline.json`,  
     `out/scorecards/S9_T8_go_no_go.json`.

3. Formato mínimo de scorecard (todos os gates)

```json
{
  "gate": "S9_T4_golden_flows",
  "status": "PASS",
  "timestamp": "2025-XX-XXT12:34:56Z",
  "details": {
    "checks_ok": 5,
    "checks_failed": 0,
    "inv1_covered": true,
    "inv2_covered": true,
    "inv3_covered": false,
    "inv4_covered": true,
    "notes": "Resumo humano enxuto do que foi validado"
  }
}
```

- `status` deve ser **sempre** "PASS" ou "FAIL". Qualquer outro valor é erro de implementação.
- O script do gate deve sair com `exit 0` **apenas** se `status == "PASS"`.
- Os campos `inv*_covered` indicam explicitamente quais invariantes o gate audita.

4. Formato mínimo de summary (todos os gates)

```json
{
  "gate": "S9_T4_golden_flows",
  "description": "Descrição humana do objetivo do gate",
  "artifacts": [
    "lista de caminhos relevantes (queries, bundles, respostas, logs, métricas)"
  ],
  "notes": "Observações adicionais (limitações, decisões, TODO consciente)",
  "invariants": ["Inv1", "Inv2"]
}
```

5. Scripts padrão de gates

Todos os gates têm scripts em `bin/`, com padrão:

- `bin/s9_t0_scope_and_alignment.sh`
- `bin/s9_t1_static_quality.sh`
- `bin/s9_t2_unit_and_contracts.sh`
- `bin/s9_t3_property_and_edge_cases.sh`
- `bin/s9_t4_golden_flows.sh`
- `bin/s9_t5_perf_and_limits.sh`
- `bin/s9_t6_logs_and_evidence.sh`
- `bin/s9_t7_ci_pipeline.sh`
- `bin/s9_t8_go_no_go.sh`

Cada script:

1) resolve a raiz via `git rev-parse --show-toplevel` e faz `cd` para lá;
2) força `NET=0` (sem acesso externo);
3) gera summary + scorecard nos caminhos definidos;
4) sai com código 0 somente se o scorecard tiver `status` = "PASS".

---

### 2. Gate S9_T0 — Scope & Alignment

**Invariantes cobertas:** Inv1, Inv2, Inv3, Inv4 (no plano).

Objetivo: garantir que o **plano da Sprint 9 existe, está consistente e é rastreável**.

Escopo:

1. Verificar a presença e integridade básica dos documentos:
   - `docs/sprint_9_capitulo_1.md` (visão, invariantes, objetivos, DoD);
   - `docs/sprint_9_capitulo_2_gates.md` (este capítulo);
   - `docs/sprint_9_capitulo_3_arquitetura.md` (filemap, contratos);
   - `docs/sprint_9_capitulo_4_execucao.md` (fases, roteiro de demo);
   - qualquer arquivo de cenários oficiais (ex.: `docs/sprint_9_cenarios_demo.md`).

2. Checar que o Capítulo 1 contém, no mínimo:
   - as quatro invariantes globais da S9;
   - objetivos inegociáveis;
   - DoD com metas numéricas (erro < 2%, p95 ≤ 1,5 s etc.).

3. Checar que este Capítulo 2:
   - define T0–T8;
   - referencia explicitamente as invariantes e metas do Cap. 1;
   - mapeia quais gates cobrem quais invariantes.

Comando padrão:

- `PYTHONPATH=. bin/s9_t0_scope_and_alignment.sh`

Evidências mínimas:

- `out/evidence/S9_T0_scope/summary.json` descrevendo arquivos e seções verificados;
- `out/scorecards/S9_T0_scope.json` com `status` e contagem de checagens.

Critério de PASS:

1. Todos os arquivos esperados existem e são legíveis;
2. As invariantes globais e o DoD numérico estão presentes no Capítulo 1;
3. Este Capítulo 2 define T0–T8 e mapeia gates ↔ invariantes;
4. Qualquer ausência ou divergência relevante resulta em `status`: "FAIL".

---

### 3. Gate S9_T1 — Static Quality

**Invariantes cobertas:** protege principalmente Inv4 (evitar erros críticos mascarados por código mal cuidado) e prepara terreno para Inv1–Inv3.

Objetivo: garantir que a base de código da S9 está **coerente, compilável e sem problemas estáticos grosseiros**, antes de rodar testes.

Escopo mínimo:

1. Compilação de todos os módulos Python relevantes (`app/`, `tests/`, utilitários em `bin/` que importem Python):
   - utilização de `python -m compileall` ou equivalente.

2. Checagem de estilo básica e problemas óbvios:
   - importações não usadas, variáveis não utilizadas;
   - nenhum `print` de debug ou logging bruto em rotas/serviços centrais de S9 (Admin, User, GPT, observabilidade).

3. **Regra dura de TODO/FIXME:**
   - `0` ocorrências de `TODO` ou `FIXME` em qualquer arquivo tocado pela S9 sob `app/`, `tests/` e `bin/s9_*`;
   - TODOs legítimos devem estar documentados como dívida no Cap. 1 (seção de dívidas) ou no resumo da S9, não no código.

4. Checagem de segredos/acessos indevidos:
   - garantir que não há chaves, tokens ou conexões externas hardcoded nas partes da S9.

Comando padrão:

- `PYTHONPATH=. bin/s9_t1_static_quality.sh`

Evidências mínimas:

- `out/evidence/S9_T1_static/summary.json` com:
  - número de arquivos compilados;
  - número de problemas de lint/estilo detectados e corrigidos;
  - contagem de TODO/FIXME antes/depois (esperado 0 no final);
- `out/scorecards/S9_T1_static_quality.json` com `status` e contagens.

Critério de PASS:

1. Compilação completa sem erros;
2. Nenhum TODO/FIXME em código S9 (conforme regra acima);
3. Nenhum segredo exposto encontrado pelo scanner;
4. Falhas em qualquer ponto resultam em `status`: "FAIL".

---

### 4. Gate S9_T2 — Unit & Contracts

**Invariantes cobertas:** Inv1 (trilha do triplo), Inv2 (multi‑fonte via modelos/contratos), Inv3 (constrangimentos do client GPT), contribui para Inv4.

Objetivo: validar, via testes unitários e de contrato, que os **componentes centrais da S9** respeitam os contratos definidos no Cap. 1 e no Cap. 3.

Escopo mínimo de cobertura:

1. Núcleo de domínio e pipeline:
   - modelos da S9 (Admin v1, User v1, prompts especializados, evidência);
   - funções centrais do pipeline (parse, search, build bundle, run_pipeline com GPT mockado);
   - invariantes de criação do triplo `QueryLog` ↔ `EvidenceBundle` ↔ `UserResponse`.

2. Admin v1:
   - serviços de cadastro/edição/ativação de fontes;
   - status de fonte (último run, contagem de itens, erros recentes);
   - validações de campos obrigatórios.

3. User v1:
   - DTOs de entrada/saída;
   - roteamento básico de perguntas para o pipeline;
   - comportamento mínimo em caso de dados insuficientes ou pergunta fora de escopo.

4. GPT client (via mocks):
   - contratos de entrada e saída dos prompts especializados;
   - garantia de que, mesmo com mock, o pipeline mantém trilha de evidência.

Requisitos quantitativos mínimos:

- Pacote de testes S9_T2 deve conter **≥ 15 testes** distintos;
- Cada módulo central de S9 (Admin service, User service, pipeline, gpt_client) deve ter **≥ 2 testes unitários** associados;
- Summary de T2 deve listar, para cada teste ou grupo de testes, quais invariantes ele toca (`inv1`, `inv2`, `inv3`, `inv4`).

Comando padrão:

- `PYTHONPATH=. bin/s9_t2_unit_and_contracts.sh`  
  (internamente chamando `pytest tests/s9_t2_unit_contracts` ou equivalente)

Evidências mínimas:

- `out/evidence/S9_T2_unit_and_contracts/summary.json` com:
  - número de testes executados;
  - número de falhas;
  - mapa módulo→tests e teste→invariantes cobridas;
- `out/scorecards/S9_T2_unit_and_contracts.json` com `status`.

Critério de PASS:

1. 100% dos testes de S9_T2 passam;
2. Existem testes cobrindo explicitamente o triplo QueryLog/Bundle/UserResponse;
3. Existem testes cobrindo validações de Admin v1 e caminhos felizes de User v1 para cada tipo oficial (preço, comparação, fato);
4. O pacote atende os requisitos quantitativos mínimos (≥ 15 testes, ≥ 2 por módulo central);
5. Qualquer falha ou ausência relevante resulta em `status`: "FAIL".

---

### 5. Gate S9_T3 — Property & Edge Cases

**Invariantes cobertas:** Inv1 (continuidade do triplo em cenários de erro), Inv2 (impacto de multi‑fonte em bordas), Inv3 (bundle‑only sob stress), Inv4 (erros não silenciosos).

Objetivo: testar **propriedades do sistema e casos de borda**, garantindo que a S9 se comporta bem em cenários adversos.

Escopo mínimo:

1. Dados insuficientes:
   - queries válidas para as quais há menos dados que o necessário (ex.: uma única fonte, poucos itens na janela);
   - o sistema deve responder com mensagem de dados insuficientes, não inventar resposta.

2. Divergência forte entre fontes:
   - cenários em que duas fontes discordam significativamente;
   - o GPT deve refletir a divergência, ajustando confiança e explicando.

3. Erros de fonte:
   - simulações de fonte fora do ar ou esquema quebrado;
   - Admin deve sinalizar o problema; User deve refletir a falha de fonte relevante.

4. Perguntas fora de escopo:
   - queries que não se encaixam nos três tipos oficiais;
   - o sistema deve recusar educadamente ("fora de escopo"), sem tentar inventar resposta.

Requisitos quantitativos mínimos:

- Pacote S9_T3 deve conter **≥ 12 testes** de propriedade/borda;
- Deve haver **≥ 2 testes** para cada uma das quatro áreas (dados insuficientes, divergência forte, erro de fonte, fora de escopo);
- Summary de T3 deve explicitar para cada grupo de testes qual invariantes está sendo exercitada.

Comando padrão:

- `PYTHONPATH=. bin/s9_t3_property_and_edge_cases.sh`  
  (internamente chamando `pytest tests/s9_t3_property` ou equivalente)

Evidências mínimas:

- `out/evidence/S9_T3_property_and_edge_cases/summary.json` com descrição das propriedades testadas e resultados;
- `out/scorecards/S9_T3_property_and_edge_cases.json` com `status`.

Critério de PASS:

1. 100% dos testes de propriedade/casos de borda passam;
2. Há pelo menos 2 testes por área (dados insuficientes, divergência, erro de fonte, fora de escopo);
3. Nenhuma resposta de GPT, em testes de borda, viola Inv1–Inv4;
4. O pacote atende os requisitos quantitativos mínimos (≥ 12 testes);
5. Falhas resultam em `status`: "FAIL".

---

### 6. Gate S9_T4 — Golden Flows (Produto v0)

**Invariantes cobertas:** Inv1 (trilha completa, via goldens), Inv2 (multi‑fonte real por cenário), Inv3 (GPT disciplinado nos cenários oficiais).

Objetivo: garantir que os **três cenários oficiais da S9** funcionam de ponta a ponta como produto v0, e que esse comportamento está congelado em goldens.

Escopo:

1. Cenários oficiais (conforme Cap. 1 e docs de cenários):
   - C1: preço médio (agregação simples);
   - C2: comparação simples (ex.: onde está mais barato);
   - C3: checagem factual simples.

2. Para cada cenário, o gate deve:
   - preparar o ambiente via Admin (cadastrar/ativar fontes, rodar ingestão necessária);
   - executar a pergunta via User v1;
   - capturar QueryLog, EvidenceBundle, UserResponse;
   - comparar o resultado com goldens salvos em `tests/goldens/s9_*.json`.

Comando padrão:

- `PYTHONPATH=. bin/s9_t4_golden_flows.sh`  
  (internamente chamando, por exemplo, `pytest tests/s9_t4_golden_flows`)

Evidências mínimas:

- `out/evidence/S9_T4_golden_flows/summary.json` descrevendo execuções dos três cenários, caminhos dos bundles e respostas;
- `out/scorecards/S9_T4_golden_flows.json` com `status` e número de cenários verificados.

Critério de PASS:

1. Os três cenários oficiais executam sem erro;
2. As respostas batem com os goldens, ignorando apenas campos instáveis (IDs, timestamps) conforme regras de comparação definidas em teste;
3. Em todos os cenários oficiais, os bundles utilizados têm `meta.num_sources >= 2`;
4. Em todos os cenários oficiais, o resumo estruturado é coerente com o conteúdo do bundle;
5. Qualquer divergência não justificada resulta em `status`: "FAIL".

---

### 7. Gate S9_T5 — Performance, Estabilidade & Throughput

**Invariantes cobertas:** reforça Inv4 (sem sistema frágil que só funciona "com carinho") e protege a experiência de produto descrita no Cap. 1.

Objetivo: garantir que a experiência de produto v0 da S9 é **performática o suficiente**, estável e com throughput mínimo aceitável.

Escopo mínimo:

1. Latência de resposta para cenários oficiais:
   - para cada cenário (C1, C2, C3), executar pelo menos **50 consultas** em ambiente controlado (dev/CI);
   - medir p50 e p95 de latência do ponto de vista da User API.

2. Taxa de erro:
   - contabilizar respostas com erro inesperado (HTTP 5xx, exceções não tratadas) nesses 50 runs por cenário.

3. Estabilidade de resultado:
   - executar, para cada cenário, **3 rodadas de 10 queries idênticas** (mesmos parâmetros, mesmo ambiente);
   - verificar que o campo `summary_structured` das respostas é **idêntico** ou difere apenas dentro de uma faixa numérica mínima (tolerância definida nos testes), evidenciando que o GPT está configurado de forma determinística para esses fluxos.

4. Throughput mínimo:
   - executar um "mini‑carga" com pelo menos **30 queries por cenário** (90 no total) em um intervalo máximo de **2 minutos**;
   - verificar que o sistema mantém p95 e taxa de erro dentro das metas durante essa carga.

Metas numéricas (refinando o Cap. 1):

1. p95 de latência para cada cenário oficial **≤ 1,5 s**;
2. taxa de erro inesperado (5xx/exception) por cenário **< 2%** nas execuções do gate;
3. variância permitida em `summary_structured` entre rodadas repetidas deve estar dentro do intervalo definido nos testes (por padrão, igual ou diferença relativa ≤ 5% em valores numéricos).

Comando padrão:

- `PYTHONPATH=. bin/s9_t5_perf_and_limits.sh`

Evidências mínimas:

- `out/evidence/S9_T5_perf_and_limits/summary.json` com:
  - número de execuções por cenário;
  - p50/p95 por cenário;
  - taxa de erro por cenário;
  - resultados da checagem de estabilidade e throughput;
- `out/scorecards/S9_T5_perf_and_limits.json` com `status` e resumo das métricas.

Critério de PASS:

1. Em todos os cenários oficiais, p95 ≤ 1,5 s;
2. Em todos os cenários oficiais, taxa de erro inesperado < 2%;
3. Estabilidade de resultado atendida dentro das tolerâncias definidas;
4. Mini‑carga respeita as metas sem degradação grave;
5. Qualquer violação resulta em `status`: "FAIL".

---

### 8. Gate S9_T6 — Logs & Evidence Integrity

**Invariantes cobertas:** Inv1 (trilha completa), Inv2 (multi‑fonte garantida), Inv4 (sem erro crítico silencioso). Contribui para Inv3 ao checar coerência bundle↔resposta.

Objetivo: garantir que as invariantes de **trilha de evidência, multi‑fonte e ausência de erro silencioso** estão de pé na prática.

Escopo mínimo:

1. Reconstrução dos três cenários oficiais via Admin/User:
   - reexecutar C1, C2 e C3 usando o caminho canônico (Admin → ingestão → User);
   - capturar os `QueryLog` correspondentes.

2. Verificações obrigatórias por cenário:
   - para cada QueryLog considerado, localizar o `EvidenceBundle` e o `UserResponse` referenciados (arquivos reais em `out/evidence/s9_*`);
   - checar que `meta.num_sources >= 2` no bundle;
   - verificar que não há flags de erro crítico ignoradas (ex.: fonte marcada como falha, mas resposta tratada como normal);
   - garantir que os campos de resumo da resposta (valor, fontes, confiança) são coerentes com o bundle.

3. Amostragem adicional (opcional mas recomendada):
   - se houver queries extras executadas em testes exploratórios, o gate deve amostrar um subconjunto (por exemplo, 10%) para repetir as checagens acima.

Comando padrão:

- `PYTHONPATH=. bin/s9_t6_logs_and_evidence.sh`

Evidências mínimas:

- `out/evidence/S9_T6_logs_and_evidence/summary.json` listando todas as queries inspecionadas, IDs de bundle/resposta e invariantes verificadas;
- `out/scorecards/S9_T6_logs_and_evidence.json` com `status` e contagem de verificações (ex.: `queries_checked`, `triples_ok`, `triples_broken`).

Critério de PASS:

1. Para 100% das queries dos cenários oficiais inspecionadas, existe o triplo QueryLog ↔ EvidenceBundle ↔ UserResponse;
2. Para 100% destes bundles, `meta.num_sources >= 2`;
3. Não há evidência de erro crítico silencioso;
4. Amostragem adicional (se feita) não encontra violações;
5. Qualquer violação de 1, 2 ou 3 resulta em `status`: "FAIL".

---

### 9. Gate S9_T7 — CI Pipeline

**Invariantes cobertas:** reforça todas (Inv1–Inv4) ao garantir que T1–T6 rodam em CI.

Objetivo: garantir que tudo o que os gates T1–T6 fazem **também é executado automaticamente em CI**, protegendo o branch principal.

Escopo:

1. Script orquestrador da Sprint 9:
   - `bin/s9_ci.sh` chamando, em ordem, os gates T1–T6 (T0 pode ser manual/ocasional);
   - deve falhar se qualquer gate chamado falhar.

2. Workflow de CI da S9:
   - arquivo `.github/workflows/s9-ci.yml`:
     - dispara em `push`/`pull_request` para branches relevantes (em geral `main` + branches da S9);
     - provisiona Python e `.venv` conforme padrão do projeto;
     - seta `NET=0`;
     - executa `bin/s9_ci.sh` com `PYTHONPATH=.`.

3. Integração com proteções de branch:
   - o workflow S9‑CI deve ser marcado como obrigatório para merge em `main` (configuração de repositório, documentada no Cap. 4 ou no resumo da S9).

Comando padrão:

- `PYTHONPATH=. bin/s9_t7_ci_pipeline.sh`  
  (que por sua vez chama `bin/s9_ci.sh` e registra evidências)

Evidências mínimas:

- `out/evidence/S9_T7_ci_pipeline/summary.json` descrevendo:
  - comando executado;
  - quais gates foram rodados;
  - status de cada gate;
  - identificação do workflow de CI;
- `out/scorecards/S9_T7_ci_pipeline.json` com `status` e mapa gate→status.

Critério de PASS:

1. `bin/s9_ci.sh` executa T1–T6 e todos retornam PASS;
2. O workflow `.github/workflows/s9-ci.yml` existe e referencia `bin/s9_ci.sh` como etapa principal;
3. Evidência T7 registra que o workflow está ativo e configurado como obrigatório para merge (pode ser via marcação manual no summary);
4. Qualquer falha em T1–T6 ou ausência/misconfiguração do workflow resulta em `status`: "FAIL".

---

### 10. Gate S9_T8 — GO/NO‑GO

**Invariantes cobertas:** todas (Inv1–Inv4), por consolidação.

Objetivo: consolidar os resultados dos gates T0–T7 e emitir uma decisão **GO/NO_GO** para a Sprint 9.

Escopo:

1. Leitura de todos os scorecards da S9:
   - `out/scorecards/S9_T0_scope.json` até `out/scorecards/S9_T7_ci_pipeline.json`.

2. Aplicação das regras de decisão:
   - se qualquer gate tiver `status != "PASS"`, a decisão é **NO_GO**;
   - se todos os gates tiverem `status == "PASS"`, a decisão é **GO**;
   - opcionalmente, o script pode verificar rapidamente se os critérios numéricos chave do Cap. 1 (p95, erro < 2%, multi‑fonte etc.) aparecem como atendidos nos summaries T4–T6.

3. Integração com resumo humano da S9:
   - verificação da presença de `docs/sprint_9_summary.md`, contendo quadro dos gates T0–T8 e entregáveis da sprint;
   - se o resumo estiver ausente ou inconsistente com os scorecards, o gate considera NO_GO.

Comando padrão:

- `PYTHONPATH=. bin/s9_t8_go_no_go.sh`

Evidências mínimas:

- `out/evidence/S9_T8_go_no_go/summary.json` incluindo:
  - mapa gate→status (T0–T7);
  - decisão final (`"decision": "GO"` ou `"decision": "NO_GO"`);
  - referência ao `docs/sprint_9_summary.md`;
  - invariantes cobertas e como foram observadas;
- `out/scorecards/S9_T8_go_no_go.json` com campos `gate`, `status` e `decision`.

Critério de PASS:

1. Todos os scorecards S9_T0…S9_T7 têm `status`: "PASS";
2. O arquivo `docs/sprint_9_summary.md` existe e reflete uma decisão GO coerente com os scorecards;
3. O scorecard S9_T8 registra `decision`: "GO" e `status`: "PASS";
4. Qualquer falha em 1, 2 ou inconsistência entre resumo e scorecards resulta em `status`: "FAIL" e `decision`: "NO_GO".

---

### 11. Relação com os demais capítulos da S9

- O **Capítulo 1** define o porquê: visão, invariantes, objetivos e metas numéricas.  
- Este **Capítulo 2** define o como provar: gates T0–T8, scorecards, metas mínimas e evidências.  
- O **Capítulo 3** definirá onde e em quais componentes cada gate atua (arquitetura, filemap, contratos de módulo).  
- O **Capítulo 4** definirá quando e em que ordem os gates são ativados ao longo da sprint (fases, automações, roteiro de demo).

A Sprint 9 só pode ser declarada **concluída** quando:

1. Todos os gates T0–T8 estiverem com `status`: "PASS";
2. A decisão T8 for "GO";
3. O resumo da S9 documentar explicitamente que os critérios de sucesso do Cap. 1 foram atingidos e comprovados pelas evidências deste capítulo.

