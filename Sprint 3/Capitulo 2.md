# Inspectah — Capítulo 2 v3
## Mapa de Gates & ORR — Linha Dura 15/10 para dizer “o Inspectah está certo, rápido e confiável”

---

### 0. TL;DR

O Capítulo 1 definiu **o que é** o Inspectah: hub de fontes, log de fatos imutável, Sinais multi‑fonte, consenso prático, `confidence_score` (%) e trilha de decisão explicável.

O Capítulo 2 v3 define **quando podemos afirmar, sem dúvida, que essa máquina está saudável**.

Ele estabelece uma linha dura de **Gates T0–T8** que:

- respondem a **uma pergunta central única** cada;
- têm **pré‑condições, pós‑condições e efeito sobre o release** padronizados;
- usam **thresholds numéricos claros** onde faz sentido;
- exigem **evidência verificável** (scorecards, bundles, métricas) para serem considerados “verdes”;
- são avaliados em **conjunto**: para um release ser saudável, precisa existir uma execução recente de ORR em que **T0–T7 estejam simultaneamente verdes**.

Além disso, o capítulo:

- fixa dependências formais entre Gates (quem depende de quem);
- introduz uma **tabela‑resumo técnica** (Gate → métricas → agregação);
- prepara explicitamente um futuro **T5.2 — Calibração de Certeza**, com exemplo concreto de experimento;
- amarra T4–T8 em um **loop de aprendizagem contínua**: medir → aprender → ajustar blueprint e perfis de confiança (`confidence_profile_id`).

---

### 1. Objetivo do Capítulo 2

Este capítulo define o **sistema oficial de validação do Inspectah**. Em termos práticos:

- Se uma versão passou pelos Gates T0–T8 conforme descritos aqui, com evidência, ela é **elegível** para uso real.
- Se falhar em qualquer Gate crítico (especialmente T3, T4, T5, T5.1, T7 ou T8), ela é **No‑Go**, por padrão.

Objetivos específicos:

1. Cobrir toda a cadeia do produto (Capítulo 1) com Gates objetivos:
   - visão e objetivos (T0),
   - modelo de domínio e schema (T1),
   - extração/configuração via Field Designer (T2),
   - invariantes de pipeline (T3),
   - Evidence Vault (T4),
   - desempenho e qualidade de dados (T5),
   - certeza (%) e cobertura (T5.1),
   - observabilidade (T6),
   - CI/ORR (T7),
   - uso real (T8).
2. Amarrar Gates ao **Blueprint Inspectah — OracleOps v1.2.1 (Data Hub First)**, com métricas e SLOs claramente atribuídos.
3. Tornar Gates **reexecutáveis, determinísticos e automatizáveis**, inclusive em CI.
4. Criar base para experimentos de calibração futura (T5.2) sobre `confidence_score`.

---

### 2. Mapa endurecido dos Gates (T0–T8)

Visão macro dos Gates e suas dependências fortes:

| Gate | Pergunta central | Tipo principal | Depende de |
|---|---|---|---|
| **T0** | Estamos construindo o Inspectah certo? | Spec & Blueprint | — |
| **T1** | Modelo de dados está completo e implementável? | Domínio & Schema | T0=PASS |
| **T2** | Extraímos dados reais via configuração, sem código? | Field Designer & Extractors | T1=PASS |
| **T3** | Pipeline respeita dedup, idempotência e log append‑only? | Invariantes de pipeline | T1=PASS |
| **T4** | Evidence Vault está 100% completo e íntegro? | Evidence Completeness | T2=PASS, T3=PASS |
| **T5** | O Inspectah é rápido e resolve campos com alta taxa de sucesso? | Performance & Qualidade | T4=PASS |
| **T5.1** | `confidence_score` está bem comportado, honesto e cobrindo quase tudo? | Certeza (%) & Cobertura | T5=PASS |
| **T6** | Temos sinais suficientes para operar e medir tudo isso? | Observabilidade & SRE | T4=PASS, T5=PASS |
| **T7** | Os Gates rodam em CI, com bundle único de evidência? | CI & ORR | T4=PASS, T5=PASS, T6=PASS |
| **T8** | O Inspectah entrega valor real em uso contínuo? | Go/No‑Go final | T4–T7=PASS |

**Regra de simultaneidade (Lamport‑style):**

