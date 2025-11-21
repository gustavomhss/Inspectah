# Inspectah — Sprint 15  
## Capítulo 1 — Visão de Inteligência & Blindagem do Sistema de Blocos

### 0. One‑liner oficial da sprint

> A Sprint 15 transforma o Sistema de Blocos em um guardião cético e resistente a canetadas: Debunker v1 operando em linha, comitês V1/V2/V3 para decisões críticas e âncoras mínimas em blockchain para provar que a história não foi reescrita.

---

### 1. Posição da Sprint 15 no roadmap do Sistema de Blocos

Contexto de alto nível (Fase 2 – Sistema de Blocos):

- **S13 – Truth‑DB Core v1**  
  Modelo de dados e eventos do Sistema de Blocos (core blocks, fatos, versões, claims), log append‑only, leitura consistente no tempo (snapshots atuais e históricos), invariantes básicos de integridade e ausência de qualquer `force_set_state`.

- **S14 – Disputas & Write Path completo**  
  Contestação bottom‑up (claims → versões → fatos → blocos), fluxo de resolução de disputas, propagação das decisões para o estado atual e APIs para abrir/acompanhar disputas.

Ao final da S14, o Sistema de Blocos **já consegue**:

- registrar blocos, fatos e versões com histórico completo;
- receber claims e abrir disputas sobre pontos específicos;
- atualizar o estado de fatos/blocos de forma rastreável, a partir da resolução de disputas.

Mas ainda existe um problema central: **muito poder concentrado em poucas decisões** (um Guardião principal, um único fluxo de validação, pouca redundância cognitiva) e **pouca blindagem contra influência externa silenciosa**.

A **Sprint 15** entra exatamente aqui para adicionar três camadas novas, em cima do que S13–S14 já entregaram:

1. **Debunker v1 em produção** (cérebro cético dedicado a descobrir buracos e inconsistências em claims de alto risco).  
2. **Comitês V1/V2/V3** (pipeline triplo de validação, que combina checagens mecânicas, múltiplos cérebros de IA e coerência global).  
3. **Âncoras mínimas em blockchain + anti‑canetada operacional** (registro externo da história e proibição explícita de atalhos que ignorem disputas e logs).

A S15 não recria o Sistema de Blocos; ela **sobe uma camada de inteligência e blindagem** em cima do core e das disputas já modeladas.

---

### 2. Problema central que a Sprint 15 resolve

Sem a S15, o Sistema de Blocos, mesmo com disputas, ainda sofre com quatro vulnerabilidades importantes:

1. **Quem vigia o Guardião?**  
   Um único modelo (ou um conjunto muito restrito) acaba decidindo resultados de disputas e mudanças de estado. Se ele errar, o Sistema de Blocos erra junto.

2. **Falta de redundância cognitiva em decisões críticas**  
   Decisões sobre disputas importantes podem ser tomadas por uma única passagem de IA + uma checagem mecânica básica. Não há comitê estruturado que coloque múltiplos cérebros em desacordo e force uma explicação melhor.

3. **Risco de canetada silenciosa**  
   Mesmo sem um `force_set_state` exposto, a ausência de um protocolo explícito de “override legal” abre espaço para pressões externas que não deixam rastro formal. Na prática, isso é equivalente a permitir uma canetada escondida.

4. **Dificuldade de provar, para terceiros, que a história não foi reescrita**  
   O log é append‑only dentro do sistema, mas ainda não existe uma âncora externa forte (blockchain) que permita mostrar, de fora, que determinados eventos e versões já existiam em uma data X e não foram alterados.

A Sprint 15 ataca essas vulnerabilidades com um conjunto coordenado de mudanças:

- Debunker v1 como **agente cético institucionalizado**;
- comitês V1/V2/V3 como **pipeline de aprovação triplo** para decisões sensíveis;
- módulo de âncoras em blockchain e “anti‑canetada” como **contrato operacional** do sistema.

---

### 3. Objetivos da Sprint 15

#### 3.1 Objetivo macro

Transformar o Sistema de Blocos em um **sistema de verdade cético, redundante e rastreável**, capaz de:

- desconfiar automaticamente de claims de alto risco;
- submeter decisões importantes a múltiplos validadores independentes;
- resistir a tentativas de override fora do fluxo normal;
- demonstrar para terceiros que a história não foi reescrita, via âncoras externas.

