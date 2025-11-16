# Inspectah — Sprint 2
## Capítulo 4 — Retrospectiva, Lessons, Backlog e Loop de Aprendizado para o Codex — v1.0

> Este capítulo responde à pergunta: **“O que realmente aconteceu na Sprint 2 e como isso melhora o desempenho do Codex nas próximas sprints?”**
>
> Capítulo 1 define o alvo. Capítulo 2 define os gates. Capítulo 3 define o plano. Este Capítulo 4 registra **os fatos**, **as lições** e **os ajustes** – em formato estruturado, pensado para humanos e para o Codex.

---

## 0) Como usar este capítulo (humano + Codex)

*(orientações originais mantidas; consulte a versão inicial caso precise do passo a passo completo.)*

---

## 1) Snapshot da Sprint 2 (estado final)

### 1.1 Estado dos gates S2-G0…S2-G6

| Gate | Status | Comentário |
|------|--------|------------|
| S2-G0 — Bootstrap & Ambiente Dev | PASS | `.venv` local + `bin/dev_up.sh/bin/dev_down.sh` mantiveram FastAPI/uvicorn reais; maior dor foi lidar com ambientes sem socket (mitigado com modo *idle* documentado). |
| S2-G1 — Field Designer v0 & IEL Core | PASS | CRUD + IEL (min/max/abs/round/concat/length/coalesce/_iel_if/lag) consolidados com AST whitelist; bug inicial foi bloquear operadores básicos, corrigido abrindo a whitelist com segurança. |
| S2-G2 — Explore API v0 + Rate Limit | PASS | Endpoints `/explore/items`, `/explore/items/{id}` e `/sources` com filtros, paginação determinística e rate limit 120/min + burst 240; dor foi lembrar de incluir os cabeçalhos `X-RateLimit-*` e manter FastAPI oficial no repo. |
| S2-G3 — Evidence Vault v0 + LGPD mínimo | PASS | Backend `local_stub` em `sa-east-1`, tabela `evidence_records`, CLI write/read e script smoke; ajuste crítico foi garantir SSE-KMS lógico mesmo no stub. |
| S2-G4 — Ingestão + Observabilidade | PASS | Pipeline RSS demo (`scripts/ingest_source_demo.sh`), logs estruturados e métricas `inspectah_ingest_*` + `inspectah_explore_queries_total`; sincronizar ingest + Explore para refletir os contadores foi o principal ponto de atenção. |
| S2-G5 — E2E Script + Tests | PASS | `tests/integration/test_e2e_inspectah_v0.py` e `bin/run_inspectah_v0_e2e.sh` cobrem dev_up → ingest → Explore → métricas → manifest → dev_down; o desafio foi tornar o script resiliente a ambientes offline. |
| S2-G6 — Docs + Retro | PASS | README operacional e Cap.4 concluídos; backlog S3+ registrado; foco em remover qualquer comando “teórico”. |

### 1.2 Entregáveis S2.x atingidos

- **S2.0 — Infra & scaffolding:** entregue.
- **S2.1 — Field Designer v0 & IEL core:** entregue.
- **S2.2 — Explore API v0:** entregue (com rate limit e filtros).
- **S2.3 — Evidence Vault v0:** entregue (writer/reader + CLI/smoke).
- **S2.4 — Ingestão mínima (1–2 fontes):** entregue (rss_news_minimal).
- **S2.5 — Observabilidade básica v0:** entregue (logs estruturados + métricas ingest/query/429).
- **S2.6 — Testes & E2E local:** entregue (pytest 37/37 + script E2E).
- **S2.7 — Documentação operacional v0:** entregue (README + Cap.4 + checklists).

### 1.3 Métricas qualitativas

- **Surpresa positiva:** a costura Field Designer → Ingest → Explore → Evidence Vault funcionou sem divergências de schema; o watcher RSS serviu como fio condutor do v0.
- **Bloqueios principais:** ambiente sandbox sem socket/Internet atrasou smoke scripts; resolver exigiu deixar `bin/dev_up.sh`/scripts resilientes.
- **Assertividade:** seguir D9.* ao pé da letra (rate limit, SSE-KMS, LGPD tags) e manter checklists ricos acelerou a aprovação dos gates.
- **Dificuldades:** o Codex inicialmente tentou improvisar stacks e ignorou bursts; ficou claro que cada gate precisa refletir o mundo real, mesmo que o ambiente não coopere.

