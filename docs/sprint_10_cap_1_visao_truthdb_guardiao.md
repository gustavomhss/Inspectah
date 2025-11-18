# Sprint 10 — Capítulo 1 — Truth-DB & Guardião de Blocos (v3)

Versão revisada com foco em concisão, exemplo concreto bem ancorado e fronteiras nítidas de escopo. Este capítulo é a visão oficial da Sprint 10.

---

## 0) TL;DR — o que a S10 entrega

A Sprint 10 faz três coisas essenciais:

1. Cria a **Truth-DB** do Inspectah: uma base de verdades versionadas, auditáveis e preparadas para blockchain.
2. Transforma o GPT em **Guardião de Blocos**: ele não só responde, mas decide que fatos entram na Truth-DB e como evoluem.
3. Garante que toda decisão passe por uma **camada mecânica de validação**, que aplica apenas ações válidas e deixa uma trilha de eventos de domínio.

Se, ao final da sprint, qualquer pessoa conseguir pegar um tema piloto e responder claramente:

- o que o Inspectah considera verdade agora;
- como essa verdade chegou a esse estado (linha do tempo);
- em quais evidências se baseou;

…então a S10 cumpriu seu papel.

---

## 1) Posição no roadmap e donos

Nome oficial: **Inspectah — Sprint 10 — Truth-DB & Guardião de Blocos**

Relação com as outras sprints:

- **S9**: prova que ingestão + decisão funcionam em cenários de demonstração.
- **S10**: cristaliza essas decisões em uma Truth-DB, com estados, versões e trilhas de evidência.
- **S11**: ancora essas verdades em blockchain e introduz contestação.
- **S12**: escala ingestão contínua e constrói os primeiros exploradores/experiências para usuários externos.

Donos principais:

- PO / visão de produto: Gustavo.
- Modelo de dados / consistência: "banca Kleppmann + Lamport".
- Experiência de decisão e relatórios: "banca Jobs + Kay".
- Qualidade, invariantes e governança: "banca Knuth + Vitalik + DNA/Leassons".

---

## 2) Problema de fundo — por que a Truth-DB existe

Hoje o Inspectah já consegue:

- ingerir dados de múltiplas fontes;
- normalizar, agrupar e enriquecer;
- usar GPT para tomar decisões sobre temas específicos;
- demonstrar cenários ponta a ponta.

O que ainda falta é um **lugar oficial onde a verdade mora**.

Sem a Truth-DB:

- cada resposta do GPT é efêmera;
- não existe ID estável de "fato" ou "tema";
- estados e versões não são rastreados formalmente;
- explicar "por que o sistema acredita nisso" exige vasculhar logs e conversas;
- não há objeto claro para ancorar em blockchain.

A Truth-DB nasce para resolver isso: torna o conhecimento do Inspectah **persistente, versionado e auditável**, servindo de base tanto para a S11 (blockchain) quanto para a S12 (Explorer/comunidade).

---

## 3) Problemas que a S10 precisa matar

1. **Verdades de chat**: o sistema responde, mas não consolida fatos como objetos de domínio com IDs, estados e versões.
2. **Falta de modelo canônico**: "tema", "fato", "complemento" e "estado" existem mais em texto do que em estruturas formais.
3. **GPT sem contrato operacional**: não há um vocabulário pequeno de ações permitidas, com pré-condições e efeitos claros.
4. **Máquina de estados implícita**: estados existem nas ideias, mas não como uma máquina de estados codificada e validada.
5. **Auditabilidade fraca**: não há um log de eventos de domínio que permita recontar a história de cada bloco/fato.
6. **Modelo pouco explorável para a futura UI**: S12 precisará montar linhas do tempo, disputas, versões e estados atuais; o modelo ainda não está pronto para isso.

Se esses problemas continuarem após a S10, a S11 e a S12 ficam de joelhos.

---

## 4) Objetivos e critérios de sucesso

### 4.1 Truth-DB canônica v1

**Objetivo**: ter uma Truth-DB que represente o conhecimento do Inspectah de forma estável e auditável.

**O que precisa existir**:

- Entidades centrais:
  - `BlocoTema` (tema/caso/obra);
  - `FatoRegistravel` (algo que pode ser verdadeiro/falso ou ter um estado bem definido);
  - `Complemento` (informação adicional ligada a um fato ou tema);
  - `VersaoFato` (histórico do fato ao longo do tempo);
  - `EstadoFato` (estado atual do fato segundo uma máquina de estados);
  - ligações explícitas com evidências (fontes, bundles, hashes) e relatórios.
