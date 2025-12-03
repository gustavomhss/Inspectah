# Inspectah — Sprint 27 (S27)
## Capítulo 6 — Learnings, Dívidas & Impacto no Roadmap

> Arquivo-alvo no repo: `docs/s27_cap_6_learnings_dividas_roadmap.md`
>
> Função: consolidar o que a Sprint 27 ensinou (learnings), o que ficou pendente (dívidas) e como isso altera ou confirma o roadmap do Inspectah, com foco no Épico E26 (Admin v1 em Programa 1: Fontes, Ingestão e Debunker).

---

## 1. Papel do Capítulo 6 na S27

Cap.6 é o lugar onde a S27 deixa de ser só um conjunto de tarefas e evidências e passa a ser memória institucional e insumo de decisão.

Ele responde a três perguntas:

1. **O que aprendemos?** — sobre Admin v1, consoles, operação, usuários internos, processo de entrega.  
2. **O que ficou devendo?** — dívidas técnicas, de produto, de UX, de testes, de operações.  
3. **O que isso muda no futuro?** — ajustes no roadmap, prioridades de próximos épicos/sprints, riscos que continuam abertos.

Este capítulo se apoia explicitamente em:

- scorecards G0–G6 (especialmente G2, G4, G5 e G6);  
- bundle de evidências da S27;  
- Cap.5 (ORR e veredito);  
- tasks S27-T-XXX e ações ACT-XXX derivadas do ORR.

---

## 2. Sumário executivo (visão em 1 página)

> Esta seção deve ser preenchida **após** o ORR, com base no G6 final e nas discussões da sessão.

### 2.1 Frase-resumo da S27

> Exemplo de formato:  
> "A S27 consolidou o Admin v1 como padrão real em Programa 1 (Fontes, Ingestão, Debunker), com fluxos E2E mínimos e operação documentada, mas deixou riscos moderados em cenários avançados de Debunker e cobertura E2E ampliada para ciclos futuros."

### 2.2 Principais learnings (3–7 pontos)

- O que mais funcionou bem na adoção do Admin v1 nos consoles.  
- O que surpreendeu positivamente na experiência dos usuários internos.  
- Onde os gates e scorecards ajudaram a evitar problemas.

### 2.3 Principais dívidas e riscos que permanecem

- Gaps principais em E2E (por exemplo, cenários avançados de Debunker, casos encadeados, falhas intermitentes).  
- Pontos frágeis em contratos ou em UX que ainda não bloqueiam Programa 1, mas podem limitar escala.  
- Aspectos de operação que ainda dependem demais de conhecimento tácito da equipe.

### 2.4 Impacto direto no roadmap

- Quais temas se tornam prioridade nas próximas sprints (ex.: Debunker E2E, Admin v1 em Programa 2, refino de runbooks, automação de ORRs).  
- Quais planos anteriores foram confirmados, quais precisam ser reordenados.

---

## 3. Learnings da S27 por eixo

### 3.1 Eixo Produto & UX (Admin v1 + Consoles)

Pontos a capturar aqui:

- Como Admin v1 se comportou aplicado de verdade aos consoles de Fontes, Ingestão e Debunker.  
- O que funcionou bem na navegação, hierarquia de informações, padronização de componentes.  
- Quais ajustes de UX se mostraram necessários quando os consoles passaram a ser usados com fluxos reais (não só mock ou dados de teste triviais).  
- Quais padrões de layout e interação provaram ser robustos o suficiente para serem replicados em outros módulos.

Sugestão de subestrutura:

- **O que funcionou bem** (lista curta, com exemplos concretos).  
- **O que não funcionou como esperado** (evidências, feedbacks de usuários internos, bugs recorrentes).  
- **Princípios de design que emergiram** (por exemplo: sempre mostrar estado de fonte e impacto em ingestão no mesmo painel; deixar rastros de fluxo em Debunker; etc.).

### 3.2 Eixo Engenharia & Qualidade (Gates, E2E, Contratos)

Aqui entram aprendizados sobre:

- Eficácia de G1, G2, G3 e G4 em pegar problemas cedo.  
- Experiência prática de manter cenários E2E alinhados com evolução das telas admin.  
- Dificuldades em manter contratos estáveis ao mesmo tempo em que os consoles evoluíram.  
- Benefícios (ou dores) de ter scorecards para cada gate.

Sugestão de pontos:

- **Gates que mais salvaram a sprint** (por exemplo, G2 pegando quebra de fluxo antes de chegar em ORR).  
- **Gates que geraram ruído ou pouco sinal** (e como melhorar ou simplificar scripts).  
- **Testes E2E** — o que foi fácil/difícil de automatizar, que tipos de cenários trouxeram mais valor.  
- **Contratos de API** — onde testes de contrato evitaram regressões reais.

### 3.3 Eixo Operação & Runbooks

Aprendizados sobre operar Programa 1 com Admin v1, guiado por docs:

- Como os runbooks de Fontes, Ingestão e Debunker se comportaram nas simulações.  
- O que as simulações revelaram sobre lacunas de informação ou de ferramenta.  
- Dicas práticas que surgiram e que deveriam constar nos runbooks (por exemplo, sequências preferenciais de telas, filtros úteis, checklists de triagem).

Aqui também vale registrar:

- Padrões de incidentes (ou quase incidentes) que apareceram nas simulações.  
- Pontos em que a equipe teve que recorrer a conhecimento tácito, mesmo com runbooks.

### 3.4 Eixo Processo & Forma de Trabalhar

Learnings sobre o próprio modelo de sprint com gates, waves e ORR:

- Como a divisão em W0–W3 funcionou para a S27 (o que poderia ser melhor distribuído).  
- Como foi o uso de Cap.1–Cap.5 como guias vivos (o que virou ruído, o que ajudou).  
- O quanto o time conseguiu rodar gates de forma incremental, e não só no fim.  
- O que o ORR da S27 trouxe de melhoria em relação a ORRs anteriores.

Essa seção também pode capturar sugestões de melhoria no Sprint Playbook e nos próprios capítulos.

---

## 4. Dívidas da S27 (técnicas, de produto, de UX, de operação)

> Idealmente, esta seção deve referenciar riscos e ações de `S27_G6_orr_summary.json`, bem como tasks S27-T-XXX que ficaram parcialmente cumpridas.

### 4.1 Formato de registro de dívidas

Cada dívida pode ser descrita no formato:

- **ID**: `DEBT-XXX` (opcional, mas ajuda a cruzar com backlog).  
- **Tipo**: `tecnica`, `produto`, `ux`, `operacao`, `processo`.  
- **Descrição**: texto claro e específico.  
- **Impacto**: `baixo`, `medio`, `alto` (em Programa 1 e/ou no roadmap).  
- **Urgência**: `baixa`, `media`, `alta`.  
- **Estado desejado**: como deveria ser quando a dívida estiver quitada.  
- **Sugestão de encaminhamento**: próximos passos, sprints ou épicos que deveriam tratar.  
- **Relacionamentos**: riscos (RISK-XXX), ações (ACT-XXX), tasks S27-T-XXX.

### 4.2 Dívidas técnicas

Exemplos típicos a avaliar (não preencher com placeholders, mas com casos reais da S27):

- pontos de acoplamento excessivo entre telas admin e APIs;  
- cobertura de testes insuficiente em áreas críticas;  
- scripts de gates com lógica duplicada ou frágil;  
- débito de refactor em componentes admin reutilizáveis.

### 4.3 Dívidas de produto & UX

Possíveis focos:

- fluxos de usuário que ficaram confusos ou longos demais;  
- telas onde a informação importante não é óbvia;  
- estados do sistema difíceis de diagnosticar a partir da UI admin;  
- oportunidades de simplificar ou consolidar telas/ações.

### 4.4 Dívidas de operação & processo

Aqui entram:

- gaps nos runbooks (seções vazias, caminhos não documentados);  
- ausência de playbooks para incidentes específicos;  
- lacunas na integração entre squad de desenvolvimento e operação (handoff de conhecimento, por exemplo);  
- necessidades de ferramentas auxiliares (scripts, dashboards, alertas) para uso real em Programa 1.

---

## 5. Conexão com riscos e ações do G6

Esta seção deve literalmente "puxar o fio" de G6:

- Para cada `RISK-XXX` presente em `S27_G6_orr_summary.json`, registrar:  
  - em qual categoria de dívida ele cai (se cair);  
  - se já foi ou será transformado em tarefa/sprint;  
  - se houve mudança de impacto/urgência após reflexão pós-ORR.

