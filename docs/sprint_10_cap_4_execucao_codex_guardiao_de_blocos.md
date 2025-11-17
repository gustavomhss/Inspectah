# Sprint 10 — Capítulo 4 — Execução e Automação (Truth-DB & Guardião de Blocos) (v3)

Versão v3 — refinada em conjunto com a “banca” (Jobs, Lamport, Vitalik, Knuth, Kay, Kleppmann, Pérez, Meyer) a partir de:
- Cap. 1 v3 — Visão da Truth-DB & Guardião de Blocos;
- Cap. 2 v3 — Gates, SLIs/SLOs e DoD da S10;
- Cap. 3 v4 — Arquitetura, Filemap e Contratos Estruturais;
- DNA/Leassons do projeto CE/Inspectah;
- feedback detalhado sobre a v2 deste capítulo (clareza de responsabilidades, semântica de status/exit code e padronização de logs/evidências).

Este capítulo é **100% operacional**: descreve como implementar e rodar os gates S10-G0…S10-G8, como gerar scorecards/evidências, como orquestrar tudo localmente e no CI, e como o Codex deve usar isso como runbook — **sem redefinir arquitetura (Cap. 3) nem critérios de julgamento (Cap. 2)**.

As melhorias da v3 foram focadas em:
- deixar explícita a relação 1:1 entre cada gate e seus artefatos, sem sobreposição de responsabilidade entre scripts;
- reforçar a semântica de `status` × exit code em TODOS os gates, inclusive G8;
- padronizar expectativas de logging (curto, determinístico, com paths fixos em `out/evidence/`);
- remover repetições e frases ambíguas da v2.

---

## 0) TL;DR — como rodar (e fazer rodar sempre) a Sprint 10

1. Para cada gate S10-G0…S10-G8 existe um script em `bin/`:
   - `bin/s10_g0_sanity.sh`
   - `bin/s10_g1_truthdb_model.sh`
   - `bin/s10_g2_state_machine.sh`
   - `bin/s10_g3_guardian_contract.sh`
   - `bin/s10_g4_mechanical_engine.sh`
   - `bin/s10_g5_e2e_domain_a.sh`
   - `bin/s10_g6_e2e_domain_b.sh`
   - `bin/s10_g7_audit_and_future.sh`
   - `bin/s10_g8_go_no_go.sh`

2. Todos os scripts:
   - são chamados sempre com `PYTHONPATH=.`;
   - usam `set -euo pipefail`;
   - produzem **um scorecard JSON** em `out/scorecards/` e evidências em `out/evidence/S10_G*/`.

3. O script `bin/s10_all_gates.sh` roda **G0→G8 em sequência**, falhando na primeira ocorrência de FAIL (especialmente em gates estruturais G1–G4).

4. O CI da S10 roda `PYTHONPATH=. bin/s10_all_gates.sh`.  
   - Se qualquer gate retorna FAIL, o pipeline falha.  
   - Se todos os gates respeitam o Cap. 2, o G8 marca `decision = "GO"`.

Este capítulo especifica **como** esses scripts funcionam, o formato dos scorecards/evidências, o runbook recomendado (local e CI) e as convenções de exit code — sem espaço para ambiguidade.

---

## 1) Convenções globais de execução

### 1.1 Ambiente e segurança

Todos os scripts de gate devem:

- iniciar com:
  - `#!/usr/bin/env bash`
  - `set -euo pipefail`
- assumir execução na raiz do repo Inspectah (validado por G0);
- nunca depender de rede externa (seguem a convenção `NET=0` do DNA);
- usar caminhos relativos (não hardcodear paths absolutos de máquina local);
- produzir logs **determinísticos e sucintos**, adequados para leitura em CI e reexecução.

Variáveis de ambiente mínimas:

- configuração de DB local de desenvolvimento/teste (ex.: `INSPECTAH_DB_URL` ou equivalente);
- qualquer flag necessária para isolar ambiente de teste da Truth-DB (ex.: schema de teste, banco separado).

### 1.2 Semântica de status × exit code

Para todos os scripts S10-G* (exceto G8, que decide GO/NO-GO):

