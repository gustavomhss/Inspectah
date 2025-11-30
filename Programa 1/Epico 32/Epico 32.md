# Épico E32 — Case Cockpit v1 (Casos & Narrativas de Verdade)

> Programa 1 — Consolidação & Consoles Full  
> Dono lógico: Squad Casos & Narrativas  
> (Judea Pearl, Karl Popper, Michael Stonebraker, Peter Norvig, Percy Liang, Steve Jobs, Andy Grove, Gerald Weinberg)

---

## 1. Identidade do épico

**Código:** E32  
**Nome curto:** Case Cockpit v1  
**Programa:** Programa 1 — Consolidação & Consoles Full (S26–S32)  
**Status:** Em design  

**Resumo em uma frase:**

> E32 entrega o primeiro Case Cockpit operacional do Inspectah: uma interface única para criar, acompanhar e resolver "casos" complexos (investigações, dossiês, narrativas de verdade), costurando Proposições (E30), Evidências (E31), Casos de Debunking (E29), Fontes (E27) e Fluxos de Agentes (E28) em uma visão coerente, auditável e trabalhável.

---

## 2. Problema

Mesmo com Debunker v1 (E29), Truth Console (E30) e Evidence Vault (E31), ainda falta uma peça crítica no Inspectah:

- Verdade e evidência são expostas principalmente "por unidade" (por claim, por proposição, por evidência), mas investigações reais acontecem em **casos**: conjuntos de claims, atores, eventos e evidências conectados por uma narrativa.  
- Sem um Case Cockpit, operadores acabam montando dossiês em ferramentas externas (docs soltos, planilhas, prints, threads de chat), quebrando rastreabilidade e integração com o restante do sistema.  
- Não existe um lugar padrão para responder perguntas como:
  - "Qual é o estado atual desta investigação?"  
  - "Quais claims ainda estão pendentes de checagem?"  
  - "Quais evidências já temos, quais estão fracas, quais vieram de fontes contestadas?"  
  - "Quem fez o quê neste caso, em que ordem e com qual decisão?"  
- A ausência de uma visão "por caso" também dificulta priorização: temas críticos (ex.: eleição, desastre ambiental, crise econômica) acabam espalhados em múltiplas Proposições e Casos de Debunking isolados, sem cockpit único.

E32 existe para resolver isso: criar o **Case Cockpit v1**, que é a camada de trabalho diário para investigações e casos complexos, costurando todas as peças de Programa 1 em uma narrativa operacional.

---

## 3. Visão & Estados-alvo

### 3.1 Frase de visão

> Quando E32 estiver completo, qualquer investigador autorizado poderá abrir o Case Cockpit, ver a lista de casos em andamento, entrar em um caso específico e enxergar, em uma única tela evolutiva, os claims, proposições, evidências, contestações, decisões, tarefas e mudanças de estado que compõem aquela investigação — com clareza sobre o que já foi resolvido e o que ainda está pendente.

### 3.2 Estados-alvo (lista canônica)

Ao final de E32, será verdade que:

1. Existe um **modelo único de Caso v1**, representando investigações/narrativas de verdade que podem envolver múltiplas Proposições, claims, evidências, fontes e decisões.  
2. Existe um **Case Cockpit v1 (UI/Admin)**, aderente a E26, que permite:
   - listar casos, com estado, prioridade, dono e progresso;  
   - abrir caso e ver visão consolidada (timeline, tarefas, blocos de informação, mapas de claims/evidências).  
3. Todo Caso v1 pode ser ligado a:
   - um conjunto de Proposições (E30);  
   - Casos/Decisões de Debunking relevantes (E29);  
   - Evidências (E31);  
   - Fontes (E27) e eventos de ingestão relevantes;  
   - fluxos de agentes utilizados na investigação (E28).
