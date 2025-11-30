# Épico E29 — Debunker v1 (Camada de Contestação & Revisão Operacional)

> Programa 1 — Consolidação & Consoles Full  
> Dono lógico: Squad Verdade & Contestação (Judea Pearl, Karl Popper, Michael Stonebraker, Peter Norvig, Percy Liang, Steve Jobs)

---

## 1. Identidade do épico

**Código:** E29  
**Nome curto:** Debunker v1  
**Programa:** Programa 1 — Consolidação & Consoles Full (S26–S32)  
**Status:** Em design  

**Resumo em uma frase:**

> E29 entrega a primeira versão operacional séria do Debunker do Inspectah: uma camada de contestação e revisão que recebe claims e evidências, passa por fluxos de agentes e humanos, produz decisões revisáveis e deixa um rastro auditável, sem ainda depender do Sistema de Blocos completo ou da ancoragem em blockchain.

---

## 2. Problema

Sem o Debunker v1, o Inspectah corre três riscos fatais:

1. **Risco epistemológico:** o sistema pode repetir, amplificar ou inventar besteiras sem uma camada clara de contestação, revisão e "desmontagem" de afirmações.
2. **Risco operacional:** mesmo que existam agentes que checam coisas, o processo fica difuso: ninguém sabe onde uma contestação entra, por quais etapas passa e quem assina embaixo da decisão final.
3. **Risco de confiança:** usuários internos e externos não têm como entender (ou auditar) por que o sistema marcou algo como verdadeiro, falso ou incerto.

Hoje (ou sem E29), contestar algo tende a ser:

- pouco estruturado (e-mails, tickets, comentários soltos),  
- sem trilha clara (quem reclamou, sobre o quê, com qual evidência, o que foi decidido),  
- sem integração com os fluxos de agentes definidos em E28,  
- sem console dedicado para operar fila de contestações.

E29 existe para dar forma concreta à **camada de contestação**: um lugar, um fluxo e um conjunto de decisões claros, antes da fase 2 de blockchain/Sistema de Blocos full.

---

## 3. Visão & Estados-alvo

### 3.1 Frase de visão

> Quando E29 estiver completo, qualquer contestação (vinda de humanos ou de agentes) entra em uma fila clara, percorre um fluxo de debunking definido, produz um parecer estruturado (com base em evidências) e deixa um registro auditável que pode ser consultado, reaberto ou usado em decisões futuras.

### 3.2 Estados-alvo (lista canônica)

Ao final de E29, será verdade que:

1. **Existe um modelo único de Contestação v1**, com campos obrigatórios (quem contesta, o que é contestado, qual é o claim, qual o contexto, evidências anexadas ou referenciadas).
2. **Existe um modelo único de Caso de Debunking v1**, que agrupa contestações relacionadas ao mesmo claim/tema e acompanha o ciclo de vida da análise (aberto, em análise, aguardando evidências, concluído, arquivado, etc.).
3. **O Console de Debunker v1 está operacional**, com:
   - fila de contestações/casos;  
   - filtros por criticidade, tema, origem, estado;  
   - visualização de detalhes (claim, histórico, evidências, decisões parciais, parecer final).
4. **Contestações percorrem fluxos de agentes definidos em E28**, com etapas explícitas de interpretação, classificação, análise e decisão, e cada passo deixa um rastro de output.
5. **O Debunker v1 produz decisões estruturadas** (ex.: "claim improvável", "claim não suportado", "claim suportado", "dados inconclusivos"), com justificativas e links para evidências.
6. **Existe um mecanismo mínimo de reabertura de casos**, permitindo que contestações novas ou evidências relevantes reativem um caso arquivado.
7. **Toda decisão de debunking é rastreável**, com informação sobre:
   - quais agentes participaram;  
   - quais humanos revisaram (se houver);  
   - quais dados/evidências foram consultados.

Esses estados são o contrato de E29; sprints posteriores devem selecionar subconjuntos deles como states-of-truth a serem tornados verdade.

