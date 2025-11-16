# Inspectah — Sprint 4 — Capítulo 2  
**Gates de Validação — Blueprint 10/10 (State of the Art)**

> Este capítulo define a **máquina de estados de qualidade** da Sprint 4. O Capítulo 1 diz o que a sprint precisa ser; o Capítulo 2 diz **como provar**, com gates T0–T8, que chegamos lá. Qualquer coisa construída na S4 existe para **encaixar nesses gates**.

---

## 0. Como ler este capítulo

- **PO:** usa este capítulo como contrato de validação. Se algo importante não estiver coberto por algum gate, isso é um bug de especificação.  
- **Codex / Engenheiros:** tratam cada gate como um "mini‑produto" com entrada, saída, artefatos obrigatórios e regras claras.  
- **Comitê / Revisores:** usam este capítulo para checar se os artefatos entregues cobrem os invariantes e SLOs da Sprint 4.

Nada é considerado "pronto" na S4 se não existir **pelo menos um gate** que o valide.

---

## 1. Papel dos gates na Sprint 4

- Responder, de forma objetiva: **“a Sprint 4 entregou o Inspectah vivo, confiável e mensurável, como prometido no Capítulo 1?”**  
- Servir como **gargalo absoluto de qualidade**: se um gate crítico está vermelho, o T8 é moralmente obrigado a ser NO_GO.  
- Tornar rastreável a relação entre:  
  - invariantes de produto;  
  - SLOs;  
  - artefatos em disco;  
  - decisão final de GO/NO_GO.

---

## 2. Regras gerais para todos os gates (T0–T8)

1. **Entrada bem definida**  
   Cada gate tem uma lista explícita de insumos (arquivos, configs, fixtures, comandos). Sem isso, o gate não existe.

2. **Saída padronizada (scorecards)**  
   Todo gate gera um scorecard JSON em `out/scorecards/` com, no mínimo:
   - `gate_id` (ex.: "S4_T3")  
   - `gate_name`  
   - `status`: `"PASS"`, `"FAIL"` ou `"NO_RUN"`  
   - métricas principais do gate  
   - lista de erros/lacunas, se houver

3. **Evidências persistidas**  
   Cada gate grava evidências em `out/evidence/` sob um diretório próprio (ex.: `out/evidence/S4_T3_fixtures/`). Logs, relatórios, snapshots, manifestos.

4. **Determinismo em contexto fixo**  
   Duas execuções consecutivas do mesmo gate, com o mesmo contexto de entrada, produzem scorecards equivalentes (ou diferenças justificadas e registradas).

5. **Acoplamento a invariantes e SLOs**  
   Nenhum gate existe “no vazio”: cada um aponta explicitamente quais invariantes e/ou SLOs ajuda a provar.

6. **Sem bypass manual**  
   `status = "PASS"` só pode ser obtido pela lógica do gate. Não existe edição manual de scorecard para “verde forçado”.

7. **Nomenclatura canônica de artefatos**  
   Os caminhos indicados neste capítulo são o padrão. Se o Codex propuser variação, precisa atualizar este documento e o Capítulo 1.

---

## 3. Grafo de dependências entre gates e regra de curto‑circuito

### 3.1 Ordem e dependência explícita

- A execução lógica dos gates segue a cadeia:  
  **T0 → T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8**

- Dependências fortes (se o anterior falha, o próximo está comprometido):
  - T1 depende de T0 (sem alinhamento, o modelo pode estar errado).  
  - T2 depende de T1 (configurar fonte sem entender dados é erro).  
  - T3/T4/T5 dependem de T2 (sem registry correto, fixtures e goldens podem ser inválidos).  
  - T6 depende de T3–T5 (observabilidade só é séria se o pipeline básico não estiver quebrado).  
  - T7 depende de todos os anteriores (integração não vale se os bricks estão errados).  
  - T8 depende de T0–T7.

### 3.2 Regra de curto‑circuito

Para efeitos de decisão de sprint (T8):

- Se **qualquer gate obrigatório** T0–T7 estiver `"FAIL"`, o T8 deve, por padrão, decidir `"NO_GO"`, a menos que haja uma **decisão explícita de exceção**, documentada no wrap humano.  
- Se um gate está `"NO_RUN"` por falta de pré‑requisitos, o T8 deve tratá‑lo como `"FAIL"`, exceto se houver justificativa formal (por exemplo, gate marcado como não aplicável para esta sprint).

Em outras palavras: **não existe GO com gates críticos vermelhos ou não executados sem justificativa formal.**

---

## 4. Visão em uma página — T0–T8

