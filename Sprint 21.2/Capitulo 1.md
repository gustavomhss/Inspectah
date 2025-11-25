# Sprint 21.2 — Capítulo 1 (Contexto, Problema e Objetivos)

**Título interno:** Copiloto de Fontes v2 — Criação, Edição e Ciclo de Vida Guiados (incluindo Fontes Oficiais Abertas)

---

## 1. Contexto macro

O Inspectah já assumiu, nas Sprints 21 e 21.1, que “fonte” é um recurso nuclear do produto: tudo o que virá depois (ingestão contínua, Debunker, timelines, Truth-DB) depende da qualidade do catálogo de fontes — o que existe, como é descrito, o quão confiável é, com que frequência é atualizado e em que estado de vida se encontra.

Estado atual, assumido como verdade:

- **Sprint 21** entregou o **Console de Fontes v1**:
  - Modelo de dados consolidado em `app/sources` (tipos, temas, info_types, estado, saúde, histórico de estados e healthchecks).
  - Migrations `0002` e `0003` criam schema e seeds de fontes por domínio (notícias, clima, esportes, etc.), com SQLite como verdade local.
  - Serviço de fontes com CRUD, transições básicas de estado, histórico de mudanças, healthcheck e integração com UI de admin.
  - Frontend de admin com listagem, detalhe e criação de fontes.
  - Gates `S21_G0…S21_G8` e `bin/s21_all_gates.sh` em estado **PASS/GO**, com scorecards e evidências em `out/`.

- **Sprint 21.1** entregou o **Copiloto de Fontes v1**:
  - Router do Copiloto em `inspectah/routers/copiloto_fontes.py`, serviços de sessão/arquivos em `inspectah/services/`, tools em `inspectah/agents/tools/`.
  - Agente `inspectah/agents/s21_1_copiloto_fontes.py` com persona, contrato JSON e política de segurança inicial.
  - Widget de chat integrado ao formulário de criação de fontes (frontend), via `useCopilotoAgent` e componentes de UI dedicados.
  - Documentação específica (modo agente, cenários, política de segurança, scorecard e wrap de execução da 21.1).
  - Testes em `tests/agents` validando fluxo básico e safety do Copiloto.

Em cima disso, o admin já consegue:

- Cadastrar fontes usando o formulário clássico do Console.
- Pedir ajuda ao Copiloto para preencher parte dos campos.
- Listar fontes, abrir detalhe, inspecionar healthcheck e histórico.

Mas a experiência real (tests manuais + feedback do PO) mostrou que esse conjunto ainda está longe do padrão de excelência esperado para o Inspectah.

---

## 2. Problema detalhado (por que a v1 é insuficiente)

A seguir, os problemas concretos que motivam a Sprint 21.2. Eles não são “nice to have”: são falhas estruturais que, se não forem resolvidas agora, vão vazar complexidade e retrabalho para S22–S25.

### 2.1 Conversa rasa e pouco adaptativa

Em cenários reais simples, como:

> “Quero cadastrar o globo.com como fonte de notícias.”
> “Quero usar https://www.terra.com.br/noticias como fonte.”

o Copiloto frequentemente responde com algo na linha de:

> “Endpoint/URL base é obrigatório.”

E fica preso nessa frase. Problemas aqui:

- O agente **não tenta inferir** nada a partir da mensagem (por exemplo, extrair URLs, propor endpoint base, sugerir tipo/temas).
- Ele **não evolui o diálogo**: não sugere o próximo passo (“cole a URL base”, “me diga qual página é a principal”, etc.).
- O admin tem a sensação de estar discutindo com um validador de formulário, não com um especialista em fontes.

### 2.2 Ausência de fluxo guiado por tipo de fonte

Hoje o Copiloto funciona como um “assistente genérico de formulário”: ele olha o `form_state` e tenta sugerir campos, mas não existe uma máquina de estados conversacional clara, nem especialização por tipo de fonte.

Consequências:

- O fluxo não segue etapas previsíveis do tipo:
  - escolher_tipo_de_fonte → coletar_dados_que_o_admin_ja_tem → preencher_lacunas → confirmar_criacao/edicao.
- O agente não se comporta de forma diferente para **notícias**, **clima**, **esportes** ou **fontes oficiais**.
- O admin não sente que está “num processo” — só sente que está em um chat que às vezes ajuda, às vezes atrapalha.

### 2.3 Edição de fontes ainda é cidadã de segunda classe

