# Inspectah — Sprint 27 (S27)
## Capítulo 4 — Bloco 1
### Plano de Waves — W0, W1, W2, W3

> Arquivo-alvo no repo: `docs/s27_cap_4_1_plano_de_waves.md`
>
> Função: detalhar o plano de waves da S27 — objetivos, foco, critérios de saída, gates alvo e principais artefatos esperados em cada wave. Este bloco é o "ritmo da sprint" e serve como guia diário de execução.

---

## 1. Visão geral das waves da S27

A S27 é organizada em até quatro waves sequenciais:

- **W0 — Groundwork & Sanidade**  
  - Wave curta de preparação: garante que o terreno está pronto para a sprint (ambiente, repo, docs, G0).  
- **W1 — Núcleo funcional Admin v1 nos consoles**  
  - Onde Admin v1 é consolidado como padrão real nos consoles de Fontes, Ingestão e Debunker, com fluxos principais funcionando.  
- **W2 — Refinos, Contratos & Operação**  
  - Onde fluxos são refinados, contratos de API são estabilizados e docs/runbooks são escritos e usados.  
- **W3 — Hardening, ORR & Bundle**  
  - Onde a sprint é "fechada": bugs críticos, rodada completa de gates, ORR e bundle de evidências.

O time pode ajustar a granularidade de cada wave (dias, metade de sprint, etc.), mas o encadeamento conceitual deve ser preservado.

---

## 2. Wave W0 — Groundwork & Sanidade

### 2.1 Objetivo da wave

Garantir que a S27 não começa torta: ambiente, repositório, docs de contexto e gates básicos estão minimamente saudáveis.

### 2.2 Foco principal

- Validar que Cap.1, Cap.2 e Cap.3 da S27 existem nos caminhos esperados.  
- Garantir que o estado atual de Admin v1, consoles e APIs mapeados em Cap.3 é conhecido (mesmo que ainda imperfeito).  
- Implementar e rodar G0 pelo menos uma vez, gerando scorecard e evidências.

### 2.3 Gates alvo na W0

- **G0** — Escopo, Grounding & Sanidade de Ambiente.  
  - Implementação e primeira execução oficial.  
- G1–G6 ainda não são alvo de GO, apenas de reconhecimento (ver o que já existe).

### 2.4 Critérios de saída de W0

W0 é considerada concluída quando:

- `docs/s27_cap_1_*.md`, `docs/s27_cap_2_*.md` e `docs/s27_cap_3_*.md` existem e foram lidos pelo squad.  
- `bin/s27_g0_env_repo.sh` existe e roda sem erros fatais.  
- `out/scorecards/S27_G0_scope_and_env.json` foi gerado com `env_ok == true` e `docs_cap_1_present == true` e `docs_cap_2_present == true`.  
- Há pelo menos um registro em `out/evidence/S27_G0_env_repo/` referente à execução inicial de G0.  
- Há um entendimento compartilhado (registrado em nota breve) do estado atual de Admin v1 e dos consoles.

### 2.5 Artefatos esperados ao final da W0

- Script `bin/s27_g0_env_repo.sh` funcional.  
- Scorecard `out/scorecards/S27_G0_scope_and_env.json`.  
- Logs em `out/evidence/S27_G0_env_repo/`.  
- Nota interna (pode ser um parágrafo em Cap.4 ou Cap.6) descrevendo o estado inicial de Admin v1 + consoles.

---

## 3. Wave W1 — Núcleo funcional Admin v1 nos consoles

### 3.1 Objetivo da wave

Fazer com que Admin v1 funcione como padrão real nas telas principais de Fontes, Ingestão 2.0 e Debunker, e não apenas como uma biblioteca opcional.

### 3.2 Foco principal

- Consolidar o uso de AdminShell, AdminHeader, AdminContent e componentes base nas páginas principais de cada console.  
- Assegurar que os fluxos fundamentais de cada console funcionam pelo menos em um happy-path por domínio.  
- Começar a preparar os testes E2E mínimos de G2 para esses fluxos.