| Gate | Pergunta que responde | Risco principal que elimina |
|------|------------------------|-----------------------------|
| **T0** | Podemos começar a Sprint 4? | Iniciar com escopo ou pré‑requisitos nebulosos |
| **T1** | Entendemos dados, camadas, objetos e invariantes? | Construir sem modelo mental sólido |
| **T2** | O registro das Fontes P0 é correto e seguro? | Fontes mal definidas ou com segredos em código |
| **T3** | Parsers/normalizadores entendem dados reais? | Pipeline quebrando na primeira entrada real |
| **T4** | O comportamento para dados reais é estável? | Regressões silenciosas e drift inesperado |
| **T5** | O Vault aguenta repetição sem corromper? | Corrupção/duplicação de evidência, vazamentos |
| **T6** | Conseguimos ver a saúde das Fontes P0? | Fontes "fantasmas" ou invisíveis à operação |
| **T7** | A pipeline S4 é reprodutível ponta a ponta? | Integração frágil, dependências ocultas |
| **T8** | A Sprint 4 merece GO? | Declarar vitória sem respeitar invariantes, SLOs e DoD |

---

## 5. Mapa gate → artefatos obrigatórios

Resumo rápido por gate (detalhes nas seções seguintes):

- **T0**  
  - `docs/sprint_4_t0_checklist.md`  
  - `out/scorecards/S4_T0_discovery.json`

- **T1**  
  - `docs/sprint_4_modelo_dados_invariantes.md`  
  - `docs/sprint_4_invariantes_matriz_gates.md`  
  - `out/scorecards/S4_T1_specs.json`

- **T2**  
  - `config/sources/sprint_4/fontes_p0/*.yaml` (ou equivalente)  
  - `config/field_designer/sprint_4/*.yaml`  
  - `out/evidence/S4_T2_sources/validation.log`  
  - `out/scorecards/S4_T2_sources.json`

- **T3**  
  - `fixtures/sprint_4/fontes_p0/<source_id>/*.json|*.xml|*.html|...`  
  - `tests/sprint_4/T3_*.spec.*` (testes cobrindo fixtures)  
  - `out/evidence/S4_T3_fixtures/report.txt`  
  - `out/scorecards/S4_T3_fixtures.json`

- **T4**  
  - `goldens/sprint_4/fontes_p0/<source_id>/*.json`  
  - `out/evidence/S4_T4_goldens/report.txt`  
  - `out/scorecards/S4_T4_goldens.json`

- **T5**  
  - `out/evidence/S4_T5_repetition/vault_snapshot_before.json`  
  - `out/evidence/S4_T5_repetition/vault_snapshot_after.json`  
  - `out/evidence/S4_T5_repetition/vault_diff.txt`  
  - `out/scorecards/S4_T5_repetition.json`

- **T6**  
  - `out/evidence/S4_T6_observability/metrics_snapshot.json`  
  - `out/evidence/S4_T6_observability/logs_sample.log`  
  - `out/evidence/S4_T6_observability/health_matrix.json`  
  - `out/scorecards/S4_T6_observability.json`

- **T7**  
  - `out/evidence/S4_T7_integration/orr_run.log`  
  - `out/evidence/S4_T7_integration/scorecards_index.json`  
  - `out/scorecards/S4_T7_integration.json`

- **T8**  
  - `out/scorecards/S4_T8_go_no_go.json`  
  - `docs/sprint_4_orr_summary.md`

---

## 6. Especificação gate a gate (T0–T8)

### 6.1 T0 — Descoberta e alinhamento

**Objetivo:** só iniciar a S4 se o terreno estiver firme.

- **Entrada:** Capítulo 1 v5, wrap S3, lista proposta de Fontes P0.  
- **Perguntas:** fontes P0 estão definidas? personas/cenários S4 são compreendidos? ORR S3 está estável?  
- **Processo:** checklist estruturado, revisto por PO + time.

**Critérios de PASS:**
- Checklist sem itens críticos em aberto.  
- Riscos bloqueantes ou removidos do escopo, ou mitigados explicitamente.

**Artefatos obrigatórios:**
- `docs/sprint_4_t0_checklist.md`  
- `out/scorecards/S4_T0_discovery.json`

**Invariantes/SLOs relacionados:**
- Prepara terreno para **onboarding_p50_min** (definindo P0).  
- Garantia de que ninguém está construindo fora da visão do Capítulo 1.

---

### 6.2 T1 — Especificação de dados e invariantes

**Objetivo:** impedir que a implementação avance sem modelo mental sólido.

- **Entrada:** Capítulo 1 v5, rascunho do modelo de dados.  
- **Perguntas:** camadas/objetos/relacionamentos estão claros? invariantes têm donos (gate + evidência)?

