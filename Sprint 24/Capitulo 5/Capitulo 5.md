# 5 – Verdade “de fora”: Produto, Narrativas & Experiência – v2

Este Capítulo 5 descreve **como a camada Verdade & Interpretação aparece para o mundo**.

Os Capítulos 1–4 trataram do interior do motor:
- **Cap. 1**: por que esta sprint existe no arco do Inspectah.
- **Cap. 2**: quais contratos de qualidade (gates, métricas, DoD) regem a sprint.
- **Cap. 3**: que anatomia de dados, serviços e integrações dá forma ao sistema.
- **Cap. 4**: como tudo isso é executado, testado e auditado em G0–G8.

O Capítulo 5 assume esse motor como dado e responde:

> Como as verdades, claims, timelines e decisões que o Inspectah produz se transformam em **casos, narrativas e experiências concretas** para pessoas reais?

No Sprint Playbook v2 (6×4), o Cap. 5 também é dividido em quatro subcapítulos fixos:
- **5.1 – Contexto & Problemas a Resolver (Produto & Experiência)**
- **5.2 – Gates, Métricas & Definition of Done (Produto/UX/Narrativas)**
- **5.3 – Arquitetura & Filemap da Camada de Produto & Casos**
- **5.4 – Execução & Evidências (Demos, Casos Reais & Feedback)**

Este texto macro define o terreno, os objetivos e as fronteiras de cada subcapítulo, no contexto específico do arco **S21–S25** e do **Squad Verdade & Interpretação**.

---

## 5.0.1 – Posição do Capítulo 5 no arco S21–S25

O arco S21–S25 constrói a espinha dorsal de verdade do Inspectah:
- **S21** – Console de Fontes: 
  cadastro, configuração e saúde de `Source` e `IngestionConfig`.
- **S22** – Ingestão 2.0: 
  `IngestionRun`, `IngestionItemRaw`, `IngestionItemNormalized` e eventos de ingestão.
- **S23** – Cérebro v1: 
  `InterpretationUnit`, `ClassificationResult`, `Claim`.
- **S24** – Comitês & Debunker v0: 
  `CommitteeEvaluation`, `CommitteeDecision`, `DebunkIssue`, `DebunkTask`.
- **S25** – Governança & Truth‑DB: 
  `TruthRecord`, `TruthChangeEvent` e política de promoção/rebaixamento de verdades.

Os Capítulos 1–4 garantem que essa espinha dorsal **funciona e é auditável**. O Capítulo 5 garante que ela **é acessível, inteligível e útil**.

Para o arco S21–S25, a expectativa mínima do Cap. 5 é:
- expor o resultado do motor Verdade & Interpretação em uma forma de **“casos Inspectah”** (unidades de narrativa que um humano consegue ler e entender);
- oferecer, ainda que de forma inicial, um **cockpit de consulta** a esses casos e timelines de truth;
- produzir um conjunto pequeno, mas sólido, de **casos canônicos** que demonstrem o valor do sistema (economia, dados oficiais vs discurso, contestação tardia, etc.);
- definir critérios objetivos para saber se a experiência dessa sprint é aceitável (gates de produto/UX, métricas e DoD específicas).

Cap. 5, portanto, é o ponto em que o Inspectah deixa de ser apenas “infra de verdade” e vira **produto de verdade**.

---

## 5.0.2 – Personas e usos-alvo desta sprint (lado produto)

Para organizar o Cap. 5, o Squad Verdade & Interpretação foca em um conjunto enxuto de personas e usos **diretamente impactados por S21–S25**.

### Persona A – Analista / Jornalista de Verificação

**Quem é**: profissional que trabalha com notícias, dados e discursos públicos, e precisa checar afirmações de forma recorrente.

**O que quer desta sprint**:
- pesquisar uma afirmação específica (frase, manchete, citação) e ver:
  - quais `Claim` o Inspectah extraiu disso;
  - quais evidências existem (dados, documentos, fontes);
  - quem avaliou (`CommitteeEvaluation`), qual foi a decisão (`CommitteeDecision`);
  - qual é o estado atual na Truth‑DB (`TruthRecord` + `TruthChangeEvent`).

**Dores atuais que o Cap. 5 precisa atacar**:
- dificuldade de navegar entre muitas telas ou APIs para montar o quebra-cabeça;
- falta de visualização clara da linha do tempo de uma claim (quando foi criada, avaliada, contestada, alterada);
- ausência de uma “página única” de caso que conte a história completa.

### Persona B – Cidadão curioso / usuário final

**Quem é**: pessoa interessada em temas específicos (inflação, vacinação, clima, crime, etc.) que não quer aprender o modelo de dados do Inspectah.

