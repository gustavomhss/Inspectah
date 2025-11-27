# 5.2 – Gates, Métricas & Definition of Done (Produto / UX / Narrativas) – v2 extremo

Este 5.2 pega o mapa de contexto e dores do 5.1 (P1–P5) e o transforma em **contratos de produto**: 

- quais **gates de produto/experiência** (GP0–GP4) precisamos passar;
- quais **métricas** serão usadas para dizer se estamos chegando lá;
- o que significa **DONE de produto** para o Capítulo 5 nesta sprint.

Tudo aqui é amarrado às três personas do 5.1 (A – analista/jornalista, B – cidadão curioso, C – curador interno) e aos problemas P1–P5:
- P1: falta de unidade “Caso Inspectah”;  
- P2: ausência de página única de caso para Persona A;  
- P3: inexistência de coleções temáticas mínimas para Persona B;  
- P4: curadoria interna sem ferramentas mínimas;  
- P5: zero métricas de produto/experiência.

Os gates de produto **não substituem** os gates técnicos G0–G8: eles se somam a eles. G0–G8 garantem que o motor Verdade & Interpretação funciona; GP0–GP4 garantem que esse motor gera algo utilizável e demonstrável.

---

## 5.2.1 – Papel dos gates de produto nesta sprint

Os gates de produto têm três funções centrais:

1. **Impedir autoengano de produto**  
   A sprint só pode se considerar bem-sucedida se, além de G0–G8, também entregar um mínimo de valor concreto para as personas A/B/C, medido pelos GP0–GP4.

2. **Forçar rastreabilidade de narrativas**  
   Cada “Caso Inspectah”, página de caso, coleção temática ou demo precisa ter lastro rastreável em Truth‑DB, Claims, Committees e Evidências.

3. **Criar baseline de métricas de produto**  
   Mesmo que as métricas ainda não sejam “boas”, é obrigatório começar a medi‑las. Pior do que métrica ruim é **nenhuma métrica**.

A partir disso, o Squad Verdade & Interpretação define **5 gates de produto** GP0–GP4, diretamente mapeados a P1–P5.

---

## 5.2.2 – Mapa dos Gates de Produto (GP0–GP4)

### GP0 – Enquadramento de produto consolidado (P1–P5 como contrato)

**Objetivo:** garantir que toda a camada de produto está construindo em cima de um entendimento único de **para quem** e **que problemas** a sprint ataca.

**Critérios:**
- O 5.1 v2 extremo está estável em `docs/sprint_xx_cap_5_1_contexto_produto.md` e é referenciado explicitamente em 5.2, 5.3 e 5.4.
- As três personas (A, B, C) e os problemas P1–P5 são citados nominalmente em 5.2–5.4; nenhum gate/feature de produto é inventado sem apontar para pelo menos uma persona + um P*.
- Os não‑objetivos (sem UI final, sem Fase 2, sem reputação avançada, etc.) são respeitados em todas as decisões de produto desta sprint.

**Como verificar:**
- Revisão de consistência: leitura cruzada de 5.1, 5.2, 5.3 e 5.4 confirmando que não há contradições nem “features órfãs” de persona/problema.

**Métrica qualitativa:**
- N_features_sem_persona_problema = 0 (nenhum elemento de produto é definido sem mapear para persona + P*).

---

### GP1 – Caso Inspectah como unidade de produto real (P1)

**Objetivo:** tirar “caso” da cabeça das pessoas e transformá‑lo em **unidade formal de produto**, com estrutura, ID, lastro na Truth‑DB e lugar no repositório.

**Critérios de aceitação:**
1. Existe uma **definição formal de "Caso Inspectah"** para esta fase, incluindo obrigatoriamente:
   - `case_id` estável;  
   - título;  
   - contexto/resumo curto;  
   - claims centrais (lista de IDs de `Claim` ou estrutura equivalente);  
   - evidências principais (links/refs para dados, documentos, fontes);  
   - decisões relevantes (`CommitteeDecision`, `DebunkIssue/DebunkTask` associados);  
   - estado atual de truth (estado consolidado dos `TruthRecord` relevantes);  
   - timeline resumida (subset legível de `TruthChangeEvent`).
