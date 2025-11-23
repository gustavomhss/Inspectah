# Sprint 17.1 — Capítulo 2 (rev final)

## 2.1 Objetivo dos gates

A Sprint 17.1 existe para corrigir um erro estrutural: a UI da Sprint 17 foi entregue antes de existir uma **API de consulta oficial, versionada e protegida por gates**. O resultado foi exatamente o que não aceitamos no Inspectah: UI pronta, mas chamando um backend “mudo” (rota inexistente, contrato implícito, CORS sem guarda, ausência de testes end‑to‑end).

Este capítulo define os **gates S17A_T0…S17A_T8** que blindam a API de consulta, garantindo que:

- A rota oficial `/api/consultation` existe, está documentada e é coerente com o contrato esperado pela UI.
- A API é apenas uma **fachada disciplinada** por cima dos núcleos já consolidados (Debunker, Comitês, Âncoras, Truth‑DB), sem atalhos ou bypass.
- Happy paths, erros e degradação controlada estão cobertos por **cenários automatizados**.
- Qualquer regressão em rota/contrato/comportamento passa a quebrar **gates e CI**, não o browser do usuário.

Os gates 17.1 não competem com os das S15–S16; eles criam uma camada explícita para o **contrato público** do Inspectah.


## 2.2 Mapa de gates (S17A_T0…S17A_T8)

Os gates são desenhados como uma sequência de perguntas objetivas:

| Gate              | Nome curto                               | Pergunta central                                                                                         |
|-------------------|-------------------------------------------|----------------------------------------------------------------------------------------------------------|
| S17A_T0_sanity    | Sanidade de ambiente backend             | O backend sobe, com dependências mínimas, no mesmo ambiente em que a UI roda?                           |
| S17A_T1_contracts | Contratos HTTP e tipos                   | O contrato HTTP/JSON de `/api/consultation` bate com os tipos da UI e com o domínio interno?            |
| S17A_T2_routing   | Roteamento, CORS e paths                 | A rota existe, responde no path e método corretos, com CORS OK para o frontend?                         |
| S17A_T3_happy     | Happy paths de consulta                  | Consultas simples funcionam end‑to‑end, com Debunker/Comitês/Âncoras bem acoplados?                     |
| S17A_T4_errors    | Erros e degradação controlada            | A API responde erros previsíveis e amigáveis, sem vazar detalhes internos, mesmo sob falha?             |
| S17A_T5_perf      | Performance e limites                    | Latência e payload da API são aceitáveis para a UI e estáveis sob carga leve?                           |
| S17A_T6_observab  | Observabilidade e rastreabilidade        | Logs, IDs de correlação e métricas permitem reconstituir uma consulta que falhou na UI?                 |
| S17A_T7_ci_repro  | CI e reprodutibilidade                   | Os checks da API rodam em CI e num clone limpo, sem depender de “config secreta na máquina do dev”?     |
| S17A_T8_go_no_go  | Decisão final da Sprint 17.1             | Com base em todos os gates acima, é seguro declarar GO/GO_WITH_RESTRICTIONS/NO_GO para a nova API?     |

Automação esperada:

- Scripts de gate: `bin/s17a_t0_sanity.sh` … `bin/s17a_t8_go_no_go.sh`.
- Orquestração: `bin/s17a_all_gates.sh`.
- Scorecards: `out/scorecards/S17A_T*.json`.
- Evidências: `out/evidence/S17A_T*_*/*`.
- CI: `.ci/sprint_17a_gates.yml` (PR/main) e `.ci/sprint_17a_nightly.yml` (rodadas diárias ou de acordo com o plano de CI).


## 2.3 Contrato de API que estamos protegendo

Antes de destrinchar cada gate, é fundamental explicitar o que estamos protegendo.

### 2.3.1 Contrato alto nível

A API de consulta oficial expõe:

- Endpoint: `POST /api/consultation`.
- Request: objeto compatível com `ConsultationRequest` da UI (Sprint 17):
  - Texto da pergunta em linguagem natural.
  - Metadados opcionais (domínio/categoria, idioma, flags de sensibilidade, etc.).
- Response: objeto compatível com `ConsultationResponse` da UI:
  - Resultado consolidado (verdade provável, classificação de risco, mensagem principal).
  - Lista de evidências (links, descrições, fontes, timestamps, tipos de evidência).
  - Campos de suporte à UX: mensagens amigáveis para incerteza, dados insuficientes e erros recuperáveis.

### 2.3.2 Integração com o domínio interno

Por baixo, o endpoint **não** inventa lógica própria. Ele deve orquestrar:

1) Debunker v1 (Sprint 15–16)

