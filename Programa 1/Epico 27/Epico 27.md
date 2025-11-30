# Épico E27 — Fontes & Ingestão 2.0 em Operação

> Programa 1 — Consolidação & Consoles Full  
> Dono lógico: Squad Fontes & Ingestão (Michael Stonebraker, Kelsey Hightower, Charity Majors, Kent Beck, Steve Jobs)

---

## 1. Identidade do épico

**Código:** E27  
**Nome curto:** Fontes & Ingestão 2.0 em Operação  
**Programa:** Programa 1 — Consolidação & Consoles Full (S26–S32)  
**Status:** Em design (ajustar quando entrar em execução)  

**Resumo em uma frase:**

> E27 garante que o Inspectah consiga cadastrar, operar e manter fontes em produção de forma previsível, observável e recuperável – da ficha da fonte ao status da ingestão diária – sem depender de malabarismo manual ou scripts obscuros.

---

## 2. Problema

Hoje (ou sem E27) o cenário de Fontes/Ingestão tende a ser este:

- Cadastro de fontes feito de forma semi-ad hoc, com campos diferentes por tipo e sem contratos claros.  
- Ausência de um **modelo único** de fonte (campos obrigatórios, estados, metadados de operação).  
- Ingestão vista como caixa preta: "funciona até parar". Quando dá problema, o operador não sabe se a culpa é da fonte, do pipeline, da rede, do parser, do agendamento ou de tudo junto.  
- Falta de **painel operacional único** com visão de saúde, backlog, erros e reprocessamentos.  
- Não há uma forma padrão de colocar uma fonte em produção, tirá-la de produção, pausar, reativar, forçar backfill, etc.

Isso é incompatível com a ambição do Inspectah de ser um "oráculo de dados" confiável. Se as fontes e a ingestão não forem operáveis como um sistema nervoso previsível, todo o resto (verdade, blocos, debunker, casos) fica apoiado em areia.

E27 existe para transformar Fontes + Ingestão em um sistema **operável**, não um conjunto de scripts aleatórios.

---

## 3. Visão & Estado-alvo do épico

### 3.1 Frase de visão

> Quando E27 estiver completo, qualquer operador consegue, a partir do Console de Fontes/Ingestão, responder rapidamente: "o que estamos puxando de onde", "o que está saudável ou doente" e "o que preciso fazer agora" – com ações padrão para colocar fontes em produção, pausar, corrigir erros e reprocessar.

### 3.2 Estados-alvo (lista canônica)

Ao final de E27, será verdade que:

1. **Existe um modelo único de Fonte v2.0**, com campos obrigatórios, opcionais e metadados operacionais (tipo, origem, credenciais, SLA, domínios, tags, owner, criticidade, etc.).
2. **Toda fonte cadastrada passa por um ciclo de vida explícito**, com estados definidos (ex.: draft, em validação, ativa, pausada, deprecada) e transições controladas.
3. **A ingestão de cada fonte possui estados operacionais claros**, com histórico de execuções, sucessos, falhas, latência, volume e erros mais recentes.
4. **O Console de Fontes/Ingestão expõe uma visão consolidada de saúde**, permitindo filtrar e priorizar problemas (ex.: fontes críticas vermelhas primeiro).
5. **Existem ações padrão de operação**: testar fonte, colocar em produção, pausar, reativar, disparar ingestão manual, pedir backfill, agendar janelas específicas.
6. **Eventos relevantes de ingestão geram logs e métricas estruturados**, conectados à camada de observabilidade do Inspectah (Sprints de Observabilidade e Programa 7).
7. **Runbooks básicos de operação de Fontes/Ingestão estão definidos**, ligados a estados/erros específicos, ajudando o operador a saber qual é o próximo passo.

Esses estados são o contrato do épico. Sprints de Programa 1 que mexerem com Fontes/Ingestão precisam apontar para quais dessas frases estão tornando verdade.

---

## 4. Escopo IN / OUT

### 4.1 Escopo IN

E27 cobre, no mínimo:

- Definição do **modelo de Fonte v2.0** (schema lógico), incluindo:
  - identificação da fonte (nome, slug, tipo);  
  - tipo de origem (RSS, API REST, CSV remoto, dataset público, banco, etc.);  
  - parâmetros de conexão (URLs, headers, auth, chaves, etc.);  
  - domínios/temas atendidos (política, economia, clima, esportes, etc.);  
  - criticidade e SLA esperada (ex.: deve atualizar a cada X minutos/horas);  
  - owner/contato (quem é responsável pela fonte);  
  - flags de compliance (LGPD, assinatura, paywall, etc.).