> Um release só pode ser declarado “saudável” se existir pelo menos uma execução recente (janela acordada, ex.: últimos 7 dias) de ORR em que **todos os Gates T0–T7 estejam simultaneamente verdes**.

Não basta cada Gate ter passado em momentos diferentes com código ou dados diferentes.

---

### 2.1. Tabela‑resumo técnica (Gate → métricas → agregação)

Esta tabela é o “header técnico” que o Codex usará para construir scorecards.

| Gate | Métricas principais | Agregação / condição |
|---|---|---|
| **T0** | — (checklist de spec) | 100% dos objetivos do Blueprint mapeados para métricas + Gates; zero conflitos conceituais.
| **T1** | — (schema/DDL) | 100% das entidades do Capítulo 1 mapeadas; invariantes refletidos em constraints; sem ambiguidades críticas.
| **T2** | `field_resolution_success_test` | ≥ 95% no conjunto de fontes de teste; 3+ tipos de fontes passando pelo fluxo completo.
| **T3** | `pipeline_dedup_violations`, `immutability_violations` | Ambos = 0 em suítes de teste sintéticas.
| **T4** | `evidence_completeness`, `evidence_hash_valid_rate` | `evidence_completeness` = 100%; `evidence_hash_valid_rate` = 100% na janela.
| **T5** | `detection_latency_p95`, `explore_query_p95`, `explore_query_p99`, `field_resolution_success`, `run_success_rate` | `detection_latency_p95` ≤ 2 min; `explore_query_p95` ≤ 200 ms; `explore_query_p99` ≤ 400 ms; `field_resolution_success` ≥ 99,5%; `run_success_rate` ≥ 99–99,5% conforme v0/v1.
| **T5.1** | `confidence_coverage_multi_source`, `confidence_score_histogram` | Cobertura ≥ 95%; zero scores fora de [0,100]/NaN; nenhum bucket > 90% sem justificativa.
| **T6** | existência de métricas T4/T5/T5.1, logs com campos mínimos | 100% das métricas chave presentes e com dados; logs com contexto mínimo; pelo menos um dashboard/consulta por SLO.
| **T7** | `orr_pipeline_success_rate`, `orr_pipeline_duration_p95` | Sucesso ≥ 95% na janela; duração p95 dentro do limite acordado; nenhum Gate interno “pulado”.
| **T8** | `sources_onboarding_p50`, KPIs T4/T5/T5.1 em produção, distribuição de `confidence_score` em domínios críticos | ≥ 10 fontes reais cadastradas; p50 de onboarding ≤ 5 min; KPIs núcleo dentro dos thresholds; scores em domínios críticos não sistematicamente baixos sem explicação.

Nos tópicos seguintes, cada Gate é detalhado com perguntas centrais, finalidade e **contrato padrão** (pré‑condições, pós‑condições, efeito sobre o release).

---

### 3. Padrão de contrato para todos os Gates

Para todos os Gates T0–T8, usamos o mesmo template mental:

- **Pré‑condições:** o que precisa estar verdadeiro para o Gate ser executado de forma válida.
- **Pós‑condições (PASS):** o que podemos afirmar com confiança se o Gate for verde.
- **Pós‑condições (FAIL):** o que sabemos que NÃO é verdade (ou é duvidoso) se o Gate falhar.
- **Efeito sobre o release:** o que fica permitido ou proibido em termos de decisão de release.

Esse padrão transforma cada Gate em um **contrato explícito** para o time e para o Codex.

---

### 4. T0 — Escopo travado (Spec & Blueprint Gate)

**Pergunta central:** _“Estamos construindo o Inspectah certo, com objetivos, métricas e conceitos alinhados?”_

#### 4.1 Finalidade

Travar o alvo. Evitar sprint em terreno movediço onde cada pessoa imagina um produto diferente.

#### 4.2 O que T0 valida

- Capítulo 1 vFinal e Blueprint estão coerentes em nomenclatura e conceito.
- Cada objetivo de v0/v1 no Blueprint está mapeado para:
  - uma métrica concreta; e
  - pelo menos um Gate (T4–T8).
- Tudo que fica fora de escopo é explicitamente registrado.

#### 4.3 Contrato de T0

- **Pré‑condições:**
  - Capítulo 1 vFinal e Blueprint atualizados e disponíveis;
  - participantes mínimos: PM + Tech Lead.
