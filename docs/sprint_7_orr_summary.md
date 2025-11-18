# Inspectah — Sprint 7 ORR Summary

## Objetivo da Sprint 7
Sprint 7 transformou o Inspectah em um produto demonstrável via navegador, entregando a **Inspectah UI Alpha** sobre o runtime estável da Sprint 6. O foco foi permitir que um admin ajuste fontes e que um usuário finalize consultas completas (com decisão consolidada e rastreabilidade de evidências) sem tocar no terminal. Toda a validação foi encapsulada em gates S7-G0…S7-G8 com scorecards e evidências versionados em `out/`.

## Gates S7-G0…S7-G8
| Gate | Descrição | Status |
| --- | --- | --- |
| S7-G0 | Baseline Sprint 6 + docs S7 presentes (`bin/s7_g0_baseline.sh`). | GO (PASS) |
| S7-G1 | UI boot & health (`/health` responde “ok”, runtime S6 disponível). | GO (PASS) |
| S7-G2 | CRUD de fontes pela UI, refletindo em `config/sources/*.yaml`. | GO (PASS) |
| S7-G3 | Modelo canônico & preview exibidos pela UI com 100% de aderência ao YAML. | GO (PASS) |
| S7-G4 | Consulta + decisão consolidada + explicação textual consistente. | GO (PASS) |
| S7-G5 | Rastreamento de evidência em ≤2 cliques com pacotes existentes. | GO (PASS) |
| S7-G6 | Fluxos Admin/Usuário UI-only cronometrados, sem terminal. | GO (PASS) |
| S7-G7 | Consolidação das métricas M1…M6 + roteiro oficial de demo. | GO (PASS) |
| S7-G8 | GO/NO-GO final da sprint, confirmando todos os gates/métricas. | GO (PASS) |

Os gates são encadeados: G0 valida a fundação da Sprint 6, G1–G5 constroem a UI passo a passo, G6 garante as jornadas completas, G7 registra as métricas e G8 fecha o GO. Cada scorecard correspondente está em `out/scorecards/S7_G*.json` com evidências em `out/evidence/S7_G*/`.

## Como rodar a Sprint 7 localmente
Pré-requisitos gerais:
```bash
cd /Users/<voce>/Inspectah
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$PWD
```

Runbook dos gates (rodar em sequência, cada comando gera scorecard/evidência):
```bash
PYTHONPATH=. bin/s7_g0_baseline.sh
PYTHONPATH=. bin/s7_g1_ui_boot_health.sh
PYTHONPATH=. bin/s7_g2_ui_sources_admin.sh
PYTHONPATH=. bin/s7_g3_ui_fields_preview.sh
PYTHONPATH=. bin/s7_g4_ui_query_consolidation.sh
PYTHONPATH=. bin/s7_g5_ui_evidence_trace.sh
PYTHONPATH=. bin/s7_g6_ui_only_flows.sh
PYTHONPATH=. bin/s7_g7_metrics_and_demo.sh
PYTHONPATH=. bin/s7_g8_sprint_go_no_go.sh
```

Suíte de testes dedicada:
```bash
PYTHONPATH=. pytest tests/sprint_7 -q
```
*Observação:* em ambientes sandbox sem permissão de abrir sockets, scripts que sobem a UI (`bin/s7_ui_start.sh`) ou gates dependentes de HTTP podem falhar; execute em uma máquina local normal.

## Métricas & Demos (M1…M6)
Valores oficiais extraídos de `out/scorecards/S7_G7_metrics_and_demo.json`:
- **M1 — Tempo end-to-end da demo:** 1,40 s para ligar a UI, ajustar fonte e completar a jornada Admin+Usuário.
- **M2 — Fluxo do usuário sem terminal:** 0,88 s para executar consulta, obter decisão consolidada e chegar à evidência.
- **M3 — Admin CRUD success rate:** 1,0 (100% dos fluxos de criação/edição/desativação passaram via UI).
- **M4 — Confiança no modelo/consulta:** schema ratio 1,0, query consistency 1,0 e preview coverage 1,0 (UI igual ao YAML e aos dados da Sprint 6).
- **M5 — Explicação da decisão consolidada:** presente em todas as consultas validadas (texto da mediana exibido na UI).
- **M6 — Evidência em ≤2 cliques:** `m6_max_clicks_to_evidence = 2` com `m6_evidence_found_ratio = 1,0`.

A demo oficial segue: ligar UI (`bin/s7_ui_start.sh`), checar `/health`, ajustar fontes, revisar modelo/preview, executar consulta, observar valor consolidado + explicação, abrir evidência e encerrar a UI.

## Evidências & Artefatos
- **Scorecards:** `out/scorecards/S7_G*.json` — cada arquivo registra inputs, métricas e status do gate correspondente.
- **Evidências:** `out/evidence/S7_G*/` — contêm summaries, logs, amostras de payloads e links para manifests.
- **UI/Runtime:** código da casca web em `inspectah/ui/` e ponte com a Sprint 6 em `inspectah/ui/runtime_bridge.py`.

Esses diretórios tornam auditável o GO da sprint e podem ser anexados em apresentações ou auditorias.

## Limitações conhecidas & Próximos passos
1. **Execução em ambientes restritos:** scripts de UI/Gates que dependem de sockets podem falhar em sandboxes; recomenda-se operar sempre em máquina local ou CI com permissões normais.
2. **UI Alpha:** a experiência é funcional, porém minimalista; próximas sprints devem focar em UX, filtros avançados, internacionalização e testes end-to-end no navegador.
3. **Observabilidade da UI:** atualmente restrita aos scorecards; incluir dashboards/alertas específicos da camada web é o passo natural para a Sprint 8.
4. **Escalar fontes:** Sprint 7 cobre apenas o domínio piloto; próximas sprints devem adicionar novas fontes/schemas usando os mesmos gates para sustentar o crescimento.
