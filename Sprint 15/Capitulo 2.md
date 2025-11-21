# Inspectah — Sprint 15  
## Capítulo 2 — Gates de Validação e Critérios de Qualidade (Revisão)

### 0. Propósito deste capítulo

Este capítulo define **como a Sprint 15 prova que entregou o que o Capítulo 1 promete**.

Aqui descrevemos, com clareza operacional, os gates T0–T8 da S15:

- o que cada gate valida;
- quais perguntas responde;
- quais riscos controla;
- quais artefatos (scorecards, evidências, logs) precisa produzir;
- quais são os critérios objetivos de PASS/FAIL.

A lógica segue o DNA e o Sprint Playbook: **nenhuma entrega da S15 é considerada real se não estiver protegida por gates claros, reproduzíveis e com evidência arquivada**.

A S15 adiciona uma camada de **inteligência e blindagem** ao Sistema de Blocos (Debunker v1, comitês V1/V2/V3, âncoras em blockchain e anti‑canetada operacional). Os gates desta sprint existem para garantir que:

1. Essas capacidades funcionam na prática, não só em papel.
2. Não introduzem rotas de bypass nem regressões nas garantias de S13–S14.
3. Produzem evidências e métricas suficientes para o hardening e ORR final da S16.

---

### 1. Visão geral dos gates da Sprint 15

Mapa resumido dos gates T0–T8 na S15:

- **T0 – Sanidade de base (S13–S14) e DoR da S15**  
  Confirma que o terreno está sólido: Truth‑DB Core e Disputas estão em GO, sem buracos de fundação sendo empurrados para a S15.

- **T1 – Contratos, estados e anti‑canetada na camada de dados**  
  Valida que novas estruturas (Debunker, comitês, âncoras, eventos de override) são compatíveis com o core e que não existe caminho técnico para alterar estados fora do fluxo de eventos/claims/disputas.

- **T2 – Debunker v1 offline (comportamento mínimo e estrutura)**  
  Testa o Debunker isoladamente, em cenários controlados, garantindo que ele identifica claims de risco, gera relatórios coerentes e recomenda ações sensatas.

- **T3 – Comitês V1/V2/V3 em fluxo integrado**  
  Verifica se o pipeline V1 → V2 → V3 funciona como um todo, sem atalhos, com rejeições reais e rastreáveis.

- **T4 – Golden Scenarios de verdade contestada (domínios reais)**  
  Usa cenários ponta‑a‑ponta (esporte, política, clima, fofoca, mandatos, projetos, ciência) para validar o comportamento real do sistema em situações delicadas.

- **T5 – Performance e custo (Debunker, comitês, âncoras)**  
  Garante que a nova camada não torna o sistema inviável: mede latência, throughput e custo (especialmente de âncoras em blockchain).

- **T6 – Observabilidade, métricas e trilhas de auditoria**  
  Confere se Debunker, comitês, âncoras e anti‑canetada são observáveis: logs, métricas e consultas respondendo perguntas chave.

- **T7 – CI, reprodutibilidade e automação dos gates**  
  Amarra T0–T6 em pipelines automatizados (CI + scripts locais), gerando scorecards e evidências de maneira previsível.

- **T8 – Go/No‑Go da camada de inteligência & blindagem**  
  Consolida os resultados e decide se a S15 entrega uma base sólida o bastante para a S16 focar em hardening e ORR final do Sistema de Blocos.

Cada seção abaixo descreve um gate com: objetivo, perguntas que responde, riscos que controla, entradas, saídas e critérios de PASS/FAIL.

---

### 2. Gate T0 – Sanidade de base (S13–S14) e DoR da S15

**Objetivo:** garantir que a S15 não está corrigindo fundação. T0 confirma que:

- Truth‑DB Core (S13) está estável (modelo de dados, log append‑only, máquinas de estado);
- Disputas & write path (S14) estão operacionais com scorecards GO;
- as pré‑condições (DoR) da S15 são verdadeiras.

**Perguntas que T0 responde:**

