# Inspectah — Sprint 18
## Capítulo 4 — Runbooks, comandos e prompts para o Console de Admin

> Arquivo alvo no repositório: `Sprint 18/Capitulo 4.md`  
> Domínio: Frontend — Console de Admin (Fontes, Casos/Temas, Saúde Operacional)

---

### 1. Objetivo deste capítulo

Os capítulos anteriores definiram a S18 em três níveis:

- **Cap. 1** — visão, contexto e escopo do Console de Admin;  
- **Cap. 2** — gates S18_G0…S18_G8, métricas M1…M6 e critérios de GO/NO‑GO;  
- **Cap. 3** — filemap, arquitetura e pontos de entrada (scripts, pastas, workflows).

Este **Capítulo 4** é o **manual de operação da S18**. Ele responde, de forma direta:

- como preparar o ambiente local para trabalhar no Console de Admin;  
- como rodar **cada gate S18_G0…S18_G8** na prática (comandos, pré‑requisitos, saídas, falhas comuns);  
- como usar `bin/s18_all.sh` e o workflow `_s18_admin_front.yml` na CI;  
- como conduzir uma **demo end‑to‑end** do Console de Admin;  
- quais prompts usar com o Codex (ou agente de código equivalente) para implementar/ajustar as partes da S18.

A meta é simples: qualquer pessoa (dev, SRE, PO) que nunca participou da S18 consegue, com este capítulo na mão, **levantar o ambiente, rodar os gates, entender os scorecards e demonstrar o Console de Admin** sem depender de conhecimento tribal.

---

### 2. TL;DR para dev apressado

Se você acabou de clonar o repo e quer validar rapidamente o Console de Admin da S18:

1. Ative o ambiente e suba o backend:

   ```bash
   cd /Users/<seu-usuario>/Documents/Inspectah
   source .venv/bin/activate
   export INSPECTAH_ENV=local
   export INSPECTAH_DEBUG=true
   PYTHONPATH=. uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Em outro terminal, suba o frontend:

   ```bash
   cd /Users/<seu-usuario>/Documents/Inspectah/frontend
   npm install        # se ainda não fez
   npm run dev
   ```

3. Confira rapidamente o Console de Admin em `http://localhost:5173/admin`.

4. Volte à raiz do repo e rode todos os gates intermediários da S18:

   ```bash
   cd /Users/<seu-usuario>/Documents/Inspectah
   PYTHONPATH=. bash bin/s18_all.sh
   ```

5. Se tudo passar, rode o GO/NO‑GO:

   ```bash
   PYTHONPATH=. bash bin/s18_g8_go_no_go.sh
   cat out/scorecards/S18_G8_go_no_go.json
   ```

Com isso você tem um **snapshot completo** do estado da S18 (UI, backend, métricas e CI) em poucos minutos.

---

### 3. Preparando o ambiente local (detalhado)

#### 3.1 Pré‑requisitos

- Python 3.x compatível com o backend do Inspectah (mesma versão usada nas sprints anteriores).  
- Node.js + gerenciador de pacotes (npm, pnpm ou yarn) compatível com a SPA da S17.  
- Dependências já instaladas conforme instruções gerais do repositório (venv para backend, `node_modules` para frontend).

#### 3.2 Subindo o backend

Na raiz do repositório `Inspectah`:

```bash
cd /Users/<seu-usuario>/Documents/Inspectah

# Ativar o virtualenv (ajustar caminho se necessário)
source .venv/bin/activate

# Exportar variáveis de ambiente mínimas (exemplo)
export INSPECTAH_ENV=local
export INSPECTAH_DEBUG=true

# Rodar o backend (FastAPI)
PYTHONPATH=. uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

A aplicação deve expor a OpenAPI em `http://localhost:8000/docs`, e as rotas de admin (`/admin/sources`, `/admin/cases`, `/admin/health`) devem aparecer sob o namespace esperado.

#### 3.3 Subindo o frontend (SPA)

Em outro terminal, ainda na raiz do repo:

```bash
cd /Users/<seu-usuario>/Documents/Inspectah/frontend

# Instalar dependências (apenas se ainda não instaladas)
npm install   # ou pnpm install / yarn install, conforme o projeto

# Rodar o front em modo dev
npm run dev
```

