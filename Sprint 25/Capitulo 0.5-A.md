# Sprint 25 — Capítulo 0.5 — Adendo v2
## Console & Agent Studio — Deep Dive Operacional, UX, Segurança e Código Humano

> Versão v2 — Revisado e endurecido pelo Squad Verdade & Interpretação, Stonebraker, Norvig, Pearl, Percy, Jobs & cia. Este adendo complementa o Capítulo 0.5 e o Adendo 0.A. O que está aqui é contrato de UX, operação e implementação para o Console Operacional e o Agent Studio.

---

### 0.5.A.1. Missão do adendo v2

Capítulo 0.5 responde: “quais módulos o Console precisa ter para operar o Sistema de Camadas e o cérebro dos agentes?”.

O Adendo 0.5.A v2 responde:

1. Como o Console e o Agent Studio devem se comportar em **uso real**, com humanos cansados, incidentes, tuning fino e pressão de tempo.
2. Como **pensamento das camadas**, **contexto de entidade/caso** e **decisões** aparecem na tela de forma clara, auditável e navegável.
3. Quais padrões de **implementação (frontend/backend)** o Codex deve seguir para produzir um console legível, seguro e sustentável por humanos.

Nada aqui muda o Capítulo 0.5; tudo aqui torna o 0.5 mais específico, mais operável e menos sujeito a “interpretação criativa” do Codex.

---

### 0.5.A.2. Exibição de pensamento, contexto e decisão

Objetivo: qualquer pessoa diante de uma Claim deve conseguir responder:

- o que foi alegado;
- o que o sistema já sabia sobre esse ator/caso antes;
- o que cada camada fez e pensou;
- por que a decisão final foi aquela (PROMOTED/CONTESTABLE/REJECTED/DEFERRED).

Componentes de UI obrigatórios na tela de Claim (drill‑down):

1. Painel “Resumo da Claim”
   - texto humano curto (“O sistema entende que esta claim diz que…”), com sujeito, predicado, objeto, tempo, local;
   - status atual (estado da claim + decisão final, se existir);
   - links rápidos: Dossiê de Entidade, Dossiê de Caso, bloco correspondente na Truth‑DB.

2. Painel “Contexto Consultado”
   - indicação explícita de que o Context Service foi chamado (ex.: badge “Contexto vN carregado”);
   - resumo do Dossiê de Entidade (cartão com contagens, eventos-chave, padrões relevantes);
   - resumo do Dossiê de Caso, quando aplicável (linha do tempo compacta + status do caso);
   - aviso claro se, por algum motivo, contexto não foi carregado embora devesse (isso vira alerta técnico).

3. Timeline de Camadas (ThoughtTrace)
   - uma linha vertical ou horizontal onde cada camada (2…10) é um nó;
   - cada nó mostra, em estado colapsado:
     - ícone da camada;
     - resultado principal (ex.: “Interpretado como DECLARAÇÃO DE FATO sobre entidade X”);
     - sinaladores de alerta (conflito, falta de evidência, divergência de agentes);
   - ao expandir a camada, o painel mostra:
     - inputs relevantes (texto resumido, contexto de entidade/caso que entrou, parâmetros);
     - outputs principais (claims geradas, scores, flags);
     - “Resumo do raciocínio” em linguagem humana: 3–10 linhas curtas descrevendo o que o comitê/agente fez.

   Quando permitido pelo RBAC, o usuário pode ainda abrir um painel de “Detalhe Técnico” com:
   - recortes de prompts/respostas (sanitizados, sem dados sensíveis);
   - IDs de logs e evidências brutas.

4. Painel “Decisão Final” (DecisionTrace)
   - explica, em ordem, quais peças pesaram na decisão:
     - quais comitês;  
     - quais pesos de política (TruthScore);  
     - se o Debunker ou humano alteraram o fluxo;
   - indica se o histórico da entidade/caso foi decisivo (“Esta claim entra em conflito com 3 fatos anteriores já promovidos sobre o mesmo caso”).

Regras de UX fortes:

- Nunca apresentar a decisão como “o sistema achou” sem referência concreta. Sempre ancorar em: evidências, conflitos, políticas, scores.
- Nunca esconder que houve incerteza: se a decisão foi difícil ou marginal, isso precisa aparecer.

---

### 0.5.A.3. Agent Studio + Context Service + KB — visão unificada

A partir da perspectiva de quem edita um agente, o Agent Studio precisa mostrar claramente:

- qual é o papel do agente no Sistema de Camadas (camada principal, pipelines onde atua);
- que contexto ele recebe automaticamente (entidade, caso, dossiê de ingestão);
- que KB ele tem acoplada (coleções globais, arquivos específicos);
- que ferramentas ele pode invocar (Context Service, Truth‑DB, adaptadores, utilitários);
- como ele se comporta em cenários de teste reais.

Aba “Contexto & Ferramentas” — requisitos mínimos:

- Bloco “Contexto automático”:
  - checkboxes fixos com explicação: “Recebe Dossiê de Entidade”, “Recebe Dossiê de Caso”, “Recebe apenas contexto bruto de Dossiê de Ingestão”;  
  - isso não é decorativo: define o contrato de entrada que o backend deve respeitar.