2. Pelo menos **N_casos_canonicos_min** (parâmetro da sprint; ex.: 3 ou 5) estão definidos nesse formato.
3. Para cada caso canônico, é possível **reconstituir programaticamente** (ou via procedimento explícito) o estado do caso a partir da Truth‑DB — sem edição manual paralela.

**Artefatos esperados:**
- Especificação de Caso Inspectah em `docs/cases/case_model.md` ou equivalente, incluindo exemplo concreto.
- Arquivos de caso (por exemplo, `docs/cases/case_<slug>.yaml`) ou estrutura similar, cada um apontando para IDs reais em banco/Truth‑DB.
- Script/notebook de verificação em `bin/sXX_check_cases.sh` ou `docs/cases/case_check.ipynb`, que:
  - lê as definições de caso;
  - verifica que todos os IDs de Claim/Truth/etc. existem;
  - falha se algum caso estiver “pendurado”.

**Métricas:**
- `N_casos_canonicos` – número de casos canônicos definidos.
- `N_casos_sem_lastro_truthdb` – contador de casos definidos cuja verificação falha. Deve ser 0.

**Condição de GO para GP1:**
- `N_casos_canonicos >= N_casos_canonicos_min` e `N_casos_sem_lastro_truthdb = 0`.

---

### GP2 – Página / endpoint único de caso para Persona A (P2)

**Objetivo:** dar à analista/jornalista (Persona A) uma visão única de caso que reúna tudo que ela precisa: afirmação, claims, evidências, decisões, estado de truth e timeline.

**Critérios de aceitação:**
1. Existe um **ponto de entrada unificado** por caso, que pode ser:
   - uma rota de UI (ex.: `/cases/:case_id`); ou
   - um endpoint de API (ex.: `GET /api/cases/:case_id`), descrito em 5.3.
2. Para cada caso canônico de GP1, esta visão única exibe, em uma estrutura legível:
   - título e resumo do caso;
   - as claims centrais com um rótulo claro (texto + tipo de claim, ex.: numérica, comparativa, etc.);
   - evidências principais (com indicação de fonte/origem);
   - decisões relevantes de comitê (com síntese de veredito);
   - estado atual de truth (ex.: FACT, CONTESTED) e breve explicação;
   - timeline de truth resumida, ordenada no tempo.
3. A partir dessa visão, existe um **caminho explícito** (links ou ações) para:
   - abrir a evidência bruta (dados, documentos, fontes originais);
   - navegar para detalhes de claims, se necessário.
4. A Persona A consegue, em **no máximo K ações (cliques/passo)**, partir de:
   - uma afirmação/ID de caso → abrir a página única de caso → abrir uma evidência principal.

**Artefatos esperados:**
- Definição da rota/endpoint de caso em 5.3, com contratos (payloads) documentados.
- Capturas de tela, exemplos de payloads JSON ou HTML para pelo menos os N casos canônicos, armazenados em `out/evidence/SXX_product_cases/`.
- Roteiro em 5.4 (“Fluxo Persona A”) descrevendo passo a passo como realizar a tarefa com exemplos reais.

**Métricas:**
- `case_view_click_distance_A`: número de ações (cliques/steps) entre “afirmação/ID de caso” e “evidência principal aberta” para Persona A, medido em pelo menos 1–2 casos.
- `N_casos_com_pagina_unica`: quantos casos canônicos possuem visão unificada funcional.

**Condição de GO para GP2:**
- `N_casos_com_pagina_unica = N_casos_canonicos` (todos os casos canônicos têm visão unificada);
- `case_view_click_distance_A <= K_max` definido (por exemplo, K_max = 4).

---

### GP3 – Coleções temáticas mínimas para Persona B (P3)

**Objetivo:** permitir ao cidadão curioso (Persona B) navegar o Inspectah por **temas**, via coleções de casos que fazem sentido como “vitrines de verdade”.

