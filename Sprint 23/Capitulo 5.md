# Inspectah — Sprint 23
## Capítulo 5 — Front end (Console de Agentes e Painéis de Comitês)

### 5.1 Objetivo do capítulo

Este capítulo define, em nível de produto + UX + integração, tudo o que o front end precisa entregar na Sprint 23 para viabilizar:

1. Um **Console de Agentes** (admin) para criar, versionar, configurar e auditar todos os agentes que compõem as camadas de interpretação, classificação/organização e debunk/curadoria do Inspectah.
2. Um conjunto de **painéis de comitês** que tornem visível como as decisões são tomadas (tripla redundância), quais agentes participaram, quais evidências foram usadas e quais diretrizes estavam ativas em cada decisão.
3. Uma experiência de uso alinhada ao paradigma de “criar um GPT customizado”, com campos claros de Nome, Descrição, Instruções, Conhecimento (KB) e Modelo, incluindo o mecanismo de rollout/buffer de modelos mais novos.
4. Uma experiência que seja **auditável por humanos** (admins e usuários avançados): qualquer decisão relevante deve permitir “abrir a caixa preta” de forma simples.

A visão aqui é: depois da Sprint 23, o front end deve ser capaz de tratar agentes e comitês como **cidadãos de primeira classe** do produto, com o mesmo nível de cuidado que demos às fontes, ingestão e timelines.

---

### 5.2 Princípios de UX e produto específicos para agentes

O front end de agentes e comitês deve seguir alguns princípios rígidos:

1. **Transparência radical**
   - Todo bloco de decisão relevante (ex.: classificação de um item, julgamento de veracidade, promoção de um bloco) precisa ter um caminho visual claro até:
     - Quais agentes participaram (nomes, papéis, versões de diretriz/modelo);
     - Quais evidências/inputs foram considerados (fontes, datas, trechos relevantes);
     - Qual foi o raciocínio de cada agente (quando disponível em forma de relatório); 
     - Como o mediador chegou ao GO/NO-GO ou à classificação final.

2. **Redundância tripla visível**
   - A tripla redundância não pode ser apenas um detalhe de backend. O UI deve explicitar a estrutura: Debunker A, Debunker B, Mediador, com estados e outputs separados.
   - Sempre que uma conclusão vier de um comitê triplo, o usuário deve conseguir ver o **painel do comitê** (pelo menos para admins; parte filtrada/simplificada para usuários finais).

3. **Configuração tão simples quanto criar um GPT**
   - O fluxo de criação/edição de um agente deve seguir o layout mental:
     - Nome
     - Descrição
     - Instruções (diretrizes detalhadas)
     - Conhecimento (arquivos, coleções de KB)
     - Modelo recomendado (com override possível)
   - O usuário não deve precisar entender os detalhes internos do backend para configurar as diretrizes de um agente.

4. **Separação clara por camadas e papéis**
   - A UI deve separar explicitamente:
     - Camada de interpretação e leitura de texto;
     - Camada de classificação/organização (taxonomias, tags, blocos, casos);
     - Camada de debunk/curadoria (ceticismo, validação de evidências, caça a inconsistências);
     - Camadas de mediação/consenso (agentes mediadores).
   - Cada agente deve estar explicitamente associado a uma camada e a um papel dentro de comitês (debunker 1, debunker 2, mediador, classificador principal, classificador revisor, etc.).

5. **Auditabilidade e versionamento de diretrizes**
   - Toda alteração de instruções, modelo, KB ou papel de um agente precisa gerar uma versão, com:
     - Quem alterou;
     - Quando;
     - O que mudou (diff humanamente legível de instruções principais e configurações-chave).
   - Front end precisa oferecer telas para listar versões, comparar versões e, quando aplicável, fazer rollback.

