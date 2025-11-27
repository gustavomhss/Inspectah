# 6.3 – Débitos Assumidos (Técnicos, de Produto e de Governança) – v2 extremo

Este 6.3 v2 extremo é a versão refinada, mais densa e mais útil dos débitos assumidos na trilha **Verdade & Interpretação / Casos Inspectah**.

Ele não é um desabafo nem uma lista de TODOs soltos. Ele é um **mapa explícito de onde o sistema está, por escolha, aquém do ideal**, com três funções práticas:

1. Proteger o time do autoengano – nada aqui é “surpresa futura”, tudo é sabido e assumido.  
2. Alimentar diretamente o backlog de S23–S25 e a Fase 2 (Sistema de Blocos, reputação, comunidade, on‑chain).  
3. Servir de checklist de dívida: a cada ciclo de planejamento, revisitamos este 6.3 para decidir o que continua aceitável e o que precisa virar prioridade.

---

## 6.3.1 – Débitos técnicos (núcleo Verdade & Interpretação)

### DT1 – Curadoria ainda 100% em arquivos/CLI (ausência de Case Builder)

**Estado atual**  
- Curadores trabalham diretamente em `docs/cases/case_*.yaml` e `collections.yaml` usando editor de texto e scripts CLI.  
- Não existe hoje uma UI que ajude a:  
  - buscar Claims/TruthRecords/Events durante a curadoria;  
  - montar a estrutura do caso com componentes visuais;  
  - validar, em tempo real, referências e coerência interna.

**Por que isso é débito técnico, não só de UX**  
- Erros mecânicos (IDs errados, links quebrados, referências inconsistentes) são tratados como “erro humano”, mas poderiam ser eliminados com tooling.  
- Sem Case Builder, a estrutura de caso e coleção continua pouco "discoverable" para o código: não há camadas intermediárias que imponham invariantes além do YAML.  
- A escalabilidade de curadoria está diretamente amarrada à habilidade de lidar com arquivos/texto, o que é uma **limitação técnica** da plataforma atual.

**Decisão desta sprint**  
- Priorizar a solidez do modelo conceitual (caso = view da Truth‑DB) e da Case Layer (`app/cases/`), aceitando que a UX de curadoria permaneça artesanal.  
- Não antecipar o desenvolvimento de um Case Builder para não fragmentar o foco entre backend, camada de produto e tooling de editor.

**Consequência controlada**  
- Enquanto o número de curadores e casos canônicos for limitado, o custo adicional é gerenciável.  
- A equipe está consciente de que qualquer aumento na escala de curadoria sem Case Builder terá custo quadrático em tempo e atrito.

**Desdobramentos recomendados**  
- S23–S25:  
  - Especificar e implementar um **Case Builder mínimo** (web) com:  
    - busca de Claims/TruthRecords;  
    - seleção de evidências;  
    - montagem de seções/timeline;  
    - geração/edição de `case_*.yaml` por trás.  
- Fase 2:  
  - Evoluir para um **Console de Curadoria** completo, integrado com ingestão, Truth‑DB, Debunker e Sistema de Blocos, incluindo estados de workflow (rascunho, em revisão, publicado, congelado, etc.).

---

### DT2 – Suíte de testes da Case Layer abaixo da criticidade real que ela tem

**Estado atual**  
- Existem scripts (`sXX_cases_check`) que pegam boa parte de problemas estruturais em casos/coleções.  
- Há testes indiretos via cenários end‑to‑end, mas não uma suíte robusta focada apenas em `app/cases/` (domínio, resolver, schemas, erro controlado).

**Por que é débito relevante**  
- A Case Layer é o **boundary oficial de produto** para casos/coleções. Qualquer bug aqui vaza direto para A/B.  
- Riscos críticos mapeados em 6.2 (RT1, RD1, RD2, RD3) passam por esse boundary.  
- Sem suíte forte, refactors na Truth‑DB, nos comitês ou na própria Case Layer ficam perigosos demais, travando evolução.

**Decisão desta sprint**  
- Investir mais em scripts e cenários concretos de demo/piloto do que em uma suíte de testes estruturada, por limite de escopo.  
- Depender mais de "testes por uso real" nesta fase de validação do modelo.

**Consequência controlada**  
- A entrega desta sprint é aceitável como v0/v1 de produto, mas **não é aceitável como base de longo prazo** sem a armadura de testes.  
- Qualquer mudança profunda em Truth‑DB ou `app/cases/` exigirá esforço manual reforçado de QA.

