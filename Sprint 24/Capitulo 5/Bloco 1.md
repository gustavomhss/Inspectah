# 5.1 – Contexto & Problemas a Resolver (Produto & Experiência) – v2

Este 5.1 é o **enquadramento de produto** do arco S21–S25 visto pelo Squad Verdade & Interpretação (Pearl, Stonebraker, Norvig, Percy + resto da equipe): ele responde, com máxima precisão, três perguntas:

1. Para **quem** estamos construindo esta camada de Verdade & Interpretação nesta fase?
2. **Que problemas concretos** dessas pessoas esta sprint tem obrigação de atacar?
3. **Onde termina o alcance** desta sprint do ponto de vista de produto/experiência?

Nada aqui é uma lista genérica de “benefícios”. É um mapa de dores, restrições e compromissos que vai guiar os subcapítulos 5.2, 5.3 e 5.4.

---

## 5.1.1 – Ponto de partida: o que já existe antes do Cap. 5

Do ponto de vista interno, o arco S21–S25 (mais os Caps. 1–4) já colocou em pé:

- **Fontes & Ingestão 2.0**  
  `Source`, `IngestionConfig`, `IngestionRun`, `IngestionItemRaw`, `IngestionItemNormalized` funcionando para um subconjunto de fontes reais (RSS de notícias, dados abertos, etc.).

- **Cérebro v1 (Claims)**  
  `InterpretationUnit`, `ClassificationResult`, `Claim` extraindo afirmações estruturadas a partir de itens normalizados.

- **Comitês & Debunker v0**  
  `CommitteeEvaluation`, `CommitteeDecision`, `DebunkIssue`, `DebunkTask` representando como o sistema avalia, revisa e contesta claims.

- **Truth‑DB v1**  
  `TruthRecord`, `TruthChangeEvent` implementando uma máquina de estados explícita para o status de verdade (CANDIDATE, FACT, CONTESTED, REJECTED, etc.).

- **Execução & Observabilidade**  
  Gates G0–G8, scripts em `bin/`, scorecards em `out/scorecards/`, evidências em `out/evidence/`, filemap explícito em 4.3 e runbook de execução em 4.4.

Do ponto de vista de “motor de verdade”, o Inspectah já tem ossos, músculos e exames de sangue. O que **não** existe ainda, de forma minimamente digna, é a pele que aparece para o mundo:

- não existe uma unidade de produto clara chamada **“Caso Inspectah”** ligada canonicamente à Truth‑DB;
- não existe uma **página/endpoint único de caso** onde um humano veja a história inteira de uma afirmação ou conjunto de afirmações;
- não existem **coleções de casos por tema** que alguém possa navegar como “vitrine de verdade”;
- não há **gates, métricas e DoD de produto/experiência** que controlem essa camada.

O 5.1 começa explicitando **essas lacunas** do ponto de vista das pessoas que tentam usar o sistema.

---

## 5.1.2 – Personas prioritárias e seus "jobs to be done"

O Squad Verdade & Interpretação escolhe, para esta fase, **três personas prioritárias**, cada uma com “jobs” muito específicos.

### Persona A – Analista / Jornalista de verificação

**Contexto:** trabalha em redações, núcleos de fact‑checking, organizações de pesquisa. Recebe, todo dia, um fluxo de declarações, manchetes, entrevistas, posts e relatórios.

**Job principal que a sprint precisa suportar:**
> Dado uma afirmação concreta (texto, citação ou trecho de matéria), conseguir **em poucos passos**:
> 1. localizar a(s) claim(s) correspondente(s) no Inspectah;
> 2. ver que evidências existem a favor/contra;
> 3. entender qual é o estado atual de truth e por que ele está assim.

Em termos de ações:
- buscar por frase, ID de claim ou entidade (pessoa, órgão, índice);
- abrir uma **página única de caso** que responda: “quem disse o quê, com base em quê, quem julgou, qual é o estado atual e como ele evoluiu?”;
- conseguir acessar, em 1–2 cliques, as evidências primárias (dados, documentos, fontes originais) que sustentam aquele estado.

### Persona B – Cidadão curioso / público geral

**Contexto:** não entende (nem quer entender) o modelo de dados do Inspectah. Chega por tema (“inflação”, “vacinação”, “desmatamento”, “violência”) e quer separar mito de realidade.

**Job principal:**
> Explorar **casos organizados por tema**, ver rapidamente o que é FACT, o que é CONTESTED e o que está aberto, sem precisar ler um paper técnico.

Em termos de ações:
- abrir uma coleção temática (ex.: “Economia hoje”, “Dados oficiais vs discurso político”);
- dentro dela, ver uma lista de **Casos Inspectah**, cada um com título, resumo e estado geral de verdade (“a narrativa X é amplamente falsa / parcialmente verdadeira / contestada”);
- opcionalmente, clicar para aprofundar em evidências e timeline, mas com uma visão padrão legível em uma ou duas telas.

### Persona C – Editor / Curador interno do Inspectah

**Contexto:** conhece o modelo de dados, mas tem cabeça de produto/narrativa. Precisa montar vitrines, dossiês, “mostras” do que o Inspectah consegue fazer hoje.

