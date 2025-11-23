# Sprint 17.1 — Capítulo 3  
Arquitetura, Filemap e Fluxos da API Oficial de Consulta

---

## 1) Objetivo do Capítulo 3

Este capítulo consolida, em nível **arquitetural e operacional**, tudo que a Sprint 17.1 precisa para transformar a API de consulta em uma **peça de primeira classe** do Inspectah:

- Onde o código vive (filemap completo, sem zonas cinzentas).
- Como as camadas se relacionam (HTTP ↔ orquestração ↔ Debunker ↔ Comitês ↔ UI).
- Como os fluxos de dados funcionam, do ponto de vista de contrato, estados e falhas.
- Como isso se ancora nos **gates** definidos no Capítulo 2 (T0…T8) sem deixar espaço para improviso.

O resultado é um blueprint que permite ao Codex implementar a sprint sem inventar nada fora do escopo, mantendo alinhamento estrito com:

- S15: Debunker v1 e Comitês v1/v2/v3.
- S16: Threat Model, hardening e políticas de risco.
- S17: UI de consulta do Inspectah (frontend).

---

## 2) Arquitetura lógica da API de Consulta

### 2.1 Camadas e responsabilidades

A API de consulta é organizada em cinco camadas bem separadas e explicitamente mapeadas para os gates da sprint:

1. **Camada HTTP (FastAPI)**  
   Responsável por:
   - Expor a rota `POST /api/consultation`.
   - Validar e desserializar o payload de entrada (`ConsultationRequest`).
   - Serializar a resposta (`ConsultationResponse` ou `ConsultationErrorResponse`).
   - Publicar o contrato no OpenAPI (`/openapi.json`, `/docs`).
   - Garantir códigos HTTP coerentes com o Threat Model (S16) e com a UX da S17.

2. **Camada de Orquestração de Consulta**  
   - Implementa o fluxo de alto nível da consulta.
   - Invoca Debunker e Comitês na ordem correta, aplicando regras de negócio de S15/S16:
     - risco esperado (quando vier do chamador),
     - tratamento de alto risco sem evidência,
     - coerência final da resposta.
   - Mantém invariantes claros (documentados mais abaixo) sobre o que significa uma resposta "ok".

3. **Camada de Domínio da Consulta (modelos)**  
   - Define modelos Pydantic e enums específicos para a API de consulta:
     - `ConsultationRequest`
     - `ConsultationResponse`
     - `ConsultationEvidence`
     - `RiskLevel` (enum)
     - `ConsultationErrorResponse`
   - Mantém estes modelos **separados** dos modelos internos da TruthDB, funcionando como uma “fachada” estável para clientes externos (UI, automações, integrações futuras).

4. **Adaptadores para Debunker / Comitês**  
   - Traduzem entre o formato de domínio da consulta e o formato esperado pelos componentes core:
     - Debunker (`inspectah.debunker.engine`, `report_models`).
     - Comitês (`inspectah.committees.*`).
   - Encapsulam detalhes como:
     - seleção de domínio(s) adequados (fofoca, esporte, clima, mandatos, política, projetos, ciência, etc.),
     - combinação de múltiplos relatórios em uma visão única para o usuário,
     - aplicação das políticas de `risk_flags` e rejeição de alto risco sem evidência.

5. **Camada de Observabilidade da Consulta**  
   - Padroniza logs estruturados para o ciclo de vida da consulta:
     - início (`consultation_started`),
     - sucesso (`consultation_succeeded`),
     - falha (`consultation_failed`).
   - Usa um `request_id` propagado ponta-a-ponta (HTTP ↔ Debunker ↔ Comitês ↔ logs),
   - Facilita o mapeamento com os gates T6 (observabilidade) e com watchers/monitores futuros.

Essa separação reforça diretamente os gates:

- T1 (contracts and states) foca na camada de domínio e no acoplamento com HTTP.
- T2/T3/T4 focam na orquestração + adaptadores Debunker/Comitês + cenários canônicos.
- T5 foca em custo/performance da rota.
- T6 foca na camada de observabilidade.

### 2.2 Invariantes da API de Consulta

