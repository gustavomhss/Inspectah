# Inspectah — Sprint 32
## Capítulo 6 — Bloco 4
### Anti-Gaps, Riscos Residuais & Mandatos para as Próximas Sprints

> Este bloco fecha o Capítulo 6 transformando os learnings da S32 em **regras explícitas, alarmes permanentes e mandatos claros** para S33+ e para qualquer sprint que ouse tocar no núcleo de verdade do Inspectah.

---

#### 6.4.1 O que é um “anti-gap” na prática

Na S32, “anti-gap” significa:

> “algo que, se ficar implícito, invariavelmente vira bug grave, dívida estrutural ou risco de confiança.”

Este bloco lista anti-gaps que precisam, a partir de agora, ser tratados como **lei estrutural** do projeto:

- devem aparecer em especificações futuras (Capítulos 1–2);  
- devem ser refletidos em modelo, testes e gates;  
- devem ser lembrados explicitamente em ORRs de núcleos críticos.

---

#### 6.4.2 Anti-gap #1 — Invariantes não podem viver só em texto

Risco identificado na S32:

- invariantes críticas surgiram primeiro em docs, discussões e comentários;  
- houve momentos em que o código quase foi adiante sem refletir 100% dessas invariantes.

Mandato permanente:

1. **Toda invariante crítica do Truth-DB precisa ter:**
   - representação explícita em `app/truthdb/models.py` (constraints, FKs, validações);  
   - testes dedicados em `tests/truthdb/test_models_and_invariants.py`;  
   - checagem automática em G1 (e, se fizer sentido, rechecada em G2/G3).

2. Exemplos de invariantes que entram nesse pacote “hard”:
   - nada de blocos órfãos (EvidenceBlock, DecisionBlock, ContestRecord sempre ligados a um Fact/State);  
   - estados finais de verdade sempre com DecisionBlock;  
   - histórico monotônico (sem apagar blocos/decisões em função de contestação);  
   - ContestRecord nunca some depois de processado.

3. Critério operacional:
   - ORRs futuros devem ter uma seção “Checklist de Invariantes” que cruza:  
     - docs → models → testes → logs de gate.

Se qualquer invariante crítica existir apenas em texto, consideramos isso um **bug de governança**, não apenas de implementação.

---

#### 6.4.3 Anti-gap #2 — Contestação sem trilha é bug, não trade-off

Risco identificado:

- em versões iniciais de rascunho, contestação flertou com ser apenas:  
  - um campo booleano (“contested = true”);  
  - um log solto;  
  - um comentário em nota interna.

Isso viola a essência do Inspectah: a possibilidade de **questionar verdades de forma séria e auditável**.

Mandato permanente:

1. Toda contestação precisa:
   - criar ou atualizar um `ContestRecord` persistente;  
   - ser associada a um `TruthState` concreto;  
   - deixar claro quem/que mecanismo contestou, quando, e com qual payload mínimo.

2. Processar uma contestação significa:
   - mudar o `ContestRecord` de “aberta” para um estado resolvido/derivado;  
   - potencialmente criar um novo `DecisionBlock` e atualizar o `TruthState`;  
   - nunca apagar a existência da contestação.

3. Critérios de ORR:
   - qualquer fluxo de contestação que não produza ContestRecord e não apareça em evidências/métricas deve ser considerado **não conforme**;  
   - testes de contestação precisam cobrir tanto o caminho “mantém decisão” quanto “muda decisão”.

---

#### 6.4.4 Anti-gap #3 — Métricas de domínio são obrigatórias (infra não basta)

Risco identificado:

- tentação de depender apenas de métricas genéricas (HTTP, CPU, latência global) para declarar o Truth-DB “saudável”.

Mandato permanente:

1. Núcleo de verdade só é promovido a ambiente sério se existirem métricas específicas, incluindo, no mínimo:
   - `truthdb_promotion_success_rate`;  
   - `truthdb_contestation_rate`;  
   - `truthdb_flow_error_rate`;  
   - `truthdb_flow_latency_p95`.

2. ORRs futuros precisam validar:
   - que essas métricas estão expostas;  
   - que há pelo menos um painel ou forma de visualizá-las;  
   - que alguém da equipe consegue explicar o que elas significam e quais ranges são aceitáveis.

3. Evoluções futuras (comitês, causalidade, etc.) devem carregar métricas específicas equivalentes para suas responsabilidades.

Sem métricas de domínio, qualquer afirmação sobre “saúde do Truth-DB” é chute educado.

---

#### 6.4.5 Anti-gap #4 — Bundle “simbólico” invalida o ORR

Risco identificado:

- tratar o bundle da sprint como formalidade:  
  - zipando qualquer coisa;  
  - deixando scorecards ou pastas de evidência de fora;  
  - sem README de replay;  
  - sem teste real de extração e reexecução.

Mandato permanente:

1. G4 (ORR & Bundle) falha se:
   - `inspectah_sXX_evidence_bundle.zip` não existir;  
   - o zip estiver quebrado;  
   - o conteúdo não bater com o filemap e os gates da sprint.

2. Pré-requisito de ORR:
   - não abrir ORR “oficial” sem bundle minimamente íntegro;  
   - qualquer sessão feita sem bundle completo precisa ser rotulada como **pré-ORR exploratório**.

3. Padrão mínimo de conteúdo do bundle:
   - scorecards de todos os gates da sprint;  
   - pastas de evidência dos gates que testam o núcleo crítico;  
   - README com instruções de replay (pré-requisitos, comandos, caminhos);
   - qualquer desvio documentado (renome, reorganização) de forma explícita.

Bundle vazio ou inconsistente derrota o propósito de ter scorecards e ORR.

