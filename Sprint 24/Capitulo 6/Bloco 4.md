# 6.4 – Recomendações Integradas & Roadmap (S23–S25 + Fase 2) – v2 extremo

Este 6.4 v2 extremo é a versão **articulada, integrada e operacional** do que o Squad Verdade & Interpretação aprendeu, teme e decidiu assumir:

- 6.1 – Lições: o que a realidade validou e o que doeu;  
- 6.2 – Riscos: onde podemos quebrar e quais sinais olhar;  
- 6.3 – Débitos: o que não fizemos de propósito, e não por esquecimento.

Aqui, isso tudo vira **plano de movimento**:

- prioridades claras para **S23–S25** na trilha Verdade & Interpretação / Casos Inspectah;  
- eixos estruturantes da **Fase 2** (Sistema de Blocos, reputação, contestação, comunidade);  
- critérios de sucesso e perguntas de GO/NO‑GO que evitam autoengano.

---

## 6.4.1 – Objetivos estratégicos da trilha Verdade & Interpretação

O Squad Verdade & Interpretação alinha quatro objetivos estratégicos para o próximo ciclo:

1. **Endurecer o elo Truth‑DB → Case Layer → Casos Inspectah**  
   A Truth‑DB só cumpre seu papel se o que chega em Casos Inspectah for uma projeção fiel, atualizável e auditável. O elo Truth‑DB ↔ casos precisa ser **contratual**, não tácito.

2. **Transformar curadoria de arte manual em processo replicável**  
   Curadores heróis funcionam para v0. Para um sistema 24/7, precisamos de ferramentas, processos e métricas que permitam curadoria por múltiplas pessoas, em múltiplos temas, sem perda de qualidade.

3. **Colocar produto/UX sob o mesmo regime de rigor do resto do sistema**  
   Casos/coleções não são marketing. São a API humana do Inspectah. Precisam ter **gates, métricas, observabilidade e revisão** tão duras quanto ingestão, Debunker e comitês.

4. **Construir S23–S25 como rampa de acesso para a Fase 2**  
   Sistema de Blocos, reputação e contestação não podem exigir rework maciço. S23–S25 precisam deixar contratos, estruturas e métricas prontos para receber essas camadas como extensões naturais.

---

## 6.4.2 – Mapa de prioridades S23–S25 (7 frentes)

A partir de 6.1–6.3, o squad consolida 7 frentes de prioridade para S23–S25. Cada frente vem com: por quê, o que fazer, critérios de sucesso.

### P1 – Blindar Truth‑DB ↔ Case Layer

**Por que é prioritário**  
- Riscos RT1, RD1, RD2 e RD3 apontam que o elo Truth‑DB↔casos é o ponto mais sensível da trilha.  
- Sem esse elo estável, qualquer trabalho posterior (curadoria, UX, blocos, reputação) será construído em areia.

**O que fazer em S23–S25**  
- Consolidar `app/cases/resolver.py` como **boundary único** de interpretação da Truth‑DB para casos (nada de lógica de truth espalhada no frontend ou em rotas);  
- Documentar as **invariantes de Truth‑DB** que a Case Layer assume (tipos de estados, semântica de FACT/DISPUTED/UNKNOWN, etc.);  
- Implementar **testes de contrato** Truth‑DB ↔ Case Layer, rodando em gates de S23–S25;  
- Adicionar metadados de reconciliação em `ResolvedCase` (timestamp, versão de regras de comitê/Debunker que originou aquele estado).

**Critérios de sucesso**  
- Toda mudança relevante em Truth‑DB/comitês dispara testes de contrato;  
- divergências entre Truth‑DB e casos críticos passam a ser detectadas pelos scripts, não pelo usuário final;  
- não há necessidade de “hotfix manual” em casos após ajustes de modelos.

---

### P2 – Case Builder + mini‑console de curadoria (v1)

**Por que é prioritário**  
- DT1, DP1, RO1 e RO2 convergem: curadoria atual é payload demais pro time; não escala e não abre espaço para novos curadores.  
- Sem tooling mínimo, qualquer promessa de aumentar o patrimônio de casos é ilusória.

