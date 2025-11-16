# D9.0 — Inspectah Blueprint Consolidado (v1.2.x)
> Status: CONGELADO (LOCKED) — Inspectah D9 v1.1 — não editar fora de novas sprints ou PATCH_D9 explícito.

> "Inspectah é o painel de controle de evidências do ecossistema CE/MBP." — Cap.1

## 1. Mandato e Objetivo
- Transformar o Inspectah em um **hub único de dados, evidências e trilhas de auditoria** para suportar decisões do CE/MBP e de oráculos parceiros.
- Fornecer especificação suficiente para que um time de engenharia (humano ou assistido pelo Codex) implemente o v0 sem perguntas estruturais em aberto.
- Garantir aderência ao DNA MBP: Inspectah **não executa payouts**, não substitui o oráculo principal e não conflita com os Blocos 0–5.

## 2. Problema Atual e Alvos de Sucesso
| Dor Atual | Contrapartida proposta pelo Inspectah |
|-----------|---------------------------------------|
| Fontes espalhadas, sem histórico consolidado | Registro versionado de itens, manifests e evidências em único vault |
| Verificações manuais repetitivas | Pipelines parametrizáveis com Field Designer e alertas configuráveis |
| Decisões baseadas em prints e links frágeis | Evidências armazenadas, assinadas e vinculadas a cada decisão |
| Dificuldade para plugar novas fontes | Modelagem declarativa com transforms e validações padronizadas |

**Critérios de sucesso v0**
1. Qualquer item exposto no Inspectah possui origem rastreável (URL + snapshot opcional) e campos estruturados derivados via Field Designer.
2. Fontes podem ser cadastradas/atualizadas sem alterar código, apenas compondo pipelines declarativas.
3. O módulo Explore entrega consultas filtráveis/paginadas em até 3 s para 95% dos requests com dataset de até 1M itens.
4. Toda extração/transformação respeita limites LGPD/ToS descritos em D9.5.

## 3. Escopo IN / OUT da Sprint D9
**IN**
- Definição detalhada de blueprint, anexos técnicos, roadmap e superprompt.
- Contratos de dados (tipos, transforms, APIs, DDL) e guardrails legais.
- Evidências de gates e backlog de lições.

**OUT**
- Implementação de código, deploys, watchers específicos de observabilidade.
- Integrações profundas com UMA/Reality ou oráculos externos (apenas modelo plugável).
- Design visual pixel-perfect; cobrimos fluxos funcionais.

## 4. Personas e Jornadas-Chave
### 4.1 Personas
- **Operator**: configura fontes, mapeia campos, monitora ingestão e qualidade.
- **Requestor/Analista**: explora dados, exporta evidências, referencia itens em decisões.
- **Codex/Engineering Lead**: implementa serviços com base nos docs D9.x.
- **Audit/Compliance**: valida aderência a LGPD/ToS e responde a auditorias.

### 4.2 Jornadas Canônicas
1. **Coleta periódica**: Operator cadastra fonte → Field Designer normaliza → Pipeline grava item + manifest → Alertas notificam diffs relevantes.
2. **Exploração investigativa**: Requestor aplica filtros em Explore → analisa detalhe com histórico/diffs → exporta CSV e referencia Evidence Vault.
3. **Suporte a resolução de mercado**: Oráculo consulta conjunto de itens do Inspectah → anexa à decisão → Auditoria consegue reproduzir contexto.
4. **Onboarding de nova fonte**: Operator cria pipeline nova, simula transformações, recebe validação LGPD/ToS antes de ir a produção.

## 5. Arquitetura Lógica
```
[Ingestão de Fontes]
    ↳ Fetchers (HTTP/RSS/API)        ↘
                                      [Field Designer]
                                       ↳ Tipos + Transforms + Computed Fields
                                            ↓
                                    [Pipelines de Indexação]
                                            ↓
                              [Storage] — Source / Item / ItemKV / Evidence Vault / FTS
                                            ↓
                                   [Explore API + Webhooks]
                                            ↓
                            [Consumers] — MBP, BI interno, scripts, auditores
```
Componentes auxiliares: Scheduler, Monitor de jobs, Guardião LGPD/ToS, módulo de export.

## 6. Componentes Principais
### 6.1 Field Designer
- Editor declarativo usado por Operators para definir campos, transforms e validações.
- Cada FieldDefinition possui versão, owner e política de fallback.
- Vide D9.2 para gramática completa.

### 6.2 Pipelines de Ingestão
- Construídos sobre jobs batelada (cron) ou gatilhos de webhook.
- Passos fixos: coleta → normalização → enriquecimento (computed fields) → persistência → indexação FTS → emissão de eventos.

### 6.3 Evidence Vault
- Armazena manifest JSON + snapshot bruto (HTML/TXT/JSON). Snapshots são opcionais e obedecem LGPD/ToS.
- Cada manifest contém: hash do payload, URL de origem, timestamp de coleta, versão do Field Designer.

### 6.4 Explore Surfaces
- API REST + painel (futuro) + exports + webhooks.
- Filtros por campos normalizados, tags e metadados da fonte.

### 6.5 Governança LGPD/ToS
- Checklist obrigatório antes de ativar fonte.
- Flags por fonte: `data_personal`, `requires_consent`, `robots_ok`.
- Alertas automáticos se fonte muda ToS ou se detecção heurística identifica PII não autorizado.

