# Sprint 25 — Capítulo 5 (v2)
## Evidências, Golden Sets, Demos Oficiais e Auditoria de Verdade/Fato v1.5

> Versão v2 — Refinado em ciclos sucessivos pelo Squad Verdade & Interpretação, com revisão de Stonebraker, Norvig, Pearl, Percy, Victor, Jobs e Conselho. Este capítulo é o **contrato de evidências** da Sprint 25: define quais dados usamos, como demonstramos o sistema, como empacotamos provas e como garantimos que qualquer humano competente consiga auditar o comportamento da Verdade/Fato v1.5 sem depender de “magia de IA”.
>
> Regra de ouro: **nenhuma afirmação de sucesso da S25 é aceita sem evidência concreta, reprodutível e ancorada em código legível e simples.**

---

### 5.1 Função estrutural do Capítulo 5 na S25

Capítulos 0/0.5/0.A/0.5.A descrevem o cérebro e o painel do Sistema de Camadas. Cap. 1 define o problema. Cap. 2 define gates e métricas. Cap. 3 define arquitetura e filemap. Cap. 4 define o plano de execução. Este Cap. 5 amarra tudo respondendo:

> “Quais histórias, dados e artefatos concretos provam que a Verdade/Fato v1.5 está funcionando, e como qualquer pessoa consegue verificar isso de forma independente?”

Para isso, o capítulo:

1. Define uma **biblioteca oficial de golden sets** — casos canônicos de verdade em ação.
2. Especifica **tipos de dados de teste** e limites de segurança/privacidade.
3. Descreve **roteiros de demo oficiais** (para ORR e validação contínua).
4. Define a **estrutura dos pacotes de evidência** por gate e dos bundles da S25.
5. Fornece **checklists de auditoria** para decisões de verdade e para código humano.
6. Explica como tudo isso entra no ORR e nas sprints futuras (Evidence Vault, Sistema de Blocos, ancoragem).

Nenhuma parte deste capítulo é “sugestão”: é contrato operacional. O Codex e o time devem tratar esta especificação como fonte de verdade para dados de teste, demos e pacotes de evidência.

---

### 5.2 Golden Sets da S25 — Biblioteca Canônica de Casos

A S25 institui uma **biblioteca oficial de golden sets**: pequenos conjuntos de casos canônicos, desenhados a dedo para exercitar tudo que a Verdade/Fato v1.5 promete. Eles não são “tests aleatórios”: são **histórias completas**, com começo, meio, reviravolta e desfecho, que atravessam o Sistema de Camadas, Políticas, Context, ThreatModel, Console e Incidentes.

#### 5.2.1 Propriedades obrigatórias de um golden set

Cada golden set S25 precisa satisfazer, no mínimo:

1. **Foco narrativo claro**  
   - Uma Entidade central (pessoa, instituição, empresa, evento) e um ou poucos Casos bem definidos.  
   - Fácil de contar para um humano em 2–3 parágrafos.

2. **Timeline rica e não trivial**  
   - Múltiplos eventos distribuídos no tempo (notícias, declarações, dados, revisões, correções).  
   - Permite observar: formação, ajuste e consolidação do TruthState.

3. **Conflito, ruído e nuance**  
   - Fontes que discordam; números que mudam; posições oficiais que recuam ou são desmentidas; ruídos típicos do mundo real.  
   - Obriga o Sistema de Camadas + Políticas + ThreatModel a trabalhar.

4. **Resultado esperado explicitamente documentado**  
   - Um arquivo em linguagem humana descrevendo: quais estados de verdade esperamos ao longo da timeline, em que momentos é aceitável ficar em estado incerto, quando a promoção deve acontecer e o que seria considerado “erro grave”.

5. **Reprodutibilidade total em dev/stage**  
   - Todos os eventos podem ser carregados via scripts presentes no repo.  
   - Sem dependência de APIs externas em tempo de execução para rodar o golden set.

