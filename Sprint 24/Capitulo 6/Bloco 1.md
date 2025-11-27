# 6.1 – Lições Aprendidas (Verdade & Interpretação / Casos Inspectah) – v2 extremo

Este 6.1 v2 extremo é a versão destilada, mais honesta e mais útil das lições aprendidas na trilha **Verdade & Interpretação**, com foco na camada de **Casos Inspectah + Coleções + Produto** construída no Cap. 5.

Ele foi retrabalhado pelo Squad Verdade & Interpretação completo para servir como:

- memória técnica e de produto da sprint;  
- mapa dos acertos que viram **fundação**;  
- autópsia das dores que viram **gargalo**;  
- checklist mental para qualquer decisão futura que mexa na Truth‑DB, Case Layer ou Casos Inspectah.

---

## 6.1.1 – O que funcionou de verdade (acertos estruturais)

Aqui não entra “coisa que pareceu legal em demo”. Só o que se mostrou sólido quando encostou em código, dados e personas.

### (1) Caso Inspectah como view estruturada da Truth‑DB (e não como banco paralelo)

**Decisão**  
Modelar o **Caso Inspectah** como uma *view estruturada* sobre as entidades de verdade já existentes:

- Claims e entidades interpretadas (`app/brain/`);  
- TruthRecords e TruthChangeEvents (`app/truthdb/`);  
- decisões de comitê (`app/committees/`);  
- issues/tarefas do Debunker (`app/debunker/`);  
- evidências (fontes primárias, datasets, documentos).

O YAML de caso (`docs/cases/case_*.yaml`) não copia fatos: ele referencia entidades e organiza a narrativa.

**Na prática**  
- Não existe “verdade do caso” diferente da verdade da Truth‑DB.  
- O curador pensa em termos de *quais entidades entram no palco*, não em “colar prints”.  
- Qualquer auditoria pode ir de um card da UI até o registro bruto sem atalhos obscuros.

**Lição**  
Essa escolha é **fundacional** e se comprovou correta. Casos devem continuar sendo views estruturadas sobre Truth‑DB, não mini‑bancos de dados paralelos.

### (2) Case Layer em `app/cases/` como boundary oficial de produto

**Decisão**  
Criar uma **Case Layer** explícita em `app/cases/`, com papel de traduzir Truth‑DB + comitês + debunker em APIs de produto:

- `domain.py` – modelos de `CaseDefinition`, `ResolvedCase`, `CaseCollectionDefinition`, etc.;  
- `repository.py` – leitura de `docs/cases/` e `collections.yaml`;  
- `resolver.py` – reconciliação de definitions com Truth‑DB/Claims/Comitês/Debunker;  
- `schemas.py` – contratos de API para UI e integrações;  
- `routes.py` – `GET /api/cases*` e `GET /api/collections*` como superfícies oficiais.

**Na prática**  
- O frontend não fala com Truth‑DB, fala com `app/cases/`.  
- Scripts e ferramentas internas que precisam de “casos” usam a mesma camada.  
- Quando a Truth‑DB mudar, existe um único lugar óbvio para absorver essa mudança.

**Lição**  
Boundary importa. `app/cases/` precisa continuar sendo a porta oficial para tudo que for “caso” ou “coleção”, inclusive para evitar explosão de variações improvisadas.

### (3) Cockpit mínimo, mas desenhado para Personas A e B (não para o diagrama)

**Decisão**  
Focar a UI em quatro rotas simples:

- `/cases` – lista de Casos Inspectah;  
- `/cases/:caseId` – visão detalhada de um caso (Persona A);  
- `/collections` – lista de coleções temáticas (Persona B);  
- `/collections/:collectionId` – visão de uma coleção + seus casos.

Todas as telas foram desenhadas pensando diretamente nas perguntas de A e B, não no “organograma do backend”.

**Na prática**  
- Persona A consegue ir de uma narrativa específica a um caso, ver o estado de truth e abrir evidência primária em poucos passos.  
- Persona B consegue navegar por temas (“economia”, “dados oficiais vs discurso”, etc.) e ver “onde o Inspectah está” em relação a determinados assuntos.  
- O time percebeu que **não precisa de 40 telas** para tornar a verdade consultável – precisa das telas certas.