**Critérios de aceitação:**
1. Existem pelo menos **T_min temas prioritários** definidos (exemplos típicos: Economia, Dados oficiais vs discurso, Contestação tardia).
2. Para cada tema, há uma **coleção explícita** de Casos Inspectah, contendo:
   - `collection_id`, título da coleção, descrição curta, lista de `case_id`.
3. Existe uma forma simples (UI ou endpoint) de:
   - listar todas as coleções disponíveis;  
   - listar os casos de uma coleção;  
   - a partir de um caso da coleção, acessar a visão unificada de caso (GP2).
4. Nenhum caso canônico fica “sem coleção”: todo caso canônico faz parte de pelo menos uma coleção.

**Artefatos esperados:**
- Arquivo(s) de coleções, por exemplo `docs/cases/collections.yaml`, definindo tema → lista de casos.
- Especificação em 5.3 da rota/endpoint para coleções (ex.: `/collections`, `/collections/:collection_id`).
- Evidências de navegação (prints, gravação, outputs de API) em `out/evidence/SXX_product_collections/`.

**Métricas:**
- `N_temas_com_colecao` – número de temas com coleções definidas.
- `N_casos_em_alguma_colecao` – número de casos canônicos presentes em pelo menos uma coleção.
- `coverage_casos_em_colecoes = N_casos_em_alguma_colecao / N_casos_canonicos`.

**Condição de GO para GP3:**
- `N_temas_com_colecao >= T_min` (T_min definido na sprint, ex.: 3);
- `coverage_casos_em_colecoes = 1.0` (todos os casos canônicos em pelo menos uma coleção).

---

### GP4 – Curadoria interna funcional + métricas de produto ativas (P4 + P5)

**Objetivo:** dar ao curador interno (Persona C) caminhos oficiais para trabalhar com casos/coleções e plantar **métricas de produto/experiência** mensuráveis.

**Critérios de aceitação – Curadoria:**
1. Existe pelo menos **um fluxo mínimo de curadoria** documentado, por exemplo:
   - “Encontrar candidatos a caso” → “Formalizar Caso Inspectah” → “Adicionar a coleções temáticas” → “Gerar demo/artefatos”.
2. Esse fluxo usa **apenas caminhos oficiais** (APIs, scripts, UI) definidos pela sprint, e não SQL solto ou manipulação manual de banco.
3. O fluxo foi executado de ponta a ponta pelo menos uma vez, com evidência registrada em 5.4.

**Critérios de aceitação – Métricas de produto:**
1. A sprint define um conjunto mínimo de métricas de produto, por exemplo:
   - `N_casos_canonicos`;
   - `N_temas_com_colecao` e `coverage_casos_em_colecoes`;
   - `case_view_click_distance_A` (média ou worst‑case medida em 1–2 casos);
   - eventualmente, `tempo_para_montar_caso` em fluxo de curadoria.
2. Há um **script, notebook ou job** que:
   - calcula essas métricas;
   - persiste a saída em um artefato reprodutível (ex.: `out/evidence/SXX_product_metrics/metrics.json`).
3. Os valores dessas métricas são mencionados em pelo menos um documento de revisão (Cap. 2, 5.4 ou ORR), para evitar que fiquem “na gaveta”.

**Artefatos esperados:**
- Descrição de fluxo de curadoria em 5.4 (passo a passo com referências a scripts/rotas).
- Script de métricas, ex.: `bin/sXX_product_metrics.sh` ou um notebook com instruções claras.
- Saída de exemplo das métricas em `out/evidence/SXX_product_metrics/`.

**Métricas:**
- `N_fluxos_curadoria_documentados` – deve ser ≥ 1.
- `N_execucoes_curadoria_com_evidencia` – execuções reais do fluxo com evidência registrada; deve ser ≥ 1.
- `N_metricas_produto_calculadas` – número de métricas diferentes calculadas pela sprint; deve ser ≥ 1 (idealmente, 3+).

**Condição de GO para GP4:**
- Pelo menos um fluxo de curadoria completo documentado e executado (com evidência em `out/`);
- Métricas de produto definidas, calculadas e registradas no pacote de evidências da sprint.

---