**Job principal:**
> A partir da Truth‑DB e das layers de ingerção/claims/comitê/debunker, **selecionar, estruturar e publicar Casos Inspectah** coerentes e auditáveis.

Em termos de ações:
- descobrir casos interessantes via queries sobre Truth‑DB, Claims, entidades, temas e tipos de conflito;
- agrupar esses elementos em uma unidade formal de produto: o **Caso Inspectah**, com metadados editoriais (título, resumo, tags, links de contexto);
- organizar casos em coleções temáticas e exportá‑los como material de demo, documentação ou conteúdo (páginas, PDFs, bundles de casos).

Esses três conjuntos de “jobs” são o eixo rígido do Cap. 5: tudo que vier em 5.2–5.4 deve, direta ou indiretamente, ajudar uma dessas personas a completar esses jobs **com menos atrito e mais clareza**.

---

## 5.1.3 – Dores estruturais hoje (sem Cap. 5)

Se a sprint parasse no Cap. 4, o mundo visto por essas personas seria algo assim:

### Para a Persona A (analista/jornalista)

- A verdade está **fragmentada em muitas camadas técnicas**: Source → IngestionItemNormalized → InterpretationUnit → Claim → CommitteeEvaluation/Decision → TruthRecord/TruthChangeEvent.
- Não existe “página de caso”; existe uma **colcha de retalhos** de consultas, endpoints e, no máximo, alguns painéis tecnicamente orientados.
- Reconstruir uma história exige:
  - saber navegar em múltiplas tabelas/entidades;
  - entender formato interno de Claim, TruthRecord, eventos;
  - aceitar um grau alto de trabalho manual (e potencial de erro humano).

Resultado: o Inspectah é **plausível como motor** e **quase inútil como ferramenta de trabalho** para essa persona.

### Para a Persona B (cidadão curioso)

- Na prática, o produto **não existe**: não há coleções de casos, nem telas simples que expliquem “sobre este tema, o que é fato e o que é lorota?”.
- Qualquer tentativa de mostrar valor exige um evangelista interno fazendo malabarismo entre consoles, bancos e scripts para montar uma história.

Resultado: a camada Verdade & Interpretação vira **infraestrutura invisível**, sem ponte para pessoas fora da equipe.

### Para a Persona C (curador/editor)

- O curador não tem um lugar canônico para **registrar casos e coleções**:
  - monta dossiês em slides, documentos e planilhas desconectadas da Truth‑DB;
  - usa scripts ad‑hoc e consultas manuais para extrair material;
  - perde auditabilidade: o que está em um PDF ou slide não é reconstituível automaticamente a partir do sistema.

Resultado: a narrativa do Inspectah é **paralela ao sistema**, não um produto nativo do próprio sistema.

Pearl, Stonebraker, Norvig e Percy convergem em um diagnóstico simples:
> Sem Cap. 5, Verdade & Interpretação é um ótimo back‑end para ninguém.

---

## 5.1.4 – Problemas concretos que a sprint se compromete a atacar

O 5.1 não serve para listar “tudo que seria legal um dia”, mas para **fechar um conjunto finito de problemas** que serão tratados agora. A equipe converte o diagnóstico acima em um conjunto de problemas P1–P5:

### P1 – Ausência de uma unidade de produto "Caso Inspectah"

Hoje:
- “caso” é uma ideia na cabeça das pessoas, não uma entidade com ID, estrutura e lugar próprio.

A sprint precisa:
- definir o que é um **Caso Inspectah** para este arco (campos mínimos, relação com Claims/TruthRecords, metadados editoriais);
- garantir que cada caso:
  - é reconstituível a partir da Truth‑DB (sem colar manual);
  - tem um identificador estável;
  - pode ser referenciado por UI, APIs e documentação.

### P2 – Falta de "página única" de caso para a Persona A

Hoje:
- não existe uma visão consolidada que responda: “qual é a situação desta afirmação (ou conjunto delas) no Inspectah?”

A sprint precisa:
- definir e implementar um **mínimo de página/endpoint único de caso** (mesmo que rústico), que inclua:
  - texto ou resumo da afirmação/narrativa;
  - claims atômicas relevantes;
  - evidências principais;
  - decisões de comitê e issues de debunker relevantes;
  - estado atual da truth + timeline sintetizada.

### P3 – Inexistência de coleções temáticas mínimas para a Persona B

Hoje:
- não há forma de navegar casos por tema; qualquer “vitrine” é improvisada.

A sprint precisa:
- selecionar um **conjunto pequeno de temas prioritários** (por exemplo: economia, dados oficiais vs discurso político, contestação tardia);
- para cada tema, montar **2–3 Casos Inspectah canônicos**, completamente ligados à Truth‑DB;
- definir como essas coleções são representadas (config, docs, UI, endpoints) de forma rastreável e versionada.

### P4 – Curadoria interna sem ferramentas mínimas (Persona C)

Hoje:
- o curador depende de SQL, scripts soltos e edição manual para construir qualquer narrativa.

