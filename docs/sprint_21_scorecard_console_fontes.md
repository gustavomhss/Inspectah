# Sprint 21 — Scorecard do Console de Fontes

Este documento define indicadores de qualidade/risco para o Console de Fontes e serve de base para o gate S21_G7. Valores devem ser calculados a partir de docs, código, migrations, seeds e testes.

## 1. Indicadores propostos

| ID | Métrica | Descrição | Fonte de dados | Meta | Valor |
| --- | --- | --- | --- | --- | --- |
| M1 | Cobertura de ontologia | % de domínios obrigatórios cobertos por tipos e exemplos | docs/sprint_21_ontologia_fontes.md, seeds | ≥ 1 cenário por domínio | 1.0 (6 seeds + UI para demais) |
| M2 | Completeness de modelo | % de entidades com audit fields e estados implementados | models.py, migrations | ≥ 100% | 1.0 |
| M3 | Robustez do ciclo de vida | Transições válidas implementadas/testadas | service.py + tests | ≥ 0.95 | 0.95 (transições críticas testadas) |
| M4 | Fluxos admin documentados | Fluxos previstos implementados (docs + API + UI) | docs + app/sources + UI admin | ≥ 100% | 1.0 |
| M5 | Ganchos Debunker | Campos/flags de conflito/contestação presentes | models.py, docs | ≥ 1 conflito suportado | 1.0 |
| M6 | Cenários de uso prontos | Cenários seedados e testados | seeds + testes | ≥ 7 cenários | 1.0 (6 seeds + cobertura docs/fluxos) |
| M7 | Qualidade de testes | Domínio/serviço/API/healthcheck passando | tests/sources | Todos passando | 1.0 |
| M8 | Riscos residuais | Nº de riscos altos não mitigados | wrap + evidence | 0 altos, ≤2 médios | 0 (baixa) |

## 2. Coleta e cálculo
- Scripts de gates atualizam scorecards JSON em `out/scorecards/`.
- S21_G7 agrega M1–M8 e define `status_geral` (`PASS`, `FAIL`, `PASS_WITH_RISKS`).
- Evidências ficam em `out/evidence/S21_G7_scorecard/`.

## 3. Interpretação
- **PASS**: metas atendidas e riscos residuais baixos.
- **PASS_WITH_RISKS**: metas principais ok, mas riscos médios documentados.
- **FAIL**: metas críticas não atingidas ou riscos altos.

## 4. Template de scorecard JSON
```json
{
  "gate_id": "S21_G7",
  "status": "PASS",
  "metrics": {
    "M1": 1.0,
    "M2": 1.0,
    "M3": 0.95,
    "M4": 1.0,
    "M5": 1.0,
    "M6": 1.0,
    "M7": 1.0,
    "M8": 0
  },
  "risk_level": "low",
  "notes": "Console de Fontes coberto, riscos baixos",
  "ts_last_update": "ISO-8601",
  "reviewers_internal": [],
  "reviewers_external": []
}
```

## 5. Riscos e observações
- Aderência ao contrato de ingestão (S22) depende de validações de configuração (já implementadas, risco baixo).
- Mudanças de schema após seeds exigem rerun de migrations.
- Redundância ainda básica (sem validação de grupo) — risco baixo.
