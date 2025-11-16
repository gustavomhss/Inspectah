# S2-G6 — Docs operacionais + Retro Sprint 2

**Responsável:** Codex (Sprint 2)
**Última atualização:** 2025-11-14T05:05:00Z

## README.md
- [x] Seção "Ambiente de desenvolvimento v0" revisada e testada (`bin/dev_up.sh`, `curl /explore/items`, `bin/dev_down.sh`).
- [x] Seção "Ingest demo" usa `./scripts/ingest_source_demo.sh` (última execução retornou `{"source_id": "rss_news_minimal", "items_ingested": 2}`).
- [x] Seção "Explore API" contém comandos `curl` reais (testados após ingest demo).
- [x] Seção "Evidence Vault v0 (CLI)" validada com os comandos `python -m inspectah.evidence_vault.cli write/read` (ID `019a8397-dc4c-71e3-a273-bc90fae97b70`).
- [x] Seção "Fluxo E2E" documenta `./bin/run_inspectah_v0_e2e.sh` (saída registrada no checklist de S2-G5).
- [x] Seção "Métricas em tempo de execução" demonstrada via snippet `from inspectah.metrics import get_snapshot`.

## Sprint 2/Capítulo 4.md
- [x] Snapshot dos gates (S2-G0…S2-G6) preenchido com status + comentários reais.
- [x] Entregáveis S2.x listados com indicador entregue/parcial.
- [x] Lessons `S2-LESSON-001`…`003` documentadas no formato exigido.
- [x] Ações `S2-ACT-001`…`003` vinculadas às lessons e organizadas por Sprint alvo.
- [x] Backlog S3+ destacado e alinhado com as actions.
- [x] Registro explícito de que não houve patches (`S2-PATCH-XXX`).

## Matriz / Mini-ORR
- [x] `evidence_s2/s2_summary_gate_matrix.json` contém S2-G0…S2-G6 = PASS com evidências/comandos corretos.
- [x] Mini-ORR (tabela do Cap.4 §1.1 + README) reflete os mesmos caminhos/comandos da matriz.

## Status do Gate
- [x] Checklist completo.
- [x] `evidence_s2/s2_summary_gate_matrix.json` atualizado para S2-G6 = PASS.
