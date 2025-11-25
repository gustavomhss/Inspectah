# Sprint 21.2 — Capítulo 3 (Filemap, Arquitetura e Pontes com S21 / S21.1) — v2

Título interno: Copiloto de Fontes v2 — Mapa Definitivo de Arquivos, Módulos e Gates

Este capítulo é o mapa de verdade da Sprint 21.2 dentro do repositório Inspectah. Ele responde, sem margem para interpretação:

– Onde cada conceito da 21.2 mora no repo.
– Como cada arquivo se conecta a S21 e S21.1.
– Qual gate S21_2_G* depende de qual conjunto de arquivos.
– Como um dev (ou o Codex) consegue navegar de um problema até o arquivo exato, sem caça ao tesouro.

Nada da 21.2 existe “por fora” deste filemap. Se não está mapeado aqui, não faz parte da sprint.

Raiz local:

/Users/gustavoschneiter/Documents/Inspectah

A partir dela, organizamos a 21.2 em oito blocos:

1. Documentação (docs/ + pastas Sprint 21, 21.1 e 21.2).
2. Domínio de Fontes (app/sources/).
3. Copiloto de Fontes (agents, routers, services).
4. Frontend (Console + widget de Copiloto).
5. Testes (tests/ + testes de frontend).
6. Scripts de gates (bin/).
7. Artefatos de execução (out/evidence/ e out/scorecards/).
8. Branches, disciplina de git e acoplamento entre sprints.

Cada seção abaixo aponta explicitamente: arquivos, responsabilidades e gates.

1. Documentação (S21, S21.1, S21.2)

1.1 Documentos base da Sprint 21 (console de fontes)

Esses arquivos são a fundação do domínio de fontes. A S21.2 depende deles e pode apenas estendê-los de forma compatível:

docs/sprint_21_capitulo_1.md
docs/sprint_21_capitulo_2_gates.md
docs/sprint_21_capitulo_3_filemap.md
docs/sprint_21_capitulo_4_execucao.md

docs/sprint_21_ontologia_fontes.md
docs/sprint_21_modelo_dados_fontes.md
docs/sprint_21_ciclo_vida_fontes.md
docs/sprint_21_fluxos_admin_fontes.md
docs/sprint_21_ganchos_debunker_fontes.md
docs/sprint_21_cenarios_uso_fontes.md

docs/sprint_21_scorecard_console_fontes.md
docs/sprint_21_wrap_execucao.md

Aqui vivem a ontologia original de fontes, o modelo de dados base (sem os refinamentos de refresh e tipo oficial aberta) e os fluxos admin “versão 1”. A Sprint 21.2 lê e respeita estes contratos.

1.2 Documentos específicos da Sprint 21.1 (Copiloto v1)

A 21.1 introduziu o Copiloto de Fontes v1. Seus documentos continuam válidos e são tratados como camada imediatamente abaixo da 21.2:

docs/sprint_21_1_capitulo_1.md
docs/sprint_21_1_capitulo_2_gates.md
docs/sprint_21_1_capitulo_3_filemap.md
docs/sprint_21_1_capitulo_4_execucao.md

docs/sprint_21_1_modo_agente_copiloto.md
docs/sprint_21_1_politica_seguranca_copiloto.md
docs/sprint_21_1_cenarios_copiloto_fontes.md

docs/sprint_21_1_scorecard_copiloto_fontes.md
docs/sprint_21_1_wrap_execucao.md

A 21.2 não apaga esses docs; ela os estende. Sempre que houver conflito, a 21.2 deve atualizar explicitamente o doc da 21.1 ou registrar uma “versão 2” clara, sem ambiguidade.

1.3 Documentos da Sprint 21.2 (núcleo da sprint)

A 21.2 adiciona a sua própria camada documental:

docs/sprint_21_2_capitulo_1.md
Docs/sprint_21_2_capitulo_2_gates.md
docs/sprint_21_2_capitulo_3_filemap.md
Docs/sprint_21_2_capitulo_4_execucao.md

