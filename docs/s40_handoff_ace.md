# Handoff ACE Exec — Sprint 40 (v1.4)
## Truth-DB Estável (Fase 2: Truth-DB Core)
### Plano refinado em 4 rodadas (63 tasks)

---

## 1. Contexto Rápido

**Sprint:** S40
**Programa:** P2 (Interpretação → Truth-DB)
**Épico:** Truth-DB Core (Fase 2)
**Predecessora:** S39 (GO/NO-GO Fase 1)
**Sucessora:** S41 (Governança v1)

**Missão em uma frase:**
Tornar o Truth-DB estável em piloto: DecisionBlocks válidos com provenance, E40.5 obrigatório, export P2→P3 sem cola manual, e Truth Twin expondo tudo para auditoria.

---

## 2. Arquivos Essenciais

| Arquivo | O que contém |
|---------|--------------|
| `docs/s40_cap_4_4_tasks_e_waves.md` | Documento raiz de tasks e waves (fonte de verdade) |
| `docs/s40_tasks_execucao.yml` | YAML executável com ace_context por wave |
| `out/logs/s40_planner_review.md` | Log de revisão e matriz de cobertura |
| `out/scorecards/s40_planner.yml` | Scorecard do plano |
| `docs/Agents/Planejamento/Programa 2/Sprint 40/S40_spec.md` | Spec oficial do Spec Master |
| `docs/Agents/Planejamento/Programa 2/Sprint 40/Capitulo 2/Bloco 2.md` | Gates G20-G24 detalhados |

---

## 3. Waves e Ordem de Execução

```
W0 (Groundwork) ────┬──→ W1 (P3 Core) ─────┐
                    ├──→ W2 (P2 Export) ───┼──→ W4 (P4 Exposure) ──→ W5 (Quality & ORR)
                    └──→ W3 (P1 Hardening) ┘
```

**Ordem recomendada:**
1. **W0** — Schemas, migrations, validadores (fundação)
2. **W1** — DecisionBlock + E40.5 + Experiências (P3 Core)
3. **W2** — ClaimGraph export + NO-GO signals (P2 Integration)
4. **W3** — P1 hardening + SLA (pode rodar paralelo a W1/W2)
5. **W4** — Truth Twin + Inspector + provenance (depende de W1+W2)
6. **W5** — Testes, observabilidade, bundle (fechamento)

---

## 4. Gates e Scripts

| Gate | Script | O que valida |
|------|--------|--------------|
| G20 | `bin/s40_g20_contracts.sh` | Schemas válidos, validadores fail-closed |
| G21 | `bin/s40_g21_p1_hardening.sh` | Fontes healthy, SLA P1 ≤1min |
| G22 | `bin/s40_g22_claimgraph.sh` | Export/ingest sem cola, NO-GO bloqueia |
| G23 | `bin/s40_g23_truthdb.sh` | DecisionBlocks válidos, E40.5 enforcement, Experiências |
| G24 | `bin/s40_g24_p4_exposure.sh` | Endpoints com provenance, latência ≤100ms |

**Script master:** `bin/s40_all_gates.sh` (roda todos em sequência)

---

## 5. Evidências Esperadas

```
out/
├── evidence/
│   ├── S40_G20_schema_validation.json
│   ├── S40_G20_export_schema.json
│   ├── S40_G20_twin_schema.json
│   ├── S40_G20_migration.log
│   ├── S40_canonical_A.json (caso PASS)
│   ├── S40_canonical_B.json (caso NO-GO)
│   ├── S40_canonical_C.json (caso contestação)
│   ├── S40_e40_5_tests.log
│   ├── S40_nogo_tests.log
│   ├── S40_export_contract.json
│   ├── S40_api_tests.log
│   ├── S40_latency_benchmark.json
│   ├── S40_playwright.html
│   ├── S40_coverage.html
│   ├── S40_dashboard_screenshot.png
│   ├── S40_alerts_config.yaml
│   ├── S40_seed_experiences.log
│   └── S40_all_gates.log
├── scorecards/
│   ├── S40_G20_contracts.json
│   ├── S40_G21_p1.json
│   ├── S40_G21_p1_latency.json
│   ├── S40_G22_claimgraph.json
│   ├── S40_G23_truthdb.json
│   ├── S40_G24_p4.json
│   ├── S40_G24_p4_latency.json
│   └── s40_planner.yml
└── bundles/
    └── S40_bundle.zip
```

---

## 6. Alertas Críticos

