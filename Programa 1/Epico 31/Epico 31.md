# Épico E31 — Evidence Vault v1 (Repositório de Evidências & Ligações)

> Programa 1 — Consolidação & Consoles Full  
> Dono lógico: Squad Evidence & Traços (Michael Stonebraker, Peter Norvig, Judea Pearl, Karl Popper, Percy Liang, Steve Jobs)

---

## 1. Identidade do épico

**Código:** E31  
**Nome curto:** Evidence Vault v1  
**Programa:** Programa 1 — Consolidação & Consoles Full (S26–S32)  
**Status:** Em design  

**Resumo em uma frase:**

E31 entrega o primeiro Evidence Vault operacional do Inspectah: um repositório unificado, consultável e rastreável de evidências (documentos, dados, trechos, citações) com ligações explícitas para Proposições (E30), Casos de Debunking (E29), Fontes (E27) e Fluxos de Agentes (E28), ainda sem exigir o Sistema de Blocos completo ou ancoragem em blockchain.

---

## 2. Problema

Sem o Evidence Vault v1, o Inspectah sofre de amnésia e bagunça de bastidores:

- Evidências usadas em decisões importantes ficam espalhadas em anexos soltos, links externos, prints, PDFs, dumps de dados, comentários em tickets ou outputs de agentes.  
- Não há um lugar único para responder: "quais evidências sustentam essa posição de verdade?" ou "de onde veio esse número?".  
- Quando uma evidência é corrigida, revogada ou se mostra duvidosa, não existe uma maneira simples de descobrir **quais decisões e verdades dependiam dela**.  
- Debunker, Truth Console, Case Cockpit e outros módulos acabam recriando mecanismos próprios de anexar e exibir evidências, sem padrão, sem reuso e sem rastreabilidade consistente.

Isso é incompatível com o objetivo do Inspectah de ser um sistema de verdade auditável, explicável e resistente à manipulação.

E31 existe para criar o **cofre de evidências v1**: um lugar unificado, com modelo e API estáveis, onde qualquer decisão séria do sistema seja capaz de apontar suas evidências centrais.

---

## 3. Visão & Estados-alvo

### 3.1 Frase de visão

Quando E31 estiver completo, qualquer pessoa autorizada poderá abrir um claim ou caso no Inspectah, clicar em "Evidências" e ver uma lista clara, estruturada e revisável de evidências que sustentam (ou contestam) aquela posição: documentos, datasets, trechos de texto, citações, cada um com origem, data, tipo, links para as fontes e uso em outros lugares do sistema.

### 3.2 Estados-alvo (lista canônica)

Ao final de E31, será verdade que:

1. Existe um **modelo único de Evidência v1**, capaz de representar de forma consistente diferentes tipos de evidência (documento, trecho, dado numérico, citação, imagem, etc.), com metadados mínimos de origem, contexto e integridade.
2. Existe um **modelo de Ligações de Evidência v1**, que conecta evidências a Proposições (E30), Casos/Decisões de Debunking (E29), Claims, Fontes (E27), Eventos de Verdade e, futuramente, Blocos.  
3. O Evidence Vault v1 possui um **Console próprio** (UI/Admin) aderente a E26, para:
   - buscar evidências por texto, tipo, entidade, fonte, tema;  
   - ver detalhe de uma evidência;  
   - ver onde ela é usada (Proposições, Casos, Decisões).
4. Debunker v1 (E29) e Truth Console v1 (E30) **não precisam inventar esquema próprio de guardar anexos**: eles usam o Evidence Vault como sistema único de referência.
5. Cada Decisão de Debunking (E29) que alegar sustentação em evidência deve apontar **explicitamente** para uma ou mais entradas no Evidence Vault v1.  
6. Atualizações críticas em evidências (ex.: revogação de um estudo, correção de um dataset) podem ser registradas e, a partir do Evidence Vault, é possível identificar **quais Proposições e Decisões potencialmente foram afetadas**.
7. O modelo e a API do Evidence Vault v1 são compatíveis com a futura promoção a Sistema de Blocos e ancoragem em blockchain, sem exigir a implementação completa dessas camadas neste momento.

---

## 4. Escopo IN / OUT

### 4.1 Escopo IN

E31 cobre, no mínimo:

Definir o **modelo lógico de Evidência v1**, incluindo:

