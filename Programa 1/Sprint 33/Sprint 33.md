# Inspectah — Sprint 33 — Doc Macro (E28 / OracleOps Wave 5)

## 0. TL;DR executivo da Sprint 33

A Sprint 33 é a quinta onda do Épico E28 (OracleOps / operação 24/7 do Inspectah) e tem um foco único:

Transformar o que hoje é um conjunto de gates, métricas soltas, dashboards parciais e logs em uma **experiência única de operação**: o **OracleOps Cockpit v1** e o **Fluxo de Incidentes v1**.

Ao final da S33, queremos que exista, para o operador e para o maintainer:

- Um **cockpit único de operação** (Web UI + APIs) que responda, em segundos, às perguntas:
  - "O Inspectah está saudável agora?"  
  - "O que quebrou, onde, desde quando e com qual impacto?"  
  - "O que eu faço exatamente para corrigir, e qual o próximo passo se isso falhar?"  
- Um **fluxo de incidentes padronizado**, com estados claros (detecção → triagem → mitigação → resolução → pós‑mortem) e trilha de auditoria.
- **SLOs operacionais praticáveis** (não só declarados em docs), com:
  - métricas ligadas a fontes reais (Prometheus/stack de observabilidade já definida no roadmap),
  - alertas mínimos configurados e versionados,
  - páginas de diagnóstico que levam diretamente aos logs, evidências e runbooks.

S33 não tenta redesenhar o produto nem o Truth‑DB; ela **amarra a operação 24/7** em cima do que S22–S32 já consolidaram: Data Hub, Console de Fontes, Ingestão 2.0 por fonte, fluxos de agentes, gates de sprint e estado atual pós‑S25 documentado.

Resultado esperado: o Inspectah passa de “um conjunto de sistemas que rodam” para “um produto que alguém consegue operar, sem ser o autor do código, às 3h da manhã sem pânico”.

---

## 1. Contexto, posicionamento e dependências

### 1.1. Onde a S33 se encaixa no mapa (Programas 1–4 + E28)

- **Programa 1 — Data Hub, Fontes, Ingestão & Operação 24/7**  
  S33 está diretamente ancorada em Programa 1: ela concretiza a camada de **Operação 24/7**, usando o Data Hub, o Console de Fontes, a Ingestão 2.0 e a arquitetura de fila/worker e observabilidade já definidas.

- **Programa 2 — Interpretação, Claims, Entidades & Sinais**  
  S33 **não** expande o ClaimGraph nem o runtime de agentes, mas passa a expor, no cockpit, sinais derivados (volume de claims, erros de agentes, quedas de throughput) como indicadores operacionais. Programa 2 é dependência conceitual e técnica, não o foco da implementação.

- **Programa 3 — Truth‑DB, Sistema de Blocos & Contestação**  
  S33 toca Programa 3 apenas no sentido de **observabilidade de verdade**: queremos conseguir enxergar quando pipelines que alimentam Truth‑DB e Sistema de Blocos estão atrasados, falhando ou gerando estados incoerentes. Não há mudança de modelo de dados de Truth‑DB nesta sprint.

- **Programa 4 — Exposição, Produtos, APIs & Uso Responsável**  
  O OracleOps Cockpit v1 é um **produto interno de Programa 4**: é um console interno, com autenticação via IdP, que expõe a saúde do sistema e os fluxos de incidentes. Ele também prepara o terreno para futuros consoles públicos/semipúblicos (Casos, Verdade, Painel de Narrativas), mas sem ainda expô‑los a usuários externos.

- **Épico E28 — OracleOps / 24/7**  
  S33 vem depois de ondas em que já consolidamos:
  - baseline de operação 24/7,
  - hardening de CI/CD e gates,
  - manutenção contínua do produto com monitores mínimos e runbooks iniciais.  
  A S33 é a sprint em que **ligamos tudo em um cockpit coerente** e definimos, de forma operável, o fluxo de incidentes.

### 1.2. Estado atual que a S33 assume como dado

A S33 assume como **pré‑condição**:

- S1–S25: todos os gates e bundles verdes no snapshot local descrito no "Estado do Produto pós‑S25".
- S22: Ingestão 2.0 por fonte com Console de Fontes já funcional, com IngestionConfig e fluxo de agentes por fonte.
- S23–S25: arquitetura de agentes, debunker v0 e camada de governança de verdade estabelecidas conceitualmente e parcialmente implementadas.
- S26–S32: ciclo de E28 já introduziu:
  - baseline de SLOs de ingestão e processamento,
  - scripts/gates para healthchecks e sanidade de pipelines,
  - primeiros dashboards em stack de observabilidade,
  - runbooks mínimos para incidentes recorrentes.