A equipe reforça os seguintes **invariantes mínimos** para a rota `/api/consultation`:

- Toda resposta **bem sucedida** deve conter:
  - `request_id` não vazio,
  - `answer` textual não vazia (salvo no caso de dados insuficientes, onde o texto explicita isso),
  - `risk_level` em `{"low", "medium", "high", "unknown"}`,
  - lista de `evidences` (pode ser vazia, mas nunca `null`).

- Em caso de erro tratado (ex.: backend indisponível), a API deve retornar:
  - status HTTP ≥ 500,
  - um `ConsultationErrorResponse` com código de erro estável (`code`) e mensagem amigável (`message`).

- Em caso de erro de validação (payload inválido):
  - status HTTP 4xx apropriado (ex.: 422),
  - corpo no formato `ConsultationErrorResponse` ou mapeamento compatível com a UX.

Esses invariantes são cobrados diretamente nos testes e gates de T1, T2, T3 e T4.

### 2.3 Relação com artefatos S15–S17

- **S15 — Debunker + Comitês + Âncoras**  
  A Sprint 17.1 não reimplementa lógica de risco. Ela **consome**:
  - engine do Debunker (`inspectah.debunker.engine`),
  - modelos de relatório (`inspectah.debunker.report_models`),
  - comitês (`v1_validator`, `v2_multibrain`, `v3_coherence`),
  - políticas de anti-canetada nas writes (quando aplicável ao fluxo de consulta).

- **S16 — Threat Model e Hardening**  
  A API de consulta respeita o Threat Model de S16:
  - protege contra entradas maliciosas (strings arbitrárias, inputs gigantes, payloads estranhos),
  - favorece respostas conservadoras em situações de incerteza ou comportamento inesperado dos componentes internos,
  - expõe sinais de risco de forma clara para a UI.

- **S17 — UI de Consulta**  
  O contrato `/api/consultation` é desenhado de trás para frente a partir da UI:
  - tipos em `frontend/inspectah-ui/src/types/inspectah.ts` são compatíveis 1:1 com os modelos de backend;
  - o fluxo do hook `useConsultation` (idle → submitting → success/error) é diretamente mapeável nos códigos HTTP e estruturas de resposta do backend.

---

## 3) Filemap detalhado da Sprint 17.1

### 3.1 Documentação

Todos os documentos da Sprint 17.1 ficam na raiz do repositório, em `docs/` e `Sprint 17.1/`:

- `Sprint 17.1/Capitulo 1.md`  
  Visão de produto/escopo da sprint (contexto, objetivos, não-escopo, riscos).

- `Sprint 17.1/Capitulo 2.md`  
  Gates T0…T8, critérios de PASS/FAIL, entradas/saídas por gate.

- `Sprint 17.1/Capitulo 3.md`  
  Este arquivo: arquitetura, filemap, fluxos de dados.

- `Sprint 17.1/Capitulo 4.md`  
  Instruções de execução orientadas ao Codex (como criar/alterar cada arquivo, como rodar gates, etc.).

- `docs/sprint_17_1_overview.md`  
  Resumo executivo da sprint, alinhado ao Capítulo 1.

- `docs/sprint_17_1_filemap_e_arquitetura.md`  
  Versão "para operador" deste capítulo, com foco em runbook e navegação do repo.

- `docs/sprint_17_1_orr_summary.md`  
  Gate × Status, artefatos principais, riscos, próximos passos, adendo final com SHA e decisão GO/GO_WITH_RESTRICTIONS/NO_GO.

### 3.2 Backend — módulo principal de API

- `inspectah/api.py`

Responsabilidades:

- Definir a aplicação FastAPI principal via `build_app()`.
- Incluir:
  - o router existente de `/explore` (D8),
  - o novo router de `/api/consultation`.

Esqueleto recomendado:

```python
from fastapi import FastAPI

from .explore.api import build_router as build_explore_router
from .ui.consultation_api import router as consultation_router


def build_app():
    app = FastAPI(title="Inspectah API")

    explore_router = build_explore_router()
    if explore_router is not None:
        app.include_router(explore_router, prefix="/explore", tags=["explore"])

    app.include_router(consultation_router, prefix="/api", tags=["consultation"])
    return app
```

