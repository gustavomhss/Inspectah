# Sprint 14 – Capítulo 3 (v2)
Arquitetura, Filemap e Amarração com os Gates

---

## 0) TL;DR

A Sprint 14 é uma sprint de **sanidade e endurecimento** do Inspectah em cima do que já existe em produção interna:

- Backbone S12 (ingestão contínua + Debunker v0 + casos/timelines + Explorer/feedback v0).
- Piloto multi-domínio S13 (seis domínios: obra pública, evento climático, projeto de lei, carreira política, influencer e atleta) rodando sobre o backbone S12.

O objetivo deste capítulo é:

- Descrever a **arquitetura operacional** que vale após a S14.
- Definir o **filemap** da sprint (docs, configs, scripts, gates, scorecards, evidências).
- Amarrar **cada gate S14_G0…S14_G8** a arquivos e artefatos concretos.
- Reafirmar o que é **núcleo de verdade v0** (truth kernel) e o que fica **explicitamente fora do escopo** (Fase 2: Sistema de Blocos completo, blockchain automática, reputação pesada, comunidade avançada).

Nada na S14 introduz blockchain automática, reputação formal, contestação pública complexa ou Sistema de Blocos completo. A S14 faz o contrário: **limpa, organiza, documenta e protege** o que já existe para que a Fase 2 tenha um chão estável.

---

## 1) Contexto e escopo da arquitetura S14

### 1.1 De onde partimos (estado pós-S13)

Antes da S14, o Inspectah já tem:

- **S12 – ingestão contínua enxuta:**
  - Registry de fontes-piloto, scheduler, conectores e pipeline de ingestão.
  - Debunker v0 obrigatório em todos os eventos.
  - Casos e timelines auditáveis (case_service, timeline_service, truthdb_adapter).
  - Explorer v0 e painel de feedback funcionando sobre esses casos.
  - Gates S12_G0…S12_G8 verdes, com ORR e docs atualizados.

- **S13 – piloto multi-domínio:**
  - Seis domínios configurados em `config/s13_pilotos.yml` (obra pública, evento climático, projeto de lei, carreira política, influencer, atleta).
  - Timelines e Debunker exercitados nesses seis domínios.
  - Explorer/feedback cobrindo cenários multi-domínio documentados em docs específicos.
  - Gates S13_G0…S13_G8 verdes, com ORR e docs atualizados.

A Sprint 14 não “reinventa” nada disso: ela assume S12 e S13 como **baseline obrigatório**. Se S12/S13 estiverem quebradas, a S14 **não pode** ser considerada concluída.

### 1.2 O que a S14 faz, do ponto de vista de arquitetura

A S14:

- Consolida o **truth kernel v0** (núcleo de verdade atual, sem Sistema de Blocos completo).
- Consolida o **Debunker v0** como serviço lógico central (com regras explícitas e estáveis).
- Garante que o Explorer/feedback use apenas o caminho “oficial” de dados (timelines e casos consolidados).
- Limpa e organiza artefatos antigos, garantindo que S12/S13 continuam válidos após migrações leves.
- Cria uma camada de **observabilidade e decisão** própria (scorecards S14_G*, snapshot de métricas, ORR S14).
- Explicita em docs e configs o que vai para a **Fase 2**, sem misturar no código atual.

### 1.3 O que a S14 NÃO faz (resumo de não-escopo)

Nesta sprint **não** implementamos:

- Sistema de Blocos completo (Blocks, SubBlocks, Facts, Versions, Disputes, reputação formal).
- Contestação pública/complexa, fluxos on-chain para disputa, bonds, staking etc.
- Blockchain automática (Merkle, âncoras periódicas, commits on-chain). No máximo, referências para futuro.
- Comitês avançados (V1/V2/V3) com múltiplos modelos e papéis sociais complexos.
- Model checking/TLA+ pesado para o Sistema de Blocos.

Tudo isso é reservado explicitamente para a **Fase 2** e rastreado em backlog próprio.

---

## 2) Arquitetura lógica após a Sprint 14

### 2.1 Truth kernel v0 – definição

Chamamos de **truth kernel v0** o conjunto de peças que, juntas, representam “o estado de verdade” do Inspectah hoje:

- Os serviços de casos/timelines/truth-db:
  - `scripts/s12_case_service.py`
  - `scripts/s12_timeline_service.py`
  - `scripts/s12_truthdb_adapter.py`

