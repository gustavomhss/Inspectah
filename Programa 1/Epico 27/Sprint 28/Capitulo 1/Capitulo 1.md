# Inspectah — Sprint 28 — Capítulo 1

## Contexto & Problemas a Resolver (E27.1 — CRUD & ON/OFF de Fonte)

---

### 1.1 Contexto e visão da sprint

**Programa e épico relacionados**  
- **Programa 1 — Consolidação & Consoles Full (E26–E32)**.  
- **Épico E27 — Fontes & Ingestão 2.0 em Modo Operação**.  
- **Sub-épico E27.1 — CRUD & ON/OFF de Fonte**.

**Estado atual antes da Sprint 28**  
1. O Inspectah já possui, a partir de S21 e S22:
   - Modelo de domínio para fontes (`Source`, `SourceType`) com estados básicos (`ACTIVE`, `DISABLED`, `DEPRECATED`) e tipos (ex.: `news_rss`, `http_json`, `price_feed`, `custom_api`).  
   - Motor de Ingestão 2.0 que agenda e executa ingestões por fonte, registrando `IngestionRun` com sucessos/falhas.  
   - API de admin `/admin/sources` criada na S21 e um console de fontes v1 funcional, porém acoplado à visão antiga de produto.
2. Após S25, o repositório está consolidado e existe sanidade global S1–S25 **possível**, mas com alertas claros de:
   - dívidas técnicas em módulos centrais (como fontes/ingestão),  
   - necessidade de sanidade contínua e gates vivos,  
   - cuidado extra com sprints estruturais (como E27) que sustentam futuros épicos de verdade, debunker, cockpits e evidence vault.
3. E26 está sendo trabalhado em paralelo, consolidando um **Design System Admin v1** que deve ser usado por todos os consoles — incluindo o de fontes.

**Foto do produto após a Sprint 28 (em 2 frases)**  
1. Qualquer fonte do Inspectah pode ser criada, editada, ativada e desativada **100% via console**, com regras claras, validação forte e sem necessidade de scripts de bastidor.  
2. O estado da fonte (`ACTIVE`/`DISABLED`/`DEPRECATED`) conversa de forma determinística com a Ingestão 2.0: desativar uma fonte realmente a retira do fluxo automático de ingestão; reativar faz a ingestão voltar de forma previsível.

**Conexão com o roadmap E26–E32**  
- Programa 1 declara que operação interna do Inspectah deve acontecer por **consoles consistentes**, não por scripts secretos. E27 é o braço de "Fontes & Ingestão em modo operação" dentro desse programa.  
- A Sprint 28 é o **primeiro bloco concreto** de E27: ela fixa o modelo de fonte, consolida a API de admin e transforma o console de fontes em uma ferramenta de operação real.  
- Sem S28 bem-feita, E27.2 (histórico & métricas), E27.3 (saúde & logs administrativos), E31 (Evidence Vault) e E32 (Case Cockpit) teriam uma base instável para responder perguntas aparentemente simples como:  
  - "Quais fontes alimentam este caso?"  
  - "Qual o estado atual de cada fonte?"  
  - "Quem desligou esta fonte e por quê?"  
  - "Por que esta fonte parou de mandar dados ontem à noite?"  
- S28 é, portanto, a sprint que transforma o módulo de fontes em **unidade de operação confiável**, sobre a qual o restante do Programa 1 pode se apoiar.

---

### 1.2 Problemas e hipóteses

**Problema 1 — CRUD desalinhado com o modelo atual de fonte**  
- O modelo de `Source` evoluiu ao longo de S21–S25 (campos, enums, domínios, criticidade, modos), mas:
  - a API `/admin/sources` manteve traços da versão antiga,  
  - o console de fontes v1 não expõe todos os campos relevantes,  
  - há risco de divergência entre o que o backend enxerga e o que o operador consegue manipular.  
- Na prática, cadastrar ou editar uma fonte ainda é uma operação com "nuances internas" que só quem conhece schema/código domina.

**Problema 2 — ON/OFF pouco previsível e risco de “duas verdades”**  
- O estado da fonte no banco (`ACTIVE`, `DISABLED`, `DEPRECATED`) nem sempre se reflete de maneira clara no que o scheduler da Ingestão 2.0 faz.  
- Há risco real de:
  - fonte marcada como `DISABLED` ainda sendo ingerida por jobs antigos/zumbis,  
  - fonte `ACTIVE` que deveria estar sendo ingerida mas ficou de fora por inconsistência de configuração.  
- Isso cria uma situação de **"duas verdades"**: uma no banco e outra no comportamento do sistema, o que é intolerável em um produto cujo tema central é confiabilidade de informação.

**Problema 3 — Console de fontes v1 é mais painel do que ferramenta de operação**  
- O console atual tende a ser:
  - mais técnico do que operacional,  
  - pouco alinhado ao Design System E26,  
  - fraco em deixar explícitos estado, modo, criticidade e domínio da fonte.  
