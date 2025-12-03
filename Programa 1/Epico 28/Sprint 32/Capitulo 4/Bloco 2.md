# Inspectah — Sprint 32
## Capítulo 4 — Bloco 2
### Fase 0 & Fase 1 — Preparação (G0) + Fundamentos do Truth-DB (G1)

> Este bloco desdobra as duas primeiras fases da execução da S32 em **passos concretos**, comandos, evidências e critérios de saída. É o roteiro para tirar a sprint do papel sem tropeçar no básico.

---

#### 4.2.1 Fase 0 — Preparação & G0 (Scope & Baseline)

**Objetivo:** garantir que a S32 começa com o mínimo de estrutura, docs e scripts em ordem. Nada de sprint começando em pasta bagunçada.

##### 4.2.1.1 Passos concretos da Fase 0

1. **Criar/ajustar docs da S32 em `docs/`**  
   - Arquivos esperados (nomes ajustáveis ao padrão do repo, mas equivalentes):
     - `docs/sprint_32_capitulo_1_contexto.md`  
     - `docs/sprint_32_capitulo_2_gates_e_metricas.md`  
     - `docs/sprint_32_capitulo_3_arquitetura_e_filemap.md`  
     - `docs/sprint_32_capitulo_4_execucao_e_evidencias.md`  
     - `docs/sprint_32_capitulo_5_orr_operacao_pos_sprint.md`  
     - `docs/sprint_32_capitulo_6_learnings_e_anti_gaps.md`  
     - `docs/sprint_32_capitulo_7_tasks.md`
   - Cada capítulo pode começar como ponte de texto (copiado/adaptado destes canvases) e ser refinado conforme a sprint avança.

2. **Criar esqueleto dos scripts de gates em `bin/`**  
   - Arquivos mínimos:
     - `bin/s32_g0_scope_and_baseline.sh`  
     - `bin/s32_g1_models_and_invariants.sh`  
     - `bin/s32_g2_promotion_flows.sh`  
     - `bin/s32_g3_contestation_flows.sh`  
     - `bin/s32_g4_orr_and_bundle.sh`
   - Versão inicial pode conter apenas:
     - `set -euo pipefail`  
     - echo com o nome do gate;  
     - criação de diretórios `out/scorecards/` e `out/evidence/` se ainda não existirem.

3. **Garantir estrutura de diretórios de saída**  
   - Verificar/garantir existência de:
     - `out/scorecards/`  
     - `out/evidence/`  
     - `out/bundles/`
   - Opcional: criar subpastas vazias específicas da S32 (`out/evidence/S32_*`) para já marcar território.

4. **Conferir dependências mínimas do backend**  
   - Ambiente Python/venv ativo.  
   - Ferramentas de migração (Alembic ou equivalente) funcionando.  
   - Testes básicos de backend rodando (para garantir que a S32 não começa em cima de um repo já quebrado).

##### 4.2.1.2 Script & execução do G0

Esqueleto conceitual do `bin/s32_g0_scope_and_baseline.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

# 1) Garantir diretórios de saída
mkdir -p out/scorecards out/evidence out/bundles

# 2) Checar presença mínima de docs e scripts
# (implementação concreta fica a cargo do Codex, mas a ideia é:
#  - verificar existência de arquivos esperados;
#  - acumular erros/warnings;
#  - gerar scorecard JSON.)

python - << 'PY'
# Script inline para gerar S32_G0_scope_and_baseline.json
PY
```

Critério de saída da Fase 0:
- `out/scorecards/S32_G0_scope_and_baseline.json` existe com `status = "PASS"` (ou, na pior hipótese, `"WARN"` para algo aceitável).  
- Todos os arquivos de docs e scripts de gate existem, mesmo que ainda não estejam completos.

Evidências mínimas:
- Scorecard G0.  
- Log de execução do script (opcional) em `out/evidence/S32_G0_scope_and_baseline/`.

---

#### 4.2.2 Fase 1 — Fundamentos do Truth-DB (Modelos, Migrações & Invariantes / G1)

**Objetivo:** sair da fase com o modelo de dados do Truth-DB sólido, migração S32 criada e invariantes críticas codificadas em testes.

##### 4.2.2.1 Passos concretos da Fase 1

1. **Implementar/ajustar modelos em `app/truthdb/models.py`**  
   - Incluir/atualizar classes:
     - `FactBlock`  
     - `EvidenceBlock`  
     - `TruthState`  
     - `DecisionBlock`  
     - `ContestRecord`
   - Garantir que:
     - FKs obrigatórias estão modeladas (sem blocos órfãos);  
     - campos de status e enums seguem padrão do projeto;  
     - campos `metadata` existem apenas onde faz sentido.

