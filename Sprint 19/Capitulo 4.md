# Sprint 19 – Capítulo 4 (v2)
## Plano de Execução Cirúrgico – Timeline e Raio‑X do Inspectah

Este capítulo pega tudo que foi decidido nos Capítulos 1, 2 e 3 da Sprint 19 e transforma em um plano de execução **cirúrgico**, pensado tanto para humanos quanto para o Codex.

Meta: chegar ao final da sprint com:

- backend de admin expondo Timeline e Raio‑X de casos via API;
- SPA de admin com telas de Timeline e Raio‑X navegáveis a partir dos casos;
- fixtures consistentes e reutilizáveis;
- gates S19_G0…S19_G8 produzindo scorecards e evidências completas;
- workflow de CI da S19 rodando verde;
- resumo humano da sprint pronto para ORR.

Tudo isso sem quebrar nada de S17 (consulta user‑facing) nem de S18 (Console de Admin).

---
## 1. Pré‑condições e Disciplina de Trabalho

Antes de qualquer mudança:

1. Repositório
   - Caminho local: `/Users/gustavoschneiter/Documents/Inspectah`.
   - Branch principal: `main`, atualizada com `git pull origin main`.

2. Ambiente Python
   - Ativar venv na raiz:
     - `source .venv/bin/activate`.
   - Garantir dependências instaladas pelo menos uma vez:
     - `python -m pip install --upgrade pip`.
     - `pip install -e .[dev]`.

3. Ambiente Frontend
   - Em `frontend/inspectah-ui` já ter rodado `npm install`.

4. Checkpoint de saúde
   - Sprint 17 funcionando (testes relevantes verdes).
   - Sprint 18 funcionando:
     - testes de admin em `tests/admin/test_admin_endpoints.py` passam;
     - gates S18 executados; admin console acessível.

5. Regras de ouro
   - Não quebrar rotas já existentes em S17 e S18.
   - Não mudar contratos de API existentes sem motivo fortíssimo.
   - Sempre rodar testes e gates da área tocada antes de commitar.

---
## 2. Fase 1 – Backend de Admin: Schemas, Services e Rotas

Objetivo: estender o backend de admin para expor Timeline e Raio‑X, sem criar um backend paralelo.

### 2.1 Schemas de Timeline e Raio‑X

Arquivo alvo: `app/admin/schemas.py`.

Tarefas:

1. Adicionar modelos Pydantic para Timeline:
   - AdminTimelineEvent
     - id: str
     - case_id: str
     - timestamp: datetime
     - event_type: str
     - severity: opcional, por exemplo info, warning, critical
     - source: opcional, identificador da fonte ou bloco
     - summary: str
   - AdminTimelineResponse
     - case_id: str
     - events: lista de AdminTimelineEvent

2. Adicionar modelos Pydantic para Raio‑X:
   - AdminCaseXRay
     - case_id, title, category, status, risk, summary
     - debunker: AdminDebunkerSection
     - committees: AdminCommitteesSection
     - anchors: AdminAnchorsSection
     - evidences: AdminEvidenceSection
   - Seções internas:
     - AdminDebunkerSection
     - AdminCommitteesSection
     - AdminAnchorsSection
     - AdminEvidenceSection

Regras:

- Tipar explicitamente valores opcionais com Optional.
- Reutilizar nomes de status e risco já existentes em S17 e S18.
- Manter schemas o mais planos possível, amigáveis a golden tests.

Critério de aceite Fase 1.1

- Projeto compila; nenhum import circular novo.
- Ferramentas de tipo e o servidor FastAPI sobem sem erro de schema.

### 2.2 Serviços de Timeline e Raio‑X

Arquivo alvo: `app/admin/service.py`.

Tarefas:

1. Implementar função de Timeline:
   - list_case_timeline(case_id: str) -> AdminTimelineResponse
   - Responsabilidades básicas:
     - ler dados consolidados de casos e eventos já usados pela S12 e S18;
     - montar lista de AdminTimelineEvent ordenada por timestamp ascendente;
     - gerar ids de evento determinísticos;
     - ser resiliente a campos ausentes, sem explodir.

2. Implementar função de Raio‑X:
   - get_case_xray(case_id: str) -> Optional[AdminCaseXRay]
   - Responsabilidades básicas:
     - consolidar dados de Debunker, comitês, âncoras e evidências a partir da Truth‑DB e snapshots;
     - garantir que, quando há dados, as seções internas vêm minimamente preenchidas;
     - retornar None quando o case_id não existir ou não houver dados suficientes.