- Campos preparados para futuro on-chain (IDs estáveis, hashes de conteúdo/estado, espaço para IDs de transação).

**Critério de sucesso**: o time consegue criar, ler e atualizar blocos e fatos piloto apenas usando a Truth-DB, sem precisar de estruturas paralelas (planilhas, JSON solto, etc.).

### 4.2 GPT como Guardião de Blocos (com contrato)

**Objetivo**: o GPT deixa de ser um agente solto e passa a operar por meio de um conjunto pequeno de ações bem definidas.

**Ações mínimas**:

- `criar_bloco_tema`;
- `criar_fato_registravel`;
- `anexar_complemento`;
- `atualizar_estado_fato`;
- `criar_versao_fato`;
- `promover_complemento_a_fato` (se necessário para alguns fluxos).

Para cada ação:

- pré-condições claras (o que deve existir na Truth-DB, qual o estado atual, evidências mínimas);
- efeitos definidos (quais entidades são criadas/atualizadas);
- campos obrigatórios (IDs, descrições, referências a evidências, resumos e relatórios).

Esse contrato é mantido em um **artefato único e canônico**, por exemplo:

- `docs/sprint_10_contrato_acoes_guardiao.md`

…e usado como fonte de verdade para:

- prompts do GPT (Cap. 4);
- implementação da camada mecânica;
- testes de validação.

**Critério de sucesso**: qualquer ação registrada na base pode ser explicada olhando esse contrato; não há divergência entre o que o GPT supõe, o que o código aceita e o que os documentos descrevem.

### 4.3 Camada mecânica de validação e aplicação

**Objetivo**: nenhuma ação do GPT é aplicada "na confiança"; tudo passa por uma máquina determinística.

**Responsabilidades da camada mecânica**:

- receber ações em formato estruturado (JSON);
- verificar se a ação existe no contrato e se seu payload está bem formado;
- validar a máquina de estados (se a transição pedida é permitida);
- validar integridade de IDs e relações (referências existentes, não duplicadas, etc.);
- aplicar a mudança na Truth-DB ou rejeitar a ação com motivo explícito;
- registrar um evento de domínio para cada ação processada (aceita ou rejeitada).

**Critério de sucesso**: em testes e cenários piloto, ações inválidas são rejeitadas com justificativas claras; ações válidas não quebram invariantes de estado ou integridade.

### 4.4 Máquina de estados de fato

**Objetivo**: tornar explícito como um fato pode evoluir ao longo do tempo.

**Elementos mínimos**:

- lista de estados possíveis (exemplo: `planejado`, `confirmado`, `concluido`, `nao_confirmado`, `adiado`, `cancelado`, `incerto`);
- tabela de transições válidas e proibidas;
- política clara para o que acontece em casos ambíguos (ex.: quando novas evidências tornam o fato mais incerto, não mais certo).

**Critério de sucesso**: a camada mecânica não permite transições fora da tabela de estados; qualquer tentativa de mudar de um estado para outro inválido é barrada com erro explícito.

### 4.5 Pipeline ponta a ponta até a Truth-DB

**Objetivo**: provar o fluxo completo em pelo menos dois domínios piloto.

**Fluxo alvo**:

1. ingestão de eventos de N fontes (como na S9);
2. agrupamento em pacotes por tema (obra, contrato, política pública, etc.);
3. chamada do GPT Guardião com contexto e evidências relevantes;
4. geração de ações e relatórios pelo GPT;
5. validação mecânica;
6. gravação na Truth-DB;
7. registro de eventos de domínio que contem a história.

**Critério de sucesso**: para cada domínio piloto, o time consegue rodar esse fluxo localmente e, ao final, inspecionar blocos/fatos e seus eventos de domínio de ponta a ponta.

### 4.6 Auditabilidade para Admin

**Objetivo**: permitir que um Admin humano entenda por que o sistema acredita em algo.

**O que precisa ser possível**:

- pegar qualquer fato criado na Sprint 10 e responder:
  - quais fontes sustentam esse fato;
  - quais ações foram aplicadas (e quais foram rejeitadas);
  - qual o estado atual;
  - qual o resumo textual da decisão (relatório simples);
- acessar, se necessário, um relatório mais detalhado para auditoria.