Por padrão, a SPA deve subir em algo como `http://localhost:5173` (ou porta equivalente), com a UI de consulta da S17. O Console de Admin ficará disponível em `http://localhost:5173/admin` (protegido por `useAdminRouteGuard` conforme configurado).

#### 3.4 Checagem manual mínima

Antes de rodar os gates, faça um sanity check rápido:

1. Abra `http://localhost:5173/admin`.  
2. Confirme que a **Visão Geral** mostra cards de saúde (fontes, casos, integrações).  
3. Navegue até **Fontes** (`/admin/sources`) e **Casos/Temas** (`/admin/cases`).  
4. Verifique se as rotas de detalhe (`/admin/sources/:id`, `/admin/cases/:id`) renderizam sem crash.

Se algo falhar aqui, corrija antes de seguir para os gates — isso poupa tempo de depuração nos scripts.

---

### 4. Runbooks por gate S18_G0…S18_G8

A seguir, os runbooks gate‑a‑gate. Todos assumem que você está na raiz do repositório `Inspectah` e, quando necessário, com o virtualenv ativado (`source .venv/bin/activate`).

Cada subseção traz:

- **Objetivo** — o que o gate garante;  
- **Relação com métricas** — quais M1…M6 são tocadas;  
- **Pré‑requisitos** — o que precisa estar pronto;  
- **Comando sugerido** — como rodar;  
- **Saídas esperadas** — scorecards e evidências;  
- **Falhas comuns** — erros típicos e onde olhar.

#### 4.1 S18_G0 — Intenção & escopo travados

**Objetivo**  
Confirmar que a visão da S18 (Cap. 1) e o backlog da sprint estão alinhados, sem vazamentos de escopo para S19/S20.

**Relação com métricas**  
Não mede M1…M6; é gate de alinhamento de produto.

**Pré‑requisitos**

- `Sprint 18/Capitulo 1.md` e `Sprint 18/Capitulo 2.md` revisados e salvos.  
- Backlog da S18 atualizado (histórias/épicos coerentes com o recorte da S18).

**Comando sugerido**

```bash
PYTHONPATH=. bash bin/s18_g0_scope.sh
```

**Saídas esperadas**

- `out/scorecards/S18_G0_scope.json`  
- `out/evidence/S18_G0_scope/README.md` (resumo humano opcional)

**Falhas comuns**

- TODOs ou “decidir depois” em seções críticas do Cap. 1.  
- Histórias de S19/S20 (timeline detalhada, raio‑X, auth completa) ainda presentes na S18.

---

#### 4.2 S18_G1 — Arquitetura de front & contratos de admin

**Objetivo**  
Garantir que rotas, módulos e contratos de API de admin estejam coerentes entre frontend, backend e Cap. 3.

**Relação com métricas**  
Não mede M1…M6 diretamente, mas é pré‑condição para G2, G4 e G5.

**Pré‑requisitos**

- Módulo de backend `backend/app/admin/` criado com `routes.py`, `schemas.py`, `service.py`.  
- Páginas e APIs de admin no frontend criadas (`frontend/src/pages/admin/`, `frontend/src/api/admin/`).  
- Cap. 3 atualizado com o filemap real.

**Comando sugerido**

```bash
PYTHONPATH=. bash bin/s18_g1_arch_front_and_api.sh
```

**Saídas esperadas**

- `out/scorecards/S18_G1_arch_front_and_api.json`  
- `out/evidence/S18_G1_arch_front_and_api/openapi_admin.json` (snapshot da spec de admin)  
- `out/evidence/S18_G1_arch_front_and_api/notes.md` (observações sobre contratos)

**Falhas comuns**

- Rotas de admin ausentes da OpenAPI.  
- Schemas de resposta divergindo do que o frontend espera.  
- Arquivos de front/back não seguindo o filemap do Cap. 3.

---

#### 4.3 S18_G2 — Journeys & UX do Console de Admin

**Objetivo**  
Validar que as jornadas definidas no Cap. 1 (Operador, Curador, PO) são possíveis e compreensíveis na UI.

**Relação com métricas**  
Começa a exercitar **M2** e **M6** de forma exploratória (sem alvos rígidos ainda).

**Pré‑requisitos**

- Backend e frontend rodando em ambiente local/homolog.  
- Rotas `/admin`, `/admin/sources`, `/admin/cases` funcionando.