- **Pós‑condições (PASS):**
  - existe um documento de "Spec Lock" com lista de objetivos, métricas, Gates associados e itens explicitamente fora de escopo;
  - não há conflitos conceituais conhecidos.
- **Pós‑condições (FAIL):**
  - objetivos sem métrica ou sem Gate;
  - conflitos de definição não resolvidos.
- **Efeito sobre o release:**
  - Se T0=FAIL, a sprint **não avança** para T1–T3; qualquer código escrito nessa condição é considerado “fora de contrato”.

---

### 5. T1 — Modelo & Schema Gate

**Pergunta central:** _“O modelo de dados está completo, coerente com o Capítulo 1 e pronto para implementação sem surpresas?”_

#### 5.1 Finalidade

Garantir que o modelo não esteja só em texto: Fonte, Observação, Item, Campo, Sinal e `confidence_score` têm representação concreta, com invariantes refletidos no schema.

#### 5.2 O que T1 valida

- Todas as entidades do Capítulo 1 têm modelos claros (tabelas, tipos, índices ou estruturas equivalentes).
- Invariantes como imutabilidade de Observações, versionamento, chaves e índices de consulta estão representados em constraints e estruturas.

#### 5.3 Contrato de T1

- **Pré‑condições:**
  - T0=PASS;
  - proposta de schema/DDL em estado revisável.
- **Pós‑condições (PASS):**
  - 100% das entidades do Capítulo 1 mapeadas;
  - invariantes críticas com representação técnica (não só em texto);
  - documento "Modelo & Schema vX" disponível.
- **Pós‑condições (FAIL):**
  - lacunas claras (entidades sem modelo);
  - invariantes que dependeriam apenas de disciplina manual.
- **Efeito sobre o release:**
  - Se T1=FAIL, T2 e T3 **não devem ser considerados válidos**, mesmo que testes isolados “passem”: eles foram construídos em cima de um modelo inconsistente.

---

### 6. T2 — Field Designer & Extractors Gate

**Pergunta central:** _“Conseguimos extrair, tipar e indexar dados de fontes reais usando o Field Designer, sem escrever código?”_

#### 6.1 Finalidade

Demonstrar, na prática, que o Inspectah é um **Data Hub configurável**, não um amontoado de scripts sob medida.

#### 6.2 O que T2 valida

- Pelo menos 3 fontes reais de tipos diferentes (RSS, API JSON, HTML) são:
  - cadastradas via fluxo padrão;
  - configuradas com Campos e, opcionalmente, Sinais;
  - validadas via dry‑run;
  - publicadas com coleta funcionando;
  - refletidas em Observações + Itens + Campos + bundles de evidência.
- `field_resolution_success_test` ≥ 95% nesse conjunto.

#### 6.3 Contrato de T2

- **Pré‑condições:**
  - T1=PASS;
  - ambiente de testes com fontes reais acessíveis.
- **Pós‑condições (PASS):**
  - Field Designer é suficiente para lidar com esses 3 tipos de fontes sem hacks de código;
  - há evidência (relatório, prints, dados) mostrando o fluxo completo.
- **Pós‑condições (FAIL):**
  - fluxo quebrado em qualquer etapa crítica (sem cadastro, sem dry‑run, sem coleta ou sem index);
  - necessidade de intervenção de dev para tarefas que deveriam ser de Admin.
- **Efeito sobre o release:**
  - Se T2=FAIL, o produto ainda não é Inspectah; é um protótipo. T4–T8 perdem sentido até isso ser resolvido.

---

### 7. T3 — Invariantes do pipeline (Dedup, Idempotência & Log)

**Pergunta central:** _“O pipeline respeita dedup, idempotência e log append‑only como prometido?”_

#### 7.1 Finalidade

Proteger o núcleo de dados. Garantir que Observações são fatos imutáveis e que o pipeline não cria estados zumbis.

#### 7.2 O que T3 valida

- Dedup bem‑comportado (mesma URL + mesmo conteúdo → um Item; hashes diferentes → versões diferentes).
- Nenhuma operação normal altera ou deleta Observações.
- Backfill gera novas versões de Item, sem apagar versões antigas.

#### 7.3 Contrato de T3

- **Pré‑condições:**
  - T1=PASS;
  - suíte de testes sintéticos disponível.
