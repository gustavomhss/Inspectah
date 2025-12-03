# Inspectah — Sprint 32 — Truth-DB 24/7 & Contestação v1

## Capítulo 1 — Contexto & Problemas a Resolver

### 1.1 Contexto macro

A Sprint 32 continua o Épico E28 (S29–S35), focado em levar o Inspectah para um modo de operação 24/7 sólido, com ciclos fechados de ingestão → interpretação → verdade/contestações → exposição, amarrados em evidências e observabilidade.

Após as S29, S30 e S31, assumimos que:

- Programa 1 já oferece um Data Hub operando 24/7 com ingestão estável das fontes prioritárias, console de fontes e painéis básicos de saúde.
- Programa 2 já transforma conteúdo em claims, entidades e sinais com trilha de logs mínima, sob governança do Squad Verdade & Interpretação.
- Existem hooks iniciais entre ingestão, interpretação e Truth-DB, mas ainda sem um ciclo robusto de promoção/contestação operando em produção.

A Sprint 32 tem como foco **colocar o Truth-DB e o Sistema de Blocos em modo de operação 24/7**, com fluxos mínimos, porém reais, de promoção e contestação, amarrados a evidências, logs e scorecards, sem ainda entrar na camada mais rica de produtos finais (Fact Cards, battlefield de narrativas, etc.).

### 1.2 Problemas a resolver

1. Não existe hoje um **fluxo completo, automatizado e auditável** de claim → blocos → estado de verdade, operando 24/7.
2. Contestação ainda é conceito de blueprint: não há um fluxo executável com entradas claras, trilha de evidências e decisões registradas.
3. Truth-DB e Sistema de Blocos ainda não possuem **invariantes operacionais** explícitos (o que nunca pode quebrar) nem observabilidade acoplada.
4. Falta um **filemap concreto e scripts de gates** específicos da S32 para Truth-DB/Blocos, alinhados ao Sprint Playbook v3.
5. Não há um pacote de evidências (bundle S32) que permita ORR e auditoria pós-sprint sobre o comportamento do Truth-DB em cenário realista.

### 1.3 Fora de escopo imediato

Para manter a S32 finita e executável, ficam explicitamente fora de escopo (empurrados para S33–S35 e/ou outros épicos):

- UI avançada de casos, battlefield de narrativas, painéis “quem ganha com isso?”, “mentiras em circulação agora” e derivados.
- Modo completo de governança humana de alto impacto (comitês humanos, workflows de aprovação complexos, SLAs contratuais).
- Qualquer integração real com serviços externos de anchoring em blockchain além de um lacre mínimo de prova de conceito.
- Otimizações pesadas de performance (tuning fino de queries, sharding, multi-região etc.).
- Automação completa dos agentes de debunking avançado e radar de manipulação (apenas ganchos mínimos quando necessário).

### 1.4 Riscos, apostas e decisões pré-tomadas

- Risco: escopo “verdade e contestação” tende a inflar. Mitigação: estados-alvo e gates muito concretos; tudo que não cabe vira input para S33–S35.
- Aposta: é melhor ter um **fluxo enxuto, porém verificado e auditável**, do que um Truth-DB parcialmente mágico e impossível de testar.
- Decisão: Truth-DB e Sistema de Blocos seguem o blueprint v2 do Sistema de Blocos e as decisões do Programa 3 v3 — qualquer divergência deve ser documentada.
- Decisão: scripts de gates da S32 seguem o Sprint Playbook v3 (Cap. 2 e 4) e produzem scorecards JSON + evidências em `out/`.

---

## Capítulo 2 — Estados-alvo, Gates, Métricas & Invariantes

### 2.1 Estados-alvo (SA)

SA32_1 — Fluxo claim → Truth-DB:
Ao final da S32, pelo menos um tipo de claim prioritário (ex.: “afirmação factual simples baseada em notícia”) percorre, de ponta a ponta, o fluxo claim → blocos (FactBlock, EvidenceBlock, DecisionBlock) → estado de verdade, com logs e evidências persistidas.