- Identidade estável (ID) de evidência.  
- Tipo de evidência (`documento_textual`, `trecho_textual`, `dado_numerico`, `tabela`, `imagem`, `audio`, `video`, `link_externo`, etc.).  
- Origem (fonte original: site oficial, organismo público, jornal, dataset, estudo científico, etc.).  
- Características básicas de integridade (ex.: hash para arquivos, metadados de captura).  
- Contexto (entidades envolvidas, tema, período, idioma, etc.).

Definir o **modelo lógico de Ligação de Evidência v1**, que representa "evidência X é usada em Y":

- Evidência ↔ Proposição (E30).  
- Evidência ↔ Decisão de Debunking / Caso (E29).  
- Evidência ↔ Claim/Objeto de entrada (ex.: notícia, documento).  
- Evidência ↔ Fonte (E27) e, futuramente, ↔ Bloco.

Criar o **Evidence Vault Console v1 (UI/Admin)**, aderente a E26, com:

- Busca e filtro de evidências.  
- Tela de detalhe com metadados, pré-visualização (quando aplicável) e lista de ligações.  
- Operações básicas (criar/registrar evidência, marcar evidência como revogada/obsoleta, anexar notas).

Definir **fluxos de ingestão/registro de evidências v1**, incluindo:

- Registro automático de evidências originadas de fontes estruturadas (ex.: dataset oficial importado).  
- Registro semiautomático de evidências textuais extraídas por agentes (ex.: citação de um relatório).  
- Registro manual de evidências por operadores (upload de documento, link, arquivo).  

Criar **APIs internas** para que Debunker, Truth Console, Case Cockpit e outros módulos possam:

- Referenciar evidências via ID.  
- Consultar metadados de evidência.  
- Listar evidências associadas a um objeto (Proposição, Caso, Decisão, Claim).

### 4.2 Escopo OUT

E31 não cobre, neste momento:

- Política avançada de versionamento e imutabilidade de evidências em nível de blockchain (Fase 2).  
- OCR complexo, extração semântica avançada ou parsing total de qualquer documento; v1 pode operar com metadados + link para arquivo.  
- Sistema de reputação completo para evidências e fontes (isso pertence à Fase 2 / Governança & Truth Ops).  
- Mecanismo sofisticado de ranking de evidências (ex.: relevância por tema/qualidade científica), além de filtros e ordenações básicas.

---

## 5. Personas & casos de uso

### 5.1 Personas

- Operator Debunker: precisa anexar, consultar e citar evidências em Casos de Debunking.  
- Analista de Verdade: quer entender quais evidências sustentam determinada Posição de Verdade.  
- Investigador de Casos: navega entre casos, claims e evidências para construir narrativas.  
- Data Curator / Evidence Curator: responsável por registrar evidências importantes (ex.: relatórios oficiais, decisões judiciais, datasets públicos) e mantê-las atualizadas.

### 5.2 Casos de uso principais

Registrar evidência nova a partir de um Caso de Debunking:

- Debunker está analisando um caso e encontra um relatório oficial PDF.  
- Clica em "Registrar evidência" dentro do Caso.  
- O sistema abre formulário de cadastro no Evidence Vault (tipo = documento_textual, origem = órgão X, hash do arquivo, etc.).  
- Ao salvar, cria Evidência v1 e automaticamente cria ligação Evidência ↔ Caso e Evidência ↔ Proposição (via claim_ref).

Ver evidências que sustentam uma Posição de Verdade:

- Analista abre Proposição no Truth Console (E30).  
- Na seção "Evidências", vê lista de evidências centrais com tipo, origem, data.  
- Clica em uma evidência e vai para o detalhe no Evidence Vault, podendo ver onde mais ela é usada.

Descobrir o impacto de uma evidência revogada:

- Um estudo científico é retratado/publicamente corrigido.  
- Evidence Curator entra no Evidence Vault, localiza a evidência e marca como "revogada" ou "obsoleta" com motivo.  
- Evidence Vault mostra lista de Proposições, Decisões de Debunking e Casos que dependem dessa evidência.  
- Isso alimenta backlog de revisões em E29/E30.

---

## 6. Modelos conceituais centrais

### 6.1 Evidência v1

Campos lógicos mínimos:

- id  
- tipo (`documento_textual`, `trecho_textual`, `dado_numerico`, `tabela`, `imagem`, `audio`, `video`, `link_externo`, etc.)  
- titulo (nome curto para humanos)  
- descricao (texto breve sobre o que é a evidência)  
- origem_tipo (`fonte_oficial`, `fonte_jornalistica`, `estudo_academico`, `dataset_publico`, `usuario_interno`, etc.)  
- origem_ref (link ou ID da fonte em E27, quando aplicável)  
- local_armazenamento (URL interna, caminho em objeto, referência de bucket, etc.)  
- hash_conteudo (quando aplicável; para arquivos)  
- entidades_relacionadas (lista de IDs de entidades)  
- dominio/tema  
- escopo_temporal (quando a evidência se aplica)  
- idioma  
- status (`ativa`, `revogada`, `obsoleta`)  
- motivo_status (quando não ativa)  
- created_at, updated_at.

Para tipos específicos, podem existir subcampos opcionais:

- dado_numerico: valor, unidade, referencia (ex.: tabela IBGE X, linha Y).  
- trecho_textual: texto_resumido, offset/página, link para doc maior.

### 6.2 Ligação de Evidência v1

Representa o uso de uma evidência em algum contexto do Inspectah.

Campos mínimos:

- id  
- evidencia_id  
- tipo_alvo (`proposicao`, `decisao_debunking`, `caso_debunking`, `claim`, `evento_verdade`, etc.)  
- alvo_id (ID concreto no módulo alvo)  
- papel (`evidencia_central`, `evidencia_de_contexto`, `contra_evidencia`, etc.)  
- created_at.

### 6.3 Evento de Evidência

Para rastrear mudanças importantes na própria evidência:

- id  
- evidencia_id  
- tipo_evento (`criada`, `atualizada`, `revogada`, `correcao`, `nota_adicionada`)  
- autor_id (quando aplicável)  
- detalhes  
- timestamp.

---

## 7. Requisitos funcionais

### 7.1 Evidence Vault Console v1 — Busca e navegação

- Campo de busca por texto livre (titulo, descricao, texto_resumido para alguns tipos).  
- Filtros por:
  - tipo de evidência;  
  - origem_tipo;  
  - dominio/tema;  
  - status (ativa, revogada, obsoleta);  
  - período de criação.

- Lista de resultados com colunas: título, tipo, origem_tipo, status, última atualização, número de ligações.

### 7.2 Detalhe de evidência

Tela de detalhe deve conter:

- cabeçalho com título, tipo, origem, status;  
- descrição e principais metadados (domínio, entidades, escopo temporal);  
- pré-visualização (quando viável: trecho de texto, thumbnail, etc.);  
- lista de ligações (onde essa evidência é usada), com links para:
  - Proposições (E30);  
  - Decisões/Casos de Debunking (E29);  
  - Claims originais;  
  - outros contextos relevantes.

- histórico de eventos da evidência (criacao, atualizacoes, revogacao, notas).

### 7.3 Registro e edição de evidências

- Criar evidência manualmente (formulário) a partir de:
  - Evidence Vault direto;  
  - outros consoles (Debunker, Truth, Case) via fluxo de "Registrar evidência".

- Editar metadados (ex.: ajustar dominio, entidades_relacionadas).  
- Mudar status (ativa → revogada/obsoleta) com motivo obrigatório.  
- Anexar notas internas (comentários estruturados) quando necessário.

### 7.4 Ligações de evidência

- Criar ligação Evidência ↔ alvo automaticamente em fluxos típicos:
  - ao citar uma evidência em decisão de debunking;  
  - ao vincular evidência a Proposição no Truth Console;  
  - ao registrar evidência a partir de um Caso.

- Permitir ligações manuais quando necessário (com tipos de papel).  
- Exibir, no módulo alvo, a lista de evidências ligadas, sempre referenciando o Evidence Vault.

---

## 8. Requisitos não funcionais

### 8.1 Integridade e auditabilidade

- Não é permitido excluir fisicamente uma evidência v1; revogação/obsolescência deve ser feita por status, mantendo histórico.  
- Logs de criação, atualização, mudança de status e ligações devem ser persistidos.

### 8.2 Performance e escala

- Busca e listagem devem continuar utilizáveis mesmo com milhares de evidências em v1.  
- Ligações devem ser eficientes o suficiente para listar evidências de um Caso/Proposição sem travar a UI.

### 8.3 Segurança & privacidade

