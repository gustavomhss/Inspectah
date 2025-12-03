# Inspectah — Sprint 32
## Capítulo 4 — Bloco 4
### Fase 4 — Sanidade Cruzada, Regressões, G4 & Bundle Final da Sprint 32

> Este bloco fecha o Capítulo 4 detalhando a Fase 4: como garantir que nada crítico foi quebrado, como montar o bundle `inspectah_s32_evidence_bundle.zip`, como rodar o G4 e como preparar a S32 para ORR e operação pós‑sprint.

---

#### 4.4.1 Objetivo da Fase 4

A Fase 4 tem três objetivos principais:

1. Verificar **sanidade cruzada** entre o novo Truth‑DB/fluxos de contestação e o restante do sistema (com foco em ingestão/claims).  
2. Consolidar todos os gates (G0–G3) e gerar o **bundle único de evidências** da S32.  
3. Produzir material claro para ORR, permitindo que o conselho julgue a sprint com base em fatos e não em opinião.

Sem essa fase, a S32 poderia até ter código funcional, mas seria um “ato de fé” – e o Inspectah não trabalha com fé, trabalha com evidência.

---

#### 4.4.2 Sanidade cruzada & regressões (SA32_6)

Antes de pensar em bundle, a Fase 4 precisa responder: **“o que a S32 quebrou?”**. O ideal é “nada”, mas a resposta precisa ser baseada em testes.

Passos sugeridos:

1. Rodar subconjunto de gates/suites de sprints anteriores
   - No mínimo, os gates que tocam ingestão/claims e domínio de casos (S21+, S24 etc.), por exemplo:  
     - scripts `bin/s21_*`, `bin/s24_*`, ou workflows equivalentes de CI.  
   - Registrar resultados (PASS/WARN/FAIL) e impactos percebidos.

2. Rodar suites de testes de regressão
   - `pytest` (ou equivalente) para módulos de ingestão/claims mais críticos.  
   - Verificar se a introdução do Truth‑DB e dos novos serviços não quebrou APIs, modelos ou contratos.

3. Analisar resultados do ponto de vista de risco
   - Falhas que não impactam diretamente promoção/contestação/Truth‑DB podem ser tratadas como WARN, desde que registadas no Capítulo 5 como dívida clara.  
   - Qualquer falha que indique corrupção de dados, quebra de ingestão ou inconsistência grave deve ser tratada como risco alto – potencialmente bloqueando GO.

4. Registrar síntese em notas
   - Criar um pequeno resumo de sanidade/reversões no Capítulo 5 (ORR), referenciando quais gates históricos foram rodados e seus estados.

Evidências mínimas de sanidade cruzada:
- Logs de execução de gates/suites antigas.  
- Notas de regressão (ou ausência delas) em formato reaproveitável no ORR.

---

#### 4.4.3 Gate G4 — `s32_g4_orr_and_bundle.sh`

O G4 é o gate “fechamento de livro” da sprint. Sua função é:

- Validar que G0–G3 foram executados e estão em estado aceitável.  
- Confirmar que as evidências mínimas para cada SA32_x existem.  
- Montar o bundle de evidências da S32.  
- Gerar um scorecard final (`S32_G4_orr_and_bundle.json`) que resuma o estado geral da sprint.

Esqueleto conceitual do script:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

mkdir -p out/scorecards out/evidence out/bundles

# 1) Validar presença dos scorecards G0–G3
#    - S32_G0_scope_and_baseline.json
#    - S32_G1_models_and_invariants.json
#    - S32_G2_promotion_flows.json
#    - S32_G3_contestation_flows.json

# 2) Validar presença das principais pastas de evidência
#    - out/evidence/S32_G1_models_and_invariants/
#    - out/evidence/S32_G2_promotion_flows/
#    - out/evidence/S32_G3_contestation_flows/

# 3) Opcional: rodar uma checagem rápida de sanidade cruzada

# 4) Montar bundle zipado com tudo o que interessa
BUNDLE_PATH="out/bundles/inspectah_s32_evidence_bundle.zip"
rm -f "$BUNDLE_PATH"
zip -r "$BUNDLE_PATH" \
  out/scorecards/S32_G0_scope_and_baseline.json \
  out/scorecards/S32_G1_models_and_invariants.json \
  out/scorecards/S32_G2_promotion_flows.json \
  out/scorecards/S32_G3_contestation_flows.json \
  out/evidence/S32_G1_models_and_invariants \
  out/evidence/S32_G2_promotion_flows \
  out/evidence/S32_G3_contestation_flows

