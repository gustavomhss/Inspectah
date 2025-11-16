# Inspectah — Sprint 2
## Capítulo 1 — Contexto, Objetivos e Entregáveis da Implementação v0 (Core Data Hub) — v2.0

> Sprint 2 = **backend do Inspectah v0 rodando em dev**, com fluxo **end‑to‑end funcionando e observável**, obedecendo rigorosamente a **D9 (spec)** e ao **Sprint Macro / Blocos 1–4** (Inspectah v0.1 Data Hub First++).
>
> D9 está CONGELADA (LOCKED) como spec de referência do Inspectah. O Sprint Macro e os Blocos 1–4 definem o **v0.1 completo**. A Sprint 2 implementa a **primeira fatia** desse objetivo: o **núcleo do Data Hub** em modo dev/lab.

---

## 0) Resumo em 30 segundos (pra humano)

Ao final da Sprint 2, queremos que qualquer engenheiro consiga:

1. Clonar o repositório do Inspectah, seguir o README e executar um comando único (por exemplo `bin/dev_up.sh` ou `docker compose up`) para subir o ambiente local do Inspectah v0.
2. Cadastrar uma fonte (ex.: uma API JSON ou fixture) via Field Designer v0 (API/CLI), definindo campos, tipos e computed fields em IEL.
3. Rodar um script de ingestão que popula essa fonte com dados reais ou representativos.
4. Consultar esses dados via Explore API v0 (curl/Postman/script), usando filtros e paginação.
5. Ver que evidências estão sendo registradas em um Evidence Vault v0 (Object Store + metadados no banco), em conformidade com LGPD/ToS.
6. Rodar um script de E2E que prova automaticamente esse fluxo completo (subir → schema → ingest → query → evidence) em uma máquina limpa de dev.

Se isso acontecer de forma reproduzível e estável, a Sprint 2 atingiu seu objetivo.

---

## 1) Propósito da Sprint 2

1. Entregar o **Inspectah v0** funcionando em ambiente de desenvolvimento, com:
   - Field Designer v0 (API/CLI) baseado na Inspectah Expression Language (IEL) definida em D9.2.
   - Explore API v0 (consulta/filtragem/paginação) em cima de dados de fontes cadastradas, conforme D9.3.
   - Evidence Vault v0 (Object Store compatível com S3 + metadados em banco), respeitando as regras de D9.4/D9.5.
   - Pipeline mínimo de ingestão para pelo menos **1–2 fontes reais ou representativas**.
   - Observabilidade básica (logs estruturados + métricas principais) para acompanhar ingestão, consultas e evidências.
   - Testes automatizados cobrindo o fluxo principal end‑to‑end.

2. Reduzir o risco estrutural da D9 testando, na prática:
   - o modelo de dados do Inspectah;
   - a IEL e o avaliador de computed fields;
   - a Explore API v0 com rate limit real;
   - o Evidence Vault v0 em região e modo de criptografia compatíveis com LGPD.

3. Construir uma base de código e scripts **limpa, previsível e fácil de evoluir**, alinhada ao filemap do Bloco 3, para que sprints futuras possam adicionar:
   - UI‑min (2 telas Fontes/Explore);
   - mais fontes e conectores;
   - hardening de produção (bench, probes, SLOs, ORR T2–T8);
   - integração profunda com o MBP.

4. Implementar apenas o escopo definido para **v0** no roadmap de D9.6/D9.8, preparando o terreno para o **v0.1 Data Hub First++** descrito no Sprint Macro e Bloco 1.

> Relação com o Capítulo 2 da Sprint 2: cada entregável S2.x descrito aqui será validado por **gates de implementação (build, testes, E2E, review)** definidos no Capítulo 2, com evidências claras — espelhando o espírito dos **T2–T8** do Bloco 2, mas adaptados ao contexto da Sprint 2.

---

## 2) Contexto e relação com D9 + Sprint Macro + Blocos 1–4