**Desdobramentos recomendados**  
- S23–S25:  
  - Criar uma **suíte de testes dedicada à Case Layer**, incluindo:  
    - casos simples, medianos e extremos;  
    - validação da timeline;  
    - tratamento de estados de incerteza/disputa;  
    - respostas de erro previsíveis e estáveis.  
- Fase 2:  
  - Garantir que features de Fase 2 (Sistema de Blocos, reputação, contestação) que tocam casos venham com **testes de contrato** associados.

---

### DT3 – Observabilidade de casos/coleções acoplada ao backend genérico

**Estado atual**  
- Logs e métricas existem, mas são genéricos (view de backend, não de Case Layer).  
- Não há, ainda, dashboards ou alertas desenhados especificamente para `/api/cases*` e `/api/collections*`.

**Por que é débito**  
- Casos e coleções são a "face pública" da Truth‑DB. Problemas nessa camada são imediatamente percebidos por usuários, mas hoje pouco visíveis para o time.  
- Sem métricas dedicadas (latência, erro, volume, payload), é difícil separar problemas de produto de problemas de infraestrutura.

**Decisão desta sprint**  
- Validar o modelo de casos/coleções usando instrumentação básica, sem construir um stack de observabilidade sob medida.  
- Prototipar primeiro a experiência; observar depois com mais granularidade.

**Consequência controlada**  
- Em pilotos limitados, o time consegue acompanhar manualmente incidentes.  
- Em qualquer cenário de crescimento de uso, esse débito se transforma rapidamente em risco operacional (ver 6.2 RT2).

**Desdobramentos recomendados**  
- S23–S25:  
  - Adicionar métricas de: latência (p95/p99), taxa de erro, tamanho de payload, número de eventos por caso, número de casos por coleção.  
  - Criar ao menos um painel focado na Case Layer, separado do resto do backend.  
- Fase 2:  
  - Correlacionar métricas de uso/performance de casos com métricas de produto (engajamento, temas quentes) para orientar decisões de curadoria e UX.

---

### DT4 – Checks de limites/extremos ainda não sistemáticos

**Estado atual**  
- `sXX_cases_check` foca em integridade estrutural (IDs válidos, referências, formatos, presença de campos obrigatórios).  
- Não há ainda uma bateria formal de "casos extremos" (mega‑casos, coleções com muitos casos, timelines hiper densas) rodando como parte dos gates.

**Por que isso é débito técnico sério**  
- A camada de produto tem comportamento qualitativamente diferente em extremos: performance, usabilidade e até integridade de renderização mudam.  
- Sem exercitar esses extremos, gates podem gerar falsos verdes, como já mapeado em 6.2 (RT3).

**Decisão desta sprint**  
- Aceitar que os casos desta fase de validação seriam moderados, com complexidade controlada.  
- Não investir em construir cenários artificiais extremos dentro desta sprint.

**Consequência controlada**  
- O sistema é relativamente seguro para o conjunto atual de casos.  
- A qualquer movimento de expandir portfólio de forma agressiva, esse débito precisa ser eliminado.

**Desdobramentos recomendados**  
- S23–S25:  
  - Criar um **kit de casos e coleções extremos** (stress pack) e integrá‑lo em `sXX_cases_check`/`sXX_cases_metrics`.  
- Fase 2:  
  - Transformar limites (por exemplo, número máximo de eventos por caso) em parâmetros explicitamente configuráveis, testados e documentados.

---

## 6.3.2 – Débitos de produto e UX (Camada de Casos/Coletâneas)

### DP1 – Ferramentas de curadoria muito aquém da ambição do sistema

**Estado atual**  
- Curadores operam em modo "power user": editor de texto, terminal, scripts, leitura de logs.  
- Não existe:  
  - visão em painel de estados de casos (rascunho, publicado, em revisão);  
  - filtro por tema, sensibilidade, criticidade;  
  - visualização integrada de “fila de trabalho” do curador.

**Por que isso é mais do que um incômodo**  
- Sem tooling, a curadoria vira gargalo político e operacional (ver 6.2 RO1).  
- O custo cognitivo torna difícil abrir curadoria para mais pessoas (internas ou comunidade futura).  
- A ausência de fluxos claros dificulta também a governança (quem mexeu em quê, com qual objetivo).

**Decisão desta sprint**  
- Assumir um modo de operação "oficina artesanal" como ponte para a fase seguinte;  
- concentrar a energia em provar o modelo de caso/coleção e o valor para A/B.