#### 3.2 Objetivos específicos

1. **Debunker v1 operacional em linha**  
   - Selecionar claims de alto risco com base em regras configuráveis (impacto, tema, divergência entre fontes, contestação prévia etc.).  
   - Buscar evidências pró e contra, consolidar contradições e lacunas.  
   - Recomendar ações concretas: abrir disputa, marcar como `questioned`, manter estado atual, escalar para comitês.  
   - Gerar relatórios estruturados consumíveis por humanos e por outras camadas (V2/V3).

2. **Comitês V1/V2/V3 em decisões críticas**  
   - V1: validador mecânico que barra qualquer decisão estruturalmente inválida (máquina de estados, integridade de IDs, evidências obrigatórias).  
   - V2: comitê mínimo multi‑cérebro de IA (Guardiões Secundários + Promotores do Diabo), capaz de concordar ou divergir explicitamente da proposta inicial.  
   - V3: verificador de coerência global que impede conflitos fatais entre blocos e fatos importantes.

3. **Âncoras em blockchain v1**  
   - Gerar batches de eventos e versões, montar Merkle trees e registrar as roots em pelo menos uma chain pública.  
   - Gravar ponteiros (`anchor_id`, `chain_id`, `tx_hash`) no Sistema de Blocos.  
   - Permitir provar que uma versão/fato fazia parte de determinado batch em determinada data.

4. **Anti‑canetada como parte do contrato do sistema**  
   - Proibir caminhos técnicos que alterem diretamente o estado de blocos/fatos fora do fluxo de claims e disputas.  
   - Modelar qualquer pedido de override externo como evento e, se aceito, como disputa formal com log completo.  
   - Expor esses eventos em logs, scorecards e interfaces internas.

5. **Preparar terreno para S16 (hardening + ORR final)**  
   - Entregar todos os componentes funcionais de inteligência e blindagem.  
   - Deixar a Sprint 16 focada em Threat Model, ataques simulados, hardening, calibração de scorecards G0…G8 e ORR dedicado do Sistema de Blocos.

---

### 4. Escopo de alto nível (dentro da Sprint 15)

#### 4.1 Debunker v1 como componente ativo do pipeline

O Debunker deixa de ser apenas conceito e passa a ser um **serviço/estágio obrigatório** nas seguintes situações:

- criação de claims em temas e domínios marcados como sensíveis;
- abertura ou atualização de disputas com impacto alto (política, finanças, saúde, etc.);
- mudanças de estado que promovem versões/fatos/blocos a campeões de narrativa (por exemplo, “resultado oficial da eleição X”, “campeão da competição Y”, “número oficial de mortes em evento Z”).

Características esperadas:

- Entrada: claim + suas evidências + contexto relevante do Sistema de Blocos (blocos relacionados, disputas anteriores, padrões históricos).  
- Saída: relatório estruturado com:
  - avaliação de risco (baixo/médio/alto);  
  - resumo das evidências pró e contra;  
  - contradições encontradas;  
  - recomendação de ação (abrir disputa, marcar `questioned`, escalar para comitês, seguir em frente).  
- Integração com logs e scorecards, para que decisões do Debunker possam ser auditadas e usadas em métricas.

#### 4.2 Comitês V1/V2/V3 v1

- **V1 – Validador mecânico obrigatório**  
  - Garante que qualquer decisão de disputa/atualização de estado:
    - respeita a máquina de estados de blocos/fatos/versões;  
    - possui evidências mínimas exigidas;  
    - não quebra invariantes de integridade (referências, datas, relações pai‑filho, etc.).  
  - Rejeita a decisão imediatamente se algo estiver estruturalmente errado.

- **V2 – Comitê mínimo multi‑cérebro (IA)**  
  - Reexecuta a análise da disputa usando pelo menos dois cérebros distintos (modelos diferentes, prompts diferentes ou ambos).  
  - Inclui Promotores do Diabo que partem das saídas do Debunker para levantar objeções explícitas ("o que pode dar errado", "que outro cenário explicaria esses dados").  
  - Registra grau de concordância/discordância com a proposta inicial do Guardião principal e produz um parecer consolidado.