docs/sprint_21_2_ontologia_fontes_v2.md
docs/sprint_21_2_fluxos_admin_fontes_v2.md
docs/sprint_21_2_maquina_estados_copiloto.md

docs/sprint_21_2_politica_seguranca_copiloto_v2.md
docs/sprint_21_2_scorecard_copiloto_v2.md
docs/sprint_21_2_wrap_execucao.md

Cada doc ancora gates específicos:

S21_2_G0: sprint_21_2_capitulo_1.md, mais referência cruzada com todos os docs S21/S21.1.
S21_2_G1: sprint_21_modelo_dados_fontes.md (atualizado) e sprint_21_2_ontologia_fontes_v2.md.
S21_2_G2: sprint_21_2_fluxos_admin_fontes_v2.md e sprint_21_2_maquina_estados_copiloto.md.
S21_2_G6: sprint_21_2_politica_seguranca_copiloto_v2.md.
S21_2_G7: sprint_21_2_scorecard_copiloto_v2.md e sprint_21_2_wrap_execucao.md.
S21_2_G8: sprint_21_2_wrap_execucao.md como fonte humana final da decisão.

Regra global: nenhum comportamento novo entra em código sem aparecer primeiro em docs.

2. Domínio de Fontes (app/sources/)

O domínio de fontes continua centralizado em app/sources/. A 21.2 o expande, sem quebrar a S21:

app/sources/__init__.py
app/sources/models.py
app/sources/schemas.py
app/sources/service.py
app/sources/validators.py
app/sources/healthcheck.py
app/sources/routes_admin.py

A 21.2 adiciona três eixos principais aqui:

Refresh interval: campo persistido, validado e exposto na API.
Tipos refinados de fonte: incluindo tipo explícito de fonte oficial aberta.
Máquina de status endurecida: estados e transições claras e centralizadas.

2.1 Refresh interval

models.py:

Inclui um campo refresh_interval (inteiro ou estrutura mais rica) no modelo Source. Esse campo representa a frequência sugerida de refresh da fonte, alinhado ao que aparece na UI e no agente.

schemas.py:

Inclui refresh_interval nas classes de input/output do domínio admin: SourceCreate, SourceUpdate, SourceRead ou equivalentes.

service.py:

Aplica defaults sensatos para refresh_interval quando o admin não informar explicitamente.
Valida combinações inválidas (por exemplo, refresh muito agressivo para fontes manuais).

Essa trilha de campos suporta diretamente S21_2_G1, S21_2_G3 e S21_2_G7 (verificação de refresh configurado).

2.2 Tipos de fonte e fonte oficial aberta

Em models.py ou em um módulo dedicado de enums, a 21.2 garante a existência de um tipo formal de fonte oficial aberta, por exemplo:

SourceType.OFFICIAL_OPEN

Esse tipo aparece em:

models.py: como valor de enum permitido para o campo type.
schemas.py: aceito nos payloads.
validators.py: com regras específicas; por exemplo, exigir descrição e URL acessível publicamente.
service.py: aplicando qualquer lógica extra para oficiais abertas, se necessário.

Ele é a âncora técnica do que os docs descrevem como “fontes oficiais que não têm API, mas expõem dados abertos em páginas, PDFs, etc.”.

2.3 Status e máquina de estados da fonte

S21 já define estados básicos; a 21.2 torna isso explícito e coeso. Opcionalmente, extrai-se a lógica para um módulo dedicado:

app/sources/status.py

Este módulo conteria:

Enum de status (PENDING, ACTIVE, SUSPENDED, DISABLED, etc.).
Tabela de transições válidas (por exemplo, PENDING → ACTIVE, ACTIVE → SUSPENDED, SUSPENDED → ACTIVE, etc.).
Helpers de domínio como can_transition(from_status, to_status) e apply_status_change(source, to_status).

O serviço service.py passa a delegar as validações de status a esse módulo, evitando espalhar lógica de if/else pelo código.

2.4 Relação com gates