- **Pós‑condições (PASS):**
  - `pipeline_dedup_violations` = 0;
  - `immutability_violations` = 0;
  - cenários de backfill se comportam conforme especificado.
- **Pós‑condições (FAIL):**
  - duplicatas não intencionais;
  - Observações alteradas ou removidas;
  - backfill corrompendo histórico.
- **Efeito sobre o release:**
  - Se T3=FAIL, qualquer medição posterior (T4–T8) é suspeita; release é **No‑Go** até correção.

---

### 8. T4 — Evidence Vault & integridade (Evidence Completeness Gate)

**Pergunta central:** _“O Evidence Vault está 100% completo e íntegro para os itens válidos?”_

#### 8.1 Finalidade

Eliminar o cenário "confie em mim". Se o Inspectah mostra um Item, ele precisa ter prova de origem guardada.

#### 8.2 O que T4 valida

- Em uma janela (ex.: últimos 7 dias) para Itens válidos:
  - `evidence_completeness` = 100%;
  - `evidence_hash_valid_rate` = 100%.

#### 8.3 Contrato de T4

- **Pré‑condições:**
  - T2=PASS, T3=PASS;
  - Evidence Vault operante com dados recentes.
- **Pós‑condições (PASS):**
  - todo Item válido tem bundle íntegro (manifest + HTML + texto + metadados + hashes corretos);
  - ausência de “buracos” na janela.
- **Pós‑condições (FAIL):**
  - Itens sem bundle;
  - bundles com hash quebrado;
  - métrica `evidence_completeness` < 100%.
- **Efeito sobre o release:**
  - Se T4=FAIL, T5/T5.1/T6/T7/T8 não podem ser considerados verdes. Latência boa sem evidência é inaceitável.

---

### 9. T5 — Desempenho & qualidade de dados

**Pergunta central:** _“O Inspectah é rápido e resolve campos com a taxa de sucesso prometida?”_

#### 9.1 Finalidade

Transformar promessas de SLO em números verificáveis.

#### 9.2 O que T5 valida

Em 7 dias de operação (produção interna ou espelho):

- `detection_latency_p95` ≤ 2 min para RSS/API monitoradas;
- `explore_query_p95` ≤ 200 ms e `explore_query_p99` ≤ 400 ms (queries até 100 itens);
- `field_resolution_success` ≥ 99,5% para campos obrigatórios;
- `run_success_rate` ≥ 99% (v0) ou ≥ 99,5% (v1).

#### 9.3 Contrato de T5

- **Pré‑condições:**
  - T4=PASS;
  - métricas alimentadas e estáveis na janela.
- **Pós‑condições (PASS):**
  - Inspectah responde rápido o suficiente;
  - resolve campos com robustez;
  - não apresenta taxa de erro crônica.
- **Pós‑condições (FAIL):**
  - latência alta, campos falhando ou muitos erros;
  - SLOs do blueprint não cumpridos.
- **Efeito sobre o release:**
  - Se T5=FAIL, T5.1 e T8 não podem ser verdes; release é **No‑Go**, salvo exceção formalíssima.

---

### 10. T5.1 — Certeza (%) e cobertura do `confidence_score`

**Pergunta central:** _“O `confidence_score` está sendo emitido quando deve, dentro de [0, 100] e com distribuição saudável?”_

#### 10.1 Finalidade

Garantir que certeza (%) é uma função real do sistema, não um enfeite.

#### 10.2 O que T5.1 valida

Em amostra grande de respostas (7 dias):

- cobertura de `confidence_score` em respostas multi‑fonte elegíveis ≥ 95%;
- invariantes básicas:
  - 0 ≤ `confidence_score` ≤ 100;
  - zero NaN/null indevido;
  - distinção clara entre single‑fonte e multi‑fonte;
- distribuição em buckets (0–30, 30–60, 60–85, 85–100) não saturada:
  - nenhum bucket > 90% dos casos sem justificativa registrada.

#### 10.3 Contrato de T5.1

- **Pré‑condições:**
  - T5=PASS;
  - métricas de `confidence_score` ativas.
- **Pós‑condições (PASS):**
  - a lógica de emissão de score está ligada ao produto real;
  - scores parecem saudáveis em termos de cobertura e distribuição;
  - cada score é etiquetado com `confidence_profile_id`.