**Lição**  
Começar pequeno, mas orientado a personas, funcionou melhor do que tentar cobrir tudo. O cockpit mínimo mostrou valor e serviu de laboratório para entender dores reais.

### (4) Scripts e evidências de produto como 1ª classe (não só código “bonito”)

**Decisão**  
Tratar a camada de produto com a mesma disciplina das outras camadas:

- scripts de checagem/métricas/demos em `bin/` (`sXX_cases_check`, `sXX_cases_metrics`, `sXX_cases_demo`);  
- evidências versionadas em `out/evidence/SXX_product_cases/`, `SXX_product_collections/`, `SXX_cases_check/`, `SXX_product_metrics/`;  
- uso desses artefatos em ORR/GO, não só em apresentações.

**Na prática**  
- Qualquer pessoa consegue reproduzir checks e métricas de produto com comandos claros.  
- O estado da camada de casos/coleções no fim da sprint não é “o que está rodando na máquina de alguém”, é o que está em `out/`.  
- “Produto” entrou na malha de evidências do projeto, não ficou como teatro.

**Lição**  
Esse padrão precisa continuar: qualquer coisa que seja “experiência de verdade” no Inspectah precisa ser roteirizável via scripts e comprovável via artefatos.

### (5) Gates de produto (GP0–GP4) como critério real de entrega

**Decisão**  
Definir gates GP0–GP4 (enquadramento, casos, página de caso, coleções, curadoria+métricas) e usá‑los como parte da decisão de GO/NO‑GO da sprint.

**Na prática**  
- O squad não podia dizer que “entregou Verdade & Interpretação” se não houvesse casos canônicos, coleções reais, página de caso funcional e um fluxo mínimo de curadoria.  
- Métricas de produto passaram a aparecer na conversa de ORR, ao lado de tempos de resposta e integridade de pipelines.

**Lição**  
Essa foi a primeira sprint onde “produto” foi avaliado com o mesmo rigor de “backend”. É um padrão que precisa ser mantido e endurecido nas próximas sprints.

---

## 6.1.2 – Onde doeu (fricções e limites reais)

Aqui entra tudo aquilo que funcionou “só com o time carregando nas costas” ou que mostrou claramente onde estão os próximos gargalos.

### (1) Curadoria é poderosa, mas artesanal e cara

**O que aconteceu**  
Para cada Caso Inspectah canônico, o caminho típico foi:

1. Vasculhar Claims, TruthRecords e eventos para entender o cenário.  
2. Escolher o que entra no palco e o que fica nos bastidores.  
3. Montar manualmente `case_*.yaml` com claims, evidências, refs de comitê/debunker, recorte de timeline.  
4. Garantir que `collections.yaml` referencia esse caso corretamente.

**Problema**  
- Processo intensivo em tempo e conhecimento;  
- Alto risco de erro humano em referências (IDs, links, etc.);  
- Baixa escalabilidade: poucos curadores conseguem fazer isso com qualidade.

**Efeito colateral**  
- A velocidade de criação/atualização de casos canônicos é limitada;  
- Casos tendem a envelhecer se ninguém olhar para eles após mudanças na Truth‑DB;  
- O projeto depende demais de “heróis curadores”.

**Lição**  
O modelo conceitual de caso é bom, mas o fluxo de trabalho precisa mudar. A sprint mostrou que, sem ferramentas de apoio (Case Builder, agentes de curadoria, automação de reconciliação), a camada de casos será gargalo estrutural.

### (2) Timeline de truth funciona para histórias simples, falha em guerras longas

**O que aconteceu**  
A timeline de caso foi desenhada para mostrar um arco claro: afirmação → avaliações → decisões → estado atual.

Funciona bem quando:
- existem poucos eventos realmente relevantes;  
- a disputa é relativamente curta;  
- há um caminho principal de “verdade se consolidando”.

Ela começa a sofrer quando:
- a história envolve muitas mudanças de estado em sequência;  
- múltiplos atores/órgãos entram e saem do debate;  
- o caso se arrasta por meses/anos com várias ondas de contestação.

**Problema**  
- A tela fica densa e difícil de ler;  
- o usuário não distingue facilmente “eventos críticos” de “ruído de fundo”;  
- camadas de narrativa diferentes (discurso político, relatório técnico, imprensa, comunidade) se misturam.