A S33 não corrige débito estrutural dessas sprints; ela **usa o que existe** como matéria‑prima e, quando necessário, cria **camadas finas de adaptação** (ex.: views agregadas, APIs internas, aproach de tagging de logs) para tornar tudo operável via cockpit.

---

## 2. Problemas a resolver (dor explícita)

A S33 parte de dores muito concretas da operação atual:

1) **Visão fragmentada da saúde do sistema**  
Metade das respostas sobre "o sistema está bem?" está em dashboards externos, outra metade em logs, e uma terceira metade (sim, matemática criativa) na cabeça de quem rodou a última sprint. Não existe uma visão unificada e opinativa de saúde.

2) **Incidentes tratados como eventos ad‑hoc**  
Quando algo quebra, a sequência típica é: abrir logs, tentar reproduzir, perguntar no chat, rodar scripts isolados. Não há um fluxo padrão de incidentes, nem estados claros, nem trilha única de decisão.

3) **SLOs declarados, mas pouco aplicados**  
O roadmap e o OracleOps Blueprint já falam de p95 de ingestão, p95 de consulta, bundle completo de evidência etc. Mas a aplicação prática ainda é parcial: há métricas, mas faltam SLOs de verdade com orçamentos de erro e alertas vinculados.

4) **Runbooks dispersos e de difícil descoberta**  
Existem decisões, notas de sanidade e scripts. Mas na hora H, o operador não tem um lugar único que diga: "Se o healthcheck X falhar, siga este passo a passo. Se não resolver, suba para este tipo de incidente".

5) **Pouca ligação entre incidentes e Truth‑DB / pipelines de verdade**  
Ainda é difícil responder, diante de uma pane, qual o impacto em pipelines críticos (ex.: ingestão de fontes oficiais, atualização de FactBlocks sensíveis, debunker de casos de alta visibilidade).

A S33 existe para **eliminar essas dores** em um recorte mínimo, mas real: poucas fontes, poucos pipelines críticos, mas fluxo completo do ponto de vista de operação.

---

## 3. Objetivos e estados‑alvo da Sprint 33

### 3.1. Objetivo macro

Colocar no ar o **OracleOps Cockpit v1** e o **Fluxo de Incidentes v1**, com SLOs operacionais praticáveis, para um subconjunto definido de fontes e pipelines críticos, de forma que:

- um operador sem contexto histórico consiga, em ≤ 5 minutos, entender o estado geral do sistema; e
- um incidente padrão consiga atravessar o fluxo completo (detecção → resolução → pós‑mortem registrado) sem depender de conhecimento tácito.

### 3.2. Estados‑alvo (SA)

SA‑33‑1 — **Cockpit de saúde unificado**  
Ao final da S33, existe uma página "OracleOps Cockpit" que mostra, em um único lugar:

- status de ingestão por fonte (OK, lento, falhando, desativado),
- backlog em fila/worker e tempos p95/p99 relevantes,
- status dos principais pipelines de agentes (parsing, classificação, debunking, Truth‑DB),
- indicadores de erro (taxa de falhas em jobs, erros 5xx em APIs internas),
- links diretos para dashboards de observabilidade e logs associados.

SA‑33‑2 — **Fluxo de incidentes operável**  
Incidentes passam a ser entidades de primeira classe com:

- estados explícitos (aberto, em triagem, mitigado, resolvido, pós‑mortem pendente, concluído),
- associação a fontes, pipelines e SLOs afetados,
- timeline de ações (quem fez o quê, quando, com qual comando ou mudança),
- checklist mínimo de pós‑mortem (causa raiz provável, ações definitivas, débitos criados).

SA‑33‑3 — **SLOs mapeados e conectados a métricas reais**  
Existem SLOs mínimos definidos e **instrumentados** para:

- ingestão de fontes críticas (tempo de detecção p95 e recência máxima dos dados),
- processamento de agentes (tempo máximo de fila para determinados pipelines),
- saúde do Truth‑DB (atraso máximo aceitável em jobs que promovem fatos),
- saúde de APIs internas essenciais ao cockpit.

Cada SLO tem:

- métricas de suporte mapeadas em stack de observabilidade,
- orçamentos de erro mínimos,
- alertas configurados para violação ou tendência de violação.