- **V3 – Coerência global v1**  
  - Verifica se aceitar a decisão proposta criaria conflitos graves em blocos/fatos importantes. Exemplos:
    - dois campeões para a mesma competição e temporada;  
    - dois resultados oficiais incompatíveis para a mesma eleição;  
    - estados irreconciliáveis para o mesmo mandato político no mesmo intervalo de tempo.  
  - Se encontrar incoerência, bloqueia a decisão e abre (ou reabre) disputa com foco no conflito detectado.

#### 4.3 Âncoras em blockchain v1

- Escolher ao menos uma chain pública (testnet ou mainnet de baixo custo) para registrar **Merkle roots de batches de eventos/versões**.  
- Definir uma cadência configurável (por exemplo, a cada N eventos relevantes ou a cada intervalo de tempo) para gerar batches e ancorá‑los.  
- Para cada batch:
  - montar a Merkle tree dos eventos/versões incluídos;  
  - calcular a root;  
  - registrar a root em blockchain;  
  - gravar no Sistema de Blocos o ponteiro para essa âncora.

O objetivo não é encher o blockchain de dados, mas sim ter um **carimbo público de integridade do log** que possa ser usado em auditorias futuras.

#### 4.4 Anti‑canetada operacional

- Remover ou vedar qualquer caminho que permita modificar diretamente o estado de blocos/fatos sem:
  - um claim ou disputa associados;  
  - passagem por V1/V2/V3 quando o impacto for alto.

- Para qualquer pedido de alteração originado de autoridade externa (judiciário, regulador, cliente corporativo, etc.):
  - registrar um evento explícito (por exemplo, `LegalOverrideSolicitado`);  
  - tratar o pedido como disputa ou claim especial;  
  - garantir que a decisão final (aceitar, rejeitar, parcial) seja rastreável como parte do histórico normal do Sistema de Blocos.

Na prática, isso significa **substituir “canetadas invisíveis” por “disputas visíveis”**, com trilha completa.

---

### 5. Fora de escopo na Sprint 15

Para manter foco e sanidade, a S15 **não** inclui:

1. **Sistema completo de reputação de fontes/autores/modelos**  
   - Nenhum score numérico de reputação será calculado nesta sprint.  
   - No máximo, tags descritivas simples como metadados neutros ("fonte oficial", "mídia", "rede social").

2. **Arquitetura elástica avançada de comitês**  
   - Nada de orquestração sofisticada de dezenas de modelos com seleção dinâmica por domínio.  
   - A S15 entrega a versão mínima funcional de V1/V2/V3; otimizações de custo, latência e elasticidade ficam para sprints futuras.

3. **Portal público completo e comunidade avançada**  
   - A S15 não constrói UI rica para o público final nem fluxo completo de participação da comunidade.  
   - O foco é infraestrutura de inteligência e blindagem; UIs mais elaboradas são assunto de S16+.

4. **Threat Model completo e hardening agressivo**  
   - Ataques simulados, fuzzing pesado, testes de captura de validadores e cenários de insider malicioso são foco da Sprint 16.  
   - A S15 precisa estar funcional, observável e com ganchos claros para esses testes, mas não pretende esgotar o tema segurança.

---

### 6. Definition of Ready (DoR) para iniciar a Sprint 15

A Sprint 15 só começa de fato quando:

- O core do Sistema de Blocos (S13) estiver:
  - com modelo de dados e eventos implementado;  
  - máquinas de estado de blocos/fatos/versões claras e testadas;  
  - logs append‑only funcionando;  
  - scorecards mínimos de integridade estrutural em estado GO.

- O write path com disputas (S14) estiver:
  - permitindo abrir e resolver disputas;  
  - propagando decisões para o estado atual de blocos/fatos;  
  - sem buracos evidentes no fluxo de eventos.

- APIs de leitura e escrita estiverem estáveis o suficiente para:
  - ler blocos, fatos, versões, claims e disputas;  
  - abrir novas disputas e consultar seu andamento.

- Houver pelo menos **um domínio real de teste** (por exemplo, campeonato esportivo ou caso político) já mapeado no Sistema de Blocos com disputas simuladas.

Se qualquer um desses itens falhar, a S15 deve ser travada até que S13–S14 sejam estabilizadas.