---

## 4. Escopo IN / OUT

### 4.1 Escopo IN

E29 cobre, no mínimo:

- Definição do **modelo de Contestação v1** (schema lógico), incluindo:
  - claim contestado (texto, ID do fato/entrada original, tipo de claim);  
  - origem da contestação (usuário interno, agente automático, futura API pública, etc.);  
  - contexto (data, local/tema, entidade(s) citadas);  
  - evidências anexadas ou referenciadas (links, docs, dados);  
  - criticidade/severidade;  
  - estado da contestação.

- Definição do **modelo de Caso de Debunking v1**, agregando contestações correlatas ao mesmo claim/base factual.

- Ciclo de vida de Contestação e de Caso, com estados e transições claras.

- Criação do **Console de Debunker v1** (UI/Admin), aderente a E26, para operar:
  - fila de contestações;  
  - painel de casos;  
  - tela de detalhe de caso, com timeline, decisões e evidências.

- Integração com **fluxos de agentes** (E28):
  - definição de fluxos padrão de debunking (ex.: Intake → Interpretação → Checagem de evidências → Parecer preliminar → Parecer final);  
  - registro de execuções dos fluxos dentro do contexto de um Caso.

- Definição de **tipos de decisão de debunking v1** (taxonomia inicial) e como elas são registradas.

- Integração mínima com **Evidence Vault / fontes de dados** (sem exigir Sistema de Blocos completo): 
  - linkar evidências usadas em um caso;  
  - registrar metadados sobre de onde veio cada evidência.

### 4.2 Escopo OUT

E29 **não** cobre (por enquanto):

- Ancoragem automática das decisões em blockchain ou no Sistema de Blocos completo (isso é Programas posteriores / Fase 2).  
- Mecanismo completo de reputação para contestantes, debunkers ou fontes.  
- Governança avançada de decisões (ex.: comitês democráticos, votação on-chain, apelação complexa) — isso é Programa 5+.  
- Interface pública completa para entrada massiva de contestações por qualquer cidadão; aqui focamos em uso interno/operadores e, no máximo, integração restrita.

---

## 5. Personas & casos de uso

### 5.1 Personas

- **Contestante interno** — analista/revisor que levantou dúvida sobre um claim registrado pelo Inspectah.
- **Operator Debunker** — pessoa que vive na fila de contestações, organiza casos, acompanha fluxos de debunking e direciona decisões.
- **Debunker especialista** — profissional que entra em casos complexos para revisar ou complementar evidências e decisões automáticas.
- **Truth/Policy Owner** — responsável por políticas e critérios de decisão; utiliza os resultados do Debunker para ajustar regras futuras.
- **Usuário de consulta** — pessoa que precisa consultar o histórico de contestação e decisões sobre um claim.

### 5.2 Casos de uso principais

1. **Registrar uma contestação interna**
   - Um analista vê um claim que considera suspeito (ex.: "Inflação em 2024 foi X%" baseada em fonte duvidosa).  
   - Abre tela de contestação diretamente a partir do claim.  
   - Preenche campos: motivo da contestação, contexto, evidências iniciais.  
   - O sistema cria Contestação v1 e a associa/abre um Caso de Debunking.

2. **Trabalhar a fila de contestações**
   - Operator Debunker abre Console de Debunker.  
   - Vê fila de casos priorizados por criticidade, impacto, idade.  
   - Abre um caso, analisa contexto e decide disparar (ou já encontra disparado) um fluxo de debunking v1.  
   - Acompanha status das etapas, outputs de agentes e decide se precisa de revisão humana ou evidência adicional.

3. **Produzir um parecer final**
   - Após agentes rodarem e, se necessário, especialistas revisarem, o caso chega a um estado em que é possível decidir.  
   - Operator aplica um tipo de decisão (ex.: "não suportado", "inconclusivo", "provavelmente verdadeiro").  
   - Preenche justificativa estruturada e vincula evidências centrais.  
   - Caso passa para estado "concluído".