- Recebe a pergunta e consulta o Truth‑DB/índices existentes.
- Classifica risco (low/high/unknown) e anota `risk_flags`, recomendações e limitações.

2) Comitês V1/V2/V3

- Validam a coerência do resultado, executam múltiplos “cérebros” e um guardião de coerência.
- Decidem se é aceitável responder, se precisa ser mais conservador ou se deve recusar (no‑go de resposta).

3) Âncoras (anchors)

- Registram o hash da consulta e/ou do resultado em uma trilha de âncoras (chain client simulado/real).
- Fornecem material futuro para auditoria e contestação.

4) Anti‑canetada (commands)

- Garante que respostas não contornam os guardiões de integridade (não há “atajo” direto ao Truth‑DB).

Os gates de 17.1 garantem que essa composição exista, esteja sob contrato estável e seja observável.


## 2.4 Definição detalhada dos gates

### S17A_T0 — Sanidade de ambiente backend

**Pergunta**  
O backend de consulta sobe de forma previsível, com as dependências mínimas, no mesmo ambiente em que a UI roda?

**Entradas**

- Código em `inspectah/api.py`, `inspectah/explore/api.py` e módulos de domínio.
- Virtualenv `.venv` com `fastapi`, `uvicorn` e dependências básicas.
- Configuração mínima (via `.env`, `config.py` ou defaults) para ambiente local.

**Procedimento (script)**

- `PYTHONPATH=. bin/s17a_t0_sanity.sh` deve:
  - Ativar o venv (ou falhar com mensagem clara se não houver venv).
  - Iniciar o servidor com `python -m uvicorn inspectah.api:build_app --factory --port 8000` em modo smoke (curta duração).
  - Realizar um `GET /docs` ou `GET /openapi.json` para verificar que o app está de pé.

**Saídas / evidências**

- Scorecard: `out/scorecards/S17A_T0_sanity.json`.
- Logs de startup: `out/evidence/S17A_T0_sanity/uvicorn_startup.log`.

**Critério PASS**

- Servidor sobe sem exceções; `build_app()` não retorna `None`.
- `/docs` e `/openapi.json` respondem 200.
- Scorecard com `"status": "PASS"` e sem warnings críticos.


### S17A_T1 — Contratos HTTP e tipos (backend ↔ UI)

**Pergunta**  
O contrato HTTP/JSON de `/api/consultation` bate com o que a UI da Sprint 17 espera e com os objetos de domínio internos?

**Entradas**

- OpenAPI gerado em runtime: `http://localhost:8000/openapi.json`.
- Tipos da UI em `frontend/inspectah-ui/src/types/inspectah.ts`.
- Modelos pydantic/DataClasses do lado do backend.

**Procedimento**

- `bin/s17a_t1_contracts.sh` deve:  
  1) Baixar o OpenAPI (`curl` ou `python -m httpx`) e salvar em `out/evidence/S17A_T1_contracts/openapi.json`.  
  2) Rodar `python scripts/s17a_check_contracts.py` que:
     - Verifica se existe `POST /api/consultation` no OpenAPI.  
     - Compara o schema de request com a interface `ConsultationRequest` da UI.  
     - Compara o schema de response com `ConsultationResponse`, considerando nomes de campos, tipos primários, enums e nullability.
  3) Gera um relatório de diffs estruturais.

**Saídas / evidências**

- Scorecard: `out/scorecards/S17A_T1_contracts.json`.
- Relatório: `out/evidence/S17A_T1_contracts/contracts_report.json` com lista de divergências (se houver).

**Critério PASS**

- Endpoint `POST /api/consultation` presente e com método correto.  
- Nenhuma divergência estrutural (ex.: campo renomeado, removido ou tipo trocado).  
- Nenhuma propriedade “surpresa” que a UI desconhece se for indispensável para renderização.


### S17A_T2 — Roteamento, CORS e paths

**Pergunta**  
A rota existe, responde no path esperado e está liberada (via CORS) para o frontend de consulta?

**Entradas**

- Backend rodando em `http://localhost:8000`.
- Convenção de base URL da UI: `VITE_INSPECTAH_API_BASE_URL=http://localhost:8000`, path `/api/consultation`.

**Procedimento**

- `bin/s17a_t2_routing.sh` deve:
  - Enviar um `OPTIONS /api/consultation` simulando origem `http://localhost:5173`.  
  - Enviar um `POST /api/consultation` com payload mínimo válido.
  - Capturar status code, cabeçalhos e corpo (ou erro) para ambos.

**Saídas / evidências**

- Scorecard: `out/scorecards/S17A_T2_routing.json`.
- Logs HTTP: `out/evidence/S17A_T2_routing/http_probes.log`.

**Critério PASS**