---

### 7. Definition of Done (DoD) macro da Sprint 15

A Sprint 15 é considerada concluída quando, no mínimo:

- **Debunker v1** estiver:
  - rodando em linha nos gatilhos previstos;  
  - gerando relatórios estruturados e reutilizáveis;  
  - marcando claims de alto risco como `questioned` ou abrindo disputas quando necessário;  
  - deixando trilha clara em logs e scorecards.

- **Comitês V1/V2/V3** estiverem ativos em decisões críticas:
  - nenhuma decisão que altere o estado de fatos/blocos de alto impacto passa sem V1 + V2 + V3;  
  - rejeições em qualquer camada ficam registradas com justificativa;  
  - é possível simular conflitos (dois campeões para a mesma competição, por exemplo) e ver o sistema barrando a decisão.

- **Âncoras em blockchain v1** estiverem operacionais:
  - batches de eventos/versões são gerados e ancorados periodicamente;  
  - é possível, dado um fato/versão, recuperar as âncoras relevantes;  
  - ao menos dois domínios de teste usam âncoras em cenários de auditoria.

- **Anti‑canetada** estiver em vigor:
  - não existe comando ou rota que altere estados diretamente fora de claims/disputas;  
  - pedidos de override externo geram eventos explícitos e são tratados via disputas;  
  - logs e scorecards tornam visível qualquer tentativa de interferência.

- Houver um **resumo de ORR parcial da S15**:
  - documento descrevendo o que foi entregue, riscos conhecidos, limitações e próximos passos;  
  - alimentando diretamente a preparação da Sprint 16 (hardening + ORR final do Sistema de Blocos).

---

### 8. Métricas de sucesso e sinais de alerta

Indicadores de sucesso da S15 (esperados ao final da sprint):

- Percentual de decisões de alto impacto que passam explicitamente por V1/V2/V3.  
- Número de claims de alto risco analisados pelo Debunker e proporção que resulta em: disputa aberta, marcação `questioned` ou manutenção do estado com explicação.  
- Tempo médio entre criação de claim de alto risco e atuação do Debunker.  
- Número de batches ancorados e proporção de fatos/versões importantes com âncoras associadas.  
- Número de tentativas de override externo registradas como eventos e taxa de decisões que recusam seguir por fora do fluxo normal.

Sinais de alerta que indicam falha de concepção ou implementação:

- Decisões críticas sendo tomadas sem evidência de passagem por V1/V2/V3.  
- Claims claramente arriscados que nunca são analisados pelo Debunker.  
- Dificuldade recorrente em provar, via âncoras, que uma versão existia em determinada data.  
- Qualquer caminho técnico de “arrumar na mão” um bloco/fato sem deixar rastro.

---

### 9. Impacto para o produto e para o projeto

Depois da Sprint 15, mesmo antes do hardening da S16:

- **Para o time interno do Inspectah**  
  - o Sistema de Blocos deixa de ser apenas um repositório elegante e se torna um **guardião cético da verdade**, com Debunker, comitês e âncoras defendendo as decisões mais sensíveis;  
  - fica mais simples explicar para qualquer stakeholder por que um fato está em determinado estado — o caminho V1/V2/V3 e o papel do Debunker são traçáveis.

- **Para futuros clientes e integradores**  
  - o Inspectah passa a oferecer uma narrativa de confiança muito mais forte: redundância cognitiva, resistência a canetadas e trilha externa em blockchain.  
  - isso aproxima o produto de casos de uso onde a prova de integridade e independência é obrigatória (finanças, política, auditoria, jornalismo investigativo).

- **Para a evolução do projeto**  
  - a S16 poderá focar em segurança ofensiva, hardening e ORR final do Sistema de Blocos, sem precisar reabrir discussões estruturais sobre inteligência e blindagem.  
  - o Sistema de Blocos passa a ter estrutura suficiente para receber, no futuro, reputação formal, comunidade avançada e camadas de governança mais ricas, em cima de uma base já cética e rastreável.

Este Capítulo 1 define o norte da Sprint 15: **não basta registrar a verdade — o Sistema de Blocos precisa desconfiar dela, testá‑la contra o mundo, resistir à pressão e provar, anos depois, que ninguém mexeu na história às escondidas.**

