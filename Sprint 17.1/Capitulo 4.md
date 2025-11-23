Sprint 17.1 — Capítulo 4
Runbook de execução da API de consulta do Inspectah
===================================================

1. TL;DR operacional
---------------------

O objetivo da Sprint 17.1 é fechar, de forma definitiva (sem gambiarras), o buraco entre o backend do Inspectah e a UI de consulta da Sprint 17:

- A rota **POST /api/consultation** passa a existir, documentada em `/docs`, com contrato estável, versionado e testado.
- Essa rota é uma **fachada fina** sobre o motor real (Debunker + Comitês + TruthDB/anchors), sem duplicar regra de negócio.
- A UI da Sprint 17 funciona **sem nenhum ajuste manual de endpoint ou shape**: o que está em `frontend/inspectah-ui/src/types/inspectah.ts` é exatamente o contrato retornado pela API.
- O fluxo ponta-a-ponta (UI → API → Debunker/Comitês/TruthDB → resposta) fica protegido pelos gates **T0…T8 da S17.1**, alinhados ao DNA e ao Playbook.

Se alguém seguir apenas este capítulo + o Capítulo 2 (gates) da Sprint 17.1, deve ser capaz de:

1. Implementar a API de consulta sem abrir o Capítulo 1 novamente.
2. Rodar todos os gates S17.1 com um comando.
3. Subir backend + frontend localmente e fazer uma consulta real pela UI, sem mais erro “Não conseguimos falar com o Inspectah agora”.

2. Objetivo e escopo deste capítulo
-----------------------------------

Este Capítulo 4 pega a visão (Capítulo 1), os gates (Capítulo 2) e o filemap/arquitetura (Capítulo 3) e transforma tudo em um **plano de execução concreto**, para humanos e para o Codex:

- Explicita **o que** deve ser construído/alterado.
- Em **quais arquivos** e **módulos**.
- Em **que ordem**.
- Com **quais comandos** de verificação e gates.

Escopo do que este capítulo cobre:

1) Modelos e contrato da API de consulta (Pydantic).
2) Serviço de consulta (orquestrador Debunker + Comitês + TruthDB/anchors).
3) Adaptadores, observabilidade e invariantes de risco.
4) Roteador HTTP e wiring com FastAPI (app real, sem stub).
5) Testes unitários, de integração e de contrato UI↔API.
6) Scripts de gates T0…T8 da Sprint 17.1 e orquestrador `s17_1_all_gates`.
7) Workflows de CI/nigthly da S17.1.
8) Runbook E2E: do clone limpo até a UI funcionando em cima da nova API.

Fora de escopo (para evitar confusão):

- Evoluções de UI além da Sprint 17 (timelines, raio‑X avançado, console admin — isso é S18+).
- Mudanças no motor profundo do Debunker/Comitês/TruthDB além do necessário para a rota de consulta.

3. Fases de execução (ordem sugerida)
-------------------------------------

### Fase 0 — Preparar ambiente e estado de trabalho

**Objetivo:** garantir que tudo é feito em cima de um baseline limpo, com venv ativado e S15–S17 estáveis.

1) Backend

- Diretório do projeto:  
  `/Users/gustavoschneiter/Documents/Inspectah`
- Ativar venv (sempre que abrir um shell novo para backend):
  - `cd /Users/gustavoschneiter/Documents/Inspectah`
  - `source .venv/bin/activate`

2) Frontend

- Diretório principal da UI de consulta:  
  `/Users/gustavoschneiter/Documents/Inspectah/frontend/inspectah-ui`
- Dependências já consolidadas na Sprint 17:  
  - `npm ci`  
  - `npm run lint`  
  - `npm run test`  
  - `npm run build`

3) Git/estado

- Garantir `main` limpo antes de começar a S17.1:
  - `cd /Users/gustavoschneiter/Documents/Inspectah`
  - `git status` → *nothing to commit, working tree clean*.
- Sprint 17.1 pode ser feita em branch dedicada (exemplo):
  - `git checkout -b feat/s17_1_consultation_api`

### Fase 1 — Modelos e contratos da API de consulta

**Objetivo:** materializar em código o contrato descrito no Capítulo 2/3, sem misturar HTTP, Debunker, Comitês ou UI.

1) Módulo de modelos

- Arquivo sugerido (conforme Capítulo 3):
  - `inspectah/consultation_models.py`