- `status = "PASS"` no scorecard implica exit code `0`;
- `status = "WARN"` também implica exit code `0` (WARN é aceito apenas em gates/SLIs SOFT definidos no Cap. 2);
- `status = "FAIL"` implica exit code **≠ 0** (tipicamente `1`).

Regras adicionais por tipo de gate:

- G0, G2, G3, G4 **não admitem WARN** (qualquer problema é FAIL);
- G1, G5, G6, G7 podem admitir WARN apenas nos SLIs explicitamente marcados como SOFT no Cap. 2;
- G8 nunca marca WARN: apenas `"GO"` ou `"NO_GO"` na decisão final.

### 1.3 Formato padrão de scorecard

Todos os scorecards S10-G* seguem um formato comum (podem ter campos adicionais, mas nunca menos que isto):

```json
{
  "gate_id": "S10_GX",
  "name": "Nome legível do gate",
  "status": "PASS" | "WARN" | "FAIL",
  "slis": {
    "ratio_valid_actions_accepted": 1.0,
    "ratio_invalid_actions_rejected": 1.0,
    "audit_trace_completeness": 1.0,
    "future_ready_completeness": 1.0,
    "e2e_scenario_success_rate": 1.0
  },
  "checks": [
    {
      "id": "check-id",
      "description": "Descrição curta do que foi verificado",
      "status": "PASS" | "WARN" | "FAIL",
      "details": "Detalhes relevantes para troubleshooting"
    }
  ],
  "meta": {
    "ts": "2025-10-10T10:10:10Z",
    "git_commit": "<sha>",
    "branch": "q2-s10-truthdb-guardian"
  }
}
```

Nem todos os SLIs estarão presentes em todos os gates; o importante é **nunca inventar SLIs novos** e usar apenas os definidos no Cap. 2.

### 1.4 Estrutura de evidências

Para cada gate S10-GX, o script correspondente cria/usa:

- pasta `out/evidence/S10_GX/` com conteúdo voltado a:
  - logs brutos ou reduzidos do que foi rodado;
  - JSONs ou snapshots de entidades relevantes (blocos, fatos, exports, etc.);
  - relatórios auxiliares (por exemplo, resumo de transições cobertas em G2, lista de cenários executados em G5/G6).

G8 também escreve um resumo agregado em `out/evidence/S10_G8/summary.json`.

---

## 2) Execução por gate (S10-G0…S10-G8)

A seguir, o comportamento esperado de cada script de gate. Os nomes de testes, fixtures e funções são ilustrativos; o Cap. 3 define os módulos/contratos que eles exercitam, e o Cap. 2 define a régua de PASS/WARN/FAIL.

### 2.1 S10-G0 — Sanidade de ambiente/repo/DNA

**Script**: `bin/s10_g0_sanity.sh`

**Objetivo**  
Garantir que a Sprint 10 está sendo rodada no lugar certo, com os documentos corretos e a estrutura mínima de saída preparada.

**Passos recomendados (alto nível)**:

1. Verificar se o diretório atual é um repo git e se o remote aponta para o repo Inspectah correto.
2. Verificar se a branch atual é uma branch da S10 (convenção definida no DNA; ex.: `q2-s10-*`).
3. Verificar presença de:
   - `docs/sprint_10_cap_1_visao_truthdb_guardiao.md`;
   - `docs/sprint_10_cap_2_gates_truthdb_guardiao.md`;
   - `docs/sprint_10_cap_3_arquitetura_filemap_truthdb_guardiao.md`;
   - `docs/sprint_10_contrato_acoes_guardiao.md`;
   - `docs/sprint_10_cap_4_execucao_codex_guardiao_de_blocos.md` (este capítulo).
4. Garantir que `out/scorecards/` e `out/evidence/` existem (criá-los se necessário).

**Critério de status**  
WARN **não é permitido** em G0. Qualquer falha estrutural ou ausência de docs/pastas leva a `status = "FAIL"`.

**Saída**  
Scorecard `out/scorecards/S10_G0_sanity.json` + logs simples em `out/evidence/S10_G0/`.

---

### 2.2 S10-G1 — Modelo de dados da Truth-DB

