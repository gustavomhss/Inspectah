# Inspectah — Sprint 12 ORR Summary

## Objetivo da Sprint 12
A Sprint 12 colocou o backbone da Sprint 10 em operação contínua: ingestão enxuta de fontes piloto, Debunker v0 obrigatório em eventos sensíveis, organização por casos/temas com timeline auditável, Explorer v0 acessível via navegador e um fluxo mínimo de feedback interno. Tudo finalizado com observabilidade consolidada (G7) e decisão GO/NO-GO automatizada (G8), com scorecards e evidências versionados em `out/`.

## O que a Sprint 12 entrega hoje
1. **Ingestão contínua:** scheduler + registry disparam conectores piloto (Diário Oficial de Niterói, Portal da Transparência RJ, alertas INMET). Cada rodada gera `raw_events` idempotentes, logs controlados e snapshots exportáveis.
2. **Pipeline + Debunker v0:** `s12_ingest_pipeline.py` normaliza os eventos, resolve `case_id`, atualiza timeline e só envia eventos elegíveis para a Truth-DB depois de passar pelo Debunker v0, com decisão (`aceito`, `incerto`, `suspeito`) e racional armazenados.
3. **Casos/temas + timeline:** eventos viram casos (`obra_publica:contrato`, `evento_climatico:alerta`) com status geral simples e timeline append-only que respeita as invariantes I1–I3 em cima da Truth-DB/Guardião.
4. **Explorer v0:** backend `/explorer/*` e UI React permitem buscar casos, abrir a timeline, conferir fontes originais e disparar feedback sem tocar em terminal.
5. **Feedback interno:** cada “reportar problema” cai numa fila (`novo`, `em_analise`, `resolvido`) persistida em `out/runtime/s12_feedback_store.json`, administrada via `/admin/feedback`.
6. **Observabilidade e GO:** G7 agrega os cinco SLIs da sprint num snapshot único; G8 lê todos os scorecards, aplica as regras de decisão e grava `decision=GO` + wrap humano em `out/evidence/S12_G8/summary.md`.

## Gates S12_G0…S12_G8
| Gate | Descrição | Status |
| --- | --- | --- |
| S12_G0 | Repo/branch/docs corretos antes de rodar qualquer coisa. | PASS |
| S12_G1 | Scheduler + fontes piloto com frescor ≥ 0,95. | PASS |
| S12_G2 | Pipeline + normalização idempotente alimentando casos/timeline. | PASS |
| S12_G3 | Debunker v0 cobrindo 100% dos eventos elegíveis com racional gravado. | PASS |
| S12_G4 | Casos/temas/timelines obedecendo I1–I3. | PASS |
| S12_G5 | Explorer F1–F3 (buscar → abrir caso → feedback) automatizados. | PASS |
| S12_G6 | Feedback entregue à fila interna e status atualizável. | PASS |
| S12_G7 | Observabilidade/SLO consolidados a partir de G1–G6. | PASS |
| S12_G8 | Decisão GO/NO-GO com wrap humano honesto. | PASS |

## Como rodar a Sprint 12
- **Localmente:**
  ```bash
  cd /Users/gustavoschneiter/Documents/Inspectah
  bash bin/s12_gates_all.sh      # G0…G7
  bash bin/s12_g8_decision.sh    # GO/NO-GO + summary
  ```
  Scorecards: `out/scorecards/S12_G*.json`. Evidências: `out/evidence/S12_G*/`.
- **CI local completo:** `bash bin/ci_local.sh` — a suíte já chama `bin/s12_gates_all.sh` junto com lint/tests/bench/release.
- **Workflow Github Actions:** `.github/workflows/_s12-gates.yml` roda em pushes/PRs para `main` e `s12_ingestao_continua_comunidade_v0`, instala o projeto e executa `bin/s12_gates_all.sh`, publicando `out/scorecards` e `out/evidence` como artifacts.

## Riscos e débitos técnicos
1. **Cobertura limitada:** ingestão contínua contempla apenas as fontes piloto. Novos domínios precisam repetir o mesmo rigor de registry, scheduler e normalizers antes de entrar na linha.
2. **Debunker heurístico:** as decisões são determinísticas e explicadas, mas ainda baseadas em regras simples; reforçar com guardiões mais sofisticados continua no backlog da Fase 2.
3. **Explorer/feedback v0:** UI funcional porém básica, sem filtros avançados, autenticação diferenciada ou integração com comunidade externa — upgrades virão na fase de Comunidade completa.
4. **Snapshots locais:** exibição no Explorer e nos gates depende dos artefatos produzidos pelo pipeline. Operadores devem rodar `bin/s12_gates_all.sh` (ou pelo menos `bin/s12_g2_ingest_pipeline.sh`) antes de qualquer demo para manter `out/evidence/` fresco.

Com isso, a Sprint 12 está oficialmente GO: ingestão contínua respirando, Debunker obrigatório, timeline auditável, Explorer/feedback em operação e observabilidade + decisão mecanizadas.