- Conteúdo esperado (alto nível):
  - Enum `RiskLevel` compatível com Debunker/Comitês e com a UI:
    - por exemplo: `low`, `high`, `unknown`.
  - Modelo de request (`ConsultationRequest`):
    - `question: str` (obrigatório, não vazio).
    - Opcionalmente, campos como `expected_risk: Optional[RiskLevel]`, `metadata: dict[str, Any] | None`, `user_context: dict[str, Any] | None` — exatamente como definido no Capítulo 2.
  - Modelo de evidência (`EvidenceItem`):
    - Campos típicos: `source_id`, `source_name`, `snippet`, `url` (quando existir), `relevance_score`.
  - Modelo de response (`ConsultationResponse`):
    - `request_id: str` (sempre presente).
    - `risk_level: RiskLevel`.
    - `answer: str | None` (texto consolidado para o usuário).
    - `summary: str | None` (versão ainda mais amigável/resumida, se aplicável).
    - `evidence: list[EvidenceItem]` (nunca `null`; lista vazia quando não houver o que mostrar).
    - Campos adicionais descritos no Capítulo 2: por exemplo, `risk_flags: list[str]`, `has_insufficient_data: bool`, `engine_metadata: dict[str, Any] | None`.

2) Invariantes de contrato

O código deve garantir, no mínimo:

- Nenhuma resposta 200 sai sem `request_id` e `risk_level` preenchidos.
- `evidence` **nunca** é `null` no JSON; sempre uma lista (possivelmente vazia).
- Erros de input (question vazia, tipos incorretos) geram erro 4xx com JSON coerente, sem stack trace.
- Erros internos geram 5xx controlado com mensagem genérica (sem vazar detalhes internos), suportando a mensagem de erro amigável que a UI exibe.

### Fase 2 — Serviço de consulta (orquestrador)

**Objetivo:** concentrar a lógica de orquestração da consulta em um serviço puro, sem acoplamento a HTTP ou UI.

1) Módulo de serviço

- Arquivo sugerido:  
  `inspectah/consultation_service.py`
- Conteúdo esperado:
  - Classe (ou conjunto de funções) `ConsultationService` com dependências injetadas:
    - Debunker (`inspectah.debunker.engine`).
    - Comitês (`inspectah.committees.*`).
    - Acesso a TruthDB/anchors (quando necessário para evidência).
    - Logger/metrics.
  - Método principal:
    - `run_consultation(request: ConsultationRequest) -> ConsultationResponse`:
      - Normaliza/valida a pergunta e metadados.
      - Chama Debunker para análise de risco e coleta de base de evidências.
      - Passa pelos Comitês para validação, coerência e decisão final.
      - Consolida a resposta no shape `ConsultationResponse`.
      - Registra logs e métricas conforme Capítulo 3.

2) Tratamento de erros no serviço

- Casos previstos (não bugs):
  - Dados insuficientes, fontes conflitantes, alto risco sem evidência robusta.
  - O serviço deve traduzir isso em `has_insufficient_data=True` ou em `risk_flags` apropriados, retornando 200.
- Casos não previstos (bugs, exceções inesperadas):
  - Devem levantar exceção interna própria (ex: `ConsultationInternalError`) para a camada HTTP converter em 5xx controlado.

### Fase 3 — Adaptadores, observabilidade e integrações

**Objetivo:** conectar o serviço com implementações reais de Debunker/Comitês/TruthDB e garantir logs/metrics consistentes.

1) Adaptadores Debunker/Comitês

- Reaproveitar os módulos já existentes:
  - `inspectah/debunker/engine.py`
  - `inspectah/committees/v1_validator.py`
  - `inspectah/committees/v2_multibrain.py`
  - `inspectah/committees/v3_coherence.py`
- Criar camada fina de adaptação (pode ser dentro de `consultation_service.py` ou um módulo auxiliar, desde que respeite o filemap do Capítulo 3):
  - Converter `ConsultationRequest` na estrutura de input esperada pelo Debunker/Comitês.
  - Converter o output deles em `RiskLevel`, `risk_flags` e `EvidenceItem`s.
  - Respeitar políticas hardened da S16 (Threat Model):
    - Ex: rejeitar submissões claramente maliciosas.
    - Sinalizar estados de alto risco devidamente.

2) Observabilidade

