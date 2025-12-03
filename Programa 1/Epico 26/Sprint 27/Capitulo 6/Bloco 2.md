# Inspectah — Sprint 27 (S27)
## Capítulo 6 — Bloco 2
### Learnings da S27 por Eixo (Produto/UX, Engenharia, Operação, Processo)

> Arquivo-alvo sugerido no repo: `docs/s27_cap_6_2_learnings_por_eixo.md`
>
> Função: registrar, de forma organizada, **o que a S27 ensinou** em quatro eixos principais — Produto/UX, Engenharia & Qualidade, Operação & Runbooks, Processo & Forma de Trabalhar. Esses learnings devem ser úteis para quem vai mexer em Admin v1, Programa 1, Debunker, consoles e ORRs nas próximas sprints.

---

## 1. Eixo Produto & UX — Admin v1 nos Consoles de Programa 1

### 1.1 O que funcionou bem

1. **AdminShell como estrutura base única**  
   - A adoção do `AdminShell` (e blocos associados como header, sidebar, área de conteúdo) nos consoles de Fontes, Ingestão 2.0 e Debunker reduziu a diversidade caótica de layouts e facilitou a navegação entre módulos.  
   - Ter um esqueleto visual comum tornou mais natural para operadores migrarem de um console para outro sem curva de reaprendizado grande.

2. **Padrões de listas e filtros reaproveitáveis**  
   - Componentes de listas (tabelas, cards) e filtros foram reaproveitados entre Fontes e Ingestão, reduzindo o esforço de UX e código duplicado.  
   - O mesmo padrão de "lista → detalhe" demonstrou ser suficiente para cobrir a maioria das necessidades iniciais de Programa 1.

3. **Feedback visual de estados de fonte e ingestão**  
   - Uso consistente de indicadores de status (cores, ícones, labels) para estados de fonte e de ingestão ajudou operadores a entender rapidamente o panorama do sistema.  
   - O padrão "estado + explicação curta" (ao invés de apenas cor) mostrou-se importante na redução de ambiguidade.

4. **Debunker como UI centrada em casos**  
   - Tratar o Debunker como um "gerenciador de casos" (em vez de uma tela genérica de logs) facilitou a compreensão da jornada de contestação.  
   - Estruturar a tela em torno de caso, evidências e decisão explicitou melhor o papel do Debunker no fluxo de Programa 1.

### 1.2 O que não funcionou tão bem (e o que o time aprendeu)

1. **Sobrecarga de informação em telas de overview**  
   - Tentativas iniciais de colocar "tudo em uma tela" (especialmente em Ingestão) criaram interfaces densas demais, com ruído visual e dificuldade de priorizar.  
   - Learnings: é preferível dividir visão geral em 2–3 painéis focados do que tentar resolver tudo em um único dashboard.

2. **Estados avançados do Debunker pouco claros**  
   - Casos com múltiplas evidências, revisões e loops de decisão tendiam a ficar confusos na UI, mesmo com Admin v1.  
   - Isso indicou que o modelo mental de "timeline de decisões" precisa ser melhor representado na interface, não só em campos soltos.

3. **Relação entre Fontes e Ingestão nem sempre explícita**  
   - Em alguns fluxos, a ligação "esta fonte → estes jobs de ingestão" não estava óbvia na UI, exigindo conhecimento prévio para ser entendida.  
   - Learnings: é essencial mostrar, no mínimo, links bidirecionais (da fonte para ingestões associadas e da ingestão para a fonte de origem).

### 1.3 Princípios de design que emergiram

Da experiência da S27, alguns princípios de UX para consoles admin ficaram mais nítidos:

- **Princípio 1 — Uma shell, múltiplos contextos**  
  Consoles de Programa 1 devem parecer "salas diferentes da mesma casa" — mesma shell, mesmos padrões de navegação, variação apenas no conteúdo.

- **Princípio 2 — Contexto sempre visível**  
  Telas críticas precisam mostrar contexto mínimo essencial (por exemplo: qual programa, qual fonte, qual caso de Debunker) sem exigir cliques adicionais.

