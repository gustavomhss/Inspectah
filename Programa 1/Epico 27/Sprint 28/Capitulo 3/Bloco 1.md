# Inspectah — Sprint 28
## Capítulo 3 — Bloco 1
### Vista panorâmica da arquitetura e princípios de desenho (E27.1 — CRUD & ON/OFF de Fonte)

---

#### 3.1.1 Propósito deste bloco

O Bloco 1 do Capítulo 3 responde à pergunta:

> "Como a Sprint 28 se encaixa na arquitetura geral do Inspectah, quais peças ela toca e quais princípios guiam todas as decisões de desenho?"

Não é um diagrama UML gigantesco nem um mergulho em detalhes de implementação — isso fica para os blocos seguintes. Aqui, o foco é construir um **mapa mental sólido** da arquitetura de E27.1 para que qualquer pessoa (dev, arquiteto, operador) entenda:

- quais **camadas** e **módulos** são afetados,  
- como as responsabilidades são divididas,  
- quais **linhas vermelhas** de acoplamento não podem ser cruzadas,  
- quais decisões arquiteturais desta sprint preparam o terreno para E27.2, E27.3 e E29–E32.

---

#### 3.1.2 Camadas principais impactadas pela Sprint 28

A arquitetura da Sprint 28 pode ser enxergada como quatro camadas principais, amarradas por uma quinta camada transversal de testes/gates:

1. **Domínio & Persistência (Core Sources)**  
   - Modelos de dados de fonte (`Source`, `SourceType`, enums de estado/modo/criticidade).  
   - Schema de banco e migrations.  
   - Invariantes de domínio (quem pode mudar de estado para o quê, o que é obrigatório, etc.).

2. **API de Administração de Fontes (Admin API)**  
   - Rotas `/admin/sources` expostas ao console e automações internas.  
   - DTOs/schemas para entrada/saída da API.  
   - Lógica de aplicação que orquestra o domínio sem vazar detalhes de persistência.

3. **Ingestão 2.0 & Scheduler**  
   - Módulos responsáveis por decidir **quais fontes** serão ingeridas e **quando**.  
   - Seleção de fontes elegíveis com base em `Source.mode` e `Source.state`.  
   - Criação de `IngestionRun` e interação com logs/observabilidade.

4. **Console de Fontes v2 (Frontend)**  
   - Tela principal de lista de fontes.  
   - Tela de criação/edição.  
   - Componentes de estado, criticidade e menu de ações.  
   - Integração com o Design System Admin v1.

5. **Testes, Gates & Evidências (Camada Transversal)**  
   - Suites de teste de domínio, API, integração e UI.  
   - Scripts `bin/s28_gX_*.sh`.  
   - Estrutura de scorecards e evidências (`out/evidence`, `out/scorecards`).

A Sprint 28 é, essencialmente, o **fio que costura essas camadas para que fontes sejam operáveis de ponta a ponta**.

---

#### 3.1.3 Fluxo de ponta a ponta: da UI ao Scheduler

Abaixo, a visão sequencial do fluxo típico envolvendo uma fonte em E27.1:

1. **Operador cria/edita uma fonte no Console de Fontes v2**  
   - Preenche formulário com: nome, tipo, domínio, categoria, config (ex.: URL), modo, cadência, criticidade, estado inicial.  
   - O console valida campos básicos (form-level) e envia o payload para a Admin API.

2. **Admin API recebe o comando**  
   - Endpoint `/admin/sources` (POST/PUT) recebe o payload.  
   - Converte o DTO em comandos de domínio (ex.: `create_source`, `update_source`, `change_source_state`).  
   - Aplica regras de negócio (invariantes de estado, validações por tipo).  
   - Persiste o `Source` via camada de repositório/ORM.

3. **Domínio & Persistência atualizam o modelo**  
   - O registro de `Source` no banco é criado/alterado com campos consolidados.  
   - `state`, `state_changed_at` e `state_reason` são atualizados quando há mudança de estado.

4. **Scheduler de Ingestão 2.0 consulta fontes elegíveis**  
   - Em cada ciclo, o scheduler busca fontes no banco com critérios como:  
     - `mode = AUTO`,  
     - `state = ACTIVE`,  
     - demais filtros herdados de S22 (ex.: janelas de tempo, flags adicionais).  
   - Para cada fonte elegível, agenda/gera um `IngestionRun`.

5. **Ingestão é executada e registrada**  
   - O pipeline de ingestão consome a fonte (ex.: faz request na URL RSS).  
   - O resultado (sucesso/erro) é registrado em `IngestionRun`.  
   - Logs e métricas alimentam a observabilidade.

6. **Operador gerencia ON/OFF via console**  
   - Se uma fonte estiver com problema, o operador usa o console para desativá-la (`DISABLED`).  
   - A Admin API aplica a mudança, atualiza `Source.state`.  
   - Em ciclos seguintes, o scheduler não seleciona mais essa fonte.

Esse fluxo consolidado é exatamente o que os gates G1–G4 e G6 precisam garantir como **verdade operacional**.

---

#### 3.1.4 Princípios de arquitetura adotados na Sprint 28

A Sprint 28 segue um conjunto explícito de princípios para evitar acoplamentos ruins e preparar o terreno para épicos futuros.