- Reaproveitar infra existente (ex: `inspectah/metrics.py` e padrões de logging em S15–S16):
  - Toda consulta deve:
    - Gerar/propagar um `request_id`.
    - Registrar:
      - `request_id`, `risk_level`, `elapsed_ms`, `status` (success/error/insufficient_data), `origin=api.consultation`.
    - Emitir métricas:
      - Contadores por resultado (`success`, `insufficient_data`, `error`), por `risk_level`.
      - Histogramas de latência.

### Fase 4 — API HTTP e wiring com FastAPI

**Objetivo:** expor uma API canônica, sem stub, integrada ao serviço de consulta e à infra HTTP já existente.

1) Módulo HTTP da consulta

- Arquivo sugerido:  
  `inspectah/consultation_api.py`
- Conteúdo esperado:
  - `router = APIRouter(prefix="/api", tags=["consultation"])`.
  - Endpoint principal:
    - `@router.post("/consultation", response_model=ConsultationResponse, ...)`
    - Recebe `ConsultationRequest`.
    - Obtém instância de `ConsultationService` com dependências reais.
    - Chama `run_consultation` e retorna `ConsultationResponse`.
  - Tratamento de exceções:
    - Deixar o FastAPI lidar com validação de input.
    - Capturar `ConsultationInternalError` e devolver 5xx com payload genérico.

2) Wiring em `inspectah/api.py`

- Ajustar `build_router()`/`build_app()` para:
  - Incluir as rotas de `/explore` já existentes.
  - Incluir o router de `/api/consultation`.
- Resultado esperado em `http://localhost:8000/docs`:
  - Grupo (tag) “consultation” com o endpoint `POST /api/consultation`.
  - Schema OAS atualizado refletindo `ConsultationRequest` e `ConsultationResponse`.

### Fase 5 — Testes automatizados (unitários, integração, contrato)

**Objetivo:** aumentar a confiança antes de ligar os gates T0…T8.

1) Testes unitários

- Arquivos sugeridos:
  - `tests/test_consultation_models.py`
  - `tests/test_consultation_service.py`
- Cobrir:
  - Invariantes dos modelos (campos obrigatórios, defaults, enums corretos).
  - Comportamento do `ConsultationService` com Debunker/Comitês simulados:
    - fluxos de baixo risco, alto risco, dados insuficientes, erros internos simulados.

2) Testes de integração/API

- Arquivo sugerido:
  - `tests/test_consultation_api.py`
- Usar `TestClient` do FastAPI para cenários:
  - Fluxo feliz: pergunta válida → 200, `risk_level` coerente, evidências preenchidas.
  - Alto risco: 200, `risk_level='high'`, `risk_flags` adequados.
  - Dados insuficientes: 200, `has_insufficient_data=True`, evidência possivelmente vazia.
  - Input inválido: erro 4xx com JSON de erro consistente.
  - Erro interno simulado: 5xx controlado sem stack trace em payload.

3) Testes de contrato UI↔API

- Garantir compatibilidade com `frontend/inspectah-ui/src/types/inspectah.ts`:
  - Os nomes dos campos e tipos JSON precisam bater; se houver divergência, ajustar este arquivo **ou** o contrato da API, sempre mantendo o Capítulo 2 como referência primária.

### Fase 6 — Gates T0…T8 e orquestração

**Objetivo:** ligar o trabalho de S17.1 à malha de gates do DNA, com scripts idempotentes e scorecards/evidências padronizados.

1) Scripts de gates

- Padrão de nomenclatura para S17.1:
  - `bin/s17_1_t0_sanity.sh`
  - `bin/s17_1_t1_contracts_and_states.sh`
  - `bin/s17_1_t2_integration_core_flows.sh`
  - `bin/s17_1_t3_error_paths_and_resilience.sh`
  - `bin/s17_1_t4_ui_wire_and_e2e_smoke.sh`
  - `bin/s17_1_t5_performance_and_limits.sh`
  - `bin/s17_1_t6_observability_and_logs.sh`
  - `bin/s17_1_t7_ci_and_repro.sh`
  - `bin/s17_1_t8_go_no_go.sh`
- Orquestrador:
  - `bin/s17_1_all_gates.sh`

2) Comportamento esperado de cada gate (vista operacional)