**Desdobramentos recomendados**  
- S23–S25:  
  - Consolidação de um **mini‑console de curadoria**: listagem de casos, filtros, flags de “precisa revisão”, links rápidos para edição.  
- Fase 2:  
  - Evoluir esse console para um **Hub de Curadoria** com workflows, permissões, reputação e integração com feedback/contestação.

---

### DP2 – Visualizações ainda lineares para histórias multidimensionais

**Estado atual**  
- Casos usam timelines e seções organizadas, mas ainda em formato predominantemente textual e linear.  
- Não há views dedicadas a:  
  - conflitos entre fontes;  
  - caminhos alternativos de narrativa;  
  - relações entre entidades ao longo do tempo.

**Por que é débito de produto**  
- Em casos simples, essa visualização é suficiente. Em casos complexos, ela mascara a estrutura do conflito.  
- Deixa de aproveitar o potencial pedagógico do Inspectah de explicar **como** a verdade foi construída (não apenas “qual é o estado atual”).

**Decisão desta sprint**  
- Manter uma visualização simples para acelerar entrega e validação de modelo.  
- Registrar desde já a necessidade de views avançadas como parte da Fase 2.

**Desdobramentos recomendados**  
- S23–S25:  
  - Incrementos de baixo custo: destaques visuais para eventos‑chave, segmentação mínima da timeline, resumos "o que importa" em cada caso.  
- Fase 2:  
  - Visualizações ricas: timelines segmentadas, gráficos de disputa, mapa de entidades e narrativas, views específicas para “guerra longa”.

---

### DP3 – Métricas de produto em formato "planilha JSON" (sem painéis vivos)

**Estado atual**  
- Scripts geram métricas importantes (número de casos, cobertura por coleções, estados de truth, distância até evidência), mas:  
  - ficam em arquivos locais;  
  - demandam leitura manual;  
  - não produzem séries temporais de fácil leitura.

**Por que é um débito de produto/priorização**  
- Limita a capacidade de enxergar trends (crescimento por tema, evolução da cobertura, impacto de mudanças de curadoria).  
- Reduz a participação de pessoas não técnicas na leitura de saúde de produto.  
- Dificulta a priorização baseada em dados em vez de intuição.

**Decisão desta sprint**  
- Tratar essas métricas como "primeira foto" da camada de produto;  
- postergar a integração com observabilidade e painéis.

**Desdobramentos recomendados**  
- S23–S25:  
  - Integrar métricas ao stack de observabilidade e criar pelo menos um **painel de patrimônio de casos** (quantos, quais temas, estados).  
- Fase 2:  
  - Usar essas métricas como insumo para modelos de reputação e participação da comunidade (quais casos atraem mais contestação, por exemplo).

---

### DP4 – Onboarding mínimo para usuário final (A/B)

**Estado atual**  
- A UI pressupõe que o usuário entende intuitivamente:  
  - o que é um Caso Inspectah;  
  - o que significa um estado de truth;  
  - como ler uma timeline de disputa.  
- Não há walkthroughs, tooltips ricos ou exemplos guiados na própria interface.

**Por que isso é débito real**  
- Eleva o atrito para novos usuários e limita o alcance do sistema;  
- obriga o time a apoiar onboarding com materiais externos (docs, vídeos, talks);  
- reduz o impacto pedagógico do Inspectah, que poderia ensinar a ler verdade de forma mais responsável.

**Decisão desta sprint**  
- Focar na estrutura de casos/coleções e na prova de valor para pilotos controlados;  
- deixar onboarding in‑product para ciclos posteriores.

**Desdobramentos recomendados**  
- S23–S25:  
  - Introduzir tooltips e pequenos blocos "como ler este caso";  
  - criar 1–2 casos marcados como "exemplos didáticos" com maior cuidado de explicação.  
- Fase 2:  
  - Desenvolver trilhas guiadas e experiências interativas de onboarding (ex.: "primeiro contato com o Inspectah").

---

## 6.3.3 – Débitos de governança e processo

### DG1 – Modelo de governança para casos sensíveis ainda incompleto

**Estado atual**  
- Existe intuição de que certos temas (política, crises sanitárias, conflitos, temas identitários) exigem mais cuidado.  
- Não há, porém, um fluxo formalizado de:  
  - quem aprova um caso sensível;  
  - quem pode alterá‑lo;  
  - quando escalar para uma instância de governança maior.

