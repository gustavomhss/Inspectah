# Inspectah — Sprint 32
## Capítulo 5 — Bloco 3
### Roteiro da Sessão de ORR & Painel de Perguntas (Truth-DB + Contestação v1)

> Este bloco descreve **como conduzir a sessão de ORR da Sprint 32 na prática**: ordem dos passos, demos obrigatórias, quais perguntas o conselho precisa conseguir responder e como usar os artefatos da S32 (scorecards, evidências, bundle) durante a revisão.

---

#### 5.3.1 Estrutura sugerida da sessão de ORR da S32

A sessão de ORR pode ser organizada em cinco atos curtos e objetivos:

1. **Abertura & Escopo (5–10 min)**  
   - Relembrar o objetivo do ORR da S32 (Bloco 1): núcleo de verdade em operação.  
   - Confirmar que os pré-requisitos do Bloco 2 estão atendidos (gates, bundle, sanidade cruzada, ambiente congelado).

2. **Visão do Truth-DB & Sistema de Blocos v1 (10–15 min)**  
   - Explicar o modelo (FactBlock, EvidenceBlock, TruthState, DecisionBlock, ContestRecord) com 1–2 diagramas simples.  
   - Mostrar rapidamente como os modelos aparecem no código (`app/truthdb/models.py`) e nas migrações.

3. **Demo dos Fluxos de Promoção & Contestação (15–25 min)**  
   - Fluxo claim → blocos → estado (PromotionService + G2).  
   - Fluxo estado → contestação → novos blocos/estado (ContestationService + G3).  
   - Uso de logs/dumps das pastas de evidência para mostrar o antes/depois.

4. **Observabilidade & Sanidade Cruzada (10–15 min)**  
   - Mostrar métricas principais do Truth-DB.  
   - Apresentar resumo da sanidade pós-S32 em ingestão/claims.  
   - Pontuar qualquer regressão detectada e sua classificação.

5. **Decisão GO / GO COM RESTRIÇÕES / NO-GO (10–15 min)**  
   - Revisar critérios formais (definidos no Capítulo 5).  
   - Registrar decisão, restrições (se houver) e dívidas operacionais.

A sessão completa pode ser curta, desde que **cada passo se apoie em artefatos concretos**, não em opiniões.

---

#### 5.3.2 Painel de perguntas para o modelo de dados & invariantes

Durante a parte de modelo/invariantes, o conselho deve conseguir responder, olhando para código + testes + evidências:

1. **Compreensão do modelo**  
   - Pergunta: *“Conseguimos explicar o modelo do Truth-DB em 5 minutos para alguém de fora?”*  
   - Evidência:  
     - diagrama rápido ou trecho de `app/truthdb/models.py`;  
     - referência ao Bloco 2 do Capítulo 3.

2. **Blocos órfãos existem?**  
   - Pergunta: *“Há alguma forma de termos EvidenceBlock, DecisionBlock ou ContestRecord órfãos?”*  
   - Evidência:  
     - testes em `tests/truthdb/test_models_and_invariants.py`;  
     - scorecard `S32_G1_models_and_invariants.json` listando invariantes checadas.

3. **Estados finais sem decisão?**  
   - Pergunta: *“É possível termos um estado marcado como ‘final’ sem DecisionBlock associado?”*  
   - Evidência:  
     - validações em modelo/serviço;  
     - testes específicos em `test_models_and_invariants.py`;
     - logs de um caso concreto (antes/depois) se necessário.

4. **Histórico monotônico**  
   - Pergunta: *“Conseguimos provar que contestações não deletam blocos/estados, apenas acrescentam?”*  
   - Evidência:  
     - cenários de contestação em `test_contestation_flows.py`;  
     - dumps em `out/evidence/S32_G3_contestation_flows/` mostrando o crescimento do histórico.

Se alguma dessas perguntas não puder ser respondida de forma convincente com base nos artefatos, o ORR deve acionar um **flag de risco em invariantes**.

---

#### 5.3.3 Painel de perguntas para os fluxos de promoção (G2, SA32_1)

Para o fluxo claim → blocos → estado de verdade, o roteiro mínimo é:

1. **Demonstração end-to-end**  
   - Pegar uma claim de exemplo (idealmente realista) do tipo prioritário.  
   - Mostrar:  
     - a claim na base (ou no log de ingestão);  
     - a chamada a `PromotionService.promote_claim(claim_id)` (via REPL, script ou endpoint interno);  
     - o resultado em blocos/estado (queries simples no banco; dumps pré-gerados em `out/evidence/S32_G2_promotion_flows/`).

2. **Perguntas-chave**  
   - *“O que exatamente é promovido a fato aqui?”*  
     - Evidência: mapeamento em `claims/adapters_truthdb.py`.  
   - *“Que evidências mínimas são anexadas ao fato?”*  
     - Evidência: conteúdo de `EvidenceBlock` + `metadata`.  
   - *“Em que condições o status do TruthState é considerado final?”*  
     - Evidência: lógica em `_update_truth_state` e testes.  
   - *“Onde está o rastro da decisão?”*  
     - Evidência: `DecisionBlock`, `reasoning_summary`, vínculo no `TruthState`.