A sprint precisa:
- estabelecer caminhos oficiais para o curador:
  - queries e filtros suportados para descobrir casos/candidatos a caso;
  - formato para registrar metadados editoriais de casos (ex.: arquivos YAML/JSON ou docs estruturados);
  - mecanismo para definir **coleções de casos** que o cockpit e as demos vão usar.

### P5 – Ausência total de métricas de produto/experiência

Hoje:
- a sprint mede apenas saúde técnica (gates, latências, cobertura de ingestão, etc.).

A sprint precisa:
- definir poucos, mas claros, **indicadores de sucesso de produto** nesta fase, por exemplo:
  - nº de Casos Inspectah canônicos completos (por tema);
  - nº de casos com timeline de truth legível (sem buracos de estados);
  - “distância de navegação” (em cliques/ações) entre claim e suas evidências;
  - presença de pelo menos uma página/endpoint único de caso por tema prioritário.

Esses problemas serão convertidos, em 5.2, em **gates de produto/UX** e, em 5.3 e 5.4, em decisões arquiteturais e runbooks de demo/evidência.

---

## 5.1.5 – Restrições e não‑objetivos deste ciclo (limites de sanidade)

Para evitar delírio de escopo, o 5.1 fixa alguns **não‑objetivos explícitos** da sprint na camada de produto:

1. **UI definitiva e visualizações avançadas**  
   Não é objetivo desta sprint entregar um cockpit completo, polido e final. Visualizações ricas (grafos dinâmicos, timelines interativas avançadas, filtros sofisticados) são material de sprints futuras.

2. **Abertura massiva ao público final**  
   O foco agora é um **produto interno/early adopters**, com capacidade de demo. Autenticação granular, perfis sofisticados, hardening completo de escala e abuso ficam fora deste ciclo.

3. **Camada avançada de reputação e comunidade**  
   Scores de reputação visíveis ao público, gamificação, mecanismos complexos de contestação pública, integração on‑chain da camada de reputação: tudo isso é Fase 2 do Sistema de Blocos.

4. **Storytelling editorial completo**  
   A sprint cria a unidade de Caso Inspectah e coleções mínimas, mas **não** entrega um sistema completo de narrativa editorial (longforms, análises opinativas complexas). O foco é clareza factual e ligação forte com a Truth‑DB.

5. **Cobertura ampla de todos os temas possíveis**  
   Esta fase trabalha com um **conjunto enxuto de temas e casos**, escolhidos para cobrir bem o arco ingestão → claims → comitês → truth, não para cobrir toda a realidade.

Essas restrições são insumos diretos para 5.2 (gates de produto) e 5.3 (filemap de UI/casos): qualquer proposta que viole essas bordas entra como “seed” para Fase 2, não como escopo desta sprint.

---

## 5.1.6 – Requisitos não‑negociáveis de produto nesta sprint

A equipe também estabelece alguns **invariantes de produto** que não podem ser quebrados, mesmo em versão mínima:

1. **Nenhum Caso Inspectah sem lastro na Truth‑DB**  
   - Toda narrativa/caso apresentado deve ter mapeamento claro para Claims, Evidence, CommitteeDecision e TruthRecord.
   - Não é permitido criar “casos bonitos de demo” que não batem com o estado real do sistema.

2. **Caminho curto da narrativa para a evidência**  
   - Da visão de caso, deve existir um caminho explícito (links, IDs, ações) até as evidências primárias.
   - Não pode haver “resumo mágico” sem mostrar onde estão os dados reais.

3. **Timeline de truth sem buracos estruturais**  
   - Para cada caso canônico, a timeline de truth exibida não pode violar as invariantes definidas em Cap. 3/4 (por exemplo, múltiplos FACT ativos ao mesmo tempo sem justificativa).

4. **Casos e coleções versionados no repositório**  
   - Casos e coleções precisam viver em lugar explícito do repo (como será definido no 5.3), versionados junto com o código, não em documentos paralelos.

5. **Demo reprodutível**  
   - Toda demo oficial de sprint precisa ser reproduzível a partir de scripts/runbooks e dados descritos, não dependente de “setup manual secreto” numa máquina de alguém.

Esses invariantes funcionam como “Design by Contract” de produto: se algum atalho os violar, o ganho de curto prazo em demo é pago com dívida de credibilidade.

---

## 5.1.7 – Entregáveis conceituais deste subcapítulo

Ao final, o 5.1 entrega para os próximos subcapítulos:

- **Um mapa preciso de personas e jobs** (A, B, C) que esta sprint precisa atender.
- **Uma lista de problemas P1–P5** que serão tratados agora, não “um dia”.
- **Bordas de sanidade** (não‑objetivos) que impedem a sprint de tentar virar produto final em um ciclo só.
- **Invariantes de produto** que amarram Cap. 5 à espinha dorsal técnico‑conceitual dos Caps. 3 e 4.

Com esse enquadramento, 5.2 pode transformar P1–P5 em gates e métricas de produto/UX, 5.3 pode desenhar a arquitetura física de UI/casos e 5.4 pode escrever o runbook de demos e evidências de valor, tudo com a mesma disciplina que já usamos para o motor interno do Inspectah.

