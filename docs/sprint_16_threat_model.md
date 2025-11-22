# Sprint 16 — Threat Model

## Visão geral
Este Threat Model cobre a pilha S13–S15 (Truth-DB, Debunker v1, Comitês V1/V2/V3, Âncoras, Anti-canetada) sob a ótica de hardening da Sprint 16. A meta é tornar ataques plausíveis detectáveis e manter trilha auditável para decisão de GO/GO_WITH_RESTRICTIONS/NO_GO. Referências canônicas: `/Sprint 16/Capitulo 1.md` (visão), `/Sprint 16/Capitulo 2.md` (gates), `/Sprint 16/Capitulo 3.md` (filemap) e `/Sprint 16/Capitulo 4.md` (runbook).

## Ativos protegidos
- Integridade de estados e histórico na Truth-DB (`inspectah.truthdb.*`).
- Relatórios do Debunker v1 (`inspectah/debunker/engine.py`, `report_models.py`).
- Decisões dos Comitês V1/V2/V3 (`inspectah/committees/*`).
- Registro de âncoras e batches (`inspectah/anchors/*`, `inspectah/blocks/__init__.py`).
- Trilhas de anti-canetada e overrides (`inspectah/commands/__init__.py`).
- Scorecards e evidências (`out/scorecards/`, `out/evidence/`).
- Logs/consultas de observabilidade de segurança (scripts `s16_security_observability_checks.py`).

## Atores
- Operadores legítimos (devs e analistas) executando gates T0–T8.
- Usuários internos desatentos (erros de operação).
- Atacante externo tentando envenenar claims/disputas ou causar colapso.
- Insider malicioso buscando bypass do anti-canetada.
- Provedor de chain/âncora falhando ou instável.

## Ameaças principais
- **Envenenamento de claims**: entradas maliciosas ou ambíguas tentando forçar `risk=low` e aprovação automática.
- **Captura/pressão de comitês**: submissões com pouca evidência aprovadas sem dissenso claro.
- **Bypass de anti-canetada**: override direto de estado sem disputa formal.
- **Falha ou reorg de chain**: âncoras atrasadas, batches incompletos ou inconsistentes.
- **Negação de serviço em disputas**: flood de casos e claims de alto risco para derrubar Debunker/comitês.
- **Opacidade de incidentes**: logs/métricas insuficientes para reconstruir ataques.

## Mitigações implementadas ou planejadas
- Debunker marca flags de risco e contradição no `meta.risk_flags`, elevando recomendações quando impacto/contradição são altos.
- Comitês V1/V2/V3 reforçados para rejeitar submissões sem evidência mínima ou com baixa concordância; registro de votos/vetos em metadados.
- Anti-canetada exige `claim_id`/`dispute_id`, bloqueia overrides explícitos e registra trilha estruturada via `audit_trail()`.
- Batcher/chain com modos de falha determinísticos, mantendo histórico e manifestos mesmo quando a chain cai.
- Scripts de ataque/stress (`scripts/s16_*.py`) reproduzindo vetores controlados com evidências em `out/evidence/S16_T*/`.
- Consultas de observabilidade de segurança que apontam lacunas (marcação explícita de “not_available” em checagens externas).

## Riscos residuais
- Cliente de chain continua simulado; reorgs reais podem ter nuances não cobertas.
- Heurísticas do Debunker são determinísticas e simplificadas, podendo subestimar ataques criativos de conteúdo.
- Stress tests locais não refletem limites de produção; gargalos reais podem aparecer em ambientes maiores.
- Observabilidade depende de artefatos locais; integrações externas podem falhar silenciosamente.

## Mapeamento ameaça → cenários/gates
- Envenenamento de claims → cenários `malicious_claim_high_risk`, `contradictory_evidence_detection` em `scripts/s16_attack_scenarios.py`; gates T2/T3.
- Captura/pressão de comitês → cenário `committee_capture_low_evidence`; gates T3/T5.
- Bypass de anti-canetada → cenário `override_without_dispute`; gate T4.
- Falha/reorg de chain → cenário `anchor_chain_failure`; gate T4.
- Negação de serviço em disputas → cenário `dispute_flood`; gates T2/T5.
- Opacidade de incidentes → consultas em `scripts/s16_security_observability_checks.py`; gate T6.

## Referências cruzadas
- Scripts: `scripts/s16_threat_model_checks.py`, `scripts/s16_attack_scenarios.py`, `scripts/s16_debunker_and_committees_under_attack.py`, `scripts/s16_anchors_and_anti_canetada_tests.py`, `scripts/s16_stress_and_degradation.py`, `scripts/s16_security_observability_checks.py`, `scripts/s16_ci_and_repro_checks.py`.
- Gates: `bin/s16_t0_sanity.sh` … `bin/s16_t8_go_no_go.sh`, `bin/s16_all_gates.sh`.
- Evidências: `out/evidence/S16_T*/MANIFEST.json` com descrições de cada execução.
