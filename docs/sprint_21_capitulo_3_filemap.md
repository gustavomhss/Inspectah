# Inspectah — Sprint 21 — Capítulo 3 (v2)
## Arquitetura, Filemap e Contratos de Implementação do Console de Fontes

### 1. Papel deste capítulo na Sprint 21

O Capítulo 1 explicou **por que** a Sprint 21 existe: o Console de Fontes como primeiro bloco sólido da onda 21–25. O Capítulo 2 definiu **como** vamos verificar se a sprint cumpriu o que prometeu (gates S21_G0…S21_G8, scorecards, evidências).

Este Capítulo 3 responde à pergunta: **“onde cada peça vive no repositório e como elas se encaixam em uma arquitetura coerente?”**

Ele é o mapa de implementação do Squad 1 e o mapa mental do Codex:
- Mostra a arquitetura lógica do módulo de fontes na Fase 1.
- Define a organização em pastas/arquivos (filemap) para docs, backend, UI, migrations, testes e scripts de gates.
- Amarra cada parte aos gates do Capítulo 2 e às dependências com S22–S25.

Se este capítulo estiver bem feito, qualquer pessoa técnica consegue, apenas com ele + Capítulos 1 e 2, implementar a Sprint 21 com alta fidelidade e sem “arquivos órfãos” ou decisões implícitas.

---

### 2. Visão arquitetural do módulo de fontes na Fase 1

Na Fase 1, o módulo de fontes é um **módulo de domínio enxuto, porém completo**, com cinco camadas principais e fronteiras claras:

1. **Domínio e modelo de dados (`app/sources/models.py`)**  
   - Entidades centrais: `Source`, `SourceType`, `SourceCategory`, `SourceStateHistory`, `SourceHealthCheck` (nomes exemplificativos, ajustáveis conforme padrão do projeto).  
   - Essas entidades são o reflexo direto de:
     - docs/sprint_21_ontologia_fontes.md (tipos, atributos semânticos);
     - docs/sprint_21_modelo_dados_fontes.md (modelo relacional/documental);
     - docs/sprint_21_ciclo_vida_fontes.md (máquina de estados).

2. **Serviços de domínio (`app/sources/service.py`)**  
   - Implementam operações de alto nível sobre fontes:
     - criar/editar fonte, validando ontologia e tipo;
     - aplicar transições de estado válidas;
     - registrar health-checks;
     - consultar fontes com filtros e paginação.
   - Aqui ficam as regras de negócio; detalhes de persistência são delegados à camada de repositórios/modelos.

3. **Validação de configuração e tipos (`app/sources/validators.py` + `schemas.py`)**  
   - Schemas Pydantic (ou equivalentes) para `SourceCreate`, `SourceUpdate`, `SourceRead` e configs específicas por tipo (RSS, API HTTP, dataset estático, etc.).  
   - Validações que impedem states inválidos, configs incompletas e combinações proibidas.

4. **API de admin (`app/sources/routes_admin.py`)**  
   - Endpoints REST para CRUD de fontes, health-check manual, listagem e leitura de histórico.  
   - Camada mais fina possível: converte HTTP ⇄ DTOs ⇄ serviços.

5. **Console de admin (UI mínima, ex.: `app/admin/ui/pages/sources_*`)**  
   - Telas mínimas para listar, criar/editar e inspecionar fontes, incluindo visualização de estados e health-checks.  
   - Não é UI final, mas já suporta o fluxo ponta a ponta descrito na Sprint 21.

Transversalmente, existem ainda duas dimensões importantes:
- **Infra de banco & migrations** (pasta `migrations/versions/`).
- **Teste e validação** (pasta `tests/sources/` + scripts `bin/s21_g*.sh` + `out/scorecards/` + `out/evidence/`).

Tudo é desenhado para **não adiantar** ingestão contínua (Sprint 22) nem lógica de agentes/Debunker (S23/S24), mas deixando os contratos prontos.

---

### 3. Filemap da Sprint 21 — visão macro

A Sprint 21 atua em seis grandes áreas do repositório:

1. `docs/` — documentação da sprint (capítulos, ontologia, modelo de dados, fluxos, cenários, contratos, scorecards, wrap).
2. `app/sources/` — módulo de domínio e serviços de fontes.
3. `app/admin/ui/` (ou equivalente) — console administrativo mínimo para fontes.
4. `migrations/versions/` — migrations específicas do módulo de fontes.
5. `tests/sources/` — testes de domínio, serviço, API e health-checks.
6. `bin/`, `out/scorecards/`, `out/evidence/` — automação dos gates e artefatos de validação.

As seções seguintes detalham o conteúdo recomendado de cada área, com foco em **clareza, rastreabilidade e aderência aos gates S21_G0…S21_G8**.

---

### 4. docs/ — documentos da Sprint 21

A Sprint 21 adiciona/atualiza os seguintes arquivos em `docs/`:

- `docs/sprint_21_capitulo_1.md`  
  Contexto, narrativa e objetivos (Capítulo 1).

- `docs/sprint_21_capitulo_2_gates.md`  
  Definição dos gates S21_G0…S21_G8 (Capítulo 2 v2).

- `docs/sprint_21_capitulo_3_filemap.md`  
  Este documento (Capítulo 3), descrevendo arquitetura e filemap.

- `docs/sprint_21_ontologia_fontes.md`  
  Gate S21_G1 — definição da ontologia de fontes, tipos, atributos e exemplos multidomínio.

- `docs/sprint_21_modelo_dados_fontes.md`  
  Gate S21_G2 — entidades, campos, relacionamentos, invariantes, chaves.

- `docs/sprint_21_ciclo_vida_fontes.md`  
  Gate S21_G2 — máquina de estados da fonte, transições válidas, eventos.

- `docs/sprint_21_fluxos_admin_fontes.md`  
  Gate S21_G3 — fluxos administrativos (cadastro, edição, suspeita, desativação, reativação).

- `docs/sprint_21_ganchos_debunker_fontes.md`  
  Gate S21_G4 — campos, estados e estruturas para Debunker, contestação e redundância.

- `docs/sprint_21_cenarios_uso_fontes.md`  
  Gate S21_G6 — cenários de uso (notícias, fofoca, esportes, clima, mandatos, projetos, ciência, etc.), com preenchimento completo.

- `docs/sprint_21_contratos_s22_s25.md`  
  Gate S21_G5 — contratos de S21 com S22, S23, S24 e S25.

- `docs/sprint_21_scorecard_console_fontes.md`  
  Gate S21_G7 — indicadores de qualidade e risco.

- `docs/sprint_21_wrap_execucao.md`  
  Gate S21_G8 — wrap final da sprint, tabela Gate × Status, entregas, riscos.

Convenções:
- Todos os documentos da Sprint 21 devem se referenciar entre si de forma consistente (por exemplo, Capítulo 3 apontando explicitamente para arquivos usados em cada gate).
- Se forem criados anexos (diagramas, imagens), eles devem ficar em subpastas como `docs/img/` com nomes que mencionem `sprint_21_*`.

---

### 5. app/sources/ — domínio, serviços e API de fontes

O pacote `app/sources/` é o coração técnico da Sprint 21. Estrutura sugerida:

- `app/sources/__init__.py`  
  Inicialização do pacote; pode registrar roteadores ou providers.

- `app/sources/models.py`  
  - Define os modelos persistidos (por exemplo, via SQLAlchemy ou ORM adotado):
    - `Source` — entidade principal da fonte.
    - `SourceType` — tabela/enum de tipos de fonte.
    - `SourceCategory` e/ou tabelas de relacionamento fonte↔categoria.
    - `SourceStateHistory` — log de estados da fonte ao longo do tempo.
    - `SourceHealthCheck` — registros de health-check.
  - Implementa:
    - campos de auditoria (`created_at`, `updated_at`, `created_by`, `updated_by`);
    - invariantes do ciclo de vida (por exemplo, não permitir voltar de `DESATIVADA_PERMANENTE` para `ATIVA`).

- `app/sources/schemas.py`  
  - DTOs e schemas de validação:
    - `SourceCreate`, `SourceUpdate`, `SourceRead`;
    - `SourceTypeRead`, `SourceCategoryRead`;
    - `SourceFilter` (para listagens paginadas com filtros);
    - schemas de config por tipo (`SourceConfigRSS`, `SourceConfigHTTPAPI`, etc.).
  - Garante coerência com `docs/sprint_21_ontologia_fontes.md` e `docs/sprint_21_modelo_dados_fontes.md`.