- **Princípio 3 — Fluxos antes de features**  
  UX deve ser desenhada a partir de fluxos reais de trabalho (ex.: detectar problema em fonte → ver impacto em ingestão → abrir/consultar caso em Debunker), não a partir de módulos independentes.

Esses princípios deveriam ser explicitados e reaproveitados na evolução do Admin v1 e na criação de Admin v1.x para outros programas.

---

## 2. Eixo Engenharia & Qualidade — Gates, E2E e Contratos

### 2.1 Como os gates se comportaram na prática

1. **G1 (Admin design system) como guard-rail estrutural**  
   - Scripts e checks de G1 ajudaram a manter o Admin v1 coerente (build, imports, estrutura geral), evitando que mudanças pontuais em um console quebrassem o design system.

2. **G2 (fluxos admin E2E) como detector de regressão funcional**  
   - Quando bem definido, G2 se mostrou a primeira linha de defesa contra regressões em fluxos críticos, especialmente ao conectar Fontes, Ingestão e Debunker.  
   - Cenários escritos com clareza (entradas, passos, saídas) tiveram alto valor para o ORR.

3. **G3 (qualidade de front) estabilizando o código dos consoles**  
   - Lint, testes unitários e build focados em `frontend/inspectah-ui` criaram uma rotina mínima de higiene que reduziu incidentes triviais (imports quebrados, código morto, etc.).

4. **G4 (contratos) como radar de inconsistências API ↔ UI**  
   - Testes de contrato em Fontes, Ingestão e Debunker capturaram rapidamente divergências de schemas e formatos que, antes, só seriam descobertas na UI.

### 2.2 Dores e aprendizados nos E2E

1. **Automação de cenários muito genéricos não trouxe valor**  
   - Scripts E2E que tentavam cobrir "tudo" de forma genérica (sem narrativas específicas) acabaram frágeis e difíceis de manter.  
   - Learnings: cenários devem ser poucos e muito concretos, contando uma história clara de uso do sistema.

2. **Dependência forte de dados estáticos atrapalhou**  
   - Cenários E2E que exigiam fixtures muito rígidas dificultaram a evolução dos domínios e das telas.  
   - Melhor abordagem: cenários que constroem seus próprios dados no começo e limpam no final, reduzindo acoplamento com estado global.

### 2.3 Contratos de API sob pressão

1. **Testes de contrato como documentação executável**  
   - Ter testes de contrato para Fontes, Ingestão e Debunker funcionou como uma forma viva de documentação das APIs — muito mais confiável do que docs soltas.  
   - Mudanças de schema ficaram mais explícitas e exigiram decisões conscientes.

2. **Custo de mudança quando contrato é frouxo**  
   - Onde o contrato não estava bem coberto, pequenas mudanças em modelos acabaram gerando efeitos colaterais silenciosos em consoles.  
   - Learnings: há valor em investir cedo em testes de contrato em áreas que alimentam UIs críticas.

---

## 3. Eixo Operação & Runbooks — Programa 1 em modo quase real

### 3.1 O que funcionou bem nas simulações de operação

1. **Runbooks como fio condutor de incidentes simulados**  
   - Em testes de "incidentes" de Programa 1, runbooks de Fontes e Ingestão ajudaram a padronizar passos de diagnóstico (o que checar, em que ordem, quais telas usar).

2. **Guia Admin v1.1 reduzindo onboarding de operadores**  
   - Um guia separado para Admin v1 facilitou explicar, de forma transversal, como os consoles se comportam, sem repetir a mesma introdução em cada runbook.

3. **Clareza mínima de papéis por console**  
   - A S27 forçou o time a explicitar "o que este console faz" e "para quem" — por exemplo, Fontes para quem cuida de cadastros e saúde de fontes, Ingestão para visão operacional de pipelines, Debunker para análise de casos.

### 3.2 Gaps descobertos nas simulações

