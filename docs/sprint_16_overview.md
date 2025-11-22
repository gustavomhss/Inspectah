# Sprint 16 — Overview

A Sprint 16 endurece o pacote entregue na S15 (Sistema de Blocos + Debunker v1 + Comitês V1/V2/V3 + Âncoras + Anti-canetada) com Threat Model formal, cenários de ataque e observabilidade de segurança. O foco é validar, sob pressão, se a pilha S13–S15 reage de forma previsível e auditável.

## Escopo e relações
- Threat Model S16 em `docs/sprint_16_threat_model.md`, guiando ataques e mitigação.
- Hardening focal em `inspectah/debunker/`, `inspectah/committees/`, `inspectah/anchors/` e `inspectah/commands/`.
- Gates T0–T8 em `bin/` e scripts de suporte em `scripts/s16_*.py`, seguindo os Capítulos 1–4 em `/Sprint 16/Capitulo *.md`.
- Scorecards em `out/scorecards/S16_T*.json` e evidências em `out/evidence/S16_T*/`.

## Objetivos práticos
- Demonstrar, com artefatos reproduzíveis, que ameaças plausíveis do Threat Model são detectadas ou mitigadas.
- Exercitar Debunker e Comitês sob entradas adversariais, validando trilha de decisão.
- Stress controlado de anchoring e anti-canetada, incluindo falhas de chain e tentativas de override.
- Observabilidade mínima para investigações rápidas de incidentes simulados.

## Como rodar
- Execução completa: `PYTHONPATH=. bin/s16_all_gates.sh`
- Gates isolados: `PYTHONPATH=. bin/s16_tX_*.sh` conforme necessidade (T0–T8).
- Capítulos de referência: `Sprint 16/Capitulo 1.md` (visão), `Capitulo 2.md` (gates), `Capitulo 3.md` (filemap/arquitetura), `Capitulo 4.md` (runbook).

## Integração com sprints anteriores
- S16 não altera contratos centrais da Truth-DB; reforça invariantes e observabilidade sobre a camada já funcional da S15.
- Reusa padrões de scorecards e evidências da S15, ampliando para cenários de ataque e consultas de segurança.
- Riscos e restrições residuais ficam registrados no ORR em `docs/sprint_16_orr_summary.md`.