SA‑33‑4 — **Runbooks versionados e navegáveis no cockpit**  
Para os principais incidentes alvo da sprint, existem runbooks:

- escritos em linguagem clara, versionados no repositório,
- ligados a tipos de incidentes e healthchecks específicos,
- acessíveis diretamente a partir do cockpit (ex.: botão "Ver runbook" ao lado do alerta/indicador).

SA‑33‑5 — **Trilha de auditoria e evidência de operação**  
A operação passa a gerar evidência estruturada:

- logs de incidentes e ações operacionais ligados a IDs internos,
- registros de quando SLOs foram violados e qual foi a resposta,
- artefatos exportáveis (ex.: JSON/zip) que documentam um incidente crítico e seu tratamento.

---

## 4. Escopo, anti‑escopo e fronteiras

### 4.1. Escopo da S33

A S33 **inclui**:

- Implementar o **OracleOps Cockpit v1** como página(s) interna(s) no Inspectah UI, integrada(s) ao backend existente.
- Expor APIs internas para:
  - listar o estado de saúde de fontes, pipelines e SLOs,
  - criar, atualizar e consultar incidentes e seus eventos,
  - buscar links de dashboards e logs associados a cada componente monitorado.
- Modelar a entidade **Incident** (domínio de ops) e integrá‑la ao restante do sistema apenas naquilo que for necessário para a operação (sem misturar com Truth‑DB ou casos de usuário final).
- Selecionar um **subconjunto explícito de fontes e pipelines críticos** (por ex.: 3–5 fontes oficiais, 1–2 pipelines de claims de alta relevância, 1 pipeline de Truth‑DB) e garantir que o cockpit funcione end‑to‑end para essas rotas.
- Definir e instrumentar **SLOs mínimos** para esse subconjunto e ligar alertas básicos.
- Criar e versionar **runbooks** para os 5–10 tipos de incidentes mais prováveis nesse recorte.
- Construir o mínimo de **componentes de UI de suporte** (badges de estado, timelines, links para dashboards, etc.) em linha com o design system já definido em sprints anteriores.

### 4.2. Anti‑escopo (o que fica explicitamente fora)

A S33 **não inclui**:

- Construção de um sistema genérico de incidentes multi‑produto; o foco é o Inspectah em si.
- Redesenho da arquitetura de observabilidade; trabalhamos em cima da stack já definida (apenas ajustes pontuais, se necessários).
- Mudanças profundas no modelo de Truth‑DB ou do Sistema de Blocos; apenas observabilidade e mapeamento de impacto.
- Exposição de painéis de saúde para usuários externos; o cockpit é interno.
- Implementação completa de todas as ideias de produto avançadas ("mentiras em circulação agora", "radar de manipulação", "linha de crédito de confiança", etc.). S33 apenas prepara o terreno do ponto de vista operacional.

### 4.3. Fronteiras e integrações

- **Com o Data Hub e Console de Fontes:** o cockpit consome o estado de fontes e jobs de ingestão, sem alterar a lógica de ingestão.
- **Com o runtime de agentes (Programa 2):** o cockpit expõe status e erros de agentes, mas não reconfigura fluxos de agentes.
- **Com o Truth‑DB (Programa 3):** o cockpit enxerga o estado de jobs que alimentam o Truth‑DB, sem alterar regras de promoção ou contestação de fatos.
- **Com o IdP e Programa 4:** o cockpit respeita o modelo de autenticação/autorização definido em Programa 4; acesso é restrito a operadores, maintainers e perfis internos autorizados.

---

## 5. Desenho macro de solução (visão de arquitetura)

Esta seção não substitui o Capítulo 3 (Arquitetura & Filemap) detalhado da sprint, mas estabelece o desenho macro que ele deve obedecer.

### 5.1. Componentes principais

- **OracleOps Cockpit UI**  
  Conjunto de páginas internas no frontend do Inspectah, provavelmente sob rota `/ops` ou equivalente, com:
  - visão geral (overview) de saúde,
  - detalhe por fonte/pipeline,
  - visão de incidentes e sua timeline.

- **Ops API / Incident Service**  
  Camada de backend (serviço ou módulo) responsável por:
  - expor o estado de saúde consolidado (via queries e/ou caches),
  - orquestrar a criação e atualização de incidentes,
  - integrar com observabilidade (links, IDs de métricas, etc.).