**Critérios de PASS:**
- Objetos Fonte, Run, Item, Evidência, Consulta descritos com campos obrigatórios.  
- 100% das invariantes do Capítulo 1 mapeadas para pelo menos um gate e um tipo de evidência.

**Artefatos obrigatórios:**
- `docs/sprint_4_modelo_dados_invariantes.md`  
- `docs/sprint_4_invariantes_matriz_gates.md`  
- `out/scorecards/S4_T1_specs.json`

**Invariantes ligados:**
- "Toda Evidência P0 rastreável à Fonte e ao Run" (estrutura e relacionamentos).  
- "Fixtures do ORR vêm de dados reais e são versionadas" (origem dos dados).

---

### 6.3 T2 — Configuração e registro de fontes

**Objetivo:** garantir que Fontes P0 e Field Designer estão corretos e seguros.

- **Entrada:**  
  - `config/sources/sprint_4/fontes_p0/*.yaml`  
  - `config/field_designer/sprint_4/*.yaml`

- **Perguntas:** registry das Fontes P0 está completo? sem segredos em texto plano? Field Designer cobre campos de interesse?

**Critérios de PASS:**
- 100% das Fontes P0 com campos obrigatórios presentes e tipos corretos.  
- Zero segredos em arquivos de configuração.  
- Todos os campos de interesse usados na S4 definidos no Field Designer.

**Artefatos obrigatórios:**
- `out/evidence/S4_T2_sources/validation.log`  
- `out/scorecards/S4_T2_sources.json`

**Invariantes ligados:**
- "Nenhum ajuste estrutural em Fonte P0 apenas em código".  
- Base para qualquer cálculo de **onboarding_p50_min**.

---

### 6.4 T3 — Testes com fixtures reais

**Objetivo:** provar que o Inspectah entende dados reais.

- **Entrada:**  
  - `fixtures/sprint_4/fontes_p0/<source_id>/*`  
  - `tests/sprint_4/T3_*.spec.*`

- **Perguntas:** cada Fonte P0 tem fixtures reais? parsers/normalizadores extraem os campos corretos? erros são visíveis?

**Critérios de PASS:**
- 100% dos testes para fixtures das Fontes P0 em PASS.  
- Nenhum erro silencioso; falhas têm mensagens claras.

**Artefatos obrigatórios:**
- `out/evidence/S4_T3_fixtures/report.txt`  
- `out/scorecards/S4_T3_fixtures.json`

**Invariantes/SLOs ligados:**
- "Nenhum Item P0 sem Evidência completa" (fixtures → itens + evidência).  
- Base para **evidence_completeness_rate**.

---

### 6.5 T4 — Goldens estáveis

**Objetivo:** impedir regressões silenciosas em dados reais.

- **Entrada:**  
  - `goldens/sprint_4/fontes_p0/<source_id>/*.json`  
  - fixtures T3

- **Perguntas:** dadas fixtures reais, o pipeline produz sempre o mesmo resultado? mudanças internas são rastreáveis?

**Critérios de PASS:**
- 100% das comparações fixture → golden sem divergências relevantes, ou divergências acompanhadas de explicação e atualização aprovada pelo PO.

**Artefatos obrigatórios:**
- `out/evidence/S4_T4_goldens/report.txt`  
- `out/scorecards/S4_T4_goldens.json`

**Invariantes ligados:**
- "Nenhum Item P0 sem Evidência completa" (goldens incorporam evidência).  
- "Fixtures do ORR vêm de dados reais e são versionadas".

---

### 6.6 T5 — Comportamento sob repetição

**Objetivo:** garantir que o Vault não se destrói com o uso.

- **Entrada:** fixtures/goldens estáveis; mecanismo de snapshot do Vault.

- **Perguntas:** execuções repetidas criam duplicações, perdas ou crescimento absurdo de dados?

**Critérios de PASS:**
- Nenhuma perda de Evidência.  
- Nenhuma duplicação injustificada.  
- Crescimento do Vault compatível com o número de execuções.

**Artefatos obrigatórios:**
- `out/evidence/S4_T5_repetition/vault_snapshot_before.json`  
- `out/evidence/S4_T5_repetition/vault_snapshot_after.json`  
- `out/evidence/S4_T5_repetition/vault_diff.txt`  
- `out/scorecards/S4_T5_repetition.json`

**Invariantes/SLOs ligados:**
- "Nenhum Item P0 sem Evidência completa" (sem perdas).  
- Support para **evidence_completeness_rate** sob repetição.

---

