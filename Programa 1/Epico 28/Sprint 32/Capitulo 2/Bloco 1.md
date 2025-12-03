# Inspectah — Sprint 32
## Capítulo 2 — Bloco 1
### Estados-alvo da Sprint 32 (SA32_x)

> Este bloco detalha os **estados-alvo** da Sprint 32. Eles são o elo direto entre o contexto do Capítulo 1 e os gates, testes e evidências que virão nos próximos blocos.

---

#### SA32_1 — Fluxo claim → blocos → estado de verdade (vivo para 1 tipo de claim)

**Enunciado:**  
Até o fim da Sprint 32, para pelo menos **um tipo de claim prioritário** definido pelo Programa 2, o Inspectah consegue executar o fluxo completo:

> claim estruturada (P2) → blocos (FactBlock, EvidenceBlock, DecisionBlock) → estado de verdade em Truth-DB

com as seguintes propriedades mínimas:

1. **Implementado em código**  
   - Existe um serviço (ou conjunto de serviços) dedicado(s), por exemplo `PromotionService`, responsável por orquestrar a promoção.  
   - O mapeamento claim → blocos (quais campos viram o quê) está documentado e versionado.

2. **Cober tura por testes de integração**  
   - Há pelo menos um teste de integração em `tests/truthdb/test_promotion_flows.py` que:  
     - cria ou injeta claims de exemplo (fixtures) do tipo prioritário;  
     - chama o fluxo de promoção real;  
     - inspeciona os blocos criados e o estado de verdade final;  
     - verifica que as invariantes relevantes são respeitadas.

3. **Gate dedicado e scorecard**  
   - O gate `S32_G2_promotion_flows` existe, é executável e está verde na conclusão da sprint.  
   - O scorecard `out/scorecards/S32_G2_promotion_flows.json` descreve claramente:  
     - quantas promoções foram testadas;  
     - quantas falharam e por quê;  
     - eventuais warnings/dívidas aceitas.

4. **Evidências armazenadas**  
   - Há evidências em `out/evidence/S32_G2_promotion_flows/`, incluindo:  
     - logs de execução do gate;  
     - dumps ou snapshots dos blocos e estados de verdade gerados em pelo menos um cenário;  
     - qualquer script auxiliar usado para gerar dados de teste.

**Interpretação prática:**  
Se alguém, no ORR, quiser ver “como uma claim vira verdade na prática”, deve bastar rodar o fluxo do G2 e ler o scorecard/evidências para entender.

---

#### SA32_2 — Contestação v1 funcional, com trilha de auditoria completa

**Enunciado:**  
Até o fim da S32, o Inspectah consegue pegar um estado de verdade existente e executar o fluxo de contestação end-to-end:

1. Registrar uma contestação formal (quem contesta, motivo, contra qual estado/claim).  
2. Processar essa contestação (por fluxo automatizado ou stub de comitê).  
3. Gerar novos blocos, incluindo pelo menos um `DecisionBlock` que justifique o resultado.  
4. Atualizar o estado de verdade sem apagar o histórico anterior.  
5. Deixar trilha auditável suficiente para replay.

**Propriedades mínimas:**

1. **API/serviço de contestação**  
   - Existe uma interface clara (função, serviço, rota interna) para registrar contestações.  
   - O formato de entrada é definido (quem, o quê, por quê, contra qual estado).

2. **Processamento concreto (não apenas stub vazio)**  
   - A contestação aciona um fluxo real (ainda que simples) que resulta em:  
     - manutenção do estado de verdade; ou  
     - alteração do estado de verdade; ou  
     - marcação em algum estado intermediário, conforme o modelo definido por Pearl/Programa 3.

3. **Blocos e estados atualizados**  
   - Novos blocos são gravados (pelo menos um `DecisionBlock`).  
   - O estado de verdade é atualizado com referência explícita a esse novo bloco.  
   - O histórico anterior permanece consultável.

4. **Testes e gate específico**  
   - Há testes de integração em `tests/truthdb/test_contestation_flows.py` cobrindo pelo menos um cenário de contestação bem-sucedida.  
   - O gate `S32_G3_contestation_flows` está verde ao final da sprint, com scorecard correspondente.

5. **Evidências para auditoria**  
   - Evidências em `out/evidence/S32_G3_contestation_flows/` mostram, na prática:  
     - estado de verdade antes;  
     - detalhes da contestação;  
     - blocos gerados;  
     - estado de verdade depois.

**Interpretação prática:**  
Se alguém perguntar “Como eu contesto uma verdade no Inspectah e vejo o que aconteceu?”, a resposta deve estar **demonstrada** pelos cenários de SA32_2 + G3.

---