### 3.3 Gates alvo na W1

- **G1** — Admin Design System (Tokens & Componentes)  
  - Deve ser implementado e rodado em modo inicial.  
  - O objetivo em W1 é garantir que `consoles_using_admin_components` esteja pelo menos em "partial" com plano claro de evolução.

- **G2 (escopo mínimo)** — Fluxos de Consoles Admin  
  - Ao menos um cenário E2E por console (Fontes, Ingestão, Debunker) deve estar implementado e passante.  

- **G3 (sanidade básica)** — Qualidade de Frontend Admin  
  - Lint, tests e build devem rodar sem quebras causadas pelas integrações iniciais com Admin v1.

### 3.4 Critérios de saída de W1

W1 é considerada concluída quando:

- As páginas principais de cada console (listagens + detalhes) usam Admin v1 visivelmente (AdminShell + Header + Content).  
- `bin/s27_g1_admin_design_system.sh` existe e foi rodado ao menos uma vez, com scorecard em `out/scorecards/S27_G1_admin_design_system.json`.  
- `bin/s27_g2_admin_flows.sh` existe com pelo menos 3 cenários E2E (1 por console) e scorecard inicial em `out/scorecards/S27_G2_admin_flows.json`.  
- `bin/s27_g3_front_quality_admin.sh` existe e foi rodado, gerando `out/scorecards/S27_G3_front_quality_admin.json`.  
- Nenhuma das integrações visíveis de Admin v1 nas telas principais está obviamente quebrada (sem layout implodido, sem crash ao carregar a página).

### 3.5 Artefatos esperados ao final da W1

- Consoles com páginas principais ajustadas em `features/sources/pages/*`, `features/ingestion/pages/*`, `features/debunker/pages/*`.  
- Scripts de G1, G2 e G3 criados em `bin/`.  
- Scorecards iniciais de G1, G2 e G3.  
- Evidências em `out/evidence/S27_G1_*`, `S27_G2_*`, `S27_G3_*`.

---

## 4. Wave W2 — Refinos, Contratos & Operação

### 4.1 Objetivo da wave

Refinar fluxos, estabilizar contratos e produzir documentação de operação para que os consoles admin possam ser usados na prática, sem depender da memória da equipe.

### 4.2 Foco principal

- Ampliar e robustecer cenários E2E (mais caminhos, mais combinações, fluxos combinados entre consoles).  
- Consolidar contratos de API de Fontes, Ingestão e Debunker, alinhando schemas e testes de contrato.  
- Escrever e alinhar docs e runbooks de operação de Admin v1 + consoles.

### 4.3 Gates alvo na W2

- **G2 (escopo ampliado)** — Fluxos Admin  
  - Cobertura de cenários E2E mais ampla (incluindo fluxos combinados Fontes → Ingestão → Debunker).

- **G3 (rodada completa de front)** — Qualidade de Frontend Admin  
  - Lint, tests e build rodando com escopo completo do front.

- **G4** — Contratos & APIs  
  - Validações de contrato para os principais endpoints dos três domínios.  

- **G5** — Docs & Runbooks  
  - Guia Admin v1.1 e runbooks de Fontes, Ingestão e Debunker escritos, minimamente estruturados e revisados pelo squad.

### 4.4 Critérios de saída de W2

W2 é considerada concluída quando:

- Cenários E2E definidos em Cap.2 (G2) estão implementados e verdes no scorecard `S27_G2_admin_flows.json`.  
- Principais endpoints mapeados em Cap.3 (Fontes, Ingestão, Debunker) estão cobertos pelos testes de contrato e aparecem no scorecard `S27_G4_admin_contracts.json` como OK ou com mismatches documentados.  
- `docs/guia_consoles_admin_v1_1.md` existe com estrutura mínima (seções chave) e foi lido pelo squad.  
- Runbooks `docs/runbook_operacao_fontes_vX.md`, `..._ingestao_...`, `..._debunker_...` existem com estrutura mínima e foram usados em pelo menos uma simulação interna.  
- G3 foi rodado após os principais ajustes de front, com `lint_ok`, `tests_ok` e `build_ok` em `S27_G3_front_quality_admin.json` (GO ou GO com ressalvas bem descritas).

### 4.5 Artefatos esperados ao final da W2

- Cenários E2E adicionais implementados nos tests de G2.  
- Scorecards G2, G3, G4 e G5 atualizados.  
- Guia Admin v1.1 e runbooks presentes e ligados ao estado atual dos consoles.  
- Evidências ampliadas em `out/evidence/S27_G2_*`, `S27_G3_*`, `S27_G4_*`, `S27_G5_*`.

---

## 5. Wave W3 — Hardening, ORR & Bundle

### 5.1 Objetivo da wave

Consolidar o trabalho da S27, eliminar arestas críticas, rodar a bateria completa de gates, produzir o bundle e conduzir o ORR que decidirá o destino do Épico E26.

### 5.2 Foco principal

- Identificar e resolver bugs e buracos de UX/fluxo descobertos em W1/W2.  
- Rodar a sequência completa de G0–G6 em condições próximas a um "dress rehearsal".  
- Gerar o bundle de evidências da S27.  
- Conduzir ORR com stakeholders relevantes (Admin, Fontes, Ingestão, Debunker, Ops) e emitir veredito.

### 5.3 Gates alvo na W3

- **G0–G5** — Rodada completa, após os ajustes finais.  
- **G6** — ORR & Bundle de Evidências, incluindo scorecard `S27_G6_orr_summary.json` e zip `inspectah_s27_evidence_bundle.zip`.

### 5.4 Critérios de saída de W3

W3 é considerada concluída quando:

- G0–G5 foram rodados em sequência e scorecards correspondentes existem e refletem o estado final da S27.  
- `bin/s27_g6_orr_bundle.sh` foi executado com sucesso, gerando `out/bundles/inspectah_s27_evidence_bundle.zip` com os artefatos esperados.  
- O ORR da S27 foi conduzido (documentado em `docs/s27_cap_5_orr_local_summary.md`), com participação dos owners de Admin/Fontes/Ingestão/Debunker/Ops.  
- `out/scorecards/S27_G6_orr_summary.json` registra um veredito (`GO`, `NO_GO` ou `GO_WITH_RISKS`) e lista clara de riscos/ressalvas.  
- A decisão sobre o Épico E26 (Admin v1 em Fontes/Ingestão/Debunker) está registrada no ORR e em Cap.6.

### 5.5 Artefatos esperados ao final da W3

- Scorecards finais G0–G6 em `out/scorecards/`.  
- Evidências finais em `out/evidence/S27_G*/`.  
- Bundle zip `out/bundles/inspectah_s27_evidence_bundle.zip`.  
- Documento de ORR `docs/s27_cap_5_orr_local_summary.md`.  
- Atualização em Cap.6 com learnings e dívidas finais.

---

## 6. Uso do plano de waves no dia a dia da sprint

O Bloco 1 do Cap.4 deve ser usado como referência diária pela equipe:

- No início de cada wave, revisar objetivo, gates alvo e critérios de saída.  
- Atualizar o board de tasks S27-T-XXX (Bloco 4.4) marcando quais tasks pertencem a qual wave.  
- Antes de terminar uma wave, verificar se todos os critérios de saída foram de fato cumpridos (não apenas "passou no olho").

Com esse plano de waves, a S27 ganha um ritmo claro: primeiro acerta o terreno (W0), depois coloca Admin v1 de pé (W1), em seguida refina e consolida operação (W2) e, por fim, valida tudo com rigor (W3).

