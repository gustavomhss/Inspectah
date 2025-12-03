# Inspectah — Sprint 32  
## Capítulo 5 — ORR & Operação Pós-Sprint (Truth-DB, Blocos & Contestação v1)

> Este capítulo responde à pergunta: **“podemos colocar o Truth-DB + Contestação v1 para rodar sem medo, e em quais condições?”**. Ele define o processo de ORR da S32, os critérios de GO/NO-GO, o plano de operação pós-sprint e as dívidas operacionais que precisam ser vigiadas.

---

### 5.1 Objetivo do ORR da Sprint 32

A Sprint 32 não é “mais uma feature”: ela introduz o **núcleo de verdade** do Inspectah (Truth-DB + Sistema de Blocos + Contestação v1).

O objetivo do ORR da S32 é:

1. Verificar se o núcleo de verdade está **correto, íntegro e observável**.  
2. Confirmar se os fluxos de promoção e contestação funcionam de forma **repetível e auditável**.  
3. Decidir se o sistema está pronto para:
   - operar em ambiente compartilhado com ingestão/claims;  
   - suportar testes mais amplos (internos) de casos reais.

Saída do ORR: uma decisão explícita **GO / GO COM RESTRIÇÕES / NO-GO** para liberar o Truth-DB + Contestação v1 no ambiente-alvo definido (ex.: staging avançado ou pre-prod).

---

### 5.2 Pré-requisitos de ORR (checklist mínimo)

Antes de abrir a sessão de ORR, os seguintes itens precisam estar verdadeiros:

1. **Gates da S32 executados e consolidados**  
   - `S32_G0_scope_and_baseline.json` existe e reflete a estrutura da sprint.  
   - `S32_G1_models_and_invariants.json` em `status = "PASS"`.  
   - `S32_G2_promotion_flows.json` em `status = "PASS"`.  
   - `S32_G3_contestation_flows.json` em `status = "PASS"`.  
   - `S32_G4_orr_and_bundle.json` em `status = "PASS"` (ou, no pior caso, `"WARN"` com justificativa forte).

2. **Bundle de evidências pronto**  
   - Arquivo `out/bundles/inspectah_s32_evidence_bundle.zip` existe, abre sem erros e contém:  
     - todos os scorecards S32_G0–G4;  
     - pastas de evidência de G1, G2, G3;  
     - README de replay.

3. **Sanidade cruzada mínima com ingestão/claims**  
   - Gates/suites críticos das sprints de ingestão (ex.: S21+, S24) foram rodados pelo menos uma vez após a S32.  
   - Resultado: **nenhuma regressão BLOQUEANTE** (vide seção 5.7 para classificação).

4. **Ambiente de avaliação definido**  
   - ORR sabe exatamente qual ambiente está sendo avaliado (ex.: `staging-truthdb-v1`), com:
     - versão de código;  
     - versão de schema;  
     - configuração de métricas/logs.

Se qualquer item acima não estiver verdadeiro, a sessão de ORR deve ser adiada ou iniciada explicitamente como “pré-ORR exploratório”.

---

### 5.3 Painel de ORR: perguntas que precisam de resposta

Durante a sessão de ORR, o conselho (Jobs, Kleppmann, Lamport, Percy, Vitalik, Pearl, Stonebraker, Norvig, etc.) deve conseguir responder, a partir dos artefatos da S32, às seguintes perguntas:

1. **Modelo de dados & invariantes**  
   - Consegue-se explicar, em 5 minutos, o modelo do Truth-DB (FactBlock, EvidenceBlock, TruthState, DecisionBlock, ContestRecord) e suas relações?  
   - Existe evidência automática de que **não há blocos órfãos**?  
   - Estados finais de verdade sempre têm um DecisionBlock associado?  
   - O histórico de blocos e estados é monotônico (sem deleção silenciosa)?

2. **Fluxo de promoção**  
   - Dado um claim do tipo prioritário, é possível demonstrar o caminho end-to-end: claim → FactBlock/EvidenceBlock → TruthState → DecisionBlock (se aplicável)?  
   - Existe evidência de que erros de promoção são detectados e visíveis (scorecards + métricas)?

3. **Fluxo de contestação**  
   - Dado um estado de verdade, é possível mostrar contestação registrada, processada e refletida em novos blocos/estado?  
   - Fica claro, em logs/dumps, o antes/depois de uma contestação?  
   - É garantido que nenhuma contestação “some sem deixar rastro”?