- Os snapshots persistidos pelos gates da S12 e S13:
  - `out/evidence/S12_G2/` – ingest pipeline (casos, timelines, normalizados).
  - `out/evidence/S12_G4/` – invariantes de casos/timelines.
  - `out/evidence/S13_G2/` – timelines multi-domínio.
  - `out/evidence/S13_G4/` – snapshots para Explorer multi-domínio.

- As convenções de domínio e casos:
  - `config/s13_pilotos.yml` (domínios, case_keys, estados, narrativa_resumo etc.).

A S14 **não troca essa base**. Ela:

- Documenta esse kernel em um doc dedicado.
- Adiciona uma config leve para centralizar parâmetros (por ex., names de domínios, estados possíveis etc.).
- Cria scripts de verificação para garantir invariantes mínimas e evitar regressões.

### 2.2 Debunker v0 – serviço lógico único

O Debunker v0 já está em uso nas S12/S13 e é composto hoje por:

- `scripts/s12_debunker_runner.py` – núcleo de decisão/explicação.
- `scripts/s13_debunker_checks.py` – checks multi-domínio e evidências.

Na S14, a arquitetura trata o Debunker v0 como um **serviço lógico único**, com as seguintes propriedades:

- Todas as chamadas “oficiais” de validação de eventos passam por um conjunto fixo de helpers.
- As regras por domínio são externalizadas em um arquivo de config (thresholds, heurísticas, flags).
- A consistência do Debunker é medida por um gate específico da S14 (cobertura de explicações, estabilidade e ausência de inconsistências graves entre domínios).

### 2.3 Explorer & feedback – clientes do truth kernel

Explorer e painel de feedback, após S12/S13, já conversam com o truth kernel v0. A S14 reforça que:

- O Explorer deve consumir **apenas** as projeções/snapshots oficiais (cases_snapshot, timelines_snapshot, decisions_by_domain etc.).
- O painel de feedback continua operando com o serviço atual de feedback, mas a S14 garante que:
  - os fluxos essenciais (create/list/update) seguem funcionando;
  - as evidências desses fluxos são salvas de forma padronizada;
  - qualquer mudança em casos/timelines/truth kernel não quebra feedback.

Um gate da S14 é responsável por exercitar **contratos de Explorer/feedback** sobre o estado pós-S14.

### 2.4 Ingestão & fontes – sem novos domínios pesados

A camada de ingestão vem de S12 (registry, scheduler, conectores, pipeline). A S14 não adiciona novos domínios pesados. O seu papel aqui é:

- Garantir que o que a S14 faz **não** torna S12/S13 instáveis.
- Limpar ou reorganizar eventualmente artefatos antigos (fixtures, diretórios de evidência) que atrapalhem a sanidade.
- Documentar claramente quais fontes e snapshots são considerados “válidos” para o truth kernel v0.

Essa limpeza/migração leve é coberta por um gate específico da S14.

### 2.5 Observabilidade e decisão S14

Por fim, a arquitetura da S14 inclui:

- Um script de snapshot de métricas da S14, consumindo scorecards S14_G0…S14_G6.
- Um conjunto de scorecards S14_G* armazenados em out/scorecards/, com SLIs claros.
- Um gate de decisão S14_G8, que mede GO/NO_GO apenas com base nesses scorecards.
- Uma ORR da S14 documentando o estado final do projeto após esta sprint.

---

## 3) Filemap da Sprint 14

### 3.1 Documentos da sprint (humanos)

Pasta da sprint:

- `Sprint 14/Capitulo 1.md` – visão, escopo e objetivos da S14.
- `Sprint 14/Capitulo 2.md` – definição de S14_G0…S14_G8 (gates, SLIs, SLOs, regras de GO/NO_GO).
- `Sprint 14/Capitulo 3.md` – este capítulo (arquitetura e filemap).
- `Sprint 14/Capitulo 4.md` – plano operacional/Codex (runbook detalhado da sprint).

Esses arquivos são **fonte de verdade narrativa** para humanos e para o Codex.

### 3.2 Documentos técnicos oficiais da S14

Dentro de `docs/`:

- `docs/sprint_14_truth_kernel.md`
  - Descreve o truth kernel v0 (serviços, snapshots, invariantes) em linguagem humana.