- Evidências podem conter dados sensíveis; controle de acesso deve respeitar perfis e políticas do Inspectah.  
- Logs não devem expor conteúdos sensíveis além do necessário; pode-se referenciar evidências por ID.

### 8.4 Consistência com E26

- Evidence Vault Console segue padrões de layout, tabelas, estados e mensagens definidos por E26.

---

## 9. Métricas de sucesso do épico

Indicadores para saber se E31 está entregando valor real:

- Percentual de Decisões de Debunking que referenciam evidências registradas no Evidence Vault (vs texto solto).  
- Tempo médio para encontrar evidências relevantes associadas a uma Proposição ou Caso.  
- Número de evidências revogadas/obsoletas que ainda estão ligadas a Posições de Verdade ativas (ajuda a monitorar débito de revisão).  
- Adoção do Evidence Vault pelos times (quantidade de evidências registradas e ligações criadas por período).

---

## 10. Decomposição em sprints

### 10.1 Entregas sugeridas

- E31.1 — Modelo de Evidência & Ligações v1 + APIs básicas  
  - Implementar entidades Evidência, Ligação de Evidência, Evento de Evidência;  
  - APIs internas para criar/consultar evidências e ligações.

- E31.2 — Evidence Vault Console v1 (busca + detalhe)  
  - UI/Admin aderente a E26;  
  - busca, filtros, lista, detalhe com metadados e ligações.

- E31.3 — Integrações com Debunker & Truth Console  
  - vincular decisões de debunking a evidências;  
  - exibir evidências no Truth Console a partir do Evidence Vault;  
  - fluxos de registro de evidência "a partir" de casos/claims.

### 10.2 Relação com sprints S26–S32

- S26–S27: podem atacar E31.1 em paralelo com fundações de E29/E30.  
- S28–S29: foco em E31.2 (console pronto para uso interno limitado).  
- S30–S32: E31.3 aprofunda integrações e começa a fechar laço Debunker → Evidence → Truth.

---

## 11. Riscos, decisões e anti-objetivos

### 11.1 Riscos

- Overdesign de schema tentando cobrir todo tipo de evidência de cara.  
- Subestimar o custo de armazenamento se o Vault virar "lixeira" de qualquer arquivo sem critério.  
- Criar UI complicada demais para registro/consulta em v1, reduzindo adoção.

### 11.2 Decisões de design esperadas

- Começar com tipos de evidência mais comuns (documento_textual, trecho_textual, dado_numerico, link_externo) e evoluir.  
- Estabelecer guidelines de registro (o que deve virar evidência formal vs o que é só contexto).  
- Focar em metadados e ligações fortes em v1; parsing avançado pode ficar para Programas posteriores.

### 11.3 Anti-objetivos

- E31 não é ainda o "arquivo histórico imutável on-chain"; é o cofre operacional v1.  
- E31 não tenta resolver classificação semântica automática perfeita de qualquer documento.  
- E31 não substitui sistemas externos de repositório de documentos corporativos; ele indexa o que é relevante para verdade/decisão no Inspectah.

---

## 12. Conexão com outros épicos e programas

E26 — Console Full: Evidence Vault Console é mais um console admin e deve ser exemplar em aderência ao padrão.  
E27 — Fontes & Ingestão: muitas evidências virão de fontes oficiais; o Vault precisa referenciar claramente essas fontes.  
E28 — Fluxos de Agentes: agentes podem sugerir ou extrair evidências; execuções de fluxo podem referenciar evidências usadas.  
E29 — Debunker v1: principal usuário do Evidence Vault, tanto para registrar quanto para consumir evidências.  
E30 — Truth Console v1: exibe evidências centrais de Proposições; todas vêm do Vault.  
E32 — Case Cockpit v1: usa o Vault para montar o dossiê de casos complexos.  
Programas futuros (Sistema de Blocos, Blockchain, Governança): o Evidence Vault é fonte primária de evidências que serão promovidas a blocos e usadas em políticas de verdade.

---

## 13. Notas finais

Este documento define a visão, escopo, modelos e contratos do Épico E31 — Evidence Vault v1.

Sprints que lidarem com registro, consulta, anexação ou auditoria de evidências devem usar este épico como referência direta no Sprint Playbook (Cap.1–Cap.4), declarando claramente quais partes de E31.1, E31.2 ou E31.3 estão sendo tornadas verdade em cada ciclo.

