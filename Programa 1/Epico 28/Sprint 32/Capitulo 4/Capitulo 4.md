# Inspectah — Sprint 32  
## Capítulo 4 — Execução & Evidências (Truth-DB, Blocos & Contestação v1)

> Este capítulo descreve **como a Sprint 32 será executada na prática**: fases, ordem de trabalho, relação com os gates S32_G0–G4, produção de evidências e estratégia de validação até o bundle final.

---

### 4.1 Estratégia geral de execução da S32

A execução da S32 segue três princípios:

1. **Primeiro fundação, depois fluxo, depois contestação**  
   - Fase 1: schema + invariantes (Truth-DB sólido).  
   - Fase 2: fluxo de promoção (claim → blocos → estado).  
   - Fase 3: fluxo de contestação (estado → contestação → novos blocos/estado).

2. **Gates como trilhos de execução**  
   - Cada fase visa deixar um gate verde (G1, G2, G3) com evidências claras.  
   - G0 abre a sprint (estrutura pronta); G4 fecha (bundle e ORR).

3. **Evidência como produto**  
   - A sprint não termina em “código que parece funcionar”, mas em **código + testes + scorecards + bundle reexecutável**.

---

### 4.2 Fases de execução e relação com os gates

A S32 é executada em cinco fases sequenciais (com sobreposição possível, mas não recomendada para o núcleo).

#### Fase 0 — Preparação & G0 (Scope & Baseline)

Objetivo: garantir que a sprint começa com docs, scripts e estrutura mínima em ordem.

Passos principais:
- Criar/atualizar os arquivos de docs da S32 em `docs/` (Capítulos 1–7).  
- Criar versões iniciais dos scripts:  
  - `bin/s32_g0_scope_and_baseline.sh`  
  - `bin/s32_g1_models_and_invariants.sh`  
  - `bin/s32_g2_promotion_flows.sh`  
  - `bin/s32_g3_contestation_flows.sh`  
  - `bin/s32_g4_orr_and_bundle.sh`  
- Garantir que diretórios `out/scorecards/`, `out/evidence/`, `out/bundles/` existem.

Execução do gate:
- Rodar `bin/s32_g0_scope_and_baseline.sh`.  
- Gerar `out/scorecards/S32_G0_scope_and_baseline.json`.  
- Corrigir qualquer falha óbvia (arquivos faltando, scripts quebrados) **antes** de seguir.

Evidências esperadas:
- Scorecard G0.  
- Log de execução do script (opcional, em `out/evidence/S32_G0_scope_and_baseline/`).

---

#### Fase 1 — Modelos, Migrações & Invariantes (G1, SA32_3)

Objetivo: implementar o núcleo de dados do Truth-DB (Bloco 2/C3) e garantir invariantes estruturais.

Passos principais:
1. Implementar/ajustar modelos em `app/truthdb/models.py` conforme especificação do Capítulo 3.  
2. Criar/ajustar migração `migrations/versions/XXXX_s32_truthdb_blocks.py`.  
3. Implementar testes de invariantes em `tests/truthdb/test_models_and_invariants.py`:
   - sem blocos órfãos;  
   - estados finais com DecisionBlock;  
   - histórico monotônico (sem deletar blocos em contestação);  
   - integridade de FKs.
4. Implementar `bin/s32_g1_models_and_invariants.sh` para:
   - aplicar migrações em banco de teste;  
   - rodar `pytest tests/truthdb/test_models_and_invariants.py`.

Execução do gate:
- Rodar `bin/s32_g1_models_and_invariants.sh`.  
- Ajustar modelos/migrações/testes até `out/scorecards/S32_G1_models_and_invariants.json` marcar `status = "PASS"` (ou, no máximo, `WARN` justificado).

Evidências esperadas:
- Scorecard G1.  
- Logs em `out/evidence/S32_G1_models_and_invariants/` (migrações + testes).  
- Referência cruzada com as invariantes listadas em Capítulo 2.

---

#### Fase 2 — Fluxo de Promoção (PromotionService & G2, SA32_1)

Objetivo: tornar funcional o fluxo claim → blocos → estado de verdade para o tipo de claim prioritário.

