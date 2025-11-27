### 3.4 – Dependências e integrações (v2)

Este subcapítulo descreve, com precisão operacional, **de quem o sistema depende, o que trafega em cada fio e o que acontece quando qualquer fio falha**. Ele amarra a arquitetura lógica (3.1), o filemap (3.2) e os modelos/contratos (3.3) em um mapa único de integrações internas e externas do Inspectah.

Ao final deste 3.4, qualquer pessoa da equipe deve conseguir responder, sem chute:
- quais componentes a sprint introduz ou altera,
- quais serviços, filas, bancos, vaults e provedores externos esses componentes usam,
- quais contratos (HTTP, eventos, objetos) regem cada integração,
- qual é o comportamento esperado em caso de lentidão, erro intermitente ou falha total.

> Escopo: este 3.4 é escrito para o arco S21–S25 (Console de Fontes → Ingestão 2.0 → Cérebro/Comitês → Debunker v0 → Governança/Truth‑DB). Cada sprint concreta deve especializar este texto, restringindo-se aos componentes e integrações que realmente toca.

---

### 3.4.1 – Visão geral de componentes e fluxos

Do ponto de vista de dependências e integrações, a arquitetura relevante da sprint é composta por:

1. **Admin/Console de Fontes**  
   Serviço responsável por cadastro, edição, pausa e health-check de `Source` e `IngestionConfig`. Expõe APIs HTTP administrativas (ex.: `/admin/sources`, `/admin/ingestions`) e lê/grava em tabelas de fontes e configuração no banco relacional.

2. **Ingestion Orchestrator & Workers (Ingestão 2.0)**  
   Orquestrador agenda `IngestionRun` a partir de `IngestionConfig` e distribui trabalho para workers. Workers consomem fontes externas (RSS, APIs, arquivos), persistem `IngestionItemRaw` e `IngestionItemNormalized`, e publicam eventos `ingestion.item.normalized` na mensageria.

3. **Interpreter & Classifier (Cérebro v1)**  
   Serviços responsáveis por criar `InterpretationUnit`, `ClassificationResult` e `Claim` a partir de eventos de ingestão. Consomem eventos de `ingestion.item.normalized`, chamam agentes GPT ou equivalentes, escrevem resultados no banco e publicam eventos `interpretation.unit.created` e `claim.created`.

4. **Committee Engine & Debunker v0**  
   Conjunto de serviços que: (a) registram avaliações de comitês (`CommitteeEvaluation`, `CommitteeDecision`), (b) gerem o ciclo de vida de `DebunkIssue` e `DebunkTask`, (c) emitem eventos `committee.decision.made`, `debunk.issue.opened` e `debunk.task.completed`.

5. **Truth‑DB Service (Governança de Verdade/Fato)**  
   Serviço responsável por gerir `TruthRecord` e `TruthChangeEvent`, reagindo a decisões de comitê e resultados de debunker. Consome eventos `committee.decision.made` e `debunk.issue.resolved` e emite `truth.state.changed`.

6. **Evidence Vault & Open Data Connectors**  
   Infra de armazenamento de evidências (objetos e snapshots) + conectores para dados abertos (portais governamentais, IBGE, bancos centrais), usados para materializar `Evidence` e revalidar claims.

7. **Observabilidade & Infra de Suporte**  
   Stack de logs estruturados, métricas e traços, mais os serviços de suporte: banco relacional, mensageria, vault de segredos e camada de autenticação/autorização de APIs.

As seções seguintes destrincham as dependências de cada componente, sempre conectando à semântica de dados do 3.3.

---

### 3.4.2 – Banco de dados relacional e organização de schemas

O banco relacional é a dependência central de persistência operacional para o arco S21–S25. Ele armazena todas as entidades descritas no 3.3, com integridade referencial forte.

**Responsabilidades do banco na sprint:**
- ser o **sistema de registro** para: `Source`, `SourceHealthCheck`, `IngestionConfig`, `IngestionRun`, `IngestionItemRaw`, `IngestionItemNormalized`, `InterpretationUnit`, `ClassificationResult`, `Claim`, `Evidence`, `CommitteeEvaluation`, `CommitteeDecision`, `DebunkIssue`, `DebunkTask`, `TruthRecord`, `TruthChangeEvent`;
- garantir **cadeias de FK completas** (por exemplo, não pode existir `Claim` sem `InterpretationUnit` associada, nem `TruthRecord` sem `Claim` e `CommitteeDecision` válidos);
- expor **metadados confiáveis** de auditoria (timestamps, status, versões) para gates de sanidade e scorecards.

