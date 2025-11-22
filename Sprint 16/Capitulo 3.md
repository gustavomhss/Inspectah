# Inspectah — Sprint 16  
## Capítulo 3 — Filemap, Arquitetura e Contratos de Layout

### 0. Papel deste capítulo

Este capítulo define **como** a Sprint 16 se materializa dentro do repositório do Inspectah:

- filemap detalhado (pastas, arquivos e padrões de nomes);
- arquitetura lógica dos componentes tocados pela S16;
- contratos de layout para scorecards e evidências;
- pontos de integração com sprints anteriores (S13–S15) e com CI.

O objetivo é permitir que qualquer pessoa (humano ou Codex) consiga:

- entender **onde** cada artefato da S16 deve morar;
- saber **como** os gates T0–T8 da S16 se conectam a scripts, módulos e docs;
- garantir que novos arquivos sigam padrões consistentes com o DNA do projeto.

Capítulo 2 respondeu “o que cada gate precisa garantir”. Este Capítulo 3 responde “onde isso mora no repositório e como se encaixa na arquitetura”, sem engessar a implementação de baixo nível que será detalhada no Capítulo 4.

---

### 1. Visão geral da arquitetura na S16

Na Sprint 16, a arquitetura do Inspectah é vista em quatro camadas principais:

1. **Camada de domínio / Truth‑DB / Sistema de Blocos (S13–S15)**  
   - Módulos centrais responsáveis por blocos, sub‑blocos, componentes, histórico, disputas e write path.  
   - Já consolidados em S13–S15 (não serão radicalmente redesenhados na S16).

2. **Camada de inteligência e blindagem (S15)**  
   - Debunker v1 (`inspectah/debunker/*`);  
   - Comitês V1/V2/V3 (`inspectah/committees/*`);  
   - Âncoras (`inspectah/anchors/*`, integradas a `inspectah/blocks/`);  
   - Anti‑canetada no write path (`inspectah/commands/__init__.py`).

3. **Camada de hardening e Threat Model (S16)**  
   - Documento de Threat Model;  
   - scripts de ataque/stress/chaos e harness de cenários;  
   - ajustes pontuais em Debunker/comitês/âncoras/commands para endurecer a pilha;  
   - gates T0–T8 da S16 + orquestrador;  
   - novas métricas/logs e consultas de observabilidade focadas em segurança.

4. **Camada de runbooks, ORR e CI (S10/S15/S16)**  
   - runbooks e resumos de sprint;  
   - scripts `bin/*` para gates/ORR;  
   - workflows `.ci/*` para garantir reprodutibilidade;  
   - scorecards e evidências em `out/`.

Um diagrama textual simplificado:

- **Camada 4 — Runbooks / CI / ORR**  
  `docs/sprint_16_*.md`, `.ci/sprint_16_*.yml`, `bin/s16_tX_*.sh`, `bin/s16_all_gates.sh`, `out/*`
- **Camada 3 — Hardening / Threat Model (S16)**  
  `docs/sprint_16_threat_model.md`, `scripts/s16_*.py`, ajustes em `inspectah/*`
- **Camada 2 — Blindagem (S15)**  
  `inspectah/debunker/*`, `inspectah/committees/*`, `inspectah/anchors/*`, `inspectah/commands/__init__.py`
- **Camada 1 — Truth‑DB / Sistema de Blocos (S13–S15)**  
  núcleo do modelo de dados e write path

A S16 atua predominantemente na **camada 3**, conectando‑se às camadas 1 e 2 pelos módulos já existentes, e à camada 4 por novos scripts, scorecards, evidências e jobs de CI.

---

### 2. Filemap de alto nível da Sprint 16

A Sprint 16 introduz ou atualiza artefatos principalmente nos seguintes diretórios do repo em `/Users/gustavoschneiter/Documents/Inspectah`:

- `Sprint 16/`  
  - Capítulos 1–4 (visão, gates, filemap/arquitetura, runbook/superprompts).

- `docs/`  
  - documentação de Threat Model, overview da sprint, filemap/arquitetura e ORR S16.

- `bin/`  
  - scripts shell para gates T0–T8 da S16 e orquestrador `s16_all_gates`.

- `scripts/`  
  - scripts Python para cenários de ataque/stress, checks do Threat Model e suportes específicos dos gates.

- `inspectah/`  
  - ajustes de hardening em módulos existentes (Debunker, comitês, âncoras, commands) e, quando necessário, helpers para Threat Model.

- `.ci/`  
  - workflows de CI específicos da S16 (gates e, opcionalmente, nightly focado em segurança).