2. **Criar/ajustar migração S32 em `migrations/versions/XXXX_s32_truthdb_blocks.py`**  
   - Criar tabelas novas ou alterar tabelas existentes conforme o Bloco 2 do Capítulo 3.  
   - Incluir índices básicos em `claim_id`, `fact_block_id`, `truth_state_id`.  
   - Garantir que a migração é:
     - idempotente (subida repetida não causa desastre);  
     - compatível com dados existentes.

3. **Criar testes de invariantes em `tests/truthdb/test_models_and_invariants.py`**  
   - Casos de teste mínimos:
     - **Sem blocos órfãos:** tentar criar `EvidenceBlock` sem `fact_block_id` deve falhar; tentar persistir `DecisionBlock` sem `truth_state_id` deve falhar; etc.  
     - **Estados finais exigem DecisionBlock:** tentar salvar `TruthState` com `status` final (`true`, `rejected`, etc.) sem `current_decision_block_id` deve levantar erro ou ser bloqueado pela lógica.  
     - **Histórico monotônico:** simular contestação (ou uma atualização sucessiva de estado) e garantir que não há deleção de blocos; número de blocos nunca diminui.  
     - **Integridade de FKs:** criar entidades com FKs inválidas deve falhar claramente.

4. **Configurar script do gate G1: `bin/s32_g1_models_and_invariants.sh`**  
   - Passos típicos:
     - ativar venv;  
     - aplicar migrações em banco de teste (ex.: `alembic upgrade head` ou comando equivalente);  
     - rodar `pytest tests/truthdb/test_models_and_invariants.py`;  
     - coletar status e gerar `out/scorecards/S32_G1_models_and_invariants.json`.

5. **Rodar iterações locais de G1**  
   - Executar o script G1 localmente;  
   - corrigir erros de migração, modelo ou teste até obter um PASS consistente.

##### 4.2.2.2 Estrutura esperada do scorecard G1

Exemplo conceitual de `out/scorecards/S32_G1_models_and_invariants.json`:

```json
{
  "gate": "S32_G1_models_and_invariants",
  "status": "PASS",
  "migrations_ok": true,
  "tests_ok": true,
  "checked_invariants": [
    "no_orphan_fact_blocks",
    "no_orphan_evidence_blocks",
    "no_orphan_decision_blocks",
    "no_orphan_contest_records",
    "final_states_require_decision_block",
    "history_is_monotonic"
  ],
  "timestamp": "2025-..-..T..:..:..Z",
  "notes": []
}
```

O formato exato pode ser ajustado, mas os campos acima representam o **contrato lógico** da S32 para G1.

##### 4.2.2.3 Critérios de saída da Fase 1

A Fase 1 é considerada concluída quando:

1. **Modelos e migrações S32 estão implementados e versionados**  
   - `app/truthdb/models.py` contém todas as entidades do Truth-DB descritas no Capítulo 3.  
   - `migrations/versions/XXXX_s32_truthdb_blocks.py` sobe um schema coerente com os modelos.

2. **Testes de invariantes estão verdes localmente**  
   - `pytest tests/truthdb/test_models_and_invariants.py` passa sem erros.

3. **Gate G1 está verde**  
   - `bin/s32_g1_models_and_invariants.sh` roda de ponta a ponta;  
   - scorecard G1 existe e marca `status = "PASS"`.

4. **Não há regressões óbvias em outros testes de backend**  
   - Um `pytest` de sanidade (pelo menos do subset crítico) não acusa que a introdução dos modelos/migrações quebrou outros domínios.

Evidências mínimas para Fase 1:
- `out/scorecards/S32_G1_models_and_invariants.json`.  
- Logs/migrações em `out/evidence/S32_G1_models_and_invariants/`.  
- Commits no repositório refletindo a estrutura de dados descrita no Capítulo 3.

---

#### 4.2.3 Como Fase 0 e Fase 1 preparam o terreno para o resto da S32

- Com **G0 verde**, a sprint tem:
  - docs ancorando o plano;  
  - scripts de gates esqueleto criados;  
  - diretórios de saída padronizados.

- Com **G1 verde**, a sprint tem:
  - Truth-DB modelado e migrado;  
  - invariantes críticas protegidas por testes;  
  - base sólida para implementar promoção (Fase 2) e contestação (Fase 3) sem medo de pisar em areia movediça.

Os próximos blocos do Capítulo 4 vão assumir Fase 0/1 concluídas e focar em **como implementar e validar os fluxos de promoção (G2), contestação (G3) e o bundle final (G4)** com a mesma disciplina de evidências e gates.