- Definição do **ciclo de vida da fonte**, com estados (exemplo):
  - `draft` (criada, ainda não validada);  
  - `em_validacao` (testes de ingestão em ambiente de teste);  
  - `ativa` (rodando em produção);  
  - `pausada` (temporariamente suspensa);  
  - `deprecada` (não será mais usada, mas histórico preservado).

- Definição do **modelo de Execução de Ingestão** por fonte:
  - registro de cada execução (timestamp, duração, sucesso/falha, contagem de itens, erros de parsing);  
  - agregados por período (últimas 24h, 7 dias, 30 dias);  
  - estados de saúde (saudável, degradada, quebrada, desconhecida).

- Criação/ajuste do **Console de Fontes/Ingestão** (UI/Admin) para:
  - listar fontes com status, criticidade, últimos erros e ações rápidas;  
  - permitir filtro por tipo, estado, criticidade, domínio, owner;  
  - abrir detalhe da fonte (configuração + histórico de ingestão);  
  - executar ações padrão (testar, ativar, pausar, reativar, rodar ingestão, pedir backfill).

- Integração com **observabilidade**:
  - métricas básicas de ingestão por fonte (contagem, latency, erro);  
  - logs estruturados por execução, com correlação para debug.

- Definição de **runbooks mínimos** para cenários típicos (ex.: "fonte parou de entregar", "erro de autenticação", "schema mudou", "rate limit").

### 4.2 Escopo OUT

E27 **não** cobre:

- Ingestão 3.0 avançada com orquestração multi-fonte e missão (isso é Programa 7).  
- Sistema completo de priorização automática de ingestão com Machine Learning.  
- Interface pública para parceiros configurarem suas próprias fontes (Fase 2).  
- Pipelines de transformação de dados complexos (DBT/BigQuery) além do mínimo necessário para ingestão básica.  
- Política avançada de custo/limite de ingestão (isso pode ser tocado em Programas de governança/custos).

---

## 5. Personas & casos de uso

### 5.1 Personas

- **Operator de Fontes** — responsável por cadastrar e manter fontes funcionando.  
- **Operator de Ingestão** — foca na saúde dos pipelines, volumes e latência.  
- **Truth/Case Operator** — não mexe em ingestão diretamente, mas precisa entender se dados de uma fonte estão atrasados ou problemáticos.  
- **SRE/Observability** — investiga problemas sistêmicos e correlaciona ingestão com infra.

### 5.2 Casos de uso principais

1. **Cadastrar uma fonte nova**
   - Operador preenche campos obrigatórios (tipo, URL, auth, SLA, domínio, owner).  
   - Roda teste de ingestão (em ambiente controlado).  
   - Ajusta parâmetros conforme feedback (latência, erros).  
   - Promove a fonte de `draft` → `em_validacao` → `ativa`.

2. **Ver o estado operacional das fontes**
   - Operador acessa lista de fontes.  
   - Ordena por criticidade e filtra por `saúde = degradada/quebrada`.  
   - Vê últimas execuções, erros e contexto (desde quando está ruim).  
   - Usa ações rápidas (pausar, tentar reprocessar, abrir runbook).

3. **Responder à pergunta: “Estamos puxando direito deste domínio?”**
   - Usuário filtra fontes por domínio (ex.: eleições) e por criticidade.  
   - Vê quais fontes estão saudáveis, degradadas ou quebradas.  
   - Consegue dizer, com confiança, se os dados daquele tema estão atualizados.

4. **Reagir a uma falha de ingestão**
   - Console mostra fontes em vermelho com último erro.  
   - Operador clica e vê detalhe da execução, logs relacionados e sugestão do runbook.  
   - Decide entre corrigir config, pausar fonte, reprocessar ou escalar para SRE.

---

## 6. Modelo de dados (lógico) do épico

### 6.1 Entidade Fonte

Campos principais (lógico; implementação física depende do modelo atual):

- `id`  
- `nome`  
- `slug`  
- `tipo_origem` (`rss`, `api_rest`, `csv_http`, `dataset_publico`, etc.)  
- `config_conexao` (objeto JSON com URLs, headers, auth, etc.)  
- `dominios` (lista de domínios/temas)  
- `criticidade` (`alta`, `media`, `baixa`)  
- `sla` (ex.: "a cada 15 min")  
- `owner` (pessoa/time responsável)  
- `estado` (`draft`, `em_validacao`, `ativa`, `pausada`, `deprecada`)  
- `flags_compliance` (ex.: `requer_assinatura`, `dados_pessoais`, etc.)  
- `created_at`, `updated_at`.