Organização típica:
- Schema único (ex.: `public` ou `inspectah_core`) contendo todas as tabelas de domínio; alternativamente, divisão leve por contexto (`sources`, `ingestion`, `claims`, `truth`).
- Índices em campos críticos para consulta e integridade:
  - `source(uri, kind)` – para unicidade e lookup rápido;
  - `ingestion_item_raw(source_id, source_item_id)` – para evitar duplicatas e permitir reprocessamento idempotente;
  - `claim(interpretation_unit_id)` e `claim(created_at)` – para busca por janela temporal;
  - `truth_record(claim_id, current_state)` – para localizar rapidamente o estado atual por claim;
  - `debunk_issue(target_type, target_id, status)` – para localizar issues ativas.

**Contrato de integração:**
- Todos os serviços escrevem/leem o banco exclusivamente via modelos ORM e repositórios documentados no 3.3; não há acesso “ad hoc” direto a tabelas por SQL hardcoded fora de pontos controlados (migrações, scripts de sanidade).
- Transações são usadas para garantir invariantes cruciais, por exemplo: criação de `IngestionRun` + inserção de `IngestionItemRaw` + marcação de status da run; ou alteração de `TruthRecord` + criação de `TruthChangeEvent`.
- Migrações são versionadas e mapeadas a gates específicos (Sx_G1, Sx_G2, etc.), que rodam em CI e localmente.

Comportamento em falhas:
- se o banco estiver indisponível ou em estado de erro, nenhum serviço deve tentar “cachear” decisões de verdade ou claims apenas em memória: a resposta adequada é falhar rápido, registrar logs estruturados e, quando aplicável, marcar execuções (`IngestionRun`, tarefas de debunker) como `FAILED` ou `PARTIAL_SUCCESS`.

---

### 3.4.3 – Mensageria e eventos (barramento assíncrono)

O barramento de eventos é a espinha dorsal da comunicação assíncrona entre ingestão, cérebro, comitês, debunker e Truth‑DB.

**Tipos de eventos mínimos na sprint:**
- `ingestion.item.normalized` – emitido ao criar `IngestionItemNormalized`;
- `interpretation.unit.created` – emitido ao criar `InterpretationUnit`;
- `claim.created` – emitido ao criar `Claim`;
- `committee.decision.made` – emitido ao registrar `CommitteeDecision`;
- `debunk.issue.opened` e `debunk.issue.resolved` – emitidos na abertura e resolução de `DebunkIssue`;
- `truth.state.changed` – emitido a cada `TruthChangeEvent`.

**Contrato de cada evento:**
- Payload segue exatamente os modelos descritos no 3.3, incluindo:
  - IDs primários das entidades;
  - campos de estado relevantes (por exemplo, `final_verdict`, `uncertainty_score` para `committee.decision.made`);
  - `trace_id` obrigatório para rastreio ponta‑a‑ponta;
  - carimbo `emitted_at`.

**Propriedades da mensageria:**
- entrega **pelo menos uma vez**;
- particionamento por chave lógica (tipicamente `claim_id` ou `source_id`) para preservar ordem local quando necessário;
- mecanismo de DLQ (dead‑letter queue) para mensagens mal-formadas ou não processáveis.

Integração dos serviços:
- Ingestion Workers **só** publicam novos itens normalizados via `ingestion.item.normalized`;
- Interpreter/Classifier consomem `ingestion.item.normalized` e publicam `interpretation.unit.created` e `claim.created`;
- Committee Engine consome `claim.created` (e outros sinais) e publica `committee.decision.made`;
- Debunker consome tanto eventos de decisão quanto eventos de contestação e publica `debunk.issue.*`;
- Truth‑DB consome `committee.decision.made` e `debunk.issue.resolved` e publica `truth.state.changed`.

Comportamento em falhas:
- Erros transitórios na mensageria (p. ex., timeout na publicação) devem gerar retries com backoff exponencial;
- Mensagens que não podem ser parseadas ou causam erros sistemáticos vão para DLQ com log estruturado apontando `event_type`, `trace_id` e causa;
- Nenhum serviço deve “inventar” estados intermediários de claims ou truths apenas em função da falha de envio/consumo de eventos: as decisões de verdade sempre derivam de registros persistidos em banco.

