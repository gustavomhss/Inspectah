# Inspectah — Sprint Playbook v3 (Supremo, S26–S65)

## 0. Propósito

Este Playbook é o contrato entre:

- quem **desenha** a sprint (Spec Office + squads),  
- quem **executa** (Codex + dev humano),  
- e quem **cobra** o resultado (Conselho + ORR).

Objetivo: cada sprint virar um bloco finito, verificável e impossível de interpretar errado, com:

- contexto cristalino (por que existe),
- estados-alvo explícitos (o que deve ser verdade ao final),
- gates e métricas duras (como provamos),
- arquitetura e filemap concretos (onde mora cada coisa),
- plano de execução com tasks (como chegamos lá),
- operação pós-sprint (como isso vive em produção),
- learnings e anti-gaps (como não repetimos erro).

Toda sprint S26–S65 é descrita em **6 capítulos macro**, cada um com **4 blocos fixos**.  
Total: **24 arquivos por sprint**. Tasks são parte formal do **Capítulo 4** (Bloco 4.4).

---

## 1. Estrutura por sprint (6 × 4)

Para a sprint `SXX`, a convenção de nomes é, por exemplo:

- `docs/sXX_cap_1_1_contexto_geral.md`  
- …  
- `docs/sXX_cap_6_4_anti_gaps_e_proximos_passos.md`

### Capítulo 1 — Contexto & Problemas a Resolver

**Função:** impedir sprint solta, sem eixo. Cap.1 fixa o **porquê**.

**Bloco 1.1 — Contexto e visão da sprint**

- Programa e épicos relacionados (ex.: Programa 1, E28).  
- Estado atual do produto antes da sprint.  
- Foto do produto após a sprint em 1–2 frases.  
- Conexão com o roadmap (onde esta sprint encaixa na sequência).

**Bloco 1.2 — Problemas e hipóteses**

- Problemas concretos (dores do usuário, gargalos, riscos).  
- Hipóteses do tipo: “Se entregarmos X, Y vai melhorar em Z”.  
- Tentativas anteriores relevantes (o que já foi testado e falhou).

**Bloco 1.3 — Domínios, personas e casos canônicos**

- Domínios impactados (política, economia, clima, etc.).  
- Personas centrais (operador de ingestão, debunker, analista de casos, etc.).  
- 2–5 casos canônicos que ilustram a sprint end-to-end.

**Bloco 1.4 — Fora de escopo e cortes**

- Itens explicitamente fora desta sprint (para evitar escopo elástico).  
- Escopos irmãos empurrados para outras sprints/épicos.  
- Regras de “não desviar” (tudo fora desta lista vira input para futuro, não para agora).

---

### Capítulo 2 — Estados-alvo, Gates, Métricas & Invariantes

**Função:** traduzir "queremos melhorar X" em **coisas verificáveis**.

**Bloco 2.1 — Estados-alvo (SA)**

- 3–7 estados do tipo:
  - “Ao final da SXX, um operador consegue executar A→B→C na tela Y sem abrir terminal.”  
  - “Ao final da SXX, o fluxo Z gera evidência W em `out/evidence/SXX_*`.”
- Cada estado-alvo `SXX-SA-0N` tem:
  - descrição clara;  
  - método de verificação (teste, script, ORR manual);  
  - ligação com casos canônicos do Cap.1.

**Bloco 2.2 — Gates & testes (G)**

- Mapeamento `SA → gates` (G0–G8, ORR, etc.).  
- Para cada gate:
  - script (`bin/sXX_gN_*.sh`),  
  - evidências esperadas (`out/evidence/SXX_GN_*`),  
  - critério de PASS/FAIL.

Regra: **sem gate não há estado-alvo; sem estado-alvo não há escopo**.

**Bloco 2.3 — Métricas & scorecards**

- Métricas principais da sprint (latência, throughput, erro, time-to-truth, etc.).  
- Como medir:
  - arquivos de scorecards (`out/scorecards/SXX_GN_*.json`),  
  - campos obrigatórios (`status`, `metric_name`, `value`, `target`, `evidence_path`).
- Como interpretar: o que é GO, GO-com-ressalva, NO-GO.

**Bloco 2.4 — Invariantes & não-negociáveis**

- Lista de invariantes que não podem ser quebrados (produto, segurança, verdade, evidência).  
- Ex.: "Nenhuma decisão de verdade sem evidência rastreável".  
- Relação entre invariantes e gates que os guardam.

---

### Capítulo 3 — Arquitetura & Filemap

**Função:** garantir que todo mundo sabe **onde** cada coisa vive.

**Bloco 3.1 — Topologia de sistemas e fluxos**