- Operadores precisam de uma visão que responda rapidamente:
  - "quais fontes críticas estão ativas?",  
  - "qual fonte posso desligar sem quebrar nada?",  
  - "esta fonte faz parte de qual domínio/categoria?".

**Problema 4 — Dependência de scripts e conhecimento tribal**  
- Algumas operações ainda exigem terminal, scripts ou consulta a quem "sabe mexer" na parte de fontes/ingestão.  
- Isso é incompatível com a visão de Programa 1, que exige consoles como ponto de verdade operacional.

---

**Hipóteses da Sprint 28**

- **H1 — CRUD consolidado reduz erros e atritos de operação**  
  Se consolidarmos o modelo de `Source` (domínio + DB) e a API `/admin/sources` com validação forte, esperamos reduzir incidentes de fonte mal configurada, dados faltando e comportamentos inesperados na ingestão.

- **H2 — ON/OFF determinístico melhora previsibilidade e confiança**  
  Se o estado da fonte (`ACTIVE`/`DISABLED`/`DEPRECATED`) tiver invariantes claras e for respeitado pelo scheduler de Ingestão 2.0, então o operador poderá confiar que "desligar" uma fonte **sempre** a tira do fluxo e que "ligar" sempre a recoloca, sem exceções ocultas.

- **H3 — Console de fontes v2 diminui dependência de scripts e especialista**  
  Se o console de fontes v2 passar a expor claramente campos-chave (estado, modo, criticidade, domínio, tipo) e oferecer fluxos limpos de criação/edição/ON-OFF, então operadores não precisarão mais recorrer a scripts ou a "quem conhece o código" para tarefas rotineiras.

- **H4 — Sanidade de legado mantida evita regressões silenciosas**  
  Se os gates críticos de S21 e S22 forem rodados como parte da S28, então aumentamos a chance de evoluir o módulo de fontes sem quebrar contratos assumidos por outras partes do sistema.

**Tentativas anteriores relevantes**  
- S21 construiu o primeiro modelo de fontes e o console v1, num contexto em que o produto ainda não tinha a Ingestão 2.0 e o Programa 1 consolidado.  
- S22 introduziu a Ingestão 2.0, mas sem reformar completamente o console de fontes e o contrato de ON/OFF.  
- Essas entregas foram fundamentais, porém **parciais**: deram o esqueleto, mas não resolveram a experiência de operação ponta a ponta nem a relação precisa entre estado da fonte e scheduler.

A Sprint 28 se apoia nessas tentativas (modelo e motor já existem) para atacar explicitamente a lacuna: **tornar fontes operáveis via console, com ON/OFF previsível e sem dependência de conhecimento tribal**.

---

### 1.3 Domínios, personas e casos canônicos

**Domínios impactados**  
- **Domínio "Operação de Fontes & Ingestão"** (transversal a todos os demais: política, economia, mercado, dados oficiais, etc.).  
- Na prática, qualquer domínio que dependa de dados externos passa a ser afetado:
  - notícias (RSS de veículos),  
  - dados macroeconômicos (IBGE, bancos centrais, institutos de estatística),  
  - dados de mercado (preços de ativos, taxas de juros, câmbio),  
  - outros feeds especializados que serão integrados ao Inspectah.

**Personas centrais**  
1. **Operador de Ingestão / Source Operator**  
   - Cuida de cadastrar e manter fontes em funcionamento.  
   - Precisa desligar fontes problemáticas rapidamente e reativá-las com segurança.  
   - Não deve depender de terminal ou scripts.

2. **SRE / On-call de Dados**  
   - É acionado quando há incidentes (ex.: ingestão em loop, volume inesperado, fonte spamando lixo).  
   - Precisa de uma forma rápida de identificar e desligar a fonte certa, com rastreabilidade.

3. **Analista de Casos / Investigador** (persona secundária na S28)  
   - Investiga casos específicos e precisa saber **quais fontes** alimentaram determinado caso ou claim.  
   - A S28 não entrega a jornada completa do caso, mas prepara a base para que, em E31/E32, isso seja trivial.

---

**Casos canônicos (2–4) que a Sprint 28 precisa suportar bem**

**Caso A — Cadastrar uma nova fonte de notícias RSS**  
1. O operador recebe a demanda: "Adicionar o feed RSS do veículo X na pasta de fontes de política".  
2. Ele abre o Console de Fontes v2, clica em "Nova Fonte" e escolhe o tipo `news_rss`.  
3. Preenche: nome, descrição, URL, domínio (ex.: política), categoria (ex.: news), criticidade (ex.: HIGH), modo (AUTO) e cadência.  
4. Salva, vê a fonte na lista com estado `ACTIVE` e, em seguida, observa (via ingestão) que novos itens começam a aparecer.  
5. Em nenhum momento ele abre terminal, edita config manual ou mexe em banco.