6. **Rollout de modelos com buffer global configurável**
   - Do ponto de vista de UX, deve existir:
     - Um painel global de “Modelos & Rollout”, onde o admin ajusta a política: 
       - usar sempre o modelo mais novo disponível;
       - aplicar um buffer de X dias para updates automáticos;
       - ou manter modelos fixos por agente.
     - No nível do agente, o admin deve enxergar claramente qual modelo está em uso, qual é o modelo “recomendado” mais novo e qual será o comportamento quando o buffer expirar.

---

### 5.3 Mapa de telas principais

Nesta sprint, o front end deve entregar pelo menos as seguintes telas e seções (não necessariamente como páginas isoladas; podem ser tabs ou sub-views dentro de Admin):

1. **Admin → Agentes**
   - Lista de agentes com filtros por:
     - Nome;
     - Camada (interpretação, classificação, debunk, mediação);
     - Papel (debunker A/B, mediador, classificador principal, etc.);
     - Status (ativo, em teste, desativado);
     - Modelo em uso (para identificar rapidamente agentes em modelos antigos).
   - Ações rápidas:
     - Criar novo agente;
     - Duplicar agente (para experimentar novas diretrizes);
     - Ver detalhes / editar;
     - Ver histórico de versões;
     - Ver últimos usos (logs agregados por agente).

2. **Admin → Agente (Detalhe)**
   - Seções principais:
     - Cabeçalho com nome, descrição, camada, papel e status.
     - Aba “Instruções & Comportamento”:
       - Campo grande de instruções (com markdown simples ou texto rico);
       - Campo de “Guidelines de segurança / limites” (ex.: o que evitar, regras de neutralidade, regras anti-delírio);
       - Campo de “Estilo de resposta” quando aplicável (mais técnico, mais sucinto, etc.).
     - Aba “Conhecimento (KB)”:
       - Lista de coleções/arquivos associados ao agente;
       - Botão de adicionar/remover arquivos ou coleções (respeitando regras globais de segurança);
       - Indicação de tamanho aproximado da KB e últimos updates.
     - Aba “Modelo & Execução”:
       - Modelo atual em uso (ex.: `gpt-5.1-mini` ou similar, conforme naming interno);
       - Modelo recomendado (mais novo disponível);
       - Comportamento de rollout herdado da configuração global (com explicação) e opção de override por agente;
       - Limites básicos de custo/performance (ex.: tamanho máximo de contexto, preferências de streaming ou não, etc.).
     - Aba “Histórico & Versões”:
       - Timeline de alterações (quem, quando, o que);
       - Lista de versões com metadados (hash, data, autor, resumo da mudança);
       - Botão para comparar versão atual vs uma anterior (diff em instruções, modelo, KB);
       - Botão para rollback, com confirmação.

3. **Admin → Comitês & Pipelines de Agentes**
   - Lista de comitês definidos (por camada):
     - Comitês de interpretação;
     - Comitês de classificação/organização;
     - Comitês de debunk/curadoria;
     - Comitês de mediação/consenso.
   - Para cada comitê:
     - Nome claro (ex.: “Classificador de Notícias Políticas — Comitê triplo v1”);
     - Descrição;
     - Camada (interpretação, classificação, debunk);
     - Estrutura (2 debunkers + mediador, 2 classificadores + revisor, etc.);
     - Agentes participantes (links para o detalhe de cada agente).
   - Ações:
     - Criar comitê novo;
     - Editar estrutura e papéis (respeitando constraints de backend);
     - Desativar/ativar comitê.