Passos principais:
1. Implementar `PromotionService` em `app/truthdb/services.py` conforme Capítulo 3/Bloco 3.  
2. Implementar helpers (se necessário) em `app/claims/adapters_truthdb.py` para mapear claims → Fact/EvidenceBlocks.  
3. Implementar testes de fluxo em `tests/truthdb/test_promotion_flows.py` cobrindo:
   - promoção bem-sucedida de claims válidas;  
   - respeito às invariantes (ex.: estados finais com DecisionBlock);  
   - comportamento em casos de erro.
4. Implementar métricas mínimas em `app/truthdb/metrics.py` e integrá‑las ao `PromotionService`:
   - tentativas, sucessos, erros, latência.
5. Implementar `bin/s32_g2_promotion_flows.sh` para:
   - subir ambiente de teste;  
   - preparar claims de exemplo (fixtures ou scripts auxiliares);  
   - invocar o fluxo de promoção (via CLI, script ou job interno);  
   - rodar testes relevantes.

Execução do gate:
- Rodar `bin/s32_g2_promotion_flows.sh`.  
- Analisar `out/scorecards/S32_G2_promotion_flows.json` (taxas de sucesso, erros, métricas amostradas).  
- Ajustar implementação até `status = "PASS"` e métricas coerentes.

Evidências esperadas:
- Scorecard G2 com contagem de promoções testadas, sucessos/falhas e amostras de métricas.  
- Logs + dumps em `out/evidence/S32_G2_promotion_flows/` (inclusive snapshots de blocos/estados antes/depois em ao menos um cenário).

---

#### Fase 3 — Fluxo de Contestação (ContestationService & G3, SA32_2)

Objetivo: tornar funcional o fluxo de contestação contra estados de verdade existentes.

Passos principais:
1. Implementar `ContestationService` em `app/truthdb/services.py` (métodos `register_contestation` e `process_contestation`).  
2. Ajustar modelos se necessário (`ContestRecord`, vínculos com `TruthState` e `DecisionBlock`).  
3. Implementar testes de fluxo em `tests/truthdb/test_contestation_flows.py` cobrindo:
   - registro de contestações válidas;  
   - processamento com criação de DecisionBlock;  
   - atualização de `TruthState` (quando aplicável);  
   - preservação de histórico (nunca apagar blocos).  
4. Integrar métricas (`truthdb_contestation_rate`, `truthdb_flow_error_rate`, `truthdb_flow_latency_p95`) ao ContestationService.  
5. Implementar `bin/s32_g3_contestation_flows.sh` para:
   - preparar estados de verdade de teste (via Fase 2 ou fixtures);  
   - registrar contestações;  
   - processá‑las usando o fluxo real;  
   - checar consistência dos resultados.

Execução do gate:
- Rodar `bin/s32_g3_contestation_flows.sh`.  
- Analisar `out/scorecards/S32_G3_contestation_flows.json` (nº de contestações, distribuição de outcomes, métricas).  
- Ajustar implementação até `status = "PASS"` e invariantes preservadas.

Evidências esperadas:
- Scorecard G3.  
- Logs e dumps em `out/evidence/S32_G3_contestation_flows/`, com snapshots de `TruthState` e blocos antes/depois de pelo menos um cenário de contestação.

---

#### Fase 4 — Sanidade cruzada, regressões & G4 (Bundle + ORR)

Objetivo: consolidar o estado final da sprint, detectar regressões e montar o bundle S32.

Passos principais:
1. Executar **sanidade de regressão** em ingestão/claims (Sprints 21+, 24 etc.), usando scripts existentes:  
   - registrar no Capítulo 5 qualquer falha residual e sua avaliação de risco.  
2. Garantir que G0–G3 foram executados recentemente e estão verdes (ou com WARNs documentados).  
3. Implementar/ajustar `bin/s32_g4_orr_and_bundle.sh` para:
   - verificar scorecards G0–G3;  
   - checar presença de evidências mínimas;  
   - empacotar tudo em `out/bundles/inspectah_s32_evidence_bundle.zip`;  
   - gerar `out/scorecards/S32_G4_orr_and_bundle.json` com resumo.
