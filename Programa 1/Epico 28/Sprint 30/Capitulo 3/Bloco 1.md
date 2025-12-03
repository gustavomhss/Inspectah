# Inspectah — Sprint 30 — Capítulo 3 — Bloco 1
## Papel da Arquitetura na S30 e Visão Geral

### 3.1 Por que este capítulo existe

Nos Capítulos 1 e 2, a Sprint 30 já assumiu um contrato bastante ambicioso:

- transformar o fluxo de notícias em **fluxo‑pivô realmente operável via Console**;
- fazer com que **estados de fluxo** (`draft`, `em_teste`, `ativo`, `pausado`) deixem de ser rótulos decorativos e passem a mandar de fato no roteamento;
- garantir **rastreabilidade ponta a ponta** e **observabilidade mínima de gente grande** para operar 24/7 sem gambiarras.

O Capítulo 3 responde à pergunta inevitável:

> “Onde, exatamente, tudo isso vai morar no código e na arquitetura do Inspectah?”

Este bloco 1 define o **pano de fundo arquitetural** da Sprint 30: quais subsistemas são tocados, quais limites de responsabilidade existem entre eles, e como isso conversa com o que já foi entregue em S29 e em programas anteriores.

Sem este bloco, a S30 correria o risco de virar um amontoado de PRs e scripts, sem uma linha clara atravessando:

- domínio de fluxos;
- orquestração;
- console;
- observabilidade.

### 3.2 Posição da S30 dentro da arquitetura macro do Inspectah

Na visão macro, o Inspectah pode ser pensado (simplificando muito) em quatro grandes camadas:

1. **Ingestão & Normalização** — coleta de dados (notícias, dados públicos, etc.), normalização e tipificação em eventos internos.
2. **Fluxos & Agentes** — orquestração de cadeias de interpretação, classificação, análise, debunking e decisão.
3. **Truth‑DB, Casos & Evidências** — persistência de fatos, estados de casos, vínculos com evidências e trilhas de contestação.
4. **Consoles & APIs de Exploração** — experiências de operação e consumo: consoles administrativos, cockpit de fontes, cockpit de fluxos, UI de casos, etc.

A S30 atua primordialmente na camada **2 (Fluxos & Agentes)** e na interface dessa camada com **1 (Ingestão)** e **4 (Consoles & Observabilidade)**:

- reforçando o modelo de Fluxo de Agentes v1 → v1.5;
- definindo templates canônicos de fluxo (com foco no fluxo de notícias);
- consolidando uma política de roteamento por tipo de entrada + estado de fluxo;
- expondo isso tudo de forma operável no Console de Fluxos;
- tornando execuções de fluxo visíveis em telemetria (métricas + logs estruturados).

A S30 **não** tenta redesenhar o Truth‑DB nem a UI de Casos; ela prepara o terreno para que esses componentes, futuramente, se apoiem em fluxos estáveis de ingestão + agentes.

### 3.3 Quais blocos arquiteturais a S30 encosta

A partir da arquitetura existente pós‑S29, a Sprint 30 encosta, com responsabilidade explícita, nos seguintes blocos:

- **Domínio de Fluxos** (`app/flows/*`):
  - models, schemas, serviços, política de roteamento, engine de execução;
  - templates de fluxo (incluindo `Fluxo_Noticias_Geral_v1`);
  - logs de operação de fluxo.

- **Camada de Orquestração** (`app/orchestration/*` ou equivalente):
  - ponto de entrada para eventos vindos da ingestão;
  - chamada a `route_event_to_flow` para todos os eventos do tipo notícia.

- **APIs de Console de Fluxos** (`app/api/flow_console_routes.py`):
  - endpoints para listar fluxos, ver detalhes, alterar estados, criar a partir de template, acionar reprocessamentos limitados e puxar execuções.

- **Frontend do Console de Fluxos** (`frontend/inspectah-ui/src/features/flows/*`):
  - telas, componentes e hooks de dados para operar fluxos de forma diária;
  - interações que implementam, de fato, a ideia de “cockpit de fluxos”.

- **Observabilidade de Fluxos** (`app/flows/instrumentation.py` + stack de métricas/logs):
  - métricas por fluxo e por etapa;
  - logs estruturados com IDs de correlação.

Cada alteração de arquitetura prevista para a S30 deve cair dentro desses blocos — ou justificar explicitamente, em Capítulo 4, qualquer incursão fora deles.

### 3.4 Princípios arquiteturais específicos da S30

O squad responsável alinha alguns princípios que servirão como bússola para todas as decisões desta sprint:

1. **Fluxos como módulo autocontido de domínio**  
   O módulo `app/flows/` deve concentrar regras de negócio de fluxo (template, estados, roteamento, execução), evitando espalhar decisões críticas em múltiplos serviços.

2. **Console como cliente privilegiado, não dono da verdade**  
   O Console de Fluxos consome APIs de fluxo; ele não implementa lógica de domínio. A verdade sobre estados, roteamento e operações mora no backend.

3. **Observabilidade plugada no domínio, não em hacks de infraestrutura**  
   Instrumentação de fluxo acontece ao lado do domínio (via `instrumentation.py`), não como pós‑processamento de logs genéricos.

4. **Integrações mínimas, porém sólidas**  
   A ponte com ingestão e com o stack de telemetria deve ser simples, bem documentada e difícil de quebrar acidentalmente.

Com isso, o Bloco 1 do Capítulo 3 estabelece a moldura arquitetural da Sprint 30. Os blocos seguintes descem o zoom para:
- mapear, em detalhe, módulos e arquivos (filemap);
- descrever componentes de backend e frontend que serão tocados;
- alinhar tudo isso com os gates e métricas definidos no Capítulo 2.