- **T0_sanity**
  - Verifica ambiente básico:
    - Ativa venv.
    - Confere import de `inspectah.api`, `consultation_models`, `consultation_service`, `consultation_api`.
    - Pode rodar subset rápido de testes (`pytest tests/test_consultation_models.py -q`).
  - Gera scorecard `out/scorecards/S17_1_T0_sanity.json` + evidências em `out/evidence/S17_1_T0_sanity/`.

- **T1_contracts_and_states**
  - Foca nos modelos e contrato da API.
  - Roda testes de contrato e estados (ex: `pytest tests/test_consultation_models.py tests/test_consultation_api.py -k contract`).
  - Scorecard `S17_1_T1_contracts_and_states.json`.

- **T2_integration_core_flows**
  - Exercita o `ConsultationService` com Debunker/Comitês reais ou fixtures realistas.
  - Garante fluxos “baixo risco”, “alto risco” e “incerto” cobertos.

- **T3_error_paths_and_resilience**
  - Simula falhas internas e de dependências.
  - Verifica códigos 4xx/5xx, payloads e logs estruturados corretos.

- **T4_ui_wire_and_e2e_smoke**
  - Sobe backend local (ou assume já rodando) e executa smoke E2E equivalente ao fluxo da UI:
    - POST para `/api/consultation` com payload idêntico ao usado pelo frontend.
    - Verifica que a resposta tem shape compatível com `types/inspectah.ts`.

- **T5_performance_and_limits**
  - Pequeno load test local (ex: N requisições sequenciais/concorrentes com script Python ou ferramenta leve).
  - Verifica p95 de latência e limites definidos no Capítulo 2.

- **T6_observability_and_logs**
  - Checa logs e métricas:
    - Logs com `request_id`, `risk_level`, `elapsed_ms`, `status`.
    - (Se existir) endpoint de métricas respondendo sem erro.

- **T7_ci_and_repro**
  - Garante que os workflows `.ci/sprint_17_1_gates.yml` e `.ci/sprint_17_1_nightly.yml` chamam os scripts corretos.
  - Opcionalmente, fornece comando único para rodar localmente o que o CI executa.

- **T8_go_no_go**
  - Lê todos os scorecards `S17_1_T0…T7`.
  - Avalia se todos estão `PASS`.
  - Gera `out/scorecards/S17_1_T8_go_no_go.json` com:
    - `decision: "GO" | "GO_WITH_RESTRICTIONS" | "NO_GO"`.
    - `commit_sha` final da S17.1.
    - Pointers das principais evidências.
  - Sai com `exit 0` somente em caso de `GO` (ou `GO_WITH_RESTRICTIONS`, se definido assim no Capítulo 2).

### Fase 7 — CI e nightly da Sprint 17.1

**Objetivo:** colocar S17.1 no mesmo trilho de qualidade das S15–S17.

1) Workflows de CI

- Arquivos:
  - `.ci/sprint_17_1_gates.yml`
  - `.ci/sprint_17_1_nightly.yml`
- Padrão:
  - `sprint_17_1_gates.yml`:
    - Rodar T0…T4 em PRs/commits relevantes.
  - `sprint_17_1_nightly.yml`:
    - Rodar T0…T6 diariamente, testando saúde da API e compatibilidade com a UI.

2) Integração com visão macro de sprints

- Atualizar docs de visão geral (por exemplo, `docs/inspectah_cap_1_produto.md` ou documento de roadmap) para registrar:
  - “Sprint 17.1 — API de consulta (backbone da UI)” como ponte entre S16 (Threat Model/hardening) e S17 (UI de consulta).

### Fase 8 — E2E operacional: do zero à consulta pela UI

**Objetivo:** garantir que qualquer operador consiga subir Inspectah + UI com passos mínimos.

1) Subir backend

- Comandos oficiais:
  - `cd /Users/gustavoschneiter/Documents/Inspectah`
  - `source .venv/bin/activate`
  - `PYTHONPATH=. python -m uvicorn inspectah.api:build_app --factory --reload --port 8000`
- Verificação:
  - Acessar `http://localhost:8000/docs`.
  - Confirmar que o endpoint `POST /api/consultation` aparece na seção de rotas.

2) Subir frontend

- Comandos oficiais:
  - `cd /Users/gustavoschneiter/Documents/Inspectah/frontend/inspectah-ui`
  - `npm ci` (na primeira vez, ou quando necessário)
  - `npm run dev`
- A UI deve estar em `http://localhost:5173/`.