4. **Observabilidade & métricas**  
   - Métricas mínimas (`truthdb_promotion_success_rate`, `truthdb_contestation_rate`, `truthdb_flow_error_rate`, `truthdb_flow_latency_p95`) estão aparecendo nos painéis/endpoint de métricas?  
   - A equipe consegue responder, olhando para métricas/logs: “o Truth-DB está saudável hoje?”

5. **Integração com ingestão/claims**  
   - Há evidência de que a S32 não quebrou ingestão/claims/glue existente?  
   - Se houve regressão, ela está bem documentada, com plano e prioridade para correção?

6. **Reexecução & auditabilidade**  
   - Dado o bundle da S32, é possível reexecutar G1, G2, G3 em outro ambiente e obter resultados consistentes?  
   - É possível, a partir dos artefatos, reconstruir a linha do tempo de uma decisão de verdade específica?

As respostas devem ser baseadas em **demonstrações com artefatos reais**, nunca em “acho que sim”.

---

### 5.4 Critérios formais de GO / GO COM RESTRIÇÕES / NO-GO

#### 5.4.1 Critério de GO pleno

A S32 recebe **GO** para o ambiente-alvo quando todas as condições abaixo são verdadeiras:

1. Todos os gates S32_G0–G4 em `status = "PASS"`.  
2. Não há evidência de corrupção de dados, perda de histórico ou violação de invariantes críticas.  
3. Fluxos de promoção e contestação operam de forma repetível, com no mínimo:
   - taxa de sucesso aceitável nos cenários de teste;  
   - nenhuma falha silenciosa (erros são logados/metricados).  
4. Métricas mínimas do Truth-DB são coletadas e visualizáveis.  
5. Sanidade cruzada com ingestão/claims mostra, no máximo, regressões NÃO-BLOQUEANTES, com planos claros de correção.  
6. O conselho não identifica riscos ocultos graves não capturados pelos testes.

#### 5.4.2 Critério de GO COM RESTRIÇÕES

Decisão intermediária, aceitável quando:

1. Truth-DB e Contestação v1 estão funcionalmente corretos, mas:
   - há limitações de performance conhecidas;  
   - há bugs não-críticos conhecidos;  
   - ou há cobertura de testes limitada em alguns cenários não centrais.

2. As restrições são explicitadas, por exemplo:
   - “apenas uso interno por analistas”;  
   - “apenas subset de claims de fonte X”;  
   - “sem integração automática com produto externo ainda”.

3. Existe um plano concreto para remover restrições em sprints futuras (registrado nas Tasks da S32 ou no backlog de sprints seguintes).

#### 5.4.3 Critério de NO-GO

A S32 recebe **NO-GO** se qualquer condição abaixo for verdadeira:

1. Evidência ou suspeita forte de corrupção de dados, perda de histórico ou violação grave de invariantes.  
2. G1, G2 ou G3 em `status = "FAIL"` sem workaround aceitável.  
3. Inexistência ou quebra do bundle de evidências (não há como auditar o que foi feito).  
4. Risco alto de quebra da ingestão/claims ou de outras partes centrais do sistema.  
5. Falta de visibilidade mínima de métricas/logs do Truth-DB (não é possível saber se está saudável).

Em caso de NO-GO, a Sprint 32 é considerada **tecnicamente incompleta** do ponto de vista de operação. O código pode continuar existindo em branch/feature flag, mas não é promovido ao ambiente-alvo.

---

### 5.5 Operação Pós-Sprint: como rodar o Truth-DB & Contestação v1

Uma vez que a S32 tenha GO (pleno ou com restrições), a operação mínima do Truth-DB + Contestação v1 envolve:

#### 5.5.1 Runbook diário de operação

1. **Checar métricas do Truth-DB**  
   - Verificar, no painel de métricas ou endpoint, se:
     - `truthdb_promotion_success_rate` está em faixa esperada;  
     - `truthdb_flow_error_rate` não explodiu;  
     - `truthdb_contestation_rate` faz sentido (nem zero absoluto, nem explosão anômala);  
     - `truthdb_flow_latency_p95` está dentro dos limites definidos.

2. **Checar logs de erro críticos**  
   - Filtrar logs relacionados a `PromotionService` e `ContestationService`.  
   - Investigar ocorrências repetidas de erros de banco, invariantes, timeouts.

3. **Rodar um “healthcheck lógico”**  
   - Executar um script simples de verificação (ex.: `python -m scripts.truthdb_healthcheck`) que:  
     - pega uma claim de teste;  
     - promove;  
     - contesta;  
     - checa se blocos/estados estão nos lugares corretos.