**Princípio P1 — Domínio de fontes como fonte de verdade única**  
- O estado de uma fonte (campos em `Source`) é a **única referência autorizada** para decidir:  
  - se a fonte deve aparecer em listagens,  
  - se ela pode ser ingerida,  
  - se pode ter certas ações aplicadas (ex.: reativar uma deprecada — ESSE é um exemplo de regra que deve ser bloqueada).  
- Scripts paralelos, flags soltas e “tabelinhas” não podem competir com o modelo `Source`.

**Princípio P2 — Admin API como fronteira oficial de mutação**  
- Nenhuma mudança relevante em fonte deve ser feita diretamente via scripts de banco em produção.  
- Toda alteração de estado e de configuração deve passar por rotas da Admin API, para:  
  - garantir que invariantes sejam aplicadas,  
  - permitir auditoria futura (via logs, Evidence Vault, etc.).

**Princípio P3 — Scheduler de Ingestão dependente apenas de projeções estáveis**  
- O scheduler não “opina” sobre regras de negócio além do necessário.  
- Ele recebe uma visão de “fontes elegíveis” baseada em critérios claros (`mode`, `state`, etc.) e age sobre isso.  
- Lógica sofisticada de health score, políticas de fallback e coisas do tipo pertencem a E27.2/E27.3, não a esta sprint.

**Princípio P4 — Console como primeira classe de operação**  
- O Console de Fontes v2 deixa de ser um painel decorativo e passa a ser o **ponto canônico de operação** de fontes.  
- Isso significa que qualquer operação que precise ser feita todos os dias (criar/editar/ligar/desligar) deve ser possível via UI, sem terminal.

**Princípio P5 — Design System Admin v1 como base de UI**  
- O console não inventa componentes paralelos: usa e alimenta o Design System Admin v1.  
- Se faltar um componente no design system, isso é input para E26, não desculpa para criar “Frankenstein UI”.

**Princípio P6 — Gates como contrato verificável de arquitetura**  
- Cada gate de S28 representa um aspecto arquitetural que **precisa** ser verdade:  
  - G1: modelo & schema,  
  - G2: API,  
  - G3: console,  
  - G4: ON/OFF × ingestão,  
  - G5: legado,  
  - G6: UX,  
  - G7: decisão final.  
- A arquitetura da sprint só é considerada estável quando todos esses pilares estiverem verdes.

---

#### 3.1.5 Fronteiras de acoplamento e o que é proibido

Para garantir que o sistema continue evoluindo de forma saudável, a Sprint 28 define algumas **linhas vermelhas**:

1. **Ingestão não fala diretamente com o console**  
   - O console conversa com Admin API.  
   - A Ingestão 2.0 conversa com o banco/modelo de domínio e, eventualmente, com serviços internos.  
   - Não existe (nem deve existir) chamada direta do scheduler para endpoints de frontend ou vice-versa.

2. **Console não consulta diretamente o banco**  
   - Toda leitura de fonte na UI passa por `/admin/sources`.  
   - Isso garante que o contrato de dados exibidos seja o mesmo para UI, automações e outros clientes internos.

3. **Scripts de gate não burlam as camadas**  
   - G4 (integração ON/OFF × ingestão), por exemplo, deve usar as rotas de Admin API para mudar estado da fonte — nada de mexer diretamente no banco para "forçar" um cenário de teste que não existe no mundo real.

4. **Nada de lógica de negócio no frontend**  
   - O console valida formulários para ajudar o usuário, mas o **juiz final** das regras de negócio é sempre o backend (domínio + API).  
   - Qualquer regra de validação importante deve ser replicada ou centralizada no backend.

Essas fronteiras existem para evitar que, daqui algumas sprints, o sistema vire um novelo de acoplamentos difíceis de desfazer.

---

#### 3.1.6 Preparando terreno para E27.2, E27.3 e E29–E32

A arquitetura da Sprint 28 não olha só para o agora. Ela precisa ser um **passo consistente** em direção a épicos mais sofisticados.

- **Para E27.2 — Histórico & métricas de ingestão**  
  - A definição clara de fontes elegíveis (`mode`, `state`, `criticality`, `domain`) permite construir dashboards por fonte, domínio, criticidade.  
  - A integração ON/OFF × Ingestão 2.0 deixa o terreno pronto para gráficos de tempo de inatividade por fonte.

- **Para E27.3 — Saúde da fonte & logs administrativos**  
  - Campos `state_changed_at` e `state_reason` em `Source` serão combustível para trilhas de auditoria.  
  - A obrigação de usar Admin API para mutações viabiliza logs mais ricos e acoplados ao Evidence Vault.

- **Para E29–E32 — Debunker, Truth Console, Case Cockpit**  
  - Quando esses módulos precisarem dizer “esta verdade foi baseada em fontes X, Y, Z, que estavam em tais estados”, eles dependerão de um modelo de fontes sólido e coerente.

A Sprint 28, portanto, é arquiteturalmente pensada como **fundação de operação de fontes** para todos os programas posteriores.

---

Com isso, o Bloco 1 do Capítulo 3 entrega a vista panorâmica da arquitetura de E27.1 na Sprint 28: camadas, fluxo ponta a ponta, princípios de desenho, fronteiras de acoplamento e alinhamento com o roadmap. Os próximos blocos descem o zoom para os detalhes de backend, ingestão, frontend, scripts de gates e filemap concreto.