#### SA32_3 — Invariantes críticas do Truth-DB explicitadas em código e testes

**Enunciado:**  
Até o fim da S32, as invariantes consideradas críticas para o Truth-DB e Sistema de Blocos:
- deixam de ser apenas ideias em documento;  
- passam a existir como testes automatizados e/ou asserts verificáveis.

**Escopo mínimo:**

1. **Integridade de blocos**  
   - Nenhum `FactBlock` fica sem vinculação a claim/entidade.  
   - Nenhum `DecisionBlock` fica sem vínculo com um estado de verdade/caso.

2. **Histórico monotônico**  
   - Contestações nunca deletam blocos; apenas acrescentam novos.  
   - Estados de verdade antigos são preservados para auditoria.

3. **Consistência estado ↔ decisão**  
   - Mudanças de estado “finais” (`true`, `rejected`, etc.) exigem `DecisionBlock` associado.

**Evidências de cumprimento:**
- Testes em `tests/truthdb/test_models_and_invariants.py` cobrindo os casos acima.  
- Gate `S32_G1_models_and_invariants` verde, com scorecard listando explicitamente quais invariantes foram checadas.

**Interpretação prática:**  
Se alguma dessas invariantes for violada em desenvolvimento ou em integração, isso deve aparecer como **falha de teste/gate**, não como surpresa em produção.

---

#### SA32_4 — Observabilidade mínima do Truth-DB acoplada ao stack 24/7

**Enunciado:**  
Até o fim da S32, o Truth-DB expõe, via stack de observabilidade padrão do Programa 1, pelo menos as métricas:

- `truthdb_promotion_success_rate`  
- `truthdb_contestation_rate`  
- `truthdb_flow_error_rate`  
- `truthdb_flow_latency_p95`

**Condições mínimas:**

1. **Emissão técnica**  
   - As métricas são emitidas em pontos claros do fluxo (promoção, contestação, erros, encerramento de fluxo).  
   - Não dependem de logs textuais manuais; usam o mecanismo oficial de métricas.

2. **Visualização prática**  
   - Existe ao menos um painel simples onde essas métricas podem ser vistas.  
   - O Capítulo 5 documenta como acessá-las rapidamente.

3. **Validação em gates**  
   - Pelo menos um gate (G2 e/ou G3) valida que as métricas estão sendo emitidas (mesmo que por meio de logs ou checagens auxiliares).

**Interpretação prática:**  
Se o Truth-DB começar a falhar silenciosamente, a culpa não pode ser da ausência de métricas básicas – elas precisam estar lá desde a S32.

---

#### SA32_5 — Bundle de evidências S32 reexecutável

**Enunciado:**  
Até o fim da S32, existe um bundle:

`out/bundles/inspectah_s32_evidence_bundle.zip`

que permite a um revisor/ORR:

- entender o que foi testado;  
- reexecutar cenários principais de promoção/contestação;  
- ver scorecards e logs no mesmo lugar.

**Conteúdo mínimo do bundle:**

- Scorecards `S32_G0` a `S32_G4`.  
- Logs dos scripts de gates (ou referências claras para arquivos maiores).  
- Dumps/snapshots de blocos e estados de verdade antes/depois de pelo menos um cenário-chave de promoção e um de contestação.  
- Um arquivo de instruções (ex.: `README_S32_BUNDLE.md`) explicando como fazer replay dos cenários.

**Interpretação prática:**  
O bundle S32 precisa ser suficiente para que alguém, com acesso ao repositório e a um ambiente de teste, consiga “refazer a sprint” nos pontos mais importantes, sem depender da memória de quem desenvolveu.

---

#### SA32_6 — Nenhuma regressão crítica em ingestão/claims

**Enunciado:**  
Até o fim da S32, o trabalho em Truth-DB/Blocos **não pode quebrar** de forma grave o que foi construído em ingestão/claims nas sprints anteriores.

Condições:

- Gates críticos de ingestão/claims de sprints relevantes (por exemplo, S21+ e S24) são executados ao menos em modo sanidade durante a S32.  
- Qualquer falha é:  
  - corrigida; ou  
  - registrada com justificativa e, se inevitável, tratada como dívida explícita no ORR.

**Interpretação prática:**  
A S32 adiciona uma camada de verdade/contestação, mas não “puxa o tapete” da ingestão. Se isso acontecer, é NO-GO conceitual até que seja resolvido ou conscientemente aceito pelo conselho.

---

Este Bloco 1 do Capítulo 2 fixa os **Estados-alvo SA32_1–SA32_6** como contrato verificável da sprint. Nos próximos blocos, esses estados serão mapeados a gates, métricas, invariantes e tasks de execução.