- Para cada ação `ACT-XXX`:  
  - anotar status (planejada, em andamento, concluída, abortada);  
  - referenciar em que parte do roadmap ou backlog ela foi parar;  
  - listar dependências relevantes.

O objetivo é evitar que riscos e ações fiquem isolados em G6; Cap.6 deve deixá-los claramente conectados ao plano futuro.

---

## 6. Impacto no roadmap (curto, médio e longo prazo)

### 6.1 Curto prazo (próximas 1–3 sprints)

Aqui entram ajustes imediatos, por exemplo:

- consolidar cobertura E2E de Debunker e de fluxos combinados Programa 1;  
- refinamentos críticos de UX em Admin v1 que surgiram da S27;  
- correções em contratos que ainda estão frágeis, mas não bloquearam o GO da S27.

Para cada item, deve existir uma indicação clara de:

- qual squad/área será responsável;  
- relação com dívidas e riscos mapeados;  
- relação com futuros épicos (se já existirem).

### 6.2 Médio prazo (próximos épicos relacionados)

Nesta subseção, a S27 projeta o que seus resultados significam para:

- a evolução do Admin v1 para outros programas (Programa 2, Programa 3, etc.);  
- a próxima onda de sprints em torno de Debunker, ingestão e verdade;  
- o amadurecimento do processo de ORR e dos gates.

Exemplos de itens possíveis:

- consolidar um "Admin v1.2" com base no feedback da S27;  
- criar um épico específico para "Debunker E2E + observabilidade", derivado dos riscos da S27;  
- estender runbooks e padrões de operação para novos módulos à medida que forem criados.

### 6.3 Longo prazo (visão Inspectah)

Por fim, a S27 deve se situar na visão maior:

- Como a maturidade de Admin v1 em Programa 1 aproxima o Inspectah da visão de produto (cockpit único, sistema de verdade, debunker robusto).  
- Que capacidades de plataforma começam a ficar possíveis a partir do que foi feito na S27 (por exemplo, replicar consoles admin como "template" para novos domínios).  
- Que riscos estruturais foram reduzidos e quais ainda exigem épicos dedicados.

Aqui não é preciso criar um roadmap completo, mas é importante registrar como a S27 mudou o mapa mental do projeto.

---

## 7. Recomendações e "se eu fosse a próxima sprint"

> Seção opinativa, mas baseada em evidências da S27.

Nesta parte, o squad da S27 pode registrar recomendações explícitas para quem pegar o bastão nas próximas sprints:

- quais temas **não deveriam ser adiados**;  
- quais experimentos ou provas de conceito valeria rodar antes de escalar Admin v1 para outros programas;  
- quais métricas observáveis (de uso real, performance, estabilidade) deveriam ser instaladas nos consoles admin assim que Programa 1 estiver em operação.

Formato sugerido:

- "Se eu fosse a próxima sprint focada em Debunker, faria X, Y, Z";  
- "Se eu fosse a próxima sprint focada em Admin v1 para Programa 2, começaria por A, B, C";  
- "Se eu fosse revisar o processo de ORR, ajustaria D, E, F".

Essa seção ajuda a próxima equipe a evitar repetir erros e aproveitar atalhos que a S27 já descobriu.

---

## 8. Como manter Cap.6 vivo após o fim da S27

Embora Cap.6 seja escrito no fechamento da sprint, ele não precisa (nem deveria) ser engessado:

- pequenas atualizações podem ser feitas conforme ações ACT-XXX forem sendo concluídas;  
- anotações podem ser adicionadas à medida que Programa 1 for usado em ambiente real e revelar learnings não previstos;  
- o documento pode ser referenciado em futuros Cap.6 de outras sprints como "base histórica" de Admin v1 em Programa 1.

Regra importante: mudanças que reescrevem a história (por exemplo, removendo dívidas graves sem justificativa) devem ser evitadas. Cap.6 é memória, não peça de marketing.

---

## 9. Resultado esperado deste capítulo

Com Capítulo 6 preenchido, a Sprint 27 entrega:

- um registro claro do que funcionou, do que doeu e do que ainda precisa ser feito;  
- um mapa organizado de dívidas, riscos e ações que nascem da S27;  
- ligações explícitas entre a S27, o Épico E26 e o roadmap futuro do Inspectah.

A partir daqui, qualquer pessoa que chegue ao projeto consegue entender, em poucos minutos de leitura, qual foi a contribuição real da S27 para o sistema como um todo — para muito além de "features entregues".

