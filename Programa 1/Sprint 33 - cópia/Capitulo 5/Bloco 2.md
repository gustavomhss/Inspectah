# Sprint 33 — Capítulo 5

## Bloco 2 — Padrões consagrados que a S33 incorpora

Este bloco detalha, em nível mais fino, **quais padrões consagrados de operação** a Sprint 33 incorpora explicitamente e como eles aparecem na arquitetura, nos gates e nos artefatos da sprint. A ideia é tornar claro que a S33 não é "operação by feeling": ela está ancorada em práticas reconhecidas, traduzidas para o contexto do Inspectah.

Vamos olhar cinco eixos principais:

1. SLOs como contrato operacional.
2. Incident como entidade de domínio com lifecycle.
3. Runbooks versionados como parte do sistema.
4. Cockpit/console de operação como feature de primeira classe.
5. Gates, scorecards e ORR como formalização de prontidão.

---

### 5.2.1 SLOs como contrato operacional, não decoração

**Padrão consagrado:** Em SRE moderno, SLOs (Service Level Objectives) são o contrato entre o sistema e quem depende dele. São expressos como metas numéricas (ex.: 99,9% de disponibilidade, P95 de latência abaixo de X ms) e servem de referência para decisões de risco.

**Como a S33 incorpora esse padrão:**

- **Definição explícita em doc**  
  A S33 exige que os SLOs do recorte da sprint estejam definidos em um documento dedicado (`docs/s33/s33_slos.md`). Não basta dizer "queremos que esteja rápido"; é necessário especificar:
  - o que está sendo medido (métrica base);
  - qual janela temporal se aplica;
  - qual valor é considerado aceitável;
  - a quais componentes isso se aplica.

- **Representação em domínio (`ops_slos`)**  
  Os SLOs não vivem apenas no doc. Eles são carregados em um módulo de domínio (`ops_slos`), que descreve para o sistema o que é um SLO, quais atributos possui e como se relaciona com componentes.

- **Avaliação por um serviço dedicado (`ops_slo_evaluator`)**  
  Em vez de cada trecho do código inventar sua própria forma de verificar SLOs, a S33 centraliza essa lógica em `ops_slo_evaluator`. Esse serviço:
  - lê definições de SLO;
  - executa queries na stack de observabilidade ou em mocks controlados;
  - retorna estados (OK, VIOLATED, NO_DATA) que o cockpit exibe.

- **Integração com UI e gates**  
  O `SloSummaryPanel` no cockpit mostra o estado dos SLOs; o gate G3 verifica, via scripts, se os SLOs definidos estão sendo de fato avaliados. Assim, SLO deixa de ser slide de apresentação e vira parte funcional do sistema.

---

### 5.2.2 Incident como entidade de domínio com lifecycle real

**Padrão consagrado:** Plataformas modernas tratam incidentes como objetos com ciclo de vida, severidade, histórico de transições, ligações com componentes/serviços e, muitas vezes, gatilhos automáticos.

**Como a S33 incorpora esse padrão:**

- **Modelo `Incident` em domínio**  
  A S33 define um modelo `Incident` em `app/domain/incidents.py`, com campos como:
  - `id`, `title`, `description`;
  - `state` (ex.: OPEN, TRIAGE, MITIGATED, RESOLVED);
  - `severity` (LOW, MEDIUM, HIGH, CRITICAL);
  - `component_ids` afetados;
  - timestamps relevantes (abertura, mitigação, resolução).

- **Lifecycle documentado e testado**  
  O doc `s33_incidents_lifecycle.md` especifica quais transições de estado são permitidas e sob quais condições. Esse lifecycle não é apenas teoria: testes automatizados verificam que o modelo respeita essas regras.

- **Vinculação a componentes e SLOs**  
  Incident não é genérico: ele aponta para componentes do `components_map` e, quando relevante, para SLOs que foram violados. Isso cria uma malha interpretável de "problema ↔ componente ↔ meta impactada".

- **Integração com cockpit**  
  A S33 define páginas de lista e detalhe de incidentes no cockpit, onde esses atributos aparecem de forma navegável. Isso aproxima o comportamento do Inspectah de ferramentas especializadas de gestão de incidentes.

---

### 5.2.3 Runbooks versionados como parte da operação

**Padrão consagrado:** Em ambientes de alta confiabilidade, runbooks (playbooks de resposta a incidentes) são tratados como ativos de primeira classe, versionados junto com o código e integrados às ferramentas de operação.

**Como a S33 incorpora esse padrão:**

- **Runbooks em `docs/s33/runbooks/`**  
  Os runbooks da S33 são arquivos versionados em um diretório específico. Cada arquivo segue um formato mínimo:
  - contexto do problema;
  - sinais de alerta;
  - passos de diagnóstico;
  - passos de mitigação/contorno;
  - critérios de sucesso;
  - links para painéis/logs relevantes.