Regras:

- Toda leitura para Timeline e Raio‑X passa por essas funções; nada de puxar storage cru nas rotas.
- Evitar acoplamento com detalhes de implementação da Truth‑DB; usar funções auxiliares já existentes sempre que possível.

Critério de aceite Fase 1.2

- Chamar list_case_timeline e get_case_xray em modo interativo não quebra;
- Para um case de teste conhecido, o retorno faz sentido sem precisar de hack.

### 2.3 Rotas FastAPI de Timeline e Raio‑X

Arquivo alvo: `app/admin/routes.py`.

Tarefas:

1. Criar rota de Timeline:
   - GET em `/admin/cases/{case_id}/timeline`.
   - Chama list_case_timeline;
   - Em caso de sucesso, retorna AdminTimelineResponse;
   - Em ausência de caso, retorna 404 com mensagem clara.

2. Criar rota de Raio‑X:
   - GET em `/admin/cases/{case_id}/xray`.
   - Chama get_case_xray;
   - Em caso de sucesso, retorna AdminCaseXRay;
   - Em ausência de raio‑X, retorna 404.

3. Garantir que essas rotas entram no mesmo router de admin já incluído em inspectah/api.py.

Critério de aceite Fase 1.3

- `PYTHONPATH=. uvicorn inspectah.api:app` sobe com as novas rotas visíveis no OpenAPI;
- Chamadas manuais simples via httpie ou curl retornam dados ou 404 coerente.

### 2.4 Testes de Backend da S19

Diretório alvo: `tests/admin`.

Arquivo novo sugerido: `tests/admin/test_admin_timeline_xray_endpoints.py`.

Tarefas:

1. Cobrir endpoint de Timeline:
   - cenário feliz com case conhecido;
   - cenário 404 para case inexistente;
   - verificar que eventos retornam ordenados por timestamp e com campos principais preenchidos.

2. Cobrir endpoint de Raio‑X:
   - cenário feliz com case conhecido;
   - cenário 404 para case inexistente;
   - checar presença de seções debunker, committees, anchors e evidences.

3. Reutilizar fixtures já existentes (S12) ou fixtures novas da S19 quando necessário.

Critério de aceite Fase 1.4

- `PYTHONPATH=. python3 -m pytest tests/admin/test_admin_timeline_xray_endpoints.py` passa verde.

---
## 3. Fase 2 – SPA de Admin: Páginas, Componentes e Tipos

Objetivo: adicionar Timeline e Raio‑X à SPA de admin em `frontend/inspectah-ui`, reaproveitando o que já existe da S18.

### 3.1 Tipos e cliente de API

Arquivos alvo:

- `frontend/inspectah-ui/src/types/admin.ts`
- `frontend/inspectah-ui/src/api/admin/index.ts`

Tarefas:

1. Adicionar interfaces TypeScript para Timeline e Raio‑X, espelhando os schemas de backend:
   - AdminTimelineEvent, AdminTimelineResponse, AdminCaseXRay e seções internas.

2. Adicionar funções de client:
   - getAdminCaseTimeline(caseId: string)
   - getAdminCaseXRay(caseId: string)

Regras:

- Mantê‑las tipadas e alinhadas com a convenção já usada para fontes, casos e health.
- Centralizar a URL base e tratamento genérico de erros.

Critério de aceite Fase 2.1

- `npm run build` compila sem erros de tipo.

### 3.2 Páginas e rotas de Timeline e Raio‑X

Arquivos alvo:

- `frontend/inspectah-ui/src/pages/admin/`
- `frontend/inspectah-ui/src/App.tsx` ou arquivo de rotas equivalente

Tarefas:

1. Criar páginas:
   - AdminCaseTimelinePage
   - AdminCaseXRayPage

2. Ajustar AdminCasesPage e/ou AdminCaseDetailPage para expor ações de:
   - Ver timeline do caso;
   - Ver raio‑X do caso.

3. Registrar rotas novas:
   - `/admin/cases/:caseId/timeline` → AdminCaseTimelinePage
   - `/admin/cases/:caseId/xray` → AdminCaseXRayPage

Critério de aceite Fase 2.2