S21_2_G1: refresh_interval e tipo oficial aberta existem e estão conectados a docs.
S21_2_G2: máquina de status de fonte faz par com a máquina de estados do Copiloto.
S21_2_G3: endpoints admin de fonte expõem e respeitam esses campos.
S21_2_G5: tools do Copiloto consultam o domínio e não reimplementam regras.

3. Copiloto de Fontes (agents, routers, services)

3.1 Routers e serviços HTTP

O Copiloto de Fontes v2 fala com o mundo através de:

inspectah/api.py
inspectah/routers/copiloto_fontes.py
inspectah/services/copiloto_sessions.py
inspectah/services/copiloto_files.py

O papel de cada arquivo:

inspectah/api.py: registra o router copilot_fontes_router no app FastAPI principal.
inspectah/routers/copiloto_fontes.py: define endpoints para criar/recuperar sessões, enviar mensagens e fazer upload de arquivos.
inspectah/services/copiloto_sessions.py: persiste sessões de conversa do Copiloto (em memória ou storage leve), incluindo agent_mode, tipo de fonte desejada, estado da FSM.
inspectah/services/copiloto_files.py: persiste metadados de arquivos enviados pelo admin e os torna acessíveis para tools do agente.

A 21.2 garante que:

Todos os endpoints aceitam agent_mode e retornam, quando apropriado, actions detalhadas (preencher_campos, sugerir_edit, sugerir_status_change) e não apenas mensagens.
Sessões são restauráveis (o frontend pode reanexar a mesma sessão em telas de edição).
Uploads de arquivos ficam associados à sessão e disponíveis para leitura por tools.

3.2 Agent e tools do Copiloto

A base do agente veio da S21.1 e vive em:

inspectah/agents/s21_1_copiloto_fontes.py
inspectah/agents/tools/form_state.py
inspectah/agents/tools/file_reader.py
inspectah/agents/tools/logging.py

A 21.2 evolui essa base para comportar fluxos guiados por tipo de fonte, edição, status e refresh, mantendo a compatibilidade de interface com o router. Se necessário, acrescenta módulos auxiliares:

inspectah/agents/copiloto_fontes_fsm.py
inspectah/agents/tools/source_reader.py
inspectah/agents/tools/status_planner.py
inspectah/agents/tools/update_planner.py

Funções típicas:

copiloto_fontes_fsm.py: define estados de conversa (escolher_tipo, coletar_dados, preencher_lacunas, revisar, pronto_para_salvar, etc.) e as transições entre eles.
source_reader.py: abstrai a leitura de uma fonte existente por source_id, para casos de edição.
status_planner.py: dado o estado atual da fonte e um objetivo (aprovar, suspender, reativar), propõe um plano de mudança de status que o Copiloto apresenta ao admin.
update_planner.py: gera uma visão “antes/depois” de campos que o Copiloto pretende atualizar, para o admin aprovar.

O agent s21_1_copiloto_fontes.py passa a orquestrar tudo:

Recebe mensagens do usuário e contexto da fonte (se estiver editando).
Chama as tools certas conforme o estado da FSM.
Respeita agent_mode (on: mais proativo; off: mais explicativo e conservador).
Retorna ações estruturadas que o frontend aplica ao formulário.

3.3 Relação com gates

S21_2_G2: FSM do Copiloto mapeada em copilot_fontes_fsm.py e casada com docs.
S21_2_G3: router e serviços compõem a API do Copiloto.
S21_2_G5: comportamento e tools do agente são validados nos testes.
S21_2_G6: safety e escopo são aplicados dentro do agente.

4. Frontend (Console + Copiloto)

4.1 Rotas e clients de API

No frontend, o Console de Fontes e o Copiloto ficam na árvore:

frontend/inspectah-ui/src/app/routes.tsx

frontend/inspectah-ui/src/core/api/api-types.ts
frontend/inspectah-ui/src/core/api/http-client.ts

frontend/inspectah-ui/src/modules/admin/api/index.ts
frontend/inspectah-ui/src/modules/admin/api/copilotoClient.ts

A 21.2 garante que:

api-types.ts está sincronizado com o contrato de fontes (incluindo refresh_interval e o tipo oficial aberta) e com o contrato do Copiloto (agent_mode, tipos de ação, payloads de plano de edição/status).
http-client.ts suporta requisições JSON e multipart/form-data para upload de arquivos.
copilotoClient.ts encapsula todas as operações de backend do Copiloto: criar sessão, enviar mensagem, anexar arquivo.

4.2 Páginas e componentes de admin

As páginas principais do Console de Fontes são:

frontend/inspectah-ui/src/modules/admin/pages/AdminSourcesPage.tsx
frontend/inspectah-ui/src/modules/admin/pages/AdminSourceFormPage.tsx
frontend/inspectah-ui/src/modules/admin/pages/AdminSourceDetailPage.tsx
frontend/inspectah-ui/src/modules/admin/pages/AdminOverviewPage.tsx
frontend/inspectah-ui/src/modules/admin/pages/AdminCasesPage.tsx

E os componentes de UI de fontes e status:

frontend/inspectah-ui/src/modules/admin/components/SourceStatusBadge.tsx
frontend/inspectah-ui/src/modules/admin/components/SourcesTable.tsx

O Copiloto aparece como um conjunto de componentes e um hook central:

frontend/inspectah-ui/src/modules/admin/hooks/useCopilotoAgent.ts

frontend/inspectah-ui/src/modules/admin/components/CopilotoWidget.tsx
frontend/inspectah-ui/src/modules/admin/components/CopilotoChatPanel.tsx
frontend/inspectah-ui/src/modules/admin/components/CopilotoMessageList.tsx
frontend/inspectah-ui/src/modules/admin/components/CopilotoInputBar.tsx
frontend/inspectah-ui/src/modules/admin/components/CopilotoFileAttachment.tsx

A Sprint 21.2 exige que:

AdminSourceFormPage.tsx abra o Copiloto automaticamente ao criar nova fonte, impeça o cadastro sem ao menos uma interação com o Copiloto e exiba descrições curtas em todos os campos críticos.
AdminSourceDetailPage.tsx mostre o Copiloto com contexto da fonte, permita edição assistida de campos (tema, endpoint, refresh) e ofereça controles de status coerentes com o domínio.
AdminSourcesPage.tsx e SourcesTable.tsx mostrem o tipo de fonte (incluindo oficial aberta), status e refresh de forma legível e filtrável.
CopilotoWidget e useCopilotoAgent exponham claramente o agent_mode (com toggle visual) e apliquem as ações retornadas pelo agente ao formulário, sempre de forma visível e revisável pelo admin.

4.3 Relação com gates

S21_2_G4: vive essencialmente nesses arquivos.
S21_2_G7: os cenários ponta-a-ponta C1–C6 são executados através dessas telas.

5. Testes (tests/ + frontend)

5.1 Testes de domínio de fontes

A S21 já trouxe testes básicos em tests/sources. A 21.2 os estende com foco em refresh, tipo oficial e status:

tests/sources/test_domain_model.py (já existente, ampliado para cobrir refresh e tipo oficial)
tests/sources/test_service.py (já existente, cobrindo service com campos novos)

tests/sources/test_s21_2_refresh_and_official_type.py
Criação de fonte com refresh e tipo oficial aberta.
Validações de domínio para combinações inválidas.

tests/sources/test_s21_2_status_transitions.py
Máquina de status: transições válidas/ inválidas.
Caminho feliz para aprovar, suspender, reativar e desativar.

Esses arquivos sustentam S21_2_G1, S21_2_G3 e S21_2_G2 (status vs docs).

5.2 Testes de agente e Copiloto

A base da 21.1 já incluía:

tests/agents/test_s21_1_copiloto_mode_agent.py

A 21.2 adiciona:

tests/agents/test_s21_2_copiloto_flows.py
Cenários guiados de criação (notícias, oficial aberta).
Cenários de edição (refresh, temas, endpoint).
Cenários de mudança de status com plano.
Variante com agent_mode on/off.

tests/agents/test_s21_2_copiloto_safety.py
Casos de escopo: tentativas de falar de verdades/fatos, Debunker, casos, timelines.
Casos de operações destrutivas: tentar desativar fonte à força.
Casos específicos de fontes oficiais (limites do agente).