4. **Reabrir caso com nova evidência**
   - Nova informação relevante surge (ex.: dataset corrigido, estudo científico publicado).  
   - Contestante ou Operator anexa nova evidência a um caso concluído e aciona "reabrir".  
   - Caso volta para estado "em análise" com log claro dessa reabertura.

5. **Consultar histórico de contestação de um claim**
   - Usuário abre claim em outro console (Truth/Evidence/Case).  
   - Vê seção: "Contestações & Debunking".  
   - Clica e é levado para o Caso de Debunking associado, com timeline das contestações, fluxos, decisões e reaberturas.

---

## 6. Modelos conceituais centrais

### 6.1 Entidade Contestação v1

Campos lógicos mínimos:

- `id`  
- `claim_ref` (referência para o item contestado: notícia, fato, bloco, etc.)  
- `tipo_claim` (ex.: afirmação factual, estatística, previsão, opinião apresentada como fato)  
- `origem_contestacao` (`interno`, `agente`, `externo_restrito`)  
- `autor_id` (quando aplicável)  
- `descricao` (texto livre sobre o problema percebido)  
- `criticidade` (`alta`, `media`, `baixa`)  
- `evidencias_iniciais` (lista de refs)  
- `estado` (`nova`, `em_triagem`, `aceita_em_caso`, `rejeitada`)  
- `created_at`, `updated_at`.

### 6.2 Entidade Caso de Debunking v1

- `id`  
- `claim_ref`  
- `titulo` (resumo humano do caso)  
- `estado` (`aberto`, `em_analise`, `aguardando_evidencias`, `pronto_para_decisao`, `concluido`, `arquivado`)  
- `criticidade`  
- `owner` (responsável pelo caso)  
- `lista_contestacoes_ids`  
- `fluxo_debunking_id` (ref. para fluxo de E28)  
- `decisao_final_id` (se houver)  
- `reaberturas` (contador; histórico em entidade à parte)  
- `created_at`, `updated_at`.

### 6.3 Entidade Decisão de Debunking v1

- `id`  
- `caso_id`  
- `tipo_decisao` (exemplo de taxonomia inicial):  
  - `nao_suportado`;  
  - `provavelmente_falso`;  
  - `inconclusivo`;  
  - `parcialmente_verdadeiro`;  
  - `provavelmente_verdadeiro`.  
- `justificativa` (texto estruturado)  
- `evidencias_citadas` (refs para Evidence Vault / fontes)  
- `agentes_involvidos` (lista de refs para execuções de fluxo/etapa de E28)  
- `human_reviewers` (lista de IDs, se houver)  
- `timestamp_decisao`.

### 6.4 Entidades auxiliares

- **Reabertura de Caso**  
  - `id`, `caso_id`, `motivo`, `origem`, `novas_evidencias`, `timestamp`.  
- **Log de Evento de Caso** (timeline)  
  - criação, mudança de estado, anexos de evidência, execuções de fluxo iniciadas/concluídas, decisão final, reaberturas.

---

## 7. Requisitos funcionais

### 7.1 Console de Debunker v1 — visão geral

O console deve oferecer, minimamente:

- **Lista de Casos**:
  - colunas: ID, claim resumido, criticidade, estado, última atualização, owner, número de contestações, indicador de novas evidências.  
  - filtros por: estado, criticidade, tema, origem, data, owner.  
  - ordenação por: criticidade, recência de atualização, idade do caso.

- **Lista de Contestações** (aba ou visão dedicada):
  - mostra contestações recentes e seu vínculo com casos (novo caso vs caso existente).  
  - permite triagem: aceitar, agrupar em caso existente, rejeitar.

### 7.2 Detalhe do Caso

Tela de detalhe precisa conter:

- cabeçalho com claim, criticidade, estado, owner.  
- seção de contestações associadas (com autor, motivo, data).  
- seção de evidências vinculadas (com tipo, origem, links).  
- **timeline de eventos** do caso:  
  - criação, triagens, execuções de fluxo, outputs de etapas (resumo), decisões parciais, decisão final, reaberturas.  
- painel de fluxo de agente (via E28):  
  - qual fluxo está associado;  
  - status atual (não iniciado, em execução, completo);  
  - possibilidade de abrir detalhes de execuções.

### 7.3 Operações sobre Contestação e Caso

- Criar Contestação a partir de claim em outros consoles (botão "Contestar").  
- Triar Contestações não vinculadas:  
  - criar novo Caso;  
  - vincular a Caso existente;  
  - marcar como irrelevante/rejeitada (com motivo).  
- Criar/editar dados do Caso (título, criticidade, owner).  
- Alterar estado do Caso (de acordo com regras de transição).  
- Anexar/remover evidências (mantendo histórico).  
- Reabrir Caso com motivo e evidências novas.

### 7.4 Integração com Fluxos de Agentes (E28)

- Para cada Caso, deve ser possível:
  - associar um fluxo de debunking (do catálogo de fluxos de E28);  
  - iniciar execução de fluxo (manual ou automática em certas condições);  
  - acompanhar andamento (status, erros) dentro do detalhe do Caso.

- Execuções de fluxos associadas ao Caso devem registrar:
  - outputs resumidos por etapa;  
  - erros (se houver);  
  - timestamps.

### 7.5 Produção de decisão

- Interface para registrar **decisão de debunking v1**:
  - escolha do `tipo_decisao`;  
  - preenchimento de justificativa longa (texto estruturado, com campo para citar evidências);  
  - seleção de evidências centrais (com links);  
  - indicação de se houve revisão humana adicional.

- Ao registrar decisão:
  - Caso muda de estado para `concluido`;  
  - log de evento é criado com snapshot de contexto;  
  - outros consoles (Truth/Evidence/Case) podem mostrar o resultado (via integração futura de Programa 3/5).

---

## 8. Requisitos não funcionais

### 8.1 Observabilidade e rastreabilidade

- Cada mudança de estado de Contestação e Caso deve ser logada.  
- Cada execução de fluxo associada a um Caso deve ter logs estruturados.

Métricas mínimas:

- número de contestações por período, por origem;  
- número de casos abertos/fechados por período;  
- tempo médio de resolução de casos (por criticidade);  
- distribuição de tipos de decisão (quantos `nao_suportado`, `inconclusivo`, etc.).

### 8.2 Consistência com E26

- Console de Debunker é console admin exemplar:
  - usa layout e componentes de E26;  
  - segue a gramática de estados (loading, vazio, erro, crítico);  
  - usa o mesmo padrão de filtros, ações, tabelas.

### 8.3 Segurança & privacidade

- Campos sensíveis (ex.: identificação de pessoas físicas em contestação) devem respeitar políticas de acesso do Inspectah.  
- Logs não devem vazar dados pessoais desnecessários; referências a evidências devem ser feitas via IDs quando possível.

---

## 9. Métricas de sucesso do épico

Indicadores para saber se E29 está entregando valor real:

- **Tempo médio de resolução de casos críticos**: redução em relação a baseline manual.  
- **Percentual de contestações triadas e vinculadas a casos** (vs perdidas em ruído).  
- **Cobertura de claims sensíveis com casos de debunking** quando há contestação.  
- **Número de decisões revisitadas por falta de rastreabilidade**: deve cair após E29.  
- Feedback qualitativo de operadores e debunkers sobre clareza do Console e fluxos.

---

## 10. Decomposição em sprints

### 10.1 Entregas sugeridas

- **E29.1 — Modelo de Contestação & Caso + API básica**  
  - Schemas e entidades (Contestação, Caso, Decisão, Logs);  
  - endpoints CRUD básicos;  
  - integração mínima com claims de outros consoles (IDs).

