# Inspectah — Sprint 14 Truth Kernel v0

## Visão e propósito
A Sprint 14 endurece o truth kernel v0 do Inspectah em cima do backbone das S12/S13. O objetivo é garantir que case_service, timeline_service e truthdb_adapter continuem representando a verdade atual, usando snapshots S12/S13 como fonte canônica e explicitando invariantes mínimas antes de evoluir para contestação v0.

## Componentes do kernel v0
- Serviços oficiais: `scripts/s12_case_service.py`, `scripts/s12_timeline_service.py`, `scripts/s12_truthdb_adapter.py`.
- Fontes de estado: resultados dos pipelines e invariantes das S12/S13 (gates G2/G4).
- Debunker v0 permanece obrigatório no caminho de atualização de casos/timelines.
- Explorer/feedback consomem somente snapshots oficiais (sem atalhos em banco local).

## Snapshots de referência da S12/S13
- S12: `out/evidence/S12_G2/` (ingestão) e `out/evidence/S12_G4/` (invariantes e snapshots de casos/timelines).
- S13: `out/evidence/S13_G2/` (timelines multi-domínio) e `out/evidence/S13_G4/` (artefatos do Explorer multi-domínio).
- Config de pilotos: `config/s13_pilotos.yml` lista case_keys oficiais por domínio.
- Cross-check: ORRs `docs/sprint_12_orr_summary.md` e (quando disponível) ORR S13 garantem baseline “GO” antes de rodar a S14.

## Domínios cobertos e representação
Os seis domínios consolidados permanecem: `obra_publica`, `evento_climatico`, `projeto_lei`, `carreira_politica`, `influencer`, `atleta`. Cada domínio mantém case_keys e convenções herdadas de `config/s13_pilotos.yml` e dos snapshots em `out/evidence/S13_G2/`.

## Invariantes e checagens esperadas (G1)
- **Domínio válido**: todo caso/timeline deve usar domínio listado em `config/s14_truth_kernel.yml`.
- **Case ↔ timeline**: cada timeline deve apontar para um `id_caso` existente e coerente com o domínio.
- **Cobertura de domínios**: todos os 6 domínios precisam ter pelo menos um caso ou timeline nos snapshots oficiais.
- **Integridade mínima**: índices de integridade ≥ 0,95 para casos/timelines e 1,0 para cobertura de domínios (SLO do gate).
- Evidências ficam em `out/evidence/S14_G1/kernel_integrity_report.json` e scorecard em `out/scorecards/S14_G1_truth_kernel.json`.

## Escopo e limites
- Não introduz Sistema de Blocos completo, reputação ou blockchain; esses itens permanecem listados em `docs/sprint_14_backlog_fase2.md`.
- Correções ou migrações que mudem snapshots devem ser rastreadas e idempotentes (Wave 4).