- Nenhum 404/405/501 em `OPTIONS` ou `POST` para `/api/consultation`.  
- Cabeçalhos CORS permitem chamadas vindas da origem da UI.  
- Content‑Type e métodos permitidos estão corretos.


### S17A_T3 — Happy paths de consulta (end‑to‑end)

**Pergunta**  
Consultas típicas funcionam end‑to‑end, com Debunker, Comitês e Âncoras integrados, produzindo respostas coerentes com a UI?

**Entradas**

- Script de cenários: `scripts/s17a_happy_paths.py` com casos como:
  - `low_risk_case` (dado bem estabelecido).  
  - `high_risk_case` (fofoca ou alegação grave sem evidência).  
  - `unknown_case` (dados insuficientes ou conflituosos).

**Procedimento**

- `bin/s17a_t3_happy_path.sh` deve:
  - Postar os três cenários em `/api/consultation`.  
  - Validar:
    - HTTP 200.  
    - `riskLevel` consistente com o Debunker.  
    - Evidências retornadas quando aplicável.  
    - Mensagens amigáveis e formatadas de forma consistente com a UI (sem texto técnico cru).

**Saídas / evidências**

- Scorecard: `out/scorecards/S17A_T3_happy_path.json`.
- Respostas: `out/evidence/S17A_T3_happy_path/responses.json`.

**Critério PASS**

- Todos os cenários retornam 200 com payload válido.  
- Os três níveis de risco (baixo/alto/incerto) são demonstráveis e coerentes.  
- Não há divergências entre a lógica de Debunker/Comitês e o que a API expõe.


### S17A_T4 — Erros e degradação controlada

**Pergunta**  
Quando algo dá errado (inputs inválidos, falhas internas, timeouts), o backend responde de forma previsível, segura e amigável?

**Entradas**

- Script de injeção de falhas: `scripts/s17a_error_scenarios.py`.
- Hooks de simulação no Debunker, Comitês e Âncoras (quando necessário).

**Procedimento**

- `bin/s17a_t4_errors.sh` deve:
  - Exercitar:
    - Requisições inválidas (ausência de campos obrigatórios → 422 com payload de validação).  
    - Erros internos simulados (exceção em Debunker/Comitês).  
    - Timeout/indisponibilidade em Âncoras.
  - Verificar que:
    - Códigos HTTP são coerentes (400/422/500).  
    - Payload de erro segue formato padronizado (`message`, `error_code`, `request_id` opcional, etc.).  
    - Logs registram o erro com o mesmo `request_id` e sem vazar stacktrace bruto para o cliente.

**Saídas / evidências**

- Scorecard: `out/scorecards/S17A_T4_errors.json`.
- Logs: `out/evidence/S17A_T4_errors/backend_errors.log`.

**Critério PASS**

- Nenhum stacktrace completo ou detalhe sensível é enviado para o cliente.  
- Todos os cenários de erro têm comportamento definido, testado e documentado.  
- O padrão de mensagem de erro é estável para a UI.


### S17A_T5 — Performance e limites

**Pergunta**  
A API de consulta responde rápido o suficiente e com payload razoável para uso interativo pela UI?

**Entradas**

- Script de micro‑carga: `scripts/s17a_perf_smoke.py`.
- Limites de referência (local/dev):
  - p50 < 400 ms, p95 < 700 ms.  
  - Payload médio < ~100 kB.

**Procedimento**

- `bin/s17a_t5_perf.sh` deve:
  - Disparar N requisições (ex.: 50–100) distribuídas ao longo de alguns segundos.  
  - Medir latência p50/p95 e tamanho do body.

**Saídas / evidências**

- Scorecard: `out/scorecards/S17A_T5_perf.json`.
- Métricas: `out/evidence/S17A_T5_perf/metrics.json`.

**Critério PASS**

- p95 dentro do limite definido para ambiente local.  
- Nenhum erro 5xx durante o smoke.  
- Payload médio e máximo aceitáveis para a experiência da UI.


### S17A_T6 — Observabilidade e rastreabilidade

**Pergunta**  
Conseguimos rastrear qualquer consulta que a UI fizer, indo da tela até os logs e métricas do backend?

**Entradas**

- Convenção de IDs de correlação (`request_id`, `correlation_id`).
- Instrumentação de logs/metrics no backend (S15–S16).

**Procedimento**

- `bin/s17a_t6_observability.sh` deve:
  - Executar uma ou mais consultas reais em `/api/consultation`.  
  - Coletar logs e extrair:
    - `request_id`.  
    - Nível de risco.  
    - Status final (sucesso/erro).  
    - Metadados relevantes (origem UI, versão de API, etc.).
  - Verificar se as métricas (se existirem) registram contadores de requests/sucessos/erros.

**Saídas / evidências**