# 5) Gerar scorecard S32_G4_orr_and_bundle.json
python - << 'PY'
# Script Python que:
#  - lê scorecards G0–G3;
#  - sintetiza estado geral (PASS/WARN/FAIL);
#  - checa existência do bundle;
#  - grava S32_G4_orr_and_bundle.json.
PY
```

O Codex pode enriquecer esse esqueleto com verificações extras (checksum do bundle, sizes mínimos etc.), mas a responsabilidade conceitual do G4 é essa.

Exemplo conceitual de `S32_G4_orr_and_bundle.json`:

```json
{
  "gate": "S32_G4_orr_and_bundle",
  "status": "PASS",
  "gates_summary": {
    "G0": "PASS",
    "G1": "PASS",
    "G2": "PASS",
    "G3": "PASS"
  },
  "bundle_exists": true,
  "bundle_path": "out/bundles/inspectah_s32_evidence_bundle.zip",
  "notes": []
}
```

---

#### 4.4.4 Conteúdo mínimo do bundle `inspectah_s32_evidence_bundle.zip`

O bundle é o “dossiê” da sprint. Para a S32, ele deve conter, no mínimo:

1. Scorecards da S32
   - `out/scorecards/S32_G0_scope_and_baseline.json`  
   - `out/scorecards/S32_G1_models_and_invariants.json`  
   - `out/scorecards/S32_G2_promotion_flows.json`  
   - `out/scorecards/S32_G3_contestation_flows.json`  
   - `out/scorecards/S32_G4_orr_and_bundle.json`

2. Evidências principais
   - `out/evidence/S32_G1_models_and_invariants/`  
     - logs de migrações;  
     - logs de testes de invariantes.  
   - `out/evidence/S32_G2_promotion_flows/`  
     - logs de execução;  
     - dumps de blocos/TruthStates antes/depois de ao menos um cenário.  
   - `out/evidence/S32_G3_contestation_flows/`  
     - logs de contestação;  
     - dumps de TruthStates e ContestRecords antes/depois de cenários de teste.

3. README/guia de replay
   - Arquivo simples (ex.: `README_S32_BUNDLE.md`) explicando:
     - pré‑requisitos de ambiente;  
     - comandos para reexecutar G1, G2, G3;  
     - onde encontrar dumps e como interpretá‑los.

Se o projeto já tiver um padrão de bundle em sprints anteriores (ex.: S20–S31), a S32 deve seguir esse padrão e apenas estendê‑lo com evidências específicas do Truth‑DB.

---

#### 4.4.5 Critérios de saída da Fase 4 (e da S32 como um todo)

A Fase 4 – e, por consequência, a Sprint 32 – é considerada concluída quando:

1. Sanidade cruzada razoável foi executada
   - Foram rodados, pelo menos, os gates/suites essenciais de ingestão/claims.  
   - Qualquer regressão relevante está documentada e classificada como BLOQUEANTE ou NÃO‑BLOQUEANTE.  
   - Não há evidência de corrupção de dados ou quebra grave de contratos.

2. G0–G3 estão verdes ou com WARNs justificados
   - Todos os scorecards S32_G0–S32_G3 existem e refletem a realidade.  
   - WARNs, se existirem, estão comentados no Capítulo 5/Capítulo 6.

3. G4 está verde
   - `s32_g4_orr_and_bundle.sh` roda de ponta a ponta.  
   - `S32_G4_orr_and_bundle.json` marca `status = "PASS"` (ou, em caso extremo, `"WARN"` com justificativa forte e aceite do conselho).

4. Bundle S32 existe, é íntegro e razoavelmente pequeno
   - `out/bundles/inspectah_s32_evidence_bundle.zip` existe.  
   - Consegue ser aberto sem erros;  
   - Contém, no mínimo, os elementos listados na seção anterior.

5. Capítulos 4, 5 e 6 estão coerentes
   - Capítulo 4 (este) reflete de fato o que foi feito.  
   - Capítulo 5 usa os scorecards/bundle como base para ORR.  
   - Capítulo 6 registra learnings, anti‑gaps e dívidas derivadas da execução real.

---

#### 4.4.6 Como este Bloco 4 deve ser usado

Para quem está implementando
- Como checklist final antes de declarar a S32 “entregue”:  
  - sanidade cruzada feita;  
  - G4 rodado;  
  - bundle gerado.

Para quem está revisando em ORR
- Como mapa de onde estão os artefatos que importam:  
  - quais scorecards olhar;  
  - onde estão as evidências de promoção/contestação;  
  - como reexecutar os gates se necessário.

Para sprints futuras (S33+)
- Como referência de padrão mínimo para qualquer sprint que mexa com Truth‑DB ou com algum subsistema core do Inspectah:  
  - sem bundle e sem sanidade cruzada, não há “DONE” – há apenas código suspeito.

Com este Bloco 4, o Capítulo 4 fica fechado: a Sprint 32 ganha uma rota claramente definida de início (G0) a fim (G4 + bundle), com disciplina de sanidade e evidência à altura do papel central que o Truth‑DB e a contestação desempenham no Inspectah.