4. **Registrar resumo diário**  
   - Pequeno log ou nota (pode ser automatizado) com:  
     - anomalias detectadas;  
     - número de promoções/contestações do dia;  
     - qualquer incidente relevante.

#### 5.5.2 Tratamento de incidentes

Em caso de incidente envolvendo o Truth-DB (ex.: falha massiva de promoção, contestações presas, aumento brusco de erros):

1. **Isolar sintoma**  
   - Identificar se o problema é de:  
     - ingestão/claims;  
     - banco/infra;  
     - serviços de promoção/contestação;  
     - camada de métricas/logs.

2. **Ativar modo de contenção**  
   - Se necessário, reduzir uso de contestações automáticas;  
   - limitar certos tipos de claims;  
   - pausar jobs de promoção em lote.

3. **Coletar evidências**  
   - Salvar dumps adicionais de blocos/estados em um diretório específico da ocorrência.  
   - Anotar IDs de claims/casos afetados.

4. **Acionar plano de correção**  
   - Usar os artefatos da S32 (modelos, serviços, testes) para reproduzir o problema em ambiente de teste.  
   - Corrigir e criar/regredir um teste que capture o bug.

5. **Registrar post-mortem curto**  
   - Causa raiz;  
   - impacto;  
   - correção;  
   - mudanças no runbook ou nos testes.

---

### 5.6 Integração com sprints futuras (S33+)

A partir do ponto de vista de operação, a S32 define algumas **expectativas para sprints seguintes**:

1. **Ampliação de escopo de claims**  
   - S33+ podem estender o tipo de claim suportado pelo Truth-DB, mas devem:
     - atualizar adaptadores em `claims/adapters_truthdb.py`;  
     - criar novos testes de promoção;  
     - manter invariantes e métricas.

2. **Refinamento da lógica de decisão**  
   - A lógica v1 de promoção/contestação pode ser simplificada; sprints futuras podem:  
     - integrar com comitês de agentes;  
     - incorporar scores de confiança;  
     - sofisticar estados de verdade.  
   - Qualquer refinamento deve manter compatibilidade com o modelo e o histórico criados na S32.

3. **Camada de produtos (Programa 4)**  
   - UIs e painéis avançados (battlefield de narrativas, Fact Cards, etc.) devem tratar o Truth-DB como fonte de verdade, respeitando:  
     - estados;  
     - blocos;  
     - contestações.

4. **Evolução do bundle e do ORR**  
   - Sprints futuras podem enriquecer o bundle (mais logs, mais métricas), mas não reduzir o padrão mínimo estabelecido pela S32.

---

### 5.7 Anexo: classificação de regressões para a S32

Para efeitos de ORR, regressões detectadas na sanidade cruzada podem ser classificadas como:

- **BLOQUEANTE**  
  - Corrupção de dados ou risco real de tal;  
  - quebra de invariantes centrais do Truth-DB;  
  - indisponibilidade grave de ingestão/claims;  
  - impossibilidade de rodar gates de sprints anteriores.

- **NÃO-BLOQUEANTE, ALTA PRIORIDADE**  
  - Falhas funcionais em cenários importantes, mas com workaround claro;  
  - gaps de observabilidade relevantes (ex.: ausência de métricas em subset crítico);  
  - testes flaky em parte do pipeline, mas com impacto delimitado.

- **NÃO-BLOQUEANTE, MÉDIA/BAIXA PRIORIDADE**  
  - Erros em caminhos raros;  
  - pequenas inconsistências em logs ou naming;  
  - melhorias cosméticas em scorecards ou bundle.

A decisão GO / GO COM RESTRIÇÕES / NO-GO deve referenciar explicitamente esta classificação, para manter o histórico claro.

---

### 5.8 Síntese final do Capítulo 5

- A Sprint 32 só está “entregue” quando:  
  - Truth-DB + Contestação v1 passam pelos gates G0–G4;  
  - o bundle de evidências existe e é reexecutável;  
  - o ORR consegue responder às perguntas-chave sobre modelo, fluxos e observabilidade;  
  - a decisão de GO/NO-GO é tomada com base em evidências, não em intuição.

- Este capítulo transforma a S32 de um conjunto de PRs em um **módulo operacional** do Inspectah:  
  - com runbooks;  
  - com critérios explícitos de risco;  
  - com compromisso de evolução contínua nas próximas sprints.

A partir daqui, o Capítulo 6 vai capturar o que aprendemos durante essa jornada e como evitar, nas próximas sprints, qualquer repetição de gaps que ainda tenham escapado nesta primeira versão do Truth-DB em operação.