**Script**: `bin/s10_g1_truthdb_model.sh`

**Objetivo**  
Validar que o modelo de dados da Truth-DB (Cap. 3) está íntegro, migrável e pronto para o futuro (S11/S12), conforme SLIs do Cap. 2.

**Passos recomendados**:

1. Aplicar/verificar a migration `migrations/versions/XXXX_s10_truthdb_core.py` em um DB de teste.
2. Rodar testes de integridade de modelo (ex.: `pytest tests/truthdb/test_models.py`).
3. Carregar fixtures ou gerar dados de teste para medir:
   - `future_ready_completeness` (SLI-4): proporção de entidades piloto com campos “futuros” preenchidos.
4. Sintetizar resultado em `S10_G1_truthdb_model.json`, preenchendo:
   - `status` conforme regras de PASS/WARN/FAIL do Cap. 2;
   - `slis.future_ready_completeness`;
   - lista de checks (migrations ok, constraints ok, etc.).

**Critério de status (encaixe com Cap. 2)**

- `PASS` se `future_ready_completeness >= 0.95` e sem falhas de integridade;
- `WARN` permitido apenas se `0.90 <= future_ready_completeness < 0.95`, com ADR/tickets registrados;
- abaixo disso ou com falhas graves de integridade, `FAIL`.

**Saída**  
Scorecard `out/scorecards/S10_G1_truthdb_model.json` + evidências em `out/evidence/S10_G1/` (por exemplo, dump parcial de entidades de teste).

---

### 2.3 S10-G2 — Máquina de estados de fatos

**Script**: `bin/s10_g2_state_machine.sh`

**Objetivo**  
Garantir que a máquina de estados de fatos (Cap. 3) está formalizada e que transições inválidas são rejeitadas nos testes.

**Passos recomendados**:

1. Rodar testes de máquina de estados (ex.: `pytest tests/truthdb/test_state_machine.py`).
2. A partir do conjunto de testes de transições inválidas, medir:
   - `ratio_invalid_actions_rejected` (SLI-2, focado em transições proibidas).
3. Gerar um relatório de cobertura de transições (quais estados de origem/destino foram exercitados).
4. Preencher `S10_G2_state_machine.json` com:
   - `slis.ratio_invalid_actions_rejected`;
   - lista de checks cobrindo estados, transições válidas e proibidas;
   - `status = "PASS"` se todas as transições inválidas foram rejeitadas;
   - `status = "FAIL"` se qualquer transição inválida foi aceita.

**Critério de status**  
G2 **não admite WARN**.

**Saída**  
Scorecard `out/scorecards/S10_G2_state_machine.json` + relatório de transições em `out/evidence/S10_G2/`.

---

### 2.4 S10-G3 — Contrato de ações do Guardião

**Script**: `bin/s10_g3_guardian_contract.sh`

**Objetivo**  
Testar o contrato de ações do Guardião (Cap. 3) contra schemas e exemplos de payloads válidos/ inválidos, medindo SLI-1 e SLI-2.

**Passos recomendados**:

1. Rodar testes de contrato (ex.: `pytest tests/truthdb/test_actions_contract.py`).
2. A partir do conjunto de payloads de teste, medir:
   - `ratio_valid_actions_accepted` (SLI-1);
   - `ratio_invalid_actions_rejected` (SLI-2).
3. Verificar consistência entre:
   - `docs/sprint_10_contrato_acoes_guardiao.md`;
   - `schema/s10_guardian_actions.schema.json`;
   - `inspectah/truthdb/actions_contract.py`.
4. Preencher `S10_G3_guardian_contract.json` com SLIs e checks de consistência.

**Critério de status**  
SLOs de G3 são HARD (Cap. 2): G3 **não admite WARN**.

**Saída**  
Scorecard `out/scorecards/S10_G3_guardian_contract.json` + amostras de payloads e resultados em `out/evidence/S10_G3/`.

---

### 2.5 S10-G4 — Engine mecânica de validação/aplicação

**Script**: `bin/s10_g4_mechanical_engine.sh`

**Objetivo**  
Validar a engine mecânica que aplica ações na Truth-DB, garantindo que nenhuma ação válida é rejeitada e nenhuma ação inválida é aceita.

