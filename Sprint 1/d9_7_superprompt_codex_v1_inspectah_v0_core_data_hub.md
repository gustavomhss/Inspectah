# D9.7 — Superprompt Codex v1 — Inspectah v0 (Core Data Hub)
> Status: CONGELADO (LOCKED) — Inspectah D9 v1.1 — não editar fora de novas sprints ou PATCH_D9 explícito.

Use este texto literalmente ao abrir uma nova sessão com o Codex para implementar o Inspectah v0. Ajustes só podem ser feitos mediante atualização deste arquivo e reexecução do gate D9-G6.

---

**Contexto resumido**
- Produto: Inspectah — hub de dados/evidências do ecossistema CE/MBP (vide D9.0 §1–§7 e D9.1).
- Versão alvo: **v0 (Core Data Hub)** definido no D9.6 (ingestão batch + Field Designer + Evidence Vault + Explore API + guardrails LGPD).
- Documentos de referência obrigatórios: D9.0–D9.6, D9.8 e D9.5 para compliance.
- Fora de escopo: integrações profundas UMA/Reality, scraping agressivo, features do roadmap v1/v1.x.

**Passo 0 — Leitura e entendimento**
1. Ler D9.0 para entender blueprint e métricas.
2. Ler D9.2 para implementar Field Designer (tipos, transforms, computed fields, versionamento).
3. Ler D9.3 para implementar Explore API (endpoints, filtros, exports, webhooks).
4. Ler D9.4 para modelagem de dados (SQLite dev, Postgres prod) e migrations.
5. Ler D9.5 para assegurar limites LGPD/ToS.
6. Ler D9.6 para confirmar cortes v0/v1 e dependências.
7. Ler D9.8 para seguir o playbook de evolução mesmo durante o desenvolvimento.

**Objetivos técnicos do v0**
1. **Field Designer Service** — parser de definições, execução determinística de transforms, computed fields e versionamento.
2. **Ingestion Pipelines** — jobs que coletam fontes (HTTP/RSS/API), aplicam Field Designer, gravam item/item_version/item_kv e atualizam FTS.
3. **Evidence Vault Connector** — upload/download de manifests + snapshots com hash SHA-256 (armazenamento criptografado).
4. **Explore API** — endpoints `/sources`, `/items`, `/items/{id}`, `/items/{id}/diff`, `/stats/sources/{id}`, `/exports`, gerenciamento de webhooks.
5. **Compliance Guardrails** — enforcement das políticas D9.5 (flags PII, robots.txt, retenção, mascaramento, logs).
6. **Observabilidade mínima** — métricas por run, logs estruturados, trilha de auditoria para chamadas de API.

**Entregáveis esperados da implementação**
- Repositório com serviços modulados (pode ser monorepo) contendo:
  - `field-designer` (engine + CLI para validar definições);
  - `ingestion-runner` (scheduler + executores);
  - `explore-api` (REST + webhooks + exports assíncronos);
  - `evidence-vault` client (upload/download + assinaturas);
  - scripts de migration (SQLite → Postgres) conforme D9.4 §6.
- Testes unitários cobrindo transforms principais, computed fields e endpoints críticos.
- Scripts utilitários: `fd_validate`, `run_ingestion_once`, `export_create`.
- Documentação operacional curta (README) apontando para D9.x originais e descrevendo como executar local/staging.

**Convenções de implementação**
- Linguagem sugerida: stack Typescript/Node ou Go; escolha deve garantir suporte a JSON, workers e Postgres. Independentemente da linguagem, respeitar contratos dos anexos.
- Configuração via arquivos YAML/ENV; sem chaves sensíveis hardcoded.
- Logs JSON estruturados com campos `source_id`, `run_id`, `item_id`, `event`.
- Sem dependências proprietárias; usar libs permissivas (MIT/Apache/BSD).
- Feature flags para funcionalidades opcionais (snapshots, webhooks) controladas por fonte.
- **Computed fields**: implementar a Inspectah Expression Language (IEL) exatamente como descrito em D9.2 §7 — operações determinísticas, acesso apenas a campos do mesmo item e janelas `lag/lead` ≤ 5, funções limitadas (min/max/abs/concat/if/coalesce etc.), sem loops, I/O, aleatoriedade ou consultas externas. Validar fallback obrigatório e bloquear qualquer expressão que lide com `pii=true` sem mascaramento.

**Regras de LGPD/ToS**
- Nunca armazenar PII sem flag `pii=true` e retenção configurada.
- Scrapers devem abortar se `robots_ok=false` (D9.5 §4).
- Export e webhooks precisam mascarar campos sensíveis por padrão.

**Critérios de pronto (Definition of Done técnica)**
1. Todos os módulos compilam/rodam localmente usando SQLite + storage mock.
2. Execução de pipeline exemplo (preço delivery) gera item, manifest e disponibiliza via Explore API.
3. Testes automatizados para transforms críticos (`parse_number`, `regex_extract`, computed `lag`).
4. Webhooks disparados em ambiente local com assinatura HMAC validada.
5. Export job gera CSV paginado e verifica limites descritos em D9.3.
6. Checklist D9-G2–G4 continuam válidos após entrega; caso precise ajuste, abrir PATCH_D9.
7. Documentação descreve como ativar/desativar fontes e como aplicar migrations.

**Guidelines para o Codex**
- Sempre cite as seções relevantes (ex.: "conforme D9.2 §4" em comentários ou README).
- Quando encontrar ambiguidade, não inventar: interromper, registrar no `d9_lessons_log_raw.md` (tag `[COD]`) e propor ação.
- Usar o backlog de lessons para saber se há pendências que devem ser endereçadas nesta implementação.

**Outputs do superprompt**
- Plano técnico detalhado para o v0.
- Código ou pseudo-código inicial dos módulos descritos.
- Scripts e testes mínimos.
- Notas sobre próximos passos (como chegar ao v1) referenciando D9.6.

Cole este superprompt no Codex apenas quando estiver pronto para iniciar a implementação do Inspectah v0. Qualquer mudança no escopo ou nos contratos exige atualizar os D9.x correspondentes e reexecutar o gate D9-G6.
