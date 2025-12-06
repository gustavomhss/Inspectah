# Sprint 33 — Capítulo 6 — State of the Art

## 6.1 Visão geral: por que a S33 é uma sprint de operação de nova geração

A Sprint 33 não é "apenas mais uma" sprint de features. Ela é a sprint em que o Inspectah dá o primeiro passo sério rumo a uma **camada de operação de nova geração**, desenhada não só para manter serviços de pé, mas para **cuidar da qualidade da verdade** que o sistema produz.

No contexto do projeto, a S33 entrega o OracleOps v1 como um conjunto coeso de:

- modelos de domínio (Incident, componentes, SLOs);
- serviços de operação (health summary, SLO evaluator, API de cockpit);
- cockpit de operação (feature `oracleops` no frontend);
- processos de operação (runbooks, bundles, ORR operacional);
- governança de sprint (gates, scorecards, evidências).

O conjunto não é apenas funcional — ele é deliberadamente alinhado ao estado da arte em SRE, observabilidade e gestão de incidentes, e ao mesmo tempo projetado para operar um tipo de sistema que quase não existe no mercado: uma **plataforma de verdade auditável**.

Este capítulo sintetiza o que torna a S33 uma sprint "state of the art" e estabelece as referências, critérios e anti‑padrões que devem guiar tanto a sua implementação quanto a evolução futura do OracleOps.

---

## 6.2 Ponto de partida: padrões de referência que inspiram a S33

Para qualquer arquitetura se declarar "state of the art" sem cair em buzzword, precisa ser capaz de apontar claramente **de onde está partindo**. A S33 é explicitamente inspirada e tensionada por:

- o corpus de **Site Reliability Engineering (SRE)**: SLOs, error budgets, gestão sistemática de risco, incidentes e postmortems;
- a **observabilidade moderna**: métricas, logs, traces e eventos tratados como primeira classe, com ênfase em explorabilidade e correlação;
- práticas de **gestão de incidentes** consolidadas: fluxos de abertura/encerramento, severidades, roles (incident commander, scribe, etc.), aprendizado estruturado;
- o padrão de **cockpits e control planes** de plataformas complexas (Kubernetes, orquestradores de dados, sistemas de mensageria);
- a visão de **governança por gates**: readiness checks formais, scorecards, evidências e ORRs como norma, não exceção.

O diferencial é que tudo isso é trazido para um contexto em que:

- a principal "mercadoria" do sistema não é throughput de requests, mas **credibilidade**;
- a principal catástrofe não é apenas downtime, mas **degradação silenciosa da verdade** exposta.

A S33 assume esse risco como central e desenha o OracleOps v1 já com essa lente.

---

## 6.3 Ponto de chegada: como a S33 redefine o que é operar um sistema

Na prática, a S33 propõe uma definição ampliada de "operar" o Inspectah:

> Operar não é só garantir que serviços respondam; é garantir que a cadeia de ingestão → interpretação → contestação → Truth‑DB → exposição se mantenha íntegra, atual, auditável e observável.

Isso implica:

- dar semântica aos componentes de operação (são degraus da jornada da informação, não apenas serviços anônimos);
- permitir que incidentes sejam definidos tanto por falhas técnicas quanto por falhas na cadeia de verdade (atrasos de recência, falta de evidência, contestação não tratada);
- enxergar SLOs como guardas não apenas de latência e uptime, mas de **recência e integridade informacional**;
- transformar o cockpit em um lugar onde uma pessoa consegue entender, em minutos, **como está a saúde da verdade** naquele recorte.

O OracleOps v1, como projetado na S33, é o primeiro artefato concreto dessa definição.

---

## 6.4 Critérios de excelência: como saber se a S33 está à altura do que promete

Para ser "state of the art", a S33 não pode depender de impressões subjetivas. Ela precisa de critérios de excelência claros, que podem ser verificados no código, na UI e nas evidências. Alguns critérios centrais:

1. **Coerência entre domínio, UI e operação**  
   - Componentes, Incident e SLOs são modelados em domínio, aparecem na API e são visíveis no cockpit com a mesma semântica.
   - Não há conceitos "fantasma" na UI que não existam no domínio — nem conceitos de domínio escondidos sem reflexão visual.

2. **Observabilidade a serviço do operador, não da ferramenta**  
   - Métricas, logs e queries de SLO existem para responder a perguntas reais de operação; não para preencher dashboards bonitos.
   - O operador consegue, via cockpit, chegar rapidamente a painéis e evidências relevantes.

3. **Gates, scorecards e evidência como trilha mestra**  
   - O estado da S33 é inferível, de forma honesta, pelo conjunto de scorecards e evidências.
   - Qualquer divergência entre narrativa e artefatos deve ser corrigida a favor dos artefatos.

4. **Runbooks e bundles testados em cenário real/simulado**  
   - Pelo menos um incidente relevante foi percorrido ponta a ponta com runbook e cockpit.
   - O bundle resultante conta a história de forma compreensível para alguém de fora da sprint.

