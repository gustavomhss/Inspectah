# Inspectah – Sprint 12
## Capítulo 1 — Ingestão Contínua & Comunidade v0 (fase sem blockchain)

## 0. One‑liner oficial e demo mental

Depois da Sprint 12, o Inspectah passa a funcionar assim:

1. O sistema roda 24/7, puxando dados de algumas fontes bem escolhidas.
2. Cada coisa importante que acontece vira um evento ligado a um caso/tema.
3. Todo evento passa por um Debunker v0, que marca como **aceito**, **incerto** ou **suspeito** e explica por quê.
4. Qualquer humano autorizado abre o **Inspectah Explorer v0**, busca um tema, vê a timeline dos eventos, clica nas fontes e, se achar algo estranho, aperta um botão de **“reportar problema”**.

Em cinco minutos de demo, a Sprint 12 precisa permitir que alguém veja isso acontecendo ao vivo, sem precisar abrir terminal, logs ou JSON.

---

## 1. Contexto: de S8–S10 para um serviço sempre ligado

### 1.1. O que já temos até aqui

S8–S9 mostraram que o Inspectah consegue:

- ingerir dados de algumas fontes reais;
- normalizar por tema;
- usar GPT em cima de bundles de evidência para responder perguntas;
- gerar scorecards e evidências para cenários de demonstração.

A Sprint 10 fechou a **Truth‑DB** e o **Guardião de Blocos**:

- modelo estável de blocos, fatos, versões, estados;
- camada mecânica (actions) que define o que pode / must / never pode ser feito na Truth‑DB;
- GPT atuando como guardião: sugere ações, não escreve direto no banco;
- gates e scorecards garantindo que a Truth‑DB é “pasta de verdade” e não “pasta de chute”.

Hoje o Inspectah já é forte em sanidade de decisão, mas ainda parece um laboratório: muitos scripts, muito gate, pouca cara de “serviço que vive no tempo”.

### 1.2. O papel da Sprint 12

A Sprint 12 responde:

> “Como transformar o Inspectah de laboratório em um serviço 24/7, com dados entrando o tempo todo, organizados em casos com timeline e expostos numa interface simples?”

Sem blockchain, sem reputação pesada, sem Sistema de Blocos completo, sem comunidade avançada. Só o necessário para:

- ingerir continuamente em poucos domínios piloto;
- obrigar o Debunker v0 a passar em todas as entradas;
- organizar o resultado em casos/temas com timelines de eventos e estados;
- expor isso num Explorer v0 com um fluxo mínimo de feedback humano.

### 1.3. Handshake explícito com a Sprint 10

A S12 não inventa um modelo novo paralelo. Ela é, literalmente, a projeção “para fora” do que a S10 já criou:

- os eventos normalizados da ingestão se tornam candidatos a fatos/versões na Truth‑DB;
- as decisões do Debunker v0 e do Guardião são materializadas como estados e versões nos mesmos blocos/fatos que a S10 definiu;
- a timeline que o usuário enxerga no Explorer v0 é um recorte navegável do log de eventos + ações da Truth‑DB.

**Regra de ouro da S12:**

> Nenhum evento aparece como “verdade visível” no Explorer v0 sem existir como entidade coerente na Truth‑DB S10.

---

## 2. Equipe de visão imaginária (fixa daqui pra frente)

- **Steve Jobs** – corta gordura, garante que o Explorer v0 é simples, óbvio e demonstrável.
- **Alan Kay** – zela pela clareza das abstrações: caso, evento, timeline como unidades simples e composíveis.
- **Martin Kleppmann** – cuida de logs, ingestão, reprocessamento e consistência 24/7.
- **Donald Knuth** – vigia a precisão das definições (o que é caso, o que é evento, que estados existem).
- **Bertrand Meyer** – garante que as operações têm pré/pós‑condições claras (ingestão, Debunker, exposição).
- **Pavel Durov** – paranoico com operação enxuta: poucos conectores, pouca dependência frágil, fácil de operar sob pressão.
- **Você + DNA/Playbook** – mantêm o alinhamento com capítulos 1–4, gates, scorecards e a nota de escopo (sem blockchain, reputação, sistema de blocos full agora).

---

## 3. Problema de fundo que a Sprint 12 resolve

Sem a S12, o Inspectah sofre de:

1. **Intermitência operacional**  
   Dados entram quando alguém dispara scripts. Não há garantia de frescor, nem de que o sistema “está cuidando do mundo” continuamente.

2. **Debunker parcial ou opcional**  
   Parte dos fluxos passa por checagem rigorosa, parte não. Isso cria zonas cinzentas em que um evento vira fato “meio sem querer”.

3. **Verdade presa na visão de backend**  
   Tudo existe, mas em tabelas, scorecards e logs. Ótimo para dev, péssimo para mostrar para qualquer outro humano.

4. **Ausência de um caminho mínimo de correção humana**  
   Se alguém vê um erro, não há um fluxo simples de “reportar problema, isso aqui está errado ou estranho”.