**O que fazer em S23–S25**  
- Especificar e implementar um **Case Builder mínimo (web)** que permita:  
  - buscar Claims/TruthRecords/Events por tema/entidade;  
  - selecionar evidências e anotações do Debunker/comitês;  
  - montar seções e timeline via interface;  
  - gerar/atualizar `case_*.yaml` por trás, com validações estruturais automáticas;  
- Criar um **mini‑console de curadoria**, com:  
  - listagem de casos com filtros (tema, sensibilidade, status, idade, criticidade);  
  - sinalização de “precisa revisão” (integrada a jobs de drift);  
  - links diretos para abrir o caso no Case Builder.

**Critérios de sucesso**  
- Um curador novo consegue criar/editar um caso canônico sem tocar diretamente em YAML;  
- o squad consegue enxergar, em uma única tela, o estado do catálogo (rascunhos, publicados, em revisão) e priorizar trabalho.

---

### P3 – Observabilidade dedicada da Case Layer

**Por que é prioritário**  
- RT2 aponta: endpoints de casos/coleções são críticos e ainda invisíveis como camada própria.  
- Sem métricas específicas, bugs e degradação de performance são detectados tarde demais.

**O que fazer em S23–S25**  
- Instrumentar endpoints `/api/cases*` e `/api/collections*` com métricas de:  
  - latência p50/p95/p99;  
  - taxa de erro por rota;  
  - tamanho de payload;  
  - quantidade de eventos/tamanho da timeline por caso;  
  - tamanho de coleções (nº de casos);  
- Criar um **painel de saúde da Case Layer**, com gráficos simples, mas focados nesses endpoints;  
- Definir thresholds iniciais de alerta (por exemplo, p95 de `/cases/:id` acima de X ms por Y minutos).

**Critérios de sucesso**  
- Reclamações sobre lentidão/instabilidade em casos podem ser respondidas com dados objetivos em segundos;  
- incidentes deixam trilha clara em painéis, facilitando RCA (root cause analysis).

---

### P4 – Suíte de testes robusta para a Case Layer

**Por que é prioritário**  
- DT2 + RT3 + RD1 + RD3: sem testes fortes, toda evolução de modelo vira roleta russa.  
- Casos/coleções são API de produto – precisam de defesa automatizada.

**O que fazer em S23–S25**  
- Criar um **módulo de testes dedicado a `app/cases/`**, cobrindo:  
  - resolução de casos simples, médios e extremos;  
  - comportamento em diferentes estados de truth (certeza, incerteza, disputa);  
  - integridade de timeline (ordem, agrupamento de eventos, filtros);  
  - respostas de erro claras para casos inválidos/incompletos;  
- Integrar essa suíte aos gates de validação das próximas sprints.

**Critérios de sucesso**  
- Refactors em Truth‑DB/Case Layer passam a ser dirigidos por feedback da suíte de testes, não por medo;  
- regressões em casos tornam‑se raras e, quando ocorrem, facilmente reproduzíveis e corrigíveis.

---

### P5 – Métricas de produto de casos/coleções como ativo de 1ª classe

**Por que é prioritário**  
- DP3 e RP1–RP3: hoje sabemos medir, mas não sabemos **ver** e **usar** essas métricas no dia a dia.  
- Sem painel vivo, o patrimônio de casos é gerido na intuição.

**O que fazer em S23–S25**  
- Exportar métricas de casos/coleções para a stack de observabilidade ou data warehouse oficial;  
- Construir um **Painel de Patrimônio de Casos**, com:  
  - nº de casos por tema, sensibilidade, estado de truth;  
  - cobertura por coleções;  
  - idade média desde última revisão (geral e por tema crítico);  
  - casos mais acessados, coleções mais vistas;  
- Definir metas mínimas (ex.: cobertura ≥ X para temas A/B, idade média ≤ Y dias para casos críticos).

**Critérios de sucesso**  
- Reuniões de planejamento de casos/coleções passam a usar esse painel explicitamente;  
- decisões de priorização deixam de ser 100% subjetivas.

---

### P6 – Ritual de revisão e combate sistemático ao "case drift"

**Por que é prioritário**  
- RD1 + RO2 + DG2: se casos não forem revisitados, viram fósseis.  
- O valor do Inspectah cai se a face pública da verdade não acompanhar a Truth‑DB.