**O que quer desta sprint**:
- encontrar **casos organizados por tema**;
- ler um resumo claro: o que foi dito, o que os dados mostram, o que o Inspectah considera FACT ou CONTESTED;
- conseguir clicar, se quiser, para ver evidências e timelines, mas sem ser obrigado a mergulhar em detalhe técnico.

**Dores atuais**:
- excesso de tecnicalidade em ferramentas de fact‑checking e dados;
- dificuldade de entender o que é “parcial”, “contestado” ou “resolvido” sem glossário;
- falta de exemplos concretos que mostrariam por que confiar em um sistema como o Inspectah.

### Persona C – Editor / Curador Interno do Inspectah

**Quem é**: pessoa (ou time) responsável por montar coleções de casos, vitrines temáticas e narrativas para mostrar o valor do sistema.

**O que quer desta sprint**:
- capacidade de selecionar casos (queries sobre Truth‑DB + Claims + Events);
- registrar metadados de narrativa (título, resumo, tags, anotação editorial);
- organizar casos em coleções (por tema, período, tipo de fonte);
- exportar esses casos (como páginas, PDFs, bundles) para uso externo.

**Dores atuais**:
- necessidade de “gambiarras” em planilhas ou ferramentas externas para organizar casos;
- dificuldade de sincronizar anotações editoriais com o estado real da Truth‑DB;
- ausência de lugar canônico no repo para “casos e narrativas”.

O Capítulo 5 será construído em torno dessas personas: cada subcapítulo 5.1–5.4 vai explicitar o que a sprint entrega para elas e como.

---

## 5.0.3 – O que o Cap. 5 abrange e o que fica fora desta fase

**Dentro do escopo desta fase (S21–S25)**:
- Definição de **“Caso Inspectah”** como unidade de produto:
  - conjunto estruturado: contexto, claims centrais, evidências principais, decisões de comitê, estado atual de truth, timeline resumida;
  - representação mínima em UI/endpoint/documento.
- First cut de **cockpit de consulta de casos e claims**, mesmo que ainda minimalista:
  - pode ser uma UI web simples, endpoints de API, ou um conjunto de páginas estáticas geradas a partir da Truth‑DB;
  - o importante é haver um caminho único e estável para chegar de uma afirmação à sua timeline de truth.
- Conjunto de **casos canônicos** que demonstrem a espinha dorsal Verdade & Interpretação funcionando ponta a ponta:
  - casos de notícia econômica;
  - casos de “dados oficiais vs discurso político”;
  - casos de contestação tardia (FACT que vira CONTESTED/REJECTED).
- Definição de **gates e métricas de produto/experiência** alinhados ao Cap. 2 e Cap. 4, mas focados em:
  - legibilidade de timelines;
  - navegabilidade de casos;
  - cobertura mínima de temas/casos;
  - distância entre a persona e a evidência.

**Explicitamente fora de escopo nesta fase (Fase 2 e além)**:
- UI definitiva e sofisticada (dashboards interativos avançados, visualizações complexas de grafos de claims/fatos);
- componentes de reputação pública de fontes e agentes (scores avançados, gamificação, reputação on‑chain);
- mecanismos complexos de acesso público massivo (alto tráfego, autenticação granular, multi‑idioma completo);
- marketplace de narrativas, colaboração em massa, comentários públicos, etc.

Cap. 5 se concentra em um **Mínimo Produto de Verdade**: poucas coisas, muito bem feitas, que mostrem a espinha dorsal S21–S25 em ação de forma clara e convincente.

---

## 5.0.4 – Papel de cada subcapítulo 5.x no Sprint Playbook v2

### 5.1 – Contexto & Problemas a Resolver (Produto & Experiência)

O 5.1 é a “cabeça” de produto do capítulo:
- traduz o arco S21–S25 para linguagem de caso, narrativa e experiência de usuário;
- lista dores concretas das personas A, B e C que esta sprint pretende atacar;
- define o **recorte de produto** da sprint: 
  por exemplo, “expor 3–5 casos canônicos com timelines completas, acessíveis via cockpit mínimo e endpoints, com clareza sobre estado de truth e evidências”.

Sem um 5.1 forte, o Cap. 5 vira uma coleção de telas soltas ou endpoints isolados, sem narrativa de produto.

### 5.2 – Gates, Métricas & DoD (Produto/UX/Narrativas)

O 5.2 define os contratos de sucesso do ponto de vista de produto/experiência:
- “gates de produto” (análogo aos G0–G8, mas na camada de experiência), por exemplo:
  - gate de **Legibilidade de Timeline**: persona A consegue entender a história de uma claim em N passos;
  - gate de **Casos Canônicos**: pelo menos N casos do tipo X/Y/Z estão completos e acessíveis;
  - gate de **Navegação**: persona B chega da página inicial a um caso relevante em até M cliques/ações;
