# Sprint 17.1 — API de Consulta v1 (ponte oficial entre motor e UI)

## 1. Contexto e problema que esta sprint resolve

Após as Sprints 15, 16 e 17, o Inspectah está num estado curioso:

- **S15/S16** entregaram o "motor" de verdade:
  - Debunker v1 com fixtures para domínios como política, fofoca, esporte, clima, mandatos, projetos, ciência, etc.
  - Comitês V1/V2/V3 fazendo validação mecânica, painel multibrain e checagem de coerência.
  - Âncoras e Anti-canetada protegendo caminho de escrita e registrando tentativas de fraude.
- **S17** entregou a **UI de consulta**:
  - Frontend React/TS (Vite + Tailwind) em `frontend/inspectah-ui/` com página de consulta simples e elegante.
  - Hook `useConsultation`, cliente HTTP, tipos e testes (Vitest + RTL) modelando exatamente o que a UI espera receber de volta.

Entre esses dois mundos, porém, existe um **gap estrondoso**:

- Não há uma **API de Consulta v1 oficial** no backend.
- A UI sabe “como deveria ser" o contrato (via tipos TS e mocks), mas o backend ainda não oferece esse contrato de forma canônica.
- O app FastAPI atual expõe `explore` (
  `GET /explore/items`, `GET /explore/sources`), mas não expõe um endpoint real de consulta consolidada (`POST /api/consultation` ou equivalente) que ligue UI → Debunker/Comitês/Âncoras.

Essa sprint existe para **corrigir isso de forma definitiva**, sem gambiarra nem workaround: transformar a **Consulta** em conceito de primeira classe no backend, com contrato estável, testes, gates e ORR.

---

## 2. Objetivo central da Sprint 17.1

**Entregar a Inspectah Consultation API v1**, composta por:

1. Uma **camada de domínio de Consulta** no backend, responsável por:
   - Entender uma pergunta em linguagem natural.
   - Identificar domínio/tema relevante.
   - Orquestrar Debunker, Comitês e, quando fizer sentido, Âncoras/Anti-canetada.
   - Consolidar uma única resposta com:
     - Resumo (answer/summary),
     - Nível de risco,
     - Evidências principais,
     - Metadados e flags de segurança.

2. Um **endpoint HTTP oficial** (v1) que:
   - Seja exposto via FastAPI no app principal (ex.: `POST /api/consultation`).
   - Use modelos Pydantic alinhados 1:1 com os tipos TypeScript da Sprint 17.
   - Apareça em `/docs` e em `/openapi.json` com schemas claros e utilizáveis.

3. **Testes e gates automatizados** que garantam que:
   - O fluxo UI → API → Debunker/Comitês → resposta funciona ponta-a-ponta, sem mocks.
   - O contrato retornado pelo backend é compatível com o que a UI espera (campos, tipos, semântica básica).

4. **Documentação e ORR específicos da Consulta v1**, registrando:
   - Arquitetura e filemap da camada de consulta.
   - Contrato HTTP oficial da API de Consulta v1.
   - Limitações conhecidas (domínios suportados, latência esperada, etc.).
   - Decisão GO/GO_WITH_RESTRICTIONS/NO_GO da própria sprint 17.1.

**Regra de ouro desta sprint:**
> Ao final da Sprint 17.1, qualquer pessoa deve conseguir subir o backend, subir a UI da S17, fazer uma pergunta real e receber uma resposta consolidada com risco + evidências, vinda do motor do Inspectah (sem mocks), com tudo coberto por testes, gates e documentação.

---

## 3. Escopo (IN / OUT)

### 3.1. Escopo IN — o que esta sprint entrega

1. **Camada de domínio "Consulta" no backend**

Criação de um módulo explícito em `inspectah/` (nome sugerido: `inspectah/consultation/`), contendo:

- **Modelos de domínio** (internos):
  - `ConsultationRequest`: texto da pergunta, contexto opcional, domínio/alvo opcional, `expected_risk` opcional, etc.
  - `ConsultationResult`: `request_id`, `risk_level`, resumo/answer, lista de evidências estruturadas, flags e metadados.