### 6.7 T6 — Observabilidade

**Objetivo:** tornar a saúde das Fontes P0 visível e mensurável.

- **Entrada:**  
  - Métricas exportadas para `out/evidence/S4_T6_observability/metrics_snapshot.json`  
  - Amostras de logs em `out/evidence/S4_T6_observability/logs_sample.log`

- **Perguntas:** todas as Fontes P0 aparecem em métricas e logs? é possível ver coletas, sucessos/falhas, latência, staleness? estados ok/degradada/quebrada são inferíveis?

**Critérios de PASS:**
- 100% das Fontes P0 com métricas e logs visíveis.  
- Matriz de saúde por fonte coerente com a realidade observada.

**Artefatos obrigatórios:**
- `out/evidence/S4_T6_observability/metrics_snapshot.json`  
- `out/evidence/S4_T6_observability/logs_sample.log`  
- `out/evidence/S4_T6_observability/health_matrix.json`  
- `out/scorecards/S4_T6_observability.json`

**Invariantes/SLOs ligados:**
- "Nenhuma Fonte P0 ativa invisível em métricas/logs".  
- "Quebras em Fonte P0 detectadas em tempo finito".  
- SLOs: **detection_latency_p95_min**, **run_success_rate**, base para **explore_query_p95_ms** (casos de uso de consulta monitorados).

---

### 6.8 T7 — Integração contínua da sprint

**Objetivo:** consolidar a pipeline S4 em um entrypoint único, reprodutível.

- **Entrada:** entrypoint ORR S4 (script/workflow), fixtures/goldens, gates T0–T6 implementados.

- **Perguntas:** é possível rodar T0–T6 de ponta a ponta automaticamente? dois runs seguidos produzem scorecards compatíveis?

**Critérios de PASS:**
- Pipeline completa executa sem falhas inesperadas.  
- Scorecards T0–T6 são consistentes entre execuções (ou diferenças justificadas).

**Artefatos obrigatórios:**
- `out/evidence/S4_T7_integration/orr_run.log`  
- `out/evidence/S4_T7_integration/scorecards_index.json` (lista de scorecards considerados)  
- `out/scorecards/S4_T7_integration.json`

**Invariantes/SLOs ligados:**
- Reforça todos os invariantes, garantindo integração.  
- SLOs medidos aqui são usados por T8 para decisão final.

---

### 6.9 T8 — GO/NO_GO da Sprint 4

**Objetivo:** responder, com base em fatos, se a Sprint 4 cumpriu o contrato do Capítulo 1.

- **Entrada:** scorecards T0–T7, métricas de SLOs, matriz de invariantes.  
- **Perguntas:** todos os gates obrigatórios estão verdes? SLOs foram atingidos? invariantes críticos foram respeitados? DoD foi cumprido?

**Critérios de GO:**
- 100% dos gates T0–T7 com `status = "PASS"`.  
- SLOs mínimos atingidos (Capítulo 1, seção 7.2).  
- Nenhuma invariante crítica quebrada.  
- Definition of Done integral.

**Artefatos obrigatórios:**
- `out/scorecards/S4_T8_go_no_go.json`  
- `docs/sprint_4_orr_summary.md`

**Invariantes/SLOs ligados:**
- Todos os invariantes.  
- Todos os SLOs: **onboarding_p50_min**, **detection_latency_p95_min**, **run_success_rate**, **evidence_completeness_rate**, **explore_query_p95_ms**.

---

## 7. Mapa SLO → gate → evidência

1. **onboarding_p50_min** (tempo de onboarding de nova fonte)
   - Gates: T0 (definição de P0), T2 (registry), T3 (fixtures), T6 (medição em campo), T8 (agregação).  
   - Evidências:  
     - tempo cronometrado de onboarding armazenado em `out/evidence/S4_T6_observability/onboarding_experiments.json`;  
     - scorecards T2/T3/T6;  
     - T8 consolida resultado.

2. **detection_latency_p95_min** (latência entre dado aparecer na fonte e ser coletado)
   - Gates: T6, T7, T8.  
   - Evidências:  
     - métricas de latência por fonte em `metrics_snapshot.json`;  
     - análise em `health_matrix.json`;  
     - T8 verifica se p95 está dentro do alvo.

3. **run_success_rate** (taxa de sucesso de execuções de coleta)
   - Gates: T3 (corretude básica), T6 (observabilidade real), T7/T8 (integração e agregação).  
   - Evidências:  
     - contadores de sucesso/falha por fonte;  
     - scorecards T3/T6;  
     - T8 verifica limiar ≥ 97%.