4. **Admin → Painel de um Comitê (Detalhe de decisões)**
   - Visão em “cartas” para últimas decisões tomadas por este comitê:
     - Caso / bloco / item analisado;
     - Resumo da decisão final;
     - Debunker A: resumo do relatório + status (concorda, discorda, incerto);
     - Debunker B: idem;
     - Mediador: rationale final e decisão (GO/NO-GO, classificação escolhida, etc.);
     - Links para evidências (fontes, blocos, timeline).
   - Filtros por:
     - Data;
     - Tipo de decisão (classificação, fact-check, promoção de bloco, etc.);
     - Divergência (ex.: casos onde debunker A e B discordaram);
     - Risco (alto, médio, baixo, desconhecido).
   - Possibilidade de clicar em uma decisão e abrir um **painel detalhado**, com:
     - Input de texto original (pergunta do usuário ou conteúdo analisado);
     - Lista de evidências consultadas (resumo + links);
     - Relatório completo/explicação de cada agente (quando o backend armazenar);
     - Versão de diretrizes e modelo que estavam ativas em cada agente na época da decisão.

5. **Admin → Modelos & Rollout Global**
   - Tela de configuração global da política de modelos:
     - Opções de política:
       - Sempre usar o modelo mais novo disponível em todos os agentes;
       - Usar modelo mais novo com buffer global de N dias (configurável);
       - Manter modelos fixos por agente (sem updates automáticos).
     - Quando buffer estiver ativo:
       - Mostrar uma linha do tempo indicando quando cada agente/linha vai migrar de modelo;
       - Permitir “forçar rollout agora” (zerar buffer) para todos ou para um subconjunto de agentes.
     - Lista de modelos disponíveis, com notas (ex.: estável, beta, deprecado) e recomendações.

6. **User-facing (Consulta/Timeline) — Hooks visuais para transparência**
   - Na página de consulta/resultado e nas timelines, o front end deve expor **ganchos visuais simplificados**:
     - “Esta conclusão foi validada por um comitê de agentes” → link para visão resumida do comitê (não necessariamente todos os detalhes internos, mas o suficiente para mostrar que houve tripla redundância e ver alguns metadados).
   - Esta parte pode ser entregue de forma incremental, mas o capítulo 5 já precisa prever:
     - Onde esses links aparecem (cards de resultado, eventos de timeline, telas de raio-X);
     - Qual é o nível de detalhe permitido para usuários não-admins (resumo, sem expor prompts completos, etc.).

---

### 5.4 Navegação, IA de UX e padrões visuais

1. **Integração com a navegação atual**
   - O Console de Agentes e Comitês deve ser acessível a partir do menu Admin, com itens claros:
     - “Agentes & Comitês” → submenu “Agentes”, “Comitês”, “Modelos & Rollout”.
   - URLs devem seguir o padrão atual (`/admin/...`) e serem previsíveis para facilitar testes automatizados e links de documentação.

2. **Consistência visual**
   - Reuso dos componentes atuais (cards, tables, badges de status, modais de confirmação, etc.).
   - Estados de loading, erro e vazio para todas as listas (agentes, comitês, decisões).
   - Badges de status para agentes e comitês (ativo, em teste, desativado, legado) com legenda clara.

3. **Mensagens e textos**
   - Linguagem consistente com o resto do Inspectah: técnica, mas acessível.
   - Explicações curtas em tooltips/abas “Ajuda” para conceitos mais avançados (tripla redundância, buffer de modelos, etc.).

---

### 5.5 Requisitos de integração com backend (alto nível)

O capítulo 3 detalha contratos e filemap; aqui, focamos em como o front end deve conversar com esses contratos.

1. **Agentes**
   - Endpoints esperados (nomes ilustrativos, não definitivos):
     - `GET /admin/agents` — listar agentes com filtros/paginação.
     - `POST /admin/agents` — criar agente.
     - `GET /admin/agents/{agent_id}` — detalhe.
     - `PUT /admin/agents/{agent_id}` — atualizar agente.
     - `GET /admin/agents/{agent_id}/versions` — listar versões.
     - `GET /admin/agents/{agent_id}/versions/{version_id}` — detalhe de versão.
     - `POST /admin/agents/{agent_id}/rollback` — rollback para versão anterior.
   - O front end deve tratar erros de validação de forma amigável (ex.: instruções muito curtas, modelo indisponível, etc.).

