# Sprint 14 – Capítulo 4 (Runbook Operacional Definitivo)

Plano operacional para o Codex + humano, amarrado aos Capítulos 1–3 da Sprint 14 e ao estado pós‑S13.

---

## 0) Visão geral (para o Codex e para o humano)

### 0.1 Estado atual obrigatório

Antes de começar qualquer coisa da S14, assuma como **pré‑requisito imutável**:

- **S12** – ingestão contínua enxuta + Debunker v0 + casos/timelines + Explorer/feedback v0,
  - Gates **S12_G0…S12_G8** verdes.
  - Decisão **S12_G8 = GO**.
- **S13** – piloto multi‑domínio (obra pública, evento climático, projeto de lei, carreira política, influencer, atleta) rodando sobre a S12,
  - Gates **S13_G0…S13_G8** verdes.
  - Decisão **S13_G8 = GO**.

Nada na Sprint 14 tem permissão de **quebrar ou regredir** esse estado.

### 0.2 Objetivo da Sprint 14

Conforme Capítulos 1–3 da S14, o objetivo é:

- Endurecer o **truth kernel v0** (case_service, timeline_service, truthdb_adapter + snapshots S12/S13) em um núcleo bem definido e verificável.
- Organizar o **Debunker v0** como serviço lógico único, com regras explícitas e checadas por gate.
- Garantir que **Explorer/feedback** continuem clientes corretos do kernel, mesmo após ajustes da S14.
- Fazer **limpezas/migrações leves**, focadas em sanidade e idempotência.
- Criar gates **S14_G0…S14_G8**, scorecards e evidências, mais uma **ORR S14** documentando o estado final.

Tudo isso sem introduzir features de Fase 2.

### 0.3 Fora de escopo (Fase 2, não mexer agora)

Toda a lista abaixo **permanece apenas em blueprints/backlog**, não deve ser implementada na S14:

- Sistema de Blocos completo (blocos/sub‑blocos/fatos/versões/disputas, regras de promoção etc.).
- Blockchain automática (Merkle, âncoras periódicas, commits ou provas on‑chain).
- Sistema de **reputação** formal de fontes/usuários, gamificação, comitês avançados.
- Fluxos de contestação pública complexos com bonds/staking.
- TLA+ ou provas formais para o kernel/blocos.

Se o Codex precisar mencionar isso em código ou docs, deve **apenas apontar para blueprints existentes** ou para `docs/sprint_14_backlog_fase2.md`.

---

## 1) Pré‑flight de trabalho

### 1.1 Repositório e branch

Repositório local:

- Caminho: `/Users/gustavoschneiter/Documents/Inspectah`
- Remote esperado: `origin` → `github.com:gustavomhss/Inspectah.git`

Fluxo inicial:

```bash
cd /Users/gustavoschneiter/Documents/Inspectah

git checkout main
git pull --ff-only origin main

# criar branch da sprint 14 a partir do main atualizado
git checkout -b s14_hardening_truth_kernel_v0
```

Todas as mudanças da S14 acontecem em `s14_hardening_truth_kernel_v0`.

### 1.2 Disciplina de execução (Codex + humano)

Regras gerais:

- Sempre assumir que está rodando comandos **na raiz** do repo.
- Antes de rodar gates da S14 pela primeira vez ou após mudanças profundas, **revalidar S12 e S13**:
  ```bash
  bash bin/s12_gates_all.sh && bash bin/s12_g8_decision.sh
  bash bin/s13_gates_all.sh && bash bin/s13_g8_decision.sh
  ```
- Não apagar, sobrescrever ou reformatar artefatos históricos de S1…S13 (docs, scorecards, evidências).
- Novos scripts/gates da S14 devem ser **idempotentes**: rodar 2x não pode quebrar nada.
- Não commitar `.pyc`, `inspectah.db`, arquivos de cache temporários ou dados gigantes de evidência fora dos diretórios oficiais (`out/evidence/…`).
- É permitido usar internet para documentação de libs/padrões, mas **jamais** para inventar escopo novo fora dos Capítulos 1–3.

Boas práticas de Git (para o Codex seguir e o humano revisar):

- Commits pequenos, coesos, mensagens claras (`s14: …`).
- Antes de cada commit:
  ```bash
  git status
  ```
  e conferir se só há arquivos esperados da S14.

---

## 2) Waves da Sprint 14

A Sprint 14 é executada em waves. Cada wave tem entregáveis específicos, mapeados diretamente aos gates do Capítulo 2.