4. Executar G4; ajustar qualquer detalhe que impeça integridade do bundle.

Evidências esperadas:
- Scorecard G4 (status final da sprint).  
- Bundle `inspectah_s32_evidence_bundle.zip` contendo:  
  - todos os scorecards G0–G4;  
  - logs principais de gates;  
  - dumps/snapshots de blocos/estados de cenários relevantes;  
  - README/guia de replay.

---

### 4.3 Evidências mínimas por estado-alvo (SA32_x)

Para facilitar o ORR e revisões futuras, o mapeamento de evidências por estado-alvo é:

- **SA32_1 — Fluxo claim → blocos → estado**  
  - Scorecard: `S32_G2_promotion_flows.json`.  
  - Evidências: pasta `out/evidence/S32_G2_promotion_flows/` com logs + dumps.

- **SA32_2 — Contestação v1 funcional**  
  - Scorecard: `S32_G3_contestation_flows.json`.  
  - Evidências: `out/evidence/S32_G3_contestation_flows/`.

- **SA32_3 — Invariantes em código/testes**  
  - Scorecard: `S32_G1_models_and_invariants.json`.  
  - Evidências: `out/evidence/S32_G1_models_and_invariants/` (logs de migração + testes).

- **SA32_4 — Observabilidade mínima Truth-DB**  
  - Referenciada em G2/G3 (amostras em scorecards);  
  - Documentada em Capítulo 5 (como visualizar métricas).

- **SA32_5 — Bundle reexecutável**  
  - Scorecard: `S32_G4_orr_and_bundle.json`.  
  - Evidência principal: `inspectah_s32_evidence_bundle.zip`.

- **SA32_6 — Sem regressões críticas em ingestão/claims**  
  - Evidência: execução de gates históricos + notas no Capítulo 5;  
  - Qualquer exceção tratada como dívida formal.

---

### 4.4 Rituais, checkpoints e disciplina de execução

Para reduzir risco de surpresas no fim da sprint, a S32 adota a seguinte cadência mínima:

- **Check-in inicial (após Fase 0):**  
  - Confirmar G0 verde;  
  - Validar que modelos/migrações planejados no Capítulo 3 ainda fazem sentido;  
  - Ajustar plano se houver mudanças drásticas de dependências.

- **Checkpoint de fundação (meio da Fase 1):**  
  - Rodar G1 em modo “early draft” para pegar problemas de schema/invariantes cedo.

- **Checkpoint de promoção (meio da Fase 2):**  
  - Rodar G2 com poucos casos de teste;  
  - Validar que o fluxo principal funciona antes de sofisticar casos de borda.

- **Checkpoint de contestação (meio da Fase 3):**  
  - Rodar G3 com 1–2 contestações simples;  
  - Ajustar lógica v1 antes de expandir.

- **Pré-ORR (início da Fase 4):**  
  - Validar se G0–G3 estão verdes;  
  - Planejar montagem do bundle e escrita das partes relevantes do Capítulo 5.

---

### 4.5 Diretrizes para implementação & CI

- Todos os scripts `s32_g*.sh` devem ser integráveis em pipelines de CI (GitHub Actions), seguindo padrão das sprints anteriores (S20+).  
- Os testes `tests/truthdb/*` devem rodar de forma determinística em ambiente de CI e local.  
- Ao final da sprint, deve existir pelo menos um workflow que permita rodar **todos os gates da S32** em sequência (ou por job único) para facilitar revalidações.

---

### 4.6 Como este Capítulo 4 se conecta aos demais

- Ele operacionaliza o **"o quê"** descrito no Capítulo 1.  
- Executa os **estados-alvo e gates** definidos no Capítulo 2.  
- Usa a **arquitetura e filemap** do Capítulo 3 como guia de onde escrever código e testes.  
- Alimenta o Capítulo 5 com material para ORR e operação pós-sprint e o Capítulo 6 com learnings/anti-gaps.

Com este Capítulo 4, a Sprint 32 deixa de ser apenas um desenho elegante e passa a ter uma rota de execução concreta, com pontos claros de validação e evidências obrigatórias até o bundle final.