- `docs/sprint_14_debunker_v0.md`
  - Lista as regras principais do Debunker v0 por domínio, vinculando-as a helpers de código.
- `docs/sprint_14_backlog_fase2.md`
  - Lista tudo que foi empurrado explicitamente para a Fase 2 (Sistema de Blocos completo, blockchain, reputação, comunidade, comitês, TLA+ etc.), apontando para os blueprints já existentes.
- `docs/sprint_14_orr_summary.md`
  - ORR da S14 (objetivo, entregáveis, tabela S14_G0…S14_G8, instruções de execução, riscos e próximos passos).

Documentos de sprints anteriores (ORRs S12/S13, blueprint do Sistema de Blocos etc.) continuam apenas como leitura.

### 3.3 Configuração

Novas configs sob `config/`:

- `config/s14_truth_kernel.yml`
  - Mapeia domínios → tipos de caso;
  - Define estados relevantes de caso/timeline e flags sobre quais snapshots são oficiais para a S14.

- `config/s14_debunker_rules.yml`
  - Concentra thresholds e heurísticas do Debunker v0 por domínio (ex.: o que marca suspeito, quando exigir explicação mais detalhada, etc.).

Esses arquivos existem para **não espalhar constantes hard-coded** pela base.

### 3.4 Scripts da S14

Novos scripts em `scripts/`:

- `scripts/s14_truth_kernel_checks.py`
  - Lê snapshots de S12/S13 e, se necessário, a base local;
  - reconstrói a visão de casos/timelines por domínio;
  - verifica invariantes definidas em `docs/sprint_14_truth_kernel.md` e em `config/s14_truth_kernel.yml`;
  - gera relatórios JSON em `out/evidence/S14_G1/` (por ex., `kernel_integrity_report.json`).

- `scripts/s14_debunker_consistency.py`
  - Usa `config/s14_debunker_rules.yml` e os helpers do Debunker v0 para gerar eventos fixos de teste por domínio;
  - mede cobertura de explicação, consistência e estabilidade ao longo de múltiplas execuções;
  - escreve relatórios em `out/evidence/S14_G2/` (por ex., `debunker_consistency_report.json`).

- `scripts/s14_explorer_contracts.py`
  - Exercita as rotas principais de Explorer/feedback em cima do truth kernel v0 pós-S14;
  - guarda requests/responses e checks em `out/evidence/S14_G3/explorer_contracts.json` (mais arquivos auxiliares, se necessário).

- `scripts/s14_migrations_and_cleanup.py`
  - Aplica migrações e limpezas leves (remover artefatos mortos, reorganizar diretórios, normalizar nomes de domínios);
  - é idempotente e protegido por evidência em `out/evidence/S14_G4/migrations_report.json`.

- `scripts/s14_metrics_snapshot.py`
  - Lê scorecards `S14_G0…S14_G6` e extrai SLIs;
  - calcula um `global_health` da S14;
  - escreve `out/evidence/S14_G7/metrics_snapshot.json` e `out/evidence/S14_G7/risks_and_debts.md`.

- `scripts/s14_decision.py`
  - Lê todos os scorecards S14_G0…S14_G7;
  - aplica as regras do Capítulo 2 para GO/NO_GO;
  - gera `out/scorecards/S14_G8_decision.json` e `out/evidence/S14_G8/summary.md`.

### 3.5 Gates da Sprint 14

Entrypoints em `bin/`:

- `bin/s14_g0_env_repo.sh`
  - Verifica repo/branch/origin corretos;
  - garante que os Capítulos da S14 existem;
  - checa se S12_G8 e S13_G8 estão em GO;
  - grava `out/evidence/S14_G0/env_snapshot.json` e `out/scorecards/S14_G0_env_repo.json`.

- `bin/s14_g1_truth_kernel.sh`
  - Roda `python -m scripts.s14_truth_kernel_checks`;
  - gera evidências em `out/evidence/S14_G1/` e `out/scorecards/S14_G1_truth_kernel.json`.

- `bin/s14_g2_debunker_consistency.sh`
  - Roda `python -m scripts.s14_debunker_consistency`;
  - gera evidências em `out/evidence/S14_G2/` e `out/scorecards/S14_G2_debunker_consistency.json`.

- `bin/s14_g3_explorer_contracts.sh`
  - Roda `python -m scripts.s14_explorer_contracts`;
  - gera evidências em `out/evidence/S14_G3/` e `out/scorecards/S14_G3_explorer_contracts.json`.

