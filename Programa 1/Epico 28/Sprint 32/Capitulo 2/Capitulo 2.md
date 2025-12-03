# Inspectah — Sprint 32
## Capítulo 2 — Estados-alvo, Gates, Métricas & Invariantes

> Capítulo 2 traduz o “porquê” e o recorte do Capítulo 1 em **condições verificáveis**: estados-alvo concretos (SA32_x), gates (`S32_Gx_*`), métricas de operação e invariantes que o Truth-DB/Sistema de Blocos não pode violar.

---

### 2.1 Estados-alvo da Sprint 32 (SA32_x)

Cada estado-alvo é escrito de forma **testável** e mapeado a gates, métricas e evidências.

**SA32_1 — Fluxo claim → blocos → estado de verdade (vivo para 1 tipo de claim)**  
Até o fim da S32, para pelo menos **um tipo de claim prioritário** definido pelo Programa 2, o sistema consegue executar o fluxo completo:

> claim estruturada (P2) → blocos (FactBlock, EvidenceBlock, DecisionBlock) → estado de verdade em Truth-DB

com as seguintes propriedades mínimas:
- Fluxo implementado em serviço(s) dedicado(s) (`PromotionService` ou equivalente).  
- Cobertura por teste(s) de integração em `tests/truthdb/test_promotion_flows.py`.  
- Gate `S32_G2_promotion_flows` verde.  
- Evidências salvas em `out/evidence/S32_G2_promotion_flows/` (logs, dumps de blocos/estados).

**SA32_2 — Contestação v1 funcional, com trilha de auditoria completa**  
Até o fim da S32, é possível pegar um estado de verdade existente e:

1. Registrar uma contestação formal contra esse estado.  
2. Processar a contestação (fluxo mínimo, porém completo).  
3. Gerar novos blocos (incluindo pelo menos um `DecisionBlock`).  
4. Atualizar o estado de verdade, sem apagar o histórico anterior.  
5. Deixar trilha auditável (blocos + logs) suficiente para replay.

Evidências de cumprimento:
- Cenários end-to-end em `tests/truthdb/test_contestation_flows.py`.  
- Gate `S32_G3_contestation_flows` verde.  
- Evidências em `out/evidence/S32_G3_contestation_flows/`.

**SA32_3 — Invariantes críticas do Truth-DB explicitadas em código e testes**  
Até o fim da S32, pelo menos o seguinte conjunto de invariantes precisa estar:

- Documentado neste capítulo (2.4).  
- Implementado como testes e/ou asserts cobrindo:
  - integridade referencial entre blocos;  
  - monotonicidade do histórico (sem apagamento/operação destrutiva silenciosa);  
  - consistência entre estados de verdade e DecisionBlocks.

Evidências de cumprimento:
- Testes em `tests/truthdb/test_models_and_invariants.py`.  
- Gate `S32_G1_models_and_invariants` verde.  
- Scorecard `out/scorecards/S32_G1_models_and_invariants.json` explicitando invariantes checadas.

**SA32_4 — Observabilidade mínima do Truth-DB acoplada ao stack 24/7**  
Até o fim da S32, o Truth-DB expõe ao menos as métricas:

- `truthdb_promotion_success_rate` (por tipo de claim).  
- `truthdb_contestation_rate` (por tipo de caso/claim).  
- `truthdb_flow_error_rate` (por etapa).  
- `truthdb_flow_latency_p95` (latência p95 de fluxo claim → estado de verdade em cenário de teste).

Essas métricas devem:
- ser emitidas usando a infraestrutura de métricas definida pelo Programa 1;  
- ser consultáveis nos dashboards mínimos da sprint;  
- ter print/log ou checagem automatizada em pelo menos um gate (G2/G3).

**SA32_5 — Bundle de evidências S32 reexecutável (inspectah_s32_evidence_bundle.zip)**  
Até o fim da S32, existe um bundle:

`out/bundles/inspectah_s32_evidence_bundle.zip`

contendo, no mínimo:
- todos os scorecards `S32_G0` a `S32_G4`;  
- logs relevantes de execução dos gates;  
- amostras de blocos e estados de verdade antes/depois de contestações (snapshots/minidumps);  
- um pequeno README/INSTRUÇÕES de replay (como reexecutar os principais cenários de promoção/contestação em ambiente de revisão).

**SA32_6 — Nenhuma regressão crítica em ingestão/claims (Sprints anteriores)**  
Até o fim da S32:
- Os gates críticos de ingestão/claims de sprints anteriores (ex.: S21+, S24) continuam passando em modo sanidade, ou têm qualquer exceção documentada em Capítulo 5.  
- Não há incidentes conhecidos de perda de dados, quebra de schema de claims ou interrupção da ingestão causados por mudanças de Truth-DB/Blocos.

Evidências de cumprimento:
- Notas de ORR em Capítulo 5 descrevendo a execução dos gates históricos.  
- Logs de execução desses gates incluídos (pelo menos em sumário) no bundle S32.

---

### 2.2 Gates da Sprint 32

Os gates são a materialização dos estados-alvo em scripts e scorecards. Todos vivem em `bin/` (scripts) e `out/scorecards/` (resultados).

#### G0 — S32_G0_scope_and_baseline

**Objetivo:** garantir que a sprint está minimamente preparada em termos de documentação e estrutura de arquivos.

- Script sugerido: `bin/s32_g0_scope_and_baseline.sh`.  
- Checa:
  - existência dos docs da S32: Capítulos 1–7 em `docs/`;  
  - presença dos arquivos-base de código e testes do Truth-DB/Blocos;  
  - presença dos scripts G1–G4 em `bin/`;  
  - integridade mínima da árvore de diretórios `out/evidence/` e `out/scorecards/`.

**Saída esperada:**  
- Scorecard JSON em `out/scorecards/S32_G0_scope_and_baseline.json` com campos como:
  - `status` ("PASS" | "FAIL");  
  - `docs_present` (bool);  
  - `scripts_present` (bool);  
  - `notes` (string / array de strings).

#### G1 — S32_G1_models_and_invariants

**Objetivo:** validar modelo de dados, migrações e invariantes estruturais/lógicas.

- Script sugerido: `bin/s32_g1_models_and_invariants.sh`.  
- Ações típicas:
  - aplicar migrações em um banco de teste;  
  - rodar `pytest tests/truthdb/test_models_and_invariants.py`;  
  - opcionalmente, rodar algum sanity check de schema/integração com claims.

**Saída esperada:**  
- Scorecard `out/scorecards/S32_G1_models_and_invariants.json` contendo:
  - `status`;  
  - lista de invariantes checadas;  
  - eventuais warnings (ex.: dívidas aceitas para S33+).

#### G2 — S32_G2_promotion_flows

**Objetivo:** validar na prática o fluxo claim → blocos → estado de verdade para o tipo de claim prioritário.

- Script sugerido: `bin/s32_g2_promotion_flows.sh`.  
- Ações típicas:
  - semear banco de teste com claims de exemplo (ou consumir fixtures geradas por Programa 2);  
  - chamar `PromotionService` ou rotas internas para promover claims;  
  - verificar blocos e estados resultantes;  
  - checar emissão de métricas de promoção e erros;  
  - salvar dumps em `out/evidence/S32_G2_promotion_flows/`.

**Saída esperada:**  
- Scorecard `out/scorecards/S32_G2_promotion_flows.json` contendo:  
  - `status`;  
  - número de promoções bem-sucedidas vs tentativas;  
  - contagem de erros por tipo;  
  - valores observados das métricas relevantes (quando fizer sentido).

#### G3 — S32_G3_contestation_flows

**Objetivo:** validar o fluxo de contestação end-to-end.

