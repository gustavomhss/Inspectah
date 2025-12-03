# Sanity local pós-S25 – 2025-12-03

## Contexto

- Repositório: `/Users/gustavoschneiter/Documents/Inspectah`
- Ambiente: macOS, Python 3.14, venv em `.venv`
- Objetivo: validar saúde geral do backend/core e dos gates da Sprint 25 (Truth-DB v1.5 + promotion policies) em ambiente local, sem depender de CI.

## Comandos executados

### 1. Sanity do backend / core

- `python -m py_compile $(git ls-files '*.py')`
- `pytest`

Resultado: todos os 252 testes passaram com sucesso (252 passed, ~1056 warnings de deprecação de Pydantic/datetime, sem falhas).

### 2. Gates da Sprint 25

- `bash bin/s25_g0_*sh`  # smoke + contratos S23/S24/S25
- `bash bin/s25_g1_*sh`  # Truth-DB v1.5: migrations + testes
- `bash bin/s25_g2_*sh`  # promotion policies

Todos os gates G0, G1 e G2 da S25 retornaram GO, com scorecards gerados em `out/scorecards/`:

- `out/scorecards/S25_G0_scope_and_baseline.json`
- `out/scorecards/S25_G1_truthstate_machine.json`
- `out/scorecards/S25_G2_promotion_policy.json`

### 3. Bundle de evidências da S25

- `bash bin/s25_bundle.sh`

Artefatos gerados:

- Diretório de trabalho da S25: `out/S25_bundle/`
- Bundle zipado de evidências: `out/bundles/inspectah_s25_evidence_bundle.zip`

## Resultados e conclusão

- Backend/core saudável (compilação Python e suíte completa de testes passando).
- Truth-DB v1.5 validado via G1 da S25, com migrations aplicadas em `out/databases/s25_truth.sqlite`.
- Policies de promoção validadas via G2 da S25.
- Bundle de evidências consolidado em `out/bundles/inspectah_s25_evidence_bundle.zip`.

Este doc funciona como registro de referência para o estado “pós-S25” local. Qualquer auditoria futura pode reproduzir o cenário rodando os mesmos comandos descritos acima.

## Como repetir

Em um shell com o venv ativo:

```bash
cd /Users/gustavoschneiter/Documents/Inspectah
source .venv/bin/activate

python -m py_compile $(git ls-files '*.py')
pytest

bash bin/s25_g0_*sh
bash bin/s25_g1_*sh
bash bin/s25_g2_*sh
bash bin/s25_bundle.sh
```
