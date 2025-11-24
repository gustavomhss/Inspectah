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

## 3. Status dos gates (final)
- S21_G0 — Contexto: **PASS**
- S21_G1 — Ontologia: **PASS**
- S21_G2 — Modelo de dados e ciclo de vida: **PASS**
- S21_G3 — Fluxos admin: **PASS**
- S21_G4 — Ganchos Debunker: **PASS**
- S21_G5 — Contratos S22–S25: **PASS**
- S21_G6 — Cenários de uso: **PASS**
- S21_G7 — Scorecard: **PASS**
- S21_G8 — GO/NO-GO: **GO**

## 4. Evidências
- Pastas `out/evidence/S21_GX_*` criadas com MANIFEST e logs/resumos.
- Scorecards JSON em `out/scorecards/` para G0…G8 (GO registrado).

## 5. Riscos e mitigação inicial
- **Risco de escopo**: volume de arquivos e código alto — mitigação com fases claras (Capítulo 4) e gates automatizados.
- **Risco de divergência com S22–S25**: mitigação com contratos explícitos e revisões cruzadas.
- **Risco de atraso em UI**: manter UI mínima funcional e priorizar APIs/gates.

## 6. Próximos passos recomendados
- Entregar a S22 (Ingestão 2.0) usando os contratos documentados e seeds `mock://`.
- Conectar agentes (S23) usando ontologia e parsing_config.
- Habilitar Debunker (S24) consumindo flags de conflito/contestação e estados.
- Ajustar políticas de governança (S25) com base em histórico e healthchecks.

## 7. Decisão final
- Decisão: **GO** (ver `out/scorecards/S21_G8_go_no_go.json`).
- Riscos residuais: baixos; dependência de ingestão respeitar contratos e evolução de parsing.