- S13 e S14 estão, de fato, em GO para os gates de que a S15 depende?  
- O modelo atual comporta blocos, fatos, versões, claims e disputas sem atalhos diretos?  
- Há algum bug estrutural aberto (invariantes quebrados, rotas de override direto) que inviabilize a camada de inteligência?

**Riscos controlados por T0:**

- Construir Debunker e comitês em cima de um core instável.  
- Usar a S15 como “caixa de remendos” de problemas antigos.  
- Ignorar rotas de corrupção de log já existentes.

**Entradas:**

- Scorecards finais de S13 e S14.  
- Schema atual do Sistema de Blocos.  
- Documentos de ORR de S13–S14 e lista de riscos herdados.

**Saídas:**

- Scorecard `S15_T0_sanity.json`.  
- Evidência de verificação das pré‑condições (DoR) da S15.

**Critérios de PASS:**

- Gates fundamentais de S13–S14 em GO ou com riscos explicitamente aceitos.  
- Nenhum bug estrutural crítico pendente (log corrompível, quebra de integridade, override direto).  
- DoR da S15 confirmada.

**Critérios de FAIL:**

- Gate fundamental de S13–S14 em NO_GO sem mitigação.  
- Rota conhecida que permita alterar estados sem eventos de log.  
- Qualquer violação grave de invariantes centrais do core.

---

### 3. Gate T1 – Contratos, estados e anti‑canetada na camada de dados

**Objetivo:** validar que as extensões de dados e contratos trazidas pela S15 são seguras e consistentes com o core.

**Perguntas que T1 responde:**

- As novas entidades/eventos (relatórios do Debunker, decisões de comitês, âncoras, pedidos de override) estão bem modelados e integrados ao modelo existente?  
- Máquinas de estado de blocos, fatos, versões e disputas continuam válidas após a S15?  
- Está garantido, em nível de contrato e código, que não há `force_set_state` ou equivalente escondido?

**Riscos controlados por T1:**

- Introduzir tipos e estados que furam o modelo de log append‑only.  
- Criar, sem querer, um atalho de override direto em algum endpoint interno.  
- Quebrar a integridade do Sistema de Blocos ao acoplar Debunker/comitês/âncoras.

**Entradas:**

- Esquemas de dados atualizados.  
- Capítulo de Contratos & TLA+ com extensões da S15.  
- Testes de unidade e propriedade focados em estados e rotas de atualização.

**Saídas:**

- Scorecard `S15_T1_contracts_and_states.json`.  
- Evidências de testes cobrindo:
  - ausência de rotas de override direto;  
  - consistência das máquinas de estado pós‑S15.

**Critérios de PASS:**

- Toda alteração de estado passa por eventos/claims/disputas, respeitando as máquinas de estado.  
- Nenhuma função/endpoint permite modificar estados de blocos/fatos/versões sem trilha.  
- Novos tipos/eventos preservam o modelo de log append‑only.

**Critérios de FAIL:**

- Qualquer caminho identificado de alteração direta de estado sem evento.  
- Inconsistências entre contratos, schema e implementação.

---

### 4. Gate T2 – Debunker v1 offline (comportamento mínimo e estrutura)

**Objetivo:** validar o Debunker v1 de forma isolada, com cenários controlados, antes de conectá‑lo ao fluxo completo.

**Perguntas que T2 responde:**

- O Debunker consegue identificar claims de alto risco usando limiares configuráveis?  
- Ele produz relatórios estruturados (risco, evidências pró/contra, contradições, recomendação)?  
- As recomendações fazem sentido frente às expectativas de cada cenário?

**Riscos controlados por T2:**

- Debunker cego a claims perigosos.  
- Relatórios inúteis (sem estrutura, sem contradições, sem recomendação).  
- Tendência a “abraçar certezas” em cenários de incerteza alta.

**Entradas:**

- Fixtures de claims e evidências em múltiplos domínios (esporte, política, clima, fofoca, mandatos, projetos, ciência).  
- Configuração de limiares de risco da S15.  
- Implementação do Debunker v1.

**Saídas:**