**Passos recomendados**:

1. Rodar testes de engine (ex.: `pytest tests/truthdb/test_engine.py`).
2. A partir desses testes, medir SLI-1 e SLI-2 sob o prisma da engine:
   - ações válidas cobrem todos os tipos de ação do contrato;
   - ações inválidas incluem casos de payload incorreto, estados proibidos, entidades inexistentes.
3. Monitorar se há qualquer exceção não tratada ou corrupção de dados na Truth-DB de teste.
4. Preencher `S10_G4_mechanical_engine.json` com SLIs, checks e `status` coerente com Cap. 2.

**Critério de status**  
G4 **não admite WARN**: qualquer quebra de SLI HARD ou evidência de corrupção é FAIL.

**Saída**  
Scorecard `out/scorecards/S10_G4_mechanical_engine.json` + snapshots antes/depois de aplicar ações em `out/evidence/S10_G4/`.

---

### 2.6 S10-G5 — E2E — Domínio piloto A

**Script**: `bin/s10_g5_e2e_domain_a.sh`

**Objetivo**  
Provar que, no domínio A (ex.: obras públicas), o pipeline completo funciona: ingestão → blocos/fatos → Guardião → engine → Truth-DB → linha do tempo auditável.

**Passos recomendados**:

1. Ler a lista de cenários de domínio A em `docs/sprint_10_cenarios_e2e.md` ou em config.
2. Para cada cenário A:
   - rodar o pipeline (`inspectah/pipelines/s10_domain_a_obras.py`);
   - observar se o fluxo termina com sucesso (ou erro esperado);
   - registrar quais ações foram emitidas e aplicadas.
3. Ao final, medir:
   - `ratio_valid_actions_accepted` e `ratio_invalid_actions_rejected` (SLI-1 e SLI-2, se aplicável ao conjunto de cenários);
   - `audit_trace_completeness` (SLI-3) para fatos piloto de A;
   - `e2e_scenario_success_rate` (SLI-5) para o conjunto de cenários A.
4. Preencher `S10_G5_e2e_domain_A.json` conforme as regras de PASS/WARN/FAIL do Cap. 2.

**Critério de status**  
G5 pode admitir WARN apenas em SLIs SOFT (tipicamente SLI-5), nunca em SLI-3.

**Saída**  
Scorecard `out/scorecards/S10_G5_e2e_domain_A.json` + dumps de blocos/fatos/linhas do tempo em `out/evidence/S10_G5/`.

---

### 2.7 S10-G6 — E2E — Domínio piloto B

**Script**: `bin/s10_g6_e2e_domain_b.sh`

**Objetivo**  
Idem G5, mas exercitando outro domínio (ex.: preços), com caminhos diferentes na Truth-DB e na máquina de estados.

**Passos recomendados**:

1. Ler cenários de domínio B em `docs/sprint_10_cenarios_e2e.md` ou em config.
2. Rodar o pipeline `s10_domain_b_precos.py` para cada cenário, registrando sucesso/falha.
3. Medir SLI-1, SLI-2 (se aplicáveis), SLI-3 e SLI-5 para o domínio B.
4. Preencher `S10_G6_e2e_domain_B.json` com `status` aderente ao Cap. 2.

**Critério de status**  
Mesmas regras de G5: WARN apenas em SLI SOFT, nunca em SLI-3.

**Saída**  
Scorecard `out/scorecards/S10_G6_e2e_domain_B.json` + evidências de E2E B em `out/evidence/S10_G6/`.

---

### 2.8 S10-G7 — Auditabilidade & futuro (S11/S12)

**Script**: `bin/s10_g7_audit_and_future.sh`

**Objetivo**  
Garantir que os fatos piloto de A e B são plenamente auditáveis (linha do tempo completa) e que os exports estão prontos para S11/S12.

**Passos recomendados**:

1. Selecionar um conjunto de fatos piloto de A e B (amostra representativa).
2. Usar funções de `inspectah/truthdb/exports.py` para:
   - gerar exports de blocos/fatos/linhas do tempo;
   - salvar em `out/evidence/S10_G7/exports/`.