4. Existe um **ciclo de vida claro de Caso v1**, com estados como: `aberto`, `em_analise`, `aguardando_terceiros`, `aguardando_dados`, `pronto_para_sintese`, `concluido`, `arquivado`.  
5. É possível **atribuir ownership e tarefas** dentro de um caso (mesmo que v1 seja simples), permitindo ver quem é responsável pelo quê e qual é o próximo passo.  
6. Cada caso possui **uma narrativa de síntese**, isto é, um resumo estruturado (texto + links para Proposições e Evidências centrais) que representa o entendimento atual do Inspectah sobre o tema daquele caso.  
7. Todas as ações importantes dentro de um caso (mudança de estado, anexos de evidência, criação de Proposição, decisões de Debunking relevantes) ficam registradas em uma **timeline auditável de eventos de caso**.

---

## 4. Escopo IN / OUT

### 4.1 Escopo IN

E32 cobre, no mínimo:

- Definição do **modelo de Caso v1**, com:
  - identificação do caso;  
  - título, descrição, escopo (tema, período, entidades envolvidas);  
  - estado, prioridade, owner;  
  - ligações com Proposições, Casos de Debunking, Evidências, Fontes;  
  - narrativa de síntese (texto estruturado, em v1 simples, mas formal).  

- Definição de **tarefas de caso v1** (tasks internas), representando trabalhos granularizados dentro do caso (ex.: "verificar série de dados do IBGE", "checar discurso do ministro X", "avaliar contestação Y").

- Definição de **timeline de eventos de caso**, incluindo:
  - mudanças de estado do caso;  
  - criação/remoção de ligações (Proposição, Evidência, Caso de Debunking);  
  - criação/conclusão de tarefas;  
  - eventos derivados de outros módulos (ex.: decisão de Debunking relevante).  

- Criação do **Case Cockpit v1 (UI/Admin)**, aderente a E26, com:
  - lista de casos;  
  - filtro por estado, prioridade, tema, owner;  
  - detalhe de caso, com abas/seções: visão geral, claims, Proposições, Evidências, Debunking, tarefas, timeline, síntese.  

- Integrações mínimas com E27–E31:
  - criação de caso a partir de contestações, clusters de claims ou eventos críticos;  
  - navegação cruzada entre Case Cockpit e Debunker, Truth Console, Evidence Vault.

### 4.2 Escopo OUT

E32 não cobre, nesta fase:

- Motor de workflow complexo com SLA, escalonamento multi-time, swimlanes e Kanban full; v1 foca em uma camada leve de tasks/ownership dentro do caso.  
- UX avançada de visualização tipo "knowledge graph" em 3D; v1 pode usar listas, tabelas, cards e visualizações simples.  
- Publicação externa de dossiês como produto final; foco é console interno de trabalho.  
- Lógica de reputação de casos ou ranking global de temas por impacto político/econômico (isso fica para Programas de governança/priorização).

---

## 5. Personas & casos de uso

### 5.1 Personas

- **Investigador de Casos** — opera casos complexos, conectando claims, evidências e decisões.  
- **Case Owner / Editor** — responsável por garantir que um caso avance, coordenando tasks e síntese.  
- **Debunker / Analista de Verdade** — precisa ver cases nos quais seus Casos de Debunking são peças.  
- **Gestor/Stakeholder** — quer visão macro de casos em andamento, estado e sínteses finais.

### 5.2 Casos de uso principais

Abrir um novo caso a partir de um evento crítico:

- Um conjunto de contestações e claims sobre um tema (ex.: "dados de desmatamento na região X") explode.  
- Operador decide que isso é grande o suficiente para virar um Caso.  
- No Debunker ou Truth Console, aciona "Criar caso" agrupando Proposições e contestações relacionadas.  
- Case Cockpit cria Caso v1 com título, escopo e links iniciais.

Trabalhar um caso durante dias/semanas:

- Investigador entra no Case Cockpit e abre o caso.  
- Vê:
  - lista de claims/Proposições associadas;  
  - Casos de Debunking ativos;  
  - evidências já registradas;  
  - tarefas pendentes;  
  - timeline dos últimos eventos.  