3. **Checagens de robustez**  
   - *“O que acontece se a claim estiver incompleta ou for de tipo não suportado?”*  
     - Evidência: testes negativos em `test_promotion_flows.py`;  
     - métrica de erro (`truthdb_flow_error_rate`) coletada.

O objetivo não é provar que o fluxo é perfeito, e sim que ele é **determinístico, previsível e audível**.

---

#### 5.3.4 Painel de perguntas para os fluxos de contestação (G3, SA32_2)

Para o fluxo de contestação, o roteiro mínimo é:

1. **Demonstração end-to-end**  
   - Escolher um `TruthState` criado na demo de promoção.  
   - Registrar uma contestação usando `ContestationService.register_contestation(...)`.  
   - Processar a contestação com `ContestationService.process_contestation(contest_id)`.  
   - Mostrar, usando dumps/logs, a evolução:  
     - `ContestRecord` criado;  
     - novo `DecisionBlock` (se aplicável);  
     - estado de verdade antes/depois.

2. **Perguntas-chave**  
   - *“Quem pode contestar e o que é registrado sobre essa pessoa/agente?”*  
     - Evidência: campos `contested_by`, `metadata` em `ContestRecord`.  
   - *“O que a v1 da lógica de contestação faz com o estado? Apenas marca como ‘contested’ ou já altera status?”*  
     - Evidência: implementação em `process_contestation`;  
     - cenários em `test_contestation_flows.py`.  
   - *“É possível que uma contestação suma sem deixar rastro?”*  
     - Evidência: garantias de persistência de `ContestRecord`;  
     - invariantes de histórico monotônico.

3. **Checagens de robustez**  
   - *“O que acontece se tentarmos processar uma contestação duas vezes?”*  
     - Evidência: tratamento em `process_contestation` + testes.  
   - *“Existe risco de loops estranhos (contestação que gera estados inconsistentes)?”*  
     - Evidência: limites v1 documentados (Capítulo 1/Capítulo 3) e cenários cobertos em teste.

O conselho precisa sair desta parte convencido de que o Truth-DB **não é um beco sem saída**: verdades podem ser desafiadas de forma rastreável.

---

#### 5.3.5 Painel de perguntas para observabilidade & sanidade cruzada

Nesta etapa, o foco é responder: *“Se isso quebrar, vamos perceber? E o que mais foi afetado?”*

1. **Métricas do Truth-DB**  
   - Perguntas:  
     - *“Onde eu vejo hoje o `truthdb_promotion_success_rate`?”*  
     - *“Onde eu vejo `truthdb_flow_error_rate` e `truthdb_flow_latency_p95`?”*  
     - *“Se o Truth-DB travar ou começar a falhar massivamente, o que nos avisa?”*  
   - Evidência: painéis, endpoint de métricas, exemplos de séries.

2. **Sanidade pós-S32 em ingestão/claims**  
   - Perguntas:  
     - *“Que gates/suites de ingestão/claims foram rodados após a S32?”*  
     - *“Quais falharam, e como essas falhas foram classificadas (bloqueante vs não-bloqueante)?”*  
   - Evidência: resumo de sanidade (Bloco 2), logs e anotações das regressões.

Se a resposta honesta a “como sabemos que o Truth-DB está saudável hoje?” for “não sabemos direito”, o ORR deve registrar isso como **risco de observabilidade** e considerar GO COM RESTRIÇÕES ou NO-GO.

---

#### 5.3.6 Uso do bundle da S32 durante o ORR

O bundle `inspectah_s32_evidence_bundle.zip` deve ser tratado, na sessão de ORR, como **protagonista**, não como extra:

- Ao demonstrar fluxos, usar dumps da pasta `out/evidence/` incluída no bundle.  
- Ao discutir invariantes, abrir arquivos de log de testes/migrações dentro do bundle.  
- Ao falar de reexecução, navegar pelo README do bundle e mostrar que qualquer membro do conselho conseguiria, em tese, reexecutar G1–G3 em outro ambiente.

A prática recomendada é conduzir parte do ORR **diretamente a partir de um bundle “limpo”**, extraído em uma pasta vazia, para simular o ponto de vista de um auditor externo.

---

#### 5.3.7 Como este Bloco 3 se conecta à decisão final

- Se as perguntas deste painel forem respondidas com confiança, usando artefatos concretos, o conselho terá base sólida para aplicar os **critérios de GO/GO COM RESTRIÇÕES/NO-GO** definidos no Capítulo 5.  
- Se houver perguntas sem resposta ou baseadas apenas em opinião, essas lacunas devem ser tratadas como **riscos explícitos**, afetando a decisão.

Este Bloco 3, portanto, transforma o ORR de uma conversa solta numa **inspeção guiada**, centrada em perguntas difíceis e respostas ancoradas em código, testes, métricas e evidências da Sprint 32.