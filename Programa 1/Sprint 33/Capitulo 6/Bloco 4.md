# Sprint 33 — Capítulo 6

## Bloco 4 — Critérios de excelência, anti‑objetivos e North Star da S33

Este bloco fecha o Capítulo 6 traduzindo o rótulo “state of the art” em três coisas bem concretas:

1. **Critérios de excelência**: como saber, na prática, se a S33 está à altura da ambição.  
2. **Anti‑objetivos explícitos**: o que a S33 se recusa a ser, mesmo sob pressão de prazo.  
3. **North Star operacional**: quais sinais acompanhar ao longo das próximas sprints para saber se o OracleOps está ficando melhor.

A função deste bloco é servir como **checklist de honestidade intelectual**: se o resultado da sprint não bate nesses pontos, o time deve ter a coragem de dizer que ainda não é state of the art.

---

### 6.4.1 Critérios de excelência: quando a S33 pode se dizer “state of the art”

A S33 só merece o rótulo “state of the art” se passar por um conjunto de critérios verificáveis em código, UI e evidências. Entre eles:

1. **Coerência entre domínio, API e cockpit**  
   - Os conceitos centrais de operação (Incident, componentes, SLOs, runbooks) aparecem de forma consistente:  
     - como modelos de domínio;  
     - como recursos expostos em API;  
     - como elementos visíveis e navegáveis no cockpit.  
   - Não existem conceitos operacionais “fantasma” em telas que não estejam presentes no domínio, nem entidades de domínio importantes invisíveis para o operador.

2. **Jornada completa do operador exercitada e registrada**  
   - Pelo menos um cenário relevante foi executado ponta a ponta em ORR:  
     - detecção de problema via cockpit;  
     - entendimento do impacto (componentes, casos, SLOs);  
     - uso de runbook;  
     - encerramento do incidente;  
     - registro em bundle.  
   - O bundle correspondente permite que alguém que não participou da S33 reconstrua o que aconteceu sem lacunas grosseiras.

3. **Gates, scorecards e evidências alinhados com a realidade**  
   - Todos os gates G0–G4 têm scorecards `status = PASS` suportados por evidências concretas (logs, prints, dumps, bundles).  
   - G5 (ORR) existe, com `status` e follow‑ups claros.  
   - Não há divergência entre o que os scorecards dizem e o que o código/UX entregam — se houver, a verdade é corrigida a favor dos scorecards/evidências.

4. **SLOs operacionais realmente em uso**  
   - Existe pelo menos um conjunto de SLOs que:  
     - está definido em doc;  
     - é carregado em domínio;  
     - é avaliado por `ops_slo_evaluator`;  
     - aparece no cockpit;  
     - influenciou alguma decisão na sprint (por exemplo, priorização de correção ou de design).

5. **Runbooks e cockpit considerados úteis por quem opera**  
   - Feedback da ORR e/ou de sessões internas mostra que:  
     - o cockpit facilita encontrar o que importa;  
     - ao menos um runbook foi considerado realmente útil, não apenas decorativo;  
     - as fricções encontradas foram endereçadas ou registradas com prioridade clara.

Se esses critérios não forem atendidos, a S33 pode ter sido produtiva, mas ainda não chegou no nível de excelência que este capítulo descreve.

---

### 6.4.2 Anti‑objetivos: o que a S33 se recusa a ser

Definir o que evitar é tão importante quanto definir o que buscar. A S33 se ancora em alguns **anti‑objetivos explícitos**:

1. **Cockpit de vaidade**  
   - Painéis cheios de gráficos “bonitos” que não ajudam o operador a decidir nada.  
   - Métricas sem pergunta associada.  
   A S33 recusa esse modelo: todo elemento de UI precisa responder a uma pergunta ou suportar uma ação.

2. **SLOs de PowerPoint**  
   - SLOs definidos em slides ou docs, sem SLI, query ou reflexo na UI.  
   - Metas que ninguém consulta para tomar decisão.  
   Na S33, um SLO sem métrica, query e lugar no cockpit é tratado como inexistente.

3. **Incident como rótulo genérico**  
   - Tickets informais chamados de “incidente” sem lifecycle, severidade ou vínculos com componentes/SLOs.  
   A S33 exige Incident como entidade de domínio séria; o resto é ruído.

4. **Runbooks mortos em wiki escondida**  
   - Runbooks fora do repositório, sem versionamento, esquecidos após a escrita.  
   - Passos genéricos do tipo “verifique os logs” sem dizer quais, onde e como interpretar.  
   A sprint recusa esse modelo: runbooks vivem no repo, e pelo menos um foi usado em cenário real/simulado.