**Critério de sucesso**: alguém que não participou da implementação consegue revisar um fato piloto e entender, em poucos minutos, a história completa da decisão.

### 4.7 Preparação para S11 e S12

**Objetivo**: evitar retrabalho quando blockchain e Explorer entrarem em cena.

**Requisitos principais**:

- entidades com IDs estáveis e hashes de conteúdo/estado;
- histórico de versões e eventos de domínio suficiente para reconstruir o estado a qualquer momento;
- organização dos dados que facilite queries típicas: por tema, por período, por fonte, por estado, por tipo de evento.

**Critério de sucesso**: a equipe de S11/S12 consegue usar a Truth-DB como está, adicionando apenas camadas de blockchain e UX, sem reescrever o modelo de dados.

---

## 5) Escopo da S10 — o que entra (sem virar filemap)

A lista abaixo não é um filemap, e sim uma visão de "componentes que precisam existir".

1. **Modelo conceitual da Truth-DB**
   - definição das entidades (`BlocoTema`, `FatoRegistravel`, `Complemento`, `VersaoFato`, `EstadoFato`);
   - definição das relações (um tema tem N fatos; um fato tem N versões; cada versão tem um estado e vínculos com evidências e relatórios).

2. **Máquina de estados de fato**
   - estados suportados e significado;
   - transições válidas e proibidas;
   - regras de como tratar reversões, correções e novas evidências.

3. **Contrato de ações do Guardião**
   - conjunto pequeno de ações explícitas, com pré-condições, efeitos e campos obrigatórios;
   - artefato único que serve de fonte de verdade para docs, prompts e código;
   - política de evolução desse contrato (como e quando pode mudar).

4. **Camada mecânica de interpretação e aplicação**
   - componente capaz de receber ações JSON, validá-las, aplicá-las ou rejeitá-las;
   - integração com a Truth-DB e com logs de eventos de domínio.

5. **Pipeline ponta a ponta para ao menos dois domínios piloto**
   - integração da Truth-DB e da camada mecânica com os fluxos de ingestão/decisão existentes;
   - capacidade de demonstrar o fluxo `eventos → GPT Guardião → ações → Truth-DB` em produção local.

6. **Ferramenta mínima de exploração interna**
   - interface de linha de comando ou endpoints internos que permitam:
     - listar blocos-tema;
     - inspecionar um bloco/fato (linha do tempo, estados, ações, relatórios);
     - exportar um bloco ou fato (com suas versões e eventos) em formato estruturado.

---

## 6) Fora de escopo da S10

A Sprint 10 **não** tenta:

- escrever qualquer coisa em blockchain (contratos, transações, gas, fees);
- implementar contestação com bond, reputação ou SLA de resolução;
- resolver ingestão contínua em larga escala (24/7, fila, backpressure, cadências distintas por fonte);
- construir UI final para usuário externo (Explorer, dashboards, etc.);
- cobrir todos os domínios possíveis; o foco é validar o modelo em poucos domínios bem escolhidos.

Qualquer iniciativa que exija essas capacidades deve ser registrada como RFC/ADR e empurrada para S11, S12 ou fases futuras.

---

## 7) Exemplo concreto — obra pública

Tema: "Reforma da escola municipal X em Niterói (contrato 2025-123)".

### 7.1 Criação do bloco-tema

O GPT recebe eventos sobre a obra (licitação, contrato, release da prefeitura) e decide criar um bloco-tema.

Ação: `criar_bloco_tema`

Campos principais:

- `id_bloco`: `obra_2025_123`
- `titulo`: "Reforma da escola municipal X (contrato 2025-123)"
- `descricao_curta`: resumo do objeto do contrato
- `referencias_iniciais`: links para licitação, contrato, matérias relevantes

Resultado: a Truth-DB passa a ter um `BlocoTema` que representa essa obra.

### 7.2 Criação de um fato registrável

Fato: "A obra está prevista para terminar em 15/12/2025".

Ação: `criar_fato_registravel`

Campos principais:

- `id_bloco`: `obra_2025_123`
- `id_fato`: `obra_2025_123_prazo_conclusao`
- `resumo_fato`: "Prazo de conclusão em 15/12/2025"
- `estado_inicial`: `planejado`
- `evidencias`: citações à licitação/contrato e releases oficiais
- `relatorio_simples`: parágrafo explicando por que esse prazo é considerado válido