## 7. Fluxo End-to-End
1. **Cadastro de Fonte**: Operator define parâmetros (URL/base API, autenticação, periodicidade, limites de coleta, política de snapshot).
2. **Configuração de Campos**: Field Designer recebe exemplos, mapeia `raw_field -> typed_field`, aplica transforms e computed fields.
3. **Execução de Job**: Scheduler chama fetcher, registra execução e metadados (latência, status HTTP, bytes transferidos).
4. **Persistência**: Item + ItemKV + Evidence Vault são gravados em SQLite (dev) ou Postgres (prod). Indices FTS atualizados.
5. **Eventos de Saída**: Explore API disponibiliza dados. Webhooks enviam `item.created`/`item.updated`/`source.error`. Export jobs podem ser agendados.
6. **Auditoria**: Evidence Vault garante reprodutibilidade. Logs de pipeline + manifest formam linha do tempo confiável.

## 8. Requisitos Funcionais do v0
1. Cadastro de fontes com autenticação básica/token, agenda e política de retenção.
2. Biblioteca mínima de transforms (parse_date, parse_number, regex_extract, map_table, concat, math básica).
3. Suporte a computed fields determinísticos utilizando apenas dados do item atual.
4. Persistência de items com histórico completo; nenhum update destrói versões anteriores.
5. Explore API com filtros por `source_id`, `tags`, `field:value`, intervalo temporal e ordenação.
6. Export em CSV/JSON com limites configuráveis e paginação.
7. Webhooks configuráveis com HMAC opcional.
8. Painel (ou CLI) para consulta rápida de status das fontes e jobs.

## 9. Requisitos Não Funcionais e SLOs
- **SLO consulta**: 95% das requisições GET `/items` ≤ 3 s com carga de 1M itens; 99% ≤ 6 s.
- **SLO ingestão**: jobs recorrentes devem completar ≥ 99% das execuções programadas em até 2x o tempo médio da fonte.
- **Auditoria**: cada item guarda referência criptográfica (hash SHA-256) do snapshot quando habilitado.
- **Disponibilidade**: 99% mensal para Explore API (v0 pode rodar em HA leve; downtime planejado documentado).
- **Observabilidade mínima**: logs estruturados, métricas de job (sucesso, falha, duração), contadores por fonte.

## 10. Métricas e KPIs
| Métrica | Definição | Meta v0 |
|---------|-----------|---------|
| Cobertura de fontes saudáveis | % de fontes ativas sem falha nos últimos 7 dias | ≥ 90% |
| Latência média de ingestão | Tempo entre coleta e item disponível no Explore | ≤ 5 min |
| Itens com manifest completo | % de itens com snapshot + hash registrado | ≥ 95% nas fontes que permitem |
| Alertas LGPD/ToS tratados | % de alertas resolvidos em ≤ 48h | 100% |

## 11. Integrações e Dependências
- **Com MBP/Oráculo**: Inspectah expõe dados; MBP consome via webhooks/jobs batch. Nenhum acoplamento direto aos contratos on-chain.
- **Com DNA**: Field Designer e Data Model herdam convenções de nomenclatura e versionamento do MBP (prefijos, IDs, timezone UTC).
- **Plugins Externos**: suporte a adapters custom (ex.: UMA) descrito como extensão do pipeline, sempre opt-in.

## 12. Guardrails e Riscos
| Risco | Mitigação |
|-------|-----------|
| Uso indevido de dados pessoais | Checklist LGPD/ToS por fonte + flags automáticas + retenção diferenciada |
| Dependência excessiva de scraping | Priorizar APIs/feeds oficiais; scraping só com robots.txt permitido e throttle configurado |
| Divergência entre spec e implementação | Superprompt D9.7 e checklists garantem aderência; lições registradas em Cap.4 |
| Crescimento descontrolado de schema | Field Designer versionado + playbook D9.8 para evoluções |

## 13. Conexão com Roadmap
- **v0**: Core Data Hub (ingestão batch, Field Designer básico, Explore API, Evidence Vault, guardrails LGPD).
- **v1**: automação de diffs, alerts configuráveis, integrações com módulos MBP críticos.
- **v1.x**: otimizações de desempenho, watchers de observabilidade dedicados, connectors premium.
(Detalhes em D9.6.)

## 14. Traçado com os Demais D9.x
| Documento | Papel no Blueprint |
|-----------|--------------------|
| D9.1 | Narrativa resumida para onboarding rápido |
| D9.2 | Contrato do Field Designer mencionado nas seções 6.1 e 7 |
| D9.3 | Define Explore/API citada nas seções 6.4 e 8 |
| D9.4 | Materializa modelo de dados descrito em 6.3 e 7 |
| D9.5 | Implementa guardrails da seção 6.5 e dos riscos |
| D9.6, D9.8 | Expandem seções 13 e 12 com roadmap e governança |
| D9.7 | Ponte para execução das decisões deste blueprint |

## 15. Glossário
- **Field Designer**: ferramenta declarativa para mapear e transformar campos.
- **Manifest**: payload JSON com metadados da coleta (hash, fonte, momento, versão).
- **Evidence Vault**: armazenamento imutável dos manifests e snapshots.
- **Inspectah Explore**: camada de consulta/integração (API, exports, webhooks).
- **Source**: configuração de ingestão (endpoint, agenda, política LGPD).
- **Item**: registro estruturado resultante de uma execução de pipeline.

Este blueprint consolida a visão do Inspectah e serve de referência primária para todos os anexos e gates da Sprint D9.