Esses arquivos sustentam S21_2_G3, S21_2_G5 e S21_2_G6.

5.3 Testes de frontend

Na estrutura atual do projeto, os testes de frontend podem viver em:

frontend/inspectah-ui/src/modules/admin/__tests__/AdminSourceFormPage.test.tsx
frontend/inspectah-ui/src/modules/admin/__tests__/AdminSourceDetailPage.test.tsx
frontend/inspectah-ui/src/modules/admin/__tests__/CopilotoWidget.test.tsx

Responsabilidades principais:

Simular fluxo de criação de fonte via UI, com Copiloto abrindo automaticamente e influenciando o formulário.
Simular fluxo de edição de fonte, incluindo mudança de status e refresh.
Verificar que o toggle de agent_mode altera o comportamento do widget (por exemplo, mais propositivo em on, mais descritivo em off).

Esses testes amarram S21_2_G4 a comportamentos verificáveis e reforçam S21_2_G7.

6. Scripts de Gates (bin/)

Os scripts da Sprint 21.2 seguem rigorosamente o padrão das sprints anteriores:

bin/s21_2_g0_contexto.sh
bin/s21_2_g1_ontologia.sh
bin/s21_2_g2_fluxos_fsm.sh
bin/s21_2_g3_backend_api.sh
bin/s21_2_g4_frontend_ux.sh
bin/s21_2_g5_agent_tools.sh
bin/s21_2_g6_safety.sh
bin/s21_2_g7_scorecard_experiencia.sh
bin/s21_2_g8_go_no_go.sh

bin/s21_2_all_gates.sh

Cada script:

Exporta PYTHONPATH=.
Roda os comandos necessários (pytest, npm, scripts auxiliares).
Escreve logs e artefatos em out/evidence/S21_2_G*/.
Escreve o scorecard em out/scorecards/S21_2_G*.json.
Sai com exit 0 apenas se o gate estiver PASS.

O all_gates orquestra G0–G7 e deixa G8 explícito para uso humano/CI.

7. Artefatos de Execução (out/evidence/ e out/scorecards/)

A 21.2 replica a estrutura das sprints anteriores, apenas com prefixo S21_2_:

out/evidence/S21_2_G0_contexto/
out/evidence/S21_2_G1_ontologia/
out/evidence/S21_2_G2_fluxos/
out/evidence/S21_2_G3_backend/
out/evidence/S21_2_G4_frontend/
out/evidence/S21_2_G5_agent/
out/evidence/S21_2_G6_safety/
out/evidence/S21_2_G7_experiencia/
out/evidence/S21_2_G8_go_no_go/

out/scorecards/S21_2_G0_contexto.json
out/scorecards/S21_2_G1_ontologia.json
out/scorecards/S21_2_G2_fluxos.json
out/scorecards/S21_2_G3_backend.json
out/scorecards/S21_2_G4_frontend.json
out/scorecards/S21_2_G5_agent.json
out/scorecards/S21_2_G6_safety.json
out/scorecards/S21_2_G7_scorecard.json
out/scorecards/S21_2_G8_go_no_go.json

Esse padrão garante que qualquer execução local reproduza fielmente o estado da sprint, sem depender de contexto externo.

8. Branches, disciplina de git e acoplamento entre sprints

A Sprint 21.2 vive em uma branch dedicada, por exemplo:

feature/s21_2_copiloto_fontes_v2

Disciplina sugerida:

Commits sempre temáticos, com prefixo s21_2 no título.
Nada de out/ e .pyc no controle de versão; são artefatos efêmeros.
Antes de qualquer merge para main:

pytest tests/sources -q
pytest tests/agents -q
cd frontend/inspectah-ui && npm run lint && npm test && npm run build
bash bin/s21_all_gates.sh
bash bin/s21_1_all_gates.sh
bash bin/s21_2_all_gates.sh

O merge só é aprovado se:

Todos os gates da S21, S21.1 e S21.2 estiverem verdes.
O wrap de execução da S21.2 recomendar GO.