### Wave 0 – Skeletons, guardrails e CI (_setup da S14_)

**Objetivo:** criar toda a estrutura da S14 (docs, configs, scripts, gates, CI) com FAIL controlado.

Passos:

1. **Docs skeleton em `docs/`:**
   - `docs/sprint_14_truth_kernel.md`
     - Estrutura mínima: introdução, definição de truth kernel v0, domínios cobertos, relação com S12/S13, seção “Próximas waves”.
   - `docs/sprint_14_debunker_v0.md`
     - Estrutura mínima: visão geral, decisões suportadas, domínios, seção “Próximas waves”.
   - `docs/sprint_14_backlog_fase2.md`
     - Estrutura mínima: seções vazias para Sistema de Blocos, blockchain, reputação, contestação avançada, TLA+.
   - `docs/sprint_14_orr_summary.md`
     - Mesmo esqueleto das ORRs S12/S13: objetivo, entregáveis, tabela S14_G0…S14_G8, exec local/CI, riscos/próximos passos.

   Importante: **sem TODOs crus**. Use frases neutras do tipo “Esta seção será detalhada na Wave 1/2 da S14”.

2. **Configs em `config/`:**
   - `config/s14_truth_kernel.yml`
     - Estrutura mínima: lista de domínios, campos reservados para estados de caso/timeline.
   - `config/s14_debunker_rules.yml`
     - Estrutura mínima: entrada para cada domínio com espaço para thresholds/flags.

3. **Scripts skeleton em `scripts/`:**
   - `scripts/s14_truth_kernel_checks.py`
   - `scripts/s14_debunker_consistency.py`
   - `scripts/s14_explorer_contracts.py`
   - `scripts/s14_migrations_and_cleanup.py`
   - `scripts/s14_metrics_snapshot.py`
   - `scripts/s14_decision.py`

   Todos devem:
   - Ser importáveis.
   - Ter uma função principal clara (ex.: `run()` ou similar).
   - No início, lançar `NotImplementedError("S14 Wave 0 skeleton – implementar na Wave X")`.

4. **Gates skeleton em `bin/`:**
   - `bin/s14_g0_env_repo.sh`
   - `bin/s14_g1_truth_kernel.sh`
   - `bin/s14_g2_debunker_consistency.sh`
   - `bin/s14_g3_explorer_contracts.sh`
   - `bin/s14_g4_migrations_and_cleanup.sh`
   - `bin/s14_g5_regression_smoke.sh`
   - `bin/s14_g6_docs_dna_alignment.sh`
   - `bin/s14_g7_observabilidade.sh`
   - `bin/s14_g8_decision.sh`
   - `bin/s14_gates_all.sh`

   Comportamento dos skeletons:
   - Conferir raiz do repo.
   - Escrever scorecard `out/scorecards/S14_GX_*.json` com `status = "FAIL"` e `reason = "S14 skeleton"`.
   - Sair com código ≠ 0.

5. **Workflow de CI em `.github/workflows/_s14-gates.yml`:**
   - Seguir o padrão de `_s12-gates.yml` e `_s13-gates.yml`:
     - Checkout.
     - Setup ambiente.
     - `bash bin/s14_gates_all.sh`.
     - Publicar `out/scorecards/` e `out/evidence/S14_*` como artefatos.

6. **Atualizar `bin/ci_local.sh`:**
   - Incluir chamada a `bash bin/s14_gates_all.sh` no final da sequência.

Check da Wave 0:

- `bash bin/s14_gates_all.sh` falha em S14_G0 com FAIL controlado (skeleton), **sem** stacktrace estranho.

### Wave 1 – Truth kernel v0 (G1 real)

**Objetivo:** consolidar o truth kernel v0 em docs/configs + gate G1 real.

Passos:

1. Completar `docs/sprint_14_truth_kernel.md` com base nos Capítulos 1–3 e ORRs S12/S13:
   - Descrever componentes do kernel: case_service, timeline_service, truthdb_adapter.
   - Especificar de onde vêm os snapshots oficiais (pastas S12/S13 citadas no Cap. 3).
   - Detalhar como cada domínio (obra pública, evento climático, projeto de lei, carreira política, influencer, atleta) aparece no kernel.

2. Preencher `config/s14_truth_kernel.yml`:
   - Lista de domínios expected.
   - Mapeamento domínio → case_keys (quando conhecidos) ou padrões.
   - Estados válidos de caso/timeline (ex.: `planejado`, `em_andamento`, `concluido`, `suspeito`, `cancelado`).