**Comando sugerido**

```bash
PYTHONPATH=. bash bin/s18_g2_journeys_and_ux.sh
```

Internamente, o script pode chamar Cypress/Playwright (ou similar) para:

- abrir `/admin`;  
- navegar para Fontes e Casos;  
- executar os roteiros das personas;  
- opcionalmente, medir tempos de navegação.

**Saídas esperadas**

- `out/scorecards/S18_G2_journeys_and_ux.json` (resumo das journeys e status)  
- `out/evidence/S18_G2_journeys_and_ux/journeys.md`  
- `out/evidence/S18_G2_journeys_and_ux/screenshots/` (opcional)

**Falhas comuns**

- Links quebrados entre Visão Geral, Fontes e Casos.  
- Estados de loading/erro ausentes ou incompreensíveis.  
- Jornadas que dependem de “atalhos secretos” conhecidos só por quem implementou.

---

#### 4.4 S18_G3 — Qualidade de implementação de frontend

**Objetivo**  
Garantir que o frontend — incluindo o Console de Admin — passa em build, lint e testes básicos.

**Relação com métricas**  
Não mede M1…M6 diretamente, mas protege todas as métricas contra regressões triviais.

**Pré‑requisitos**

- `frontend/` com dependências instaladas.  
- Scripts de build/lint/test configurados no `package.json`.

**Comando sugerido**

```bash
PYTHONPATH=. bash bin/s18_g3_front_quality.sh
```

Internamente, o script deve executar algo como:

```bash
cd frontend
npm run lint
npm run test -- --watch=false
npm run build
```

**Saídas esperadas**

- `out/scorecards/S18_G3_front_quality.json` (status e métricas básicas: número de testes, etc.)  
- `out/evidence/S18_G3_front_quality/build.log`  
- `out/evidence/S18_G3_front_quality/lint.log`  
- `out/evidence/S18_G3_front_quality/tests.log`

**Falhas comuns**

- Testes E2E ou unitários assumindo rotas antigas da S17.  
- Import de componentes de admin em caminhos errados.  
- Falta de updates nos tipos quando contratos de admin mudam.

---

#### 4.5 S18_G4 — Coerência UI ↔ Backend (Fontes & Casos)

**Objetivo**  
Comprovar que a UI mostra o mesmo universo de fontes e casos que o backend expõe.

**Relação com métricas**  
Mede diretamente **M3** (cobertura de fontes) e **M4** (cobertura de casos/temas).

**Pré‑requisitos**

- Backend com endpoints de admin funcionando.  
- Console de Admin integrado a esses endpoints.  
- Fixtures em `Sprint 18/fixtures/admin_sources_fixture.json` e `Sprint 18/fixtures/admin_cases_fixture.json` (quando aplicável).

**Comando sugerido**

```bash
PYTHONPATH=. bash bin/s18_g4_ui_vs_backend.sh
```

**Comportamento esperado (alto nível)**

1. Carregar fixtures em um ambiente de teste (ou garantir estado controlado).  
2. Chamar o backend (`/admin/sources`, `/admin/cases`) e salvar snapshots.  
3. Obter, via UI ou API interna, o conjunto de fontes/casos exibidos.  
4. Calcular M3 e M4 e registrar no scorecard.

**Saídas esperadas**

- `out/scorecards/S18_G4_ui_vs_backend.json` (inclui M3 e M4)  
- `out/evidence/S18_G4_ui_vs_backend/backend_sources_snapshot.json`  
- `out/evidence/S18_G4_ui_vs_backend/backend_cases_snapshot.json`  
- `out/evidence/S18_G4_ui_vs_backend/ui_sources_snapshot.json`  
- `out/evidence/S18_G4_ui_vs_backend/ui_cases_snapshot.json`  
- `out/evidence/S18_G4_ui_vs_backend/diff_report.md`

**Falhas comuns**

- Filtros ou paginação da UI escondendo subconjuntos inteiros de fontes/casos.  
- Campos críticos (estado, timestamps principais) divergindo sistematicamente.  
- Esquecimento de registrar novos tipos de caso/fonte na UI.

---

#### 4.6 S18_G5 — Saúde operacional refletida na UI

**Objetivo**  
Verificar se a Visão Geral do Console de Admin reflete corretamente os sinais de health do backend e é rápida o suficiente.