- **Pós‑condições (FAIL):**
  - falta de cobertura (muitas respostas sem score);
  - scores inválidos;
  - saturação suspeita (ex.: quase tudo 100%).
- **Efeito sobre o release:**
  - Se T5.1=FAIL, qualquer uso de `confidence_score` como insumo confiável (especialmente integrações externas e futuros oráculos) é **bloqueado**; T8 não pode ser “Go” para esses cenários.

#### 10.4 Gancho para T5.2 — Calibração de Certeza

T5.1 garante que a infraestrutura de score está **bem comportada**. Isso é pré‑condição para um futuro **T5.2 — Calibração**, que perguntará:

> “Quando o Inspectah diz 80% de certeza, isso significa que estamos certos em ~8 de cada 10 casos auditados?”

Um experimento típico de T5.2 poderia ser:

- Escolher um domínio (ex.: preço semanal de item X em bairros Y/Z).
- Coletar, por 3 meses, respostas do Inspectah com `confidence_score` em faixas como 60–70–80–90%.
- Para cada amostra, comparar com:
  - auditorias humanas (operadores verificando manualmente as fontes brutas);
  - ou fatos externos observáveis posteriormente (ex.: preço medido diretamente em app/loja).
- Medir, por faixa, o percentual de acerto real. Exemplo:
  - scores na faixa 80–85% se confirmam como corretos em 82% dos casos → calibrado;
  - scores de 60–65% se confirmam em apenas 40% dos casos → subcalibrado.
- Ajustar perfis de confiança (`confidence_profile_id`) com base nesses resultados.

Capítulo 2 não exige que T5.2 exista ainda, mas **exige** que os dados e metadados (scores etiquetados, evidências, trilhas) estejam prontos para esse tipo de experimento.

Importante: **integrações externas e oráculos só podem, por política, se apoiar em perfis de confiança que tenham passado por calibração formal (T5.2)**. Antes disso, o uso de `confidence_score` para esse tipo de integração deve ser considerado “experimental”.

---

### 11. T6 — Observabilidade & SRE Gate

**Pergunta central:** _“Temos métricas e logs suficientes para operar o Inspectah e medir os SLOs definidos?”_

#### 11.1 Finalidade

Evitar “teatro de SLO”: indicadores no papel sem métricas reais por trás.

#### 11.2 O que T6 valida

- Presença e frescor das métricas usadas em T4, T5, T5.1;
- Logs com contexto mínimo (IDs, timestamps, erros, correlações);
- pelo menos um dashboard ou consultas padrão para cada SLO principal.

#### 11.3 Contrato de T6

- **Pré‑condições:**
  - T4=PASS; T5=PASS;
  - stack de observabilidade ativo.
- **Pós‑condições (PASS):**
  - é possível, a partir de métricas/logs, reconstituir a saúde do sistema na janela de interesse;
  - SRE/Operações têm uma visão oficial dos SLOs.
- **Pós‑condições (FAIL):**
  - métricas ausentes ou quebradas;
  - logs insuficientes para investigar incidentes;
  - falta de qualquer visão consolidada.
- **Efeito sobre o release:**
  - Se T6=FAIL, T7 não pode ser considerado estável; ORR sem olhos/ouvidos é teatro.

---

### 12. T7 — CI & ORR integrado

**Pergunta central:** _“Todos os Gates relevantes rodam em CI, com bundle único de evidência, de forma reprodutível?”_

#### 12.1 Finalidade

Matar o “funciona na minha máquina”. T7 garante que a linha T1–T6 é executável em ambiente limpo.

#### 12.2 O que T7 valida

- Pipeline ORR que orquestra Gates ou suas versões automatizadas;
- geração de scorecards e bundles de evidência padronizados;
- taxa de sucesso do pipeline razoável (sem flakiness crônica);
- nenhum Gate “pulado” silenciosamente.

#### 12.3 Contrato de T7

- **Pré‑condições:**
  - T4=PASS; T5=PASS; T6=PASS;
  - ambiente CI configurado.
- **Pós‑condições (PASS):**
  - existe pelo menos um job de ORR que roda T1–T6 ou equivalentes;
  - `orr_pipeline_success_rate` ≥ 95% na janela;
  - `orr_pipeline_duration_p95` dentro do limite acordado;
  - bundle ORR único por execução, contendo scorecards + resumos.