### 6.2 Entidade Execução de Ingestão

- `id`  
- `fonte_id`  
- `timestamp_inicio`  
- `timestamp_fim`  
- `status` (`sucesso`, `falha`, `parcial`, `cancelada`)  
- `itens_processados`  
- `itens_validos`  
- `itens_descartados`  
- `erro_principal` (código + mensagem resumida)  
- `detalhes_erro` (JSON com stack, payloads, etc., ou referência para logs externos)  
- `origin_run_id` (referência para pipeline/engine, se existir)  
- `latencia_segundos`.

### 6.3 Entidade Saúde da Fonte (derivada)

- `fonte_id`  
- `health_status` (`saudavel`, `degradada`, `quebrada`, `desconhecida`)  
- `motivo` (ex.: "3 falhas consecutivas nas últimas 24h")  
- `desde_quando` (timestamp)  
- `ultimo_sucesso`, `ultima_falha`  
- `indicadores` (objeto com contagens por período).

---

## 7. Requisitos funcionais

### 7.1 Cadastro & edição de fontes

- O sistema deve permitir criar, editar e visualizar fontes com base no modelo v2.0.  
- Validações mínimas: campos obrigatórios, formatos de URLs, compatibilidade de auth com tipo_origem.  
- Mudanças de `estado` devem seguir regras de transição (não pode ir de `draft` direto para `deprecada`, por exemplo, sem histórico).  
- Logs de alteração devem registrar quem alterou o quê e quando.

### 7.2 Execução de ingestão

- O sistema deve permitir:
  - execuções automáticas (agendadas) conforme SLA;  
  - execuções manuais disparadas por operador (`rodar agora`);  
  - backfills limitados (ex.: reprocessar últimos X dias) com proteções de volume.

- Cada execução deve gerar um registro em `Execução de Ingestão` e logs associados.

### 7.3 Console de saúde de Fontes/Ingestão

- Tela de lista com:
  - nome da fonte;  
  - tipo;  
  - domínios;  
  - criticidade;  
  - estado;  
  - health_status;  
  - último sucesso/falha;  
  - ações rápidas (testar, pausar, ver erros).

- Filtros: por criticidade, estado, tipo, health_status, domínio, owner.  
- Ordenação: por criticidade, health_status, tempo desde última falha, tempo desde último sucesso.

### 7.4 Ações operacionais padrão

A partir do Console:

- `testar fonte` (em modo dry-run/sem comitar dados);  
- `ativar` (colocar em produção);  
- `pausar` (impedir novas ingestões automáticas);  
- `reativar`;  
- `rodar ingestão agora`;  
- `solicitar backfill` (com limites e avisos);  
- `abrir runbook` relacionado ao erro/estado atual.

### 7.5 Runbooks

- Para cada erro/estado recorrente, deve haver um runbook mínimo com:
  - descrição do problema típico;  
  - passos de diagnóstico;  
  - possíveis correções;  
  - quando escalar para SRE/engenharia.

- Runbooks podem ser simples no início (Markdown), mas precisam ser vinculados a estados reais no Console.

---

## 8. Requisitos não funcionais

### 8.1 Observabilidade

- Métricas mínimas por fonte:
  - `ingestao_execucoes_total`,  
  - `ingestao_execucoes_falha_total`,  
  - `ingestao_execucoes_sucesso_total`,  
  - `ingestao_latencia_p95`,  
  - `ingestao_itens_processados_total`.

- Logs estruturados para cada execução, com capacidade de busca por fonte, status, erro.

### 8.2 Resiliência e limites

- Proteções contra:
  - tempestade de backfills simultâneos;  
  - fontes mal configuradas disparando ingestão infinita;  
  - fontes mega volumosas derrubando o sistema.

- Limites configuráveis (por workspace/instância) para ingestões simultâneas e volume de backfill.

### 8.3 Consistência com E26

- O Console de Fontes/Ingestão deve seguir a gramática de UI/Admin definida em E26:  
  - mesma linguagem visual de estados;  
  - mesmos padrões de tabelas, filtros, ações;  
  - mensagens de erro/vazio consistentes.

