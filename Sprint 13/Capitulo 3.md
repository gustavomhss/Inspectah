# Sprint 13 — Capítulo 3 — Arquitetura, Filemap & Contratos Técnicos (v2)

Versão revisada em conjunto com a equipe (Jobs, Knuth, Kay, Lamport, Vitalik, Kleppmann, Meyer, Pavel), alinhada ao DNA, ao blueprint S10–S16 e ao Capítulo 2 (gates S13_G0…S13_G8).

Este capítulo responde, de forma concreta:

- **Quais componentes** (scripts, configs, serviços, UI) dão suporte ao piloto multi-domínio da S13.
- **Onde** cada artefato vive no repositório (filemap).
- **Como** cada gate S13_G0…S13_G8 é implementado (entrypoints, helpers, scorecards, evidências).
- **Quais contratos técnicos** o Codex deve respeitar para manter tudo reprodutível, determinístico e alinhado ao escopo (sem blockchain, reputação ou Sistema de Blocos completo).

Se o Capítulo 2 é o contrato de *validação*, este Capítulo 3 é o contrato de *arquitetura e organização*.

---

## 1) Visão arquitetural da S13 em cima da S12

### 1.1 O que já existe (backbone S12)

A S13 assume que a S12 está em GO (ex.: tag `v0.3-s12`) e traz, entre outros:

- **Ingestão contínua enxuta**
  - `scripts/s12_sources_registry.py`, `scripts/s12_scheduler.py`, `scripts/s12_run_connector.py`.
  - Conectores piloto (`scripts/s12_connectors/*.py`) e normalizadores (`scripts/s12_normalizers/*.py`).

- **Debunker v0 e pipelines de evento → caso → timeline**
  - `scripts/s12_debunker_runner.py`, `scripts/s12_truthdb_adapter.py`.
  - `scripts/s12_case_service.py`, `scripts/s12_timeline_service.py`.

- **Explorer v0 + feedback v0**
  - Backend: `app/explorer/routes.py`, `app/feedback/routes.py`.
  - UI: `ui/explorer/*.tsx`, `ui/admin/FeedbackListPage.tsx`.

- **Gates e orquestração S12**
  - `bin/s12_g0_env_repo.sh` … `bin/s12_g8_decision.sh`, `bin/s12_gates_all.sh`.
  - Workflow `.github/workflows/_s12-gates.yml`.

A S13 **não altera esse backbone de forma radical**. Ela adiciona uma camada de **piloto multi-domínio** por cima, usando os mesmos serviços, padrões de evidência e estilo de gates.

### 1.2 Camadas lógicas da S13

A S13 se organiza em 4 camadas lógicas:

1. **Configuração de pilotos**  
   - Define quais casos piloto existem em cada domínio (obra pública, evento climático, projeto de lei, carreira política, influencer, atleta).

2. **Serviços de verificação S13**  
   - Helpers Python que:
     - carregam pilotos;
     - montam timelines;
     - chamam Debunker;
     - exercitam o Explorer;
     - verificam narrativas;
     - consolidam feedbacks;
     - calculam SLIs da S13.

3. **Gates S13 (scripts bin/)**  
   - Scripts de shell `bin/s13_g*_*.sh` que colam tudo, chamam os helpers e produzem scorecards + evidências, encaixando nos SLIs/SLOs do Cap. 2.

4. **Orquestração & CI**  
   - Orquestrador `bin/s13_gates_all.sh`.
   - Workflow `.github/workflows/_s13-gates.yml` rodando os gates da S13 em CI.

---

## 2) Filemap da Sprint 13

### 2.1 Documentação

Documentação principal da sprint:

- Pastas de sprint (fonte canônica humana):
  - `Sprint 13/Capitulo 1.md`
  - `Sprint 13/Capitulo 2.md`
  - `Sprint 13/Capitulo 3.md`
  - `Sprint 13/Capitulo 4.md`