1. **Fluxos de recuperação parcial pouco documentados**  
   - Quando algo dava errado parcialmente (por exemplo, ingestões falhando apenas para subset de fontes), os runbooks nem sempre tinham caminhos claros de mitigação.  
   - Aprendizado: runbooks não podem focar só em "tudo certo" ou "tudo quebrado"; estados intermediários são comuns.

2. **Dependência de conhecimento tácito em Debunker**  
   - Operar o Debunker ainda exigia saber detalhes não documentados sobre estados de caso, critérios de decisão e relação com outras partes do sistema.  
   - Isso revelou a necessidade de melhorar tanto a UX quanto os próprios runbooks do Debunker.

3. **Ausência de métricas operacionais visíveis na UI**  
   - Operadores sentiram falta de indicadores simples na interface (por exemplo, contagem de casos abertos, ingestões em erro, fontes críticas), tendo que inferir estado a partir de listas.  
   - Learnings: para operação, métricas de alto nível na UI admin são tão importantes quanto listas detalhadas.

---

## 4. Eixo Processo & Forma de Trabalhar — Waves, Gates, ORR

### 4.1 Experiência com waves W0–W3

1. **W0 como preparação indispensável**  
   - Ter uma wave dedicada a sanidade de ambiente, alinhamento de capítulos e visão inicial dos consoles reduziu confusões durante o desenvolvimento.  
   - Learnings: W0 é lugar para matar divergências básicas de visão, não para empurrar código.

2. **W1/W2 como núcleo de entrega funcional**  
   - Organizar a S27 em W1 (núcleo funcional dos consoles e gates básicos) e W2 (refino, contratos, docs) ajudou a escalonar expectativas, evitando a ilusão de que tudo ficaria pronto só na última semana.

3. **W3 como espaço real de hardening e ORR**  
   - Reservar uma wave inteira para hardening, rodada final de gates e ORR impediu que "ajustes de última hora" consumissem tempo crítico da sessão de avaliação.

### 4.2 Uso de Cap.1–Cap.5 como guias vivos

1. **Capítulos como contrato de sprint, não como burocracia**  
   - Onde o time tratou os capítulos (especialmente Cap.2–Cap.4) como referência real, houve menos desalinhamento entre código, testes e expectativas de ORR.  
   - Em alguns momentos, a disciplina de atualizar docs ficou aquém do ideal — isso apareceu em pequenos descompassos no ORR.

2. **Cap.5 como ferramenta de decisão, não pós-fato**  
   - Tratar Cap.5 (ORR) como algo a ser preparado ao longo da sprint, e não apenas na véspera, mostrou-se um diferencial na qualidade da sessão.

### 4.3 ORR da S27 como aprendizado de governança

1. **Scorecards G0–G6 como linguagem comum**  
   - No ORR, scorecards se tornaram uma forma objetiva de discutir o estado da sprint, reduzindo espaço para percepções contraditórias.

2. **Importância de registrar riscos e ações ao vivo**  
   - Preencher `key_risks` e `actions_required` em G6 durante a reunião ajudou a evitar a clássica situação "depois alguém anota", que nunca acontece.

3. **Valor de ter um chair claro para a sessão**  
   - Ter uma pessoa explicitamente responsável por guiar o ORR (chair) fez diferença para manter tempo, foco e clareza de decisão.

---

## 5. Como usar estes learnings na prática

- **Para quem vai evoluir Admin v1**: use os pontos de Produto/UX como checklist de princípios a preservar e problemas a atacar primeiro.  
- **Para quem vai trabalhar em Debunker, ingestão ou novos consoles**: parta dos aprendizados de E2E, contratos e operação para não repetir erros estruturais.  
- **Para quem vai rodar próximas sprints com waves e ORR**: trate as lições de Processo como ajustes do próprio Sprint Playbook, não como curiosidades históricas.

Este Bloco 2 deve ser mantido o mais factual possível, sempre que possível apontando para evidências (scorecards, logs, cenários, runbooks) descritas nos demais capítulos e no bundle da S27.