Esse desenho garante que o endpoint de exploração D8 continue funcionando e que a nova API de consulta fique claramente separada, com seu próprio namespace.

### 3.3 Backend — camada de UI de consulta

Nova pasta (já existente no repo, mas agora formalizada como “lugar oficial” da API de consulta no backend):

- `inspectah/ui/__init__.py`  
  Mantido mínimo, servindo como ponto de agregação para componentes de UI backend.

- `inspectah/ui/consultation_models.py`  
  Contém os modelos Pydantic da API de consulta:

  - `ConsultationRequest`
    - `question: str`
    - `context: Optional[str] = None`
    - `expected_risk: Optional[str] = None` (alinhado com Debunker/Comitês quando o chamador já tem uma expectativa de risco).

  - `RiskLevel` (enum)
    - valores esperados: `"low"`, `"medium"`, `"high"`, `"unknown"`.

  - `ConsultationEvidence`
    - `id: str`
    - `source_name: str`
    - `source_type: str`
    - `url: Optional[str]`
    - `excerpt: Optional[str]`
    - `score: Optional[float]`

  - `ConsultationResponse`
    - `request_id: str`
    - `answer: str`
    - `risk_level: RiskLevel`
    - `short_summary: str`
    - `evidences: list[ConsultationEvidence]`
    - `notes: Optional[str]`

  - `ConsultationErrorResponse`
    - `code: str` (por exemplo: `"backend_unavailable"`, `"validation_error"`, `"unknown_error"`)
    - `message: str`

Observação importante: esses modelos devem estar sincronizados com `frontend/inspectah-ui/src/types/inspectah.ts` para evitar drift de contrato (Gate T1). A Sprint 17.1 inclui testes específicos comparando campos críticos entre backend e frontend.

- `inspectah/ui/consultation_service.py`  
  Camada de **orquestração de consulta**.

  Função core sugerida:

  ```python
  def run_consultation(request: ConsultationRequest) -> ConsultationResponse:
      ...
  ```

  Responsabilidades principais:

  - normalizar input (trimming, limites de tamanho, saneamento básico de texto),
  - decidir quais domínios do Debunker serão utilizados para a pergunta,
  - chamar Debunker e obter um `DebunkerReport`,
  - chamar Comitês v1/v2/v3 com o contexto produzido,
  - aplicar as políticas de risco (especialmente alto risco sem evidência),
  - construir `ConsultationResponse` com:
    - resposta final para o usuário,
    - nível de risco consolidado,
    - evidências ordenadas por relevância,
    - notas adicionais (por exemplo, "dados insuficientes").

  Funções auxiliares (nomes indicativos):

  - `map_debunker_to_consultation(...)`
  - `apply_committees_policies(...)`
  - `build_evidences_from_report(...)`

- `inspectah/ui/consultation_api.py`  
  Router FastAPI dedicado à API de consulta.

  - Cria um `APIRouter()` com prefixo `/consultation`.
  - Define:
    - `POST /consultation`
      - `request: ConsultationRequest`
      - `response: ConsultationResponse`
      - erros mapeados para `ConsultationErrorResponse` com HTTP status adequado.
  - Usa a camada de observabilidade para logar início, sucesso e falha.

- `inspectah/ui/consultation_observability.py`  
  - Exporta funções:
    - `log_consultation_started(...)`
    - `log_consultation_succeeded(...)`
    - `log_consultation_failed(...)`
  - Define o formato padrão de log (campos como `request_id`, `risk_level`, `error_type`, timestamps), alinhado com a telemetria de S16/S17.

### 3.4 Backend — integração com Debunker e Comitês

Arquivos já existentes, mas explicitamente usados pela Sprint 17.1:

- `inspectah/debunker/engine.py`  
  Fornece a função principal de análise (por exemplo, `run_debunker(...) -> DebunkerReport`).

- `inspectah/debunker/report_models.py`  
  Define as estruturas de relatório que serão consumidas por `consultation_service.py`.