1. **DecisionBlock inválido = bloqueio.** Sem `references.guias[]`, `references.pilares[]`, ou `references.e40_5` → ValidationError → transição não ocorre.

2. **E40.5 FAIL = bloqueio.** Nenhuma transição crítica passa sem E40.5 PASS. Sem bypass.

3. **NO-GO signal = bloqueio real.** Sinais INCONSISTENCY, SUSPICION, ABUSE devem impedir transição, não ser só label.

4. **Provenance obrigatória em P4.** Endpoint sem provenance deve retornar `X-Provenance-Valid: false` ou marcar resposta como `invalid`.

5. **Cobertura ≥97%.** CLAUDE.md obriga. Rode `PYTHONPATH=. .venv/bin/python -m pytest --cov=app` antes de finalizar.

---

## 7. Gaps Conhecidos (para o ACE resolver)

| Gap | O que fazer |
|-----|-------------|
| GAP-01: Embedding para Experiências | Escolher implementação (sentence-transformers ou similar). Documentar em `app/truth/experiences.py`. |
| GAP-02: Formato de references.guias[] | Seguir Cap.3/Bloco 2.md. Implementar conforme schema. |
| GAP-03: Threshold de NO-GO signals | Definir critérios objetivos. Documentar em `app/claims/signals.py`. |

---

## 8. Como Começar

```bash
# 1. Ler o YAML de tasks
cat docs/s40_tasks_execucao.yml

# 2. Verificar estado atual do repo
git status

# 3. Começar pela Wave 0
# Primeira task: S40-INF-001 (schema decision_block_v1.json)

# 4. Para cada task:
#    - Ler descrição e DONE
#    - Implementar
#    - Rodar testes
#    - Gerar evidência
#    - Marcar como completa

# 5. Ao final de cada wave, rodar script de gate
bin/s40_g20_contracts.sh  # (exemplo para W0)
```

---

## 9. Reportar Gaps

Se encontrar algo que impede execução de uma task:

1. **Não inventar solução ad-hoc.**
2. **Registrar gap** com descrição clara.
3. **Comunicar imediatamente** para ajuste de plano.

---

## 10. Sucesso Real

A S40 está **DONE** quando:

- [ ] G20-G24 = PASS com evidências
- [ ] SLAs no recorte piloto atingidos (P1≤1min, P4≤100ms)
- [ ] Casos canônicos A/B/C executados e rastreáveis
- [ ] GO/NO-GO 7/7 comprovado
- [ ] Cobertura de testes ≥97%
- [ ] Bundle `S40_bundle.zip` gerado
- [ ] Handoff S40→S41 preenchido

---

## 11. Notas de Implementação

### Embedding para Experiências
```python
# Usar sentence-transformers/all-MiniLM-L6-v2 (384 dims)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(claim_text)
```

### NO-GO Signal Thresholds
```python
NOGO_THRESHOLDS = {
    "INCONSISTENCY": {"contradictions": 2},
    "SUSPICION": {"anomaly_score": 0.8},
    "ABUSE": {"spam_score": 0.9, "report_count": 3}
}
```

### TruthState Mapping
```
uncertain   → TruthState.UNKNOWN
claimed     → TruthState.CLAIMED
review      → TruthState.UNDER_REVIEW
provisional → TruthState.PROVISIONAL
true        → TruthState.ESTABLISHED_FACT
disputed    → TruthState.UNDER_DISPUTE
retracted   → TruthState.RETRACTED
```

---

## 12. GO/NO-GO 7/7 — Checklist Rápido

| # | Critério | Como Evidenciar |
|---|----------|-----------------|
| 1 | Checklist 100% | `bin/s40_all_gates.sh` exit 0 |
| 2 | Guias em DecisionBlocks | Validador rejeita sem guias[] |
| 3 | Testes passando | Coverage ≥97% |
| 4 | SLAs piloto | Scorecards P1/P4 dentro |
| 5 | Docs atualizados | S40_ORR_Checklist + S40_Handoff preenchidos |
| 6 | E40.5 operando | Testes E2E passam |
| 7 | Pré-condições éticas | references.pilares[] obrigatório |

---

## 13. Formato de Evidências

Todas as evidências DEVEM conter metadata com carimbo:
```json
{
  "metadata": {
    "sprint": "S40",
    "gate": "G2X",
    "timestamp": "ISO8601",
    "commit": "SHA",
    "policy_version": "vX.Y.Z",
    "domain": "pilot_*"
  }
}
```

---

*Handoff gerado pelo Sprint Planner Técnico — S40 v1.4 (4 rodadas de refinamento)*