3. Implementar `scripts/s14_truth_kernel_checks.py`:
   - Ler `config/s14_truth_kernel.yml`.
   - Ler snapshots de S12/S13 (paths definidos no Capítulo 3 da S14).
   - Reconstituir visão de kernel por domínio.
   - Verificar invariantes definidas no Capítulo 2 (por ex., proporção mínima de timelines válidas, ausência de estados impossíveis, etc.).
   - Emitir `out/evidence/S14_G1/kernel_integrity_report.json` com métricas por domínio e `kernel_integrity_ratio` global.

4. Implementar `bin/s14_g1_truth_kernel.sh`:
   - Rodar `python -m scripts.s14_truth_kernel_checks`.
   - Ler `kernel_integrity_report.json`.
   - Aplicar thresholds do Capítulo 2 (SLO para `kernel_integrity_ratio`).
   - Escrever `out/scorecards/S14_G1_truth_kernel.json` com `status`, `kernel_integrity_ratio` e resumo.

5. Atualizar `bin/s14_gates_all.sh` para, a partir de agora, rodar **G0 (ainda skeleton) → G1 real → G2 skeleton…**.

Check da Wave 1:

- `bash bin/s14_g1_truth_kernel.sh` → PASS ou WARN aceitável conforme Cap. 2.

### Wave 2 – Debunker consistency (G2 real) + G0 real

**Objetivo:** consolidar o Debunker v0, centralizar regras e promover G0 a gate real.

Passos:

1. Completar `docs/sprint_14_debunker_v0.md`:
   - Explicar decisões possíveis (aceito/suspeito/incerto/rejeitado, etc.).
   - Redigir diferenças de heurística por domínio.
   - Registrar expectativa de explicabilidade (quase todos os casos com explicação legível).

2. Preencher `config/s14_debunker_rules.yml`:
   - Thresholds e flags por domínio.
   - Exemplo: domínios mais sensíveis exigem explicações mais completas.

3. Implementar `scripts/s14_debunker_consistency.py`:
   - Construir um conjunto fixo de eventos sintéticos por domínio.
   - Passar pelo `s12_debunker_runner` existente.
   - Calcular `debunker_explanation_coverage` e, se pertinente, métricas de consistência (mesmo tipo de caso → decisões estáveis).
   - Gravar `out/evidence/S14_G2/debunker_consistency_report.json` com métricas globais e por domínio.

4. Implementar `bin/s14_g2_debunker_consistency.sh`:
   - Rodar `python -m scripts.s14_debunker_consistency`.
   - Aplicar thresholds do Capítulo 2.
   - Escrever `out/scorecards/S14_G2_debunker_consistency.json`.

5. Promover `bin/s14_g0_env_repo.sh` a gate real:
   - Verificar:
     - Raiz do repo (`git rev-parse --show-toplevel`).
     - Branch atual = `s14_hardening_truth_kernel_v0`.
     - Remote origin correto.
     - Presença de `Sprint 14/Capitulo 1.md…Capitulo 4.md`.
     - Presença dos docs da S14 em `docs/`.
     - Scorecards `S12_G8_decision.json` e `S13_G8_decision.json` com `decision = "GO"`.
   - Gravar `out/evidence/S14_G0/env_snapshot.json`.
   - Gravar `out/scorecards/S14_G0_env_repo.json` com `status = "PASS"`.

6. Ajustar `bin/s14_gates_all.sh` para ordem final: **G0 → G1 → G2 → … → G7**.

Checks da Wave 2:

- `bash bin/s14_g0_env_repo.sh` → PASS.
- `bash bin/s14_g1_truth_kernel.sh` → PASS/WARN aceitável.
- `bash bin/s14_g2_debunker_consistency.sh` → PASS/WARN aceitável.

### Wave 3 – Explorer contracts (G3 real)

**Objetivo:** verificar que Explorer/feedback continuam em contrato correto com o kernel v0 endurecido.

Passos:

1. Implementar `scripts/s14_explorer_contracts.py`:
   - Reaproveitar cenários da S13 (docs de cenários Explorer) para montar um conjunto pequeno de queries por domínio.
   - Exercitar endpoints do Explorer (ex.: `/explorer/cases`, `/explorer/cases/{id}`) e, se fizer sentido, rotas de feedback relacionadas.
   - Validar estrutura das respostas (campos obrigatórios, tipos, presença de timeline e decisões).
   - Gravar `out/evidence/S14_G3/explorer_contracts.json` com requests/responses e métricas (por ex., `success_rate`).