- **D9 (Sprint 1)**: consolidou o Inspectah como Data Hub First (D9.0–D9.8), definindo Field Designer/IEL, Explore API, modelo de dados, Evidence Vault e envelope LGPD/ToS, além de roadmap v0/v1/v1.x, miniplaybook de evolução e superprompt Codex.
- **Sprint Macro + Bloco 1**: definem a visão de **Inspectah v0.1 10/10**, incluindo: múltiplas fontes (RSS+APIs JSON), UI‑min, FTS, export CSV/JSON, bench com 50k itens, probe E2E contínuo, backups, SLOs e error budget, ToS/robots verificados em CI, etc.
- **Bloco 2**: estabelece gates T2–T8, scorecards, runners e formatos de artefatos para provar que o Inspectah v0.1 cumpre os SLOs e requisitos operacionais.
- **Bloco 3**: fixa o filemap/scaffold do repositório, runners `bin/orr_t*.sh`, `bin/orr_all.sh` e Makefile de orquestração.
- **Bloco 4**: descreve o plano de execução D1→D7 para levar o Inspectah v0.1 a “funcionando” (48h de uptime, one‑click demo, T2–T8 verdes).

A Sprint 2 não tenta entregar o **v0.1 completo**; ela implementa a **primeira onda (Wave 1)** desse plano, focada em:

- levantar o **núcleo do Data Hub** (serviço, dados, IEL, Explore básica, Evidence Vault, ingestão mínima);
- garantir **observabilidade e E2E local**;
- criar o terreno para que os itens mais pesados do Sprint Macro (UI‑min, FTS+bench 50k, probe contínuo, 10–15 fontes, ORR T2–T8 completo) possam ser realizados em sprints seguintes, sem retrabalho de base.

---

## 3) Escopo IN da Sprint 2 (o que DEVE ser entregue)

A Sprint 2 gera entregáveis de **código + scripts + docs**, agrupados como S2.x.

### 3.1 S2.0 — Infraestrutura base & scaffolding

- Estrutura do serviço Inspectah v0 (pastas, módulos, dependências mínimas), alinhada ao filemap do Bloco 3.
- Scripts para subir o ambiente de dev (por exemplo `bin/dev_up.sh` e/ou `docker-compose.yml`).
- Configuração básica de banco + Object Store (Evidence Vault), com pontos de configuração coerentes com D9.4/D9.5.
- Por que importa: sem esse scaffolding, nenhum outro entregável é reproduzível.

### 3.2 S2.1 — Field Designer v0 (engine + API/CLI)

- Implementação do core do Field Designer (entidades, validação, armazenamento de schemas de fonte).
- Implementação da Inspectah Expression Language (IEL) na prática, conforme D9.2:
  - operadores e funções permitidos;
  - escopo de leitura (campos da mesma linha/item);
  - pureza (sem I/O, sem efeitos colaterais);
  - política de fallback e erros.
- Endpoints ou comandos CLI para criar/atualizar/listar schemas e campos, com validação antes de persistir.
- Por que importa: o Field Designer define “o que é dado” dentro do Inspectah.

### 3.3 S2.2 — Explore API v0

- Implementação de endpoints de leitura conforme D9.3:
  - filtros por fonte, intervalo temporal e campos tipados;
  - paginação determinística (limit/offset ou cursor, conforme spec);
  - rate limit v0 implementado (120 req/min, burst 240) com cabeçalhos X‑RateLimit‑* e resposta 429 bem definida.
- Exemplos reais documentados (curl/Postman/scripts) e suportados por testes.
- Por que importa: a Explore API é a porta de saída do Inspectah para o MBP e para outros consumidores.

### 3.4 S2.3 — Evidence Vault v0

- Integração com CE Object Store (S3‑like) para gravação de evidências, na região e com criptografia definidos em D9.4/D9.5.
- Metadados de evidências persistidos no banco, ligados a fontes/itens/eventos, conforme modelo de dados da D9.
- Contrato mínimo claro (o que é armazenado, como é versionado, como é referenciado a partir de um item).

### 3.5 S2.4 — Pipeline de ingestão mínima

- Scripts/processos para ingestão de dados de pelo menos **1–2 fontes** (ou fixtures representativos), cobrindo:
  - registro da fonte;
  - definição do schema via Field Designer;
  - ingestão inicial (batch) e, se possível, incremental simples;
  - ligação com Evidence Vault quando fizer sentido.
