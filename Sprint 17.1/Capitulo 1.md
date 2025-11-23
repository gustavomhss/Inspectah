# Sprint 17.1 — Capítulo 1
## API de Consulta v1 (ponte oficial entre motor e UI)

---

## 1. Contexto

Depois das Sprints 15, 16 e 17, o Inspectah chegou a um ponto muito poderoso e, ao mesmo tempo, com um buraco claro na arquitetura:

- **S15**: entregou o Debunker v1, com fixtures reais para domínios como política, fofoca, esporte, clima, mandatos, projetos, ciência etc., gerando relatórios estruturados, classificação de risco e um primeiro pipeline de julgamento.
- **S16**: fez o hardening do motor de verdade — Threat Model, comitês mais conservadores, âncoras e anti‑canetada mais robustas, logs de falhas de chain e decisões GO_WITH_RESTRICTIONS bem justificadas.
- **S17**: colocou no ar a primeira **UI de consulta** em `frontend/inspectah-ui/`:
  - Página de consulta em React/TS (Vite + Tailwind),
  - Hook `useConsultation`, cliente `inspectahClient`, componentes de estado (loading/erro/vazio/resultado),
  - Testes (Vitest + RTL) exercitando o fluxo do ponto de vista do usuário.

Na prática, porém, a arquitetura ficou assim:

- O **motor** sabe responder perguntas estruturadas (Debunker + Comitês + Âncoras),
- A **UI** sabe exibir uma resposta consolidada com risco e evidências,
- Mas **não existe uma API oficial de Consulta** ligando essas duas pontas.

O app FastAPI atual expõe apenas endpoints de exploração (`/explore/items`, `/explore/sources`), pensados para D8/DNA, e nenhum endpoint de consulta consolidada (`POST /api/consultation`) compatível com o contrato que a UI da S17 espera.

Resultado direto:

- O usuário vê uma interface bonita e funcional do ponto de vista de front‑end,
- Mas a requisição cai num 404/500, e o motor de verdade nunca é acionado.

Esta sprint existe para **corrigir esse gap de arquitetura de forma definitiva**, transformando "Consulta" em um conceito de primeira classe no backend e formalizando a **Inspectah Consultation API v1** como ponte oficial entre UI e motor.

---

## 2. Problema

### 2.1. Sintoma atual

Hoje, o fluxo real é:

1. A UI de consulta da S17 chama um endpoint configurado como `/api/consultation` (via `VITE_INSPECTAH_API_BASE_URL` + `VITE_INSPECTAH_CONSULT_PATH`).
2. Uvicorn/FastAPI sobem com sucesso (`inspectah.api:build_app`).
3. Mas **o endpoint real não existe**:
   - Não há rota registrada em `inspectah/api.py` para `/api/consultation`.
   - Não há modelos Pydantic específicos de consulta.
   - Não há integração com Debunker/Comitês/Âncoras para produzir a resposta esperada pela UI.

### 2.2. Impacto

- **Experiência do usuário**: qualquer tentativa de consulta real resulta em erro genérico:
  > "Não conseguimos falar com o Inspectah agora. Verifique sua conexão e tente de novo."
  
  Isso acontece mesmo com backend rodando, o que gera confusão e quebra de confiança.

- **Quebra de contrato entre camadas**:
  - A S17, na prática, definiu um contrato de `ConsultationRequest`/`ConsultationResponse` em TypeScript (`src/types/inspectah.ts` + testes),
  - O backend não implementa esse contrato em lugar nenhum.

- **Risco de padrão tóxico**:
  - Se esse comportamento for tolerado, abre‑se precedente para futuras UIs nascerem sem backend correspondente,
  - A esteira de produto passa a depender de mocks eternos, stubs frágeis e “remendos” em produção.

### 2.3. Root cause em termos de DNA

- S15/S16 focaram no **motor** e nas defesas (Debunker, Comitês, Âncoras, Threat Model).
- S17 focou na **UI de consulta**.
- A “ponte” — o **módulo de Consulta + API pública** — nunca teve uma sprint própria com Capítulos 1–4, gates T0–T8 e ORR dedicados.

A Sprint 17.1 existe para corrigir essa lacuna no nível do DNA:

> Nenhuma UI séria do Inspectah pode existir sem uma API oficial correspondente, com contrato, testes e ORR.

Esta sprint transforma essa frase em realidade operacional.

---

## 3. Visão de produto da Sprint 17.1

### 3.1. Frase de visão