**O que fazer em S23–S25**  
- Definir critérios de seleção de casos para revisão (idade, criticidade do tema, volume de alterações recentes na Truth‑DB, volume de acessos, volume de feedback);  
- Implementar **jobs de reconciliação** que comparem estados de truth de casos críticos com a Truth‑DB e marquem “precisa revisão”;  
- Reservar capacidade explícita em cada sprint para revisão de um subconjunto de casos (por tema ou criticidade).

**Critérios de sucesso**  
- A diferença entre estado de truth da Truth‑DB e o exibido em casos críticos se mantém dentro de um limite estabelecido;  
- a porcentagem de casos marcados como “precisa revisão” e ignorados de sprint a sprint cai ao longo do tempo.

---

### P7 – Canais internos de feedback/contestação (primeiro passo)

**Por que é prioritário**  
- RP4 + DG3: sem feedback interno, o sistema é surdo; sem contestação, é monólogo.  
- Fase 2 (contestação pública, reputação) exigirá que esses reflexos já existam.

**O que fazer em S23–S25**  
- Incluir, na UI de casos, um **canal mínimo de feedback** (ex.: botão “Reportar problema/dúvida” → issue interna ou formulário);  
- Definir rota de triagem: quem recebe, em quanto tempo responde, como isso se conecta a Debunker/curadoria;  
- Começar a medir: nº de feedbacks por caso, tipos de feedback (erro factual, clareza, pedido de atualização, etc.).

**Critérios de sucesso**  
- Feedback via produto passa a existir de forma rastreável;  
- pelo menos alguns casos são efetivamente corrigidos ou melhorados em função de feedback registrado.

---

## 6.4.3 – Eixos da Fase 2 (Blocos, Reputação, Contestação) conectados à S23–S25

A Fase 2 não é reset: é multiplicador. Este trecho mapeia **o que a Fase 2 faz** e **o que ela exige de S23–S25**.

### F2.1 – Sistema de Blocos como âncora de verdade e de processo

**O que a Fase 2 quer**  
- Representar fatos, decisões de comitê, revisões importantes e acordos de verdade como **blocos** em uma estrutura resistente (on‑chain ou ledger equivalente), com:
  - imutabilidade;  
  - rastreabilidade;  
  - verificação independente.

**Como isso conversa com Casos Inspectah**  
- Casos canônicos referenciam blocos que ancoram o estado de truth mostrado;  
- revisões significativas de casos geram novos blocos (ou relacionamentos entre blocos), criando uma **linha do tempo ancorada** da verdade daquele tema.

**O que S23–S25 precisam entregar para isso ser viável**  
- Case Layer com contratos estáveis (P1 + P4);  
- modelo claro de "quais eventos de truth/revisão merecem virarem blocos";  
- rotina de revisão minimamente estruturada (P6), para saber quando uma mudança é “material” o suficiente para ancoragem.

---

### F2.2 – Reputação de fontes, atores, curadores e processos

**O que a Fase 2 quer**  
- Medir e expor sinais de **confiabilidade** de fontes, atores e curadores: histórico de acertos, correções, contestação válida, transparência, etc.  
- Usar reputação como mais uma camada de contexto, não como oráculo.

**Como isso conversa com Casos Inspectah**  
- Casos passam a carregar sinais de reputação dos principais ingredientes:  
  - quão confiáveis historicamente são as fontes em destaque;  
  - qual é o histórico do curador;  
  - quanto aquele caso já foi questionado e quantas correções gerou;  
- Curadores e comitês podem ter reputação associada à qualidade e estabilidade dos casos em que atuam.

**O que S23–S25 precisam entregar**  
- Painel de métricas de produto/uso de casos (P5);  
- registros estruturados de revisões de casos (P6);  
- primeiros canais de feedback/contestação internos (P7);  
- pelo menos um modelo claro de como registrar “acertos, correções e revisões importantes” como eventos.

---

### F2.3 – Contestação estruturada e participação da comunidade

**O que a Fase 2 quer**  
- Transformar o Inspectah de um sistema que "fala para" pessoas em um sistema que **conversa com** pessoas: contestação pública estruturada, regras claras de participação e integração com Debunker e comitês.  
- Permitir que o processo de revisão de verdade seja visível e auditável.

**Como isso conversa com Casos Inspectah**  
- Casos se tornam hubs de discussão verificada:  
  - contestação gera issues vinculadas ao caso;  
  - issues relevantes viram investigações Debunker/comitê;  
  - investigações que alteram estados de truth acabam ancoradas em blocos;  