- Espelhos opcionais integrados a `docs/` (se o time desejar):
  - `docs/sprint_13_cap_1_visao.md`
  - `docs/sprint_13_cap_2_gates.md`
  - `docs/sprint_13_cap_3_arquitetura.md`
  - `docs/sprint_13_cap_4_execucao_codex.md`

Roteiros de teste (para gates G4 e G6):

- `docs/sprint_13_cenarios_explorer.md`  
  - Lista de cenários de consulta por domínio (input, caso esperado, checagens).

- `docs/sprint_13_cenarios_feedback.md`  
  - Lista de cenários de feedback (tipo de problema, domínio/alvo, estado esperado no painel interno).

### 2.2 Configuração de pilotos multi-domínio

Arquivo canônico dos casos piloto:

- `config/s13_pilotos.yml`

Estrutura em alto nível (exemplo conceitual):

```yaml
dominios:
  - id: obra_publica
    nome: "Obra pública municipal"
    casos:
      - id: obra_escola_cidadeX_2024
        nome: "Reforma da escola municipal X"
        descricao_curta: "Reforma da escola X, anunciada em 2022, com execução questionada."
        periodo: "2022-2024"
        local: "Cidade X (Região Metropolitana do Rio)"
        backbone_refs:
          case_id: "..."    # opcional, se já existir
          tags: ["obra_publica", "educacao"]
  - id: evento_climatico
    nome: "Evento climático severo"
    casos:
      - id: chuva_forte_baixada_2024
        ...
  - id: projeto_lei
  - id: carreira_politica
  - id: influencer
  - id: atleta
```

Requisitos para `config/s13_pilotos.yml`:

- Deve listar **exatamente os 6 domínios da S13**.
- Cada domínio deve ter **≥ 1 caso piloto** (SLI-1 `domain_pilot_coverage`).
- IDs de casos piloto devem ser **estáveis** e únicos.
- Campos mínimos obrigatórios:
  - `id`, `dominio`, `nome`, `descricao_curta`, `periodo` (quando aplicável).

---

## 3) Helpers S13 em `scripts/`

Helpers Python da S13, separados da lógica da S12, mas reutilizando seus serviços.

### 3.1 Registro de pilotos

- `scripts/s13_pilots_registry.py`

Responsabilidades:

- Ler e validar `config/s13_pilotos.yml`.
- Expor funções como:
  - `list_domains()` → lista de domínios configurados.
  - `list_pilots()` → lista de todos os casos piloto.
  - `get_pilots_by_domain(domain_id)`.
  - `get_pilot(pilot_id)`.
- Verificar unicidade e integridade das chaves.

Este módulo é usado diretamente pelos gates S13_G1, S13_G2, S13_G3, S13_G4, S13_G5 e S13_G6.

### 3.2 Checks de timeline

- `scripts/s13_timeline_checks.py`

Responsabilidades:

- Receber um piloto e montar a timeline correspondente usando o backbone da S12:
  - via `scripts/s12_case_service.py` e `scripts/s12_timeline_service.py`.
- Validar invariantes de timeline (ordem temporal, estados válidos, ausência de estados impossíveis, etc.).
- Exportar snapshots por caso em `out/evidence/S13_G2/timelines/<pilot_id>.json`.
- Calcular `pilot_timeline_integrity_ratio` para G2.

### 3.3 Checks de Debunker

- `scripts/s13_debunker_checks.py`

Responsabilidades:

- Para cada caso piloto, passar seus eventos pelo Debunker v0 (S12):
  - usar `scripts/s12_debunker_runner.py` como base;  
  - coletar decisão + explicação mínima.
- Calcular `debunker_explanation_coverage` (SLI-3) e breakdown por domínio.
- Exportar decisões por domínio em `out/evidence/S13_G3/decisions_by_domain/<dominio>.json`.

### 3.4 Cenários do Explorer

- `scripts/s13_explorer_scenarios.py`

Responsabilidades:

- Ler `docs/sprint_13_cenarios_explorer.md` (ou um JSON derivado em `config/s13_explorer_scenarios.json`).
- Para cada cenário:
  - montar request de busca para o Explorer (pode ser via função interna ou HTTP local);
  - verificar se o caso retornado corresponde ao piloto esperado;
  - validar que a timeline está acessível na UI/backend.
- Calcular `explorer_success_rate` (SLI-4), com breakdown por domínio.
- Exportar amostras de requests/respostas em `out/evidence/S13_G4/queries/<cenario_id>.json`.

### 3.5 Registro e validação de narrativas

- `scripts/s13_narratives_registry.py`

Responsabilidades:

- Garantir que cada caso piloto possui narrativa mínima completa.
- Fontes possíveis:
  - campos adicionais em `config/s13_pilotos.yml` (ex.: `estado_atual_humano`, `resumo_1min`);
  - arquivos em `out/evidence/S13_G5/narrativas/<pilot_id>.md`.
- Validar presença de:
  - título;
  - descrição curta;
  - estado atual em linguagem humana;
  - parágrafo de resumo.
- Calcular `narrative_completeness_ratio` (SLI-6) para G5.

### 3.6 Feedback & backlog

- `scripts/s13_feedback_backlog.py`

Responsabilidades:

- Exercitar o fluxo de feedback em cima dos casos piloto, usando o backend já existente em S12 (`app/feedback/routes.py`).
- Verificar criação, listagem e atualização de feedback por domínio/caso.
- Calcular `feedback_delivery_ratio` (SLI-5) para G6.
- Exportar backlog consolidado em `out/evidence/S13_G6/backlog_s14_seed.json`, agrupando por domínio/caso e tipo de problema.

### 3.7 Snapshot de métricas S13

- `scripts/s13_metrics_snapshot.py`

Responsabilidades:

- Ler os scorecards S13_G0…S13_G6 em `out/scorecards/`.
- Calcular e consolidar SLI-1…SLI-6.
- Quando fizer sentido, comparar com baseline de S12.
- Exportar:
  - `out/evidence/S13_G7/metrics_snapshot.json` (valores numéricos, flags de regressão);
  - `out/evidence/S13_G7/risks_and_debts.md` (riscos/débitos para S14–S16).

---

## 4) Gates S13 — Arquitetura prática (bin/, scorecards, evidências)

Abaixo, a ligação gate a gate entre Cap. 2 e a arquitetura concreta.

### 4.1 S13_G0 — env_repo

**Script**

- `bin/s13_g0_env_repo.sh`

**Entrada**

- Repo atual (via git).
- `out/scorecards/S12_G8_decision.json` ou tag da S12.
- Arquivos `Sprint 13/Capitulo *.md`.

**Saídas**

- Scorecard:
  - `out/scorecards/S13_G0_env_repo.json`
  - Campos: `status`, `repo_ok`, `remote_ok`, `s12_go`, `s13_docs_present`.
- Evidência:
  - `out/evidence/S13_G0/env_snapshot.txt`.

### 4.2 S13_G1 — pilotos_multi_dominio

**Script**

- `bin/s13_g1_pilotos_multi_dominio.sh`

**Entrada**

- `config/s13_pilotos.yml`.

**Helpers**

- `scripts/s13_pilots_registry.py`.

**Saídas**

- Scorecard:
  - `out/scorecards/S13_G1_pilotos_multi_dominio.json`
  - Campos: `status`, `domain_pilot_coverage`, `domains` (mapa domínio → coberto?).
- Evidência:
  - `out/evidence/S13_G1/pilotos_resolved.json`.

### 4.3 S13_G2 — cases_timeline_multi

**Script**

- `bin/s13_g2_cases_timeline_multi.sh`

**Entradas**

- `config/s13_pilotos.yml`.
- Serviços de timeline S12.

**Helpers**

- `scripts/s13_pilots_registry.py`.
- `scripts/s13_timeline_checks.py`.

**Saídas**

- Scorecard:
  - `out/scorecards/S13_G2_cases_timeline_multi.json`
  - Campos: `status`, `pilot_timeline_integrity_ratio`, `violations`.