---

### 3.4.4 – Fontes externas: notícias, dados abertos e APIs oficiais

A sprint depende de integrações com fontes externas de informação, em especial:
- **Fontes de notícias** (feeds RSS/Atom, APIs de portais de notícias);
- **Fontes de dados abertos** (portais de dados governamentais, IBGE, bancos centrais, órgãos estatísticos);
- **APIs financeiras** (cotações, séries temporais de indicadores), quando aplicável ao escopo.

Essas dependências são encapsuladas por um conjunto de **clientes externos** (por exemplo, `NewsClient`, `OpenDataClient`, `FinanceClient`), cada um com:
- endpoint base bem definido;
- mecanismo de autenticação explícito (chave de API em header, OAuth, nenhum);
- timeouts padrão por tipo de fonte (ex.: notícias ≤ 5s, dados pesados ≤ 15s);
- política de retry com limite de tentativas e backoff.

Contrato de integração:
- nenhuma chamada HTTP para fontes externas é feita “na mão” diretamente em código de worker; tudo passa pelos clientes externos compartilhados;
- respostas são sempre convertidas para estruturas internas estáveis (`payload_raw` de `IngestionItemRaw`), registrando também metadados de status HTTP, headers importantes e possíveis códigos de erro;
- erros de rede, timeouts ou respostas mal‑formadas resultam em:
  - registro em `SourceHealthCheck` com `status = DEGRADED` ou `DOWN`;
  - marcação apropriada da `IngestionRun` (`FAILED` ou `PARTIAL_SUCCESS`);
  - logs estruturados com a combinação (`source_id`, `ingestion_run_id`, `error_code`).

Limites e governança:
- Respeito estrito a rate limits documentados, com backoff e, se necessário, circuito de proteção (circuit breaker) para não derrubar fontes externas.
- Uso de caches temporários quando fizer sentido (por ex., dados estáticos ou muito lentos), sempre configurados do lado dos clientes externos, nunca “espalhados” em serviços.

---

### 3.4.5 – Evidence Vault: armazenamento de artefatos de evidência

O Evidence Vault é a infra responsável por armazenar artefatos brutos usados como evidência (`Evidence`): snapshots HTML de notícias, PDFs, CSVs, imagens e outros arquivos.

Características contratuais:
- interface tipo objeto (S3‑like): `put_object`, `get_object`, `list_object_versions`;
- objetos identificados por chaves estáveis que são armazenadas em `Evidence.uri`;
- política de imutabilidade lógica: uma vez que um artefato é usado como base de decisão de comitê ou truth, sua versão específica deve permanecer acessível.

Integração com modelos de dados:
- Ao criar uma `Evidence` do tipo `OFFICIAL_DATASET` ou semelhante, o sistema deve:
  - salvar o artefato bruto no vault;
  - registrar em `metadata` detalhes relevantes (hash do arquivo, tamanho, formato, fonte);
  - usar o hash para validar integridade futura.

Comportamento em falhas:
- se o vault estiver indisponível, a criação de `Evidence` pode falhar ou ser rebaixada (ex.: evidência marcada como `PENDING_UPLOAD`), mas decisões de comitê não devem ser tomadas com base em evidência inexistente;
- leitura de artefatos falhando deve ser registrada com logs estruturados e, se afetar revalidações automáticas, deve disparar tarefas de reprocessamento.

---

### 3.4.6 – Observabilidade, métricas e logs

A stack de observabilidade é tratada como uma integração essencial, porque o Inspectah só é confiável se for possível enxergar claramente o que está acontecendo.

Dependências típicas:
- **Tracing**: SDK de tracing (ex.: OpenTelemetry) integrado no entrypoint de cada serviço;
- **Métricas**: cliente de métricas (Prometheus/StatsD) expondo counters, gauges e histograms para operações críticas;
- **Logs estruturados**: saída padronizada em JSON ou formato equivalente, coletada por agente (ex.: Loki/Fluentbit).