- `out/scorecards/` e `out/evidence/`  
  - scorecards JSON e bundles de evidências gerados pelos gates T0–T8 da S16.

As seções seguintes detalham os contratos de nomes e responsabilidades, sempre em modo **propositivo**: o Capítulo 4 transforma esses contratos em comandos e superprompts concretos para o Codex.

---

### 3. Documentação da Sprint 16 (docs/ + /Sprint 16)

#### 3.1 Pasta raiz da sprint: `/Sprint 16/`

Os Capítulos 1–4 textuais da S16 ficam na pasta raiz:

- `Sprint 16/Capitulo 1.md` — visão, contexto e objetivos (Cap. 1);  
- `Sprint 16/Capitulo 2.md` — gates T0–T8 e critérios de qualidade (Cap. 2);  
- `Sprint 16/Capitulo 3.md` — este documento (filemap/arquitetura);  
- `Sprint 16/Capitulo 4.md` — runbook operacional + superprompts Codex.

Esses arquivos são o ponto de partida humano (e também para prompts) da S16.

#### 3.2 Arquivos principais em `docs/`

A Sprint 16 introduz/atualiza os seguintes documentos operacionais:

- `docs/sprint_16_overview.md`  
  - resumo executivo da S16 (contexto, objetivo geral, escopo principal, decisões importantes);  
  - referência cruzada para os Capítulos 1–4 em `/Sprint 16/`.

- `docs/sprint_16_filemap_e_arquitetura.md`  
  - versão derivada deste Capítulo 3, focada no repositório (paths, contratos de layout, diagramas textuais);  
  - usada como referência rápida para navegação no repo.

- `docs/sprint_16_threat_model.md`  
  - documento central do Threat Model S16;  
  - seções mínimas: visão geral, ativos, atores, ameaças, mitigação, riscos residuais, mapeamento ameaça → cenários/gates.

- `docs/sprint_16_orr_summary.md`  
  - resumo do ORR da S16 (T0–T8), incluindo decisão final GO/GO_WITH_RESTRICTIONS/NO_GO;  
  - links para scorecards e evidências relevantes em `out/`.

Esses docs formam a "frente documental" da S16, em linha com o padrão criado na S15.

---

### 4. Gates T0–T8 da S16 (bin/)

#### 4.1 Scripts de gates

Os gates T0–T8 da S16 serão expostos via scripts shell em `bin/`, seguindo a convenção já usada em sprints anteriores:

- `bin/s16_t0_sanity.sh`  
- `bin/s16_t1_threat_model.sh`  
- `bin/s16_t2_attack_scenarios.sh`  
- `bin/s16_t3_debunker_and_committees_under_attack.sh`  
- `bin/s16_t4_anchors_and_anti_canetada.sh`  
- `bin/s16_t5_stress_and_degradation.sh`  
- `bin/s16_t6_security_observability.sh`  
- `bin/s16_t7_ci_and_repro.sh`  
- `bin/s16_t8_go_no_go.sh`

Contratos fortes para esses scripts:

- devem ser **idempotentes** (rodar duas vezes não deve corromper artefatos nem mudar decisões, salvo timestamps);  
- devem respeitar `PYTHONPATH=.` e não depender de hacks globais de ambiente;  
- `exit 0` somente quando o gate concluir e o `status` indicado no scorecard for coerente;  
- em caso de erro estrutural, devem retornar `exit != 0` e registrar o motivo no scorecard/logs.

Cada script:

- é responsável por **um** gate;  
- prepara o ambiente necessário para aquele gate;  
- chama scripts Python/serviços auxiliares em `scripts/` e/ou `inspectah/*`;  
- escreve um scorecard JSON específico em `out/scorecards/` e evidências em `out/evidence/`.

#### 4.2 Orquestrador de gates S16

- `bin/s16_all_gates.sh`  
  - executa, em ordem, os gates T0–T8;  
  - por padrão, interrompe na primeira falha (comportamento padrão, salvo exceções documentadas no Cap. 4);  
  - imprime no terminal um resumo legível de status, apontando para paths de scorecards.

Contrato de uso:

- execução padrão (local):  
  - `PYTHONPATH=. bin/s16_all_gates.sh`  
- execução por gate (para debugging):  
  - `PYTHONPATH=. bin/s16_t3_debunker_and_committees_under_attack.sh` etc.

---

### 5. Scripts de apoio da S16 (scripts/)

A S16 introduz scripts Python para concretizar cenários de ataque, stress e checks de Threat Model. A organização proposta é:

- `scripts/s16_threat_model_checks.py`  
  - valida estrutura básica de `docs/sprint_16_threat_model.md` (seções obrigatórias, links para módulos e scripts);  
  - é usado principalmente por T1.