- Cria novas tarefas, anexa evidências, aciona fluxos de Debunking quando necessário.  
- Atualiza estado do caso conforme avança (ex.: de `em_analise` para `pronto_para_sintese`).

Produzir síntese de um caso:

- Quando o caso já tem um conjunto robusto de Proposições e decisões, o Case Owner aciona a aba "Síntese".  
- Escreve (ou edita com ajuda de agentes) uma síntese estruturada que:
  - descreve o contexto;  
  - lista os principais claims e suas Posições de Verdade;  
  - destaca as evidências centrais, com links;  
  - resume as decisões de Debunking chave.  
- Marca o caso como `concluido`, mantendo a timeline e a síntese disponíveis para consulta.

Consultar histórico de um caso:

- Meses depois, alguém quer saber "o que o Inspectah concluiu no caso do escândalo X".  
- Abre Case Cockpit, busca pelo caso, entra, lê a síntese e, se precisar, desce para a timeline, Proposições e evidências.

---

## 6. Modelos conceituais centrais

### 6.1 Caso v1

Campos lógicos mínimos:

- id  
- titulo  
- descricao  
- escopo_tema (ex.: `eleicoes`, `saude_publica`, `economia`, etc.)  
- escopo_temporal (intervalo ou período)  
- entidades_chave (lista de IDs de entidades relevantes)  
- estado (`aberto`, `em_analise`, `aguardando_terceiros`, `aguardando_dados`, `pronto_para_sintese`, `concluido`, `arquivado`)  
- prioridade (`alta`, `media`, `baixa`)  
- owner (pessoa/time responsável)  
- created_at, updated_at  
- data_fechamento (quando `concluido`/`arquivado`)  
- sintese_atual_id (ref para síntese mais recente).

### 6.2 Ligação de Caso v1

Liga Caso a objetos centrais do Inspectah:

- id  
- caso_id  
- tipo_alvo (`proposicao`, `caso_debunking`, `decisao_debunking`, `evidencia`, `claim`, `fonte`, etc.)  
- alvo_id  
- papel (`claim_principal`, `claim_secundario`, `evidencia_central`, `evidencia_de_contexto`, `contexto_politico`, etc.)  
- created_at.

### 6.3 Task de Caso v1

Representa trabalho granular dentro de um caso.

- id  
- caso_id  
- titulo  
- descricao  
- estado (`aberta`, `em_andamento`, `bloqueada`, `concluida`, `cancelada`)  
- responsavel_id (quando aplicável)  
- prazo (opcional)  
- created_at, updated_at.

### 6.4 Evento de Caso v1 (timeline)

- id  
- caso_id  
- tipo_evento (`criacao`, `mudanca_estado`, `ligacao_criada`, `ligacao_removida`, `task_criada`, `task_concluida`, `evidencia_anexada`, `decisao_debunking_relevante`, `sintese_atualizada`, etc.)  
- ref_origem (ID no módulo correspondente, se aplicável)  
- autor_id (quando houver ação humana)  
- detalhes (resumo textual)  
- timestamp.

### 6.5 Síntese de Caso v1

- id  
- caso_id  
- texto_sintese (estrutura mínima: contexto, claims centrais, posições de verdade, evidências centrais, conclusões)  
- data_criacao  
- autor_id (quando houver)  
- versao (para histórico de sínteses, se necessário).  

---

## 7. Requisitos funcionais

### 7.1 Case Cockpit — Lista de casos

- Lista com colunas: título, tema, estado, prioridade, owner, última atualização, número de claims/Proposições, número de evidências.  
- Filtros por estado, tema, prioridade, owner, período de criação/atualização.  
- Ordenação por prioridade, recência, idade.

### 7.2 Detalhe de caso — Visão geral

