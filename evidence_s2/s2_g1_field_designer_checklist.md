# S2-G1 — Field Designer v0 & IEL Core

**Responsável:** Codex (Sprint 2)
**Data:** 2025-11-14T02:20:13Z

## Schema CRUD
- [x] FieldDefinition suporta tipos e transforms descritos em D9 (text, number, bool, timestamp, etc.).
- [x] `create_schema` cria versão inicial em `registry/fields/schemas/<schema>/vN.yaml` com metadata (status, owner, description).
- [x] `update_schema` incrementa versão mantendo histórico e metadados.
- [x] `list_schemas` / `load_schema` retornam metadata coerente e ordenada.

## Computed Fields / IEL
- [x] Computed fields exigem `expression` + `fallback` e são validados no publish.
- [x] IEL aceita apenas operadores/funções permitidas (min/max/abs/round/concat/length/coalesce/_iel_if/lag).
- [x] IEL bloqueia acesso a atributos, funções externas ou nomes não declarados.
- [x] Avaliação dos computed fields aplica fallback determinístico em caso de erro.

## Evidências
- [x] Testes unitários `tests/field_designer/test_schema_crud.py` e `tests/field_designer/test_iel.py` executam sem falhas (pytest).
- [x] Exemplos de schema/computed fields registrados nos testes (`tests/field_designer/test_schema_crud.py`).

## Observações
- Comando usado para validar IEL no ambiente do desenvolvedor: `PYTHONPATH=$PWD ./.venv/bin/pytest tests/field_designer/test_iel.py` (5 testes). Em sandbox offline, o comando deve ser executado manualmente após `pip install -e .[dev]`.