- Scorecard `S15_T2_debunker_offline.json`.  
- Evidência em `out/evidence/S15_T2_debunker_offline/` com relatórios gerados e comparações com expectativas.

**Critérios de PASS:**

- Claims rotulados como “alto risco” nos fixtures são corretamente identificados.  
- Recomendações acompanham a lógica prevista (aceitar quando evidência é forte, `questioned` ou disputa quando há ambiguidade).  
- Em cenários ambíguos, o Debunker tende à prudência, não à certeza artificial.

**Critérios de FAIL:**

- Claims de alto risco ignorados de forma sistemática.  
- Recomendações majoritariamente opostas ao esperado nos cenários de teste.  
- Relatórios incompletos ou incoerentes (campos vazios, contradições não apontadas).

---

### 5. Gate T3 – Comitês V1/V2/V3 em fluxo integrado

**Objetivo:** validar o funcionamento integrado dos comitês V1, V2 e V3 sobre decisões reais (propostas pelo Guardião principal, com insumo do Debunker).

**Perguntas que T3 responde:**

- Decisões críticas de disputa passam por V1, V2 e V3 sem atalhos?  
- V1 barra decisões estruturalmente inválidas antes de chegar em IA?  
- V2 consegue gerar concordância/discordância explícita entre múltiplos cérebros, incluindo Promotores do Diabo?  
- V3 detecta incoerências globais relevantes e consegue bloquear decisões perigosas?

**Riscos controlados por T3:**

- Tratamento decorativo de comitês (pipeline existe, mas não decide nada).  
- Decisões graves passando sem revisão mecânica ou sem oposição.  
- Conflitos fatais entre blocos/fatos passando despercebidos.

**Entradas:**

- Implementação dos comitês V1, V2, V3.  
- Conjunto de disputas de teste com diferentes graus de complexidade.  
- Saídas do Debunker (T2) para alimentar V2.

**Saídas:**

- Scorecard `S15_T3_committees_flow.json`.  
- Evidências:
  - logs de execuções de V1/V2/V3 por disputa;  
  - exemplos de decisões aceitas e rejeitadas em cada camada.

**Critérios de PASS:**

- Toda decisão crítica nos cenários de teste tem rastro completo de V1, V2 e V3.  
- Há exemplos claros de rejeição em cada camada (V1, V2, V3).  
- Não existe rota alternativa aplicando decisões sem passar pelos comitês.

**Critérios de FAIL:**

- Decisões aplicadas sem evidência de passagem pelos três comitês.  
- V2 sempre concordando, sem objeções, mesmo em cenários conflituosos.  
- V3 incapaz de detectar conflitos óbvios entre blocos de teste.

---

### 6. Gate T4 – Golden Scenarios de verdade contestada (domínios reais)

**Objetivo:** validar a S15 ponta‑a‑ponta em cenários realistas de verdade contestada, cobrindo vários domínios.

**Perguntas que T4 responde:**

- Em casos simulados de alto interesse (esporte, eleição, clima, fofoca, mandatos, projetos, ciência), o fluxo completo se comporta como previsto?  
- Debunker, comitês, âncoras e anti‑canetada aparecem na linha do tempo do caso?  
- Pedidos de override externo são registados e tratados como disputas, nunca como atalho silencioso?

**Riscos controlados por T4:**

- Sistema teoricamente correto, mas com buracos práticos em casos reais.  
- Falta de integração entre os componentes da S15 em domínios sensíveis.  
- Atalhos de override surgindo na prática, fora do desenho.

**Entradas:**

- Cenários golden pré‑definidos em múltiplos domínios, com roteiro esperado.  
- Configuração de gatilhos do Debunker e comitês.

**Saídas:**

- Scorecard `S15_T4_golden_scenarios.json`.  
- Evidência por cenário (por exemplo, `out/evidence/S15_T4_golden_<dominio>/`) com:
  - sequência de eventos;  
  - atuação do Debunker;  
  - parecer dos comitês;  
  - âncoras geradas;  
  - pedidos de override (se houver) e sua resolução.

**Critérios de PASS:**

