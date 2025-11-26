# Inspectah — Sprint 23 – Capítulo 2: Gates de Validação

## Visão geral dos gates da Sprint 23

Objetivo da Sprint 23: projetar, especificar e validar a **primeira geração do Sistema de Agentes do Inspectah** para interpretação, classificação/organização e debunk/tripla redundância, com:

- Console de agentes para admins (configuração estilo “GPT customizado”).
- Registro unificado de agentes, perfis, modelos e KBs anexas.
- Política de modelos (modelo recomendado, overrides, buffer de adoção de modelos novos).
- Pipeline em camadas com **tripla redundância por etapa** (dois debunkers + 1 mediador).
- Artefatos e diretrizes transparentes e auditáveis para cada agente/camada.

Os gates abaixo garantem que nada entra em produção sem:

- Modelo conceitual sólido (ontologia de agentes, camadas, papéis).
- Contratos formais entre backend, UI e orquestração de agentes.
- Cenários de teste que cubram desde o “happy path” até casos adversariais.
- Evidências claras e repetíveis de que a tripla redundância funciona e é auditável.

Numeração de gates da Sprint 23: **S23_G0 a S23_G7**, mais o **wrap de ORR** (S23_orr) que consolida tudo.

---

## S23_G0 – Contexto, escopo e alinhamento com o produto

**Objetivo**  
Garantir que toda a equipe entenda exatamente **o que o Sistema de Agentes da Sprint 23 cobre** (e o que fica para sprints futuras), evitando overreach ou gaps conceituais.

**O que este gate valida**

- Escopo da Sprint 23 está alinhado com o plano macro (S21–S25) e com a visão de produto do Inspectah.
- Limites claros entre o que é entregue agora e o que fica para S24+ (ex.: Debunker v1 mais completo, UI avançada de auditoria pública, etc.).
- Papéis das camadas de agentes:
  - Camada A: **Interpretação & normalização semântica** (ler textos, notícias, documentos, etc.).
  - Camada B: **Classificação & organização** (taxonomias, temas, info_types, casos/timelines).
  - Camada C: **Debunk & verificação cética** (questionar, procurar inconsistências, solicitar evidências adicionais).
  - Camada D: **Mediação & consenso** (terceiro elemento que recebe relatórios dos dois céticos e decide GO/NO-GO por etapa).
- Escopo do **console de agentes**: o que já precisa existir na S23 (CRUD + configuração base) e o que será plugado depois.

**Critérios de aprovação**

- Documento `docs/sprint_23_capitulo_1_contexto.md` está revisado, sem TODOs ou “pendente definir”.
- Matriz “Escopo agora vs futuro” explícita, citando claramente o que **não** será feito na S23.
- Mapa de camadas e papéis de agentes consolidado e sem ambiguidades.

**Evidências esperadas**

- `docs/sprint_23_capitulo_1_contexto.md` (vFinal), referenciando S21–S22 e S24.
- `docs/sprint_23_g0_summary.md` com checklist de escopo e decisões de fora de escopo.

---

## S23_G1 – Ontologia de agentes, camadas e papéis (modelos & invariantes)

**Objetivo**  
Definir, de forma formal e estável, a **ontologia dos agentes**, incluindo tipos, papéis, camadas, relações e invariantes que não podem ser quebrados.

**O que este gate valida**

- Modelo conceitual dos agentes:
  - Tipos de agente: `INTERPRETADOR`, `CLASSIFICADOR`, `DEBUNKER`, `MEDIADOR`, `PIPELINE_ORCHESTRATOR` (se existir), etc.
  - Papéis dentro de cada camada: `DEBUNKER_A`, `DEBUNKER_B`, `MEDIADOR`.
  - Relação com fontes, casos, timelines e blocos da Truth-DB.
- Invariantes críticos, por exemplo:
  - Cada decisão relevante do sistema passa por **no mínimo 2 agentes céticos + 1 mediador** na camada correspondente.
  - Nenhum agente debunker/mediador escreve diretamente em Truth-DB sem passar pelo pipeline de consenso configurado.
  - Toda execução de agente gera um **AgentRun** com input, output, metadata de modelo, versão, timestamp e evidência.
- Tipos de “conhecimento” anexado a agentes (KBs): arquivos, conjuntos de instruções, exemplos de decisão, anti-padrões, blacklists.
- Mapa de modelos (GPT-Plus, etc.) e como os agentes referenciam o “modelo recomendado” e overrides.