Resultado: o tema agora tem um fato registrável com estado inicial `planejado` e uma trilha mínima de evidências.

### 7.3 Atualização de estado após novas evidências

Meses depois, aparecem notícias de atraso e um aditivo de prazo.

Ação: `atualizar_estado_fato`

Campos principais:

- `id_fato`: `obra_2025_123_prazo_conclusao`
- `estado_anterior`: `planejado`
- `estado_novo`: `adiado`
- `justificativa`: resumo das novas evidências (aditivo, reportagens)
- `relatorio_simples`: explicação legível da mudança

A camada mecânica verifica se `planejado → adiado` é uma transição válida. Se for:

- cria uma nova `VersaoFato`;
- atualiza o `EstadoFato` para `adiado`;
- registra um evento de domínio do tipo `EstadoAtualizado`.

### 7.4 Conclusão da obra

Quando a obra termina de fato:

- nova ação `atualizar_estado_fato` para `concluido`;
- criação de uma nova `VersaoFato` refletindo a data real de conclusão;
- anexação de evidências (relatório de entrega, fotos, comunicados oficiais).

Ao olhar o tema `obra_2025_123`, um Admin enxerga:

- a linha do tempo de estados (`planejado → adiado → concluido`);
- as evidências que sustentaram cada mudança;
- os relatórios que explicam as decisões;
- um conjunto de objetos pronto para ser ancorado em blockchain na S11.

---

## 8) Handshake com S9, S11 e S12

- **De S9 para S10**: S9 fornece pipelines de ingestão e decisão em cenários de demonstração. S10 usa esses fluxos como fonte de eventos para construir blocos, fatos e estados na Truth-DB.

- **De S10 para S11**: S11 assume que:
  - a Truth-DB existe;
  - blocos/fatos/versões/estados são auditáveis;
  - há eventos de domínio e hashes/IDs estáveis.
  S11 constrói smart contracts e fluxos de ancoragem on-chain em cima disso.

- **De S10/S11 para S12**: S12 assume Truth-DB + âncoras on-chain funcionando, e foca em:
  - ingestão contínua em escala;
  - qualidade ao longo do tempo;
  - Explorer/experiências para usuários externos e comunidade.

---

## 9) Riscos e guardrails

1. **Modelo engessado demais**
   - Risco: desenhar uma Truth-DB que só funciona para 1–2 domínios.
   - Guardrail: manter blocos/fatos/versões/estados genéricos, permitir campos específicos via metadados/configuração.

2. **Vocabulário de ações inflado ou confuso**
   - Risco: criar dezenas de ações difíceis de entender e testar.
   - Guardrail: manter um conjunto pequeno e poderoso; mudanças no contrato exigem ADR e atualização do artefato canônico.

3. **Invariantes não codificados**
   - Risco: depender de "bom senso" para estados, versões e integridade de IDs.
   - Guardrail: invariantes formalizados em código + testes; gates futuros da S10 validam estados impossíveis.

4. **Acoplamento com ambiente/infra**
   - Risco: decisões de domínio amarradas a detalhes de ambiente (ports, paths, etc.).
   - Guardrail: este capítulo fala apenas de domínio; detalhes de infra ficam em docs/capítulos próprios, usando variáveis de ambiente e scripts padrão.

5. **Evidência frouxa**
   - Risco: verdades entrando na Truth-DB com pouca ou nenhuma trilha de evidências.
   - Guardrail: qualquer fato/estado criado na S10 deve apontar para um conjunto mínimo de evidências e um relatório simples que um humano consiga ler e entender.

---

## 10) Como usar este capítulo

- Para o PO e arquitetos: este é o **contrato de visão** da Sprint 10. Mudanças relevantes de escopo ou modelo devem passar por aqui e gerar ADR.
- Para engenheiros e Codex: use este capítulo como norte conceitual. Cap. 2 transforma objetivos em gates e DoD; Cap. 3 mapeia em arquivos e fluxos; Cap. 4 conecta o contrato de ações do Guardião aos prompts do GPT.
- Para S11/S12: sempre que surgir dúvida se algo pertence à S10 ou deve ser empurrado para depois, use esta regra simples:
  - mexeu em verdade, estados, versões, contrato de ações ou auditabilidade básica → é S10;
  - mexeu em blockchain/contestação → é S11+;
  - mexeu em ingestão contínua, Explorer ou comunidade → é S12+.

