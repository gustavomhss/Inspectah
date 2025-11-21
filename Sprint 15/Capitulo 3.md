# Inspectah — Sprint 15  
## Capítulo 3 — Filemap, Arquitetura de Artefatos e Contrato de Layout (Revisão)

### 0. Papel deste capítulo

Este capítulo é o **contrato de layout e arquitetura da Sprint 15**. Ele responde, sem ambiguidade:

1. **Onde cada artefato da S15 vive no repositório?**  
2. **Como os componentes da S15 (Debunker, comitês, âncoras, anti‑canetada) se encaixam na arquitetura existente (S13–S14)?**  
3. **Que arquivos o Codex e os operadores devem tocar quando forem evoluir, rodar ou inspecionar a S15?**

A intenção é eliminar caça ao tesouro: qualquer pessoa deve conseguir sair deste capítulo diretamente para o arquivo certo, tanto para:

- ler (docs e evidências),
- editar (código, scripts, configs),
- rodar (gates T0–T8, pipelines de CI),
- ou auditar (scorecards, logs, âncoras).

Este capítulo **não é sugestão**: ele define o layout alvo da S15. Se o repositório divergente existir, a sprint precisa ou alinhar o repo a este layout, ou atualizar este capítulo explicitamente.

---

### 1. Princípios de organização da S15

Antes do filemap, alguns princípios explícitos que guiam a S15:

1. **Local único de verdade por conceito**  
   - Cada conceito novo da S15 (Debunker, comitês, âncoras, anti‑canetada) tem um diretório raiz único no código.  
   - Scripts de gates têm um nome e um lugar padronizados em `bin/`.  
   - Scorecards e evidências seguem o padrão `out/scorecards/` e `out/evidence/`.

2. **Alinhamento com o DNA e sprints anteriores**  
   - `Sprint 15/Capitulo N.md` segue a convenção de S1–S14.  
   - `docs/sprint_15_*.md` segue a mesma linha de overview/filemap/ORR das sprints anteriores.

3. **Layout previsível para o Codex**  
   - Arquivos e caminhos aqui descritos são o input oficial para prompts de geração de código.  
   - Quando o Codex criar um novo arquivo da S15, ele deve usar **exatamente** o caminho e nome definidos aqui.

4. **Scripts idempotentes, com saída sempre em `out/*`**  
   - Qualquer script de gate T0–T8 pode ser reexecutado sem quebrar o repo.  
   - Cada execução grava scorecards e evidências em locais estáveis.

---

### 2. Camadas de artefatos da Sprint 15

A S15 se distribui em quatro camadas principais:

1. **Planejamento e narrativa da sprint** (pasta `Sprint 15/`).
2. **Documentos operacionais** para humanos (pasta `docs/`).
3. **Código de domínio** (Debunker, comitês, âncoras, comandos anti‑canetada).  
4. **Scripts e pipelines de validação** (gates T0–T8, CI, evidências e scorecards).

#### 2.1 Planejamento e narrativa — `Sprint 15/`

- `Sprint 15/Capitulo 1.md`  
  - Visão de inteligência & blindagem (Debunker, comitês, âncoras, anti‑canetada).  
- `Sprint 15/Capitulo 2.md`  
  - Gates T0–T8, critérios de PASS/FAIL, riscos cobertos.  
- `Sprint 15/Capitulo 3.md`  
  - Este filemap + arquitetura (versão estabilizada).  
- `Sprint 15/Capitulo 4.md` (opcional, mas recomendado)  
  - Runbook Codex + operadores: comandos exatos, prompts, exemplos de uso.

#### 2.2 Documentos operacionais — `docs/`

- `docs/sprint_15_overview.md`  
  - Resumo executivo: o que é a S15, por que existe, principais decisões e artefatos.  
- `docs/sprint_15_filemap_e_arquitetura.md`  
  - Versão condensada deste capítulo (para consulta rápida, sem detalhes narrativos).  
- `docs/sprint_15_orr_summary.md`  
  - Mini‑ORR alinhado com T8: GO/NO_GO, riscos residuais, limitações e ganchos para S16.

#### 2.3 Código de domínio

**Debunker v1 — `inspectah/debunker/`**

- `inspectah/debunker/__init__.py`  
- `inspectah/debunker/engine.py`  
  - Funções principais esperadas:  
    - `select_risky_claims(...)`  
    - `analyze_claim(...)`  
    - `recommend_action(...)`
- `inspectah/debunker/rules.py`  
  - Regras de risco por domínio/tema (política, esporte, clima, fofoca, mandatos, projetos, ciência).  
- `inspectah/debunker/report_models.py`  
  - Tipos estruturados de relatório: `DebunkerReport`, `EvidenceItem`, `Contradiction`, etc.  
- `inspectah/debunker/fixtures/`  
  - Arquivos de fixtures por domínio, reutilizados em T2 e T4.

**Comitês V1/V2/V3 — `inspectah/committees/`

- `inspectah/committees/__init__.py`  
- `inspectah/committees/common.py`  
  - Tipos e enums: `CommitteeDecision`, `Vote`, `Reason`, status, helpers de log.  