**Por que é débito de governança sério**  
- Em temas sensíveis, a pergunta "quem decidiu isso e com base em quê?" vai aparecer.  
- Sem processo, fica difícil responder de forma clara e auditável.  
- Curadores podem se autocensurar ou evitar temas difíceis por medo de errar sozinho.

**Decisão desta sprint**  
- Não travar o avanço de Casos Inspectah esperando um conselho de governança perfeito;  
- resolver casos sensíveis com bom senso do squad, registrando o que for possível em commits e docs.

**Desdobramentos recomendados**  
- S23–S25:  
  - Classificar casos por nível de sensibilidade (baixa, média, alta);  
  - Exigir revisões adicionais para casos de alta sensibilidade;  
  - Registrar decisões-chave com justificativa mínima ligada ao caso.  
- Fase 2:  
  - Integrar esse modelo a reputação, Sistema de Blocos e contestação pública – de modo que decisões sobre casos sensíveis sejam visíveis, explicáveis e auditáveis.

---

### DG2 – Ausência de um processo formal de revisão periódica de casos

**Estado atual**  
- Revisões são acionadas por eventos pontuais (nova evidência muito forte, tema voltando à pauta, percepção informal de drift).  
- Não existe ainda um calendário ou SLA de revisão por tema/idade/criticialidade.

**Por que isso é débito de processo**  
- Sem revisão programada, casos antigos podem ficar defasados sem ninguém notar (ver RD1 em 6.2).  
- Isso acumula "dívida de verdade" no catálogo, difícil de limpar depois.  
- Complica a afirmação de que o Inspectah mantém seus casos “em dia”.

**Decisão desta sprint**  
- Focar em construir catálogo inicial de casos canônicos e na camada de produto mínima;  
- aceitar, provisoriamente, a ausência de um ritual formal de revisão.

**Desdobramentos recomendados**  
- S23–S25:  
  - Definir ciclos de revisão por tema/idade/risco, com metas (ex.: N casos revisados por sprint);  
  - Integrar métricas de drift e idade de caso à seleção de prioridades;  
  - Registrar revisões como eventos de processo vinculados ao caso.  
- Fase 2:  
  - Ancorar revisões relevantes no Sistema de Blocos, criando trilha imutável de evolução de casos.

---

### DG3 – Canais de feedback/contestação ainda em modo "offline"

**Estado atual**  
- Usuários não têm, na UI, um caminho para contestar ou sugerir correções em casos;  
- feedback chega por canais paralelos (e‑mail, redes sociais, conversas privadas).

**Por que é um débito estratégico**  
- Dificulta capturar erros ou lacunas em escala;  
- reduz a sensação de transparência e abertura;  
- prepara mal o terreno para uma fase em que contestação e participação pública são centrais.

**Decisão desta sprint**  
- Não introduzir ainda fluxos de feedback/contestação, para não aumentar demais a superfície de UX e governança numa sprint já densa.

**Desdobramentos recomendados**  
- S23–S25:  
  - Adicionar um mecanismo mínimo de feedback por caso (form simples, issue interna);  
  - Integrar esse fluxo ao Debunker e à curadoria com triagem básica.  
- Fase 2:  
  - Evoluir para fluxos formais de contestação com regras claras, reputação e possível visibilidade pública controlada.

---

## 6.3.4 – Síntese: como tratar estes débitos no planejamento

O Squad Verdade & Interpretação propõe que este 6.3 v2 seja usado de forma operacional, não apenas como registro histórico:

1. **Antes de cada sprint relevante (S23–S25)**, revisar DT*, DP*, DG* e decidir:  
   - quais débitos permanecem aceitáveis;  
   - quais precisam ser reduzidos ou quitados;  
   - quais só fazem sentido serem atacados junto com peças da Fase 2.

2. **Em discussões de GO/NO‑GO**, usar o 6.3 como checklist:  
   - a sprint aumentou, reduziu ou deixou igual a exposição a esses débitos?  
   - algum débito passou do ponto de aceitável para "risco crítico"?

3. **No desenho da Fase 2**, tratar estes débitos como **insumo principal**:  
   - Sistema de Blocos, reputação, comunidade e contestação só fazem sentido se ajudarem a resolver justamente os pontos de fragilidade mapeados aqui.

Este capítulo fecha o triângulo 6.1–6.2–6.3:

- 6.1 diz o que aprendemos e validamos;
- 6.2 mostra onde podemos quebrar e como mitigar;
- 6.3 assume, sem vergonha, o que ainda não construímos – e transforma isso em mapa de investimento para o próximo ciclo do Inspectah.