- `inspectah/debunker/rules.py`  
  Contém regras que ajudam a decidir risco, flags, etc.

- `inspectah/committees/common.py`  
  Funções utilitárias que unem Debunker e Comitês.

- `inspectah/committees/v1_validator.py`  
  Primeira linha de validação mecânica da proposta de resposta.

- `inspectah/committees/v2_multibrain.py`  
  Painel multibrain e políticas de rejeição de alto risco sem evidência, além de metadados sobre risco.

- `inspectah/committees/v3_coherence.py`  
  Guarda de coerência da resposta consolidada.

A Sprint 17.1 não deve alterar a semântica destes componentes (a menos que explicitamente pedido em gates específicos). Ela os **consome** via adaptadores na camada de orquestração da consulta.

### 3.5 Testes automatizados backend

Para sustentar os gates e evitar regressões silenciosas, a Sprint 17.1 define a seguinte estrutura mínima de testes:

- `tests/test_consultation_api_contract.py`
  - Testa o contrato HTTP de `/api/consultation` com `TestClient` (FastAPI):
    - caminho feliz com risco baixo/médio,
    - alto risco com evidência suficiente,
    - alto risco sem evidência (resposta deve refletir política de S16),
    - caso de dados insuficientes (risk_level `"unknown"` e mensagem amigável),
    - erros de validação de entrada.

- `tests/test_consultation_service_integration.py`
  - Testa a integração da orquestração com Debunker e Comitês (com mocks quando necessário):
    - cenários core mapeados nos gates T2/T3/T4 (goldens de risco e evidência),
    - tratamento de exceções internas (timeouts/erros inesperados).

- `tests/test_consultation_models.py`
  - Garante que os modelos Pydantic:
    - serializam/desserializam corretamente,
    - mantêm compatibilidade com os tipos da UI (ao menos em campos chave e enums),
    - respeitam restrições básicas de tamanho/formatos.

Esses testes são conectados diretamente aos gates T1, T2, T3 e T4.

### 3.6 Scripts de gates e scorecards

Mesmo sendo uma sprint "17.1", seguimos o padrão de gates da esteira:

- Scripts de gate:
  - `bin/s17_1_t0_sanity.sh`
  - `bin/s17_1_t1_contracts_and_states.sh`
  - `bin/s17_1_t2_golden_flows.sh`
  - `bin/s17_1_t3_debunker_and_committees_integration.sh`
  - `bin/s17_1_t4_error_and_edge_cases.sh`
  - `bin/s17_1_t5_performance_and_cost.sh`
  - `bin/s17_1_t6_observability_and_logging.sh`
  - `bin/s17_1_t7_ci_and_repro.sh`
  - `bin/s17_1_t8_go_no_go.sh`

- Orquestrador:
  - `bin/s17_1_all_gates.sh`

- Scorecards:
  - `out/scorecards/S17_1_T0_sanity.json`
  - …
  - `out/scorecards/S17_1_T8_go_no_go.json`

- Evidências:
  - `out/evidence/S17_1_T0_sanity/*`
  - …
  - `out/evidence/S17_1_T7_ci_and_repro/*`

O Capítulo 2 define a semântica destes gates; aqui apenas fixamos **onde** os scripts, scorecards e evidências vivem.

### 3.7 CI e pipelines

- `.ci/sprint_17_1_gates.yml`
  - Roda T0–T4 em PR/main, garantindo que mudanças na API de consulta não quebrem contrato/fluxos principais.

- `.ci/sprint_17_1_nightly.yml`
  - Roda T2–T6 em cadência diária, cobrindo:
    - cenários de ataque,
    - integrações Debunker/Comitês,
    - observabilidade,
    - performance básica.

Esses workflows seguem o padrão das Sprints 15–17, com nomes de jobs, passos e artefatos alinhados.

---

## 4) Fluxos de dados principais

### 4.1 Fluxo feliz — consulta com evidência sólida e risco baixo/médio

