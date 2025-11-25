# Sprint 22 — G3 Máquina de Estados da Ingestão

## 1. Estados
- `PENDING`: run criado, ainda não iniciado.
- `RUNNING`: ingestão em execução.
- `SUCCESS`: ingestão concluída com todos os itens.
- `PARTIAL_SUCCESS`: ingestão concluiu parcialmente, com erros recuperáveis/itens faltantes.
- `FAIL`: ingestão falhou de forma não recuperada.

## 2. Eventos
- `START`: cria run (PENDING → RUNNING).
- `COMPLETE`: encerra run com sucesso (RUNNING → SUCCESS).
- `PARTIAL_COMPLETE`: encerra parcialmente (RUNNING → PARTIAL_SUCCESS).
- `ERROR`: falha controlada (RUNNING → FAIL).
- `TIMEOUT`: excedeu timeout (RUNNING → FAIL com `error_code=timeout`).
- `REPROCESS`: cria novo run derivado de anterior (qualquer final → novo run PENDING/RUNNING).

## 3. Tabela de transições
| Estado atual      | Evento            | Próximo estado     | Notas |
|-------------------|-------------------|--------------------|-------|
| PENDING           | START             | RUNNING            | exige `started_at` |
| RUNNING           | COMPLETE          | SUCCESS            | exige `finished_at`, `payload_ref` |
| RUNNING           | PARTIAL_COMPLETE  | PARTIAL_SUCCESS    | exige `finished_at`, `payload_ref`, `error_message` opcional |
| RUNNING           | ERROR             | FAIL               | exige `finished_at`, `error_code` |
| RUNNING           | TIMEOUT           | FAIL               | seta `error_code=timeout` |
| SUCCESS           | REPROCESS         | novo run PENDING   | origem opcional para auditoria |
| PARTIAL_SUCCESS   | REPROCESS         | novo run PENDING   | idem |
| FAIL              | REPROCESS         | novo run PENDING   | idem |

Transições não previstas devem gerar `IllegalTransitionError` com log.

## 4. Regras adicionais
- `RUNNING` não pode permanecer indefinidamente: serviços aplicam timeout → TIMEOUT → FAIL.
- Apenas uma instância RUNNING por `config_id` (ver INV-6).
- `finished_at` sempre maior que `started_at`.
- Transições duplicadas (ex.: RUNNING → COMPLETE duas vezes) são idempotentes e retornam estado final já registrado sem alterar metadados.

## 5. Métricas do gate G3
- `fsm_states_count`: 5
- `fsm_transitions_covered`: 7 transições válidas testadas + 2 ilegais.
- `illegal_transitions_caught`: ≥1 em testes.
- `fsm_tests_pass_rate`: 1.0 nos scripts do gate.