9. Resumo: Gate → Arquivos-chave

S21_2_G0 (Contexto)

Docs: sprint_21_2_capitulo_1.md, sprint_21_* e sprint_21_1_*.
Scripts/logs: bin/s21_2_g0_contexto.sh, out/evidence/S21_2_G0_contexto/*, out/scorecards/S21_2_G0_contexto.json.

S21_2_G1 (Ontologia e Modelo)

Docs: sprint_21_modelo_dados_fontes.md, sprint_21_2_ontologia_fontes_v2.md.
Código: app/sources/models.py, app/sources/schemas.py, app/sources/service.py, validators/status se existirem.
Artefatos: out/evidence/S21_2_G1_ontologia/*, out/scorecards/S21_2_G1_ontologia.json.

S21_2_G2 (Fluxos e FSM)

Docs: sprint_21_2_fluxos_admin_fontes_v2.md, sprint_21_2_maquina_estados_copiloto.md.
Código: inspectah/agents/s21_1_copiloto_fontes.py, inspectah/agents/copiloto_fontes_fsm.py (separado ou embutido).
Artefatos: out/evidence/S21_2_G2_fluxos/*, out/scorecards/S21_2_G2_fluxos.json.

S21_2_G3 (Backend API)

Docs: sprint_21_2_capitulo_2_gates.md (seção de G3).
Código: app/sources/routes_admin.py, app/sources/service.py, inspectah/routers/copiloto_fontes.py, inspectah/services/copiloto_sessions.py, inspectah/services/copiloto_files.py.
Testes: tests/sources/*, tests/agents/*s21_1* e *s21_2*.
Artefatos: out/evidence/S21_2_G3_backend/*, out/scorecards/S21_2_G3_backend.json.

S21_2_G4 (Frontend e UX)

Docs: sprint_21_2_capitulo_2_gates.md (seção de G4).
Código: AdminSourceFormPage.tsx, AdminSourceDetailPage.tsx, AdminSourcesPage.tsx, SourceStatusBadge.tsx, components do Copiloto, useCopilotoAgent.ts.
Testes: __tests__ de admin e do Copiloto.
Artefatos: out/evidence/S21_2_G4_frontend/*, out/scorecards/S21_2_G4_frontend.json.

S21_2_G5 (Agent e Tools)

Docs: sprint_21_2_maquina_estados_copiloto.md.
Código: inspectah/agents/s21_1_copiloto_fontes.py, inspectah/agents/copiloto_fontes_fsm.py, inspectah/agents/tools/*.py.
Testes: tests/agents/test_s21_2_copiloto_flows.py.
Artefatos: out/evidence/S21_2_G5_agent/*, out/scorecards/S21_2_G5_agent.json.

S21_2_G6 (Safety)

Docs: sprint_21_1_politica_seguranca_copiloto.md, sprint_21_2_politica_seguranca_copiloto_v2.md.
Código: trechos de safety dentro do agente e configuração de logging.
Testes: tests/agents/test_s21_2_copiloto_safety.py.
Artefatos: out/evidence/S21_2_G6_safety/*, out/scorecards/S21_2_G6_safety.json.

S21_2_G7 (Experiência Ponta-a-Ponta)

Docs: sprint_21_2_scorecard_copiloto_v2.md, sprint_21_2_wrap_execucao.md.
Código: principalmente frontend (telas de admin) + agente.
Artefatos: out/evidence/S21_2_G7_experiencia/*, out/scorecards/S21_2_G7_scorecard.json.

S21_2_G8 (GO/NO_GO)

Docs: sprint_21_2_wrap_execucao.md.
Código: bin/s21_2_g8_go_no_go.sh.
Artefatos: out/evidence/S21_2_G8_go_no_go/*, out/scorecards/S21_2_G8_go_no_go.json.

Com esse filemap v2, a S21.2 deixa de ser apenas uma ideia sobre o Copiloto de Fontes v2 e passa a ser um bloco estruturalmente sólido no repositório: cada comportamento tem um endereço, um gate, um teste e uma evidência correspondentes.