- Via browser, a partir da lista ou detalhe de casos, é possível alcançar as páginas de Timeline e Raio‑X para um case concreto.

### 3.3 Componentes de Timeline

Diretório alvo sugerido:

- `frontend/inspectah-ui/src/components/admin/timeline/`

Tarefas:

1. Criar componente Timeline:
   - Responsável por receber lista de AdminTimelineEvent e filtro;
   - Ordenar e renderizar os eventos na tela.

2. Criar componente TimelineEventCard:
   - Mostrar tipo, severidade, fonte e resumo do evento;
   - Destacar visualmente severidade quando relevante.

3. Criar TimelineFilters:
   - Permitir filtrar por período e tipo de evento.

Regras:

- Reutilizar padrões visuais de admin (cards, badges, espaçamentos).
- Não embutir lógica de negócio pesada nos componentes.

### 3.4 Componentes de Raio‑X

Diretório alvo sugerido:

- `frontend/inspectah-ui/src/components/admin/xray/`

Tarefas:

1. Criar CaseXRayLayout para orquestrar as seções:
   - DebunkerPanel
   - CommitteesPanel
   - AnchorsPanel
   - EvidenceSummaryPanel

2. Cada painel recebe apenas a parte do AdminCaseXRay que precisa renderizar.

Regras:

- Interface limpa; sem dependência direta de detalhes internos do backend.
- Layout focado em leitura rápida pelos operadores.

### 3.5 Testes de frontend

Diretório alvo:

- `frontend/inspectah-ui/src/__tests__/admin/`

Arquivo sugerido: `AdminTimelineXRay.test.tsx`.

Tarefas:

1. Configurar MSW para servir respostas de Timeline e Raio‑X usando fixtures da S19.

2. Testar:
   - estados de loading e erro;
   - render correto de eventos de timeline;
   - render das seções de Raio‑X;
   - navegação da página de casos para Timeline e Raio‑X.

Critério de aceite Fase 2.3

- `npm run lint` passa;
- `npm run test -- --watch=false` passa incluindo os testes da S19;
- `npm run build` passa.

---
## 4. Fase 3 – Fixtures da Sprint 19

Objetivo: criar fixtures estáveis que sirvam de base para backend, gates e frontend.

Diretório alvo:

- `Sprint 19/fixtures/`

Tarefas:

1. Criar fixtures de timelines para casos de domínios distintos, por exemplo:
   - timeline_expected_evento_climatico_inmet_2025_0901.json
   - timeline_expected_fofoca_celebridade_x.json
   - timeline_expected_mandato_politico_y.json
   - timeline_expected_projeto_obra_publica_z.json

2. Criar fixtures de Raio‑X para alguns desses casos quando fizer sentido:
   - xray_expected_evento_climatico_inmet_2025_0901.json
   - etc.

3. Garantir que os formatos batem com AdminTimelineResponse e AdminCaseXRay.

Uso das fixtures:

- Backend: consumidas em testes de admin da S19;
- Gates: usadas por S19_G4 e S19_G5 como expected para comparações;
- Frontend: MSW usa os mesmos arquivos para simular o backend.

Critério de aceite Fase 3

- Fixtures versionadas no repo;
- Nenhum teste ou gate da S19 depende de caminhos obscuros ou arquivos fora de Sprint 19.

---
## 5. Fase 4 – Gates S19_G0…S19_G8, Scorecards e Evidências

Objetivo: implementar gates da S19 seguindo o padrão do DNA, gerando scorecards e evidências auditáveis.

### 5.1 Scripts de gates

Diretório alvo: `bin`.

Scripts esperados:

- s19_g0_scope.sh
- s19_g1_contracts_and_data.sh
- s19_g2_journeys_and_ux.sh
- s19_g3_front_quality.sh
- s19_g4_timeline_correctness.sh
- s19_g5_xray_consistency_and_depth.sh
- s19_g6_metrics_and_demo.sh
- s19_g7_ci_and_observability.sh
- s19_g8_go_no_go.sh
- s19_all.sh

Padrão obrigatório:

1. Shebang e disciplina
   - linha inicial com interpretador bash;
   - set de flags de segurança (erros fecham o script, variáveis indefinidas não passam em branco).

2. Cálculo de diretórios e saída
   - calcular ROOT_DIR a partir da localização do script;
   - garantir existência das pastas de scorecards e evidências da S19.