- Bloco “KB associada”:
  - lista de coleções globais e específicas (com tags e versões);
  - status: ATUAL, DEPRECADA, EM MIGRAÇÃO;
  - link para tela de KB global.

- Bloco “Ferramentas habilitadas”:
  - toggles para cada ferramenta (Truth‑DB read, adaptador IBGE, adaptador TSE, normalizador de datas, etc.);
  - limites exibidos (“até N chamadas por job”, “timeout Xs”, “quota diária Y”).

Isso cria uma visão única: “o que esse agente sabe, de onde ele tira isso, e o que ele consegue chamar?”.

---

### 0.5.A.4. Fluxos operacionais típicos (end‑to‑end)

O Console precisa ser desenhado pensando em fluxos reais, não só em telas isoladas. Três fluxos são mandatórios como referência de design.

1) Ajustar um agente que está performando mal

Passos desejados:

- Observabilidade mostra aumento de contestáveis, divergência entre comitês ou queda na qualidade em domínio X.
- Operador clica no alerta e chega à lista de claims afetadas.
- Seleciona 2–3 claims representativas e abre o drill‑down.
- Na tela da Claim, vê ThoughtTrace + DecisionTrace + Dossiê de Entidade/Caso.
- Identifica camada/agente suspeito (ex.: Comitê Epistemológico de Política).
- Clica em “Abrir agente no Agent Studio”.
- No Agent Studio:
  - verifica instruções e guardrails;  
  - verifica contexto recebido (o Context Service está dando informação suficiente? está exagerado?);  
  - revisa KB associada (coleções antigas, KB irrelevante?);
  - roda os mesmos casos de teste (com os textos e contextos das claims problemáticas);  
  - ajusta instruções/KB/ferramentas;
  - roda suite de testes completa;
  - submete a nova versão para aprovação;
  - após aprovação, promove versão e registra no incidente.

2) Introduzir nova KB global sensível

Exemplo: uma nova ontologia de cargos públicos, ou uma base oficial de indicadores macroeconômicos.

Fluxo:

- Curador de KB sobe a nova coleção (v1) na tela de KB global.
- Marca como “sensível” e define quem pode usá‑la.
- O sistema mostra quais agentes seriam bons candidatos a usar essa coleção (por papel/domínio).
- Em modo “ensaios”, o curador associa a coleção apenas a agentes em pipelines não críticos, e roda testes e simulações.
- Resultados são analisados; se aprovados, a coleção passa a ser usada por agentes em pipelines críticos.
- Todo rollout gera evento de auditoria, com datas e escopo.

3) Conectar um novo Context Slice ao pipeline

Exemplo: criar uma visão extra de contexto para casos de corrupção (priorizando histórico de denúncias infundadas da mesma fonte).

Fluxo:

- Engenheiro de pipeline cria uma nova “estratégia de contexto” no Context Service (ex.: `build_corruption_risk_slice`).
- Especifica quais sinais entram (claims anteriores, fontes envolvidas, decisões passadas).
- Adiciona esse slice como insumo apenas para o Debunker de domínios relacionados.
- No Flow Designer, ajusta o pipeline de política para chamar esse slice extra em alguns cenários.
- Roda simulações em claims históricas e compara decisões antigas vs novas.
- Se o resultado for melhor, registra em scorecards e promove a mudança.

Esses fluxos são exemplos, mas definem a qualidade mínima esperada de navegação: sempre possível sair de um “sintoma” (alerta, métrica) e chegar até código/dados que podem ser ajustados.

---

### 0.5.A.5. Comportamento em incidentes — modo investigação ligada

Requisitos mínimos da tela de incidente:

- Painel de resumo:
  - descrição humana do incidente;
  - severidade (S1…S4);
  - período afetado;
  - domínios/pipelines/camadas envolvidos.

- Painel de impacto:
  - número de claims afetadas (estimado e confirmado);
  - lista de exemplos representativos;
  - se houve promoção de Fatos/Verdades potencialmente incorretos.

- Painel de “Mutações recentes”:
  - versão de agentes alterados recentemente (com links para Agent Studio);
  - mudanças em políticas de TruthScore;
  - alterações em pipelines (Flow Designer);
  - rollout de KB (coleções globais).

- Painel de ações:
  - “Segurar promoções neste domínio” (flag global de segurança);
  - “Desviar para pipeline de contingência” (se existir);
  - “Marcar claims recém-decorridas para revalidação”.

Quando um incidente é encerrado, o console obriga o preenchimento de:

- causa raiz;
- mudanças de agentes/políticas/KBS/pipelines feitas;
- recomendação para futuras sprints (ex.: novo gate, nova métrica, nova política de rollout).

Essas informações alimentam diretamente os Capítulos 1–4 de sprints futuras.

---

### 0.5.A.6. UX de segurança — limitar o estrago antes que ele aconteça

Como o Console é um “painel de usina nuclear”, algumas regras de UX de segurança são obrigatórias:

- Ações perigosas sempre em “modo duas chaves”:
  - alteração de política global de TruthScore em domínios sensíveis;
  - ativação de novo pipeline como principal;
  - desativação de Debunker ou humano‑no‑loop em domínios críticos;
  - reprocessamento em lote de claims já promovidas.

- Confirmar intenção de forma friccional, mas não sádica:
  - exigir digitação de uma frase/chave (ex.: nome do pipeline, “CONFIRMAR‑PROMOCAO”, etc.);
  - mostrar resumo do impacto (“Você está prestes a alterar a política de promoção para claims de tipo X. Nos últimos 30 dias, isso afetaria N claims.”).

- Sempre oferecer rollback e mostrar o caminho de volta:
  - qualquer alteração em pipeline/política/agente precisa ter versão anterior disponível;
  - botões de rollback devem ser visíveis, porém protegidos por confirmação;
  - ao reverter, o console deve sugerir marcar claims recentes para revisão.

- Evitar “acidentes de contexto”:
  - o console deve exibir, em destaque, filtros ativos para qualquer operação (datas, domínios, estados);
  - nenhuma operação em lote sem filtros explícitos (domínio ou período mínimo).

---

### 0.5.A.7. Padrões de implementação para o Codex (frontend/backend)

Este trecho é recado direto para quem vai escrever código do console (Codex incluído).

Frontend (ex.: React + TypeScript):

- Componentes pequenos e reutilizáveis para padrões recorrentes: tabelas, timelines, painéis de resumo, modais de confirmação.
- Tipagem forte: todos os dados que vêm da API devem ter tipos/interfaces bem definidas; nada de `any` generalizado.
- Estados consistentes:
  - loading, erro, vazio, sucesso;
  - feedback ao usuário (toasts, banners, indicadores) centralizado em um sistema de notificação.
- Navegação clara:
  - rotas estáveis (`/admin/claims/{id}`, `/admin/agents/{id}`, `/admin/incidents/{id}`);
  - possibilidade de salvar URLs para revisitar estados específicos.

Backend (ex.: FastAPI / Django / outro):

- APIs versionadas (`/api/admin/v1/...`) com contratos estáveis.
- Separação de camadas:
  - modelos de dados;
  - serviços de domínio (ex.: `IncidentService`, `AgentService`, `ContextServiceAdapter`);
  - camada de API leve que orquestra chamadas.
- Logging estruturado:
  - logs de ações do console (quem fez o quê, em qual recurso, com qual payload);
  - correlação com IDs de incidentes e claims.

- Testes automatizados:
  - testes de API para endpoints críticos (incidentes, rollout de política, promoção de agente);
  - testes de serviços de domínio (especialmente para seleção de contexto, impacto de políticas, etc.).

Ponto central: código deve parecer escrita de um time sênior organizado, não de um script gigantesco de IA. Pequenos módulos, nomes decentes, testes.

---

### 0.5.A.8. Integração explícita com o Adendo 0.A (Entidades, Casos, Context Service)

O Adendo 0.A define:

- estruturas de Entidade e Caso;
- dossiês de Entidade/Caso;
- Context Service e seus contratos.

Este Adendo 0.5.A v2 define:

- como o Console e o Agent Studio exibem Entidades, Casos, Dossiês e Contexto;
- como operadores e curadores acionam e ajustam essas estruturas;
- como incidentes e fluxos de trabalho reais se aproveitam desse modelo.

Isso significa que:

- nenhuma tela de Claim pode existir sem mostrar, quando houver, Entidade/Caso associados;
- o Agent Studio deve sempre deixar claro qual contexto é fornecido ao agente;
- telas de incidente precisam puxar tanto estrutura (modelo de dados) quanto comportamento (pipelines, políticas, agentes) e cruzar tudo.

---

### 0.5.A.9. Critério de excelência do Adendo 0.5.A v2

Este adendo atinge o nível de excelência esperado da Sprint 25 quando:

- qualquer pessoa do time consegue explicar “como eu investigo uma decisão bizarra” apenas apontando para telas e fluxos descritos aqui;
- qualquer engenheiro consegue implementar telas e APIs do console sem inventar comportamento, apenas traduzindo este texto em código legível;
- qualquer incidente sério gera, naturalmente, ajustes em agentes/políticas/pipelines que são visíveis, auditáveis e reversíveis via Console;
- olhando o Console pronto, é possível enxergar claramente o triângulo:
  - **dados & memória** (Entidades, Casos, Dossiês, Context Service),
  - **camadas & decisões** (Timeline de Camadas, Debunker, Humano, TruthScore),
  - **operação & governança** (Agent Studio, incidentes, políticas, rollback);

e sentir que tudo foi desenhado para humanos inteligentes, não para ser decodificado por outra IA.

O Capítulo 0.5 e este Adendo 0.5.A v2 juntos formam a especificação oficial do Console Operacional e do Agent Studio da Sprint 25. Capítulos 1–6 só podem especializar, detalhar e implementar o que está escrito aqui.