3. Verificar, para cada fato piloto:
   - se a linha do tempo é completa e coerente (SLI-3);
   - se todos os campos marcados como “necessários para S11/S12” estão presentes (SLI-4).
4. Preencher `S10_G7_audit_and_future.json` com:
   - `sli.audit_trace_completeness`;
   - `sli.future_ready_completeness`;
   - `status` conforme regras do Cap. 2 (SLI-3 HARD, SLI-4 SOFT).

**Critério de status**  
Qualquer buraco em SLI-3 é FAIL; SLI-4 pode gerar WARN apenas dentro das faixas permitidas pelo Cap. 2.

**Saída**  
Scorecard `out/scorecards/S10_G7_audit_and_future.json` + exports e relatórios em `out/evidence/S10_G7/`.

---

### 2.9 S10-G8 — GO/NO-GO da Sprint 10

**Script**: `bin/s10_g8_go_no_go.sh`

**Objetivo**  
Consolidar resultados de G0…G7 e emitir decisão GO/NO-GO para a S10, **sem recalcular SLIs** (usa apenas scorecards existentes).

**Passos recomendados**:

1. Ler todos os scorecards `out/scorecards/S10_G0_*.json … S10_G7_*.json`.
2. Verificar pré-condições de GO do Cap. 2:
   - G0 deve ser PASS;
   - G1–G4 devem ser PASS, sem WARN;
   - G5–G7 podem ter WARN apenas em SLIs SOFT, com ADRs registrados.
3. Construir `S10_G8_go_no_go.json` com:
   - `gate_id = "S10_G8"`;
   - `decision = "GO"` ou `"NO_GO"`;
   - um resumo dos gates (status e SLIs principais);
   - referência a `docs/sprint_10_summary.md`.
4. Escrever `out/evidence/S10_G8/summary.json` com:
   - lista de WARNs aceitos;
   - riscos residuais;
   - débitos técnicos priorizados.

**Critério de status / exit code**  
G8 não tem `status` próprio (usa a chave `decision`). O exit code do script é `0` se **todas** as condições de GO do Cap. 2 forem atendidas, e `≠ 0` caso contrário.

**Saída**  
Scorecard `out/scorecards/S10_G8_go_no_go.json` + resumo em `out/evidence/S10_G8/summary.json`.

---

## 3) Orquestrador da Sprint 10 — `s10_all_gates.sh`

**Script**: `bin/s10_all_gates.sh`

**Objetivo**  
Fornecer um único comando para rodar todos os gates na ordem correta, tanto localmente quanto no CI.

**Regras principais**:

1. Sempre usar `set -euo pipefail`.
2. Rodar, em ordem e com `PYTHONPATH=.`:
   - `bin/s10_g0_sanity.sh`
   - `bin/s10_g1_truthdb_model.sh`
   - `bin/s10_g2_state_machine.sh`
   - `bin/s10_g3_guardian_contract.sh`
   - `bin/s10_g4_mechanical_engine.sh`
   - `bin/s10_g5_e2e_domain_a.sh`
   - `bin/s10_g6_e2e_domain_b.sh`
   - `bin/s10_g7_audit_and_future.sh`
   - `bin/s10_g8_go_no_go.sh`
3. Abortar na primeira falha de script (exit code ≠ 0).
4. Opcionalmente aceitar flags simples (ex.: `--from G3`, `--to G6`) para rodar subconjuntos em desenvolvimento local (não obrigatório para CI).

No CI, o uso padrão será sem flags: rodar todos os gates em sequência.

---

## 4) Runbook operacional — desenvolvimento local

### 4.1 Ciclo de desenvolvimento por ondas

Recomendação para dev local (humano ou Codex):

1. Focar primeiro em G1/G2 (modelo + estados).  
   - Implementar/ajustar modelo, migrations, máquina de estados e testes.
2. Em seguida, G3/G4 (contrato + engine).  
   - Implementar contrato de ações, schemas, helpers e engine;
   - garantir que ações válidas/ inválidas se comportam como esperado.