- Script sugerido: `bin/s32_g3_contestation_flows.sh`.  
- Ações típicas:
  - preparar um estado de verdade existente (usando fluxo de promoção real ou fixtures);  
  - registrar contestações contra esse estado;  
  - acionar fluxo de processamento (automatizado/stub de comitê);  
  - verificar novos blocos (incluindo `DecisionBlock`);  
  - checar atualização do estado de verdade mantendo histórico;  
  - checar métricas de contestação e erros;  
  - salvar evidências em `out/evidence/S32_G3_contestation_flows/`.

**Saída esperada:**  
- Scorecard `out/scorecards/S32_G3_contestation_flows.json` com:  
  - `status`;  
  - número de contestações processadas;  
  - distribuição de resultados (mantido, alterado, rejeitado etc.);  
  - métricas observadas (taxa de contestação, erros, latência se possível).

#### G4 — S32_G4_orr_and_bundle

**Objetivo:** consolidar a visão final da sprint (bundle, scorecards, sanidade) para ORR e operação 24/7.

- Script sugerido: `bin/s32_g4_orr_and_bundle.sh`.  
- Ações típicas:
  - verificar que `S32_G0`–`S32_G3` foram executados e estão verdes;  
  - validar presença de todos os scorecards e logs relevantes;  
  - empacotar artefatos em `out/bundles/inspectah_s32_evidence_bundle.zip`;  
  - gerar um sumário de estado para o ORR.

**Saída esperada:**  
- Scorecard `out/scorecards/S32_G4_orr_and_bundle.json` com:  
  - `status`;  
  - check de integridade do bundle;  
  - resumo de estados dos gates G0–G3;  
  - notas para ORR (links/paths para evidências).

---

### 2.3 Métricas & Observabilidade

A Sprint 32 define um **mínimo não negociável** de métricas para o Truth-DB.

**Métrica 1 — `truthdb_promotion_success_rate`**  
- **O que mede:** proporção de promoções bem-sucedidas / total de tentativas, segmentada por tipo de claim.  
- **Uso:** monitorar saúde do fluxo de promoção; quedas abruptas indicam problemas em schema, migrações ou serviços.

**Métrica 2 — `truthdb_contestation_rate`**  
- **O que mede:** número de contestações registradas por janela de tempo (e opcionalmente por tipo de caso/claim).  
- **Uso:** visibilidade sobre atividade de contestação; valores anômalos podem indicar abuso, bugs ou mudanças na política de promoção.

**Métrica 3 — `truthdb_flow_error_rate`**  
- **O que mede:** erros por etapa dos fluxos (promoção, contestação, gravação de blocos, migrações).  
- **Uso:** apontar gargalos e pontos frágeis; deve ser monitorada em conjunto com logs para diagnóstico.

**Métrica 4 — `truthdb_flow_latency_p95`**  
- **O que mede:** latência p95 de um fluxo completo claim → estado de verdade (em cenários de teste controlados).  
- **Uso:** garantir que o Truth-DB não se torne um gargalo perceptível; importante para experiências futuras em UI.

Requisitos gerais:
- As métricas devem ser emitidas usando a infraestrutura adotada pelo Programa 1 (por exemplo, Prometheus/OpenTelemetry ou equivalente).  
- Deve existir, no mínimo, um painel simples agregando essas métricas para ambientes de teste/integração.  
- O time deve documentar, no Capítulo 5, como visualizar essas métricas rapidamente em caso de incidentes.

---

### 2.4 Invariantes do Truth-DB & Sistema de Blocos

As invariantes abaixo são consideradas **críticas** para a S32 e devem ser refletidas diretamente em testes/contratos.

1. **Nenhum bloco solto**  
   - Todo `FactBlock` deve estar associado a pelo menos uma claim/entidade.  
   - Todo `EvidenceBlock` deve referenciar pelo menos um `FactBlock` ou claim/estado relevante.  
   - Todo `DecisionBlock` deve estar amarrado a um estado de verdade/caso.