- Cabeçalho com título, descrição curta, estado, prioridade, owner, escopos (tema, temporal, entidades).  
- Indicadores rápidos:  
  - número de claims/Proposições;  
  - número de evidências;  
  - número de Casos de Debunking;  
  - tasks abertas vs concluídas.

- Ações: mudar estado do caso, ajustar prioridade, trocar owner.

### 7.3 Abas/seções internas

É aceitável v1 organizar em seções:

- **Claims & Proposições**: lista de Proposições associadas (E30) com estado de verdade atual.  
- **Debunking**: lista de Casos de Debunking/Decisões relevantes (E29), com status e links.  
- **Evidências**: lista de evidências do Evidence Vault (E31) ligadas ao caso, com papel.  
- **Tasks**: lista de tasks com estado e responsável.  
- **Timeline**: eventos do caso em ordem cronológica.  
- **Síntese**: texto estruturado da síntese atual, com histórico básico (quem criou, quando atualizou).

### 7.4 Operações típicas

- Criar caso manualmente (a partir do Case Cockpit) ou a partir de outros módulos (Debunker, Truth, ingestão de eventos críticos).  
- Adicionar/remover ligações de objetos ao caso (Proposição, Evidência, Caso de Debunking, etc.).  
- Criar/editar/concluir tasks do caso.  
- Atualizar estado do caso com registro de evento.  
- Criar/atualizar síntese (manual ou com auxílio de agentes, v1 pode ser manual com campo de texto estruturado).

### 7.5 Integração com outros consoles

- De um Caso de Debunking, possibilidade de "Adicionar a caso" ou "Ver casos relacionados".  
- De uma Proposição no Truth Console, ação de "Ver casos relacionados".  
- De uma Evidência no Evidence Vault, seção "Usada em casos" com links para o Case Cockpit.  
- Do Case Cockpit, links diretos para detalhes em Debunker, Truth Console, Evidence Vault, Fontes, etc.

---

## 8. Requisitos não funcionais

### 8.1 Consistência & integridade

- Nenhuma mudança importante em Caso, Task ou ligações deve ocorrer sem gerar Evento de Caso na timeline.  
- IDs e ligações devem ser estáveis e compatíveis com futuras promoções a Sistema de Blocos.

### 8.2 Observabilidade

Métricas mínimas:

- número de casos abertos por estado/prioridade;  
- tempo médio de ciclo de casos (abertura → conclusão);  
- número médio de Proposições/Evidências por caso (dá noção de complexidade);  
- taxa de casos reabertos (indicador de instabilidade ou revisões frequentes).

### 8.3 Usabilidade

- Case Cockpit deve ser utilizável por humanos sob carga cognitiva alta (casos complexos):  
  - layout limpo;  
  - seções bem separadas;  
  - sem sobrecarga visual desnecessária.  
- Deve ser fácil responder: "o que falta para este caso ser concluído?" a partir da tela.

### 8.4 Consistência com E26

- Reaproveitar componentes de tabela, cards, filtros e padrões de estados (loading, vazio, erro, crítico) definidos em E26.  
- Manter comportamento consistente com Debunker/Truth/Evidence.

---

## 9. Métricas de sucesso do épico

- Tempo médio para montar um dossiê consistente sobre um tema relevante, comparado com baseline (sem Case Cockpit).  
- Percentual de Casos de Debunking e Proposições críticas que estão vinculados a algum Caso (evitando investigações órfãs).  
- Adoção do Case Cockpit por analistas/investigadores (número de casos ativos, acessos, uso de tarefas e síntese).  
- Redução de dependência de documentos externos soltos para organizar investigações (feedback qualitativo dos times).

---

## 10. Decomposição em sprints

### 10.1 Entregas sugeridas

- **E32.1 — Modelo de Caso v1 + Ligações + Timeline**  
  - Entidades Caso, Ligação de Caso, Task de Caso, Evento de Caso, Síntese;  
  - APIs internas para criar/editar casos, tasks, ligações.