## 5.2.3 – Como GP0–GP4 se conectam a G0–G8 e ao bundle da sprint

Os gates GP0–GP4 não criam uma segunda camada de “bureaucracia”, mas sim uma **camada visível de produto** que conversa com a camada técnica.

- Em G5 (Truth‑DB) e G6 (Observabilidade), passamos a verificar também a integridade das ligações entre Truth‑DB e Casos Inspectah (scripts de checagem de casos podem ser chamados de dentro de gates técnicos, se fizer sentido).
- Em G7 (ORR), o relatório oficial da sprint passa a incluir uma seção “Cap. 5 – Produto & Experiência”, resumindo o estado de GP0–GP4.
- Em G8 (GO/NO‑GO), a decisão de GO passa a depender não só de G0–G6 verdes, mas também de um estado mínimo aceitável para GP1–GP4. Uma sprint que falha totalmente em GP1–GP4 pode até gerar um bom protótipo técnico, mas **não entregou o Mínimo Produto de Verdade** desta fase.

No bundle oficial da sprint (zip de evidências), além de scorecards técnicos e evidências de execução, passam a entrar também:
- definições de casos e coleções (ou referências a elas dentro do repo);
- capturas/payloads de páginas de caso e coleções;
- scripts e outputs de métricas de produto;
- roteiros de demo/curadoria.

Isso garante que qualquer revisor futuro consiga não só reexecutar os gates técnicos, mas também **rever a camada de produto** como ela existia nesta sprint.

---

## 5.2.4 – Definition of Done de Produto para o Cap. 5 nesta sprint

O Cap. 5 é considerado **DONE** do ponto de vista de produto/experiência somente se todas as condições abaixo forem verdadeiras:

1. **GP0 – Enquadramento claro**  
   5.1 estável, personas e problemas P1–P5 mapeando explicitamente cada gate/feature de produto.

2. **GP1 – Casos canônicos sólidos**  
   - Existem pelo menos `N_casos_canonicos_min` Casos Inspectah.
   - Todos estão ancorados em Claims/TruthRecords reais (verificação automática ou semi‑automática).

3. **GP2 – Página/endpoint único para cada caso canônico**  
   - Cada caso possui visão unificada atendendo Persona A.
   - O caminho até evidências principais é curto (≤ K_max ações).

4. **GP3 – Coleções temáticas mínimas**  
   - Existem coleções para pelo menos T_min temas.
   - 100% dos casos canônicos estão em pelo menos uma coleção.

5. **GP4 – Curadoria funcional + métricas vivas**  
   - Pelo menos um fluxo completo de curadoria foi documentado e executado.
   - Pelo menos um conjunto de métricas de produto foi calculado e registrado.

6. **Evidência consolidada**  
   - Todos os artefatos de produto (casos, coleções, prints/payloads de páginas, scripts de métricas, saídas de métricas, roteiros de curadoria/demos) estão:
     - versionados no repositório (docs/scripts/configs); e
     - incluídos ou referenciados no bundle de evidências da sprint.

Se qualquer uma dessas condições não for atendida, o Cap. 5 permanece “em progresso” e a sprint não pode ser declarada como tendo entregado o Mínimo Produto de Verdade — mesmo que todos os gates técnicos estejam verdes.

---

## 5.2.5 – Checklist rápido para o squad

Antes de declarar 5.2 “ok para avançar”, o Squad Verdade & Interpretação pode usar o seguinte checklist:

- Cada gate GP0–GP4 aponta claramente para pelo menos uma persona e um problema P* do 5.1?
- As métricas definidas são, de fato, calculáveis com o que a sprint implementa?
- Há um caminho claro para verificar cada critério (scripts, docs, demos), ou estamos confiando em “bom senso”?  
- O que foi prometido aqui cabe dentro das restrições de escopo (sem UI final, sem Fase 2 disfarçada)?

Se a resposta for **sim** para todas as perguntas, o 5.2 está pronto para servir de base para o 5.3 (Arquitetura & Filemap de Produto) e o 5.4 (Execução & Evidências de Produto). Caso contrário, o problema deve ser resolvido aqui, não empurrado para a frente.