- `bin/s14_g4_migrations_and_cleanup.sh`
  - Executa `python -m scripts.s14_migrations_and_cleanup`;
  - produz `out/evidence/S14_G4/migrations_report.json` e `out/scorecards/S14_G4_migrations_and_cleanup.json`.

- `bin/s14_g5_regression_smoke.sh`
  - Roda um subconjunto de testes/smokes de regressão (reusando testes existentes);
  - escreve `out/evidence/S14_G5/regression_smoke_report.json` e `out/scorecards/S14_G5_regression_smoke.json`.

- `bin/s14_g6_docs_dna_alignment.sh`
  - Executa checks de alinhamento entre Capítulos S14, ORRs, blueprint do Sistema de Blocos e backlog de Fase 2;
  - gera `out/evidence/S14_G6/docs_alignment_report.md` e `out/scorecards/S14_G6_docs_dna_alignment.json`.

- `bin/s14_g7_observabilidade.sh`
  - Roda `python -m scripts.s14_metrics_snapshot`;
  - escreve `out/evidence/S14_G7/metrics_snapshot.json`, `out/evidence/S14_G7/risks_and_debts.md` e `out/scorecards/S14_G7_observabilidade.json`.

- `bin/s14_g8_decision.sh`
  - Roda `python -m scripts.s14_decision`;
  - valida a presença de `S14_G8_decision.json` e de `summary.md`;
  - falha se a decisão for `NO_GO` ou se algum gate obrigatório estiver em status inaceitável.

- `bin/s14_gates_all.sh`
  - Orquestrador da S14;
  - roda G0…G7 em ordem, parando no primeiro erro;
  - usado localmente e no CI.

### 3.6 CI / GitHub Actions

Workflow dedicado da S14 em `.github/workflows/_s14-gates.yml`:

- Faz checkout do repo;
- instala dependências;
- executa `bash bin/s14_gates_all.sh`;
- publica `out/scorecards/` e `out/evidence/S14_*` como artefatos;
- roda em pushes/PRs para `main` e para a branch da sprint (por exemplo, `s14_hardening_truth_kernel_v0`).

O script `bin/ci_local.sh` é atualizado para incluir `bin/s14_gates_all.sh` na sequência local.

### 3.7 Scorecards e evidências

Padrão de scorecards S14 em `out/scorecards/`:

- `S14_G0_env_repo.json`
- `S14_G1_truth_kernel.json`
- `S14_G2_debunker_consistency.json`
- `S14_G3_explorer_contracts.json`
- `S14_G4_migrations_and_cleanup.json`
- `S14_G5_regression_smoke.json`
- `S14_G6_docs_dna_alignment.json`
- `S14_G7_observabilidade.json`
- `S14_G8_decision.json`

Padrão de evidências S14 em `out/evidence/`:

- `S14_G0/` – env_snapshot.
- `S14_G1/` – snapshots do kernel e `kernel_integrity_report.json`.
- `S14_G2/` – `debunker_consistency_report.json` e exemplos de decisões.
- `S14_G3/` – `explorer_contracts.json` e logs de requests/responses.
- `S14_G4/` – `migrations_report.json` e, se necessário, estados "before/after".
- `S14_G5/` – `regression_smoke_report.json`.
- `S14_G6/` – `docs_alignment_report.md`.
- `S14_G7/` – `metrics_snapshot.json` e `risks_and_debts.md`.
- `S14_G8/` – `summary.md` com a decisão e links para os principais scorecards.

---

## 4) Gate → Arquitetura → Artefatos (visão cruzada)

Em forma condensada, a relação é:

- **S14_G0 – Ambiente/Repo**
  - Arquitetura: garante que estamos no repo/branch certo e que S12/S13 estão em GO.
  - Entrypoint: `bin/s14_g0_env_repo.sh`.
  - Artefatos: env_snapshot + scorecard S14_G0.

- **S14_G1 – Truth kernel v0**
  - Arquitetura: invariantes do kernel (casos/timelines/snapshots) pós-S12/S13.
  - Entrypoint: `bin/s14_g1_truth_kernel.sh` → `scripts/s14_truth_kernel_checks.py`.
  - Artefatos: snapshots e relatórios em S14_G1 + scorecard S14_G1.