> "Transformar a Consulta do Inspectah em um serviço oficial, com uma API v1 estável e testada, que conecta a UI da S17 ao motor de S15/S16 sem gambiarras, com risco e evidências vindos do mesmo núcleo de verdade do sistema."

### 3.2. Cenário alvo (do teclado ao motor)

Ao final da Sprint 17.1, queremos que o seguinte fluxo seja verdadeiro e reproduzível, sem passos ocultos ou patches locais:

1. **Backend**
   ```bash
   cd /Users/gustavoschneiter/Documents/Inspectah
   source .venv/bin/activate
   PYTHONPATH=. python -m uvicorn inspectah.api:build_app --factory --reload --port 8000
   ```

2. **Frontend**
   ```bash
   cd /Users/gustavoschneiter/Documents/Inspectah/frontend/inspectah-ui
   npm ci
   npm run dev
   ```

3. **Usuário final**
   - Acessa `http://localhost:5173`.
   - Digita uma pergunta real em linguagem natural, por exemplo:
     - "Esse boato de fofoca X procede?",
     - "Essa informação política Y é verdadeira?",
     - "Esse dado climático Z confere?".
   - Clica em **Consultar**.
   - A UI envia `POST http://localhost:8000/api/consultation` com um payload compatível com `ConsultationRequest`.
   - O backend aciona o **módulo de Consulta**, que por sua vez conversa com Debunker/Comitês/Âncoras.
   - O backend devolve um `ConsultationResponse` JSON alinhado com os tipos TS da UI (risco, resumo, evidências, flags).
   - A UI mostra resumo, nível de risco e evidências sem qualquer mock, stub ou adaptação ad hoc.

Se em qualquer ponto desse fluxo a API não estiver presente, o contrato JSON não bater ou o motor não for acionado, os gates da Sprint 17.1 devem falhar.

### 3.3. Princípios que a Consulta v1 precisa respeitar

1. **Confiabilidade > conveniência**  
   Se o motor não conseguir responder com segurança, a API deve ser explícita (por exemplo, `riskLevel = "unknown"`, mensagem honesta, evidências insuficientes), em vez de inventar resposta ou mascarar erro.

2. **Contratos claros, explícitos e versionáveis**  
   A `Consultation API v1` deve ser suficiente para a UI atual, mas já nascer preparada para evoluir (v2, v3…) sem quebrar consumidores. Campos, enums e formatos de data/riscos precisam ser estáveis.

3. **Alinhamento estrito com o motor**  
   O que a UI exibe deve refletir o que Debunker/Comitês/Âncoras de fato concluíram. A camada HTTP **não** reinterpreta o julgamento; ela apenas o organiza e serializa de forma amigável.

4. **Erro previsível, não caótico**  
   Em caso de falha técnica, a API deve responder de forma consistente (códigos 5xx, shape de erro conhecido) para que a UI mostre mensagens amigáveis sem quebrar layout.

5. **Nenhum atalho local**  
   A Sprint 17.1 deve eliminar qualquer dependência de ajustes manuais no ambiente local para a consulta funcionar. Se for preciso setar algo, estará documentado e coberto por gates.

---

## 4. Personas e casos de uso

### 4.1. Personas

1. **Usuário final (Consultor)**
   - Perfil: pessoa que quer validar se um fato procede, em diferentes domínios (política, fofoca, esporte, clima, mandatos, projetos, ciência etc.).
   - Ferramenta: UI de consulta da S17.
   - Expectativa: fazer uma pergunta em linguagem natural e receber uma resposta clara, com nível de risco e principais evidências.

2. **Operador / Admin técnico**
   - Perfil: responsável por subir backend e frontend, monitorar logs, rodar gates, validar ORR.
   - Ferramenta: terminal, scripts `bin/s*`, logs do Uvicorn, `/docs` da API, pipelines de CI.
   - Expectativa: ter um endpoint estável, com contrato documentado e testado, que não quebre silenciosamente.

3. **Desenvolvedor de UI** (Bret, Kent e equipe)
   - Perfil: evolui a interface, adiciona novos componentes, estados, tooltips, etc.
   - Ferramenta: `frontend/inspectah-ui`, tipos TS, testes RTL/Vitest.
   - Expectativa: poder confiar que o backend fala **exatamente** o mesmo idioma de tipos que a UI; nada de “ajustes mágicos” no front para compensar buracos do backend.