**Critérios de aprovação**

- Ontologia formal documentada em um arquivo único, sem contradições com S21–S22.
- Lista explícita de invariantes com justificativa (por que existem, que problema evitam).
- Nenhum agente “mágico” ou genérico demais: todos os tipos têm definição clara.

**Evidências esperadas**

- `docs/sprint_23_ontologia_agentes.md` (ou equivalente definido no capítulo 1).
- `docs/sprint_23_modelos_e_invariantes.md` com a lista de invariantes, exemplos e anti-exemplos.
- Eventuais diagramas (mesmo em ASCII/markdown) ilustrando camadas e fluxos.

---

## S23_G2 – Modelo de dados e contratos de serviço (registry + console de agentes)

**Objetivo**  
Fechar o **modelo de dados e os contratos de serviço** que sustentam o registry de agentes e o console de configuração, garantindo que tudo seja versionável, auditável e fácil de manter.

**O que este gate valida**

- Modelo de dados para o **Agent Registry**:
  - Entidades mínimas: `Agent`, `AgentProfile`, `AgentVersion`, `AgentKB`, `AgentPolicy`, `AgentRun`, `AgentCommittee`.
  - Campos inspirados no fluxo “Criar GPT customizado”: nome, descrição, instruções, modelo recomendado, arquivos/KBs anexos, tags, camada/papel, etc.
  - Campos extra específicos do Inspectah: janela de contexto de decisões, targets (tipos de fonte, tipos de caso), “modo cético”/“modo mediador”, etc.
- Contratos de serviço:
  - API Admin para CRUD de agentes, perfis, versões e KBs (endpoints, payloads, schemas de request/response).
  - API para agendar/rodar execuções de agentes em pipeline (ex.: `/admin/agents/{id}/test-run`, `/admin/agent-committees/{id}/simulate`).
- Política de versionamento:
  - Cada mudança relevante nas instruções ou KB cria uma nova versão, com changelog mínimo.
  - Históricos de mudanças são persistidos e consultáveis.

**Critérios de aprovação**

- Schema de agentes e related (pydantic/SQLAlchemy) está definido e revisado.
- Contratos de API documentados com exemplos concretos (happy path e casos de erro).
- Não existe acoplamento “hard-coded” a um modelo específico de IA; tudo passa por referências configuráveis.

**Evidências esperadas**

- `docs/sprint_23_modelo_dados_agentes.md`.
- `docs/sprint_23_contratos_servico_agentes.md` com tabelas ou trechos OpenAPI.
- Se aplicável, migrations esboçadas em `migrations/versions/000x_s23_agents_*.py` ainda que marcadas como “draft” (sem rodar).

---

## S23_G3 – Maquina de estados e pipelines em camadas (tripla redundância)

**Objetivo**  
Definir a **FSM (finite state machine)** das execuções de agentes e dos comitês em tripla redundância, garantindo previsibilidade, rastreabilidade e ausência de estados zumbi.

**O que este gate valida**