A Sprint 12 existe para matar esses quatro problemas com o menor conjunto de peças possível.

---

## 4. Visão macro da Sprint 12

### 4.1. Ingestão contínua enxuta

Poucas fontes, muito bem selecionadas, com diferentes cadências:

- quase tempo real (feeds de notícia relevantes para um tema);
- diária (portais de transparência, dados de governo);
- semanal/mensal (relatórios, estatísticas consolidadas).

Um scheduler unificado dispara os conectores no ritmo certo, coloca eventos em filas e garante:

- frescor suficiente para ser útil;
- controle suficiente para não virar loucura operacional;
- idempotência (reprocessar não cria duplicata lógica).

### 4.2. Debunker v0 obrigatório em todas as entradas

Todo evento normalizado passa por Debunker v0 antes de se tornar “fato principal” da Truth‑DB. O Debunker:

- lê o evento;
- considera o histórico do caso;
- atribui um estado: **aceito**, **incerto** ou **suspeito**;
- gera um racional curto (“por que marquei assim”).

**Pré‑condição D1 (ingestão):**  
Nenhum evento entra na fila de normalização sem fonte identificada, timestamp, domínio e payload bruto.

**Pré‑condição D2 (Debunker):**  
Nenhum evento normalizado é elegível para virar fato visível sem: referência a um caso, tipo de evento e extrato textual.

**Pós‑condição D3 (cobertura do Debunker):**  
Todo evento que chega na Truth‑DB como candidato a fato principal possui estado de Debunker ∈ {aceito, incerto, suspeito} **e** explicação registrada.

### 4.3. Casos/temas com timeline

Cada caso/tema é um “filme” sobre algo que o mundo está fazendo. Exemplos:

- “Reforma da escola municipal X em Niterói (contrato 2025‑123)”
- “Furacão Y na região Z em 2025”

**Definição mínima de caso/tema para a S12:**

- `id_caso` estável;
- domínio (ex.: `obra_publica`, `evento_climatico`);
- título humano;
- descrição curta;
- fonte(s) principais envolvidas;
- status geral (derivado dos eventos: dominante entre aceito/incerto/suspeito + regras simples).

**Invariantes de caso:**

- **I1:** todo evento normalizado pertence a exatamente um caso (ou dispara criação atômica de um novo caso).
- **I2:** um caso pertence a um único domínio (não misturar obra pública com clima no mesmo `id_caso`).
- **I3:** a timeline é append‑only; correções aparecem como novos eventos ou novas versões, nunca como edição silenciosa do passado.

### 4.4. Inspectah Explorer v0 (Comunidade v0)

Uma interface mínima, mas real:

- busca por tema/caso por texto livre;
- lista de casos:
  - título;
  - status geral (aceito/incerto/suspeito);
  - última atualização;
- página de caso:
  - resumo;
  - timeline de eventos com ícones de estado;
  - links claros para fontes originais;
  - botão de “reportar problema” no nível de evento ou do caso.

Sem login sofisticado, sem votos, sem reputação, sem discussão aberta. É uma comunidade v0 controlada: poucos usuários, foco em visibilidade e feedback mínimo.

### 4.5. Feedback “reportar problema”

O botão gera um registro estruturado:

- qual caso/evento;
- quem reportou (se houver identidade);
- descrição livre;
- timestamp.

**Pós‑condição F1:**  
Todo feedback gera um item rastreável em uma fila interna, passível de ser marcado como “novo”, “em análise”, “resolvido”, com log das ações tomadas (reprocessar, criar nova versão etc.).

---

## 5. Objetivos da Sprint 12

**Objetivo 1 – Ingestão contínua em dois domínios piloto**  
Pelo menos dois domínios (ex.: obras públicas, eventos climáticos) rodando com:

- múltiplas fontes;
- cadências configuradas;
- ingestão automática ao longo do dia.

**Objetivo 2 – Cobertura total do Debunker v0**  
SLI base: cobertura do Debunker = 1.0 para todos os eventos elegíveis.

- nenhum fato principal aparece na Truth‑DB ou no Explorer v0 sem passar pelo Debunker;
- a proporção de eventos “sem estado do Debunker” deve ser 0.

**Objetivo 3 – Casos/temas com timelines coerentes**  
É possível:

- ver a sequência de eventos de um caso em ordem cronológica;
- entender, lendo só a timeline + racionais, o que vem acontecendo;
- identificar rapidamente eventos marcados como suspeitos.

**Objetivo 4 – Explorer v0 demonstrável**  
Rodar o Inspectah local/dev, abrir um browser e:

- buscar um caso;
- abrir a página;
- ver timeline e fontes;
- apertar “reportar problema”;
- ver o feedback aparecer na fila interna.

**Objetivo 5 – Observabilidade mínima de 24/7**  
Ter métricas e logs suficientes para saber:

- se ingestão está rodando;
- se conectores estão falhando;
- como está distribuída a classificação do Debunker;
- onde estão concentrados os feedbacks da comunidade v0.

---

## 6. Escopo da Sprint 12 (o que entra)