---

#### 6.4.6 Anti-gap #5 — Sanidade cruzada não é opcional para núcleos críticos

Risco identificado:

- o Truth-DB da S32 poderia estar “verde”, mas ao mesmo tempo ter quebrado ingestão, claims ou APIs de consumo.

Mandato permanente:

1. Toda sprint que mexer em núcleo crítico (Truth-DB, comitês, causalidade, etc.) deve conter, no mínimo:
   - uma seção de **sanidade cruzada** nos Capítulos 4 e 5;  
   - uma lista explícita de gates/suites antigos que serão rodados;  
   - resultados dessa execução (PASS/WARN/FAIL) e classificação de regressões.

2. ORR deve exigir:
   - um quadro-síntese de sanidade pós-sprint;  
   - explicações para qualquer regressão marcada como BLOQUEANTE ou NÃO-BLOQUEANTE.

3. Planejamento futuro:
   - sprints que dependem fortemente de ingestão/claims/truth precisam ser desenhadas juntas, com consciência dessa interdependência.

Sem sanidade cruzada, a sprint pode até ser “verdade” em si mesma, mas correndo o risco de destruir o resto do sistema.

---

#### 6.4.7 Riscos residuais da S32 — o que precisa ser vigiado

Mesmo com todos os anti-gaps, a S32 deixa riscos residuais que precisam entrar em radar explícito (e não em “memória oral”). Exemplos típicos:

1. **Cobertura limitada de tipos de claims**
   - Situação atual: v1 foca em um tipo de claim mais simples/estruturado.  
   - Risco: uso indevido do Truth-DB para claims não suportadas, gerando estados “tortos” ou pouco informativos.  
   - Mitigação:  
     - validações explícitas no `PromotionService`;  
     - erros claros para tipos não suportados;  
     - tasks em S33+ para ampliar cobertura com testes adequados.

2. **Lógica de contestação ainda simplificada**
   - Situação atual: v1 de contestação pode se limitar a estados simples (contestado, revisado, mantido).  
   - Risco: falta de nuance para casos complexos; risco de interpretar “contestada” como “falsa” ou vice-versa.  
   - Mitigação:  
     - documentar limites da v1 nas specs e no código;  
     - usar GO COM RESTRIÇÕES se o uso for mais amplo;  
     - planejar evolução em sprints de lógica/comitês.

3. **Observabilidade ainda em construção**
   - Situação atual: métricas mínimas existem, mas painéis/alertas podem ser rudimentares.  
   - Risco: dificuldades em detectar problemas sutis ou tendências longas (ex.: contestação subindo muito, mas sem alertas).  
   - Mitigação:  
     - tasks para enriquecer dashboards;  
     - criação de alertas básicos para thresholds críticos;  
     - envolvimento explícito do time de operação na evolução de métricas.

4. **Dependência de conhecimento de núcleo**
   - Situação atual: o modelo e os fluxos ainda exigem expertise do time que implementou a S32.  
   - Risco: novos membros ou times externos fazendo uso incorreto do Truth-DB por falta de documentação/demos.  
   - Mitigação:  
     - guias “how-to” reutilizáveis, baseados em cenários de teste reais;  
     - sessões de onboarding internas usando o bundle da S32 como material didático.

Cada risco residual deve ser mapeado para tasks concretas em Capítulo 7 ou para épicos futuros (ex.: S33, S34), com prioridade e dono.

---

#### 6.4.8 Mandatos estruturais da S32 para S33+ (e além)

Com base nos anti-gaps e riscos residuais, a S32 deixa alguns mandatos claros para o futuro:

1. **Núcleos críticos sempre com gates + bundle + ORR forte**
   - Qualquer sprint que introduzir ou alterar núcleo crítico deve repetir o padrão S32:  
     - gates dedicados;  
     - bundle robusto;  
     - ORR centrado em perguntas difíceis.

2. **Evolução por camadas, não por reescrita total**
   - O Truth-DB da S32 é o “chão” sobre o qual camadas futuras devem ser construídas (comitês, causalidade, blockchain).  
   - Rewrites radicais que ignorem invariantes, dados históricos ou bundles anteriores devem ser tratados como riscos de projeto, não como “refactors naturais”.

3. **Verdade como produto interno de plataforma**
   - O Truth-DB não é detalhe de infraestrutura; é um **produto interno** consumido por ingestão, comitês, UI, APIs e produtos externos.  
   - Isso implica:  
     - SLAs claros;  
     - expectativas formais de comportamento;  
     - alinhamento com squads de ingestão, comitês e produto.

4. **Cultura de evidência como requisito não funcional**
   - O jeito S32 de operar (scorecards, bundles, sanidade cruzada, ORR baseado em perguntas) deve virar padrão cultural para sprints que lidam com verdades e fatos.  
   - “Acreditar no código” deixa de ser opção; **só vale o que é demonstrável**.

---

#### 6.4.9 Síntese final do Bloco 4 (e fechamento do Capítulo 6)

Com este Bloco 4, o Capítulo 6 deixa explícito que:

- A S32 não é só uma sprint que implementou o Truth-DB e a Contestação v1;  
- Ela é a sprint que definiu **os limites aceitáveis e inaceitáveis** de como o Inspectah trata verdade e evidência na própria engenharia.

Os anti-gaps viram alarmes permanentes; os riscos residuais viram backlog consciente; e os mandatos estruturais viram linha de base para S33, S34, S35…

A mensagem final da S32 é simples e dura:  
> Se o sistema quer falar de verdade sobre o mundo, ele precisa primeiro ser honesto sobre si mesmo — e isso começa aqui, com o nível de rigor que este capítulo consolidou.

