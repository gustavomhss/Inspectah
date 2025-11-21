# Sprint 15 — Overview

A Sprint 15 adiciona inteligência e blindagem ao Sistema de Blocos: Debunker v1, comitês V1/V2/V3, âncoras mínimas em blockchain e regras anti-canetada. O objetivo é tornar o fluxo de disputas cético, redundante e rastreável.

## Pilares entregues
- Debunker v1 em `inspectah/debunker/` com regras por domínio e fixtures multi-domínio.
- Comitês V1/V2/V3 em `inspectah/committees/` com fluxo integrado e Promotores do Diabo.
- Âncoras e batching em `inspectah/anchors/` com registry interno e cliente de chain testnet.
- Anti-canetada no write path em `inspectah/commands/`, bloqueando overrides sem disputa.
- Gates T0–T8 e orquestrador em `bin/` com evidências em `out/evidence/`.

## Como rodar
- `PYTHONPATH=. bin/s15_all_gates.sh`
- Scorecards em `out/scorecards/S15_T*.json` e evidências em `out/evidence/S15_T*/`.

## Integração com S13–S14
As novas camadas são aditivas: nenhum contrato da Truth-DB foi quebrado. O validador V1 usa a máquina de estados existente e os comandos anti-canetada chamam `TruthDB.update_estado` somente quando há claim/disputa documentados.