- **E29.2 — Console de Debunker v1 (fila + detalhe)**  
  - Lista de casos e contestações;  
  - tela de detalhe com timeline, evidências, operações básicas;  
  - adesão a E26.

- **E29.3 — Integração com Fluxos de Agentes + Decisão Estruturada**  
  - vínculo Caso ↔ Fluxo (E28);  
  - visualização de execuções;  
  - registro de decisão final, reaberturas, métricas.

### 10.2 Relação com sprints S26–S32

- S26–S27: podem focar em E29.1, associando contestações simples a claims.  
- S28–S29: entregam Console de Debunker v1 (E29.2), integrado com os consoles de E26.  
- S30–S32: ligam E29.3 a fluxos (E28) e refinam operação diária do Debunker.

---

## 11. Riscos, decisões e anti-objetivos

### 11.1 Riscos

- **Complexidade de política cedo demais:** tentar resolver todas as nuances de verdade, governança e apelação já em v1 e paralisar o épico.  
- **UI sobrecarregada:** console que mostra tudo ao mesmo tempo (fluxo, logs brutos, evidências inteiras), tornando a operação impraticável.  
- **Dependência forte de sistemas futuros** (Truth-DB full, blockchain) bloqueando o valor imediato.

### 11.2 Decisões de design esperadas

- Manter Debunker v1 focado em **processo operacional claro** (fila → fluxo → decisão → rastro), não na perfeição filosófica da verdade.  
- Tratar decisões como **revisáveis**: sempre com possibilidade de reabertura, em vez de pretender infalibilidade.  
- Começar com uma **taxonomia simples de decisões** e evoluir depois.

### 11.3 Anti-objetivos

- E29 **não** tenta ser um tribunal supremo absoluto de verdade; é a primeira camada robusta de contestação e revisão.  
- E29 **não** inclui reputação pesada, staking ou punições automáticas (isso é Fase 2+).  
- E29 **não** dá poderes mágicos a agentes sem supervisão; humanos continuam no loop em casos críticos.

---

## 12. Conexão com outros épicos e programas

- **E26 — Console Full & Coerência de UI/Admin:** Console de Debunker é caso de teste perfeito para a gramática de consoles.  
- **E27 — Fontes & Ingestão 2.0:** muitas contestações podem estar ligadas a dados de fontes específicas; insights de E29 alimentam ajustes em fontes e ingestão.  
- **E28 — Fluxo de Agentes Configurável v1:** Debunker v1 é cliente direto dos fluxos de agentes — ao menos um dos primeiros fluxos será o fluxo de debunking.  
- **E30–E32 (Truth Console, Evidence Vault, Case Cockpit):**  
  - Truth Console vai precisar mostrar estado de contestação;  
  - Evidence Vault serve como fonte de evidências para casos;  
  - Case Cockpit integra resultado de debunking em narrativas maiores.  
- **Programas futuros (Governança & Truth Ops, Sistema de Blocos)**: E29 limpa o terreno para que, no futuro, decisões do Debunker sejam promovidas para blocos, âncoras e políticas de verdade.

---

## 13. Notas finais

Este documento define a visão, escopo, modelos e contratos do **Épico E29 — Debunker v1**.

Qualquer sprint que mexer com contestação, fila de casos, decisões de debunking ou console correspondente deve usar este épico como referência direta:

- Cap.1: problemas e states-of-truth de E29 sendo atacados.  
- Cap.2: gates e scorecards específicos para Debunker (ex.: integridade de casos, rastreabilidade mínima, métricas de resolução).  
- Cap.3: impacto em schemas de Contestação/Caso/Decisão, APIs e filemap.  
- Cap.4: tasks que implementam E29.1/E29.2/E29.3, integradas a fluxos de E28.

Mudanças profundas na forma de contestar, revisar ou decidir sobre claims devem ser refletidas neste épico antes de serem empurradas para novas sprints ou camadas de governança/truth mais avançadas.