- Em todos os cenários golden, o sistema segue o caminho previsto pelo Capítulo 1.  
- Não há atualização de verdade fora de disputas/comitês.  
- Âncoras são criadas e ligadas aos fatos/versões relevantes dentro das janelas planejadas.

**Critérios de FAIL:**

- Cenários que exigem contestação passando sem atuação do Debunker.  
- Decisões finais que contradizem o roteiro esperado sem justificativa registrada.  
- Override acontecendo na prática sem evento/disputa visível.

---

### 7. Gate T5 – Performance e custo (Debunker, comitês, âncoras)

**Objetivo:** garantir que a camada de inteligência & blindagem tem custo e performance aceitáveis.

**Perguntas que T5 responde:**

- Qual a latência adicional introduzida pelo Debunker e comitês em decisões críticas?  
- Qual o throughput suportado em cenários alvo (claims/disputas por unidade de tempo)?  
- Qual o custo estimado de âncoras em blockchain, por período e por volume de eventos?

**Riscos controlados por T5:**

- Sistema conceitualmente correto, porém impraticável em escala.  
- Custos de âncoras inviabilizando a operação.  
- Gargalos de comitês travando disputas em massa.

**Entradas:**

- Cenários de carga definidos (claims, disputas, batches de ancoragem).  
- Ferramentas de benchmark e coleta de métricas.  
- Implementações finais de Debunker, comitês e módulo de âncoras.

**Saídas:**

- Scorecard `S15_T5_performance_and_cost.json`.  
- Relatórios de bench de latência/throughput e estimativa de custos de âncoras.

**Critérios de PASS:**

- Latência e throughput dentro dos SLOs definidos para S15.  
- Custos de âncoras em patamar aceitável para a Fase 2 (com margem de segurança).  
- Sem erros recorrentes de ancoragem sob carga planejada.

**Critérios de FAIL:**

- Latência ou custo materialmente incompatíveis com o uso pretendido.  
- Erros ou timeouts sistemáticos em cenários de carga moderada.

---

### 8. Gate T6 – Observabilidade, métricas e trilhas de auditoria

**Objetivo:** garantir observabilidade real da camada introduzida na S15.

**Perguntas que T6 responde:**

- Conseguimos listar, rapidamente, claims de alto risco analisados pelo Debunker em um período?  
- Sabemos quantas decisões passaram por V1/V2/V3, quantas foram rejeitadas e por qual motivo?  
- Conseguimos mapear fatos/versões para suas âncoras e vice‑versa?  
- Temos logs claros de pedidos de override e da forma como foram tratados?

**Riscos controlados por T6:**

- Sistema que “funciona”, mas é opaco e inauditável.  
- Dificuldade em investigar incidentes ou suspeitas de manipulação.  
- Falta de dados para o Threat Model e hardening da S16.

**Entradas:**

- Instrumentação de logs e métricas (Debunker, V1/V2/V3, âncoras, override).  
- Ferramentas de observabilidade usadas no projeto.  
- Conjunto de consultas e painéis propostos.

**Saídas:**

- Scorecard `S15_T6_observability.json`.  
- Evidência de consultas que respondem perguntas chave, além de exports/snapshots dos painéis.

**Critérios de PASS:**

- Perguntas chave respondidas em poucos passos (consulta ou painel já pronto).  
- Logs com estrutura suficiente para reconstruir o caminho de uma decisão crítica.  
- Métricas úteis para S16 (taxa de disputas, revisões, overrides, etc.).

**Critérios de FAIL:**

- Dificuldade prática em rastrear decisões ou âncoras específicas.  
- Ausência de logs ou métricas em pontos críticos.

---

### 9. Gate T7 – CI, reprodutibilidade e automação dos gates

**Objetivo:** garantir que a validação da S15 é reprodutível, tanto em CI quanto localmente.

**Perguntas que T7 responde:**

- Existe um caminho único e bem documentado para rodar todos os gates T0–T6 e gerar scorecards/evidências?  
- O CI executa essa bateria de forma confiável?  
- Um operador consegue reproduzir localmente a mesma validação que roda em CI?