**Relação com métricas**  
Mede diretamente **M1** (tempo de carregamento da Visão Geral) e conecta com cenários de health.

**Pré‑requisitos**

- Endpoint `/admin/health` implementado e estável.  
- AdminOverviewPage integrada ao endpoint.  
- Opcional: fixture `Sprint 18/fixtures/admin_health_fixture.json`.

**Comando sugerido**

```bash
PYTHONPATH=. bash bin/s18_g5_health_mapping.sh
```

**Comportamento esperado (alto nível)**

1. Exercitar cenários de health (por fixture ou simulando estados): tudo ok, fontes degradadas, casos em atenção/contestação.  
2. Para cada cenário, capturar a resposta do backend e o estado da UI.  
3. Medir M1 em um cenário padrão.  
4. Registrar consistência e tempo no scorecard.

**Saídas esperadas**

- `out/scorecards/S18_G5_health_mapping.json` (inclui M1 e resultado por cenário)  
- `out/evidence/S18_G5_health_mapping/backend_health_snapshots.json`  
- `out/evidence/S18_G5_health_mapping/ui_health_snapshots.json`  
- `out/evidence/S18_G5_health_mapping/scenarios.md`

**Falhas comuns**

- UI apresentando labels que não batem com os estados de health (ex.: fonte marcada como "OK" quando backend sinaliza problema).  
- Requests em cascata desnecessárias aumentando M1.  
- Falta de estados de erro claros quando `/admin/health` falha.

---

#### 4.7 S18_G6 — Experiência de operação end‑to‑end

**Objetivo**  
Comprovar, com métricas, que um operador consegue usar o Console de Admin para entender o estado do sistema e investigar problemas.

**Relação com métricas**  
Mede diretamente **M2** (tempo do alerta à fonte), **M5** (profundidade de explicação) e **M6** (caminho até evidência em até 2 cliques).

**Pré‑requisitos**

- Console de Admin completo em ambiente local/homolog com dados realistas (fixtures ou sandbox).  
- Cenários de demo definidos (ver seção 6).

**Comando sugerido**

```bash
PYTHONPATH=. bash bin/s18_g6_metrics_and_demo.sh
```

**Comportamento esperado (alto nível)**

1. Executar cenários de ponta a ponta automatizados ou semi‑automatizados:  
   - da Visão Geral até uma fonte problemática (alerta → lista de fontes → detalhe);  
   - da Visão Geral até um caso em contestação (alerta → lista de casos → detalhe).  
2. Medir M2 para a jornada alerta→fonte.  
3. Medir M5 e M6 com base nos cenários (se há explicação e se é possível chegar à evidência em até 2 cliques).  
4. Registrar métricas e observações.

**Saídas esperadas**

- `out/scorecards/S18_G6_metrics_and_demo.json` (inclui M2, M5, M6)  
- `out/evidence/S18_G6_metrics_and_demo/scenarios.md`  
- `out/evidence/S18_G6_metrics_and_demo/demo_notes.md`  
- `out/evidence/S18_G6_metrics_and_demo/recordings/` (opcional)

**Falhas comuns**

- Jornadas que exigem mais de 2 cliques para chegar em evidências.  
- Telas de detalhe sem resumo textual ou motivos claros (derrubando M5).  
- Dependência de URLs mágicos em vez de navegação guiada.

---

#### 4.8 S18_G7 — Observabilidade + CI da S18

**Objetivo**  
Assegurar que o Console de Admin está protegido por CI e, minimamente, observável.

**Relação com métricas**  
Não mede M1…M6 diretamente, mas garante que testes que cobrem essas métricas são executados em CI.

**Pré‑requisitos**

- Workflow `.github/workflows/_s18_admin_front.yml` criado.  
- CI geral do projeto configurada e rodando.

**Comando sugerido**

```bash
PYTHONPATH=. bash bin/s18_g7_ci_and_observability.sh
```

**Comportamento esperado (alto nível)**

- Ler e validar o conteúdo de `_s18_admin_front.yml` (build, lint, tests).  
- Confirmar que existe pelo menos um teste na CI que falharia se `/admin` quebrasse grosseiramente.  
- Opcionalmente, ler a última execução do workflow e resumir o estado.

**Saídas esperadas**

