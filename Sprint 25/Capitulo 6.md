# Sprint 25 — Capítulo 6 (v2)
## Governança da Verdade, Scorecards, ORR e Ciclo de Confiança Contínua

> Versão v2 — Refinado pelo Squad Verdade & Interpretação em várias rodadas, com revisão de Stonebraker, Norvig, Pearl, Percy, Victor, Jobs e Conselho. Este capítulo fecha a Sprint 25 no nível de governança: define quem manda em quê, com base em quais evidências, como isso aparece em scorecards e ORR, e como o sistema segue confiável amanhã sem reescrever tudo.
>
> Regra de ouro: **nenhuma decisão de verdade é “sagrada”; todas são versionadas, auditáveis e reversíveis de forma controlada, com código legível e processo claro.**

---

### 6.1 Papel estrutural do Capítulo 6 na S25

Capítulos anteriores construíram o corpo da Verdade/Fato v1.5:

- Cap. 0 / 0.5 / 0.A / 0.5.A: cérebro e painel do Sistema de Camadas + Agent Studio.
- Cap. 1: problema e objetivos da S25.
- Cap. 2: gates, métricas e scorecards.
- Cap. 3: arquitetura e filemap em 7 domínios (truth, policies, layers, context, threatmodel, agents, incidents/console).
- Cap. 4: plano de execução (waves, branches, scripts, rotina).
- Cap. 5: dados, golden sets, demos e pacotes de evidência.

Este Cap. 6 responde à pergunta final:

> “Quem tem autoridade para chamar algo de verdade dentro do Inspectah, com base em quê, como essa autoridade é vigiada e como isso evolui sem explodir o sistema?”

Para isso, o capítulo define:

1. Um **modelo de governança da verdade**: papéis, poderes, limites e trilhas de responsabilidade.
2. **Regras normativas de decisão**: quando promover, quando rebaixar, quando parar tudo, quando acionar humano.
3. Uma **arquitetura de scorecards e ORR** que transforma complexidade interna em sinais claros de saúde/risco.
4. Um **ciclo de confiança contínua**: como métricas, incidentes e revisões alimentam ajustes de políticas, camadas, agentes e código.

Tudo isso precisa estar implementado de forma simples, legível e operacional — nada de “constituição em PDF e código que faz outra coisa”.

---

### 6.2 Modelo de Governança: Papéis, Permissões e Fronteiras

A S25 assume que “governar verdade” não é tarefa de um único agente ou humano. É um sistema de checks and balances. O modelo de papéis é minimalista, mas suficiente para o estágio atual.

#### 6.2.1 Papéis principais

1. **Sistema de Camadas (Layers Pipeline)**
   - Papel: interpretar, classificar, avaliar evidências, sugerir decisões.
   - Limite: nunca promove nem rebaixa sozinho; sempre gera recomendações estruturadas (ThoughtTrace → Recommendation) consumidas por Policies + Truth‑DB.

2. **Engine de Políticas (PromotionPolicy)**
   - Papel: traduzir princípios de prudência em regras concretas por domínio (ex.: política, ciência, fofoca).
   - Limite: não inventa evidência; opera só sobre contexto formal (ContextDossier, ThreatSignals, Recommendation das camadas).

3. **ThreatModel**
   - Papel: monitorar padrões de risco (flood narrativo, fonte única, reversões, incidentes) e sinalizar quando o ambiente está “contaminado”.
   - Limite: não decide TruthState, mas pode **bloquear** promoções, forçar rotas endurecidas e abrir incidentes.

4. **Debunker & Comitês de Interpretação (S24)**
   - Papel: revisar casos difíceis, testar hipóteses alternativas, apontar incoerências, sugerir correções.
   - Limite: atuam como “freios de emergência” e camadas de redundância, não como oráculo final.

5. **Operadores Humanos (Console, Agent Studio, Incident Console)**
   - Papel: configurar agentes/políticas, analisar incidentes, intervir em casos extremos, assinar decisões de alto impacto.
   - Limite: não podem “editar verdade” na marra; qualquer intervenção gera registros formais (DecisionRecord, IncidentAction) e passa por política de permissão.

6. **Comitê de Revisão da Verdade (Conselho)**
   - Papel: aprovar políticas por domínio, revisar cenários críticos, decidir GO/NO_GO/GO_WITH_RISKS no ORR.
   - Limite: não atua no “dia a dia” de cada claim; atua por amostras, cenários e incidentes críticos.

7. **Repositório & Historiador (Truth‑DB, Evidence & Bundles)**
   - Papel: registrar o que foi decidido, quando, por quem/qual política, com base em quais evidências.
   - Limite: não decide nada; é a memória e o espelho.

#### 6.2.2 Matriz de decisão (quem pode fazer o quê)

A S25 formaliza uma matriz simples:

- **Promoção de TruthState em domínios não sensíveis**
  - Autorizado por: Camadas + Policies, desde que ThreatModel não sinalize risco crítico.
  - Revisão humana: opcional, mas recomendada para amostras.