- **E32.2 — Case Cockpit v1 (lista + detalhe básico)**  
  - UI/Admin com lista de casos e detalhe com abas principais;  
  - operações básicas de criação/edição de caso, tasks, timeline;  
  - primeira integração com Proposições e Casos de Debunking.

- **E32.3 — Integrações profundas & síntese estruturada**  
  - ligações com Evidence Vault e Truth Console;  
  - fluxo de criação/edição de síntese dentro do cockpit;  
  - refinamentos de UX para suportar casos mais complexos.

### 10.2 Relação com sprints S26–S32

- S26–S27: podem iniciar E32.1 em paralelo à base de E29–E31 (modelagem de caso e ligações).  
- S28–S29: foco em E32.2, entregando Case Cockpit utilizável para alguns casos piloto.  
- S30–S32: E32.3 aprofunda integrações, síntese e prepara terreno para Programas futuros (Sistema de Blocos, governança).

---

## 11. Riscos, decisões e anti-objetivos

### 11.1 Riscos

- Tentar fazer do Case Cockpit um "Jira + Notion + Miro" de uma vez só, perdendo foco e atrasando valor v1.  
- Duplicar funcionalidades de Debunker/Truth/Evidence, em vez de integrá-las; o cockpit deve costurar, não replicar.  
- UX confusa que não deixa claro o que é claim, Proposição, Caso de Debunking, Caso (cockpit) e Evidência.

### 11.2 Decisões de design esperadas

- Tratar Case Cockpit como **camada de orquestração humana e narrativa**, não como substituto dos consoles de baixo nível.  
- Manter fluxos de navegação claros: caso → proposição → evidência → debunking e volta.  
- Focar em responder bem duas perguntas:  
  - "Qual é o estado deste caso?"  
  - "O que falta para este caso ser concluído?".

### 11.3 Anti-objetivos

- E32 não é um sistema de tickets genérico; ele é um cockpit específico para casos de verdade/investigação.  
- E32 não substitui ferramentas de gestão de projeto da organização; ele organiza o *conteúdo* e o *estado* das investigações de verdade.  
- E32 não tenta, em v1, ser a interface pública de relatórios finais; é ferramenta interna de trabalho.

---

## 12. Conexão com outros épicos e programas

- **E26 — Console Full & Coerência de UI/Admin:** Case Cockpit deve ser um dos consoles mais bem acabados, ajudando a validar a gramática geral de consoles.  
- **E27 — Fontes & Ingestão:** casos podem focar em problemas de fontes específicas; links para fontes ajudam a investigar raiz de inconsistências.  
- **E28 — Fluxos de Agentes:** casos podem acionar fluxos específicos ou analisar outputs de fluxos; eventos de fluxo relevantes podem aparecer na timeline do caso.  
- **E29 — Debunker v1:** Casos de Debunking frequentemente são subpeças de um Caso maior; integrações precisam ser suaves.  
- **E30 — Truth Console v1:** Case Cockpit consome Proposições e Posições de Verdade para construir narrativa de caso.  
- **E31 — Evidence Vault v1:** é de onde vêm e onde se registram as evidências centrais de um caso.  
- **Programas de Fase 2 (Sistema de Blocos, Blockchain, Governança):** muitos casos importantes podem futuramente gerar blocos de alto impacto (fatos consolidados, dossiês ancorados, políticas derivadas); E32 fornece a narrativa e o rastro operacional que serão "destilados" em blocos.

---

## 13. Notas finais

Este documento define a visão, escopo, modelos e contratos do **Épico E32 — Case Cockpit v1 (Casos & Narrativas de Verdade)**.

Sprints que mexerem com investigação, dossiês, visão "por caso" ou coordenação de trabalho em torno de verdade devem usar E32 como referência direta no Sprint Playbook (Cap.1–Cap.4), deixando claro quais partes de E32.1, E32.2 ou E32.3 estão sendo tornadas verdade em cada ciclo.