- **S14_G2 – Debunker consistency**
  - Arquitetura: Debunker v0 estável, explicável e coerente entre domínios.
  - Entrypoint: `bin/s14_g2_debunker_consistency.sh` → `scripts/s14_debunker_consistency.py`.
  - Artefatos: relatórios em S14_G2 + scorecard S14_G2.

- **S14_G3 – Explorer contracts**
  - Arquitetura: Explorer/feedback como clientes corretos do truth kernel v0.
  - Entrypoint: `bin/s14_g3_explorer_contracts.sh` → `scripts/s14_explorer_contracts.py`.
  - Artefatos: traces de chamadas em S14_G3 + scorecard S14_G3.

- **S14_G4 – Migrations & cleanup**
  - Arquitetura: limpeza/migrações leves que não quebram S12/S13.
  - Entrypoint: `bin/s14_g4_migrations_and_cleanup.sh` → `scripts/s14_migrations_and_cleanup.py`.
  - Artefatos: migrations_report em S14_G4 + scorecard S14_G4.

- **S14_G5 – Regression smoke**
  - Arquitetura: sanity check de regressão em cima do que já era garantido antes.
  - Entrypoint: `bin/s14_g5_regression_smoke.sh` (reutiliza testes existentes).
  - Artefatos: regression_smoke_report em S14_G5 + scorecard S14_G5.

- **S14_G6 – Docs/DNA alignment**
  - Arquitetura: história oficial (Capítulos, ORRs, DNA) coerente com o estado de código e com a separação Fase 1/Fase 2.
  - Entrypoint: `bin/s14_g6_docs_dna_alignment.sh`.
  - Artefatos: docs_alignment_report em S14_G6 + scorecard S14_G6.

- **S14_G7 – Observabilidade**
  - Arquitetura: visão condensada da saúde da S14 via SLIs/scorecards.
  - Entrypoint: `bin/s14_g7_observabilidade.sh` → `scripts/s14_metrics_snapshot.py`.
  - Artefatos: metrics_snapshot + risks_and_debts em S14_G7 + scorecard S14_G7.

- **S14_G8 – Decisão**
  - Arquitetura: decisão GO/NO_GO baseada exclusivamente nos scorecards da S14.
  - Entrypoint: `bin/s14_g8_decision.sh` → `scripts/s14_decision.py`.
  - Artefatos: S14_G8_decision.json + summary.md.

---

## 5) Fase 2 – limites reforçados

Para evitar qualquer ambiguidade, este capítulo reforça que tudo a seguir permanece em **Fase 2**, fora do escopo da S14:

- Implementação completa do Sistema de Blocos (incluindo todas as hierarquias de bloco/sub-bloco/fato/versões/disputas e propagação bottom-up).
- Qualquer forma de reputação formal de fontes/autores/validadores (scores, decays, gamificação, ranking público etc.).
- Qualquer integração automática com blockchain (Merkle trees, batching de commits, múltiplas chains, provas on-chain etc.).
- Mecânicas de contestação pública complexa (bonds, staking, múltiplas instâncias de arbitragem, comitês V1/V2/V3, modos “tribunal” etc.).
- Pipelines de model checking/TLA+ focados no Sistema de Blocos.

Todos esses itens são listados e referenciados em `docs/sprint_14_backlog_fase2.md` e nos docs de blueprint já existentes, para que o time consiga retomá-los na Fase 2 sem perder contexto.

---

## 6) Notas operacionais para o Capítulo 4 / Codex

O Capítulo 4 vai traduzir tudo isso em passos concretos (waves, comandos, checklists). Este Capítulo 3 assume:

- Branch de trabalho algo como `s14_hardening_truth_kernel_v0`, criada a partir de `main` em `v0.4-s13`.
- S12 e S13 em GO antes e depois de qualquer alteração da S14 (rodando `bin/s12_gates_all.sh` + `bin/s12_g8_decision.sh` e `bin/s13_gates_all.sh` + `bin/s13_g8_decision.sh`).
- Todos os scripts da S14 idempotentes, gerando evidência clara a cada execução.
- Nenhum doc de blueprint de Sistema de Blocos é modificado – apenas referenciado e usado como base conceitual.

Com isso, a Sprint 14 passa a ter uma arquitetura e um filemap **claros, auditáveis e alinhados** aos gates do Capítulo 2, preparando o Inspectah para a Fase 2 sem estourar o escopo agora.