---

## 2) Lessons estruturadas

### S2-LESSON-001
- Tipo: DESIGN
- Gates relacionados: S2-G0
- Threads relacionadas: T0
- Resumo: Substituir FastAPI/uvicorn por shims “offline” gerou divergência de arquitetura e invalidou o gate.
- Causa raiz: Pressa em driblar limitações do sandbox levou a improvisar dependências em vez de refletir o stack real.
- Impacto: Retrabalho no bootstrap e atraso para gates seguintes.
- Regra: Mesmo em ambiente restrito, mantenha as dependências oficiais no repo; limitações de execução são tratadas com scripts resilientes, não com mudanças de stack.

### S2-LESSON-002
- Tipo: GATE_FAIL
- Gates relacionados: S2-G2
- Threads relacionadas: T4, T5
- Resumo: O primeiro patch de rate limit ignorou o burst 240 req/min, bloqueando clientes legítimos.
- Causa raiz: Leitura parcial da seção de limites da D9.3.
- Impacto: Gate S2-G2 ficou FAIL até incluir burst + cabeçalhos e cobrir via testes/smoke.
- Regra: Quando a spec define múltiplos parâmetros, todos devem ser implementados/testados/registrados nos checklists.

### S2-LESSON-003
- Tipo: PROCESS
- Gates relacionados: S2-G5, S2-G6
- Threads relacionadas: T9, T10
- Resumo: Documentação só ficou confiável quando cada comando descrito foi executado de fato (dev_up, ingest, Explore, Evidence Vault, E2E).
- Causa raiz: README inicial continha comandos teóricos e divergentes.
- Impacto: Revisão extra até que os comandos fossem testados e vinculados às evidências.
- Regra: Nenhum comando entra em docs/checklists sem ter sido executado e registrado.

---

## 3) Ações & backlog estruturado

### S2-ACT-001
- Lessons relacionadas: S2-LESSON-001
- Tipo: BACKLOG_S3+
- Descrição: Criar `bin/dev_sanity.sh` para validar se `bin/dev_up.sh` subiu o servidor ou entrou em modo idle, facilitando diagnósticos fora do sandbox.
- Prioridade: Média
- Dono sugerido: Codex + Squad Inspectah
- Sprint alvo: S3
- Status: OPEN
- Comentário: Exige patch em Cap.2/Cap.3 da Sprint 3.

### S2-ACT-002
- Lessons relacionadas: S2-LESSON-002
- Tipo: BACKLOG_S3+
- Descrição: Rodar `scripts/rate_limit_smoke.sh` em ambiente com rede liberada (self-hosted runner) para garantir observação real de 429.
- Prioridade: Alta
- Dono sugerido: Squad Inspectah (ops)
- Sprint alvo: S3
- Status: OPEN
- Comentário: Script existe; falta infraestrutura.

### S2-ACT-003
- Lessons relacionadas: S2-LESSON-003
- Tipo: BACKLOG_S3+
- Descrição: Adicionar etapa “doc-check” automática ao `bin/orr_final.sh`, executando os comandos do README e anexando logs aos checklists.
- Prioridade: Média
- Dono sugerido: Codex
- Sprint alvo: S3
- Status: OPEN
- Comentário: Depende da priorização do PO para S3.

**Backlog S3+ resumido:**
1. Sanity pós-`bin/dev_up.sh` (S2-ACT-001).
2. Smoke de rate limit em ambiente com rede real (S2-ACT-002).
3. Automação do doc-check (S2-ACT-003).
4. Expansão de ingest para novas fontes e reforço do `/metrics` externo (derivado das ações acima).

---

## 4) Patches de spec/gates

Nenhum patch (`S2-PATCH-XXX`) foi necessário na Sprint 2. Qualquer alteração futura em Cap.1–3 ou D9.* deve ser registrada aqui antes de ser aplicada.