4. **Desenvolvedor de motor / domínio**
   - Perfil: trabalha em Debunker, Comitês, Âncoras, Threat Model.
   - Ferramenta: módulos Python em `inspectah/`, testes, gates S15/S16.
   - Expectativa: ter uma camada de Consulta que orquestra o motor sem expor detalhes internos direto para a UI, permitindo evoluir o núcleo sem quebrar o contrato HTTP.

### 4.2. Casos de uso principais

1. **Consulta em domínio bem suportado (baixo risco)**
   - Exemplo: dado climático (“A máxima de ontem no Rio foi X ºC?”) ou estatística esportiva simples.
   - Comportamento esperado:
     - Debunker encontra múltiplas evidências consistentes.
     - Comitês convergem para risco baixo.
     - API retorna 200 com `riskLevel = "low"` (ou equivalente), resumo direto e evidências claramente listadas.

2. **Consulta em domínio sensível (alto risco)**
   - Exemplo: denúncia política, boato de corrupção, acusação séria.
   - Comportamento esperado:
     - Debunker identifica conteúdo sensível.
     - Comitês aplicam políticas conservadoras.
     - Âncoras/Anti-canetada impedem “canetada” sem evidências fortes.
     - API retorna 200 com `riskLevel = "high"` + justificativa coerente, ou `"unknown"` se não houver base suficiente.

3. **Consulta com dados insuficientes / domínio pouco suportado**
   - Exemplo: pergunta muito vaga ou sobre tema ainda sem boas fixtures/regras.
   - Comportamento esperado:
     - Serviço de consulta tenta mapear domínio, identifica falta de evidência.
     - API responde com `riskLevel` adequado (provavelmente `"unknown"`), mensagem clara de limitação e orientação para refinar pergunta ou fornecer mais contexto.

4. **Falhas técnicas previsíveis**
   - Exemplo: indisponibilidade de parte do motor, exceção interna inesperada.
   - Comportamento esperado:
     - API retorna código HTTP apropriado (5xx) com shape de erro conhecido.
     - UI exibe mensagens amigáveis e consistentes com os estados de erro já modelados na S17.

---

## 5. Escopo da Sprint 17.1 (nível de produto)

### 5.1. Escopo IN (o que entra)

- **Criação de um módulo de Consulta** em algo como `inspectah/consultation/` contendo:
  - Modelos de domínio (`ConsultationRequest`, `ConsultationResult`, enums de risco/estado);
  - Serviço de orquestração que integra Debunker, Comitês e, quando fizer sentido, Âncoras/Anti-canetada;
  - Tradução clara entre o mundo interno (motor) e o contrato HTTP/JSON.

- **Definição e implementação da Inspectah Consultation API v1**:
  - Endpoint principal `POST /api/consultation` registrado no app FastAPI em `inspectah/api.py`;
  - Modelos Pydantic alinhados 1:1 com os tipos TypeScript usados pela UI da S17;
  - Documentação automática em `/docs` + `/openapi.json` com schemas claros.

- **Integração real com o motor**:
  - A API de consulta deve acionar Debunker e Comitês (e Âncoras quando aplicável) para produzir respostas, risco e evidências;
  - Não é aceitável responder com mocks ou dados “inventados” para satisfazer apenas a UI.

- **Testes e gates focados em Consulta v1**:
  - Testes de unidade e integração da camada de domínio de consulta;
  - Testes de API para `POST /api/consultation` cobrindo os casos de uso principais;
  - Gates que falham explicitamente se:
    - O endpoint não existir,
    - O contrato JSON divergir dos tipos da UI,
    - O motor não for acionado (ex.: consulta que nunca chega ao Debunker/Comitês).

- **Documentação e ORR dedicados**:
  - Overview, arquitetura/filemap da consulta e ORR específicos da Sprint 17.1;
  - Registro de SHA final, estado dos gates e decisão GO/GO_WITH_RESTRICTIONS/NO_GO.

### 5.2. Escopo OUT (o que fica de fora)

- Novas superfícies de UI (console/admin, timeline, dashboards, etc.).
- Autenticação/Autorização de usuários finais (auth será tema de outras sprints).
- Mudanças profundas na forma como Debunker/Comitês/Âncoras funcionam — a 17.1 só fará ajustes pontuais necessários para suportar a Consulta v1.
- Expansão massiva de domínios; o foco é **usar bem** os domínios já modelados na S15.
- Alterações estruturais na UI da S17: a regra aqui é alinhar o backend ao contrato já estabelecido, não redesenhar a interface.

---

## 6. Requisitos de alto nível

### 6.1. Requisitos funcionais