- `app/sources/validators.py`  
  - Funções que:
    - validam `SourceConfig*` por tipo de fonte;
    - verificam se combinações de tipo/categoria/estado são aceitáveis;
    - garantem que campos obrigatórios do tipo estão presentes.

- `app/sources/service.py`  
  - Operações de domínio:
    - `create_source`, `update_source`, `change_source_state`;
    - `register_healthcheck`;
    - `list_sources` com filtros combinados;
    - `get_source_detail` com histórico e health-checks.
  - Aplica a máquina de estados e chama `validators.py` quando necessário.

- `app/sources/healthcheck.py`  
  - Implementa health-check manual por tipo de fonte:
    - resolve config;
    - executa requisição ou leitura (HTTP, arquivo, etc.);
    - mede latência e classifica resultado (`OK`, `DEGRADED`, `FAIL`);
    - grava um `SourceHealthCheck`.

- `app/sources/routes_admin.py`  
  - Router da API de admin:
    - `GET /admin/sources` — lista paginada, filtros por tipo/categoria/estado.
    - `GET /admin/sources/{id}` — detalhe da fonte.
    - `POST /admin/sources` — criação.
    - `PUT /admin/sources/{id}` — edição.
    - `POST /admin/sources/{id}/healthcheck` — health-check manual.
    - `GET /admin/sources/{id}/healthchecks` — histórico.

- `app/sources/events.py` (opcional, mas recomendado)
  - Emite eventos internos para criação, alteração, mudança de estado e health-checks.
  - Esses eventos alimentam logs, métricas e, futuramente, hooks de S22–S25.

Todos esses arquivos são **evidências técnicas** relevantes para os gates S21_G2 (modelo de dados), S21_G3 (fluxos admin), S21_G4 (ganchos Debunker) e S21_G6 (cenários).

---

### 6. app/admin/ui/ — console mínimo de fontes

A UI mínima de admin deve refletir os fluxos descritos em `docs/sprint_21_fluxos_admin_fontes.md` e servir como base para demos da Sprint 21.

Exemplo de estrutura em um stack React/Next (adaptar conforme a stack real):

- `app/admin/ui/pages/sources/index.tsx`
  - Lista de fontes com colunas: Nome, Tipo, Categoria, Estado, Último Health-Check, Ações.
  - Filtros combinados por tipo/categoria/estado.

- `app/admin/ui/pages/sources/[id].tsx`
  - Página de detalhe: mostra todos os campos da fonte, estados recentes, histórico de health-check.

- `app/admin/ui/pages/sources/new.tsx`
  - Formulário de criação, com campos condicionais por tipo de fonte.

- `app/admin/ui/components/source_health_pill.tsx`
  - Componente visual para estado de saúde (OK/DEGRADED/FAIL).

- `app/admin/ui/components/source_state_timeline.tsx`
  - Pequena timeline dos últimos estados da fonte.

O objetivo não é entregar UI polida, mas **uma interface funcional** para operar os fluxos de admin que serão usados como evidência nos gates (especialmente S21_G3, S21_G6 e o wrap de S21_G8).

---

### 7. migrations/versions/ — migrations da Sprint 21

A Sprint 21 exige migrations explícitas para o módulo de fontes. Convenção recomendada:

- `migrations/versions/<hash>_s21_sources_schema.py`
  - Criação/alteração das tabelas:
    - `sources`
    - `source_types`
    - `source_categories` / tabelas de join
    - `source_state_history`
    - `source_health_checks`
  - Comentários no cabeçalho referenciando `docs/sprint_21_modelo_dados_fontes.md`.

- `migrations/versions/<hash>_s21_sources_seed_examples.py`
  - Inserção de algumas fontes de exemplo (notícias, fofoca, esportes, clima, mandatos, projetos, ciência) para cenários da S21.

Essas migrations servem como parte das evidências de S21_G2 (modelo de dados) e S21_G6 (cenários de uso com dados reais). O Capítulo 4 definirá os comandos padrão para criá-las/aplicá-las.

---

### 8. tests/sources/ — testes de domínio, serviços, API e cenários