**Lição**  
A timeline atual é um bom MVP, mas não é o modelo final para conflitos complexos. Visualização de verdade é um problema de primeira classe, não um detalhe cosmético.

### (3) Métricas de produto são boas como primeira foto, ruins como filme

**O que aconteceu**  
A sprint introduziu métricas como:

- número de casos canônicos;  
- cobertura de casos em coleções;  
- distribuição de estados de truth em casos;  
- distância em cliques até evidência principal para Persona A.

**Valor**  
- Ajudou a tirar o discurso de "tem uns casos aí" e colocar números na mesa;  
- Forçou o time a pensar em mínimos aceitáveis (ex.: cobertura de casos em coleções = 1.0);  
- Deu insumos para ORR além de “tá bonito, confia”.

**Limite**  
- Métricas ainda lidas via arquivos JSON isolados;  
- sem série temporal estruturada (dá trabalho comparar sprints);  
- não medem percepção subjetiva (clareza, confiança) nem custo de curadoria em horas.

**Lição**  
Essas métricas são o primeiro andar, não o prédio. Precisam entrar na stack de observabilidade e evoluir para descrever a “saúde do patrimônio de casos” no tempo.

### (4) Casos canônicos ainda não nascem do fluxo de ingestão

**O que aconteceu**  
Os casos escolhidos para esta sprint foram, em boa parte, selecionados manualmente pelo time: “isso é um bom exemplo pedagógico de como o sistema funciona”.

**Problema**  
- Falta um canal automático onde o fluxo de ingestão diga: “aqui tem fumaça o suficiente para virar caso”;  
- sem isso, há risco de o conjunto de casos ficar mis‑alinhado com o que o mundo está discutindo com mais intensidade.

**Lição**  
O elo ingestão → candidatos a caso precisa ser formalizado em sprints futuras, usando sinais como: volume de menções, conflitos de fonte, divergência entre discurso e dado oficial, etc.

### (5) Produto ainda é monástico: verdade forte, debate fraco na superfície

**O que aconteceu**  
Por escolha de escopo, a sprint não tocou em:

- reputação de fontes/atores/curadores;  
- mecanismos de contestação pública estruturada;  
- ancoragem on‑chain ou Sistema de Blocos completo.

**Resultado**  
- A camada de verdade é robusta internamente (comitês, debunker, Truth‑DB), mas o usuário vê pouco do conflito e da contestação;  
- Casos parecem “respostas oficiais” mais do que “janela para uma disputa de narrativas bem auditada”;  
- Não há ainda sinais de imutabilidade fortes expostos no front.

**Lição**  
Foi correto adiar isso para manter sanidade. Mas o produto só vai mostrar todo o potencial de Verdade & Interpretação quando reputação, contestação e âncoras fortes entrarem no palco.

---

## 6.1.3 – Síntese operacional: o que este 6.1 crava para o futuro

O squad condensa as lições desta sprint em quatro linhas mestras:

1. **Fundação válida**  
   Truth‑DB + Case Layer + `docs/cases/` + cockpit mínimo formam uma base sólida. Não há evidência de que o modelo conceitual esteja “torto”. O problema agora não é mais “o que é um caso”, é “como povoar, manter e mostrar casos em escala”.

2. **Curadoria e visualização são os próximos chefes de fase**  
   O motor de verdade funciona. A partir daqui, as maiores dificuldades estarão em:
   - criar e manter casos com menos atrito e mais automação;  
   - representar conflitos longos e complexos de forma compreensível.

3. **Produto é parte do sistema de verdade, não adereço**  
   Casos e coleções não são marketing; são a maneira oficial de expor “o que o Inspectah sabe”. Eles precisam continuar debaixo dos mesmos gates, métricas e evidências que o resto do sistema.

4. **Fase 2 precisa atacar exatamente as dores mapeadas aqui**  
   Reputação, contestação, Sistema de Blocos e on‑chain não podem ser enfeite. Eles precisam ser desenhados para aliviar:
   - a dependência de curadores heróis;  
   - a dificuldade de visualizar disputas complexas;  
   - a distância entre “verdade calculada internamente” e “debate público visível”.

Este 6.1 v2 extremo é, portanto, o quadro na parede da sala do Squad Verdade & Interpretação: sempre que alguém sugerir “um atalho esperto”, é aqui que a gente volta para lembrar o que o sistema já ensinou na prática.