1. A UI envia `POST` para `http://<base>/api/consultation` com um `ConsultationRequest` válido.
2. A camada HTTP valida o payload (Pydantic) e instancia `ConsultationRequest`.
3. `consultation_service.run_consultation()` é chamado com o request.
4. A orquestração:
   - normaliza a pergunta/contexto,
   - chama Debunker, obtendo um `DebunkerReport`,
   - aciona Comitês v1/v2/v3 para sanity, multibrain e coerência,
   - converte tudo em `ConsultationResponse`.
5. A camada HTTP retorna `200 OK` com `ConsultationResponse` em JSON.
6. A camada de observabilidade registra logs `consultation_started` e `consultation_succeeded` com `risk_level` final.

### 4.2 Fluxo de backend indisponível (Debunker/Comitês com erro)

1. A UI envia `POST /api/consultation` normalmente.
2. Durante a orquestração, Debunker ou Comitês lançam exceção (timeout, erro interno, etc.).
3. `run_consultation()` captura a exceção e a traduz em uma falha conhecida.
4. A camada HTTP devolve um `ConsultationErrorResponse` com status `503 Service Unavailable` (ou equivalente), e mensagem amigável.
5. Logs estruturados registram `consultation_failed` com `error_type`, `stack_hint` (quando seguro) e `request_id`.

### 4.3 Fluxo de “dados insuficientes / alta incerteza”

1. Debunker conclui que não há evidência suficiente ou que as fontes entram em conflito forte.
2. Comitês confirmam incerteza e reforçam política de resposta conservadora.
3. A orquestração monta `ConsultationResponse` com:
   - `risk_level = "unknown"` (ou equivalente),
   - `answer` deixando claro que a informação não é conclusiva,
   - `evidences` contendo o que foi possível agregar,
   - `notes` com orientação ao usuário.
4. A UI exibe um estado específico para incerteza (já desenhado na S17), sem mascarar o fato de que os dados são fracos.

### 4.4 Fluxo de input inválido

1. A UI ou cliente externo envia um payload inválido (campos faltando, tipos errados, tamanhos excessivos).
2. Pydantic identifica o erro e FastAPI retorna `422 Unprocessable Entity` ou outro status definido, com `ConsultationErrorResponse` aderente ao Gate T1.
3. Logs registram `consultation_failed` com `error_type="validation_error"` e metadados mínimos para diagnóstico.

---

## 5) Integração com a UI e Threat Model

### 5.1 UI de consulta (S17)

- O hook `useConsultation` e os componentes `ConsultationForm`, `ResultContainer`, `RiskBadge` e estados de erro/vazio são pensados para consumir diretamente o contrato de `/api/consultation`.
- A Sprint 17.1 garante, via testes de contrato, que:
  - `risk_level` e demais campos chegam na UI exatamente como definidos em `RiskLevel` e nos modelos de resposta;
  - mensagens de erro mapeiam corretamente para textos exibidos em tela;
  - estados de incerteza ("unknown") são diferenciados de falhas de backend.

### 5.2 Threat Model (S16)

- A API de consulta segue as recomendações de Threat Model:
  - limita tamanho de inputs (para evitar abusos de payload),
  - trata conteúdo inesperado como de risco elevado ou desconhecido,
  - não vaza detalhes internos sensíveis em mensagens de erro públicas,
  - registra logs suficientes para investigação futura sem comprometer segurança.

Esses pontos são exercitados explicitamente nos cenários dos gates T2, T4 e T6.

---

## 6) Notas finais para o Codex e para o operador

- A Sprint 17.1 não é um “remendo rápido”, mas a formalização da **API canônica de consulta** do Inspectah.
- O Capítulo 1 define o “porquê”; o Capítulo 2, o “como saber se está bom”; o Capítulo 3, o “como estruturar e onde colocar cada peça”.
- O Capítulo 4 fechará o ciclo com um passo a passo detalhado para o Codex criar/alterar os arquivos aqui descritos, rodar gates e produzir evidências e scorecards consistentes.

Com este capítulo, a equipe considera a arquitetura e o filemap da Sprint 17.1 em nível de maturidade suficiente para implementação direta, sem espaço para interpretações ambíguas ou soluções improvisadas fora do DNA do Inspectah.