- A UI de casos passa a mostrar não apenas "qual é o estado atual", mas também **o histórico de contestação e revisão**.

**O que S23–S25 precisam entregar**  
- Fluxos internos de feedback minimamente estáveis (P7);  
- governança um pouco menos difusa para casos sensíveis (DG1);  
- processos de revisão em funcionamento (P6) para suportar o volume aumentado de contestação.

---

## 6.4.4 – Critérios de sucesso e perguntas de GO/NO‑GO por sprint

Para evitar que este plano vire apenas texto bonito, o squad propõe que **cada sprint relevante (S23–S25)** responda, de forma explícita, às perguntas abaixo ao fechar.

### Bloco 1 – Truth‑DB ↔ casos

1. Alguma mudança em Truth‑DB/comitês foi feita nesta sprint?  
2. Os testes de contrato Truth‑DB ↔ Case Layer rodaram em cima dessas mudanças?  
3. Algum caso crítico apresentou drift relevante? Se sim, foi revisado ou marcado para revisão imediata?

### Bloco 2 – Curadoria e ferramentas

4. O fluxo de curadoria ficou **mais leve, igual ou mais pesado** que na sprint anterior? Por quê?  
5. Alguma parte do processo ainda depende exclusivamente de 1–2 pessoas? O que foi feito para reduzir isso?  
6. O Case Builder/mini‑console ganhou capacidades concretas (ou ficou em protótipo/slide)?

### Bloco 3 – Produto/UX de Casos Inspectah

7. As métricas de produto de casos/coleções ficaram mais visíveis e foram usadas em alguma decisão real?  
8. A experiência de A/B ao ler um caso melhorou em algum aspecto mensurável (menos cliques até evidência, mais clareza, menos confusão reportada)?  
9. Alguma melhoria de visualização (timeline, resumos, destaques) foi testada com casos complexos?

### Bloco 4 – Governança, revisão e feedback

10. Houve avanço em processos de revisão periódica (casos revisados, calendário, critérios)?  
11. Algum caso sensível foi tratado com um fluxo de aprovação mais cuidadoso? Isso foi registrado?  
12. Feedback/contestação in‑product foi recebido e tratado? Qual foi o ciclo completo (receber → analisar → agir)?

### Bloco 5 – Preparação para Fase 2

13. Alguma decisão desta sprint **facilitou** de forma concreta a adição de blocos, reputação ou contestação estruturada?  
14. Alguma decisão desta sprint criou **barreiras novas** para a Fase 2 (acoplamentos desnecessários, contratos tacitamente quebráveis)?  
15. Se sim, essas barreiras estão registradas como novos débitos em 6.3 ou precisam ser incorporadas?

Uma sprint só deveria receber GO “forte” na trilha Verdade & Interpretação se as respostas acima mostrarem avanço real em pelo menos alguns desses blocos, sem regressões graves nos demais.

---

## 6.4.5 – Como usar este 6.4 v2 na prática

Para que este capítulo não vire só documento de referência, o Squad Verdade & Interpretação recomenda:

1. **Planejamento de sprint**  
   - Começar o planejamento revisando 6.3 (débitos) e 6.4 (prioridades P1–P7).  
   - Selecionar conscientemente quais débitos vão ser atacados na sprint e quais continuam aceitos.

2. **Execução**  
   - Amarrar tarefas de implementação e curadoria explicitamente às frentes P1–P7 e eixos F2.1–F2.3.  
   - Usar os critérios de sucesso como parte do Definition of Done para features de Casos Inspectah.

3. **Fechamento / ORR**  
   - Responder, por escrito, ao bloco de perguntas 6.4.4 para cada sprint;  
   - Atualizar 6.3 com quaisquer novos débitos que tenham surgido;  
   - Ajustar prioridades em 6.4, se algum risco ou lição nova surgir.

Se 6.1 foi o que aprendemos, 6.2 foi o que pode quebrar e 6.3 foi o que deixamos de pé por enquanto, este 6.4 v2 é o **caderno de rota**: a forma como o Inspectah transforma tudo isso em direções claras, iteráveis e auditáveis para as próximas sprints e para a Fase 2.