- `inspectah/committees/v1_validator.py`  
  - Checagens puramente mecânicas (máquinas de estado, integridade, evidências mínimas).  
- `inspectah/committees/v2_multibrain.py`  
  - Orquestra múltiplos cérebros (modelos/policies), inclui Promotores do Diabo.  
- `inspectah/committees/v3_coherence.py`  
  - Verifica coerência global entre blocos/fatos relacionados, impede estados impossíveis.

**Âncoras em blockchain — `inspectah/anchors/`

- `inspectah/anchors/__init__.py`  
- `inspectah/anchors/merkle.py`  
  - Construção de Merkle trees e proofs.  
- `inspectah/anchors/chain_client.py`  
  - Cliente abstrato de chain (implementação v1 focada em uma testnet principal).  
- `inspectah/anchors/batcher.py`  
  - Lógica de batching por volume/tempo e agendamento de submissão.  
- `inspectah/anchors/registry.py`  
  - Registro interno de âncoras: mapeia batches para `anchor_id`, `chain_id`, `tx_hash` e expõe APIs de consulta.

**Anti‑canetada e integração com Sistema de Blocos**

- `inspectah/blocks/`  
  - Modelos de blocos, fatos, versões, claims e disputas (S13–S14).  
  - Extensões da S15 para:  
    - campos de referência a relatórios do Debunker;  
    - campos de referência a decisões de comitês;  
    - campos de referência a âncoras relevantes.

- `inspectah/commands/`  
  - Comandos de criação/atualização de blocos/fatos/versões/disputas.  
  - Implementação das regras anti‑canetada:  
    - nenhuma função de “mudar estado direto”;  
    - qualquer pedido de alta autoridade vira evento/disputa registrado.

Se existirem camadas de serviço (por exemplo, `inspectah/services/`), a S15 deve documentar aqui quais arquivos novos são criados para orquestrar Debunker, comitês e âncoras.

#### 2.4 Scripts, scorecards, evidências e CI

**Scripts de gates — `bin/`**

- `bin/s15_t0_sanity.sh`  
- `bin/s15_t1_contracts_and_states.sh`  
- `bin/s15_t2_debunker_offline.sh`  
- `bin/s15_t3_committees_flow.sh`  
- `bin/s15_t4_golden_scenarios.sh`  
- `bin/s15_t5_performance_and_cost.sh`  
- `bin/s15_t6_observability.sh`  
- `bin/s15_t7_ci_and_repro.sh`  
- `bin/s15_t8_go_no_go.sh`  
- `bin/s15_all_gates.sh` → orquestração completa T0–T8.

**Scorecards — `out/scorecards/`**

- `out/scorecards/S15_T0_sanity.json`  
- `out/scorecards/S15_T1_contracts_and_states.json`  
- `out/scorecards/S15_T2_debunker_offline.json`  
- `out/scorecards/S15_T3_committees_flow.json`  
- `out/scorecards/S15_T4_golden_scenarios.json`  
- `out/scorecards/S15_T5_performance_and_cost.json`  
- `out/scorecards/S15_T6_observability.json`  
- `out/scorecards/S15_T7_ci_and_repro.json`  
- `out/scorecards/S15_T8_go_no_go.json`

**Evidências — `out/evidence/`**

- `out/evidence/S15_T0_sanity/`  
- `out/evidence/S15_T1_contracts_and_states/`  
- `out/evidence/S15_T2_debunker_offline/`  
- `out/evidence/S15_T3_committees_flow/`  
- `out/evidence/S15_T4_golden_esporte/`  
- `out/evidence/S15_T4_golden_politica/`  
- `out/evidence/S15_T4_golden_clima/`  
- `out/evidence/S15_T4_golden_fofoca/`  
- `out/evidence/S15_T4_golden_mandatos/`  
- `out/evidence/S15_T4_golden_projetos/`  
- `out/evidence/S15_T4_golden_ciencia/`  
- `out/evidence/S15_T5_performance_and_cost/`  
- `out/evidence/S15_T6_observability/`  
- `out/evidence/S15_T7_ci_and_repro/`  
- `out/evidence/S15_T8_go_no_go/`  
  - `summary.json` → síntese da decisão.  
  - `MANIFEST.json` → índice dos artefatos usados em T8.

**Workflows de CI — `.ci/`**

- `.ci/sprint_15_gates.yml`  
  - Workflow principal da S15: encadeia T0–T7 (T8 pode ser manual ou automatizado).  
- `.ci/sprint_15_nightly.yml` (opcional)  
  - Executa subconjunto de T2–T6 com cargas de teste em ambiente de staging.

---

### 3. Mapa gate → scripts, artefatos e riscos

Esta seção conecta o Capítulo 2 (gates) ao filemap com ênfase em **riscos controlados**.

#### 3.1 T0 – Sanidade de base (S13–S14) e DoR

- Script: `bin/s15_t0_sanity.sh`  
- Scorecard: `out/scorecards/S15_T0_sanity.json`  
- Evidência: `out/evidence/S15_T0_sanity/`  
- Riscos: core instável, invariantes quebrados, rotas antigas de override.