Embora os componentes de backend e frontend permitam **editar** fontes, essa capacidade ainda não foi tratada como protagonista na experiência com o Copiloto:

- O Copiloto não “entra” no detalhe da fonte com consciência de que está em modo edição.
- Não existe fluxo desenhado para pedidos como:
  - “Ajusta o refresh para 6 horas.”
  - “Troca esses temas por estes outros.”
  - “Atualiza o endpoint para esta nova URL.”
- O agente não monta um **plano de mudança** (antes/depois) para revisão, nem devolve um diff que a UI possa exibir ao admin.

Na prática, edição ainda acontece mais “na mão” do que assistida pelo Copiloto.

### 2.4 Ciclo de status subaproveitado (aprovar, suspender, desativar)

O modelo e a ontologia de fontes já preveem estados de ciclo de vida (ex.: pendente, aprovada/ativa, suspensa, desativada), mas:

- O Console ainda não expõe esse fluxo de maneira amigável e consistente.
- O Copiloto não ajuda de forma estruturada na decisão de aprovar/suspender/desativar.
- Não há um padrão consolidado de:
  - ler o estado atual,
  - sugerir uma transição válida,
  - explicar o impacto,
  - devolver um plano para confirmação,
  - só então acionar os endpoints reais.

### 2.5 Intervalo de refresh como “parente pobre” do modelo

Consultar fontes em produção, de forma contínua, exige que o intervalo de atualização faça parte do contrato da fonte. Hoje:

- O intervalo de refresh **não é tratado como campo de primeira classe** de ponta a ponta.
- Ele não está claramente modelado/persistido na mesma dignidade que tipo, endpoint, temas, etc.
- Não está bem exposto nem explicado na UI.
- Não faz parte natural do fluxo de conversa do Copiloto (“com que frequência você quer atualizar isso?”).

Sem isso, S22+ (ingestão contínua e agendamento) terão que “chutar” comportamento ou refazer base.

### 2.6 Falta um tipo formal para fontes oficiais abertas

O Inspectah precisa tratar com carinho um tipo específico de fonte:

- **Fontes oficiais abertas** (IBGE, órgãos públicos, portais oficiais, etc.) que:
  - não têm API nem RSS, mas
  - expõem dados em HTML, PDF, CSV, etc., abertos para leitura.

Hoje:

- Não existe um tipo formal na ontologia para esse caso.
- O Console encaixa essas fontes em tipos genéricos.
- O Copiloto não tem roteiro próprio nem perguntas específicas para esse tipo, apesar da importância estratégica (estatísticas oficiais, dados macroeconômicos, etc.).

### 2.7 UX de formulário e explicações inconsistentes

Campos como slug, tipo, temas, info_types, endpoint, refresh e status ainda não têm descrições curtas e objetivas na UI, totalmente alinhadas com:

- A ontologia de fontes da Sprint 21.
- A forma como o Copiloto descreve esses elementos na conversa.

Resultado: o admin frequentemente não tem clareza total sobre o que deve preencher, o que é obrigatório, qual o formato esperado ou qual o impacto daquele campo.

### 2.8 Segurança e escopo ainda aquém do novo tamanho do problema

À medida que damos ao Copiloto capacidade de:

- sugerir status,
- propor desativação de fontes,
- operar sobre fontes oficiais,

a superfície de risco aumenta:

- É preciso garantir que ele **nunca sai do domínio de fontes** (não mexe em usuários, casos, timelines, etc.).
- É preciso garantir que ele **não prometa o que não existe** (ex.: ingestão automática em fontes oficiais) e recuse pedidos de validação de verdade/fato (isso pertence ao Debunker/futuras sprints).
- É necessário logar decisões sensíveis (principalmente em status e fontes oficiais) de forma auditável.

A política de segurança da S21.1 é um bom começo, mas o escopo da 21.2 é maior e precisa de blindagem equivalente.

---

## 3. Visão da Sprint 21.2 (estado desejado)

A Sprint 21.2 existe para transformar o Console + Copiloto de Fontes em uma camada **pronta para produção séria**, que sirva de base confiável para as sprints de ingestão contínua, Debunker e Truth-DB.

Depois da 21.2, a experiência esperada é:

- **Criação guiada**: ao abrir “Nova fonte”, o Copiloto abre automaticamente, pergunta o tipo de fonte, entende o que o admin já sabe, ajuda a encontrar o que falta e acompanha até o momento de salvar. O admin nunca fica preso em mensagens vazias.
- **Edição guiada**: ao abrir o detalhe de uma fonte, o Copiloto enxerga o estado atual, entende pedidos de ajuste (endpoint, temas, refresh, descrição, etc.) e monta planos de alteração com diff antes/depois para o admin revisar.
- **Ciclo de vida explícito**: aprovar, suspender e desativar fontes deixa de ser “opção escondida”. O Copiloto entende o ciclo de status, sugere transições válidas e nunca aplica nada sem confirmação humana.
- **Refresh como contrato**: toda fonte relevante tem um intervalo de atualização explícito, persistido, visível e sugerido pelo Copiloto de acordo com o tipo.
- **Fontes oficiais abertas como tipo de primeira classe**: existe um tipo formal na ontologia e no Console; o Copiloto tem um fluxo específico para esses casos e ajuda o admin a capturar todos os metadados necessários para ingestão futura, sem prometer magia.
- **Segurança e escopo blindados**: o Copiloto continua confinado ao domínio de fontes, recusa pedidos fora de escopo, não decide verdade/fato, e registra decisões importantes em logs auditáveis.

Essa é a “linha de chegada” conceitual: qualquer solução técnica que não leve a esse estado é parcial.

---

## 4. Objetivo principal da Sprint 21.2

**Objetivo central:**

Transformar o Console + Copiloto de Fontes em um **Copiloto de Fontes v2**, capaz de:

- Guiar **criação** e **edição** de fontes de ponta a ponta (campos, status, refresh),
- Operar o **ciclo de vida** da fonte (pendente, aprovada, suspensa, desativada) de forma segura e explicável,
- Tratar **refresh interval** e **fontes oficiais abertas** como elementos de primeira classe no modelo, na UI e no agente,

sem quebrar S21/S21.1 e sem sair do domínio de fontes.

---

## 5. Objetivos específicos (desdobrados)

1. **Fluxo conversacional guiado por tipo de fonte e estágio**
   - Introduzir uma máquina de estados conversacional explícita no Copiloto (armazenada na sessão) com etapas como:
     - escolher_tipo_de_fonte
     - coletar_dados_que_o_admin_ja_tem
     - preencher_lacunas_obrigatorias
     - confirmar_criacao_ou_edicao
   - Especializar perguntas/heurísticas para tipos já previstos na S21 (notícias, clima, esportes, etc.) e para o novo tipo de **fonte oficial aberta**.
   - Tornar o fluxo adaptativo: se o admin adianta informações (URL, órgão, frequência), o Copiloto reconhece e não repete.

2. **Copiloto obrigatório na criação, “modo agente” opcional e visível**
   - O Copiloto deve ser **sempre aberto automaticamente** na tela de criação de fonte.
   - Nenhuma fonte é criada sem pelo menos uma interação com o Copiloto.
   - “Modo agente” (uso intenso de tools e inferências) passa a ser controlado por um toggle no UI, com comportamento diferenciado entre:
     - modo agente ligado (mais proativo, mais automatização, sempre com confirmação humana),
     - modo agente desligado (mais conservador, explicativo, menos ações automáticas).
   - Esse `agent_mode` precisa ser respeitado ponta a ponta: payload do frontend, router, agente e testes.

3. **Edição de fontes como primeiro cidadão do Copiloto**
   - No detalhe da fonte, o Copiloto trabalha com contexto de `source_id` + snapshot atual.
   - O admin consegue pedir mudanças específicas (temas, endpoint, refresh, descrição, etc.).
   - O agente lê a fonte via tools de domínio, monta um **plano de alteração** (campos, valores antes/depois) e devolve actions consumíveis pela UI.
   - A UI mostra um diff claro, e só após confirmação humana os endpoints de update/delete/status são acionados.

4. **Ciclo de status operacionalizado (aprovar, suspender, desativar)**
   - Formalizar no código e docs a máquina de estados de fonte (nomes e transições válidas).
   - Ensinar o Copiloto a:
     - explicar o status atual em linguagem simples,
     - propor transições coerentes com o contexto,
     - recusar transições inválidas ou perigosas,
     - sempre retornar um plano de mudança de status, nunca aplicar diretamente.

5. **Refresh interval como parte do contrato da fonte**
   - Introduzir/consolidar campo de `refresh_interval` no modelo de fontes (migrations, schemas, service).
   - Expor esse campo na UI com explicação clara e opções sensatas.
   - Integrar o refresh no fluxo conversacional do Copiloto, com perguntas, sugestões por tipo de fonte e validação.