Os testes da Sprint 21 vivem sob `tests/sources/` e se alinham diretamente com os gates:

- `tests/sources/test_domain_model.py`
  - Foca em:
    - invariantes do modelo (`Source`, `SourceStateHistory`, etc.);
    - transições válidas/ inválidas de estados;
    - obrigatoriedade de campos.
  - Evidência para S21_G2.

- `tests/sources/test_service.py`
  - Testa `create_source`, `update_source`, `change_source_state`, `register_healthcheck`.
  - Garante que as regras de negócio descritas nos docs estão implementadas.
  - Evidência para S21_G2 e S21_G3.

- `tests/sources/test_routes_admin.py`
  - Exercita endpoints da API de admin, cobrindo erros esperados (ex.: config inválida, transição proibida).
  - Evidência para S21_G3.

- `tests/sources/test_healthcheck_integration.py`
  - Roda health-checks sobre as fontes seedadas nas migrations da S21.
  - Usa cenários de `docs/sprint_21_cenarios_uso_fontes.md` como referência.
  - Evidência para S21_G6.

Os testes são também insumo indireto para o scorecard S21_G7 (métrica de cobertura qualitativa e robustez do Console de Fontes).

---

### 9. bin/, out/scorecards/ e out/evidence/ — automação e rastreabilidade

#### 9.1 Scripts de gates em `bin/`

A Sprint 21 adiciona scripts shell para cada gate, seguindo padrão já estabelecido no projeto:

- `bin/s21_g0_contexto.sh`
- `bin/s21_g1_ontologia_fontes.sh`
- `bin/s21_g2_modelo_dados.sh`
- `bin/s21_g3_fluxos_admin.sh`
- `bin/s21_g4_ganchos_debunker.sh`
- `bin/s21_g5_contratos_s22_s25.sh`
- `bin/s21_g6_cenarios_uso.sh`
- `bin/s21_g7_scorecard.sh`
- `bin/s21_g8_go_no_go.sh`

Opcional:
- `bin/s21_all_gates.sh` — orquestra execução sequencial dos scripts acima.

Cada script deve:
- Validar a presença e formato de arquivos esperados.
- Gerar (ou atualizar) um scorecard em `out/scorecards/`.
- Escrever evidências em `out/evidence/S21_GX_nome_gate/`.

#### 9.2 Scorecards em `out/scorecards/`

Scorecards esperados:

- `out/scorecards/S21_G0_contexto.json`
- `out/scorecards/S21_G1_ontologia.json`
- `out/scorecards/S21_G2_modelo_dados.json`
- `out/scorecards/S21_G3_fluxos_admin.json`
- `out/scorecards/S21_G4_ganchos_debunker.json`
- `out/scorecards/S21_G5_contratos.json`
- `out/scorecards/S21_G6_cenarios_uso.json`
- `out/scorecards/S21_G7_scorecard.json`
- `out/scorecards/S21_G8_go_no_go.json`

Formato mínimo (conforme Capítulo 2 v2):
- `gate_id`
- `status`
- `automated_checks`
- `reviewers_internal[]`
- `reviewers_external[]`
- `risk_level`
- `notes`
- `ts_last_update`

#### 9.3 Evidências em `out/evidence/`

Para cada gate, uma pasta:

- `out/evidence/S21_G0_contexto/`
- `out/evidence/S21_G1_ontologia/`
- `out/evidence/S21_G2_modelo_dados/`
- `out/evidence/S21_G3_fluxos_admin/`
- `out/evidence/S21_G4_ganchos_debunker/`
- `out/evidence/S21_G5_contratos/`
- `out/evidence/S21_G6_cenarios_uso/`
- `out/evidence/S21_G7_scorecard/`
- `out/evidence/S21_G8_go_no_go/`

Cada pasta deve conter, no mínimo:
- `MANIFEST.json` — lista dos arquivos de evidência.
- Um ou mais arquivos com extratos de docs, logs de scripts, prints de cenários ou snapshots de configs.

---

### 10. Gate → Artefatos principais (tabela mental)

Este capítulo também funciona como uma tabela mental Gate → Artefatos principais (todos descritos acima):