5. **ORR de teatro**  
   - Sessão encenada por quem desenvolveu a sprint, sem fricção real, apenas para marcar GO.  
   - Ausência de follow‑ups ou de registros honestos de dificuldades.  
   A S33 considera esse padrão uma falha grave: se a ORR não expõe nada difícil, ela não foi bem desenhada.

6. **Evidência de fachada**  
   - Logs e prints gerados às pressas no fim da sprint apenas para preencher diretórios.  
   - Scorecards ajustados manualmente para PASS sem respaldo em execução real dos scripts.  
   A S33 recusa evidência retro‑fabricada: se não aconteceu de verdade, não entra como PASS.

Esses anti‑objetivos funcionam como alarmes internos: se algum deles começar a aparecer, é sinal de que a sprint está se afastando perigosamente da proposta original.

---

### 6.4.3 Linhas de evolução: como não deixar o OracleOps v1 estagnar

Mesmo que a S33 cumpra todos os critérios de excelência, o OracleOps v1 é, por definição, um ponto de partida. Algumas linhas de evolução naturais, que este bloco registra como orientação para sprints futuras:

1. **Expandir o recorte de operação**  
   - Incluir mais fontes, pipelines, blocos de verdade e APIs no `components_map`.  
   - Incorporar novos tipos de incidentes (por exemplo, ligados a contestação ou a inconsistência de versões de blocos).

2. **Aprofundar SLOs técnico‑epistemológicos**  
   - Passar de SLOs de recência/latência básicos para SLOs que medem tempo de correção de casos, tempo de reação a contestação, estabilidade de narrativas em cenários voláteis.

3. **Refinar UX do cockpit com base em uso real**  
   - Usar feedback de operadores para simplificar fluxos;  
   - destacar componentes/SLOs mais relevantes conforme temas/casos ganham importância.

4. **Aumentar a automação da resposta operacional**  
   - A partir de bundles, identificar padrões que possam ser automatizados (abertura de incidentes, rótulos de incerteza, mitigação temporária).

5. **Conectar operação à governança de verdade**  
   - Usar sinais de OracleOps (instabilidade, SLOs estourados) como gatilhos para revisão de políticas, prioridades de pesquisa e exposição de casos.

Essas linhas não são metas da S33 em si, mas guard rails para não tratar o OracleOps v1 como “produto acabado”.

---

### 6.4.4 North Star: sinais que dizem se o OracleOps está melhorando

Por fim, a S33 define um conjunto de **indicadores de North Star** — não necessariamente implementados nesta sprint, mas úteis para julgar, nos próximos ciclos, se o OracleOps está caminhando na direção certa.

Alguns exemplos de sinais a acompanhar:

1. **Tempo de detecção de incidentes críticos em fontes/pipelines chave**  
   - Quanto tempo leva, em média, para o sistema (mais operador) perceber que algo importante na cadeia de ingestão quebrou.

2. **Tempo de reação a problemas que impactam casos sensíveis**  
   - Tempo entre a degradação de um componente crítico e a mitigação efetiva do impacto sobre casos/cenários de alto risco.

3. **Proporção de incidentes conduzidos com runbooks**  
   - Percentual de incidentes relevantes em que um runbook versionado foi usado como guia principal, em vez de improviso.

4. **Qualidade percebida do cockpit por operadores**  
   - Feedback qualitativo e quantitativo (por exemplo, NPS interno) sobre o quanto o cockpit ajuda a entender a situação e agir.

5. **Cobertura de SLOs em temas estratégicos**  
   - Proporção de temas/casos estratégicos que têm SLOs claros e monitorados, em vez de depender apenas de percepção ad hoc.

6. **Correlação entre saúde operacional e confiabilidade da Truth‑DB**  
   - Em janelas em que OracleOps aponta saúde frágil, é possível observar queda em indicadores de confiabilidade da verdade (atrasos de atualização, aumento de contestação não resolvida, etc.).  
   - A meta de longo prazo é que essa correlação seja bem compreendida e usada para priorização.

Se, ao longo das sprints seguintes, o OracleOps:

- reduz tempos de detecção e reação;
- aumenta a proporção de incidentes guiados por runbooks;
- melhora a experiência de operação medida por operadores;
- amplia a cobertura de SLOs relevantes;

então a S33 terá cumprido não só seu objetivo imediato, mas também seu papel como sprint fundadora de uma operação **realmente alinhada à missão de verdade do Inspectah**.

Este Bloco 4 é, portanto, o contrato de excelência da S33 com o futuro do OracleOps.