2. **Histórico monotônico (sem apagamento destrutivo)**  
   - Contestações não apagam blocos existentes; toda reavaliação gera novos blocos.  
   - Estados de verdade antigos permanecem registráveis para auditoria, mesmo se superados.

3. **Estado de verdade sem DecisionBlock é inválido para certos estágios**  
   - Qualquer mudança relevante de estado (ex.: de `pending` para `true` ou `rejected`) deve ter um `DecisionBlock` associado.  
   - Estados marcados como finais (ex.: `true`, `rejected`) **devem** apontar para um `DecisionBlock`.

4. **Consistência de referências cruzadas**  
   - Não pode haver referências a blocos inexistentes (chaves estrangeiras quebradas).  
   - Operações de promoção/contestação devem falhar explicitamente se violarem integridade, e não “mascarar” o erro.

5. **Compatibilidade de versões/migrações**  
   - Migrações S32 não podem alterar retroativamente o significado de dados já consolidados sem plano explícito de migração.  
   - Em ambiente de teste, deve ser possível subir o schema do zero até a versão S32 e rodar todos os testes de invariantes.

Essas invariantes devem ser testadas em:
- `tests/truthdb/test_models_and_invariants.py` (nível estrutural/modelos).  
- `tests/truthdb/test_promotion_flows.py` / `test_contestation_flows.py` (nível de fluxo).

Falhas nessas invariantes devem quebrar `S32_G1`/`S32_G2`/`S32_G3`.

---

### 2.5 Critérios formais de GO/NO-GO da S32 (amarrados a Capítulo 5)

A partir dos estados-alvo e gates, o Capítulo 2 define a base objetiva para decisão de GO/NO-GO.

**GO (conceitual e técnico)**  
A sprint pode ser considerada GO se, e somente se:

1. SA32_1 a SA32_5 estão cumpridos, com evidências claras nos scorecards e no bundle.  
2. Não há regressões críticas em ingestão/claims (SA32_6), ou qualquer exceção está documentada e aceita no ORR.  
3. Gates `S32_G0`–`S32_G4` estão verdes ou com justificativas formais para algum warning mild (não crítico).  
4. Métricas mínimas do Truth-DB estão expostas e foram verificadas ao menos uma vez em ambiente de teste.  
5. Invariantes críticas (2.4) estão codificadas e validadas por testes.

**NO-GO (conceitual)**  
A sprint deve ser tratada como NO-GO se qualquer um dos pontos abaixo ocorrer:

- SA32_1 ou SA32_2 falham de forma substantiva (sem fluxo end-to-end de promoção ou contestação para o tipo de claim prioritário).  
- Invariantes estruturais são violadas e não há correção/waiver formal.  
- As métricas mínimas não estão disponíveis na stack de observabilidade.  
- O bundle `inspectah_s32_evidence_bundle.zip` não existe ou é claramente incompleto.  
- Regressões sérias em ingestão/claims não são mitigadas nem aceitas conscientemente.

---

### 2.6 Como este Capítulo 2 deve ser usado

- Pelo squad: como **checklist operacional**. Cada SA32_x e gate deve virar tasks e testes concretos (ver Capítulo 7).  
- Pelo conselho/ORR: como base objetiva para decidir GO/NO-GO, sem depender de narrativas vagas sobre “quase pronto”.  
- Pelo futuro (S33+): como régua de qualidade — qualquer extensão da lógica de verdade/contestação deve, no mínimo, respeitar o mesmo nível de rigor em estados-alvo, gates, métricas e invariantes.

Com este Capítulo 2, a Sprint 32 ganha um conjunto claro de **metas verificáveis** e mecanismos de validação, garantindo que o trabalho descrito no Capítulo 1 será cobrado em forma de código, testes, métricas e evidências reais.