- `scripts/s16_attack_scenarios.py`  
  - mantém o registro canônico de cenários de ataque: mapping ameaça → função de cenário;  
  - fornece CLI para rodar um ou vários cenários;  
  - é usado por T2 (para smoke e listagem) e como backend para T3–T5.

- `scripts/s16_debunker_and_committees_under_attack.py`  
  - orquestra cenários focados em Debunker v1 e Comitês V1/V2/V3;  
  - gera relatórios agregados para T3.

- `scripts/s16_anchors_and_anti_canetada_tests.py`  
  - dispara cenários de falha em âncoras e tentativas de bypass de anti‑canetada;  
  - consolida resultados para T4.

- `scripts/s16_stress_and_degradation.py`  
  - executa testes de stress contra fluxos críticos (disputas, anchoring, comitês);  
  - coleta métricas básicas e escreve resumos para T5.

- `scripts/s16_security_observability_checks.py`  
  - executa consultas padrão em logs/métricas para simular investigações;  
  - ajuda T6 a responder às perguntas do Threat Model.

- `scripts/s16_ci_and_repro_checks.py`  
  - inspeciona configurações `.ci/*` relacionadas à S16;  
  - opcionalmente consome artefatos de runs recentes da CI (paths/links) para T7.

Contratos recomendados para esses scripts:

- interface CLI clara (`python scripts/s16_*.py --help`);  
- saída estruturada (JSON e/ou logs com prefixos identificáveis por gate);  
- não assumir caminhos mágicos fora do repo;  
- permitir, quando fizer sentido, filtros/flags para rodar subconjuntos de cenários.

---

### 6. Ajustes em módulos centrais (inspectah/*)

A S16 **não** recria a pilha S13–S15, mas pode aplicar ajustes focados em hardening. Arquivos mais prováveis de sofrer pequenas mudanças:

- `inspectah/debunker/*`  
  - ajustes finos de regras, thresholds, tipos de relatório, campos de risco;  
  - invariantes que garantam que saídas perigosas sejam sempre marcadas com flags adequadas.

- `inspectah/committees/*`  
  - reforço de checks em V1/V2/V3;  
  - limites para decisões automáticas em cenários de altíssimo risco;  
  - logging adicional de votos, dissensos e coerência.

- `inspectah/anchors/*`  
  - comportamento mais robusto frente a falhas de chain (retries, estados intermediários bem documentados);  
  - validações extras de integridade de Merkle/batches.

- `inspectah/commands/__init__.py`  
  - endurecimento do anti‑canetada com invariantes claras (por exemplo, “nenhum estado crítico é mutado sem gerar um evento de disputa/override auditável”).

Qualquer alteração feita pela S16 nesses módulos deve ser:

- motivada por riscos do Threat Model (Cap. 1/2);  
- coberta por cenários de ataque/testes;  
- documentada em `docs/sprint_16_threat_model.md` e/ou `docs/sprint_16_orr_summary.md`.

Se a S16 precisar de fixtures específicas (por exemplo, casos artificiais de blocos/mandatos/projetos para ataques), elas devem ser colocadas em locais previsíveis, como:

- `inspectah/debunker/fixtures_s16/*.json` **ou**  
- `fixtures/s16/*.json` (a definir no Cap. 4),

sempre com documentação mínima nos docs da S16.

---

### 7. Scorecards e evidências da S16 (out/)

A S16 segue os contratos existentes de `out/scorecards/` e `out/evidence/`, adicionando a camada S16.

#### 7.1 Scorecards (out/scorecards/)

Para cada gate, haverá um scorecard JSON específico, com nome padrão:

- `out/scorecards/S16_T0_sanity.json`  
- `out/scorecards/S16_T1_threat_model.json`  
- `out/scorecards/S16_T2_attack_scenarios.json`  
- `out/scorecards/S16_T3_debunker_and_committees_under_attack.json`  
- `out/scorecards/S16_T4_anchors_and_anti_canetada.json`  
- `out/scorecards/S16_T5_stress_and_degradation.json`  
- `out/scorecards/S16_T6_security_observability.json`  
- `out/scorecards/S16_T7_ci_and_repro.json`  
- `out/scorecards/S16_T8_go_no_go.json`

Campos mínimos recomendados em cada scorecard:

- `gate`: identificação textual (ex.: "S16_T3_debunker_and_committees_under_attack");  
- `status`: "PASS" | "FAIL";  
- `decision`: "GO" | "NO_GO" | "GO_WITH_RESTRICTIONS" (quando aplicável);  
- `timestamp`: data/hora da execução;  
- `inputs`: resumo de parâmetros/flags relevantes;  
- `metrics`: dicionário com métricas relevantes do gate;  
- `evidence_paths`: lista de paths em `out/evidence/...`;  
- `notes`: observações relevantes (limitações, riscos residuais, TODOs explícitos de segurança).

