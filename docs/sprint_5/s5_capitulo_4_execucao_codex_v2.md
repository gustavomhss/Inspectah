# Sprint 5 — Capítulo 4 (v2)
## Guia de Execução para o Codex + Padrões de Engenharia
### Inspectah Data Hub Core — Sprint 5

> v2 — Versão 15/10. Este capítulo é o **manual operacional definitivo** para o Codex e para o time de engenharia na Sprint 5. Ele conecta, de forma explícita, **componentes → boas práticas → testes → gates**, define antipadrões proibidos, checks automáticos e orientações de segurança/privacidade.
>
> Cap. 1 = contrato conceitual.  
> Cap. 2 = contrato de gates.  
> Cap. 3 = mapa de arquivos/CI/execução.  
> Cap. 4 = **como pensar e agir** enquanto implementa tudo isso.

---

## 1. Mandamentos gerais (com ligação a gates)

1. **Respeite o triângulo Cap. 1–2–3**  
   - Qualquer mudança estrutural (estados, claims, invariantes) exige atualizar Cap. 1–3 antes do código.
   - Gates impactados: **G0, G1, G3** (spec lock, schema/contratos, pipeline com fixtures).

2. **Sem placeholders, sem gambiarras, sem TODO/FIXME**  
   - Código de S5 não pode conter `TODO`, `FIXME`, `HACK` ou comentários equivalentes.  
   - Devemos ter um check automático simples (ver Seção 6) para isso.  
   - Gates impactados: **G2, G3, G7** (componentes, pipeline, estabilidade).

3. **Design orientado por gate**  
   - Sempre perguntar: "Qual gate vai validar isso?" antes de escrever código.  
   - Exemplo: mudando normalizer → pensar em **G1 (schema)**, **G2 (components)**, **G3 (golden)**, **G4 (IA real)**.

4. **Testes e fixtures antes de "otimizações"**  
   - Primeiro deixar **G1–G3 verdes com fixtures/golden**; só depois pensar em ajustes finos de performance.

5. **Idempotência operacional**  
   - Scripts de gate, de ingest e de verificação devem poder ser executados várias vezes sem efeitos colaterais destrutivos.
   - Gates impactados: **G3, G7**.

6. **Logs e métricas estruturados, nunca ruído**  
   - Nenhum log solto de debug permanente em S5. Logs devem ter contexto mínimo (`source_id`, `item_id`, operação, resultado).  
   - Gates impactados: **G6, G7**.

7. **Segurança e privacidade em primeiro plano**  
   - Não logar dados sensíveis ou texto completo desnecessariamente.  
   - Respeitar termos de uso, robots.txt e limites de fontes (Cap. 1 §11).  
   - Gates impactados: **G4 (IA e dados de entrada)**, **G6 (observabilidade)**, **G7 (estabilidade/ética)**.

---

## 2. Tabela “Componente → Boas práticas → Testes/Gates”

### 2.1 Visão geral

| Componente                      | Boas práticas principais                                       | Testes relacionados                           | Gates que dependem diretamente |
|---------------------------------|----------------------------------------------------------------|-----------------------------------------------|---------------------------------|
| Watchers (engine + RSS/API/HTML)| Registry central, isolamento de falhas, respeito a limites    | `test_watchers_engine.py`                     | G2, G3, G6, G7                  |
| Evidence Builder/Verifier       | Bundles imutáveis, layout fixo, manifest com hashes           | `test_evidence_builder.py`, `test_evidence_verifier.py` | G2, G3, G6, G7                  |
| Models + Schemas + Equiv. Key   | 1:1 com Cap. 1, determinismo, sem campos extras               | `test_schema_item.py`, `test_schema_claim.py`, `test_equivalence_key.py` | G1, G2, G3, G4                  |
| Normalizer + Client IA          | Prompt sólido, validação rigorosa, não-invenção               | `test_normalizer_stub.py`, golden data        | G2, G3, G4, G6, G7              |
| Indexer + Query API             | Index simples, queries previsíveis, sem acoplamento excessivo | `test_indexer.py`, `test_pipeline_fixtures.py`| G3, G5, G6, G7                  |
| UI Admin & Explore              | Fluxo natural, estado claro, erro explícito                   | UI smokes / G5 cenário operador               | G5, G6                          |
| Métricas & Dashboards           | Métricas nomeadas, sem alta cardinalidade, dashboards claros  | `ci-metrics-smoke`, screenshots de painel     | G6, G7                          |
| Scripts de Gate (G0–G7)         | Saída clara, scorecards, códigos de saída corretos            | Execução dos próprios scripts em CI/local     | Todos                           |

### 2.2 Exemplos de ligação prática com gates

- Ao mexer em `inspectah/normalizer/normalizer.py`:
  - Verificar **G1** (schema/contratos): campos continuam válidos; enums iguais.
  - Rodar testes de **G2** (components): `pytest tests/components/test_normalizer_stub.py`.
  - Rodar **G3** com fixtures/golden: `bin/s5_gate_g3_pipeline_fixtures.sh`.
  - Se for IA real: preparar **G4** (integração) e amostra manual.