4. **evidence_completeness_rate** (completude de evidência)
   - Gates: T3, T4, T5, T6, T8.  
   - Evidências:  
     - testes de fixtures (Evidência deve existir para cada Item);  
     - goldens com evidência completa;  
     - snapshots/vault_diff;  
     - indicador agregado em T8.

5. **explore_query_p95_ms** (desempenho de consulta Explore M0)
   - Gates: T3 (testes de integração Explore+Vault), T6 (monitoramento em produção interna), T7/T8 (agregação).  
   - Evidências:  
     - testes de consulta com latência medida em `out/evidence/S4_T3_fixtures/explore_queries_bench.json`;  
     - métricas de latência em `metrics_snapshot.json`;  
     - verificação de p95 ≤ 800ms em T8.

---

## 8. Matriz invariantes → gates → evidências (resumo)

- **Nenhum Item P0 sem Evidência completa**  
  - Gates: T3, T4, T5, T6, T7, T8.  
  - Evidências: fixtures, goldens, vault_diff, health_matrix, scorecards.

- **Toda Evidência P0 rastreável à Fonte e ao Run**  
  - Gates: T1, T3, T4, T5.  
  - Evidências: modelo de dados, manifestos, relatórios de teste.

- **Nenhuma Fonte P0 ativa invisível em métricas/logs**  
  - Gates: T6, T7, T8.  
  - Evidências: metrics_snapshot, logs_sample, health_matrix.

- **Explore M0 nunca mostra Item sem Evidência**  
  - Gates: T3, T4, T6, T7.  
  - Evidências: testes de integração de consulta, relatórios específicos.

- **Fixtures do ORR vêm de dados reais e são versionadas**  
  - Gates: T3, T4, T7.  
  - Evidências: diretórios de fixtures/goldens, logs de ORR.

- **Quebras em Fonte P0 detectadas em tempo finito**  
  - Gates: T6, T7, T8.  
  - Evidências: métricas de falha/staleness, health_matrix, scorecards.

- **Nenhum ajuste estrutural em Fonte P0 apenas em código**  
  - Gates: T2, T6.  
  - Evidências: validações de registry, ausência de fontes “especiais” fora do registry.

---

## 9. Contratos anti‑gambiarra (proibições explícitas)

Para manter a integridade dos gates e da sprint:

1. **Proibido “despromover” fonte P0 para escapar de gate**  
   - Toda mudança na lista de Fontes P0 durante a sprint deve ser aprovada pelo PO e registrada no wrap.  
   - T0/T2/T6/T8 devem refletir essa mudança.

2. **Proibido alterar fixtures/goldens só para fazer teste passar**  
   - Fixtures/goldens só podem ser atualizados após:  
     - correção legítima no código ou ajuste explícito de especificação;  
     - revisão e aprovação do PO.  
   - Logs de T4 devem registrar quando goldens forem atualizados.

3. **Proibido mascarar falhas em scripts/workflows**  
   - Nenhum gate pode esconder erro com comandos do tipo “ignorar saída/erro” ou equivalentes.  
   - FAIL é FAIL; se for aceitável, precisa estar justificado no wrap.

4. **Proibido alterar SLOs de forma silenciosa**  
   - Qualquer ajuste em limiares de SLO precisa atualizar: Capítulo 1, Capítulo 2, scorecards e, se aplicável, T8.  
   - Não existe mudança de threshold só em código.

5. **Proibido criar caminhos paralelos de validação fora dos gates**  
   - Qualquer validação relevante deve ser incorporada a algum gate (T0–T7).  
   - Scripts soltos que “não aparecem em lugar nenhum” são considerados dívida.

---

## 10. Como o Codex deve usar este capítulo

1. **Antes de implementar**, escolher para cada tarefa:  
   - qual gate T0–T8 ela fortalece;  
   - quais artefatos em `docs/`, `config/`, `fixtures/`, `goldens/`, `out/evidence/`, `out/scorecards/` serão impactados.

2. **Ao implementar um gate**, garantir:
   - entrypoint claro (script/comando/workflow);  
   - scorecard no caminho indicado;  
   - diretório de evidências preenchido;  
   - ligações corretas com invariantes e SLOs.

3. **Na revisão**, checar sempre:
   - se o PR não cria nada que escape da malha de gates;  
   - se eventuais mudanças em fixtures/goldens foram justificadas e registradas;  
   - se o estado de gates está coerente com o que este capítulo define.

Com o Capítulo 1 (intenção) e o Capítulo 2 (validação) em conjunto, a Sprint 4 passa a ter um **guia completo de qualidade**: sabemos o que queremos e sabemos exatamente como comprovar que chegamos lá.

