# S2-G3 — Evidence Vault v0 + LGPD mínimo

**Responsável:** Codex (Sprint 2)  
**Última atualização:** 2025-11-14T04:05:00Z

## Storage & Config
- [x] Configuração padrão (`configs/evidence_vault.yml`) fixa `region=sa-east-1`, `backend=local_stub`, `bucket=inspectah-evidence-dev`, `kms_key_alias=alias/inspectah-evidence-dev`.
- [x] Loader (`inspectah/config.py::load_evidence_vault_settings`) aplica overrides via `INSPECTAH_VAULT_*`, valida região obrigatória e resolve `local_root` sob `BASE_DIR`.
- [x] Client (`inspectah/evidence_vault/client.py::LocalEvidenceStoreClient`) força SSE-KMS (verifica `kms_key_alias`) e rejeita paths absolutos/traversais.

## Metadados & LGPD
- [x] Schema `evidence_records` criado e versionado em `db/migrations/001_add_evidence_records.sql` + `inspectah/models.py`, contendo fonte, tipo, hash, tamanho, tags LGPD e storage_key.
- [x] Writer (`inspectah/evidence_vault/writer.py::store_evidence`) aplica enum de tags LGPD, calcula SHA256 e persiste metadados completos.

## Segurança & Privacidade
- [x] Logs do client não incluem payload bruto (ver `tests/unit/test_evidence_vault_client.py::test_local_client_stores_and_recovers_bytes_without_leaking_payload`).
- [x] Writer/reader usam apenas o backend autorizado (`LocalEvidenceStoreClient`) e não criam dumps transitórios fora do root isolado — coberto por `tests/unit/test_evidence_vault_writer.py::test_store_evidence_persists_metadata_and_hash`.

## Testes Automatizados
- [x] `PYTHONPATH=$PWD ./.venv/bin/pytest tests/unit/test_evidence_vault_client.py` cobre validação de config, path safety e env overrides.
- [x] `PYTHONPATH=$PWD ./.venv/bin/pytest tests/unit/test_evidence_vault_writer.py` garante hashing, enum LGPD e tratamento de erros.
- [x] `PYTHONPATH=$PWD ./.venv/bin/pytest tests/integration/test_evidence_vault.py` garante fluxo completo write→read + persistência de metadados.
- [x] Suite consolidada `PYTHONPATH=$PWD ./.venv/bin/pytest tests/unit/test_evidence_vault_client.py tests/unit/test_evidence_vault_writer.py tests/unit/test_evidence_vault_cli.py tests/integration/test_evidence_vault.py` roda como parte do gate.

## Smoke & Operação
- [x] `scripts/evidence_vault_smoke.sh` executa write→read (via CLI `python -m inspectah.evidence_vault.cli`) e imprime apenas IDs/hashes/tags/tamanhos.
- [x] Evidências de execução registradas no próprio output do script e objetos armazenados no backend local_stub (`data/vault_objects/...`).

## CLI
- [x] `inspectah/evidence_vault/cli.py` fornece comandos `write`/`read` que reutilizam a API oficial e nunca expõem payload bruto (somente metadados + flags).

## Veredito S2-G3
- [x] Checklist completo (itens acima validados com comandos indicados).
- [x] `evidence_s2/s2_summary_gate_matrix.json` atualizado com S2-G3 = PASS com referências a testes e smoke.