6. **Compatibilidade com domínios sensíveis**  
   - Para política, saúde, crime, etc., o golden set precisa respeitar as regras de domínio sensível (fluxo endurecido, Policy e ThreatModel atentos, potencial de incidente.

#### 5.2.2 Famílias de golden sets

A S25 terá, no mínimo, uma instância de golden set para cada uma destas famílias:

1. **Política institucional (domínio ultra sensível)**  
   - Entidade: governante fictício ou órgão institucional.  
   - Caso: escândalo de desvio de verba ou decisão controversa.  
   - Eventos:
     - denúncia inicial em fonte de baixa credibilidade;  
     - replicação por mídias de grande porte;  
     - nota oficial negando;  
     - surgimento de documentos/provas;  
     - investigação formal;  
     - eventual conclusão (arquivamento ou condenação).

2. **Fraude corporativa / crime econômico**  
   - Entidade: empresa fictícia listada em bolsa;  
   - Caso: maquiagem de balanço / fraude contábil.  
   - Eventos: relatórios de analistas, balanços conflitantes, whistleblower, agência reguladora, etc.

3. **Evento climático / desastre natural**  
   - Entidade: região/cidade;  
   - Caso: furacão/enchente com estimativas de danos e vítimas.  
   - Eventos: previsões, avisos, dados preliminares, revisões, relatórios finais.

4. **Fato científico em evolução**  
   - Entidade: afirmação científica específica (ex.: eficácia de um tratamento).  
   - Caso: trajetória desde pré‑print, estudo inicial, replicações, metanálise.  
   - Eventos: estudos contraditórios, revisões de guidelines, retratações.

5. **Fofoca / celebridade / cultura pop**  
   - Entidade: figura pública fictícia;  
   - Caso: rumor de relacionamento ou escândalo pessoal.  
   - Eventos: rumor, boatos, “fontes próximas”, pronunciamento oficial, confirmação/desmentido, novas evidências.

Essas famílias cobrem espectro de impacto, sensibilidade, ruído e reversões. Em futuras sprints, a biblioteca pode crescer, mas a S25 consolida as primeiras cinco.

#### 5.2.3 Estrutura de arquivos dos golden sets

Estrutura proposta no repo:

- `data/s25/golden_sets/`
  - `politics_case_01/`
  - `corporate_case_01/`
  - `climate_case_01/`
  - `science_case_01/`
  - `gossip_case_01/`

Dentro de cada diretório:

- `entities.yaml`  
  - Entidades envolvidas (id estável, tipo, descrição humana).  
  - Casos: id, descrição, tipo (política, ciência, etc.).

- `events.yaml`  
  - Lista ordenada de eventos: timestamp lógico, tipo (notícia, declaração, dado), fonte (tipada por credibilidade), payload simplificado (ex.: referência a texto, label de “conteúdo positivo/negativo/neutro”, marcadores).

- `expected_behaviour.md`  
  - Narrativa humana de como esperamos que a Verdade/Fato v1.5 se comporte ao longo da timeline.

- `adversarial_scenarios.yaml` (opcional, mas recomendado)  
  - Variações específicas para ThreatModel/G7 (flood narrativo, reempacotamento malicioso, etc.).

O código que carrega e injeta esses dados na pipeline vive em módulos simples (por exemplo, `app/threatmodel/test_scenarios.py` ou `app/demo/golden_sets_loader.py`), com funções pequenas e comentadas.

---

### 5.3 Tipos de dados de teste e limites de segurança

A S25 estabelece uma tipologia clara de dados de teste, para evitar o caos entre sintético, inspirado e real.

#### 5.3.1 Sintético puro

- Construído do zero, sem ligação rastreável a pessoas/entidades reais.
- Ideal para a maior parte dos golden sets.
- Total liberdade para exercícios de ThreatModel (podemos “forçar” situações extremas).

#### 5.3.2 Inspirado em casos reais, porém pseudonimizado

- Estrutura, ritmo temporal e dinâmica geral inspirados em eventos históricos, mas com:
  - nomes alterados;
  - datas embaralhadas;
  - detalhes sensíveis removidos ou trocados.
- Objetivo: preservar a “forma” do problema real sem expor dados sensíveis.

#### 5.3.3 Dados reais (controlados)

- Só para casos MUITO específicos, com critérios fortes:
  - datasets públicos e anonimizados;
  - sem dados pessoais sensíveis;
  - sem risco de quebrar leis ou comprometer privacidade.
- Mesmo assim, tratados como “de passagem”: S25 idealmente constrói versões sintéticas equivalentes para uso de rotina.

#### 5.3.4 Regras de segurança e LGPD

- Nenhum dado que permita identificar uma pessoa física real sem necessidade e plano claro de anonimização.
- Tudo que extrapola o escopo de teste sintético/pseudonimizado é marcado explicitamente em doc e nos scorecards como risco e como dívida (para Evidence Vault futura).
- Scripts de construção de dados de teste (para qualquer tipo) vivem no repo, são legíveis e versionados.

---

### 5.4 Roteiros de Demo Oficiais da S25

A S25 define um conjunto enxuto de **demos oficiais**, usadas para ORR, validação interna recorrente e demonstrações de produto. São roteiros repetíveis, com passos numerados e observáveis.

Os roteiros são descritos em `docs/sprint_25_demos.md` e referenciados pelos scripts de gate (especialmente S25_G4 e S25_G7).

#### 5.4.1 Estrutura padrão de um roteiro de demo

Cada demo tem:

- **Nome e objetivo**  
  - Ex.: “Demo 1 — Linha do tempo de verdade em caso político sensível”.

- **Pré‑requisitos técnicos**  
  - Branch / tag;  
  - migrações aplicadas;  
  - scripts de preload de dados.

- **Passo a passo numerado**  
  - Comandos CLI (scripts Python, binários);
  - URLs do Console a acessar;
  - cliques e interações relevantes.

- **Checklist de observação**  
  - O que olhar no Truth Console, Threat Dashboard, Incidents, Agent Studio.

- **Referências de evidência**  
  - Onde o output daquele roteiro aparece em `out/evidence/S25_GX_*/`.

#### 5.4.2 Demo 1 — Linha do tempo em caso político sensível

Objetivo: demonstrar o Sistema de Camadas, Políticas, Context e ThreatModel trabalhando juntos num domínio sensível, com timeline complexa.

Resumo da execução:

1. Carregar o golden set `politics_case_01` usando script simples (ex.: `python -m app.demo.load_golden politics_case_01`).
2. Rodar pipeline para os eventos na ordem temporal (via script ou API) — o Sistema de Camadas processa tudo, gera `LayersTrace`, `ContextDossier`, `DecisionRecord`, `TruthChangeEvent`.
3. Abrir Console na página TruthRecord da claim principal.
4. Confirmar:
   - estados de TruthState e sua timeline;
   - ThoughtTrace (camadas, agentes, outputs);  
   - DecisionTrace (política, contexto, explicações);
   - Threat metrics relevantes (ex.: single_source_dependency, reversal_rate) em pelo menos um ponto crítico da timeline.
5. Comparar o comportamento observado com `expected_behaviour.md` desse golden set (diferenças importantes viram incidentes ou ajustes de política).

#### 5.4.3 Demo 2 — Fato científico que muda com o tempo

Objetivo: mostrar que o sistema não “crava verdade cedo demais” e consegue recuar ou ajustar frente a novas evidências.

Fluxo similar, agora com `science_case_01`:

- no início, TruthState permanece prudente (ex.: “em avaliação”, “hipótese em teste”);  
- com evidências mais robustas, ocorre promoção com explicações claras;  
- se surgirem refutações fortes, o sistema pode recuar ou marcar o fato como controverso, com rastreabilidade total.

#### 5.4.4 Demo 3 — Cenário adversarial de flood narrativo

Objetivo: exercitar ThreatModel, Incident Console e guardrails de promoção.

Fluxo (usando variações em `adversarial_scenarios.yaml`):

1. Injetar eventos que simulam flood coordenado de narrativas (muitas fontes repetindo a mesma afirmação duvidosa).
2. Observar Threat metrics específicas de flood.  
3. Confirmar que o sistema não promove verdades frágeis automaticamente (bloqueios de política, flags de risco).  
4. Verificar se ThreatModel gera ThreatSignals e, se configurado, abre Incident ligado à Entidade/Caso.
5. Usar o Incident Console para acompanhar ciclo de vida do incidente.

Outras demos (ex.: uso do Agent Studio para ajustar agente de camada + regressões) podem ser definidas como “Demo 4+”, mas as três acima formam o **núcleo obrigatório** da S25.

---

### 5.5 Estrutura de Evidências por Gate

Cap. 2 descreve os gates; Cap. 4 descreve como executá‑los; este Cap. 5 define **o que precisa existir em disco** para que cada gate seja auditável.

#### 5.5.1 Convenção de diretórios

Para cada gate S25_GX, o script correspondente deve garantir a criação de:

- `out/scorecards/S25_GX_<nome>.json` — scorecard sintético (status, métricas, riscos).  
- `out/evidence/S25_GX_<nome>/` — diretório raiz de evidências.

Dentro de cada `out/evidence/S25_GX_*/`, convencionar subpastas (usar apenas as necessárias):

- `tests/` — saídas relevantes de testes automatizados (logs/texto, snapshots).  
- `logs/` — logs de execução de scripts/gates (stdout/stderr, quando útil).  
- `screens/` — screenshots ou exports estáticos de UI (Truth Console, Threat Dashboard, Incident Console, Agent Studio).  
- `scenarios/` — inputs/fixtures utilizados para cenários específicos (especialmente G3, G5, G7).  
- `analysis/` — notas de análise humana (por exemplo, interpretação de um cenário adversarial).  
- `review_notes/` — notas de code review, usadas fortemente em S25_G6.

Scripts `bin/s25_gX_*.sh` devem ser escritos de forma simples, com comentários explicando o que é capturado em cada subpasta.

#### 5.5.2 Mapeamento gate → evidências mínimas esperadas

Exemplos (não exaustivo, mas obrigatório como base):

- **S25_G0 (scope & baseline)**  
  - Scorecard com presença de docs e estrutura;  
  - evidência de `git status` limpo;  
  - execução mínima de testes de sanidade.

- **S25_G1 (TruthState machine)**  
  - testes de `tests/truth/`;  
  - exemplos de timelines em `analysis/`;  
  - pelo menos um caso de transição bloqueada documentado (tentativa inválida).

- **S25_G2 (PromotionPolicy)**  
  - simulações rodadas;  
  - policies YAML válidas salvas;  
  - casos em que política bloqueia ou adia promoção com explicação clara.

- **S25_G3 (Layers & Context integrados)**  
  - traces de pipeline completos em `scenarios/`;  
  - dumps de LayersTrace + ContextDossier;  
  - evidência de que claims em domínios sensíveis passaram por pipeline endurecido.

- **S25_G4 (Console & Agent Studio)**  
  - screenshots de páginas críticas (TruthRecord, ThoughtTrace, Threat Dashboard, Incident Console, Agent Studio);  
  - logs de navegação de cenários (requests/response minimamente logados).

- **S25_G5 (ThreatModel sinais & métricas)**  
  - saídas de métricas para cenários de teste;  
  - pelo menos um exemplo de deteção de anomalia.

- **S25_G6 (Human code quality)**  
  - logs de linters/typecheckers;  
  - notas de review em `review_notes/`, apontando onde o código foi simplificado ou esclarecido.

- **S25_G7 (Threat model coverage)**  
  - cenários adversariais executados com resultados armazenados;  
  - análise humana em `analysis/` ligando cenários aos sinais gerados.

- **S25_G8 (ORR)**  
  - scorecard consolidado S25_ORR;  
  - ata de decisão GO/NO_GO/GO_WITH_RISKS.

---

### 5.6 Bundles de Auditoria da S25

Para facilitar ORR, auditorias externas e revisões futuras, a S25 define um formato padrão de bundles zipados.

#### 5.6.1 Estrutura dos bundles

Em `out/bundles/`, scripts dedicados (por exemplo, `bin/s25_make_bundle.sh`) geram arquivos como:

- `s25_full_orr_bundle_<yyyy-mm-dd>_<hash>.zip`

Conteúdo mínimo do bundle:

- todos os `out/scorecards/S25_G*.json`;
- `out/scorecards/S25_ORR_summary.json`;
- diretórios `out/evidence/S25_G*/` (com subpastas relevantes);
- `docs/sprint_25_demos.md` (roteiros de demo);
- `docs/sprint_25_threat_scenarios.md` (cenários adversariais);
- resumo `README_S25_BUNDLE.md` explicando:
  - versão da base de código;  
  - como reproduzir as demos principais;  
  - onde encontrar evidências de cada gate.

Bundles devem ser:

- automaticamente geráveis (nada manual);
- reproduzíveis (mesmo código + mesmos dados de teste → bundle compatível);
- suficientemente pequenos para serem tratados como artefatos de CI (sem dumps gigantes desnecessários).

---

### 5.7 Checklists de Auditoria — Decisões de Verdade e Código Humano

Para que a S25 seja auditável por humanos, este capítulo inclui checklists explícitos.

#### 5.7.1 Checklist de auditoria de decisão de verdade (claim/caso)

Dado um claim/caso (idealmente em um golden set), o auditor deve conseguir responder, **usando apenas artefatos da S25**:

1. **Qual é o TruthState atual?**  
   - Onde ver: `TruthRecord` no Truth Console / API.

2. **Como o TruthState chegou até aqui?**  
   - Onde ver: `TruthChangeEvents` (timeline) e `DecisionRecord` associados.

3. **Quais evidências foram consideradas?**  
   - Onde ver: `ContextDossier` (facts/claims anteriores), `LayersTrace`, outputs de comitês/Debunker/humano.

4. **Que política foi usada para decidir?**  
   - Onde ver: `policy_id`/`policy_version` no `TruthChangeEvent`, detalhes em `PromotionPolicyVersion`.

5. **Havia sinais de ameaça relevantes?**  
   - Onde ver: `ThreatSignal` e métricas no período correspondente.

6. **Houve intervenção humana direta?**  
   - Onde ver: `human_decision_ref` em `DecisionRecord` e, se existir, Incident associado.

Se qualquer uma dessas perguntas ficar sem resposta com o material da S25, temos um problema de observabilidade/evidência que precisa ser corrigido.

#### 5.7.2 Checklist de auditoria de código humano (reforçando S25_G6)

Para cada módulo crítico (truth, policies, layers, context, threatmodel, console, agents, incidents), o auditor verifica:

1. O arquivo é legível de ponta a ponta em tempo razoável, sem “paredes de código” desnecessárias?  
2. Funções principais têm nomes por intenção (o que fazem) e não por implementação (como fazem)?  
3. Há docstrings/comentários apenas onde a lógica não é óbvia, sem poluir o código?  
4. Existem testes que cobrem os caminhos normais e pelo menos um caminho de falha, com nomes descritivos?  
5. Regras críticas de verdade/política/métricas estão em código versionado, não enterradas em prompts obscuros?  
6. Todo uso de IA (prompts de agentes) está encapsulado em estruturas claras (`AgentVersion`), com testes de regressão associados?  
7. Quaisquer gambiarras necessárias estão marcadas como débitos e aparecem nos scorecards / review_notes?

As respostas, incluindo “achados” e correções feitas, são registradas em arquivos simples (por exemplo, `out/evidence/S25_G6_human_code_quality/review_notes/<modulo>.md`).

---

### 5.8 Integração com ORR, Evidence Vault e Sistema de Blocos (futuro)

Por fim, a S25 não é o fim da história, mas a base.

- **ORR da S25 (S25_G8)**  
  - Usa diretamente: scorecards, evidências, bundles e roteiros de demo definidos aqui.  
  - A decisão GO/NO_GO/GO_WITH_RISKS deve referenciar explicitamente: golden sets, cenários adversariais e auditorias de código.

- **Evidence Vault (sprints futuras)**  
  - Os artefatos de S25 (golden sets, bundles, logs, reviews) são candidatos naturais a serem migrados para o Evidence Vault, com políticas de retenção e anonimização mais refinadas.

- **Sistema de Blocos & ancoragem (Fase 2)**  
  - Verdades, decisões e metadados consolidados na S25 (TruthRecord, TruthChangeEvent, DecisionRecord, ThreatSignals, ContextDossiers) formam o “payload” ideal a ser ancorado em blocos imutáveis.  
  - A clareza e disciplina de evidência deste capítulo é o que torna essa ancoragem possível sem virar retro‑engenharia caótica.

Se este Cap. 5 for seguido à risca, ao final da Sprint 25 teremos:

- uma pequena biblioteca de histórias canônicas exercitando a Verdade/Fato v1.5;
- dados de teste organizados, não sensíveis, reusáveis e bem documentados;
- demos oficiais poderosas, repetíveis e fáceis de entender;
- pacotes de evidência que qualquer auditor independente consegue navegar;
- e um sistema de Verdade/Fato v1.5 cujo comportamento é explicável, reproduzível e ajustável por humanos — sem caixas‑pretas indecifráveis, mesmo que haja IA ajudando nos bastidores.