3. Depois, G5/G6 (domínios A e B).  
   - Ligar pipelines de domínio à Truth-DB e ao Guardião/engine.
4. Só então G7 (auditabilidade/export).  
   - Montar exports e ferramentas de inspeção.
5. Por fim, G8 e `s10_all_gates.sh`.  
   - Consolidar tudo e garantir que GO/NO-GO funciona.

### 4.2 Comandos típicos em dev local

Durante o desenvolvimento:

- Rodar gates individualmente enquanto estabiliza:
  - `PYTHONPATH=. bin/s10_g1_truthdb_model.sh`
  - `PYTHONPATH=. bin/s10_g2_state_machine.sh`
  - `PYTHONPATH=. bin/s10_g3_guardian_contract.sh`
  - `PYTHONPATH=. bin/s10_g4_mechanical_engine.sh`
  - `PYTHONPATH=. bin/s10_g5_e2e_domain_a.sh`
  - `PYTHONPATH=. bin/s10_g6_e2e_domain_b.sh`
  - `PYTHONPATH=. bin/s10_g7_audit_and_future.sh`

Antes de abrir PR ou pedir review:

- `PYTHONPATH=. bin/s10_all_gates.sh`

Critério para considerar “dev local ok”:  
Todos os gates essenciais para o escopo mexido retornam PASS, sem FAIL; WARNs só onde o Cap. 2 permite.

---

## 5) Runbook operacional — integração com CI

### 5.1 Workflow S10 no CI

O workflow de CI da S10 (nome recomendado: `_s10-gates.yml`) deve:

1. Clonar o repo e preparar o ambiente (Python, DB de teste, etc.).
2. Rodar testes básicos/lint, se ainda não existirem em outro job.
3. Executar:
   - `PYTHONPATH=. bin/s10_all_gates.sh`
4. Publicar como artefatos de build:
   - a pasta `out/scorecards/`;
   - a pasta `out/evidence/` (ou um zip com subset relevante).

### 5.2 Regras de falha e aprovação

- Qualquer script de gate com exit code ≠ 0 derruba o workflow.
- Não deve existir lógica no CI que “disfarce” FAIL de gate como sucesso.
- Para merges importantes (ex.: fechamento da S10), recomenda-se exigir que:
  - o scorecard `S10_G8_go_no_go.json` exista;
  - `decision = "GO"`.

---

## 6) Papel deste capítulo para o Codex

Para o agente Codex (engenheiro), este Cap. 4 é o roteiro de implementação e automação da S10. Em particular:

- Diz **quais scripts** criar em `bin/` e o que cada um precisa fazer.
- Diz **como** esses scripts interagem com:
  - modelo, estados, contrato, engine, pipelines e exports definidos no Cap. 3;
  - gates, SLIs/SLOs e DoD do Cap. 2.
- Diz **quais scorecards** e **quais pastas de evidência** devem existir ao final.
- Diz **como integrar tudo no CI**, sem reabrir escopo nem critérios de qualidade.
- Define claramente a semântica de `status`, SLIs e exit codes, evitando zonas cinzentas.

O Codex não precisa redefinir arquitetura (Cap. 3) nem critérios de julgamento (Cap. 2); ele apenas implementa o que está aqui e garante que `bin/s10_all_gates.sh` se torne um comando único de confiança para rodar e provar a S10.

---

## 7) Relação com os demais capítulos da S10

- **Cap. 1 — Visão**  
  Define o *porquê* e o *o quê* da Truth-DB & Guardião de Blocos.

- **Cap. 2 — Gates, SLIs/SLOs e DoD**  
  Define *como* a S10 é julgada e quando é GO/NO-GO.

- **Cap. 3 — Arquitetura, Filemap e Contratos Estruturais**  
  Define *onde* vivem modelo, estados, ações, engine, pipelines e exports, e quais são os contratos estáveis.

- **Cap. 4 — Execução e Automação (este)**  
  Define *como* tudo isso roda na prática: scripts, scorecards, evidências, runbook local e CI.

Com os quatro capítulos juntos, a S10 deixa de ser apenas um plano e se torna uma sprint **executável, gated e auditável**, no nível de excelência esperado pelo DNA do projeto.