- **Pós‑condições (FAIL):**
  - pipeline intermitente, sem confiabilidade;
  - partes da suíte nunca executando;
  - bundles incompletos.
- **Efeito sobre o release:**
  - Se T7 for flaky ou FAIL, não existe “foto” ORR confiável; T8 não pode declarar Go com base em evidência sólida.

---

### 13. T8 — Pronto para uso real (Go/No‑Go)

**Pergunta central:** _“O Inspectah está entregando valor real, dentro dos SLOs, em uso contínuo?”_

#### 13.1 Finalidade

Ser o juiz final. T8 olha para o sistema **em operação real**, não só para testes sintéticos.

#### 13.2 O que T8 valida

Em janela (7–14 dias) de uso interno:

- Onboarding de pelo menos 10 fontes reais, com p50 de tempo ≤ 5 min.
- KPIs principais (T4, T5, T5.1) batendo as metas na prática.
- `confidence_score` em domínios críticos não sistematicamente baixo (<50%) sem motivo documentado.
- Operadores conseguem usar o sistema no dia a dia sem fricções bloqueantes.

#### 13.3 Contrato de T8

- **Pré‑condições:**
  - T4–T7=PASS;
  - ambiente real de uso interno ativo.
- **Pós‑condições (PASS):**
  - Inspectah Data Hub interno v0/v1 é **Go** para uso contínuo;
  - eventuais dores são refinamentos, não bloqueios;
  - documento de Go/No‑Go registra métricas e feedback.
- **Pós‑condições (FAIL):**
  - onboarding lento ou doloroso;
  - KPIs alvo falhando na prática;
  - `confidence_score` claramente pouco confiável em domínios críticos;
  - operadores relatando fricções que inviabilizam uso diário.
- **Efeito sobre o release:**
  - Se T8=FAIL, a versão é **No‑Go** para adoção interna ampla; só pode rodar em modo piloto/experimental com riscos explícitos.

---

### 14. Loop de aprendizagem contínua

Os Gates T4–T8 não existem só para “dar verde/vermelho”. Eles alimentam um ciclo de aprendizagem:

1. **Medir** — T4/T5/T5.1/T6/T7/T8 produzem métricas, scorecards e feedback de operadores.
2. **Aprender** — o time analisa:
   - onde a latência está estourando;
   - onde `field_resolution_success` cai;
   - em quais domínios `confidence_score` está sistematicamente baixo ou mal calibrado;
   - onde o ORR é flaky.
3. **Ajustar** — essas descobertas se traduzem em:
   - ajustes no Blueprint (metas, prioridades);
   - ajustes de perfis de confiança (`confidence_profile_id`) e heurísticas do Confidence Engine;
   - melhorias no Field Designer, pipeline, observabilidade e UX de operador.
4. **Revalidar** — ao subir nova versão com ajustes, o ciclo T0–T8 roda de novo, gerando nova "foto" de saúde.

Capítulo 2 v3 exige que esse loop seja possível: não apenas Gates isolados, mas uma linha de feedback contínuo entre operação e próxima versão do produto.

---

### 15. Resumo para o Codex

Para o Codex (ou qualquer agente executor), a tradução é direta:

- Implementar scorecards e workflows de forma que cada Gate T0–T8 respeite o contrato definido (pré, pós, thresholds, evidências).
- Garantir que exista pelo menos um pipeline ORR que, periodicamente, rode T1–T6/T7 e gere um bundle único com o estado dos Gates.
- Verificar a **regra de simultaneidade**: apenas execuções em que T0–T7 estão todos verdes são elegíveis como “foto saudável” para decisões de release.
- Tratar `confidence_score` como cidadão de primeira classe: T5.1 precisa ser verde para qualquer uso sério do score, e perfis de confiança para integrações externas devem ser marcados como “calibrados” apenas após o futuro T5.2.
- Nunca alterar thresholds, métricas ou semântica de Gates diretamente no código sem antes atualizar este capítulo; o código é implementação, o Capítulo 2 é o contrato.

Este Capítulo 2 v3 é a **versão 15/10 do mapa de validação do Inspectah**: mais seco, mais binário, com métricas claras, contratos padronizados e um loop explícito de aprendizado. A partir daqui, qualquer spec técnica, workflow de CI ou documentação de ORR que contradiga este capítulo está errada por definição e precisa ser ajustada.