- **S21_G0**  
  - docs/sprint_21_capitulo_1.md  
  - docs/sprint_21_capitulo_2_gates.md  
  - out/scorecards/S21_G0_contexto.json  
  - out/evidence/S21_G0_contexto/*

- **S21_G1**  
  - docs/sprint_21_ontologia_fontes.md  
  - (opcional) docs/sprint_21_ontologia_fontes.json  
  - out/scorecards/S21_G1_ontologia.json  
  - out/evidence/S21_G1_ontologia/*

- **S21_G2**  
  - docs/sprint_21_modelo_dados_fontes.md  
  - docs/sprint_21_ciclo_vida_fontes.md  
  - migrations/versions/*_s21_sources_schema.py  
  - app/sources/models.py  
  - tests/sources/test_domain_model.py  
  - out/scorecards/S21_G2_modelo_dados.json  
  - out/evidence/S21_G2_modelo_dados/*

- **S21_G3**  
  - docs/sprint_21_fluxos_admin_fontes.md  
  - app/sources/service.py  
  - app/sources/routes_admin.py  
  - app/admin/ui/pages/sources_*  
  - tests/sources/test_service.py  
  - tests/sources/test_routes_admin.py  
  - out/scorecards/S21_G3_fluxos_admin.json  
  - out/evidence/S21_G3_fluxos_admin/*

- **S21_G4**  
  - docs/sprint_21_ganchos_debunker_fontes.md  
  - app/sources/models.py (campos e relações extras)  
  - docs/sprint_21_ciclo_vida_fontes.md (estados e transições de contestação)  
  - out/scorecards/S21_G4_ganchos_debunker.json  
  - out/evidence/S21_G4_ganchos_debunker/*

- **S21_G5**  
  - docs/sprint_21_contratos_s22_s25.md  
  - out/scorecards/S21_G5_contratos.json  
  - out/evidence/S21_G5_contratos/*

- **S21_G6**  
  - docs/sprint_21_cenarios_uso_fontes.md  
  - migrations/versions/*_s21_sources_seed_examples.py  
  - tests/sources/test_healthcheck_integration.py  
  - out/scorecards/S21_G6_cenarios_uso.json  
  - out/evidence/S21_G6_cenarios_uso/*

- **S21_G7**  
  - docs/sprint_21_scorecard_console_fontes.md  
  - out/scorecards/S21_G7_scorecard.json  
  - out/evidence/S21_G7_scorecard/*

- **S21_G8**  
  - docs/sprint_21_wrap_execucao.md  
  - out/scorecards/S21_G8_go_no_go.json  
  - out/evidence/S21_G8_go_no_go/MANIFEST.json

---

### 11. Integração com CI/ORR e próximas sprints

O Capítulo 3 também baliza o trabalho de CI/ORR:

- Um workflow de CI específico (por exemplo, `.github/workflows/_s21-orr.yml`) pode:
  - rodar testes em `tests/sources/`;
  - executar `bin/s21_all_gates.sh`;
  - arquivar `out/scorecards/` e `out/evidence/` como artefatos.

- A disciplina de ORR (T0–T8) do projeto pode, mais tarde, tratar a Sprint 21 como mais um “pacote de evidência” plugado ao pipeline padrão.

Para S22–S25, este capítulo garante que:
- S22 sabe **onde** ler config e estados de fontes para ingestão.
- S23 sabe **quais tipos/categorias** existem e como eles estão representados.
- S24 sabe **quais campos e estados** usar para conectar Debunker e contestação ao Console de Fontes.
- S25 sabe **como rastrear** a proveniência das fontes em decisões de verdade/fato.

---

### 12. Definição de pronto do Capítulo 3

O Capítulo 3 é considerado pronto quando:

1. O filemap aqui descrito cobre todos os arquivos e pastas relevantes da Sprint 21, sem lacunas óbvias.
2. As responsabilidades de cada arquivo estão claras, conectadas aos gates do Capítulo 2.
3. As interfaces com S22–S25 estão explícitas, sem contradições com os Capítulos 1 e 2.
4. O documento é detalhado o bastante para que o Capítulo 4 possa descrever um plano de execução quase mecânico (passo a passo para Codex) com base nele.

Com isso, o Squad 1 tem um mapa único para implementar o Console de Fontes, e o resto da equipe tem uma visão compartilhada de onde cada parte da Sprint 21 vive dentro do Inspectah.