2. **KB / Conhecimento**
   - Endpoints para associar coleções/arquivos a agentes, ou seleção de coleções pré-existentes.
   - O front end precisa lidar com uploads assíncronos (barra de progresso e estados de sucesso/falha), mas o desenho exato dos fluxos de upload pode ser refinado em sprints futuras; nesta sprint, o essencial é mapear UI e contratos esperados.

3. **Comitês e decisões**
   - Endpoints para listar comitês, definir sua estrutura, e recuperar decisões recentes.
   - O front end deve consumir endpoints de “audit log” de decisões quando disponíveis, mapeando para os painéis descritos em 5.3.4.

4. **Modelos & Rollout**
   - Endpoints para ler e configurar a política global de modelos, bem como para ler modelos disponíveis e suas flags (estável/beta/deprecado).
   - Endpoints para override por agente, quando permitido pelas regras do backend.

---

### 5.6 Estados de erro, segurança e observabilidade no front

1. **Erros previsíveis**
   - Agente inválido (configuração inconsistente, ex.: falta de modelo) → UI deve indicar claramente que há um problema de configuração e oferecer caminho para o detalhe/edição do agente.
   - Comitê incompleto (faltando um dos papéis) → UI deve sinalizar como “Incompleto” e impedir sua seleção em pipelines novos.
   - Falhas de backend (HTTP 5xx ou timeouts) → mensagens amigáveis, com botão para tentar novamente e, para admins, link para ver logs no painel de observabilidade.

2. **Segurança e permissões**
   - Seções de criação/edição de agentes, comitês e política de modelos devem ser restritas a perfis admin (ou equivalente).
   - Usuários não-admins nunca devem ver prompts completos, instruções internas sensíveis ou KB bruta; apenas resumos/painéis simplificados.

3. **Observabilidade de UX**
   - Eventos de analytics internos (no estilo já usado no frontend) para:
     - criação/edição de agentes;
     - alterações de modelo;
     - criação/edição de comitês;
     - abertura de painéis de decisão.
   - Esses eventos alimentam os watchers/metrics descritos em capítulos anteriores, permitindo medir o uso real do Console de Agentes.

---

### 5.7 Critério de pronto (DoD) para o front end da Sprint 23

O front end da Sprint 23 será considerado “DONE” quando:

1. Console de Agentes implementado com:
   - Lista de agentes (filtros básicos funcionando);
   - Tela de detalhe com abas de Instruções, Conhecimento, Modelo & Execução, Histórico & Versões;
   - Fluxo de criação/edição funcional, integrado ao backend;
   - Exibição clara de camada, papel e status do agente.

2. Console de Comitês implementado com:
   - Lista de comitês (por camada);
   - Tela de detalhe de comitê com estrutura tripla (ou equivalente) e ligação com agentes;
   - Painel de decisões recentes com pelo menos uma visão detalhada de cada decisão.

3. Tela de Modelos & Rollout implementada com:
   - Visualização da política global;
   - Possibilidade de alterar política (conforme contratos de backend);
   - Exibição do impacto esperado por agente (ao menos em forma simplificada).

4. Hooks de transparência nas telas de consulta/timeline:
   - Pelo menos um caminho visível para admins abrirem o painel de decisão de um comitê a partir de um resultado.

5. Testes de front end:
   - Cobertura de testes para componentes críticos do Console de Agentes e Comitês (listas, detalhes, formulários, painéis de decisão);
   - Scripts de qualidade de front (lint/test/build) passando, integrados aos gates da sprint.

6. Documentação mínima incorporada:
   - Capturas de tela ou descrições atualizadas em `docs/sprint_23_*` descrevendo os fluxos principais de front;
   - Referências claras para desenvolvedores sobre os endpoints que o front consome.

Este capítulo 5 passa a ser a referência oficial de front end para a Sprint 23: qualquer ajuste no escopo visual ou de UX deve ser refletido aqui antes de entrar em execução.