6. **Fontes oficiais abertas como tipo formal na ontologia**
   - Adicionar tipo dedicado para “fontes oficiais abertas” na ontologia da S21 e no Console (ex.: official_open_html, nome final a ser decidido no Cap. 2/3).
   - Definir campos obrigatórios (órgão emissor, URL oficial, escopo, formato, frequência, etc.).
   - Ensinar o Copiloto a reconhecer esse tipo a partir da fala do admin e guiá-lo com perguntas específicas.
   - Documentar explicitamente que ingestão automática é futura: o escopo da 21.2 é o **cadastro perfeito** dessas fontes, não o pipeline completo.

7. **Segurança e logging no nível do novo escopo**
   - Reforçar, no prompt e no código do agente, que o Copiloto:
     - só atua no domínio de fontes,
     - não decide verdade/fato,
     - não altera usuários, casos, timelines ou outras entidades.
   - Expandir testes de safety para cobrir:
     - pedidos indevidos envolvendo fontes oficiais,
     - tentativas de prompt injection para sair do escopo,
     - solicitações para “dar um jeito” de fazer algo não suportado.
   - Logar decisões sensíveis (especialmente status e oficiais abertas) usando a infra de logging existente, de forma auditável.

---

## 6. Escopo da Sprint 21.2 (IN / OUT)

**Escopo IN:**

- Evolução do Copiloto (backend + agente + tools) para suportar:
  - Fluxo conversacional guiado por tipo e estágio.
  - Criação **e edição** completas de fontes.
  - Ciclo de status (aprovar, suspender, desativar) com plano e confirmação.
  - Refresh interval de ponta a ponta.
  - Fontes oficiais abertas como tipo formal.
  - Modo agente opcional, Copiloto obrigatório na criação.
- Ajustes no Console de Fontes (backend + frontend) necessários para:
  - refletir o novo tipo de fonte,
  - expor e validar refresh interval,
  - suportar ciclo de status completo,
  - melhorar descrições de campos alinhadas ao Copiloto.
- Atualização dos docs da S21, S21.1 e novos docs da S21.2 para refletir o comportamento real.
- Ampliação de testes em `tests/sources` e `tests/agents` cobrindo os novos fluxos.
- Ajustes finos nos gates (S21/S21.1 e camada S21.2) para garantir que scorecards e evidências passam a cobrir esse novo escopo.

**Escopo OUT:**

- Qualquer alteração em Sprints 8 e 9 ou no pipeline ORR global que não seja estritamente necessária para manter S21/S21.1/S21.2 verdes.
- Implementação de ingestão automática real para fontes oficiais abertas (crawler/parser).
- Redesign geral do frontend de admin ou da UI de usuário final; a sprint atua focada em Console de Fontes + Copiloto.
- Mudanças em Debunker, timeline de casos, Truth-DB ou regras de promoção de verdade/fato.

---

## 7. Definição de pronto (DoD) — visão de alto nível

A Sprint 21.2 será considerada concluída quando, além de testes, lint, build e gates relevantes verdes, as seguintes afirmações forem verdadeiras em uso real da interface:

1. Um admin consegue criar, sem atrito, uma fonte de notícias, uma de clima/esportes e uma fonte oficial aberta, sempre com o Copiloto guiando o processo, sem mensagens pobres e sem dúvidas sobre o que falta.
2. O admin consegue editar fontes existentes (incluindo ajustes de refresh, temas, endpoint e descrição) com auxílio do Copiloto, vendo um diff claro antes de confirmar as mudanças.
3. Aprovar, suspender e desativar fontes é possível de forma segura, guiada e previsível, tanto pela UI quanto usando o Copiloto, sem transições inválidas.
4. Toda fonte relevante tem um **refresh interval** persistido, visível e integrado ao fluxo do Copiloto.
5. Fontes oficiais abertas têm tipo específico, campos claros, fluxo dedicado no Copiloto e documentação consistente com o comportamento real.
6. O Copiloto não sai do domínio de fontes, não promete funcionalidades inexistentes e registra decisões sensíveis em logs auditáveis.
7. Os documentos da S21, S21.1 e S21.2 refletem com precisão o que o código faz; não há divergências conceituais relevantes entre “papel” e “sistema”.

Este Capítulo 1 define o **norte conceitual** da Sprint 21.2. Os Capítulos 2 (gates e critérios), 3 (filemap/arquitetura) e 4 (plano de execução) devem ser construídos de forma estritamente alinhada a este texto.

