# Inspectah — Sprint 30 — Capítulo 6 — Bloco 1
## Propósito do Capítulo 6 e Estrutura Geral de Tasks da Sprint 30

O Capítulo 6 existe para fazer a ponte final entre **especificação** e **execução diária** da Sprint 30.

Se os Capítulos 1–5 respondem:
- o que precisa se tornar verdade (objetivos, escopo, riscos);
- como vamos provar que é verdade (gates, métricas, ORR);
- onde isso mora no código e na arquitetura (filemap, módulos, rotas, UI);
- quem é dono, quais decisões viram contrato e como a S30 se encaixa no Épico E28;

então o Capítulo 6 responde a pergunta que dói no calendário:

> “Quais são exatamente as tasks que precisamos executar, em que ordem e com que relação direta com os gates e evidências da sprint?”

O Bloco 1 faz três coisas:
1. Define o papel do Capítulo 6 dentro da S30;
2. Explica como organizamos as tasks por eixos de trabalho;
3. Crava um mapa mental simples para o squad acompanhar a execução sem se perder.

---

## 6.1 Mandato do Capítulo 6

O Capítulo 6 deve ser tratado como **fonte única da verdade** sobre:
- quais tasks compõem a Sprint 30;
- como elas se agrupam por eixo (backend, console, observabilidade, governança);
- quais são críticas para GO e quais vão direto para backlog pós‑sprint.

Mandato explícito:
- eliminar “tasks fantasmas” (trabalho que acontece mas não está escrito em lugar nenhum);
- evitar que gates e evidências virem “exigência surpresa” perto do fim da sprint;
- permitir que qualquer pessoa, abrindo apenas este capítulo, consiga entender **o que ainda falta** para a S30 ser GO.

O Capítulo 6 não reabre discussão de escopo: ele traduz o que já foi decidido nos Capítulos 1–5 em tarefas concretas.

---

## 6.2 Organização das Tasks por Eixo

Para não virar uma lista amorfa, as tasks da S30 são organizadas em quatro eixos, que refletem a anatomia da sprint:

1. **Fundação e Domínio de Fluxos (Eixo F)**  
   Tudo que diz respeito ao **modelo de fluxos v1.5**, migrations, serviço de domínio, engine de execução e política de roteamento.

2. **Console de Fluxos (Eixo C)**  
   Tudo que diz respeito ao **cockpit de operação**: APIs do console, schemas, frontend e UX mínima para operar fluxos.

3. **Observabilidade, E2E, Gates e CI (Eixo O/G)**  
   Tudo que garante que o fluxo‑pivô de notícias não é uma caixa‑preta: instrumentação, métricas, logs, cenários E2E, scripts de gate, scorecards, bundle e workflow de CI.

4. **Governança, ORR e Backlog (Eixo Gv)**  
   Tudo que amarra a sprint no nível de produto: consolidação de docs, ritual de ORR, decisão GO/NO‑GO e material de continuidade para S31–S35.

Cada task definida nos próximos blocos é rotulada com seu eixo (F, C, O/G, Gv) para facilitar:
- distribuição entre membros do squad;
- paralelização segura (o que depende de quê);
- leitura rápida do que está travando um gate específico.

---

## 6.3 Vista de 10.000 pés das Tasks da S30

Antes de entrar no detalhamento task a task, é útil ter uma visão macro do que a Sprint 30 promete entregar em termos de execução:

- **Eixo F (Fundação de Fluxos)**
  - consolidar modelos v1.5 e migrations;
  - configurar template canônico do fluxo de notícias;
  - implementar serviço de fluxos, roteamento e engine de execução.

- **Eixo C (Console de Fluxos)**
  - expor operações de fluxo via API;
  - construir telas, componentes e hooks do Console de Fluxos;
  - garantir testes básicos de UI e integração.

- **Eixo O/G (Observabilidade & Gates)**
  - instrumentar execuções com métricas e logs estruturados;
  - preparar dataset de notícias sintéticas e script E2E;
  - implementar scripts G0–G5, métricas summary, bundle e CI.

- **Eixo Gv (Governança & Continuidade)**
  - consolidar docs da sprint, incluindo Cap. 5 e este Cap. 6;
  - conduzir ORR com base em scorecards e evidências;
  - registrar backlog imediato para S31–S35.

Esses quatro blocos de trabalho não são independentes, mas se conversam via gates:
- sem Eixo F, não existe fluxo real para operar (G1, G3, G5 caem);
- sem Eixo C, não existe cockpit de operação (G2, G5 caem);
- sem Eixo O/G, não existe prova de que nada funciona (G4, G5 e ORR caem);
- sem Eixo Gv, a sprint até pode “rodar”, mas não entra ordenada na história do E28.

---

## 6.4 Como ler os próximos blocos

Os próximos blocos do Capítulo 6 descem o nível:

- **Bloco 2** — detalha as tasks de fundação (Eixo F) e as tasks de Console (Eixo C);
- **Bloco 3** — detalha as tasks de observabilidade, E2E, gates, bundle e CI (Eixo O/G);
- **Bloco 4** — detalha as tasks de governança, ORR, backlog (Eixo Gv) e apresenta um checklist final de GO.

Cada task vem com:
- descrição clara;
- arquivos/módulos principais envolvidos;
- dependências entre tasks;
- relação explícita com gates e evidências.

Com isso, o Bloco 1 do Capítulo 6 entrega o mapa mental da execução: a partir daqui, é só seguir os blocos seguintes como se fossem instruções de montagem de kit — sem espaço para trabalho fantasma ou “fiz, mas não estava escrito em lugar nenhum”.