3. Execução do gate
   - rodar comandos estritamente necessários para o objetivo daquele gate;
   - direcionar logs relevantes para out/evidence/S19_GX_nome/.

4. Scorecard
   - escrever JSON em out/scorecards/S19_GX_nome.json com, no mínimo:
     - gate_id;
     - status PASS ou FAIL;
     - timestamp;
     - metrics (para gates que medem M1 a M6);
     - details com lista de falhas quando houver.

### 5.2 Evidências por gate

Diretório alvo: `out/evidence`.

Padrão:

- Cada gate possui uma pasta dedicada, como out/evidence/S19_G4_timeline_correctness.
- Nessas pastas devem existir:
  - logs de execução;
  - snapshots de resposta da API;
  - comparações expected versus actual quando aplicável;
  - notas ou manifestos explicando o que foi validado.

Critério de aceite Fase 4

- `PYTHONPATH=. bash bin/s19_all.sh` executa G0 a G7 e gera scorecards da S19 com status PASS;
- `PYTHONPATH=. bash bin/s19_g8_go_no_go.sh` gera scorecard S19_G8 com decisão GO.

---
## 6. Fase 5 – CI da S19

Objetivo: conectar a Sprint 19 ao CI, mantendo o mesmo padrão das sprints anteriores.

Diretório alvo:

- `.github/workflows`

Arquivo sugerido:

- `_s19_timeline_xray.yml`

Tarefas:

1. Configurar job de CI da S19 para rodar, pelo menos:
   - script de qualidade de front de admin da S19;
   - um recorte representativo de timeline e raio‑X (ou scripts específicos da S19 que encapsulem isso).

2. Upload de artefatos relevantes:
   - scorecards da S19;
   - evidências principais (ou pacote único zip de out/evidence da S19).

3. S19_G7 deve verificar a existência e o wiring desse workflow.

Critério de aceite Fase 5

- Workflow visível na aba de Actions;
- Execução da pipeline da S19 completando com sucesso em PR relevante.

---
## 7. Fase 6 – Validação Local Completa e Resumo da Sprint

Objetivo: rodar a bateria final local e produzir o resumo humano da sprint para ORR.

### 7.1 Checks finais locais

1. Backend
   - rodar testes de admin gerais;
   - rodar testes de timeline e raio‑X.

2. Frontend
   - lint;
   - testes com coverage da S19;
   - build de produção da SPA.

3. Gates S19
   - rodar agregador s19_all;
   - rodar s19_g8_go_no_go e garantir decisão GO.

### 7.2 Resumo humano da S19

Arquivo sugerido:

- `docs/sprint_19_orr_summary.md`

Conteúdo mínimo:

- objetivo claro da sprint;
- estado dos gates S19_G0 a S19_G8;
- leitura de alto nível das métricas M1 a M6 no contexto da Timeline e do Raio‑X;
- resumo de entregas em backend, frontend, fixtures, gates e CI;
- riscos e débitos técnicos empurrados;
- decisão GO ou NO‑GO coerente com S19_G8.

Critério de aceite Fase 6

- Todos os testes e gates verdes;
- resumo humano consistente com scorecards e evidências.

---
## 8. Definição de Pronto (DoD) – Sprint 19

A S19 só está concluída quando TODOS os itens abaixo forem verdadeiros:

1. Backend
   - endpoints de Timeline e Raio‑X existem e passam nos testes;
   - contratos de S17 e S18 continuam válidos.

2. Frontend
   - Timeline e Raio‑X acessíveis a partir do Console de Admin;
   - UI legível, com eventos ordenados e seções de Raio‑X completas.

3. Fixtures e testes
   - fixtures da S19 em Sprint 19 são consumidas por backend, gates e frontend;
   - testes dedicados da S19 estão verdes.

4. Gates e CI
   - todos os scorecards da S19 estão em status PASS;
   - decisão final de S19_G8 é GO;
   - workflow de CI da S19 está configurado e rodando com sucesso.

5. Documentação
   - docs da S19 atualizados, incluindo sprint_19_orr_summary;
   - caminho de evidências é rastreável de ponta a ponta.

Com isso, a Sprint 19 se consolida como a camada de diagnóstico profundo do Inspectah: a ponte que liga a consulta do usuário final (S17) e o cockpit de admin (S18) a uma visão forense e temporal de como cada caso evoluiu dentro da Truth‑DB e do Sistema de Blocos.