#### 3.2 T1 – Contratos, estados e anti‑canetada

- Script: `bin/s15_t1_contracts_and_states.sh`  
- Scorecard: `out/scorecards/S15_T1_contracts_and_states.json`  
- Evidência: `out/evidence/S15_T1_contracts_and_states/`  
- Riscos: tipos incoerentes, estados inválidos, comandos com `force_set_state` escondido.

#### 3.3 T2 – Debunker v1 offline

- Script: `bin/s15_t2_debunker_offline.sh`  
- Scorecard: `out/scorecards/S15_T2_debunker_offline.json`  
- Evidência: `out/evidence/S15_T2_debunker_offline/`  
- Riscos: Debunker cego a claims perigosos, relatórios inúteis, certeza artificial em cenários ambíguos.

#### 3.4 T3 – Comitês V1/V2/V3 integrados

- Script: `bin/s15_t3_committees_flow.sh`  
- Scorecard: `out/scorecards/S15_T3_committees_flow.json`  
- Evidência: `out/evidence/S15_T3_committees_flow/`  
- Riscos: comitês decorativos, ausência de rejeições, conflitos globais passando em branco.

#### 3.5 T4 – Golden Scenarios

- Script: `bin/s15_t4_golden_scenarios.sh`  
- Scorecard: `out/scorecards/S15_T4_golden_scenarios.json`  
- Evidência: `out/evidence/S15_T4_golden_*` por domínio  
- Riscos: integração quebrada entre componentes em casos reais, atalhos de override surgindo só em produção.

#### 3.6 T5 – Performance e custo

- Script: `bin/s15_t5_performance_and_cost.sh`  
- Scorecard: `out/scorecards/S15_T5_performance_and_cost.json`  
- Evidência: `out/evidence/S15_T5_performance_and_cost/`  
- Riscos: camada de blindagem inviável em escala (latência/custo).

#### 3.7 T6 – Observabilidade e auditoria

- Script: `bin/s15_t6_observability.sh`  
- Scorecard: `out/scorecards/S15_T6_observability.json`  
- Evidência: `out/evidence/S15_T6_observability/`  
- Riscos: sistema opaco, difícil de auditar e investigar.

#### 3.8 T7 – CI e reprodutibilidade

- Script: `bin/s15_t7_ci_and_repro.sh`  
- Scorecard: `out/scorecards/S15_T7_ci_and_repro.json`  
- Evidência: `out/evidence/S15_T7_ci_and_repro/`  
- Riscos: gates que só funcionam “na máquina de quem fez”, divergência CI/local.

#### 3.9 T8 – Go/No‑Go

- Script: `bin/s15_t8_go_no_go.sh`  
- Scorecard: `out/scorecards/S15_T8_go_no_go.json`  
- Evidência: `out/evidence/S15_T8_go_no_go/`  
- Riscos: declarar vitória com gates quebrados, empurrar riscos estruturais para S16.

---

### 4. Workflows de CI e orquestração local

#### 4.1 CI — `.ci/sprint_15_gates.yml`

- Orquestra T0–T7 (T8 pode ser acionado manualmente em branch principal).  
- Publica scorecards em `out/scorecards/` e arquiva evidências relevantes.  
- Regras mínimas implementadas:  
  - PR não pode ser mergeado se T1, T2, T3, T4 ou T6 estiverem em NO_GO.  
  - T5 e T7 podem emitir WARN com limites configuráveis, se acordado em ORR.

#### 4.2 Nightly (opcional) — `.ci/sprint_15_nightly.yml`

- Reexecuta subconjunto de T2–T6 em ambiente de staging, com dados sintéticos ou recortes de produção.  
- Gera evidências versionadas por data (ex.: `out/evidence/S15_nightly_YYYYMMDD/`).

#### 4.3 Orquestração local — `bin/s15_all_gates.sh`

- Comando recomendado:

```bash
cd /Users/gustavoschneiter/Documents/Inspectah
PYTHONPATH=. bin/s15_all_gates.sh
```

- Responsabilidades:  
  - rodar, em ordem, `bin/s15_t0_*`…`bin/s15_t8_*`;  
  - imprimir um resumo final de PASS/FAIL por gate;  
  - apontar caminhos de scorecards e evidências em caso de falha.

---

### 5. Como este capítulo deve ser usado

- **Pelo Codex:**  
  - para saber onde criar/modificar arquivos da S15;  
  - para preencher scripts e módulos com o comportamento especificado nos Capítulos 1 e 2;  
  - para garantir que qualquer alteração de layout venha acompanhada de atualização deste capítulo.

- **Por operadores e revisores humanos:**  
  - para localizar rapidamente scripts, scorecards, evidências e docs da S15;  
  - para entender que gate olhar quando um risco específico estiver em jogo;  
  - para preparar a S16 (Threat Model + hardening) com base em um mapa claro de onde atacar/testar.

Com esta versão revisada do Capítulo 3, a S15 passa a ter um **contrato de layout explícito**: arquivos, diretórios e scripts deixam de ser implícitos e passam a ser parte formal da especificação da sprint.

