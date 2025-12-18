# HANDOFF — Sprint 42 (ACE Exec) v3.0 MATURE

## Identificacao

- **Sprint:** S42
- **Programa:** P2 + P3 + P4 (+ P5/P6)
- **Epico:** Simulacoes MAC + Plano Adiabatico + Exposicao MI
- **Gates:** G30, G31, G32, G33, G34, G35
- **Versao do Plano:** 3.0 MATURE (18 rodadas de refinamento)
- **Tasks Totais:** 158

---

## Objetivo (2-3 linhas)

Construir simulacoes deterministicas da MAC (dry-run + batch) para permitir ao Conselho responder "o que muda se alterarmos policy X?" com evidencias. Implementar plano adiabatico (mudanca gradual) e expor MI/Experiencias de forma governada. Preparar S43 (GO/NO-GO Fase 2).

---

## Documentos do Plano

| Documento | Caminho |
|-----------|---------|
| **Cap.4 Bloco 4 (Tasks e Waves)** | `docs/s42_cap_4_4_tasks_e_waves.md` |
| **YAML de Execucao** | `docs/s42_tasks_execucao.yml` |
| **Analise de Gaps** | `docs/s42_gap_analysis.md` |
| **Spec Master S42** | `docs/Agents/Planejamento/Programa 2/Sprint 42/S42_spec.md` |
| **Filemap Spec** | `docs/Agents/Planejamento/Programa 2/Sprint 42/FILEMAP.md` |

---

## Estrutura de Waves v3.0

| Wave | Nome | Tasks | Objetivo |
|------|------|-------|----------|
| W0 | Fundacao MAC | 24 | Modulos, schemas, migrations, configs, datasets canonicos (~1100 casos), manifest |
| W1 | MAC Simulate | 22 | Endpoint dry-run deterministico com manifest completo |
| W2 | MAC Batch | 18 | Simulacao em lote + scorecards + streaming + cancel |
| W3 | Plano Adiabatico | 16 | Validador + simulador por fases + rollback |
| W4 | MI/Exp Exposure | 20 | Exposicao parcial governada + RBAC + redaction + derivation |
| W5 | Frontend P4 | 32 | UI completa com virtualization, disclaimers, estados MI, diffs |
| W6 | ORR/Bundle | 26 | Scripts de gate + runbooks + teste carga + bundle com redaction |

---

## Como Seguir as Waves

1. **Comecar por W0 (Fundacao)** — criar modulos, migrations, configs, datasets canonicos
2. **W1 (MAC Simulate)** — implementar dry-run unitario (G30) com manifest completo
3. **W2 e W3 podem rodar em paralelo** apos W1:
   - W2: batch + scorecards + cancel + streaming (G31)
   - W3: plano adiabatico + rollback (G32)
4. **W4 (MI Exposure)** — pode iniciar apos W1
5. **W5 (Frontend)** — requer APIs de W1, W2, W4
6. **W6 (ORR/Bundle)** — consolidacao final, requer W0-W5

---

## Invariantes (Inegociaveis)

| ID | Descricao | Verificacao |
|----|-----------|-------------|
| INV_S42_SIM_01 | Simulacao NAO muda TruthState | S42-BE-015, S42-TST-002 |
| INV_S42_DET_01 | Replay 100% quando T=0 | S42-BE-016, S42-TST-002, S42-TST-011 |
| INV_S42_TRAIL_01 | Provenance completa (manifest com lineage) | S42-BE-005, S42-BE-017, S42-FE-018, S42-FE-020 |
| INV_S42_PRIV_01 | Privacidade MI (RBAC + redaction) | S42-BE-064..067, S42-TST-040..042 |
| INV_S42_QUAL_01 | Sem PASS sintetico | S42-BND-001..008 |

---

## Metricas de Sucesso (Targets MAC Anexo D)

| Metrica | Target | Verificacao |
|---------|--------|-------------|
| Accuracy gold standard | >= 95% | S42-TST-010 |
| Attack detection (global) | >= 95% | S42-BE-038 |
| Attack detection (temporal) | >= 98% | S42-DAT-005 |
| Attack detection (reversal) | >= 99% | S42-DAT-006 |
| Replay concordance (T=0) | = 100% | S42-TST-002 |
| Audit trail | = 100% | S42-BE-067 |
| Performance p95 | < 500ms | S42-TST-001, S42-PERF-001 |
| Performance p99 | < 2s | S42-TST-001, S42-PERF-001 |

---

## Melhorias v3.0 vs v2.0

| Area | v2.0 | v3.0 | Delta |
|------|------|------|-------|
| Tasks totais | 111 | 158 | +47 |
| Datasets | 80 casos | ~1100 casos | +1020 |
| Runbooks | 1 | 6 | +5 |
| Manifest/Lineage | Parcial | Completo | Full |
| Batch states | 4 | 5 (+ cancel) | +1 |
| Batch streaming | Nao | Sim | New |
| Experience derivation | Nao | Sim | New |
| Load tests | Nao | Sim | New |
| Testes MI states FE | Nao | Sim | New |
| Virtualization FE | Nao | Sim | New |

---

## Gaps Conhecidos v3.0

Nenhum gap critico remanescente apos 18 rodadas de refinamento. Todos os gaps identificados na analise inicial foram resolvidos com tasks especificas.

---

## Alertas para o ACE

1. **Nao confundir simulacao com producao** — disclaimers sao obrigatorios (S42-FE-015)
2. **Determinismo e critico** — usar seed + T=0 para replay (S42-BE-016)
3. **MI/Experiencias sao sensiveis** — redaction por padrao, RBAC real (S42-BE-064..067)
4. **Scorecards precisam de provenance** — sem manifest = NO-GO (S42-BND-001..008)
5. **Datasets devem ser canonicos** — estrutura conforme Cap.6B2 (~1100 casos)
6. **Cancel de batch deve ser graceful** — registrar cancel_reason (S42-BE-032)
7. **Evidencias em out/ devem ser redatadas** — script automatico (S42-BND-007)

---

## Tasks Criticas (Bloqueadores)

Se qualquer uma destas falhar, o sprint e NO-GO:

| Task | Motivo |
|------|--------|
| S42-BE-016 | Determinismo e invariante inegociavel |
| S42-BE-005 | Manifest/lineage completo e obrigatorio |
| S42-DAT-001..008 | Datasets sao pre-requisito para batch |
| S42-BE-064..067 | RBAC/Redaction protege privacidade |
| S42-CI-001..006 | Scripts de gate geram evidencias |

---

## Proximos Passos

1. Ler `docs/s42_tasks_execucao.yml` (versao 3.0)
2. Iniciar W0 (S42-BE-001, S42-BE-002, S42-DB-001, etc.)
3. Criar datasets canonicos (~1100 casos) logo
4. Reportar qualquer gap encontrado imediatamente

---

## Contato para Gaps

Se encontrar:
- Task impossivel de executar
- Dependencia nao mapeada
- Contradicao com a spec

**Reportar como gap para revisao do Planner.**

---

## Assinatura

```
Sprint: S42
Versao: 3.0 MATURE
Tasks: 158
Waves: 7 (W0-W6)
Gates: G30, G31, G32, G33, G34, G35
Invariantes: 5
Riscos mitigados: 7
Datasets: ~1100 casos
Runbooks: 6
Refinamentos aplicados: 18
Status: PRONTO PARA EXECUCAO
```

*Handoff gerado pelo Sprint Planner Tecnico v7*
*18 rodadas de refinamento aplicadas*
*Analise de gaps resolvida*