SA32_2 — Contestação executável v1:
Ao final da S32, é possível registrar uma contestação para um estado de verdade existente, gerar um caso de reavaliação, acionar um fluxo mínimo de análise (agentes/comitê) e registrar a decisão resultante em novos blocos, tudo com trilha de auditoria.

SA32_3 — Invariantes de Truth-DB explícitos e testados:
Ao final da S32, existe um conjunto de invariantes formais (e.g., em testes, asserts, contratos) garantindo que blocos não perdem vínculo com evidências, que estados de verdade são monotônicos em termos de trilha de decisão e que contestações não apagam histórico.

SA32_4 — Observabilidade mínima acoplada ao Truth-DB:
Ao final da S32, pelo menos 3 métricas operacionais do Truth-DB/Blocos estão expostas (via logs/metrics) e integradas ao stack de observabilidade (Programa 1), permitindo ver taxa de promoção, taxa de contestação e erros por tipo.

SA32_5 — Bundle de evidências S32 reproduzível:
Ao final da S32, existe um bundle `out/bundles/inspectah_s32_evidence_bundle.zip` que permite reexecutar os principais fluxos de promoção/contestação em ambiente de revisão (ORR), com scripts declarados e scorecards versionados.

SA32_6 — Nenhuma regressão grave nos fluxos de ingestão/claims:
Ao final da S32, todos os gates críticos de Sprints anteriores ligados a ingestão e claims continuam verdes (ou com justificativa explícita), garantindo que colocar o Truth-DB em operação não quebrou o pipeline anterior.

### 2.2 Gates e scorecards

G0 — S32_G0_scope_and_baseline:
- Checa existência dos docs da S32 (Cap. 1–7) em `docs/`.
- Valida que estados-alvo, filemap e scripts existem.
- Gera `out/scorecards/S32_G0_scope_and_baseline.json` com checklist de escopo.

G1 — S32_G1_models_and_invariants:
- Roda testes de modelo do Truth-DB e Sistema de Blocos.
- Valida invariantes estruturais (relacionamentos, estados válidos, enums, migrações aplicadas).
- Gera `out/scorecards/S32_G1_models_and_invariants.json`.

G2 — S32_G2_promotion_flows:
- Executa cenários de promoção claim → blocos → estado de verdade.
- Verifica logs, evidências e consistência dos estados.
- Gera `out/scorecards/S32_G2_promotion_flows.json`.

G3 — S32_G3_contestation_flows:
- Executa cenários de contestação e reavaliação.
- Checa integridade da trilha de blocos, ausência de apagamento de histórico e estados finais coerentes.
- Gera `out/scorecards/S32_G3_contestation_flows.json`.

G4 — S32_G4_orr_and_bundle:
- Valida a construção do bundle S32.
- Checa que todos os scorecards G0–G3 estão presentes e verdes.
- Gera `out/scorecards/S32_G4_orr_and_bundle.json` e confirma `out/bundles/inspectah_s32_evidence_bundle.zip`.

### 2.3 Métricas & observabilidade

Métrica 1 — `truthdb_promotion_success_rate`:
- Proporção de promoções bem-sucedidas vs tentativas, por tipo de claim.

Métrica 2 — `truthdb_contestation_rate`:
- Número de contestações registradas por intervalo de tempo e por tipo de caso.

Métrica 3 — `truthdb_flow_error_rate`:
- Erros por etapa (promoção, contestação, gravação de blocos) com tags para diagnóstico.

Métrica 4 — `truthdb_latency_p95`:
- Latência p95 de um fluxo completo claim → estado de verdade (em cenário de teste controlado).

Todas as métricas devem aparecer na stack de observabilidade padrão do Inspectah (decisão de infra do Programa 1), ainda que em dashboards simples.

### 2.4 Invariantes & no-regressions