- Evidência:
  - `out/evidence/S13_G2/timelines/<pilot_id>.json`.

### 4.4 S13_G3 — debunker_multi_dominio

**Script**

- `bin/s13_g3_debunker_multi_dominio.sh`

**Entradas**

- `config/s13_pilotos.yml`.
- Debunker v0 (via scripts da S12).

**Helpers**

- `scripts/s13_pilots_registry.py`.
- `scripts/s13_debunker_checks.py`.

**Saídas**

- Scorecard:
  - `out/scorecards/S13_G3_debunker_multi_dominio.json`
  - Campos: `status`, `debunker_explanation_coverage`, breakdown por domínio.
- Evidência:
  - `out/evidence/S13_G3/decisions_by_domain/<dominio>.json`.

### 4.5 S13_G4 — explorer_multi_dominio

**Script**

- `bin/s13_g4_explorer_multi_dominio.sh`

**Entradas**

- `docs/sprint_13_cenarios_explorer.md` ou `config/s13_explorer_scenarios.json`.
- Backend do Explorer v0.

**Helpers**

- `scripts/s13_explorer_scenarios.py`.

**Saídas**

- Scorecard:
  - `out/scorecards/S13_G4_explorer_multi_dominio.json`
  - Campos: `status`, `explorer_success_rate`, breakdown por domínio.
- Evidência:
  - `out/evidence/S13_G4/queries/<cenario_id>.json`.

### 4.6 S13_G5 — narrativas_multi_dominio

**Script**

- `bin/s13_g5_narrativas_multi_dominio.sh`

**Entradas**

- `config/s13_pilotos.yml`.
- Arquivos de narrativa em `out/evidence/S13_G5/narrativas/*.md` (ou fonte equivalente definida no Cap. 4).

**Helpers**

- `scripts/s13_narratives_registry.py`.

**Saídas**

- Scorecard:
  - `out/scorecards/S13_G5_narrativas_multi_dominio.json`
  - Campos: `status`, `narrative_completeness_ratio`, lista de casos incompletos (se houver).
- Evidência:
  - `out/evidence/S13_G5/narrativas/<pilot_id>.md`.

### 4.7 S13_G6 — feedback_multi_dominio

**Script**

- `bin/s13_g6_feedback_multi_dominio.sh`

**Entradas**

- Backend/painel de feedback S12.
- `config/s13_pilotos.yml`.
- `docs/sprint_13_cenarios_feedback.md`.

**Helpers**

- `scripts/s13_feedback_backlog.py`.

**Saídas**

- Scorecard:
  - `out/scorecards/S13_G6_feedback_multi_dominio.json`
  - Campos: `status`, `feedback_delivery_ratio`, breakdown por domínio.
- Evidência:
  - `out/evidence/S13_G6/backlog_s14_seed.json`.

### 4.8 S13_G7 — observabilidade

**Script**

- `bin/s13_g7_observabilidade.sh`

**Entradas**

- Scorecards `out/scorecards/S13_G0_*.json`…`S13_G6_*.json`.
- Opcionalmente scorecards S12 (para comparação).

**Helpers**

- `scripts/s13_metrics_snapshot.py`.

**Saídas**

- Scorecard:
  - `out/scorecards/S13_G7_observabilidade.json`
  - Campos: `status`, SLI-1…SLI-6 consolidados, flags de regressão.
- Evidência:
  - `out/evidence/S13_G7/metrics_snapshot.json`.
  - `out/evidence/S13_G7/risks_and_debts.md`.

### 4.9 S13_G8 — decision

**Script**

- `bin/s13_g8_decision.sh`

**Entradas**

- Scorecards `out/scorecards/S13_G0_*.json`…`S13_G7_*.json`.

**Helpers**

- Pode ser um pequeno script Python dedicado (ex.: `scripts/s13_decision.py`) ou lógica inline no shell, desde que:
  - respeite a classificação de gates HARD vs SOFT do Cap. 2;
  - gere `decision = "GO"` ou `"NO_GO"` com base nas regras definidas.

