# Sprint 21 — Wrap de Execução (Console de Fontes)

Este wrap consolida objetivos, entregas, status de gates e riscos da Sprint 21. Deve permanecer sincronizado com os scorecards em `out/scorecards/S21_G0…S21_G8.json`.

## 1. Objetivo da sprint
Construir o Console de Fontes Fase 1: ontologia clara, modelo de dados e ciclo de vida implementáveis, fluxos admin operacionais, ganchos para Debunker/redundância e contratos firmes com S22–S25.

## 2. Principais entregas
- Documentação completa: ontologia, modelo de dados, ciclo de vida, fluxos admin, ganchos Debunker, cenários de uso, contratos S22–S25.
- Módulo de domínio `app/sources/` com modelos, serviços, validação, health-check e rotas de admin.
- UI mínima do console de fontes (lista, detalhe, criação/edição, timeline de estados, health-check).
- Migrations de schema e seeds de fontes exemplo.
- Testes de domínio/serviço/API/health-check em `tests/sources/`.
- Scripts de gates S21_G0…S21_G8 com scorecards e evidências organizadas.

## 3. Status dos gates (inicial)
- S21_G0 — Contexto: em andamento (docs base copiados).
- S21_G1 — Ontologia: em elaboração.
- S21_G2 — Modelo de dados e ciclo de vida: em elaboração.
- S21_G3 — Fluxos admin: em elaboração.
- S21_G4 — Ganchos Debunker: em elaboração.
- S21_G5 — Contratos S22–S25: em elaboração.
- S21_G6 — Cenários de uso: em elaboração.
- S21_G7 — Scorecard: aguardando consolidação de métricas.
- S21_G8 — GO/NO-GO: será definido após os gates anteriores.

## 4. Evidências planejadas
- Pastas `out/evidence/S21_GX_*` com MANIFEST.json, snapshots de docs, logs de testes/gates, capturas de UI.
- Scorecards JSON em `out/scorecards/` espelhando o status acima.

## 5. Riscos e mitigação inicial
- **Risco de escopo**: volume de arquivos e código alto — mitigação com fases claras (Capítulo 4) e gates automatizados.
- **Risco de divergência com S22–S25**: mitigação com contratos explícitos e revisões cruzadas.
- **Risco de atraso em UI**: manter UI mínima funcional e priorizar APIs/gates.

## 6. Próximos passos imediatos
- Completar docs específicos (ontologia → contratos).
- Implementar modelos/migrations e serviços.
- Construir UI e testes, executar gates e atualizar scorecards.

## 7. Decisão final
Será registrada em `out/scorecards/S21_G8_go_no_go.json` após execução dos gates. O wrap deve ser atualizado para refletir o resultado (GO ou NO_GO) com justificativas e riscos residuais.