3) Smoke test manual

- Exemplos de perguntas para testar via UI:
  - “O furacão Katrina atingiu Nova Orleans em 2005?”
  - “É verdade que o jogador X marcou mais de 30 gols no campeonato Y?”
- Comportamento esperado:
  - A UI não mostra mais “Não conseguimos falar com o Inspectah agora” por falta de endpoint.
  - A resposta traz um nível de risco (`baixo/alto/incerto`) e evidências coerentes.
  - Quando os dados são insuficientes, a UI mostra mensagem amigável (estado de “dados insuficientes”) e não um erro genérico de backend.

4. Definição de pronto (DoD) da Sprint 17.1
-------------------------------------------

A Sprint 17.1 só é considerada concluída quando **todos** os itens abaixo forem verdadeiros:

1) **API canônica**

- `POST /api/consultation` existe, está documentada em `/docs` e responde conforme o contrato.
- Os modelos Pydantic (request/response/evidence/risk) estão em `inspectah/consultation_models.py` (ou arquivo equivalente, conforme filemap) e cobertos por testes.

2) **Integração Debunker/Comitês/Threat Model**

- `ConsultationService` utiliza Debunker + Comitês + políticas de risco maduras da S16.
- Fluxos de baixo risco, alto risco e dados insuficientes estão cobertos por testes e pelos gates T2/T3.

3) **Observabilidade**

- Cada consulta gera logs estruturados com `request_id`, `risk_level`, `elapsed_ms` e `status`.
- Métricas básicas estão disponíveis (contadores, latência) conforme Capítulo 3.

4) **Gates e CI**

- `bin/s17_1_t0...t8.sh` executam com `exit 0` em ambiente limpo.
- `bin/s17_1_all_gates.sh` roda inteira e gera scorecards `out/scorecards/S17_1_T*.json` + evidências em `out/evidence/S17_1_T*_*`.
- Workflows `.ci/sprint_17_1_gates.yml` e `.ci/sprint_17_1_nightly.yml` estão presentes, validados e acionam os scripts corretos.

5) **UI funcionando sem ajustes manuais**

- Com backend (S15–S16 + S17.1) e frontend (S17) rodando, um operador consegue:
  - Abrir `http://localhost:5173/`.
  - Enviar consultas em linguagem natural.
  - Ver respostas com risco + evidências, sem erro de backend.

6) **ORR da Sprint 17.1**

- `docs/sprint_17_1_orr_summary.md` existe e está preenchido com:
  - Tabela Gate×Status atualizada.
  - `commit_sha` final onde a S17.1 foi entregue.
  - Decisão T8 (`GO` ou `GO_WITH_RESTRICTIONS`) e restrições, se houver.

5. Checklists finais
---------------------

### Checklist para o Codex

- [ ] Criar/atualizar `inspectah/consultation_models.py` conforme Capítulos 2 e 3.
- [ ] Criar `inspectah/consultation_service.py` com `ConsultationService` e integração com Debunker/Comitês.
- [ ] Criar `inspectah/consultation_api.py` com router `/api/consultation` e conectar em `inspectah/api.py`.
- [ ] Escrever testes:
  - [ ] `tests/test_consultation_models.py`
  - [ ] `tests/test_consultation_service.py`
  - [ ] `tests/test_consultation_api.py`
- [ ] Criar scripts `bin/s17_1_t0...t8.sh` + `bin/s17_1_all_gates.sh`.
- [ ] Criar workflows `.ci/sprint_17_1_gates.yml` e `.ci/sprint_17_1_nightly.yml`.

### Checklist para execução humana

- [ ] `git status` → árvore limpa antes de começar.
- [ ] `source .venv/bin/activate` no backend.
- [ ] `PYTHONPATH=. bin/s17_1_all_gates.sh` → todos os gates verdes.
- [ ] `git commit` com mensagem clara (ex: `feat: entregar Sprint 17.1 (API de consulta)`), `git push`.
- [ ] Atualizar `docs/sprint_17_1_orr_summary.md` com SHA final e decisão T8.
- [ ] Subir backend + frontend e fazer uma consulta real via UI.

Com isso, o Capítulo 4 da Sprint 17.1 entrega um runbook de ponta a ponta, sem atalhos e sem correções provisórias, alinhado ao DNA e garantindo que a API de consulta do Inspectah passe a ser um componente canônico e confiável do sistema.