- **Ligação explícita com incidentes e componentes**  
  Runbooks não são genéricos: eles são associados a tipos de incidente ou a componentes específicos. Essa associação aparece tanto em docs quanto no cockpit (por exemplo, em `RunbookLinks`).

- **Validação prática via G4**  
  O gate G4 exige que pelo menos um incidente seja percorrido usando um runbook real. O bundle de evidência do incidente inclui o runbook usado e notar quais passos funcionaram ou precisaram de ajuste.

- **Evolução contínua**  
  Como runbooks vivem no repositório, revisões e melhorias podem ser feitas via PR, com revisão de pares, da mesma forma que código. A S33 estabelece essa cultura.

---

### 5.2.4 Cockpit de operação como feature de primeira classe

**Padrão consagrado:** Plataformas maduras oferecem consoles ou cockpits de operação dedicados, isolados da UI de usuário final, com visão e ações voltadas à confiabilidade.

**Como a S33 incorpora esse padrão:**

- **Feature isolada no frontend (`oracleops`)**  
  A S33 define uma feature `oracleops` com rotas, páginas e componentes próprios, como:
  - `OverviewPage` — visão geral de saúde do recorte;
  - `ComponentDetailsPage` — foco em um componente;
  - `IncidentsListPage` e `IncidentDetailsPage` — lista e detalhe de incidentes.

- **Cliente de API dedicado (`opsCockpitClient`)**  
  Em vez de chamadas HTTP soltas, o cockpit usa um cliente dedicado para comunicar com as rotas `ops_cockpit`. Isso reforça o acoplamento saudável entre o domínio de operação e a UI de operação.

- **Componentes de visualização orientados a perguntas reais**  
  Componentes como `SloSummaryPanel`, `ComponentHealthTable` e `RunbookLinks` são desenhados para responder diretamente às perguntas do operador: o que está ruim? o que está em risco? o que fazer agora?

- **Integração com a arquitetura de programas**  
  O cockpit é desenhado para refletir a estrutura de programas e sprints do Inspectah, permitindo que recortes específicos (como o da S33) sejam observados e operados de forma consistente.

---

### 5.2.5 Gates, scorecards e ORR como revisão operacional formal

**Padrão consagrado:** Muitas organizações praticam revisões de prontidão (operational readiness reviews) para garantir que novos serviços ou mudanças significativas estejam realmente operáveis antes de produção.

**Como a S33 incorpora esse padrão:**

- **Gates G0–G5 com scripts associados**  
  Cada gate encapsula uma pergunta de prontidão (escopo, domínio de incidentes, cockpit, SLOs, runbooks, ORR) e tem um script em `bin/` que o verifica.

- **Scorecards em `out/scorecards/`**  
  O estado de cada gate é registrado em JSON estruturado. Isso permite saber, sem narrativas, qual era a situação da sprint em determinado commit.

- **Evidências em `out/evidence/`**  
  Logs, capturas de cockpit, resultados de queries e bundles de incidentes sustentam os scorecards.

- **ORR operacional (G5) com roteiro e ata**  
  A S33 exige uma sessão de ORR com roteiro claro, papéis definidos, execução prática e registro de feedbacks. O resultado alimenta tanto os scorecards quanto os docs de aprendizado (`s33_incidents_learnings.md`).

Esse conjunto forma uma camada de governança operacional que vai além de "parece estar pronto". A S33 formaliza prontidão como algo testado, registrado e auditável.

---

### 5.2.6 Síntese: de boas práticas isoladas a sistema coerente

Cada um dos padrões acima já existe, de forma isolada, em diferentes ferramentas e organizações. O que torna a S33 interessante no contexto do estado da arte é a **integração coerente** desses elementos:

- SLOs não estão só em planilhas: alimentam o domínio, a stack de observabilidade e o cockpit.
- Incident não é apenas um ticket: é entidade com lifecycle e bundles de evidência.
- Runbooks não são páginas soltas: vivem no repositório, ligados ao cockpit e a incidentes.
- Cockpit não é dashboard aleatório: é feature pensada para operação do recorte da sprint.
- Gates, scorecards e ORR não são burocracia: são a coluna vertebral que garante que tudo isso está funcionando antes de chamar a sprint de DONE.

Este Bloco 2, portanto, explicita os "tijolos" de boas práticas que a S33 incorpora. Nos próximos blocos, o capítulo explora como o Inspectah diverge (positivamente) do mainstream ao aplicar esses padrões a um sistema de verdade e quais caminhos de evolução se abrem a partir daqui.