- **Integradores de Observabilidade**  
  Adaptadores leves que ligam o mundo do Inspectah (fontes, pipelines, jobs) aos nomes/labels usados em dashboards e métricas na stack de observabilidade.

- **Modelo de Incident e Audit Trail**  
  Entidade persistida com campos mínimos (id, state, severity, source(s) afetadas, pipelines afetados, timestamps, ações, links externos).

### 5.2. Princípios de arquitetura

- **Não duplicar fontes de verdade:** o cockpit lê de modelos e métricas existentes; não reimplementa lógica de ingestão ou de agentes.
- **De fora para dentro:** começamos pela experiência do operador (quais perguntas precisa responder) e, a partir daí, definimos as queries e integrações.
- **Extensibilidade controlada:** tudo que for criado (API de incidentes, componentes de UI, mapeamentos de métricas) deve ser fácil de estender na S34–S35 sem refatorações traumáticas.
- **Operação como primeiro cidadão:** incidentes, SLOs e runbooks passam a ter modelos e pastas claras no repositório, não apenas docs soltos.

---

## 6. Gates, evidências e critérios de aceite (visão macro)

Os detalhes finos de cada gate e de suas evidências ficarão no Capítulo 2, mas a S33 já define aqui a visão macro:

- **G0 — Escopo & baseline ops**  
  Critério: doc de escopo da S33 aprovado pelo Conselho (Spec Office + representantes de Ops) com recorte claro de fontes e pipelines críticos.

- **G1 — Modelo de Incident & API mínima**  
  Critério: migrations aplicadas, testes unitários cobrindo criação/atualização/leitura de incidentes, API interna estável.

- **G2 — Cockpit UI v1 navegável**  
  Critério: páginas acessíveis via login interno, mostrando pelo menos 1 visão geral, 1 visão por fonte/pipeline e 1 visão de incidentes.

- **G3 — SLOs operacionais instrumentados**  
  Critério: para o recorte da sprint, SLOs definidos e métricas comprovadamente ligadas (teste por simulação/forçagem de carga ou falha controlada).

- **G4 — Runbooks & fluxo de incidentes validado**  
  Critério: para cenários de teste definidos (por ex., falha em fonte oficial X, fila de jobs acima do limiar Y, erro em pipeline de Truth‑DB Z), o time consegue seguir o fluxo de incidentes com runbooks correspondentes.

- **G5 — Evidência de operação real**  
  Critério: pelo menos 1 incidente real (ou simulado de forma realista) documentado de ponta a ponta, com bundle de evidência exportável (logs, dashboards, ações, pós‑mortem).

---

## 7. Riscos, anti‑gaps e decisões não‑negociáveis

### 7.1. Riscos principais

- **Escopo inflado de SLOs:** tentar cobrir tudo de uma vez (todas as fontes, todos os pipelines) e não entregar um cockpit útil para ninguém.
- **Dependência excessiva da stack de observabilidade:** gastar metade da sprint ajustando stack externa, em vez de construir o cockpit.
- **Cockpit "bonito mas mudo":** UI polida com dados fracos ou não confiáveis, gerando falsa sensação de segurança.

### 7.2. Anti‑gaps explícitos

- Nenhum indicador no cockpit pode ser "fake" ou puramente decorativo; tudo precisa estar ligado a dados reais.
- Todo SLO declarado na sprint precisa ter **evidência de medição** (print de dashboard não basta; queremos queries/logs parametrizados, scripts de sanity, etc.).
- Todo runbook precisa ser testado pelo menos uma vez em cenário real ou simulado.

### 7.3. Decisões não‑negociáveis

- A S33 não abre mão do foco: **ops first**. Qualquer feature "legal" que não ajude diretamente a operar o sistema 24/7 vai para backlog de futuros épicos.
- A ergonomia do operador em situações de stress é prioridade: menos cliques, menos janelas, mais links diretos para ação.
- A evidência de operação (incident bundles, logs, timelines) deve ser armazenada de forma que possa ser reusada em ORR futuros e em auditorias internas.

---

Este doc macro da Sprint 33 serve como contrato de alto nível entre squads, Ops e Conselho. Os próximos capítulos (2 a 6) vão detalhar:

- estados‑alvo, gates e métricas (Capítulo 2),
- arquitetura concreta e filemap (Capítulo 3),
- plano de execução, waves e tasks (Capítulo 4),
- estado da arte / referências (Capítulo 5),
- lessons learned e anti‑gaps específicos da sprint (Capítulo 6).