- `out/scorecards/S18_G7_ci_and_observability.json`  
- `out/evidence/S18_G7_ci_and_observability/workflows_list.md`  
- `out/evidence/S18_G7_ci_and_observability/ci_last_run_summary.log`

**Falhas comuns**

- `_s18_admin_front.yml` existente mas sem chamar `bin/s18_g3_front_quality.sh`.  
- Testes de admin marcados como opcionais ou desplugados da pipeline principal.  
- Ausência de qualquer log ou telemetria mínima de erros em admin em ambientes não‑dev.

---

#### 4.9 S18_G8 — GO/NO‑GO da Sprint 18

**Objetivo**  
Tomar a decisão final de GO/NO‑GO da S18, com base nos gates anteriores e nas métricas M1…M6.

**Relação com métricas**  
Agrega M1…M6 e valida se todos os gates S18_G0…S18_G7 estão em PASS.

**Pré‑requisitos**

- Scorecards S18_G0…S18_G7 gerados.  
- `docs/sprint_18_overview.md` atualizado com o wrap humano da sprint.

**Comando sugerido**

```bash
PYTHONPATH=. bash bin/s18_g8_go_no_go.sh
```

**Comportamento esperado (alto nível)**

- Ler todos os scorecards S18_G0…S18_G7.  
- Confirmar que todos estão em `status: "PASS"`.  
- Agregar M1…M6 e demais campos relevantes.  
- Gerar `S18_G8_go_no_go.json` com decisão `GO` ou `NO_GO` e lista de riscos/débitos residuais.

**Saídas esperadas**

- `out/scorecards/S18_G8_go_no_go.json`  
- `out/evidence/S18_G8_go_no_go/summary.json`

**Falhas comuns**

- Risco conhecido de painel decorativo (UI divergindo do backend) sendo ignorado.  
- Falta de registro de débitos empurrados para S19/S20.  
- Execução de G8 sem regenerar G4–G6 após mudanças relevantes.

---

### 5. Runbook completo da S18 — `bin/s18_all.sh`

Para facilitar validações locais e em alguns contextos de CI, a S18 conta (opcionalmente) com um script agregador:

```text
bin/s18_all.sh
```

**Função**

- Executar, em ordem, os gates S18_G0…S18_G7.  
- Parar na primeira falha (exit code ≠ 0), indicando claramente qual gate quebrou.  
- Não executar S18_G8 (GO/NO‑GO), que deve ser rodado de forma mais deliberada.

**Uso típico**

```bash
PYTHONPATH=. bash bin/s18_all.sh
```

Esse script é especialmente útil para:

- rodar uma validação completa antes de abrir PR;  
- validar o estado da S18 antes de rodar uma demo maior;  
- servir de entrypoint simplificado para jobs de CI que queiram apenas saber se “a S18 está consistente”.

---

### 6. Modo demo — roteiro para apresentar o Console de Admin

Esta seção descreve um roteiro sugerido para demos da S18, combinando console de admin e gates, no espírito “ver o sistema funcionando” (linha Bret Victor).

#### 6.1 Preparação

1. Backend e frontend rodando em ambiente limpo (local ou homolog).  
2. Opcionalmente, carregar fixtures para garantir cenários controlados (por exemplo, uma fonte degradada e um caso em contestação).  
3. Rodar `PYTHONPATH=. bash bin/s18_all.sh` para garantir que todos os gates intermediários estão verdes.  
4. Ter à mão o diretório `out/scorecards/` aberto em um editor para mostrar evidências ao vivo, se necessário.

#### 6.2 Roteiro de apresentação (exemplo)

1. **Visão Geral (health)**  
   - Abrir `/admin` e mostrar os cards de saúde.  
   - Explicar rapidamente o que cada card significa (fontes, casos, integrações).  
   - Conectar com G5 (health mapping) e M1.

2. **Fontes**  
   - Navegar para `/admin/sources`.  
   - Filtrar por fontes degradadas.  
   - Abrir uma fonte problemática e mostrar histórico curto de falhas.  
   - Conectar com G4 (UI↔backend) e M3.

3. **Casos/Temas**  
   - Navegar para `/admin/cases`.  
   - Filtrar por casos em contestação ou com dados frágeis.  
   - Abrir detalhe de um caso e mostrar resumo + principais fontes/evidências.  
   - Conectar com G4/G6, M4, M5 e M6.