- Componentes afetados (backend, frontend, ingestão, agentes, etc.).  
- Fluxos principais (sequência textual, não precisa ser diagrama gráfico):
  - Ex.: "Fonte → Ingestão → Fluxo de Agentes → Debunker → Truth Console → Case Cockpit".

**Bloco 3.2 — Modelagem de dados, contratos & APIs**

- Esquemas novos/alterados (tabelas, modelos ORM, JSONs).  
- Endpoints de API (paths, verbos, inputs/outputs, erros).  
- Compatibilidade: migrations, versionamento de payloads, fallback.

**Bloco 3.3 — Filemap da sprint**

- Lista de arquivos criados/alterados **com path exato**, agrupados por categoria:
  - backend (`app/...`, `tests/...`),  
  - frontend (`frontend/inspectah-ui/src/...`),  
  - scripts (`bin/sXX_*.sh`, `scripts/*.py`),  
  - CI/infra (`.github/workflows/*.yml`),  
  - docs (`docs/sXX_*.md`).
- Convenções de nome para esta sprint (prefixos, sufixos, pastas de evidência).

**Bloco 3.4 — Integrações & dependências externas**

- Serviços externos (APIs de governo, RSS, DBT, BigQuery, etc.).  
- Configuração necessária (env vars, secrets, arquivos de config).  
- Como testar localmente e na CI (mocks vs real).

---

### Capítulo 4 — Execução, Evidências & Tasks

**Função:** virar **plano de ataque executável**: waves, tasks, evidências.  
**Aqui vivem as tasks de sprint. Não existe Capítulo 7.**

**Bloco 4.1 — Plano de waves**

- Divisão da sprint em waves (W0, W1, W2, W3…):
  - W0 — groundwork / sanidade;  
  - W1 — núcleo funcional;  
  - W2 — bordas / UX / integrações;  
  - W3 — hardening / limpeza.
- Para cada wave:
  - objetivo,  
  - critérios de saída,  
  - gates que dependem dela.

**Bloco 4.2 — Estratégia de desenvolvimento & CI/CD**

- Organização em branches e PRs (nomes, ordem, granularidade).  
- Uso de CI local (`bin/ci_local.sh`) e CI remoto.  
- Ordem de leitura do Playbook pelo Codex (Cap.1–3 → 4 → 5–6).  
- Directives para Codex (por exemplo: "não crie arquivos fora do filemap").

**Bloco 4.3 — Plano de evidências**

- Evidências obrigatórias por gate:  
  - logs, arquivos, prints, bundles.  
- Mapeamento `gate → evidência esperada`, com paths concretos.  
- Regra: toda task crítica aponta para pelo menos uma evidência (direta ou via script).

**Bloco 4.4 — Tasks, checklists e waves (fonte oficial de tasks)**

Bloco 4.4 é a **fonte de verdade** das tasks da sprint.  
Qualquer arquivo auxiliar de tasks deve ser derivado daqui.

Formato conceitual de cada task:

- `id`: `SXX-T-YYY` (YYY numérico).  
- `wave`: `W0`, `W1`, etc.  
- `categoria`: `backend`, `frontend`, `infra`, `tests`, `docs`, `gates`, etc.  
- `descricao`: uma frase clara, iniciando com verbo.  
- `artefatos`: arquivos/pastas esperados (coerentes com o filemap do Cap.3).  
- `gates`: lista de gates relacionados (ex.: `[G2, G4]`).  
- `estados_alvo`: lista de SAs ligados à task (ex.: `[SA-02, SA-03]`).  
- `done_condition`: critério objetivo de conclusão.  
- `evidencias`: paths ou referências a evidências produzidas.

Exemplo de tabela dentro do Bloco 4.4:

```markdown
| ID        | Wave | Cat      | Descrição                              | Arquivos principais                     | Gates | SA    |
|-----------|------|----------|----------------------------------------|-----------------------------------------|-------|-------|
| S27-T-001 | W0   | infra    | Preparar ambiente backend S27          | bin/ci_local.sh, .env.example           | G0    | SA-01 |
| S27-T-002 | W1   | backend  | Implementar GET /api/sources/{id}      | app/api/sources.py, tests/test_sources* | G2,G4 | SA-02 |
| S27-T-003 | W1   | frontend | Criar tela de detalhe de fonte         | frontend/inspectah-ui/src/...          | G3    | SA-02 |
```

Decisões oficiais:

1. **Não existe Capítulo 7 “Tasks”.**  
2. Tasks vivem **sempre** no Capítulo 4, Bloco 4.4.  
3. O Codex deve usar o Bloco 4.4 como roteiro primário de execução.  
4. Qualquer arquivo de tasks auxiliar (YAML/JSON) é derivado de 4.4.

---

### Capítulo 5 — ORR & Operação Pós-sprint