- Ao mexer em `inspectah/ui/explore.py`:
  - Garantir que o cenário de operador em `G5_operator_scenario.md` continue válido.  
  - Executar G5 via `bin/s5_gate_g5_operator_journey.sh` assim que as mudanças forem significativas.

---

## 3. Padrões e antipadrões (com exemplos concretos)

### 3.1 Watchers & Registry

**Padrões desejados**

- Toda fonte configurada exclusivamente em `sources_registry.yaml`.
- Watchers usam tempo limite/config de tentativas definidos no registry.
- Logs trazem: `source_id`, URL alvo (ou hash/descrição quando sensível), status e latência.

**Antipadrões proibidos (exemplos)**

- **Hardcode de URLs** dentro de `engine.py` ou watchers específicos.  
  _Errado:_ `url = "https://site.com/feed"` cravado no código.  
  _Correto:_ `url` vem de `sources_registry.yaml`.

- **Loops de retry sem limite** ou com `while True` em watchers.  
  Consequência: bombardeio de fonte, quebra ética e riscos de banimento.

- **Tratamento silencioso de erro**: capturar exceção e seguir como se nada tivesse acontecido.

### 3.2 Evidence Vault

**Padrões desejados**

- Bundles `write-once` em paths determinísticos.  
- `manifest.json` consistente; `verifier.py` sempre usado em gates/tests.

**Antipadrões proibidos (exemplos)**

- Reaproveitar pasta de bundle para "corrigir" dados antigos, sobrescrevendo arquivos.
- Depender da ordem de listagem do arquivo de sistema (ao invés de nomes claros).  
- Salvar texto de evidência com encoding não definido (sem UTF‑8, por exemplo).

### 3.3 Normalizer & IA

**Padrões desejados**

- Prompt deixando claro: "não inventar fatos" e respeitar schema.
- Sempre validar JSON contra schema antes de marcar S3.

**Antipadrões proibidos (exemplos)**

- Aceitar saída do modelo sem validação completa.  
- "Ajeitar" JSON com regex frágil só para passar no teste, sem corrigir a causa raiz.  
- Logar a **entrada inteira** da fonte + a **saída inteira** da IA em logs permanentes (risco de privacidade e volume).

### 3.4 Indexer & Query API

**Padrões desejados**

- Campos indexados bem definidos, com tipos previsíveis.
- Queries que retornam dados suficientes para a UI sem excesso.

**Antipadrões proibidos (exemplos)**

- Escrever queries cheias de `SELECT *` em produção interna, sem controle, dificultando manutenção.  
- Misturar normalização de dados no indexer (o indexer não é um segundo normalizer).

### 3.5 UI Admin & Explore (foco Jobs)

**Padrões desejados**

- **Admin:** campos de fonte com rótulos claros, ajuda contextual simples (tooltip ou texto curto).  
- **Explore:** operador entende em poucos segundos: qual fonte, qual item, qual evidência, quais claims.

**Antipadrões proibidos (exemplos)**

- Campos com labels criptográficos (“EQK”, “CID”) sem explicação.  
- Esconder erros de ingestão atrás de ícones sem texto (“ver log” sem contexto).  
- Exigir 3+ cliques para o operador ver evidência + texto + claims no mesmo fluxo.

### 3.6 Observabilidade & Incidentes

**Padrões desejados**

- Métricas com nomes claros, sem labels de alta cardinalidade.  
- Dashboards que respondem perguntas concretas: "Quais fontes estão quebrando?", "Quantos itens estão em S2 vs S3?".

**Antipadrões proibidos (exemplos)**

- Uma enxurrada de métricas irrelevantes, sem ligação com estados S0–S4 ou gates.  
- Logs de erro sem contexto: "erro ao normalizar" sem `source_id`/`item_id`.

---

## 4. Segurança, privacidade e ética (versão mínima exigida na S5)

1. **Respeito a fontes**  
   - Seguir ToS/robots.txt.  
   - Limitar taxa de requisições por domínio, mesmo em ambiente interno.

2. **Dados sensíveis**  
   - Não logar texto completo de evidência quando não for necessário para debug; preferir hashes, IDs, trechos curtos.  
   - Criptografar ou, no mínimo, proteger diretórios de evidência em ambientes compartilhados.

3. **Uso da IA**  
   - Não enviar para a IA dados que violem termos dos provedores das fontes.  
   - Não usar respostas da IA como "verdades" fora do escopo S3 (lembrar: local_verdict = "segundo esta fonte").

4. **Incidentes e resposta**  
   - Se uma métrica crítica (ex.: `evidence_verification_failures_total` > 0 ou `watcher_success_rate` cair muito) explodir:  
     - congelar novos deploys;  
     - reverter para estado estável anterior;  
     - investigar causa antes de reativar features.

Este conjunto de práticas é parte implícita de **G4, G6 e G7**.

---

## 5. Checks automáticos e ligação com CI

### 5.1 Check “sem TODO/FIXME/HACK”

- Script simples (por exemplo, em `bin/s5_check_no_todos.sh`) que faz `grep -R` no repo e falha se encontrar:
  - `TODO`, `FIXME`, `HACK`, `XXX` em código de produção.

