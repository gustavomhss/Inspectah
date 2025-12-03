# Inspectah — Sprint 28
## Capítulo 5 — Bloco 1
### Objetivo, Escopo e Mapa Geral de Riscos & Dívida

---

#### 5.1.1 Papel deste bloco dentro da Sprint 28

O Capítulo 5 é o lugar onde a Sprint 28 assume, de forma explícita e adulta, que **nenhuma entrega séria vem sem risco nem sem trade-off**. 

Este Bloco 1 define:
- o **objetivo geral** do Capítulo 5,
- o **escopo** do que será tratado aqui (o que entra e o que fica para outros capítulos/sprints),
- um **mapa geral de riscos e dívidas** gerados ou revelados pela S28,
- a ligação direta com o Programa 1 e o Épico **E27.1 — CRUD & ON/OFF de Fonte**.

Os próximos blocos descem para o detalhe fino (listas de riscos, dívidas e backlog), mas este Bloco 1 é o quadro geral que orienta leitura e decisões do Conselho/ORR.

---

#### 5.1.2 Objetivo do Capítulo 5 na S28

Em termos práticos, o Capítulo 5 responde quatro perguntas centrais:

1. **Riscos**  
   Que riscos continuam existindo mesmo depois de todos os gates G0–G7 estarem em PASS?

2. **Dívida técnica**  
   Que pontos foram conscientemente deixados para depois (para não travar o épico) e precisam ser registrados como dívida técnica explícita?

3. **Backlog de continuidade**  
   Que itens nascem diretamente do que foi feito em S28 e precisam alimentar as próximas sprints de E27 (E27.2, E27.3, etc.)?

4. **Saúde pós-sprint**  
   Que rotinas de monitoração, sanity e revisão periódica são necessárias para garantir que o que foi entregue em S28 não se degrade com o tempo?

Se Capítulos 1–4 respondem “**o que** vamos fazer”, “**como** vamos fazer” e “**como provar** que fizemos”, o Capítulo 5 responde:

> “Quais são as consequências, os pontos fracos conhecidos e o plano para continuar evoluindo a partir daqui?”

---

#### 5.1.3 Escopo do Capítulo 5

O Escopo do Capítulo 5 é intencionalmente focado em **S28 dentro de E27.1**, mas olhando para frente:

Inclui:
- Riscos remanescentes especificamente ligados a:
  - modelo `Source`,  
  - Admin API `/admin/sources`,  
  - console de fontes v2 (frontend),  
  - ingestão 2.0 obedecendo `mode` + `state`,  
  - integração com sprints anteriores (S21/S22) e observabilidade básica.

- Dívida técnica que nasce **diretamente** das decisões de S28:
  - auditoria ainda básica de operações de fonte,  
  - validações pouco profundas por tipo de fonte,  
  - observabilidade ainda pouco refinada por fonte/estado.

- Backlog de continuidade **imediato**:
  - itens que naturalmente se encaixam nas próximas sprints do Épico E27 (E27.2 = S29, E27.3 = S30, etc.).

- Recomendações de monitoração e sanity pós-sprint:
  - rotinas semanais/mensais,  
  - possíveis watchers/alerts relacionados a fontes e ingestão.

Não inclui (por design):
- Todo o universo de riscos do Inspectah como um todo (Truth-DB, Sistema de Blocos, Debunker, Comitês, etc.).  
- Discussões macro de governança de verdade/fato — que pertencem às sprints de Programa Verdade & Interpretação (S23–S25 e além).  
- Detalhes de implementação de futuros módulos que apenas tangenciam fontes.

---

#### 5.1.4 Mapa geral de riscos — visão por categoria

Antes de entrar nos detalhes (nos próximos blocos), o Capítulo 5 organiza os riscos remanescentes da S28 em quatro grandes categorias:

1. **Riscos de Produto/Experiência (UX)**  
   Focados em como operadores reais interagem com o console de fontes e com o conceito de `Source` como entidade de primeira classe.

   Exemplos típicos (detalhados nos blocos seguintes):
   - console ainda não cobre todos os cenários avançados de operação (filtros, agrupamentos, visão por contexto),  
   - trilha de auditoria de ações do operador ainda limitada,  
   - validações de formulário simples demais para configurações complexas.