5. **ORR com fricção real, não teatro**  
   - Operador convidado encontra pontos de fricção; isso é esperado e desejado.
   - Esses pontos viram backlog ou ajustes imediatos, não são varridos para baixo do tapete.

Se esses critérios não forem atendidos, a S33 perde o direito de se chamar state of the art — mesmo que tecnicamente "funcione".

---

## 6.5 Anti‑objetivos: o que a S33 explicitamente recusa

Parte do caráter "state of the art" da S33 vem, também, de **coisas que ela escolhe não ser**. Alguns anti‑objetivos importantes:

1. **Cockpit como dashboard de vaidade**  
   A S33 recusa um cockpit cheio de gráficos bonitos, mas que não respondem a nenhuma pergunta concreta de operação.

2. **SLOs como retórica**  
   Não há espaço para SLOs que existem apenas em documentos ou slides. Se um SLO não tem métrica, query e lugar na UI ou em processos de decisão, ele não conta.

3. **Incident como rótulo genérico para qualquer problema**  
   A S33 recusa a ideia de Incident como "campo de texto com status". Incident é entidade com lifecycle, vínculos e invariantes.

4. **Runbooks como wiki abandonada**  
   Runbooks não vivem em lugares obscuros não versionados e não são escritos apenas para cumprir requisito. Eles são tratados como código operacional.

5. **ORR como checklist vazio**  
   A ORR não é um ritual para carimbar GO. Se a sessão não expõe dificuldades, provavelmente foi mal desenhada.

6. **Evidência como pós‑produção**  
   A sprint não aceita a prática de "depois a gente junta as evidências". Evidência é produzida junto com a execução dos gates e cenários.

Esses anti‑objetivos devem ser lembrados sempre que aparecerem atalhos tentadores durante a implementação.

---

## 6.6 Linhas de pesquisa e exploração a partir da S33

Do ponto de vista de pesquisa e inovação, a S33 abre algumas linhas claras para avançar o estado da arte além do mainstream atual:

1. **Chaos engineering orientado à verdade**  
   Introduzir falhas controladas em fontes, pipelines e componentes do Truth‑DB e observar como o OracleOps responde em termos de detecção, priorização e mitigação.

2. **SLOs semânticos de casos e temas**  
   Explorar SLOs que medem:
   - quão rapidamente a Truth‑DB incorpora correções em casos sensíveis;
   - a distância entre o estado de um caso no Inspectah e estados declarados por fontes oficiais;
   - a densidade mínima de evidências para considerar um caso "operacionalmente saudável".

3. **Observabilidade técnico‑epistemológica unificada**  
   Investigar modelos e visualizações que coloquem, lado a lado:
   - a saúde de pipelines e serviços;
   - a saúde de casos, narrativas e blocos de verdade;
   - permitindo ver como problemas técnicos reverberam em confiança epistemológica.

4. **Aprendizado automatizado a partir de bundles de incidentes**  
   Usar os bundles como dataset para sugerir melhorias automáticas de runbooks, detecção precoce de padrões de falha e até recomendações de redesign arquitetural.

5. **Integração com camadas de governança e política de verdade**  
   Conectar sinais de OracleOps (instabilidade, contestação, SLOs estourados) a mecanismos de governança (por exemplo, restringir exposição de certos casos, disparar revisões extraordinárias em comitês).

Estas linhas não precisam ser resolvidas na S33, mas a sprint as reconhece como fronteiras naturais de evolução.

---

## 6.7 North Star: como medir o sucesso do OracleOps nos próximos ciclos

Por fim, um capítulo "state of the art" precisa apontar um **North Star**: um conjunto de métricas ou sinais que indiquem se estamos, ao longo do tempo, nos aproximando da visão desejada.

Alguns indicadores possíveis para sprints futuras, derivados da S33:

1. **Tempo de detecção e resposta a incidentes críticos em fontes/pipelines chave.**
2. **Tempo entre publicação de correção oficial em fontes confiáveis e atualização de casos associados no Inspectah.**
3. **Proporção de incidentes relevantes que foram conduzidos usando runbooks versionados (vs. improviso).**
4. **Qualidade percebida do cockpit por operadores (pesquisas internas, NPS operacional, feedback da ORR).**
5. **Grau de cobertura de SLOs técnico‑epistemológicos em temas/casos estratégicos.**
6. **Correlação entre períodos de degradação operacional e degradação medida da confiabilidade da Truth‑DB.**

Se, ao longo de sprints subsequentes, o OracleOps evolui na direção de:

- reduzir tempos e aumentar a previsibilidade desses indicadores;
- ampliar cobertura de SLOs e recortes operados;
- tornar a operação cada vez mais explicável e auditável;

então a S33 terá cumprido, com folga, seu papel como sprint "state of the art" fundadora da operação do Inspectah.

Este Capítulo 6 cristaliza essa visão e serve de referência tanto para a implementação da própria S33 quanto para a leitura crítica de suas sucessoras.