Contrato extra para a S16:

- scorecards devem ser **append‑only** no tempo: novas execuções geram novos arquivos (com timestamp ou hash no nome quando fizer sentido) ou sobrescrevem de forma claramente rastreável (documentada no Cap. 4 e no ORR).

#### 7.2 Evidências (out/evidence/)

Cada gate da S16 escreverá evidências em subpastas específicas, seguindo o padrão:

- `out/evidence/S16_T0_sanity/`  
- `out/evidence/S16_T1_threat_model/`  
- `out/evidence/S16_T2_attack_scenarios/`  
- `out/evidence/S16_T3_debunker_and_committees/`  
- `out/evidence/S16_T4_anchors_and_anti_canetada/`  
- `out/evidence/S16_T5_stress_and_degradation/`  
- `out/evidence/S16_T6_security_observability/`  
- `out/evidence/S16_T7_ci_and_repro/`  
- `out/evidence/S16_T8_go_no_go/`

Dentro de cada pasta, espera‑se encontrar:

- `MANIFEST.json` com lista de arquivos, descrições sucintas e checksums;  
- arquivos de logs, dumps, amostras de relatórios, snapshots de consultas/painéis;  
- materiais auxiliares usados no ORR (por exemplo, tabelas resumidas de ataques e resultados).

Princípio: **scorecard conta a história em alto nível; pasta de evidências traz as provas detalhadas**, sempre separando S16 de sprints anteriores.

---

### 8. CI da Sprint 16 (.ci/)

A S16 estende a camada de CI com workflows específicos, sem quebrar o que já existe para S10/S15:

- `.ci/sprint_16_gates.yml`  
  - roda, em ambiente de CI, o equivalente de `PYTHONPATH=. bin/s16_all_gates.sh` ou um subconjunto crítico (T0–T4, por exemplo);  
  - é usado para validar PRs/branches relacionados à S16.

- `.ci/sprint_16_nightly.yml`  
  - roda, em base diária ou outra cadência, um conjunto de testes de segurança mais pesados (stress, ataques mais longos);  
  - produz artefatos adicionais para inspeção manual quando necessário.

Contratos para os workflows S16:

- expor artefatos produzidos (logs/scorecards) de forma previsível;  
- falhar o job quando gates críticos derem FAIL;  
- documentar, em `docs/sprint_16_orr_summary.md`, quais gates da S16 estão cobertos em CI e quais ficam apenas para rodadas locais/nightly.

---

### 9. Integração com sprints anteriores

A S16 precisa respeitar e reforçar a estrutura estabelecida em sprints anteriores:

- **S10**  
  - Truth‑DB, ingestão e observabilidade básica;  
  - S16 aproveita a infraestrutura de logs/métricas/painéis, adicionando consultas específicas de segurança (via `scripts/s16_security_observability_checks.py` e configs).

- **S13–S14**  
  - Sistema de Blocos, disputas e write path;  
  - S16 não altera fundamentos, apenas endurece comportamentos críticos e invariantes sensíveis (via ajustes em `inspectah/commands/`, `inspectah/anchors/` e afins).

- **S15**  
  - Debunker v1, Comitês V1/V2/V3, Âncoras, Anti‑canetada, gates S15;  
  - S16 toma a S15 como base funcional e acrescenta Threat Model, cenários de ataque, hardening e ORR de segurança.

Arquiteturalmente, a ideia é clara: **cada camada adiciona proteção sem quebrar a anterior**. A S16 é uma camada de "pressão + análise" sobre o que já foi construído.

---

### 10. Relação com o Capítulo 4 (runbook)

Este Capítulo 3 define onde tudo mora e quais são os contratos de layout. O Capítulo 4 da S16 vai:

- detalhar **como** rodar cada gate localmente e em CI (comandos exatos, variáveis de ambiente, flags);  
- fornecer superprompts para Codex implementar/ajustar cada script `bin/s16_tX_*.sh` e `scripts/s16_*.py`;  
- descrever fluxos de troubleshooting e investigação usando `out/scorecards/` e `out/evidence/`;  
- amarrar os comandos de dia‑a‑dia com os arquivos definidos aqui.

Com Capítulos 1, 2 e 3 consolidados e coerentes, a Sprint 16 passa a ter **contexto, mapa de qualidade e filemap/arquitetura sólidos**, prontos para serem materializados via implementação e automação no Capítulo 4.