**Caso B — Fonte quebrada ou passando spam, precisa ser desligada rapidamente**  
1. SRE/on-call recebe alerta de ingestão anômala (muitos erros ou conteúdo suspeito).  
2. Ele entra no Console de Fontes, filtra por domínio/categoria e encontra a fonte problemática.  
3. Clica em "Desativar"; o estado muda para `DISABLED` e o sistema registra `state_changed_at` e `state_reason`.  
4. Novas ingestões automáticas para essa fonte param de ocorrer (confirmado por logs/`IngestionRun`).  
5. Posteriormente, após correção, ele reativa a fonte via UI e a ingestão volta ao normal.

**Caso C — Manutenção planejada em fonte crítica**  
1. Uma fonte de dados macroeconômicos de alta criticidade precisa passar por manutenção do lado do fornecedor.  
2. O operador desativa a fonte antecipadamente, registrando a razão (manutenção programada).  
3. Durante o período de manutenção, a Ingestão 2.0 não tenta consumir dados dessa fonte, evitando alertas falsos.  
4. Ao final, o operador reativa a fonte e verifica que as ingestões automáticas normalizam.  
5. Registros de estado e timestamps permitem justificar qualquer lacuna temporária para times que dependem desses dados.

**Caso D — Corrigir uma fonte antiga sem quebrar ingestão**  
1. O operador percebe que uma fonte antiga foi cadastrada com config parcial (por exemplo, URL errada ou cadência absurda).  
2. Ele acessa o detalhe da fonte, ajusta os campos permitidos e salva.  
3. As invariantes de domínio bloqueiam qualquer mudança proibida (ex.: tentar reativar uma fonte `DEPRECATED`), evitando estados ilegais.  
4. O motor de ingestão passa a ler a nova config de forma previsível, sem ter que reinicializar manualmente jobs ou editar arquivos internos.

Esses casos definem o que "operar fontes" deve significar ao final da Sprint 28:
- operação via UI,  
- estados de fonte claros,  
- ON/OFF que se traduz em comportamento real da ingestão.

---

### 1.4 Fora de escopo e cortes

Para evitar escopo elástico, a Sprint 28 **não** vai atacar os seguintes pontos (mesmo que apareçam oportunidades tentadoras durante o desenvolvimento):

1. **Health score completo de fontes**  
   - Não entra nesta sprint o cálculo detalhado de saúde (scores, janelas temporais, thresholds) nem a UI de "semáforo" de saúde de fonte.  
   - Isso é responsabilidade de **E27.3 — Saúde da fonte & logs administrativos**.

2. **Histórico detalhado de ingestão por fonte**  
   - A S28 garante apenas a integração mínima (ON/OFF conversando com Ingestão 2.0).  
   - Telas específicas de histórico de `IngestionRun`, charts de sucesso/falha por período e análises mais ricas ficam para **E27.2**.

3. **Logs administrativos ricos e integração profunda com Evidence Vault**  
   - Nesta sprint, o foco é garantir que mudanças de estado tenham registro mínimo (`state_reason`, timestamps).  
   - O desenho de um log administrativo completo (quem fez o quê, com vínculo direto ao Evidence Vault) será consolidado em **E27.3/E31**.

4. **Reforma ampla da Ingestão 2.0**  
   - A S28 só toca o motor de ingestão na medida estritamente necessária para respeitar o estado da fonte e seu modo (`MANUAL`/`AUTO`).  
   - Refactors estruturais da Ingestão 2.0 (ex.: troca de engine, mudança de arquitetura de agendamento) são proibidos nesta sprint.

5. **Alterações profundas no Design System Admin v1**  
   - O console de fontes v2 é **consumidor** do Design System.  
   - Qualquer evolução estrutural do Design System acontece em E26; S28 apenas reclama se algo for insuficiente, registrando como input para E26.x.

6. **Jornadas completas de casos, debunker ou truth**  
   - A S28 prepara terreno para E31 (Evidence Vault & Explore) e E32 (Case Cockpit) ao consolidar fontes, mas **não** vai desenhar jornadas completas de caso, telas de Debunker ou Truth Console.  
   - Qualquer insight surgido durante a sprint sobre esses temas deve ser registrado como input para os épicos E29–E32, não como "escapadinha" de escopo.

**Regra de não desviar**  
- Sempre que surgir um item fora destes escopos explícitos, o padrão é:
  1. Registrar em uma lista de "Inputs para E27.2/E27.3/E29–E32" (Cap. 4.4 / backlog estruturado),  
  2. Não expandir o escopo da Sprint 28 para abraçar o item,  
  3. Manter foco em tornar verdade os estados-alvo associados a CRUD & ON/OFF de fonte.

Com isso, o Capítulo 1 fixa com precisão **por que** a Sprint 28 existe, **que dores** ela resolve, **para quem** e **o que fica de fora**, servindo de eixo para os capítulos seguintes (gates, arquitetura, execução).