1. A API deve expor pelo menos um endpoint HTTP de consulta consolidada (`POST /api/consultation`).
2. O endpoint deve aceitar payloads compatíveis com o que a UI da S17 envia hoje (`ConsultationRequest`).
3. O endpoint deve:
   - Identificar (ou pelo menos receber) o domínio da pergunta;
   - Invocar Debunker/Comitês (e Âncoras quando aplicável);
   - Consolidar uma resposta com risco + evidências;
   - Retornar JSON compatível com `ConsultationResponse`.
4. A API deve diferenciar claramente entre:
   - Respostas normais (200);
   - Casos sem dados suficientes mas com sistema saudável (200 com `riskLevel`/flags apropriados);
   - Falhas técnicas (5xx) com mensagens coerentes com os estados de erro já modelados na UI.

### 6.2. Requisitos não funcionais

1. **Estabilidade de contrato**  
   O shape do JSON (campos, enums, tipos) não deve mudar de forma arbitrária. Mudanças quebráveis → nova versão.

2. **Observabilidade básica**  
   A camada de consulta deve deixar rastros suficientes (logs, métricas ou evidências) para entender:
   - Qual domínio foi detectado;
   - Quais módulos foram invocados;
   - Qual foi o resultado final (risco, evidências, flags).

3. **Performance aceitável**  
   Nos cenários canônicos, o tempo de resposta deve ser confortável para uso interativo na UI.

4. **Integração com o DNA do projeto**  
   A consulta deve respeitar padrões já estabelecidos:
   - Organização de módulos em `inspectah/`;
   - Scripts em `bin/`;
   - Scorecards em `out/scorecards/`;
   - Evidências em `out/evidence/`;
   - Gates T0–T8 como guard‑rails oficiais.

5. **Reprodutibilidade ponta‑a‑ponta**  
   Dado o SHA final da Sprint 17.1, qualquer pessoa com o repo clonado deve conseguir:
   - Subir backend e frontend;
   - Reproduzir as consultas canônicas;
   - Rodar os gates da Sprint 17.1 com o mesmo resultado (GO/GO_WITH_RESTRICTIONS/NO_GO).

---

## 7. Critérios de sucesso (visão de produto)

A Sprint 17.1 será considerada bem‑sucedida quando, do ponto de vista de produto, todas as afirmações abaixo forem verdadeiras:

1. **Usuário final** consegue fazer uma consulta real na UI de S17 e receber resposta vinda do motor, sem mocks.
2. **Desenvolvedor de UI** consegue evoluir a tela de consulta sabendo exatamente quais campos a API entrega e quais estados de erro/risco precisa tratar.
3. **Operador** consegue subir backend + frontend, rodar gates, olhar `/docs` e `/openapi.json` e enxergar claramente:
   - O endpoint oficial de consulta;
   - Os modelos Request/Response;
   - Como reproduzir o fluxo via `curl` ou ferramenta de API.
4. **Time de motor** consegue evoluir Debunker/Comitês/Âncoras sem quebrar a UI, desde que preserve a interface da camada de Consulta.
5. **DNA do Inspectah** passa a incluir, de forma explícita, a regra:
   
   > "Não existe UI séria sem API oficial com sprint própria, contrato e ORR."

---

## 8. Hand‑off para os próximos capítulos

- **Capítulo 2 (Gates)** vai transformar esta visão em uma matriz de validação detalhada:
  - Quais gates específicos garantem que a API existe, está correta e conversa com o motor;
  - Quais scorecards e evidências serão gerados;
  - Como a Sprint 17.1 se encaixa na esteira T0–T8 existente (S15–S17).

- **Capítulo 3 (Filemap & Arquitetura)** vai especificar:
  - Estrutura de pastas e módulos para o núcleo de consulta (`inspectah/consultation/` ou similar) e para o router da API v1;
  - Como scripts e testes se organizam para manter a consulta testável e evolutiva.

- **Capítulo 4 (Execução)** vai descrever:
  - Roteiro passo a passo para implementar a sprint;
  - Comandos de desenvolvimento, testes, gates e ORR;
  - Fluxo completo do ponto de vista de quem está com o repo clonado.

Com isso, o Capítulo 1 consolida a fundação conceitual da Sprint 17.1: **Consulta** deixa de ser apenas um formulário na UI e passa a ser um cidadão de primeira classe na arquitetura do Inspectah, com API formal, contrato estável, validação ponta‑a‑ponta e nenhum atalho provisório escondido no ambiente local.