**Função:** garantir que a sprint termina com algo operacional, não com um demo.

**Bloco 5.1 — Cenários end-to-end de validação**

- 2–5 cenários E2E cobrindo os estados-alvo críticos.  
- Para cada cenário:
  - passos (input → ações → output esperado),  
  - gates/ scripts que o exercitam.

**Bloco 5.2 — Plano de ORR**

- Checklist de pré-ORR (gates que precisam estar verdes, evidências mínimas).  
- Como o ORR será conduzido (quem participa, quais docs abrir).  
- Estrutura do resumo ORR (`docs/sXX_orr_summary.md`).

**Bloco 5.3 — Runbooks & operação**

- Runbooks criados/atualizados (`docs/runbooks/...`).  
- Tipos de incidente cobertos e como reagir.  
- Relação com Truth Ops / On-call.

**Bloco 5.4 — Riscos, rollback & feature flags**

- Riscos que permanecem após a sprint.  
- Plano de rollback (como desligar ou reverter).  
- Feature flags (nomes, escopo, responsáveis).

---

### Capítulo 6 — Learnings, Roadmap & Anti-gaps

**Função:** capturar aprendizado e fechar buracos para as próximas sprints.

**Bloco 6.1 — Lessons Learned**

- Técnicas (design, libs, ferramentas).  
- Processuais (playbook, comunicação, Codex, revisão).  
- O que repetir; o que evitar.

**Bloco 6.2 — Dívidas técnicas**

- Lista de dívidas com:
  - `id` (`SXX-DT-YYY`),  
  - descrição,  
  - risco,  
  - sugestão de quando/onde atacar (sprint/épico).

**Bloco 6.3 — Impacto no roadmap**

- Efeitos na trilha S26–S65:  
  - coisas que foram adiantadas,  
  - coisas que escorregaram,  
  - ajustes finos de escopo de programas/épicos.

**Bloco 6.4 — Anti-gaps & recomendações**

- Gaps encontrados (esquecimentos, ambiguidades, fragilidades).  
- Regras novas para specs futuras (ex.: “sempre explicitar tal coisa no Cap.2”).  
- Alertas para o próximo PO/Spec Office.

---

## 2. Regras de uso com Codex & Spec Office

1. **Ordem de escrita humana:**
   - Cap.1 → Cap.2 → Cap.3 primeiro.  
   - Só depois Cap.4–6.  
   - Sprint não entra em execução sem Cap.1–3 aprovados pelo Spec Office.

2. **Ordem de consumo pelo Codex:**
   - Ler Cap.1 (contexto).  
   - Ler Cap.2 (estados-alvo, gates, métricas).  
   - Ler Cap.3 (arquitetura, filemap).  
   - Ler Cap.4, focando em 4.1 (waves) e 4.4 (tasks).  
   - Usar Cap.5–6 para ORR, runbooks e ajustes finos.

3. **Contrato de qualidade:**
   - Se qualquer capítulo estiver ambíguo, a sprint é NO-GO antes de chegar ao Codex.  
   - Se a execução divergir do Playbook, o problema é de especificação ou de prompt, não de “adivinhação” do dev.

---

## 3. Arquivo auxiliar de tasks (opcional, derivado)

Para facilitar automação e execução, é permitido gerar um arquivo auxiliar, por exemplo:

- `docs/sXX_tasks_execucao.yml` ou `.json`.

Regras:

- Conteúdo **é derivado** do Bloco 4.4 (Cap.4).  
- Não é novo capítulo, não altera o modelo 6×4.  
- Em caso de conflito, o Bloco 4.4 é a fonte de verdade.

Estrutura sugerida (conceitual):

```yaml
tasks:
  - id: SXX-T-001
    wave: W0
    category: infra
    description: Preparar ambiente backend SXX
    artifacts:
      - bin/ci_local.sh
      - .env.example
    gates: [G0]
    states: [SA-01]
    done_condition: "bin/sXX_g0_env_repo.sh sai com exit 0"
    evidences:
      - out/evidence/SXX_G0_env_repo/log.txt
```

Codex pode usar esse arquivo como checklist mecânico, mas a semântica vem sempre do Playbook.

---

## 4. Anti-ambiguidades da versão v3

- **Não existe Capítulo 7 "Tasks".**  
- Tasks são parte formal do **Capítulo 4, Bloco 4.4**.  
- Arquivos auxiliares de tasks são derivados, nunca fonte principal.  
- O modelo 6×4 é estável: 6 capítulos × 4 blocos = 24 arquivos por sprint.  
- Este documento substitui versões anteriores do Sprint Playbook na KB do Inspectah.

A partir de agora, qualquer sprint S26–S65 deve seguir este Playbook v3 ao ser especificada, executada e validada.