2. **Riscos Técnicos — Domínio & Backend**  
   Relacionados a evolução futura de `Source`, das migrations e da Admin API.

   Exemplos típicos:
   - futuras alterações de schema quebrarem contrato com API e ingestão,  
   - invariantes de domínio ficarem duplicadas ou divergentes entre modelo e rotas,  
   - migrações futuras em tabelas grandes se tornarem caras se não forem bem planejadas.

3. **Riscos Técnicos — Ingestão 2.0**  
   Relacionados à interação entre `mode` + `state` e o scheduler.

   Exemplos típicos:
   - lógica de elegibilidade duplicada fora do scheduler oficial,  
   - janelas de corrida entre mudança rápida de estado e execução do scheduler,  
   - observabilidade ainda insuficiente para detectar padrões sutis de erro.

4. **Riscos Operacionais**  
   Ligados à forma como humanos e processos usam (ou contornam) o que S28 entregou.

   Exemplos típicos:
   - uso de caminhos alternativos (scripts de banco, ferramentas paralelas) para mudar fontes,  
   - operadores ainda não treinados adequadamente sobre `mode`, `state`, `criticality`,  
   - confusão sobre impacto de desligar fontes críticas.

Esse mapa não substitui a lista detalhada de riscos; ele é um **quadro de categorias** que ajuda o time e o Conselho a entender rapidamente onde estão as fragilidades naturais do que foi entregue.

---

#### 5.1.5 Mapa geral de dívida técnica — visão por eixo

Da mesma forma, a dívida técnica explicitamente assumida em S28 é organizada em três eixos principais (que serão detalhados nos próximos blocos):

1. **Auditoria de operações de fonte**  
   - S28 registra estados e timestamps, mas ainda não possui um modelo completo de auditoria (`SourceActionLog`) com autor, contexto e vínculo com Truth-DB/Sistema de Blocos.

2. **Validações por tipo de fonte**  
   - S28 foca em validações genéricas; a inteligência de “tipo de fonte” (RSS, API JSON, etc.) ainda não se traduz em validações profundas nem em wizards guiados.

3. **Observabilidade orientada a fontes**  
   - S28 se apoia na infraestrutura de observabilidade existente, mas ainda não cria dashboards específicos nem métricas de saúde por fonte/estado/mode.

Essa dívida é considerada **intencional**: o time conscientemente escolheu não atacar esses pontos em S28 para manter o foco em consolidar o núcleo (modelo + API + console + ingestão obediente a ON/OFF). Os próximos blocos vão conectar cada eixo de dívida a itens de backlog em E27.2/E27.3.

---

#### 5.1.6 Ligação com E27.2/E27.3 e com a visão do Programa 1

S28 é a **primeira sprint "core"** do Épico E27 focada em tornar a fonte uma cidadã de primeira classe na operação do Inspectah. Ela estabelece o mínimo inegociável:

- Entidade `Source` bem definida.  
- Admin API coerente com domínio.  
- Console de Fontes v2 capaz de operar o básico.  
- Ingestão 2.0 obedecendo `mode` + `state` de forma determinística.

S28, porém, não tenta resolver tudo. Em vez disso, ela deixa o terreno pronto para:

- **E27.2 (ex.: Sprint 29)**: auditoria básica, validações mais ricas por tipo de fonte, métricas iniciais por fonte.  
- **E27.3 (ex.: Sprint 30)**: auditoria avançada integrada ao Truth-DB/Sistema de Blocos, wizards inteligentes de criação de fontes, painéis de operação mais avançados.

Em termos de Programa 1, este capítulo garante que S28 não é um ponto isolado, mas um **degrau bem definido** em uma escada maior: de um sistema que apenas "consome dados" para um ecossistema em que as fontes são operadas com disciplina, auditabilidade e alinhamento com a camada de verdade/fato.

---

Com este Bloco 1, o Capítulo 5 da Sprint 28 define o propósito, os limites e o mapa conceitual de riscos & dívidas. Nos próximos blocos, o documento desce para o nível de risco por categoria, dívida detalhada e backlog de continuidade, mantendo sempre o fio condutor com E27.2/E27.3 e com a visão maior do Programa 1.