4. **Gates e scorecards na prática**  
   - Mostrar rapidamente `out/scorecards/S18_G4_ui_vs_backend.json` e `S18_G5_health_mapping.json`, apontando M3, M4, M1.  
   - Explicar como G6 mede M2, M5, M6 em `S18_G6_metrics_and_demo.json`.

5. **Fechamento com GO/NO‑GO**  
   - Rodar `PYTHONPATH=. bash bin/s18_g8_go_no_go.sh`.  
   - Abrir `out/scorecards/S18_G8_go_no_go.json` e mostrar a decisão `GO` e principais riscos/resíduos.  
   - Conectar a decisão com o espírito da S18: sem painel decorativo, sem backdoor, sem incoerência UI↔verdade.

Esse roteiro pode ser adaptado para demos curtas (5–10 minutos) ou longas (com foco em arquitetura e DNA).

---

### 7. Foco em testes de frontend (visão Kent C. Dodds)

Para manter o Console de Admin saudável ao longo do tempo, os testes de front precisam ser pensados como **contratos de comportamento**, não como screenshots frágeis.

Sugestões práticas:

- Priorizar testes que validam **comportamento das rotas** (`/admin`, `/admin/sources`, `/admin/cases`) e não detalhes cosméticos.  
- Nos testes de página (ex.: `AdminOverviewPage.test.tsx`):  
  - garantir que, dado um mock de `/admin/health`, os cards corretos são renderizados;  
  - validar estados de loading/erro.  
- Em testes de listas (Fontes/Casos):  
  - garantir que filtros aplicados se refletem na tabela;  
  - não acoplar os testes a textos muito específicos de UI quando não for essencial.  
- Em E2E:  
  - priorizar as jornadas mapeadas em G2 e G6;  
  - instrumentar o tempo das jornadas para alimentar M2/M6 quando fizer sentido.

Essas práticas se conectam diretamente aos gates S18_G2, S18_G3, S18_G4, S18_G5 e S18_G6.

---

### 8. Prompts de referência para o Codex (ou agente de código)

Esta seção traz prompts práticos para pedir ajuda ao Codex (ou agente equivalente) na implementação e evolução da S18.

#### 8.1 Prompt — Implementar páginas de admin no frontend

```text
Você é um engenheiro de frontend trabalhando no projeto Inspectah.

Objetivo: implementar o Console de Admin da Sprint 18, usando React + Vite + Tailwind, dentro da SPA já existente da Sprint 17.

Contexto:
- O repositório local está em: /Users/<seu-usuario>/Documents/Inspectah
- O frontend vive em: frontend/
- O Capítulo 1 da Sprint 18 define a visão do Console de Admin (Visão Geral, Fontes, Casos/Temas).
- O Capítulo 3 define o filemap e recomenda criar:
  - páginas em frontend/src/pages/admin/
  - componentes em frontend/src/components/admin/
  - clientes de API em frontend/src/api/admin/
  - tipos em frontend/src/types/admin/
- O backend expõe endpoints:
  - GET /admin/sources
  - GET /admin/sources/{id}
  - GET /admin/cases
  - GET /admin/cases/{id}
  - GET /admin/health

Tarefas:
1. Criar AdminLayout.tsx, AdminOverviewPage.tsx, AdminSourcesPage.tsx, AdminSourceDetailPage.tsx, AdminCasesPage.tsx, AdminCaseDetailPage.tsx em frontend/src/pages/admin/.
2. Criar componentes reutilizáveis em frontend/src/components/admin/ (tabelas, badges de status, cards de health, estados vazios/loading/erro).
3. Criar clientes de API em frontend/src/api/admin/ para chamar as rotas de admin.
4. Integrar essas rotas no roteador principal (frontend/src/router.tsx), adicionando /admin, /admin/sources, /admin/cases e rotas de detalhe.
5. Criar testes básicos em frontend/src/tests/admin/ para garantir que as páginas principais rendem sem erro.

Requisitos:
- Usar o padrão de componentes e estilo já adotado na Sprint 17.
- Manter o namespace admin/ bem isolado.
- Expor estados de loading/erro de forma amigável.

Responda com o plano de arquivos a criar/editar e o código completo para cada um, usando o filemap sugerido.
```

#### 8.2 Prompt — Implementar módulo de admin no backend