- Definição explícita dos formatos de ingestão suportados no v0 (por exemplo CSV/JSON bem definidos).
- Documentação de como rodar essa ingestão localmente.

### 3.6 S2.5 — Observabilidade básica v0

- Logs estruturados nas principais rotas e operações:
  - definição de schema;
  - ingestão de dados;
  - chamadas à Explore API;
  - gravação no Evidence Vault.
- Métricas básicas expostas (mesmo que só localmente), incluindo pelo menos:
  - contagem de requests da Explore API;
  - contagem de respostas 429 (rate limit);
  - itens ingeridos por fonte;
  - erros por tipo (ingestão, query, evidence).

### 3.7 S2.6 — Testes & E2E local (script único)

- Conjunto mínimo, mas robusto, de testes unitários/internos para componentes críticos (IEL, validação de schema, ingestão básica, queries simples).
- Script E2E único (por exemplo `bin/run_inspectah_v0_e2e.sh`) que:
  1. sobe o ambiente de dev;
  2. cria schema via Field Designer;
  3. ingere dados em pelo menos uma fonte de exemplo;
  4. consulta via Explore API;
  5. verifica pelo menos uma evidência no Evidence Vault.
- Este script deve rodar em ambiente limpo de dev (repos freshly cloned + dependências mínimas) e será peça central dos gates da sprint.

### 3.8 S2.7 — Documentação operacional v0

- README operacional da Sprint 2/Inspectah v0, explicando:
  - como instalar dependências;
  - como subir o ambiente (comando único);
  - como rodar o script E2E;
  - exemplos de chamadas à API (curl/postman) com payloads reais.
- Seção ligando estes artefatos a D9.6/D9.8 (roadmap/evolução) e ao superprompt D9.7 (para orientar futuras sprints de implementação).

---

## 4) Escopo OUT da Sprint 2 (o que fica explicitamente para depois)

Os itens abaixo são parte do objetivo **v0.1 completo** do Sprint Macro e dos Blocos 1–4, mas **não** são entregáveis da Sprint 2. Eles devem aparecer como backlog para Sprints 3+.

1. **UI‑min (2 telas Fontes/Explore)**
   - Implementação de interface web mínima para operadores, com foco em onboarding ≤ 5 min e consultas ≤ 200 ms p95.

2. **Catálogo amplo de fontes (10–15 fontes ativas)**
   - Suporte a muitas fontes reais (RSS/APIs JSON diversas) e scheduling completo (cron, retries com jitter, backpressure mais sofisticado).

3. **FTS avançado e bench 50k**
   - Full‑text search, índices otimizados, bench com 50k itens e SLOs de latência p95/p99 sob carga definida no Bloco 1.

4. **Probe E2E contínuo e monitoração 24x7**
   - Probes automatizadas, rodando continuamente e emitindo scorecards/registros de saúde do Inspectah.

5. **Backup/Restore completo e runbooks avançados**
   - Estratégias e scripts de backup/restore com testes formais e runbooks detalhados para incidentes e takedown.

6. **ORR completo T2–T8 com scorecards em pipeline de CI/CD**
   - Implementação integral dos runners e gates do Bloco 2 (T2–T8) rodando em CI/CD, incluindo erro budget e política de congelamento.

7. **Hardening de produção (multi‑região, HA, IAM avançado, etc.)**
   - Multi‑região, alta disponibilidade, IAM/RBAC enterprise, OAuth/OIDC completo, cofre de segredos robusto, DLP guard avançado.

8. **Integração profunda e automatizada com o MBP em produção**
   - Hooks automáticos, watchers de mercado e pipelines que conectam Inspectah e MBP sem intervenção manual.

A Sprint 2 pode preparar terreno (por exemplo, deixar flags, estruturas ou testes esboçados), mas não deve considerar esses itens como "done".

---

## 5) Personas e fluxos mínimos que o v0 precisa atender

### 5.1 OracleOps / Operador do Inspectah

Fluxo mínimo, passo a passo:

1. Ler o README da Sprint 2 e instalar as dependências necessárias.
2. Executar um comando único (por exemplo `bin/dev_up.sh` ou `docker compose up`) para subir o ambiente local do Inspectah v0.
3. Chamar a API/CLI do Field Designer para criar uma nova fonte.
4. Definir o schema dessa fonte (campos, tipos, transforms, computed fields simples em IEL) via API/CLI, validando antes de salvar.
5. Rodar o script/CLI de ingestão de dados para essa fonte, usando um dataset de exemplo.
6. Usar a Explore API (ex.: via curl/postman) para fazer consultas filtradas nesse dataset.
7. Ver os logs e, se disponível, métricas locais para checar se houve erros, rate limit, ingestão com sucesso etc.

### 5.2 Integrador do MBP (engenheiro)

Fluxo mínimo, passo a passo:

1. Ler a documentação da Explore API v0 (endpoints, parâmetros, exemplos em D9.3 e README S2).
2. Preparar um script/serviço simples capaz de chamar a Explore API a partir de outro sistema (por exemplo, o MBP ou uma ferramenta de teste).
3. Fazer uma chamada autenticada/simples e receber dados em formato JSON consistente com o schema definido via Field Designer.
4. Validar que os campos retornados correspondem ao schema configurado.
5. (Opcional) Ler evidências ou metadados associados a certas fontes/consultas, conforme D9.4/D9.5.

### 5.3 Guardião LGPD / Risco

Fluxo mínimo, passo a passo:

1. Ler D9.4 e D9.5, mais a documentação da Sprint 2, para entender como o Evidence Vault v0 foi configurado.
2. Verificar, nas configs/código, que o Evidence Vault está em região e modo de criptografia compatíveis com o envelope definido (por exemplo CE Object Store em região sa‑east‑1 com SSE‑KMS).
3. Checar que os tipos de dados ingeridos nas fontes de exemplo estão dentro do que foi definido como aceitável em D9.5.
4. Garantir que não existem endpoints "esquecidos" que retornem dumps de dados sem controle (por exemplo lists gigantes sem filtro de fonte/escopo).

---

## 6) Critérios de sucesso da Sprint 2

A Sprint 2 será considerada bem‑sucedida se, ao final:

1. O Inspectah v0 puder ser subido em um ambiente limpo de dev com **um único comando/script documentado**, funcionando sem ajustes manuais obscuros.

2. Um operador técnico conseguir, seguindo apenas o README e usando o script de E2E (S2.6), executar o fluxo end‑to‑end:
   1. subir o ambiente;
   2. criar schema via Field Designer;
   3. ingerir dados em pelo menos uma fonte de exemplo;
   4. consultar via Explore API;
   5. verificar as evidências correspondentes.

3. Todos os S2.x estiverem implementados em nível v0 (mesmo que simples), sem buracos óbvios em relação à D9 e ao Sprint Macro.

4. As principais métricas e logs estiverem disponíveis para inspecionar problemas básicos (sem ficar "cego" durante o uso).

5. O backlog de lessons da Sprint 2 alimentar um plano claro para as próximas sprints (UI‑min, mais fontes, performance/bench, integração profunda com MBP, ORR completo).

6. As ações `BACKLOG_PROX_SPRINT` herdadas da D9 e relevantes para implementação (por exemplo, teste de carga da Explore API, monitoramento contínuo do Evidence Vault) estejam, no mínimo, refletidas no plano da Sprint 2 (scripts/esqueleto de testes, ganchos de observabilidade) e prontas para virarem trabalho direto nas próximas sprints.

---

## 7) Entradas obrigatórias para a Sprint 2

Antes de começar a implementação, os seguintes artefatos são **entrada obrigatória** para qualquer trabalho da Sprint 2:

1. Todos os arquivos da Sprint 1 (D9) congelada, especialmente:
   - D9.0 (blueprint consolidado do Inspectah).
   - D9.2 (Field Designer + IEL).
   - D9.3 (Explore API).
   - D9.4 (modelo de dados + DDL + migração).
   - D9.5 (LGPD/ToS/envelope de risco).
   - D9.6 (roadmap v0/v1/v1.x).
   - D9.7 (superprompt Codex Inspectah v0).
   - D9.8 (miniplaybook de evolução).
   - Capítulo 4 da Sprint 1 com retrospectiva D9.