- Maquina de estados de um **AgentRun** (unidade atômica de execução de um agente):
  - Estados típicos: `PENDING`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED`, `SKIPPED`.
  - Eventos que causam transições (ex.: `start`, `retry`, `timeout`, `cancel`, `force_fail`).
  - Regras de timeout e retentativas (policy-based, configuráveis).
- Maquina de estados de um **AgentCommitteeRun** (tripla redundância):
  - Estados: `PENDING`, `DEBUNKERS_RUNNING`, `WAITING_MEDIATOR`, `CONSENSUS_REACHED`, `CONSENSUS_FAILED`, `CANCELLED`.
  - Como os outputs dos debunkers são agregados e apresentados ao mediador.
  - Como o mediador decide GO/NO-GO e se existe espaço para “NEEDS_MORE_EVIDENCE”.
- Integração com o pipeline macro do Inspectah:
  - Onde estas FSMs plugarão nas sprints futuras (Debunker v0, Truth-DB, etc.).
  - Garantias de que nenhum bloco é promovido sem passar por ao menos uma cadeia de comitês bem definida.

**Critérios de aprovação**

- FSM desenhada em pelo menos um formato inequívoco (tabela, diagrama textual, pseudocódigo ou similar).
- Nenhum estado sem saída ou estado inalcançável.
- Regras de timeout → falha claras, principalmente para evitar “RUNNING eterno” versão agentes.

**Evidências esperadas**

- `docs/sprint_23_maquina_estados_agentes.md` com FSMs de AgentRun e AgentCommittee.
- Pequenos exemplos de traces (executando em texto) que mostram fluxo normal e fluxos de erro.

---

## S23_G4 – Política de modelos, updates e buffers de adoção

**Objetivo**  
Fechar a política que controla **quais modelos de IA cada agente usa**, como upgrades de modelo são adotados (ou adiados) e como isso é exposto no console admin.

**O que este gate valida**

- Esquema de configuração de modelos por agente:
  - `recommended_model` (sempre apontando para o “mais atual do ChatGPT Plus” por padrão).
  - `override_model` (quando o admin quiser algo diferente, por exemplo fallback ou modelo mais barato para testes).
  - Flags de “canary / rollout gradual” se aplicável.
- Política de atualização global:
  - Chave geral de “usar o modelo mais recente disponível” com **buffer configurável** (ex.: 15 dias).
  - Modo de pausar/adiantar esse buffer por decisão explícita do admin.
  - Registro de quando um modelo foi trocado e qual impacto esperado (pelo menos descritivo).
- Transparência:
  - Para cada decisão/AgentRun relevante, persistir qual modelo foi usado (nome, versão ou alias estável).
  - Console permite ver “quais agentes estão usando que modelos” de forma rápida.

**Critérios de aprovação**

- Documento de política de modelos claro e livre de ambiguidades.
- Campos necessários já planejados no modelo de dados de `Agent`/`AgentPolicy`.
- Estratégia para lidar com mudanças de comportamento entre modelos (observabilidade mínima, ex.: métricas de divergência entre versões em ambiente de teste).

**Evidências esperadas**

- `docs/sprint_23_politica_modelos_agentes.md`.
- Esboço de tela ou checklist de UI mostrando como o admin enxerga/edita essas opções.

---

## S23_G5 – Console de agentes (UX, auditabilidade e transparência)

**Objetivo**  
Definir e validar o **Console de Agentes** para admins, inspirado na experiência de criar/editar um GPT customizado, mas com camadas extras de transparência e auditabilidade.

**O que este gate valida**

- Fluxos principais de UI:
  - Listar agentes (com filtros por camada, papel, status, modelo, etc.).
  - Ver detalhe de um agente (nome, descrição, instruções, camada, papel, modelos, KBs anexas, histórico de versões).
  - Criar/editar agente, incluindo:
    - Nome, descrição, instruções.
    - Camada/papel (interpretador/classificador/debunker/mediador).
    - Anexar/remover arquivos de KB.
    - Escolher modelo recomendado / override.
    - Configurar participação em comitês (ex.: “Debunker A na camada de Interpretação”).
  - Visualizar histórico de AgentRuns e CommitteeRuns (timeline mínima para admins).
- Requisitos de transparência/auditabilidade:
  - Para qualquer decisão posterior, deve ser possível clicar e enxergar **qual agente**, **com quais instruções**, **com qual modelo** e **com quais KBs** participou.

**Critérios de aprovação**

- Protótipo de telas (mesmo que em markdown ou descrição minuciosa) cobrindo todos os fluxos acima.
- Lista clara de campos obrigatórios e opcionais no formulário de criação/edição.
- Não há ambiguidade entre fluxo de “editar agente existente” e “criar nova versão”.

**Evidências esperadas**

- `docs/sprint_23_console_agentes_ux.md` com fluxos, wireframes textuais e cenários de uso.
- Se já existirem componentes React pensados, pseudo-filemap de front (`frontend/inspectah-ui/src/modules/agents/...`).

---

## S23_G6 – Segurança, safety e limites dos agentes

**Objetivo**  
Garantir que o desenho dos agentes considere **segurança, abuse-prevention e safety**, especialmente porque eles vão operar sobre temas sensíveis (política, saúde, desinformação, etc.).

**O que este gate valida**

- Diretrizes de safety por camada/papel:
  - O que um interpretador pode/não pode fazer (por exemplo, não “inventar” fatos, apenas resumir e estruturar).
  - O que um classificador pode/não pode inferir (limites de inferência sobre atributos sensíveis, etc.).
  - Como os debunkers devem se comportar (céticos, mas não sensacionalistas nem tendenciosos).
- Integração com políticas globais de safety (inclusive as da própria OpenAI, quando aplicável).
- Mecanismos para **limitar escopo de decisão** de cada agente:
  - Agentes não alteram diretamente configurações críticas sem review humano.
  - Logs detalhados e imutáveis de execuções de agentes.
- Cenários adversariais mapeados:
  - Inputs maliciosos (prompt injection, tentativas de burlar a política).
  - Casos de política sensível (eleições, saúde crítica, etc.) e como o sistema se protege.

**Critérios de aprovação**

- Documento de política de segurança dos agentes claro e alinhado com a visão de “verdade auditável” do Inspectah.
- Lista de anti-padrões que os agentes devem evitar e mecanismos para reforçar isso nas instruções.
- Checklists de revisão humana em pontos sensíveis (ex.: mudança de política global de modelos, alterações massivas em instruções de agentes críticos).

**Evidências esperadas**

- `docs/sprint_23_politica_segurança_agentes.md`.
- Exemplos de instruções de agentes com foco em safety (inputs/outputs exemplares).

---

## S23_G7 – Scorecard, cenários de simulação e ORR (pré-execução técnica)

**Objetivo**  
Fechar um **scorecard de qualidade** e um conjunto de cenários de simulação que permitam avaliar, de forma estruturada, se o desenho dos agentes e da tripla redundância atende ao nível de excelência exigido.

**O que este gate valida**

- Scorecard S23 com eixos mínimos, como:
  - Clareza e completude da ontologia de agentes.
  - Robustez da tripla redundância (cobertura de casos, ausência de gaps).
  - Transparência e auditabilidade (facilidade de explicar qualquer decisão).
  - Facilidade de manutenção/evolução (quão fácil é alterar/versão um agente crítico sem quebrar tudo).
  - Cobertura de safety e abuso.
- Conjunto de cenários de simulação que exercitam as camadas:
  - Caso de notícia simples (baixa controvérsia) passando pelo pipeline de interpretação → classificação → debunk.
  - Caso altamente controverso (política, desinformação em saúde, etc.).
  - Caso com fontes conflitantes (uma dizendo A, outra B).
  - Caso de “dados insuficientes”.
- Plano de como esses cenários serão automatizados em sprints futuras (mesmo que agora seja só documento/runbook).

**Critérios de aprovação**

- Scorecard documentado, com peso para cada eixo e critério claro de PASS/NO_GO.
- Pelo menos 5–10 cenários de simulação bem descritos, cobrindo diferentes tipos de risco.
- Amarração explícita entre cada cenário e quais agentes/camadas/comitês são exercitados.

**Evidências esperadas**

- `docs/sprint_23_scorecard_agentes.md`.
- `docs/sprint_23_cenarios_simulacao_agentes.md`.
- `docs/sprint_23_orr_plan.md` explicando como esses materiais serão usados no ORR técnico/futuras sprints.

---

## S23_orr – Wrap de encerramento conceitual da Sprint 23

**Objetivo**  
Consolidar, em um documento único, **o estado final da Sprint 23**, listando gates, decisões, riscos remanescentes e próximos passos para as sprints que vão implementar o código e os pipelines reais dos agentes.

**O que este wrap consolida**

- Tabela Gate × Status (S23_G0…S23_G7).
- Resumo das principais decisões de desenho (inclusive trade-offs conscientes).
- Riscos e dívidas assumidas para próximas sprints (ex.: ainda não há implementação de runtime real de comitês, só blueprint; UI do console ainda sem código, etc.).
- Como a Sprint 23 se conecta diretamente com:
  - S24 – Debunker v0 e humano-no-loop.
  - S25 – Governança, verdade/fato & política de promoção.

**Evidências esperadas**

- `docs/sprint_23_orr_summary.md` (vFinal), referenciado no roadmap e nos próximos capítulos.

---

Com todos esses gates **claramente definidos, com critérios de PASS objetivos e evidências nomeadas**, a Sprint 23 passa a ter um norte preciso: entregar um blueprint de Sistema de Agentes à prova de erros e falhas humanas, pronto para ser implementado em código nas próximas sprints sem espaço para ambiguidades ou “interpretações criativas” indesejadas.