- Esse script deve rodar em um job de CI (ex.: `ci-style`) e/ou ser invocado dentro de algum gate (tipicamente G2 ou G7).

### 5.2 Check de consistência de nomes

- Opcional, mas recomendado: script que verifica se os termos `source_id`, `item_id`, `bundle_id`, `equivalence_key` são usados corretamente (por padrão, só check de lint/grep para detectar variações estranhas como `src_id`, `eqKey`).

### 5.3 Check de logs e métricas básicos

- `ci-metrics-smoke` deve:
  - subir o app em modo mínimo;  
  - chamar o endpoint de métricas;  
  - verificar se algumas métricas mínimas (definidas no Cap. 1) aparecem.

### 5.4 Check de gates principais em CI

- Idealmente, um job `ci-s5-gates-core` que roda:
  - `bin/s5_gate_g1_schema_contracts.sh`
  - `bin/s5_gate_g2_components.sh`
  - `bin/s5_gate_g3_pipeline_fixtures.sh`

Se qualquer um desses falhar, a PR não deve ser mesclada.

---

## 6. “Como o Codex deve pensar” para cada gate (exemplos explícitos)

### 6.1 G3 — Pipeline com fixtures

Perguntas que o Codex deve se fazer ao mexer em qualquer parte do pipeline:

- "Se eu rodar `bin/s5_gate_g3_pipeline_fixtures.sh` agora, o que deve acontecer exatamente?"  
- "Quais fixtures e golden data são afetados pela mudança?"  
- "Estou introduzindo qualquer comportamento não determinístico que torne o gate instável?"

Se a resposta incluir "não sei", é sinal de que o Cap. 3 e/ou os testes precisam ser revisitados antes de mexer no código.

### 6.2 G4 — IA real (GPT‑4.1 mini)

Antes de alterar `client_ai.py` ou `normalizer.py`, o Codex deve pensar:

- "Como isso afeta as métricas de % de JSON válidos e % de itens com claims?"  
- "Estou piorando ou melhorando o risco de invenção? O gate G4 tem amostras suficientes para pegar isso?"  
- "Preciso ajustar o prompt ou apenas a validação?"

Se a mudança não tiver um plano claro de como será medida em G4, ela não está pronta.

### 6.3 G5 — Jornada do operador

Ao mexer na UI, perguntar:

- "Com esta mudança, o operador ainda consegue seguir o roteiro de `G5_operator_scenario.md` sem se perder?"  
- "Estou adicionando passos ou confusão desnecessária?"  
- "Preciso atualizar o cenário de G5 para refletir a nova UI?"

### 6.4 G7 — Estabilidade

Antes de chamar a sprint de "pronta":

- "Se eu rodar 7 dias simulados, que tipo de erro ainda pode explodir em série?"  
- "Há algum componente que não aguenta long run (memory leak, file leak, etc.)?"  
- "Os KPIs do Cap. 2 estão realmente sendo medidos do jeito certo?"

---

## 7. Checklist final de engenharia por mudança

Antes de considerar qualquer tarefa "pronta", o Codex (ou dev humano) deve passar mentalmente por:

1. **Contrato**  
   - A mudança está alinhada com Cap. 1 (estados/claims/invariantes)?

2. **Gates**  
   - Quais gates são afetados? G1/G2/G3/G4/G5/G6/G7?  
   - Consigo rodar o gate relevante e ver PASS?

3. **Filemap**  
   - O arquivo está no lugar e nome corretos conforme Cap. 3?  
   - Se criei algo estrutural novo, atualizei Cap. 3?

4. **Testes**  
   - Há testes cobrindo esse comportamento?  
   - Eles rodam limpos (zero FAIL)?

5. **Observabilidade**  
   - Se isso quebrar em produção interna, teremos métricas/logs suficientes pra entender?  
   - Não exagerei nos logs (sem spam), nem escondi contexto demais?

6. **Segurança/privacidade**  
   - Não estou vazando conteúdo sensível em logs, dashboards ou erros.

7. **Simplicidade**  
   - Outra pessoa entende esse código em 2–3 minutos?  
   - Se a resposta for "não", é hora de simplificar.

Se qualquer item acima estiver indefinido, a tarefa **não está** no nível de excelência esperado da Sprint 5.

---

## 8. Fechamento

Com este Capítulo 4 v2, o conjunto de planejamento/execução da S5 fica assim:

- **Cap. 1** — O que o Inspectah precisa ser (modelo, claims, invariantes, métricas).  
- **Cap. 2** — Como a sprint será julgada (gates G0–G7, scripts, scorecards, KPIs).  
- **Cap. 3** — O que construir, onde e em que ordem (filemap, eixos, CI, riscos).  
- **Cap. 4** — Como o Codex e o time devem se comportar enquanto implementam (padrões, antipadrões, checks, gates na cabeça).

A partir daqui, qualquer execução da Sprint 5 que respeite estes quatro capítulos tem tudo para ser **executável, auditável e de nível 15/10**, sem gambiarras, sem retrabalho estrutural e com um caminho claro até o GO da S5.

