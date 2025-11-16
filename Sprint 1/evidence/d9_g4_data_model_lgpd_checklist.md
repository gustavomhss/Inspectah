# D9-G4 — Data Model + LGPD/ToS

**Responsável:** Codex (Inspectah Sprint D9)
**Data:** 2025-11-13T22:50:39Z

## Data Model / DDL
- [x] Esquemas de Source, Item, ItemKV, FTS e Evidence Vault descritos (D9.4 §3–4)
- [x] Chaves primárias, FKs e índices principais definidos (DDL em cada subseção)
- [x] Estratégia de migração SQLite → Postgres delineada (§6)

## Retenção e Volume
- [x] Prazos de retenção de dados raw vs manifests/índices definidos (§5)
- [x] Limites de volume/particionamento documentados (§7)
- [x] Localização/região do Evidence Vault e controles de criptografia descritos (D9.4 §2 + §4)

## LGPD / ToS
- [x] Fontes permitidas, condicionais e proibidas mapeadas (D9.5 §§2–3)
- [x] Tratamento de dados pessoais e respeito a robots.txt explicitados (D9.5 §§4–6)

## Envelope de Risco
- [x] Exemplos de fontes borderline e critérios de decisão descritos (D9.5 §7)
- [x] Reforço de que Inspectah não depende de scraping agressivo presente (D9.5 §4 + §7)

## Observações
- Revisão conjunta de D9.4 e D9.5 garante aderência cruzada entre modelo físico e guardrails legais; ação D9-LGPD-001 aplicada.