- **Promoção em domínios sensíveis (política, saúde, crime)**
  - Autorizado por: Camadas + Policies + ThreatModel **e**, quando configurado, Debunker/Humano‑no‑loop.
  - Exigência mínima: 
    - pipeline endurecido;  
    - ausência de sinais críticos;  
    - registro de decisão com explicação clara.

- **Rebaixamento de TruthState**
  - Autorizado por: Camadas + Policies, ou Debunker + Humano em cenário de correção, sempre com registro de motivo.

- **Abertura e fechamento de Incident**
  - Autorizado por: ThreatModel (automático) ou Operador/Comitê (manual).  
  - Fechamento exige registro de causa raiz e ações.

- **Alteração de Policies/Agentes em produção**
  - Autorizado por: Operador com permissão adequada + revisão mínima do comitê ou processo leve de change management.  
  - Sempre gera nova versão (`PromotionPolicyVersion`, `AgentVersion`) e teste de regressão.

Essa matriz é simples o suficiente para caber num diagrama, mas poderosa o bastante para evitar arbitrariedades.

---

### 6.3 Regras Normativas de Verdade: Promoção, Rebaixamento, Congelamento

A Verdade/Fato v1.5 é prudente por design. Este capítulo torna essa prudência operacional.

#### 6.3.1 Promoção de estados de verdade

Regras mínimas para qualquer promoção relevante:

1. **Contexto suficiente**
   - Um `ContextDossier` adequado (Entidade/Caso) precisa estar disponível e referenciado.

2. **Camadas convergentes**
   - O Sistema de Camadas deve apontar, de forma clara, qual o quadro interpretativo final (via Recommendation e ThoughtTrace).

3. **Política satisfeita**
   - A política de domínio deve retornar recomendação positiva explícita (PromotionPolicyVersion ativa).  
   - Exemplo: política política_2025 prevendo número mínimo de fontes independentes e ausência de incidentes pendentes.

4. **Sinais de ameaça abaixo de thresholds**
   - Threat metrics relevantes (single_source_dependency, reversal_rate, flood, etc.) devem estar dentro dos limites em `configs/threatmodel/thresholds.yaml`.

5. **Domínios sensíveis: requisitos extras**
   - Pipeline endurecido, Debunker/Humano‑no‑loop, possibilidade de contestação facilitada, maior latência aceitável.

Se qualquer um desses eixos falha, a política deve sugerir “não promover” e permanecer em estado prudente.

#### 6.3.2 Rebaixamento e correção

Rebaixar não é vergonha; é requisito de sanidade.

Motivos típicos de rebaixamento:

- novas evidências fortes que contradizem a verdade atual;
- descoberta de erro metodológico em estudos ou dados usados;
- incidente grave (ex.: uso malicioso de fontes, manipulação narrativo);
- decisão inicial tomada sob contexto insuficiente.

Procedimento mínimo:

1. Registrar um novo `TruthChangeEvent` com tipo “rebaixamento/correção”.
2. Associar `DecisionRecord` contendo:
   - evidências novas;
   - ThreatSignals relevantes (se existirem);
   - referência a Incident, se houver.
3. Atualizar `TruthState` para um estado prudente ou “em disputa controlada”.
4. Opcionalmente, disparar notificações em canais internos (fora do escopo do código, mas previsto).

#### 6.3.3 Congelamento e “zona de observação”

Em domínios ultra sensíveis ou sob ataque adversarial ativo, o sistema pode entrar em modo de “congelamento de promoções” para alguns casos.

Critérios gerais:

- ThreatModel sinaliza risco alto para Entidade/Caso ou domínio;  
- políticas de domínio definem que, em certos padrões, promoções devem ser travadas até revisão humana.

Operacionalmente:

- Promoções são bloqueadas por Policy;  
- Incident é aberto ou anotado;  
- claims podem permanecer em estados intermediários por mais tempo, conscientemente.

---

### 6.4 Scorecards, Painéis e ORR: Como a Governança Vira Decisão

Scorecards e ORR são o “front-end” da governança. Eles traduzem tudo acima em um veredito operacional.

#### 6.4.1 Estrutura dos scorecards S25_G* (versão de governança)

Todos os scorecards S25_G* compartilham uma estrutura JSON básica, com campos voltados explicitamente à governança:

- `gate_id`, `gate_name`, `sprint`;
- `status` (GO, NO_GO, GO_WITH_RISKS);
- `governance_dimension` (truth_state, policy, layers, threatmodel, console, code_quality, orr);
- `metrics` (objeto com métricas específicas do gate);
- `sensitive_domains_covered` (lista);
- `golden_sets_exercised` (lista);
- `risks` (array de objetos com severidade, descrição, plano);
- `evidence_paths` (lista de paths em `out/evidence/S25_GX_*/`).

O Codex deve gerar scorecards alinhados a esse formato, com foco em:

- clareza (nomes autoexplicativos),
- simplicidade (sem estruturas aninhadas absurdas),
- correlação direta com evidências físicas em disco.

#### 6.4.2 Visão agregada de governança (dashboard lógico)

A S25 define o “wireframe lógico” de um futuro Dashboard de Governança, que pode ser implementado em sprints seguintes:

- **Cards por dimensão**: TruthState, Policies, Layers/Context, ThreatModel, Console/Agents, CodeQuality, ORR.
- **Semáforo de domínios sensíveis**: status agregado (verde/amarelo/vermelho) para política, saúde, crime, etc.
- **Métricas chave**:
  - latência média de promoção por domínio;
  - taxa de reversão;
  - incidentes abertos/fechados no período;
  - cobertura de golden sets;
  - % de promoções com ThreatSignals próximos de threshold.

Todos esses dados podem ser derivados de:

- scorecards S25_G*;
- consultas simples em Truth‑DB, ThreatModel e Incidents;
- registros do Evidence Vault futuro.

A S25 não precisa construir a UI completa, mas precisa garantir que: dados, modelos e evidências estão prontos para alimentar esse painel sem retrabalho massivo.

#### 6.4.3 ORR da S25 como ritual de governança

O ORR da S25, suportado por `bin/s25_orr.sh`, segue um fluxo claro:

1. **Entrada**
   - scorecards `S25_G*.json`;
   - bundles `s25_full_orr_bundle_*.zip` (Cap. 5);
   - docs de demos, cenários e decisões anteriores (Cap. 5 e este Cap. 6).

2. **Processo**
   - leitura e discussão dos scorecards;  
   - revisão de pelo menos:
     - um golden set por família;  
     - um cenário adversarial crítico (flood ou similar);
     - amostra de incidentes abertos/fechados.
   - avaliação de métricas de governança (latência, reversão, contestação, cobertura).

3. **Saída**
   - decisão GO/NO_GO/GO_WITH_RISKS registrada em `S25_ORR_summary.json` + documento humano (`docs/sprint_25_orr_decision.md`);
   - lista explícita de riscos residuais e recomendações para próximas sprints.

O ORR não é um teatro: é onde o comitê assume responsabilidade explícita pela governança da Verdade/Fato v1.5.

---

### 6.5 Ciclo de Confiança Contínua: Como a Governança Evolui

A S25 não promete perfeição eterna; promete um ciclo saudável de aprendizado.

#### 6.5.1 Feedback loop entre métricas, incidentes e políticas

A arquitetura S25 prevê que:

- métricas de governança (latência, reversão, contestação, etc.) sejam medidas e revisadas periodicamente;
- incidentes recorrentes em certos domínios disparem revisão de políticas, camadas, agentes ou thresholds do ThreatModel;
- decisões particularmente difíceis (casos “de vitrine”) sirvam como aprendizado para refinar golden sets e demos.

Operacionalmente, isso significa que, após a S25:

- ajustes em `PromotionPolicyVersion` e `AgentVersion` devem sempre ser precedidos por:
  - revisão das métricas;
  - análise de incidentes;
  - reexecução de golden sets como regressão.

#### 6.5.2 Papel do Evidence Vault e do Sistema de Blocos (futuro)

A disciplina de evidências da S25 prepara o terreno para:

- um **Evidence Vault** robusto, onde bundles de sprints, golden sets, logs e reviews são archivados com políticas de retenção e privacidade;
- uma camada de **Sistema de Blocos** e ancoragem em blockchain, onde fatos consolidados e seus metadados de governança (TruthRecord, DecisionRecord, ThreatSignals, Incident summaries) podem ser ancorados de forma imutável.

A governança de hoje precisa assumir que, amanhã, alguém poderá auditar tudo isso olhando para um bloco ancorado — e que a narrativa vai bater com os artefatos que a S25 produziu.

#### 6.5.3 Código humano como requisito de governança

Por fim, repetir o ponto que atravessa a S25 inteira:

> **Código ilegível é falha de governança.**

Não adianta ter políticas lindas em papel se a implementação for um monstro que ninguém entende. A S25 exige que:

- lógica de estados, políticas, camadas e ThreatModel seja expressa em código simples, modular, bem nomeado e testado;
- prompts de agentes sejam configuráveis e versionados de forma clara, com testes de regressão via Agent Studio;
- qualquer engenheiro sênior razoável consiga, em tempo limitado, auditar a lógica de governança olhando para: código, scorecards, evidências e docs desta sprint.

---

### 6.6 Resultado esperado da governança na Sprint 25

Se este capítulo for implementado e exercido conforme os Cap. 1–5 e 7:

- a Verdade/Fato v1.5 deixa de ser “um conjunto de heurísticas de GPT” e passa a ser um sistema governado, com papéis claros, políticas explícitas, sinais de ameaça monitorados e trilhas completas;
- scorecards, bundles e cenários executados permitem que qualquer revisor independente avalie se o sistema está pronto para o uso proposto;
- o ORR da S25 torna‑se um ritual de responsabilidade, não um carimbo automático;
- e a plataforma Inspectah ganha um esqueleto de governança que pode ser estendido, mas não precisa ser destruído, quando Evidence Vault, Sistema de Blocos e ancoragem entrarem em cena.

Em outras palavras: a S25 entrega não só uma máquina de verdade, mas também as regras, instrumentos e provas necessárias para confiar nela — e para ajustá‑la quando o mundo mudar.