- **Serviço de consulta** responsável por:
  - Mapear pergunta → domínio (política, fofoca, esporte, clima, mandatos, projetos, ciência, etc.).
  - Selecionar as fixtures/regras apropriadas do Debunker.
  - Invocar Comitês (V1/V2/V3) de forma consistente, aplicando as mesmas políticas de hardening da S16.
  - Consolidar o resultado em um objeto único de `ConsultationResult` com:
    - Nível de risco coerente,
    - Evidências prioritárias,
    - Flags/justificativas (por exemplo, quando a resposta é "unknown" por falta de evidências).

2. **API HTTP de Consulta v1 (endpoint oficial)**

- Implementar um router FastAPI dedicado à Consulta v1 (por exemplo, `inspectah/ui/api.py` ou `inspectah/consultation/api.py`).
- Expor pelo menos um endpoint v1, com path e contrato alinhados à S17, por exemplo:
  - `POST /api/consultation`
    - Request: JSON compatível com `ConsultationRequest` TypeScript atual.
    - Response: JSON compatível com `ConsultationResponse` TypeScript atual.
- Integrar o router no app principal em `inspectah/api.py`, ao lado do router de `explore`.
- Garantir que o contrato esteja visível em `/docs` e `/openapi.json` com schemas descritivos (nomes de campos, tipos, explicações básicas).

3. **Alinhamento fino contrato UI ↔ backend**

- Ler os arquivos reais da UI:
  - `frontend/inspectah-ui/src/types/inspectah.ts`
  - `frontend/inspectah-ui/src/api/inspectahClient.ts`
  - `frontend/inspectah-ui/src/hooks/useConsultation.ts`
  - Testes em `frontend/inspectah-ui/src/__tests__/*.test.tsx`
- Garantir que o backend retorne exatamente o que o front espera:
  - Mesmo nome de propriedades (`riskLevel`, `requestId`, `summary`, `evidence`, etc.).
  - Mesmo conjunto de valores permitidos para risco (`"low"`, `"high"`, `"unknown"`, etc., conforme tipos reais).
  - Sem necessidade de remendar o front da S17 — a sprint 17.1 ajusta o backend para honrar o contrato firmado pela UI.

4. **Testes de backend específicos da consulta**

- Testes de domínio (`tests/test_consultation_service_*.py`):
  - Cenário de baixo risco (ex.: clima) → resultado com `risk_level` baixo, resposta coerente, evidências suficientes.
  - Cenário de alto risco (ex.: escândalo político sensível) → `risk_level` alto, exigência de evidências fortes, comportamento conservador.
  - Cenário incerto/insuficiente → `risk_level` adequado (por exemplo, `unknown`) + mensagem clara de limitação.
- Testes de API (`tests/test_consultation_api_*.py`):
  - Exercitar `POST /api/consultation` com payloads representativos.
  - Verificar status HTTP, shape do JSON, presença de campos obrigatórios, consistência mínima (evidências não vazias quando esperadas, requestId presente, etc.).

5. **Gates e scripts de integração**

- Criar (ou reforçar) gates específicos para esta sprint, por exemplo:
  - Um gate que sobe a app FastAPI (ou a usa em memória via TestClient) e faz smoke tests em `POST /api/consultation` com payload real.
  - Um gate que valida o contrato JSON retornado contra um schema (ou contra um fixture de resposta esperada).
- Integrar esses gates na esteira:
  - Mantendo T0–T8 das sprints anteriores intactos.
  - Adicionando gates dedicados da sprint 17.1, ou fortalecendo o papel de S17_T3_api_integration para depender da API real.

6. **Documentação e ORR da Sprint 17.1**

- Criar docs específicos, seguindo o padrão do projeto:
  - `docs/sprint_17_1_overview.md`: contexto, objetivos, escopo, entregáveis.
  - `docs/sprint_17_1_filemap_e_arquitetura.md`: módulos, fluxo HTTP → domínio → Debunker/Comitês/Âncoras.
  - `docs/sprint_17_1_orr_summary.md`: Gate × Status, SHA final, decisão, restrições, referências a scorecards e evidências.
- Atualizar, se necessário, o ORR da S17 para referenciar a existência da API de Consulta v1 como parte da solução final.