2. Backlog em `d9_lessons_actions_backlog.md`, especialmente ações marcadas como `BACKLOG_PROX_SPRINT` ou `ALERTA_RISCO` relacionadas a:
   - teste de carga da Explore API (rate limit e performance);
   - monitoramento LGPD/Evidence Vault;
   - melhorias sugeridas para implementação v0.

Essas entradas são **contratos**, não sugestões. A Sprint 2 não pode redefinir o mandato do Inspectah descrito em D9.0/D9.1 nem ignorar as lições e ações herdadas.

---

## 8) Saídas esperadas da Sprint 2 (alto nível)

Ao final desta sprint, devemos ter:

- Código, scripts e configs que implementam o Inspectah v0, organizados e versionados em repositório alinhado ao filemap do Bloco 3.
- Documentação operacional suficiente para que um terceiro consiga rodar o sistema localmente (README + exemplos reais).
- Conjunto mínimo de testes garantindo que o fluxo principal funciona, incluindo o script de E2E S2.6.
- Atualização do backlog de lessons (agora da Sprint 2), apontando claramente o que entra nas próximas sprints (UI‑min, mais fontes, performance, integração profunda com MBP, ORR completo, etc.).

Os detalhes de **gates de implementação, evidências e forma de validação** serão definidos no **Capítulo 2 da Sprint 2**, que funcionará como o equivalente dos D9‑G0…G6 e dos T2–T8 do Bloco 2, porém focados em código, testes e operação.

---

## 9) Invariantes da Sprint 2

A Sprint 2 herda o espírito de contratos da D9 e do Sprint Playbook. Estas invariantes valem para todo o trabalho de implementação:

1. **Proibido divergir da D9/Sprint Macro sem registrar patch**
   - Qualquer decisão que entre em conflito com D9.0–D9.8, Sprint Macro ou Blocos 1–4 deve ser tratada como lição + ação (`PATCH_D9` ou `PATCH_DNA`) em `d9_lessons_actions_backlog.md`.
   - Não é permitido "resolver localmente" um conflito ignorando a D9.

2. **Mandato do Inspectah é imutável nesta sprint**
   - A Sprint 2 não pode redefinir o papel do Inspectah em relação ao MBP: ele continua sendo hub de dados / OracleOps, como definido em D9.0/D9.1 e Sprint Macro.
   - Qualquer tentativa de ampliar/encolher o mandato entra no backlog de discussões futuras, não no código desta sprint.

3. **Regra de ouro: divergência vira lesson, não gambiarra**
   - Qualquer choque entre spec e realidade deve virar entrada em `d9_lessons_log_raw.md` + ação em `d9_lessons_actions_backlog.md`.
   - A implementação deve seguir a solução escolhida de forma explícita, registrada, não improvisada.

4. **S2 deve respeitar cortes v0/v1/v1.x e evolução definida em D9.6/D9.8**
   - Não é permitido implementar features de v1/v1.x "escondidas" no v0 se isso aumentar risco ou complexidade.
   - Se uma necessidade de v1 aparecer forte demais, ela entra como backlog/prioridade para as próximas sprints.

5. **Critérios de sucesso só valem com E2E operacional**
   - A Sprint 2 só pode ser declarada "concluída com sucesso" se o fluxo E2E do operador (via script S2.6) estiver funcionando como descrito nas personas.

6. **Filemap e scripts devem permanecer compatíveis com os Blocos 2 e 3**
   - Mesmo que a Sprint 2 não implemente todos os runners de ORR, a estrutura de arquivos e scripts não pode bloquear a adoção futura dos gates T2–T8.

Essas invariantes serão lembradas e reforçadas no Capítulo 2 (gates) e no Capítulo 3 (plano de execução), garantindo que a Sprint 2 se mantenha alinhada ao DNA do projeto, à D9 congelada e ao Sprint Playbook do Inspectah.