Contrato de observabilidade:
- toda requisição HTTP relevante e toda operação crítica (criação de `IngestionRun`, `Claim`, `CommitteeDecision`, `TruthRecord`, `DebunkIssue`) gera logs estruturados com, no mínimo: `trace_id`, IDs das entidades, resultado, duração e erros;
- métricas mínimas:
  - latência de endpoints administrativos (`/admin/sources`, `/admin/ingestions`);
  - throughput de ingestão (items/segundo, runs/hora);
  - contagem de claims criadas por fonte e tipo;
  - contagem de decisões por tipo de veredito (`TRUE`, `FALSE`, `UNDECIDED`, `CONTESTED`);
  - número de `DebunkIssue` abertas, em revisão e resolvidas;
  - número de mudanças de estado na Truth‑DB.
- traços distribuídos conectam ingestão → interpretação → claim → comitê → debunker → truth via `trace_id`.

Esses sinais são usados diretamente pelos gates da sprint: por exemplo, limites mínimos de cobertura de métricas ou ausência de erros sistemáticos em ingestão antes de um GO.

---

### 3.4.7 – Segurança, segredos e limites de escopo

As integrações da sprint dependem de um mecanismo único de gestão de segredos (vault ou variáveis de ambiente gerenciadas por ambiente), e de políticas claras de manuseio de dados sensíveis.

Regras contratuais:
- chaves de API, tokens e credenciais de banco **nunca** aparecem em código-fonte, logs, eventos ou scorecards;
- acesso a fontes externas que possam conter dados pessoais é feito apenas quando estritamente necessário, e sempre com avaliação prévia de escopo;
- modelos de `Evidence` e payloads de eventos não transportam diretamente dados pessoais identificáveis, salvo quando indispensáveis e alinhados com requisitos legais (ex.: em fases futuras com LGPD totalmente modelada).

Integração com autenticação/autorização:
- endpoints administrativos (`/admin/*`) só são acessíveis a usuários ou serviços autenticados e com permissões adequadas;
- quaisquer integrações B2B futuras (por exemplo, consoles de parceiros) devem usar chaves ou tokens dedicados, mantidos no vault e rotacionáveis.

---

### 3.4.8 – Matriz de integrações e comportamento em falhas

Para fechar, o 3.4 apresenta uma **matriz de integrações**, que funciona como visão tabular entre componentes e dependências. Para cada componente principal, são listadas:
- dependências diretas (banco, filas, clientes externos, vault, observabilidade);
- operações principais com essas dependências (CRUD, publicação/consumo de eventos, upload/download de objetos);
- comportamento esperado em falhas (retries, fallback, marcação de status, geração de logs/métricas específicas).

Exemplos (a serem detalhados na sprint concreta):

- **Ingestion Worker**  
  - Depende de: banco (para `IngestionRun`, `IngestionItemRaw`, `IngestionItemNormalized`), mensageria (para `ingestion.item.normalized`), clientes HTTP (fontes), Evidence Vault (snapshots, se configurado), observabilidade.  
  - Em falha de fonte externa: registra `SourceHealthCheck`, marca run como `PARTIAL_SUCCESS` ou `FAILED`, não gera claims sem dados.  
  - Em falha de banco: interrompe processamento, registra erro crítico, deixa run pendente para reprocessamento.  
  - Em falha de mensageria: armazena itens normalizados, marca para publicação posterior ou falha a run com log estruturado.

- **Committee Engine**  
  - Depende de: banco (para `Claim`, `Evidence`, `CommitteeEvaluation`, `CommitteeDecision`), mensageria (para `committee.decision.made`), observabilidade.  
  - Em falha de banco: não emite decisões “em memória”; processamento é abortado e refeito quando o banco voltar.  
  - Em falha de mensageria: registra a decisão em banco, tenta republicar; se falhar, registra item em fila local ou tabela de `pending_events`.

- **Truth‑DB Service**  
  - Depende de: banco (para `TruthRecord`, `TruthChangeEvent`), mensageria (para consumir decisões e debunk), observabilidade.  
  - Em falha de mensageria: não avança estados; a verdade oficial só muda com base em eventos consumidos e persistidos.  
  - Em falha de banco: nenhuma mudança de estado é aplicada; qualquer tentativa gera erro previsível para o chamador.

Essa matriz, quando preenchida para a sprint específica, serve como referência final para a equipe de desenvolvimento, QA e SRE: ela diz **onde o sistema pode quebrar, como deve quebrar e como deve se recuperar**, mantendo alinhamento com a modelagem de dados (3.3) e com os gates definidos no Capítulo 2.