---

### 3.2. Escopo OUT — o que esta sprint **não** faz

Para manter a sprint focada e sanidade alta, esta sprint **não** irá:

- Criar novas UIs (console/admin, timeline/raio-X, dashboards, etc.).
- Implementar autenticação/autorização de usuários finais (isso é assunto das sprints de auth).
- Integrar com provedores reais de blockchain/chain; a camada de chain permanece no regime definido na S16 (cliente simulado + falhas controladas), salvo ajustes mínimos de interface com a consulta.
- Expandir o Debunker/Comitês em escopo massivo — apenas ajustes pontuais que forem estritamente necessários para suportar a Consulta v1.
- Definir políticas de versionamento público da API a longo prazo (v2, breaking changes, deprecation policy). A v1 é o foco.

---

## 4. Interfaces e contratos chave

### 4.1. Contrato HTTP v1 (visão conceitual)

A Sprint 17.1 definirá, implementará e testará um contrato HTTP v1 com pelo menos:

- **Endpoint principal:**
  - `POST /api/consultation`
- **Request (conceitual):**
  - Texto da pergunta em linguagem natural.
  - Campos opcionais de contexto/domínio/tags.
  - Campo opcional `expected_risk` (se o chamador quiser sinalizar sensibilidade).
- **Response (conceitual):**
  - `requestId`: identificador único da consulta.
  - `riskLevel`: nível de risco consolidado.
  - `summary`/`answer`: resposta em linguagem natural, breve, direta.
  - `evidences`/`evidence`: lista de evidências com origem, descrição/snippet e, se possível, link.
  - `meta`/`flags`: informações adicionais (por exemplo, quando o motor está sendo conservador por falta de dados).

Os nomes finais de campos não serão inventados neste macro — serão **derivados dos tipos TypeScript já existentes** na S17, para garantir que o contrato seja realmente 1:1.

### 4.2. Integração com Debunker/Comitês/Âncoras

A API de Consulta v1 não vai reinventar a roda; ela será uma **orquestração disciplinada** do que já existe:

- Debunker continua fazendo a leitura/normalização/checagem de evidências por domínio.
- Comitês continuam avaliando:
  - V1: regras mecânicas básicas.
  - V2: painel multibrain.
  - V3: coerência global.
- Âncoras/Anti-canetada continuam protegendo o caminho de escrita e garantindo que nada seja “enfiado à força” sem passar pelos comitês.

A sprint 17.1 garante que **Consulta** sabe como conversar com esses módulos e traduzir o resultado em termos que a UI e os consumidores externos entendem.

---

## 5. Entregáveis principais

1. **Módulo de domínio de Consulta** em `inspectah/consultation/` (ou equivalente), com:
   - Modelos de domínio.
   - Serviço de orquestração.
   - Pontos de extensão para crescimento futuro (novos domínios, novas políticas de risco, etc.).

2. **Endpoint HTTP v1 funcionando** em `POST /api/consultation`, exposto pelo app FastAPI principal:
   - Com request/response alinhados à UI da S17.
   - Visível em `/docs` e `/openapi.json`.

3. **Testes de backend para Consulta** cobrindo:
   - Serviço de domínio.
   - Endpoint HTTP.
   - Casos de baixo/alto risco e casos incertos/insuficientes.

4. **Gates e scripts**:
   - Script(s) de smoke para `POST /api/consultation`.
   - Gates que falham se o endpoint não existir, estiver quebrado ou retornar JSON incompatível.

5. **Documentação e ORR da Sprint 17.1**:
   - Overview.
   - Filemap + Arquitetura.
   - ORR Summary com SHA, Gate × Status e decisão final.

---

## 6. Definition of Done (macro) da Sprint 17.1

A sprint 17.1 só é considerada concluída quando **todas** as condições abaixo forem verdadeiras:

1. **Fluxo ponta-a-ponta funcional (sem mocks)**
   - Backend:
     - `cd /Users/gustavoschneiter/Documents/Inspectah`
     - `source .venv/bin/activate`
     - `PYTHONPATH=. python -m uvicorn inspectah.api:build_app --factory --reload --port 8000`
   - Frontend:
     - `cd frontend/inspectah-ui`
     - `npm ci`
     - `npm run dev`
   - Ao acessar `http://localhost:5173` e enviar uma pergunta:
     - A UI recebe resposta de verdade (HTTP 200, sem 404/500).
     - Nível de risco, resumo e evidências são exibidos.
     - Logs do backend mostram a passagem pela camada de Consulta e, quando aplicável, por Debunker/Comitês.

2. **Testes de backend passando**
   - `cd /Users/gustavoschneiter/Documents/Inspectah`
   - `source .venv/bin/activate`
   - `PYTHONPATH=. pytest` (ou comando equivalente definido).
   - Nenhum teste de consulta falhando; cobertura mínima aceitável em módulos novos.

3. **Gates específicos da sprint 17.1 passando**
   - Gates que exercitam `POST /api/consultation` passam localmente e no CI.
   - Qualquer gate da S17 que dependa da API (por exemplo, integração) passa usando a API real.

4. **Documentação atualizada e sem TODOs**
   - Docs da sprint 17.1 estão presentes, sem seções em branco ou placeholders.
   - ORR da sprint 17.1 contém:
     - Tabela Gate × Status.
     - SHA final.
     - Decisão (GO ou GO_WITH_RESTRICTIONS bem justificada se houver).
   - Se necessário, ORR da S17 faz referência clara à API de Consulta v1.

5. **Repositório limpo e consistente**
   - `git status` limpo na raiz do Inspectah após rodar todos os comandos da sprint.
   - Todos os scripts/gates/evidências previstos na documentação existem e rodam como descrito.

---

## 7. Riscos e mitigação

1. **Risco: over-engineering da v1 de consulta**
   - *Perigo:* tentar abraçar todos os domínios, políticas e exceções logo na v1.
   - *Mitigação:* definir claramente um conjunto inicial de domínios bem suportados e documentar as limitações da v1. Para casos fora desse conjunto, usar um caminho explícito para `unknown` com mensagem honesta.

2. **Risco: divergência entre TypeScript e Pydantic**
   - *Perigo:* contrato HTTP "parecido" mas não idêntico ao que a UI espera (field faltando, nome diferente, enum divergente).
   - *Mitigação:* backend lê tipos TS existentes como fonte de verdade para o contrato. Testes de integração validam o JSON completo, e testes de front seguem rodando acima disso.

3. **Risco: acoplamento excessivo com fixtures/implementação interna do Debunker**
   - *Perigo:* contrato v1 ficar amarrado demais à forma atual dos fixtures, dificultando evolução do motor.
   - *Mitigação:* encapsular interação com Debunker no serviço de consulta, mantendo uma interface de domínio estável. Alterações internas em Debunker não quebram a API.

4. **Risco: latência alta ou respostas muito grandes**
   - *Perigo:* experiência ruim na UI, tempo de resposta imprevisível.
   - *Mitigação:* medir latência da chamada de consulta (via testes/gates) e limitar número de evidências retornadas por padrão, documentando o comportamento.

---

## 8. Como esta sprint fortalece o DNA do Inspectah

A Sprint 17.1 não é apenas uma correção técnica; ela cristaliza no DNA do projeto algumas regras permanentes:

- **Nenhuma UI nova nasce sem um backend formalmente definido.**
  - Sempre que uma UI depender de um endpoint ainda inexistente, esse endpoint deve ser objetivo explícito de sprint, com Capítulos 1–4 e ORR.

- **Contratos entre camadas são cidadãos de primeira classe.**
  - Não basta o motor ser correto e a UI ser bonita; o contrato entre os dois precisa ter sprint, filemap, testes, gates e ORR.

- **Consulta vira conceito de domínio, não apenas um formulário.**
  - A partir daqui, "Consulta" passa a existir como módulo, serviço e contrato, servindo de base para futuras superfícies (console admin, timeline, API pública, SDK, etc.).

Em resumo, a Sprint 17.1 é a peça que faz o Inspectah parar de ser um conjunto de motores poderosos + uma UI bonita, e passar a ser um **serviço de consulta coeso**, com começo, meio e fim bem definidos na arquitetura.