- Scorecard: `out/scorecards/S17A_T6_observability.json`.
- Logs: `out/evidence/S17A_T6_observability/consultation_logs.log`.

**Critério PASS**

- Cada requisição de consulta é rastreável por um ID único.  
- Logs permitem reconstruir o fluxo Debunker → Comitês → Âncoras para uma consulta específica.  
- Não há “buracos” de observabilidade entre UI e backend.


### S17A_T7 — CI e reprodutibilidade

**Pergunta**  
Os checks da API de consulta rodam em CI e num clone limpo, sem depender da máquina específica do dev?

**Entradas**

- Workflows de CI: `.ci/sprint_17a_gates.yml`, `.ci/sprint_17a_nightly.yml`.
- Scripts de automação: `bin/s17a_all_gates.sh`.

**Procedimento**

- `bin/s17a_t7_ci_and_repro.sh` deve:
  - Validar que os workflows chamam os scripts corretos (T0…T7).  
  - Simular um clone limpo (`Inspectah-s17a-clean`):
    - `python -m venv .venv`.
    - `pip install -r requirements*.txt` (ou equivalente).  
    - Execução de `PYTHONPATH=. bin/s17a_all_gates.sh`.

**Saídas / evidências**

- Scorecard: `out/scorecards/S17A_T7_ci_and_repro.json`.
- Manifesto: `out/evidence/S17A_T7_ci_and_repro/clone_manifest.json`.

**Critério PASS**

- CI verde, rodando os gates da API de forma consistente.  
- Clone limpo consegue rodar todos os gates sem passos manuais adicionais.  
- Não há dependências “fantasmas” (ex.: libs só instaladas na máquina local).


### S17A_T8 — Go/No‑Go da API de consulta

**Pergunta**  
Com todos os gates acima, é seguro declarar GO/GO_WITH_RESTRICTIONS/NO_GO para o endpoint `/api/consultation`?

**Entradas**

- Scorecards S17A_T0…S17A_T7.
- ORR summary da Sprint 17.1 (`docs/sprint_17a_orr_summary.md`).

**Procedimento**

- `bin/s17a_t8_go_no_go.sh` deve:
  - Ler todos os scorecards S17A_T*.
  - Gerar `out/scorecards/S17A_T8_go_no_go.json` com:
    - `commit_sha` (do commit final da 17.1).  
    - `decision` ∈ {`GO`, `GO_WITH_RESTRICTIONS`, `NO_GO`}.  
    - `restrictions` (lista textual, quando houver).  
    - ponteiros para evidências relevantes.
  - Em paralelo, gerar `out/evidence/S17A_T8_go_no_go/summary.json` com resumo legível da sprint.

**Critério de decisão**

- **GO**: todos os gates PASS, sem riscos críticos pendentes.  
- **GO_WITH_RESTRICTIONS**: existem limitações controladas (por exemplo, chain client ainda simulado) claramente documentadas.  
- **NO_GO**: qualquer gate crítico FAIL (rota inexistente, contrato divergente, erros descontrolados, ausência de CI) leva à decisão de não liberar a API para uso pela UI.


## 2.5 Mapa de risco → gate

Para evitar cegueira futura, explicitamos o mapeamento entre os erros recentes e os gates 17.1:

- **Rota inexistente / 404 em `/api/consultation`**  → S17A_T0, S17A_T2, S17A_T8.
- **Contrato implícito e divergente entre backend e UI**  → S17A_T1, S17A_T3, S17A_T4.
- **Erros genéricos e imprevisíveis (500 sem padrão)**  → S17A_T4, S17A_T6.
- **Comportamento só funcionando na máquina local**  → S17A_T7, S17A_T0.
- **Falta de rastro para debug entre UI e backend**  → S17A_T6.

Se qualquer um desses cenários reaparecer, a expectativa é que ao menos um gate 17.1 falhe de forma gritante, evitando que o problema seja descoberto só no navegador.


## 2.6 Resultado esperado deste capítulo

Quando todos os gates deste Capítulo 2 estiverem implementados e verdes:

- A UI da Sprint 17 fala com uma **API de consulta oficial, estável e versionada**.
- O bug original torna‑se quase impossível de reaparecer sem quebrar gates e CI.
- O caminho pergunta → Debunker → Comitês → Âncoras → resposta está observable e rastreável.
- A Sprint 17.1 passa a ser o **firewall de contrato** entre backend e frontend: se algo nesse contrato quebrar, a falha será detectada aqui, e não só pelo usuário.

Este Capítulo 2 torna a API de consulta um cidadão de primeira classe no Inspectah, com os mesmos padrões de rigor que já aplicamos às sprints de backend (S10–S16) e agora estendidos à camada de contrato público com a UI.