2. Implementar `bin/s14_g3_explorer_contracts.sh`:
   - Rodar `python -m scripts.s14_explorer_contracts`.
   - Aplicar thresholds do Capítulo 2 para `success_rate`.
   - Gravar `out/scorecards/S14_G3_explorer_contracts.json`.

3. Revalidar S12/S13 após qualquer ajuste em Explorer/feedback:
   ```bash
   bash bin/s12_gates_all.sh && bash bin/s12_g8_decision.sh
   bash bin/s13_gates_all.sh && bash bin/s13_g8_decision.sh
   ```

Check da Wave 3:

- `bash bin/s14_g3_explorer_contracts.sh` → PASS.

### Wave 4 – Migrations & cleanup (G4 real)

**Objetivo:** aplicar migrações/limpezas leves, focadas em sanidade, sem quebrar nada.

Passos:

1. Implementar `scripts/s14_migrations_and_cleanup.py`:
   - Focar nas pendências listadas em lessons learned/Cap. 3.
   - Exemplos possíveis (só se estiverem alinhados com Cap. 3):
     - Normalizar nomes de domínios em configs.
     - Remover evidências obsoletas que não são mais usadas em nenhum gate.
     - Garantir existência de pastas esperadas em `out/evidence/S14_*`.
   - Script precisa ser **idempotente**.
   - Gravar `out/evidence/S14_G4/migrations_report.json` (o que foi feito, quantos arquivos afetados, etc.).

2. Implementar `bin/s14_g4_migrations_and_cleanup.sh`:
   - Rodar `python -m scripts.s14_migrations_and_cleanup`.
   - Escrever `out/scorecards/S14_G4_migrations_and_cleanup.json`.

3. Rodar gates S12/S13 novamente para garantir que nada foi quebrado.

Check da Wave 4:

- `bash bin/s14_g4_migrations_and_cleanup.sh` → PASS.

### Wave 5 – Regression smoke (G5 real)

**Objetivo:** criar um gate rápido de regressão que reusa testes existentes.

Passos:

1. Definir, nos Capítulos 2 e 3, qual subset de testes compõe o **smoke S14** (ex.: contratos críticos e algum teste de observabilidade).

2. Implementar `bin/s14_g5_regression_smoke.sh`:
   - Rodar o subset definido (por ex., `pytest -m "s14_smoke"` ou lista explícita de módulos).
   - Consolidar saída em `out/evidence/S14_G5/regression_smoke_report.json`.
   - Escrever `out/scorecards/S14_G5_regression_smoke.json` com regra PASS/WARN/FAIL clara (conforme Cap. 2).

Check da Wave 5:

- `bash bin/s14_g5_regression_smoke.sh` → PASS.

### Wave 6 – Docs/DNA alignment (G6 real)

**Objetivo:** garantir alinhamento entre docs da S14, DNA e backlog de Fase 2.

Passos:

1. Completar `docs/sprint_14_backlog_fase2.md`:
   - Mover, de forma organizada, todos os itens de blockchain, Sistema de Blocos completo, reputação, contestação avançada, TLA+ etc.
   - Referenciar os blueprints já existentes, sem duplicar conteúdo.

2. Implementar `bin/s14_g6_docs_dna_alignment.sh` (pode acionar um pequeno helper Python):
   - Verificar presença e estrutura mínima de:
     - `docs/sprint_14_truth_kernel.md`
     - `docs/sprint_14_debunker_v0.md`
     - `docs/sprint_14_backlog_fase2.md`
     - `docs/sprint_14_orr_summary.md`
   - Fazer um scan simples garantindo que termos como "blockchain", "Sistema de Blocos" e "reputação" aparecem nas seções corretas (blueprints + backlog Fase 2) e não como features implementadas da S14.
   - Gravar `out/evidence/S14_G6/docs_alignment_report.md`.
   - Escrever `out/scorecards/S14_G6_docs_dna_alignment.json` com status conforme Cap. 2.

Check da Wave 6:

- `bash bin/s14_g6_docs_dna_alignment.sh` → PASS.

### Wave 7 – Observabilidade S14 (G7 real)

**Objetivo:** consolidar métricas da S14 em snapshot único.

Passos:

1. Implementar `scripts/s14_metrics_snapshot.py`:
   - Ler scorecards `S14_G0…S14_G6`.
   - Extrair SLIs definidos no Cap. 2 (integridade do kernel, coverage do Debunker, sucesso do Explorer, saúde do smoke, docs alinhados).
   - Calcular `global_health` para a S14 (thresholds 0.95/0.90, por ex.).
   - Gravar `out/evidence/S14_G7/metrics_snapshot.json`.
   - Gravar `out/evidence/S14_G7/risks_and_debts.md` com riscos/débitos.

2. Implementar `bin/s14_g7_observabilidade.sh`:
   - Rodar `python -m scripts.s14_metrics_snapshot`.
   - Escrever `out/scorecards/S14_G7_observabilidade.json` com status baseado em `global_health`.

Check da Wave 7:

- `bash bin/s14_g7_observabilidade.sh` → PASS.

### Wave 8 – Decisão (G8 real) + ORR S14 + release

**Objetivo:** fechar a sprint com decisão GO/NO_GO formal e ORR consolidada.

Passos:

1. Implementar `scripts/s14_decision.py`:
   - Ler scorecards `S14_G0…S14_G7`.
   - Aplicar regras do Capítulo 2 (gates hard vs. soft; quando WARN é aceito).
   - Gerar `out/scorecards/S14_G8_decision.json` com:
     - `gate`, `status`, `decision`.
     - Mapa de gates + razões.
   - Gerar `out/evidence/S14_G8/summary.md` com resumo humano (principais SLIs, riscos, recomendação).

2. Implementar `bin/s14_g8_decision.sh`:
   - Garantir execução na raiz.
   - Rodar `python -m scripts.s14_decision`.
   - Checar presença de `S14_G8_decision.json` e `summary.md`.
   - Sair com FAIL se decisão for `NO_GO` ou se faltar artefato.

3. Fluxo de merge + release (humano):

   ```bash
   cd /Users/gustavoschneiter/Documents/Inspectah

   # garantir que s14 está commitada e verde
   git checkout s14_hardening_truth_kernel_v0
   bash bin/s14_gates_all.sh
   bash bin/s14_g8_decision.sh

   # merge no main
git checkout main
git pull --ff-only origin main
   git merge --no-ff s14_hardening_truth_kernel_v0 -m "merge: Sprint 14 hardening truth kernel v0"

   # rodar gates da S14, S13 e S12 no main
   bash bin/s14_gates_all.sh
   bash bin/s14_g8_decision.sh
   bash bin/s13_gates_all.sh && bash bin/s13_g8_decision.sh
   bash bin/s12_gates_all.sh && bash bin/s12_g8_decision.sh

   # publicar
   git push origin main
   git tag -a v0.5-s14 -m "Inspectah v0.5 — Sprint 14 hardening truth kernel v0"
   git push origin v0.5-s14
   ```

4. Atualizar `docs/sprint_14_orr_summary.md` com:
   - Tabela final de S14_G0…S14_G8 (todos PASS/WARN permitidos).
   - `decision = GO` (se aplicável).
   - Riscos/débitos e ponte clara para Fase 2.

Check da Wave 8:

- Gates S14_G0…S14_G8 com scorecards válidos.
- `S14_G8_decision.json` com `status = "PASS"` e `decision = "GO"`.
- `docs/sprint_14_orr_summary.md` atualizado.

---

## 3) Checklist compacto para o humano

Quando você quiser simplesmente "rodar a S14" e ver se está tudo no lugar, o fluxo é:

1. Garantir que S12 e S13 seguem verdes:
   ```bash
   bash bin/s12_gates_all.sh && bash bin/s12_g8_decision.sh
   bash bin/s13_gates_all.sh && bash bin/s13_g8_decision.sh
   ```

2. Trabalhar na branch `s14_hardening_truth_kernel_v0`, seguindo as waves acima (de preferência deixando o Codex aplicar as mudanças).

3. Ao final da sprint, na `s14_hardening_truth_kernel_v0`:
   ```bash
   bash bin/s14_gates_all.sh
   bash bin/s14_g8_decision.sh
   ```

4. Se tudo estiver PASS/GO, seguir com merge + tag conforme descrito na Wave 8.

5. Conferir rapidamente:
   - `out/scorecards/S14_G8_decision.json`
   - `out/evidence/S14_G8/summary.md`
   - `docs/sprint_14_orr_summary.md`

Se essas três coisas fizerem sentido e S12/S13 continuarem verdes, a S14 está entregue de forma **impecável** e pronta para abrir a porta da Fase 2 (Sistema de Blocos, blockchain, reputação, contestação avançada) em sprints futuras, sem dívida escondida no núcleo de verdade do Inspectah.