---

## 9. Métricas de sucesso do épico

Indicadores para saber se E27 entregou valor real:

- **Tempo médio para diagnosticar problema de fonte**: queda significativa em relação ao baseline (medido em testes internos).  
- **Porcentagem de fontes com health_status = saudável** em janela típica (ex.: últimas 24h), especialmente entre fontes críticas.  
- **Número de incidentes de ingestão "caixa preta"** (onde a causa raiz fica obscura) reduzido.  
- **Taxa de sucesso de backfills e execuções manuais** (com logs claros).  
- **Aderência aos runbooks**: incidentes fechados seguindo passos definidos, não via gambiarra improvisada.

---

## 10. Decomposição em sprints

E27 é grande o suficiente para ser atacado em camadas, alinhadas com Programa 1.

### 10.1 Entregas sugeridas

- **E27.1 — Modelo de Fonte v2.0 + ciclo de vida básico + CRUD no Console**  
  - Schema de Fonte;  
  - estados `draft/em_validacao/ativa/pausada/deprecada`;  
  - tela de cadastro/edição aderente a E26.

- **E27.2 — Histórico de Execução + Saúde da Fonte + Console de saúde**  
  - registros de execução;  
  - cálculo de health_status;  
  - tela de lista de fontes com saúde e ações rápidas.

- **E27.3 — Operação diária & runbooks**  
  - ações padrão (testar/ativar/pausar/reativar/rodar agora/backfill);  
  - integração com observabilidade e runbooks;  
  - ajustes finos de UX/Admin.

### 10.2 Relação com sprints S26–S32

- S26–S27 tendem a focar em E26 + E27.1 (padrão de console + modelo de fonte/ciclo de vida).  
- S28–S29 podem focar em E27.2 (saúde + console de saúde) e primeiras integrações com observabilidade.  
- S30–S32 refinam E27.3 e conectam profundamente com Truth Ops e Programas seguintes.

---

## 11. Riscos, decisões e anti-objetivos

### 11.1 Riscos

- **Modelo de fonte genérico demais**: tentar abraçar todos os tipos antes de ter exemplos reais e travar.  
- **Console sobrecarregado**: tanta informação que o operador não consegue priorizar.  
- **Dependência forte de infra externa** (observabilidade, fila de ingestão) atrasando a entrega do básico.

### 11.2 Decisões de design esperadas

- Começar com um conjunto de tipos de fonte suportados (RSS, API simples, dataset HTTP) e expandir depois.  
- Priorizar clareza de estados e operações em poucas telas bem pensadas, em vez de múltiplas microtelas confusas.  
- Modelar saúde com heurísticas simples no começo (ex.: janelas, contagem de falhas) para não travar na "perfeição".

### 11.3 Anti-objetivos

- E27 **não** é para virar uma plataforma de ETL genérica estilo Airflow/DBT.  
- E27 **não** tenta automatizar toda e qualquer correção de problema de fonte; foco é dar visão e ferramentas para humanos qualificados agirem.

---

## 12. Conexão com outros épicos e programas

- **E26 (Console Full & Coerência de UI/Admin)**: E27 herda a gramática visual de consoles; qualquer tela nova de fontes/ingestão deve ser 100% aderente a E26.
- **E28 (Fluxo de Agentes Configurável v1)**: agentes podem depender da ingestão de certas fontes; a definição de fontes e sua saúde alimenta decisões de fluxos.
- **E29 (Debunker v1)** e **E30–E32 (Truth/Evidence/Case)**: dependem implicitamente de que os dados estejam chegando bem; E27 expõe se isso é verdade.
- **Programas 5–7**: E27 é pré-requisito operacional para métricas de verdade, governança e ingestão 3.0.

---

## 13. Notas finais

Este documento define a visão, escopo e contratos do **Épico E27 — Fontes & Ingestão 2.0 em Operação**.

Sprints do Programa 1 devem referenciar este épico explicitamente:

- No Cap.1 do Sprint Playbook (contexto, problemas, states-of-truth alvo).  
- No Cap.2 (gates e scorecards que validam estados de E27).  
- No Cap.3 (impacto em schema, APIs, filemap de Fontes/Ingestão).  
- No Cap.4 (Execution Matrix, tasks que avançam E27.1, E27.2, E27.3).

Qualquer mudança profunda na forma como o Inspectah lida com fontes e ingestão deve ser refletida neste épico antes de ser empurrada para novas sprints.