- Nenhuma contestaçao pode apagar blocos existentes; toda reavaliação é sempre “por adição” (novos blocos, novos estados), nunca por destruição.
- Um estado de verdade só pode mudar se existir um DecisionBlock associado, com referência explícita a evidências e motivo da mudança.
- Nenhum bloco pode ficar “solto”: todo FactBlock deve estar ligado a pelo menos uma claim/entidade e pelo menos uma EvidenceBlock.
- Scripts S32 não podem alterar migrações já consolidadas em Sprints anteriores; apenas acrescentar novas migrações versionadas.
- Gates de Sprints anteriores relacionados ao pipeline de ingestão/claims não podem ser desativados ou burlados para “fazer a S32 passar”.

---

## Capítulo 3 — Arquitetura & Filemap

### 3.1 Visão de arquitetura

A arquitetura da S32 conecta três grandes componentes:

1. **Truth-DB Core**: modelos, migrações, serviços de persistência e APIs internas para blocos e estados de verdade.
2. **Promotion & Contestation Services**: serviços que traduzem outputs do Programa 2 (claims, entidades, sinais) em blocos e estados, e orquestram contestações.
3. **Orquestração & Observabilidade**: scripts de gates, jobs de teste/replay e integração com a stack de logs/metrics.

A visão macro:

- Programa 2 continua responsável por gerar claims estruturadas e sinais.
- Programa 3 (Truth-DB + Blocos) recebe esses artefatos e cuida de promoção/contestação + estados de verdade.
- Programa 1 garante que os jobs e serviços rodem em ambiente 24/7 com logs e métricas exportados.
- Programa 4 ainda não entra na camada de UI avançada, apenas consome estados consolidados de verdade para futuros produtos.

### 3.2 Componentes e contratos

Componentes principais:

- `TruthDbModel` e modelos de blocos (FactBlock, EvidenceBlock, DecisionBlock, AnchorBlock).
- Serviços `PromotionService` e `ContestationService`.
- API interna (e/ou handlers) para registrar promoções e contestações.
- Adaptadores para consumir claims do Programa 2 (ex.: via filas, tabelas intermediárias ou APIs internas).
- Scripts de gates em `bin/` e testes em `tests/truthdb/`.

Contratos principais:

- Contrato entre Programa 2 e Programa 3: schema de claims e mapping para blocos.
- Contrato entre serviços de contestação e Truth-DB: como registrar uma contestação, quais campos são obrigatórios, como referenciar evidências.
- Contrato de evidências: onde ficam guardadas (path, schema) e como são ligadas aos blocos.

### 3.3 Filemap S32

Sugestão de filemap (ajustável, mas obrigatório manter a essência):

- `docs/sprint_32_capitulo_1_contexto.md`
- `docs/sprint_32_capitulo_2_gates_e_metricas.md`
- `docs/sprint_32_capitulo_3_arquitetura_e_filemap.md`
- `docs/sprint_32_capitulo_4_execucao_e_evidencias.md`
- `docs/sprint_32_capitulo_5_orr_operacao_pos_sprint.md`
- `docs/sprint_32_capitulo_6_learnings_e_anti_gaps.md`
- `docs/sprint_32_capitulo_7_tasks.md`

Código e serviços:

- `app/truthdb/__init__.py`
- `app/truthdb/models.py`
- `app/truthdb/blocks.py`
- `app/truthdb/services/promotion.py`
- `app/truthdb/services/contestation.py`
- `app/truthdb/api/routes_truthdb.py` (se exposto via API interna)

Testes:

- `tests/truthdb/test_models_and_invariants.py`
- `tests/truthdb/test_promotion_flows.py`
- `tests/truthdb/test_contestation_flows.py`

Scripts e gates:

- `bin/s32_g0_scope_and_baseline.sh`
- `bin/s32_g1_models_and_invariants.sh`
- `bin/s32_g2_promotion_flows.sh`
- `bin/s32_g3_contestation_flows.sh`
- `bin/s32_g4_orr_and_bundle.sh`

Evidências e scorecards:

- `out/evidence/S32_G0_scope_and_baseline/…`
- `out/evidence/S32_G1_models_and_invariants/…`
- `out/evidence/S32_G2_promotion_flows/…`
- `out/evidence/S32_G3_contestation_flows/…`
- `out/evidence/S32_G4_orr_and_bundle/…`
- `out/scorecards/S32_G0_scope_and_baseline.json`
- `out/scorecards/S32_G1_models_and_invariants.json`
- `out/scorecards/S32_G2_promotion_flows.json`
- `out/scorecards/S32_G3_contestation_flows.json`
- `out/scorecards/S32_G4_orr_and_bundle.json`
- `out/bundles/inspectah_s32_evidence_bundle.zip`

### 3.4 Qualidade, padrões e dívidas aceitáveis

- Código deve seguir padrões já estabelecidos (tipagem, linters, organização de módulos).
- Testes mínimos de unidade + integração cobrindo os fluxos dos gates G1–G3.
- Dívidas aceitas: otimizações de performance, refatorações cosméticas e UI avançada para casos/contestações, desde que registradas no Cap. 6.

---

## Capítulo 4 — Execução, Evidências & Tasks brutas

### 4.1 Plano de execução (linha do tempo)

Fase 1 — setup e migrações:
- Criar branch da sprint S32 a partir de `main`/branch relevante.
- Implementar ou ajustar modelos de Truth-DB/Blocos e migrações.
- Escrever testes básicos de invariantes (G1).

Fase 2 — fluxos de promoção:
- Implementar `PromotionService` e integrações com claims do Programa 2.
- Escrever cenários de teste e scripts de gate G2.
- Coletar primeiras evidências.

Fase 3 — fluxos de contestação:
- Implementar `ContestationService` com fluxo mínimo de reavaliação.
- Escrever cenários de teste e scripts de gate G3.
- Garantir trilha de auditoria e não regressão.

Fase 4 — ORR e bundle:
- Finalizar scripts G4 e geração do bundle.
- Rodar todos os gates em sequência.
- Preparar notas de ORR (Cap. 5) e registrar learnings/anti-gaps (Cap. 6).

### 4.2 Execução dos gates & ORR

Cada gate S32 deve ser executado via script correspondente em `bin/`, com saída clara, fail-fast e scorecards JSON em `out/scorecards/`.

O ORR da S32 usa:

- Scorecards G0–G4.
- Logs de execução dos scripts.
- Evidence bundle S32.

### 4.3 Evidências & bundles

- Cada gate grava evidências em `out/evidence/S32_GX_*` com logs, snapshots de DB (quando aplicável) e artefatos relevantes.
- O bundle `out/bundles/inspectah_s32_evidence_bundle.zip` empacota:
  - Todos os scorecards G0–G4.
  - Sumário de logs.
  - Amostras de blocos e estados de verdade antes/depois de contestações.

### 4.4 Tasks brutas (para detalhar no Capítulo 7)

- Implementar/ajustar modelos e migrações de Truth-DB/Blocos.
- Implementar serviços de promoção e contestação com contratos claros.
- Escrever testes e scripts de gates G0–G4.
- Conectar métricas básicas do Truth-DB na stack de observabilidade.
- Produzir docs da S32 (Cap. 1–7) e garantir consistência com o filemap.

---

## Capítulo 5 — ORR & Operação pós-sprint

### 5.1 Escopo do ORR S32

- Validar se os estados-alvo SA32_1 a SA32_6 foram cumpridos.
- Garantir que os gates G0–G4 estão verdes (ou com exceções documentadas).
- Verificar se o Truth-DB pode rodar 24/7 com o nível atual de logs e métricas.

### 5.2 Checklists de operação e runbooks

- Runbook mínimo: como reexecutar um fluxo de promoção.
- Runbook mínimo: como registrar uma contestação e acompanhar o resultado.
- Passo a passo para rodar scripts S32 em ambiente de revisão.

### 5.3 Planos de fallback e reversão

- Se migrações de Truth-DB falharem, plano para rollback seguro.
- Se novos fluxos quebrarem ingestão/claims, como desativá-los temporariamente sem perda de dados.

### 5.4 Critérios de GO/NO-GO

GO:

- SA32_1–SA32_5 cumpridos sem regressões críticas.
- G0–G4 verdes.
- Nenhum incidente grave de integridade do Truth-DB.

NO-GO:

- Invariantes quebradas sem correção ou plano claro.
- Falha em reproduzir fluxos de promoção/contestação via bundle S32.
- Regressões significativas em gates de ingestão/claims de sprints anteriores.

---

## Capítulo 6 — Learnings, Roadmap & Anti-gaps

### 6.1 Conexão com lessons learned anteriores

- A S32 deve respeitar e atualizar, se necessário, o documento "Leasson Learned so far v1" e os lessons das S4, S25 e demais sprints relevantes.
- Qualquer problema recorrente (escopo difuso, falta de evidência, falta de scripts reprodutíveis) deve ser explicitamente listado e mitigado.

### 6.2 Gaps que S32 não fecha (e para onde vão)

- UI avançada de casos e battlefield de narrativas → empurrado para sprints futuras do Programa 4.
- Monitor anti-repetição de mentiras, estado emocional da cobertura, “quem ganha com isso?” etc. → futuros épicos focados em produtos de narrativa.
- Governança humana complexa e contratos comerciais → programas de governança e produto.

### 6.3 Ajustes no roadmap macro (Programas 1–4)

- Registrar se a maturidade do Truth-DB após S32 permite antecipar ou adiar features de produtos do Programa 4.
- Ajustar dependências entre Programas 2 e 3 conforme aprendizados sobre schema de claims e blocos.

### 6.4 Próximos passos imediatos (S33+)

- S33 e seguintes podem expandir cobertura de tipos de claims, enriquecer contestação, integrar com features avançadas de narrativa e UI.
- S32 entrega o “esqueleto vivo” de operação 24/7 do Truth-DB — S33+ refinam, escalam e expõem.

---

## Capítulo 7 — Tasks (visão consolidada)

### 7.1 Lista consolidada de tasks S32 (macro)

T32_01 — Consolidar e documentar o modelo de Truth-DB e blocos.
T32_02 — Implementar migrações de banco para suportar blocos e estados de verdade conforme Programa 3 v3.
T32_03 — Implementar `PromotionService` com cenários de promoção para pelo menos um tipo de claim prioritário.
T32_04 — Implementar `ContestationService` com fluxo mínimo de contestação e reavaliação.
T32_05 — Escrever testes para invariantes de modelo e fluxos de promoção/contestação.
T32_06 — Implementar scripts de gates G0–G4 em `bin/`.
T32_07 — Integrar métricas do Truth-DB à stack de observabilidade.
T32_08 — Produzir e manter atualizados os docs da S32 (Cap. 1–7).
T32_09 — Construir o bundle de evidências S32 e validar reexecução em ambiente de revisão.
T32_10 — Atualizar documentos de lessons learned e anti-gaps com aprendizados da S32.

### 7.2 Mapeamento tasks ↔ estados-alvo ↔ gates (macro)

- SA32_1 — T32_01, T32_02, T32_03, T32_05, G1, G2.
- SA32_2 — T32_01, T32_02, T32_04, T32_05, G1, G3.
- SA32_3 — T32_01, T32_02, T32_05, G1.
- SA32_4 — T32_07, G2, G3.
- SA32_5 — T32_06, T32_09, G4.
- SA32_6 — execução dos gates históricos + validação no ORR S32.

### 7.3 Sugestão de fatiamento em issues/PRs

- 1 PR para modelos + migrações + testes básicos (G1).
- 1 PR para fluxos de promoção + testes (G2).
- 1 PR para fluxos de contestação + testes (G3).
- 1 PR para scripts de gates, métricas e bundle (G4).
- 1 PR final para docs, lessons learned e ajustes finos.

### 7.4 Itens explicitamente adiados

- Suporte a múltiplos tipos complexos de claims (além do prioritário definido na S32).
- UI avançada para visualização de casos, contestações e linha do tempo de blocos.
- Integrações de alto volume com serviços externos de anchoring e analytics de narrativa.

---

Este documento funciona como especificação oficial da Sprint 32 segundo o Sprint Playbook v3, alinhado ao Programa 3 v3 e ao Roadmap Macro v3 dos Programas 1–4.