**Saídas**

- Scorecard:
  - `out/scorecards/S13_G8_decision.json`  
    - Campos: `gate`, `status`, `decision`, resumo de gates/SLIs.
- Evidência:
  - `out/evidence/S13_G8/summary.md`.

---

## 5) Orquestração e CI

### 5.1 Orquestrador local da S13

- `bin/s13_gates_all.sh`

Responsabilidades:

- Rodar, em ordem, os gates S13_G0…S13_G7.
- Parar no primeiro FAIL (propagando exit code ≠ 0).
- Imprimir logs claros (`[S13] -> s13_gX_*.sh`).
- Opcionalmente, chamar `bin/s13_g8_decision.sh` no final (detalhe a ser fixado no Cap. 4).

### 5.2 Workflow de CI

- `.github/workflows/_s13-gates.yml`

Papel:

- Garantir que o que funciona na máquina local também funciona em CI.
- Rodar em pushes/PRs para `main` e para a branch da sprint (ex.: `s13_piloto_multi_dominio_v0`).

Passos típicos (detalhados no Cap. 4):

- checkout;
- setup de Python/Node conforme DNA;
- instalação de dependências;
- execução de `bin/s13_gates_all.sh` (e opcionalmente `bin/s13_g8_decision.sh`);
- upload de `out/scorecards/` e `out/evidence/` como artefatos.

---

## 6) Princípios e restrições arquiteturais da S13

1. **Escopo travado: sem blockchain, reputação avançada ou Sistema de Blocos completo**  
   - Tudo o que envolver blockchain, contestação on-chain, reputação pesada ou Sistema de Blocos completo fica para Fase 2 (S11–S16 originais replanejados);
   - A S13 foca em **piloto multi-domínio** em cima do backbone S12.

2. **Determinismo e reprodutibilidade**  
   - Helpers S13 não devem depender de chamadas de rede externas imprevisíveis;
   - scorecards e evidências devem ser reproduzíveis a partir do mesmo código/fixtures;
   - nomes de arquivos em `out/scorecards/` e `out/evidence/` devem seguir o padrão S12/S13.

3. **Separação de preocupações (config → lógica → execução → resultado)**  
   - `config/` para arquivos de configuração (pilotos, cenários);
   - `scripts/` para lógica de negócio/reuso;
   - `bin/` para orquestração e CLI;
   - `out/` para resultados (scorecards/evidências).

4. **Compatibilidade com S12 e futuro encaixe na Fase 2**  
   - Nenhum componente da S13 deve quebrar gates ou fluxos existentes da S12;
   - O desenho de pilotos/casos/timelines/narrativas deve ser compatível com a futura camada de Sistema de Blocos (Fase 2), mas sem antecipar sua implementação.

5. **Legibilidade e auditabilidade primeiro**  
   - Sempre que houver dúvida entre uma solução "genial" e uma solução simples/legível, escolher a segunda;
   - scorecards e evidências devem ser fáceis de inspecionar por humanos (nomes claros, JSON legível, markdowns curtos e diretos).

---

## 7) Encadeamento com o Capítulo 4

Com este Capítulo 3, a Sprint 13 passa a ter um **mapa claro de artefatos e componentes**:

- sabemos quais arquivos devem existir em `config/`, `scripts/`, `bin/`, `docs/`, `out/` e `.github/workflows/`;
- sabemos como cada gate S13_G0…S13_G8 é suportado por scripts e helpers;
- sabemos como a S13 se apoia na S12 sem violar o escopo replanejado (sem blockchain/Sistema de Blocos agora).

O próximo passo é o **Capítulo 4**, que transforma essa arquitetura em um plano operacional para o Codex:

- comandos exatos para criar/ajustar arquivos;
- ordem de implementação (waves);
- como rodar localmente e em CI;
- como o Codex deve se comportar ao longo da sprint (branch, commits, validações contínuas).