### 6.1. Cadastro de fontes e scheduler unificado

Entra:

- registro de fontes com cadência e parâmetros;
- scheduler central que respeita essas cadências;
- políticas simples de retry e de backoff;
- logs claros por fonte.

Não entra o sonho de “mil conectores plug‑and‑play para qualquer coisa”.

### 6.2. Pipeline de ingestão e normalização

Entra:

- pipeline que transforma payloads brutos em eventos normalizados com campos mínimos bem definidos;
- regra de roteamento evento → caso/tema (por chave sintética, entidades, `id_externo` etc.);
- tratamento de duplicatas lógicas (idempotência).

### 6.3. Debunker v0 em todas as entradas

Entra:

- integração do Debunker v0 como etapa obrigatória;
- registro estruturado do racional;
- métricas básicas (quantos aceitos/incertos/suspeitos por fonte, domínio, dia).

### 6.4. Casos/temas + timeline e status geral

Entra:

- definição e persistência de casos;
- timeline de eventos por caso;
- cálculo simples de status geral do caso (ex.: “predominância dos últimos N eventos + prioridade para suspeitos”).

### 6.5. Inspectah Explorer v0

Entra:

- backend para busca e lista de casos;
- backend e frontend para página do caso;
- botão de “reportar problema” com backend para armazenar feedbacks.

### 6.6. Painel interno de feedbacks

Entra:

- endpoint ou tela mínima que lista feedbacks pendentes;
- capacidade de marcar como “em análise” / “resolvido”;
- log das ações.

---

## 7. Fora de escopo (por decisão de sanidade)

Explicitamente fora da S12:

- Blockchain (contratos, anchors, TruthRegistry, DisputeRegistry).
- Sistema de Blocos completo (blocos/sub‑blocos/componentes formais).
- Reputação (scores de fonte, usuário, feedback).
- Disputa formal com bond, prazos, escalonamento jurídico.
- Comunidade avançada (perfis, followers, ranking, discussões públicas).
- Hardening nível S16 (threat model completo, ataques simulados em massa).

Se aparecer alguma ideia nessa linha, ela vira RFC/ADR para fase 2.

---

## 8. Exemplo concreto de ponta a ponta

**Tema:** “Reforma da escola municipal X”

1. O scheduler puxa diário oficial, portal de transparência e notícias locais.  
2. Conectores normalizam eventos (contrato assinado, ordem de início, relatórios de avanço, denúncia de paralisação).  
3. Cada evento é roteado para o caso “Reforma da escola X” (ou cria o caso na primeira ocorrência).  
4. Debunker v0 avalia cada evento, marca estados, registra racional.  
5. A Truth‑DB atualiza fatos/versões conforme as ações do Guardião + regras da S10.  
6. No Explorer v0, qualquer humano:
   - busca “escola municipal X”;
   - abre o caso;
   - vê timeline com estados;
   - abre fontes originais.
7. Se notar algo errado (ex.: status oficial não bate com realidade local), aperta “reportar problema” e descreve.  
8. Operador vê o feedback, investiga, gera novos eventos/versões se necessário. O caso e a timeline são atualizados.

Nenhum passo exigiu blockchain, reputação complexa ou disputa formal. Só o ciclo mínimo de “mundo → ingestão → Debunker → Truth‑DB → Explorer → feedback → correção”.

---

## 9. Antecipação de gates e SLI/SLO (ponte para o Capítulo 2)

O Capítulo 2 vai transformar essa visão em gates S12‑G0…S12‑G8 com SLIs/SLOs. Mas desde já, a S12 nasce com alguns alvos implícitos:

- **SLI‑1 (frescor):** percentual de eventos das últimas 24h processados até T+X minutos.
- **SLI‑2 (cobertura Debunker):** proporção de eventos elegíveis com estado do Debunker registrado (alvo: 1.0).
- **SLI‑3 (integridade de casos):** proporção de eventos normalizados que estão ligados a um caso válido e aparecem na timeline correta.
- **SLI‑4 (Explorer v0):** taxa de sucesso na navegação básica (buscar caso, abrir página, ver timeline).
- **SLI‑5 (feedback):** todo feedback gerado é persistido e chega em uma fila interna dentro de T+Y minutos.

O Capítulo 2 vai detalhar esses SLIs, definir SLOs (thresholds) e amarrar cada objetivo deste Capítulo 1 a um gate concreto com scorecard e evidências.

---

## 10. Uso deste capítulo

Este Capítulo 1 é o contrato de visão da Sprint 12. Ele responde:

- o que a S12 muda no produto;
- que problemas ela mata;
- o que está dentro e fora da sprint;
- como ela encaixa S10 (Truth‑DB + Guardião) e prepara terreno para a fase 2.

Se alguém conseguir, lendo apenas este texto, explicar a uma terceira pessoa, em 5 minutos:

> “O que é a Sprint 12, o que ela entrega, o que não entrega e como se demonstra o resultado”

então este capítulo atingiu o nível de excelência esperado e está pronto para virar Capítulo 2, 3 e 4.