- métricas de produto/UX:
  - tempo médio de resposta de consultas de caso;
  - número de casos canônicos, por tema;
  - “distância” média em cliques entre claim e evidência;
- Definition of Done de produto:
  - endpoints e/ou telas existem, são documentados, têm exemplos concretos (casos reais da sprint);
  - as personas definidas em 5.0.2 conseguiriam, em tese, completar tarefas descritas.

### 5.3 – Arquitetura & Filemap da Camada de Produto & Casos

O 5.3 é o mapa físico da parte “de fora” do Inspectah:
- estrutura de **frontend/UI** (por exemplo, `frontend/inspectah-ui/`, rotas, componentes);
- representação de **casos e coleções** no repo (por exemplo, `docs/cases/`, YAML/JSON de configuração, templates);
- contratos de API e integração com a Truth‑DB (endpoints que alimentam o cockpit e casos);
- relação entre esses artefatos e o filemap técnico do Cap. 3/4 (como a UI conversa com `app/truthdb/`, `app/claims/`, etc.).

O objetivo é que alguém que queira mexer na camada de produto saiba **onde mexer** e **como isso encaixa com o resto do sistema**.

### 5.4 – Execução & Evidências (Demos, Casos Reais & Feedback)

O 5.4 descreve como a sprint prova, na prática, que a camada de produto funciona:
- runbook de **demos oficiais** da sprint (sequência de casos a serem apresentados, telas/endpoints, o que observar);
- como gerar e armazenar **evidências de produto**:
  - capturas de tela, gravações, scripts de demo;
  - outputs exportados (páginas HTML estáticas, PDFs, bundles de casos);
- como registrar e aproveitar **feedback de usuários/pessoas reais** (se houver inícios de teste) para alimentar o Cap. 6.

Enquanto o 4.4 é o manual de execução técnica, o 5.4 é o manual de demonstração e validação de valor.

---

## 5.0.5 – Interface entre Cap. 4 e Cap. 5

O Cap. 5 não reimplementa o que Cap. 4 já resolve; ele se apoia diretamente nas garantias de execução:

- **Entrada do Cap. 5**:
  - Truth‑DB operando de forma coerente (G5 do Cap. 4);
  - comitês e debunker produzindo decisões e issues rastreáveis (G4);
  - pipelines de ingestão e cérebro estáveis para o recorte de fontes desta sprint (G2–G3);
  - evidências técnicas registradas em `out/evidence/`.

- **Saída do Cap. 5**:
  - Casos Inspectah estruturados (em UI, docs, APIs);
  - Cockpit mínimo de consulta por claim/caso/tema;
  - Demos oficiais e artefatos de narrativa (capturas, bundles de casos);
  - Métricas e gates de produto que alimentam a decisão de GO/NO‑GO no Cap. 2/4.

Dito de outra forma: **Cap. 4 prova que o sistema funciona; Cap. 5 prova que alguém consegue usar isso para aprender algo verdadeiro sobre o mundo.**

---

## 5.0.6 – Resultado esperado do Capítulo 5 nesta sprint

Ao final desta sprint, considerando o escopo de produto definido para S21–S25, o Cap. 5 deve ter produzido:

1. **Um recorte claro de produto** para Verdade & Interpretação nesta fase:
   - quais tipos de casos serão suportados (ex.: economia, dados oficiais vs discurso, contestação tardia);
   - quais personas são priorizadas e que tarefas elas conseguem realizar.

2. **Um conjunto mínimo de casos canônicos prontos**:
   - cada caso com página/endpoint/representação clara;
   - timelines legíveis;
   - ligações diretas para claims, evidências e decisões.

3. **Gates de produto/UX definidos e testáveis**, com métricas associadas.

4. **Arquitetura e filemap de produto explícitos**, sem “UI mágica” ou casos soltos fora do repo.

5. **Runbook de demo e evidências de valor** (demos gravadas, capturas, exemplos exportados) suficientes para:
   - convencer alguém de fora de que a espinha dorsal S21–S25 faz algo compreensível e útil;
   - alimentar futuras sprints focadas em UI completa, reputação, colaboração e Fase 2 do Sistema de Blocos.

Esse é o norte do Capítulo 5: 

> garantir que, ao olhar para o Inspectah nesta sprint, não vemos só um motor perfeito de verdade – vemos **casos concretos e narrativas legíveis** que mostram, sem esforço heroico, o que é verdade, o que é contestado e o que ainda está em aberto.