```text
Você é um engenheiro de backend trabalhando no projeto Inspectah.

Objetivo: implementar o módulo de Admin para o Console de Admin da Sprint 18 em FastAPI.

Contexto:
- O repositório local está em: /Users/<seu-usuario>/Documents/Inspectah
- O backend vive em: backend/
- O Capítulo 3 da Sprint 18 recomenda criar um namespace backend/app/admin/ com:
  - routes.py
  - schemas.py
  - service.py
  - dependencies.py
- O Truth-DB e o Sistema de Blocos já existem em backend/app/core/.

Tarefas:
1. Criar backend/app/admin/schemas.py com modelos Pydantic para fontes, casos/temas e health agregada.
2. Criar backend/app/admin/service.py com funções que leem estados consolidados do Truth-DB/Sistema de Blocos e os projetam nesses schemas.
3. Criar backend/app/admin/routes.py com rotas:
   - GET /admin/sources
   - GET /admin/sources/{id}
   - GET /admin/cases
   - GET /admin/cases/{id}
   - GET /admin/health
4. Garantir que /admin/health agregue watchers e scorecards existentes para produzir um objeto simples de health.
5. Criar testes em backend/tests/admin/ garantindo respostas mínimas corretas.

Requisitos:
- Não expor estados intermediários nem permitir mutações via admin.
- Manter o módulo de admin desacoplado de detalhes internos do Truth-DB (usar serviço/core como camada intermediária).

Responda com o plano de arquivos a criar/editar e o código completo para cada um.
```

#### 8.3 Prompt — Implementar scripts de gates S18_G0…S18_G8

```text
Você é um engenheiro de confiabilidade trabalhando no projeto Inspectah.

Objetivo: implementar os scripts de gates da Sprint 18 descritos no Capítulo 2 (S18_G0…S18_G8) e no Capítulo 3 (filemap e paths de saída).

Contexto:
- Repositório: /Users/<seu-usuario>/Documents/Inspectah
- Scripts de gates devem ser criados em: bin/
- Scorecards em: out/scorecards/
- Evidências em: out/evidence/

Tarefas:
1. Criar scripts shell bin/s18_g0_scope.sh … bin/s18_g8_go_no_go.sh.
2. Cada script deve:
   - assumir PYTHONPATH=. na raiz do repo;
   - rodar os checks relevantes (build, testes, chamadas HTTP, etc.);
   - escrever um JSON de scorecard em out/scorecards/S18_G*.json com campos gate_id, status, timestamp, metrics (quando houver) e details.
3. Criar bin/s18_all.sh para orquestrar G0…G7.

Requisitos:
- Scripts idempotentes.
- Exit code 0 apenas quando o gate passar.
- Não duplicar lógica desnecessária (podem existir helpers em Python se fizer sentido).

Responda com o plano de scripts e o conteúdo completo de cada arquivo, incluindo JSON de exemplo de scorecard.
```

---

### 9. Definição de pronto (Cap. 4)

Este Capítulo 4 é considerado concluído quando:

1. Cada gate S18_G0…S18_G8 tem um runbook claro, com comando(s) sugeridos, pré‑requisitos, saídas esperadas e falhas comuns mapeadas.  
2. Existe um caminho explícito para rodar todos os gates em sequência (`bin/s18_all.sh`).  
3. Há um roteiro de demo que permita mostrar o Console de Admin para stakeholders, conectando UI, gates e métricas.  
4. Existem prompts de referência suficientes para que o Codex (ou agente similar) implemente e evolua o Console de Admin, o módulo de backend e os scripts de gates sem inventar filemaps ou contratos.  
5. Um dev novo consegue, em menos de uma hora, seguir este capítulo para: levantar o ambiente, rodar `s18_all.sh`, interpretar os scorecards e fazer uma demo curta do Console de Admin.

Com Cap. 1–4 publicados e alinhados à DNA, a Sprint 18 passa a ter:

- visão clara (Cap. 1);  
- critérios objetivos de validação (Cap. 2);  
- mapa concreto de arquivos e pontos de entrada (Cap. 3);  
- manual operacional completo (Cap. 4).

A partir daqui, o trabalho da S18 deixa de ser apenas um conjunto de telas + código e passa a ser um **módulo operável, verificável, demonstrável e evoluível** do Inspectah.