**Riscos controlados por T7:**

- Gates que só funcionam no ambiente de quem criou.  
- Divergência entre o que CI valida e o que é possível rodar localmente.  
- Evidências espalhadas e difíceis de localizar.

**Entradas:**

- Pipelines de CI atualizados para S15.  
- Scripts de orquestração local (por exemplo, um `bin/s15_all_gates.sh` ou equivalente).  
- Configuração de artefatos de evidência e scorecards.

**Saídas:**

- Scorecard `S15_T7_ci_and_repro.json`.  
- Logs de execução de CI e listagem consolidada de scorecards e pastas de evidência.

**Critérios de PASS:**

- Um comando (ou conjunto pequeno e bem definido) roda toda a bateria T0–T6 localmente.  
- CI executa a mesma bateria em PRs e/ou na branch principal quando acionado.  
- Scorecards e evidências são salvos em locais previsíveis e documentados (Capítulo 3).

**Critérios de FAIL:**

- Gates importantes só funcionam via passos manuais e pouco documentados.  
- Resultados inconsistentes entre CI e ambiente local.

---

### 10. Gate T8 – Go/No‑Go da camada de inteligência & blindagem

**Objetivo:** consolidar os resultados dos gates T0–T7 e decidir, de forma objetiva, se a camada da S15 está pronta para a S16 focar em hardening e ORR final.

**Perguntas que T8 responde:**

- Todos os gates T0–T7 atingiram PASS ou há falhas com mitigação clara e prazo definido?  
- Os riscos residuais são compatíveis com o estágio da S15 (funcionalidade completa, ainda antes do hardening agressivo)?  
- É seguro permitir que a S16 foque em testar/atacar o sistema sem reabrir arquitetura da S15?

**Riscos controlados por T8:**

- Declarar vitória com gates quebrados.  
- Empurrar riscos estruturais graves para a S16.  
- Entrar em hardening sem base funcional estável.

**Entradas:**

- Scorecards `S15_T0`…`S15_T7`.  
- Evidências principais de cada gate.  
- Análise humana de riscos e limitações conhecidas.

**Saídas:**

- Scorecard final `S15_T8_go_no_go.json` com decisão GO/NO_GO.  
- Mini‑ORR da S15 com:  
  - resumo do que foi entregue;  
  - o que ficou fora de escopo;  
  - riscos conhecidos e planos de mitigação.

**Critérios de PASS (GO):**

- Gates T0–T7 em PASS, ou desvios limitados com mitigação clara e aceita.  
- Nenhum risco estrutural grave pendente (override direto, log não confiável, âncoras inoperantes, comitês decorativos).  
- Capacidade comprovada de operar Debunker, comitês e âncoras nos domínios de teste.

**Critérios de FAIL (NO_GO):**

- Qualquer gate fundamental (T1, T2, T3, T4 ou T6) em NO_GO sem mitigação aceitável.  
- Evidência de que o Sistema de Blocos pode ser manipulado sem rastro, mesmo após a S15.  
- Impossibilidade prática de operar a camada de inteligência & blindagem nos cenários alvo.

---

### 11. Amarração com os demais capítulos

- O **Capítulo 1** define o *porquê* da S15: o Sistema de Blocos precisa ser cético, redundante e resistente a canetadas.  
- Este **Capítulo 2 (revisado)** define o *como provar* que isso é verdade: gates, riscos controlados, critérios e evidências.  
- O **Capítulo 3** vai detalhar o *onde vive cada coisa*: filemap, arquitetura de scripts, scorecards, evidências e painéis.  
- Um eventual **Capítulo 4** traduzirá estes gates em *como usar na prática*: prompts, comandos concretos, rotinas de operação e de debug.

Com esta versão revisada do Capítulo 2, a Sprint 15 passa a ter um mapa de validação mais nítido: fica claro **que riscos cada gate segura**, **quais perguntas ele responde** e **que evidência precisa existir** para declararmos a camada de inteligência & blindagem pronta para o crivo pesado da S16.

