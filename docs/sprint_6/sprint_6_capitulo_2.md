# Sprint 6 — Capítulo 2 (v2)

Inspectah Data Hub Alpha — Gates de Validação (Funil de GO/NO‑GO da Sprint 6)

---

## 0) Papel deste capítulo

Este Capítulo 2 define **exclusivamente** os **gates de validação** da Sprint 6 do Inspectah e sua lógica de **GO/NO‑GO**. Ele é o manual definitivo de validação da sprint.

Ele responde, de forma operacional e sem ambiguidade:

- Quais são os gates S6‑G0…S6‑G8.
- Que scripts os implementam.
- Que scorecards e diretórios de evidência cada gate produz.
- Quais pré‑condições e pós‑condições cada gate garante.
- Como executar todos os gates em sequência no “dia de corte” da Sprint 6.

Tudo o que for construído na Sprint 6 deve existir para **alimentar e satisfazer esses gates**. Se um gate crítico falha ou não pode ser executado com evidência adequada, a sprint é **NO‑GO**, independentemente de quantas features foram implementadas.

---

## 1) Filosofia geral dos gates e dos statuses

### 1.1. Tipos de status

Cada gate S6‑G0…S6‑G7 emite um scorecard com um destes status:

- `PASS` — o gate foi executado com sucesso e todas as pré‑condições/pós‑condições foram satisfeitas;
- `WARN` — o gate tecnicamente passou, mas com ressalvas explicitamente documentadas no scorecard;
- `FAIL` — o gate não atingiu as condições mínimas e a Sprint 6 **não pode** ser marcada como concluída.

O gate final S6‑G8 emite um status de sprint:

- `GO` — todos os gates críticos estão em `PASS`, nenhum está em `FAIL`, warnings são pontuais e documentados;
- `NO_GO` — pelo menos um gate crítico está em `FAIL`, um scorecard essencial está ausente ou existe violação de invariante.

### 1.2. WARN vs FAIL (onde é aceitável?)

- `WARN` é aceitável **apenas** em situações com risco limitado e bem documentado, como:
  - fontes secundárias com cobertura parcial em S6‑G1;
  - campos opcionais com falhas pontuais em S6‑G2;
  - pequenas lacunas de observabilidade em S6‑G5;
  - limitações não críticas no bundle em S6‑G6.

- `WARN` **não é aceitável** em:
  - S6‑G0 (Domínio & Setup) — a sprint não pode começar em terreno instável;
  - S6‑G3 (Coleta & Evidência) — contrato de evidência precisa ser sólido;
  - S6‑G4 (Consulta Consolidada) — experiência mínima do operador não pode ser “meio‑pronta”;
  - S6‑G7 (Guard Automatizado) — guard não pode ser “meio guard”; ou funciona, ou não;
  - S6‑G8 (GO/NO‑GO) — não há `WARN` em decisão de sprint.

Em qualquer gate, se uma violação de invariante for detectada (por exemplo, registro sem evidência, sobrescrita silenciosa de evidência, consultas sem ponte para evidência), o resultado deve ser **`FAIL`**, nunca `WARN`.

### 1.3. Evidência como pré‑requisito de verdade

Regra absoluta: **scorecard sem evidência correspondente é inválido**.

Se existir `out/scorecards/S6_GX_*.json` sem um diretório de evidência `out/evidence/S6_GX_*/`, o gate é tratado como **não executado** para fins de GO/NO‑GO. Não é permitido “ajustar status manualmente” sem logs, manifests e amostras ancorando a decisão.

---

## 2) Roteiro do “Dia de Validação” da Sprint 6

Este é o filme operacional do dia de corte da Sprint 6, amarrado ao “Filme do operador” descrito no Capítulo 1.

Na prática, o dia de validação segue esta ordem:

1. `bin/s6_g0_domain_setup.sh`
2. `bin/s6_g1_sources_registry.sh`
3. `bin/s6_g2_field_designer.sh`
4. `bin/s6_g3_collect_evidence.sh`
5. `bin/s6_g4_explore_verify.sh`
6. `bin/s6_g5_metrics_obs.sh`
7. `bin/s6_g6_bundle_repro.sh`
8. `bin/s6_g7_guard_automation.sh`
9. `bin/s6_g8_sprint_go_no_go.sh`

O fluxo recomendado é:

- Rodar cada gate isoladamente da ordem G0→G7, corrigindo problemas até obter `PASS` (ou `WARN` aceitável nos casos permitidos).
- Em seguida, rodar S6‑G7 para validar a orquestração automatizada (G1→G4) em um único comando.
- Por fim, rodar S6‑G8 para consolidar a decisão de sprint.

Ao final do dia de validação:

- O operador consulta `out/scorecards/S6_G8_sprint_go_no_go.json`.
- Se `status` for `GO`, a Sprint 6 está aprovada do ponto de vista de validação.
- Se `status` for `NO_GO`, o próprio scorecard final indica quais gates estão em `FAIL` e onde investigar.

---

## 3) Mapa geral: Gate → Script → Scorecard → Evidência → Capítulo 1

| Gate   | Script                                | Scorecard                                    | Evidência                                 | Cap. 1 — Pilares / Contratos                           |
|--------|----------------------------------------|----------------------------------------------|-------------------------------------------|--------------------------------------------------------|
| S6‑G0  | `bin/s6_g0_domain_setup.sh`           | `out/scorecards/S6_G0_domain_setup.json`     | `out/evidence/S6_G0_domain_setup/`       | DoR, docs da sprint, domínio piloto                     |
| S6‑G1  | `bin/s6_g1_sources_registry.sh`       | `out/scorecards/S6_G1_sources_registry.json` | `out/evidence/S6_G1_sources_registry/`   | P1 — Source Registry v0                               |
| S6‑G2  | `bin/s6_g2_field_designer.sh`         | `out/scorecards/S6_G2_field_designer.json`   | `out/evidence/S6_G2_field_designer/`     | P2 — Field Designer v0, modelo canônico               |
| S6‑G3  | `bin/s6_g3_collect_evidence.sh`       | `out/scorecards/S6_G3_collect_evidence.json` | `out/evidence/S6_G3_collect_evidence/`   | P3 — Watchers + Evidence Vault, contrato de evidência |
| S6‑G4  | `bin/s6_g4_explore_verify.sh`         | `out/scorecards/S6_G4_explore_verify.json`   | `out/evidence/S6_G4_explore_verify/`     | P4 — Explore & Verify v0, filme do operador           |
| S6‑G5  | `bin/s6_g5_metrics_obs.sh`            | `out/scorecards/S6_G5_metrics_obs.json`      | `out/evidence/S6_G5_metrics_obs/`        | Métricas/SLOs mínimos                                  |
| S6‑G6  | `bin/s6_g6_bundle_repro.sh`           | `out/scorecards/S6_G6_bundle_repro.json`     | `out/evidence/S6_G6_bundle_repro/`       | P5 — Bundle S6 e reprodutibilidade                    |
| S6‑G7  | `bin/s6_g7_guard_automation.sh`       | `out/scorecards/S6_G7_guard_automation.json` | `out/evidence/S6_G7_guard_automation/`   | Guard da Sprint 6 (automatização de P1–P4)            |
| S6‑G8  | `bin/s6_g8_sprint_go_no_go.sh`        | `out/scorecards/S6_G8_sprint_go_no_go.json`  | `out/evidence/S6_G8_sprint_go_no_go/`    | Decisão final GO/NO‑GO da S6                          |

---

## 4) S6‑G0 — Domínio & Setup (Gate de Readiness)

### 4.1. Objetivo

Implementar, de forma automatizada, o **DoR** da Sprint 6:

- garantir que o domínio piloto está definido e documentado;
- garantir que Capítulo 1 e Capítulo 2 estão presentes;
- garantir que o repositório está limpo antes da execução dos demais gates.

### 4.2. Relação com o Capítulo 1

- Amarra diretamente a seção de DoR do Capítulo 1 (domínio piloto + docs da sprint).
- É o gate que responde: “Estamos autorizados a começar/fechar a Sprint 6?”.

### 4.3. Script, entradas e saídas

- Script: `bin/s6_g0_domain_setup.sh`
- Entradas esperadas:
  - `docs/sprint_6/sprint_6_capitulo_1.md`
  - `docs/sprint_6/sprint_6_capitulo_2.md`
  - `docs/sprint_6/dominio_piloto.md`
  - estado do repositório (`git status`)
- Saídas:
  - Scorecard: `out/scorecards/S6_G0_domain_setup.json`
  - Evidência: `out/evidence/S6_G0_domain_setup/` contendo:
    - snapshot de `git status`;
    - hashes dos docs da sprint;
    - cópia de `dominio_piloto.md`.

### 4.4. Pré‑condições

- Repo é o do Inspectah, com layout da Sprint 5 consolidado.
- Script `bin/s6_g0_domain_setup.sh` existe e é executável.

### 4.5. Pós‑condições

- Todos os docs obrigatórios da sprint existem e estão não vazios.
- `git status` está limpo no momento da execução.
- Scorecard S6‑G0 existe, está bem formado e indica o estado real.

### 4.6. Critérios de PASS/FAIL

- `PASS`:
  - todos os arquivos obrigatórios existem e passam validações básicas;
  - `git status` sem alterações relevantes;
  - scorecard com `status: "PASS"`.
- `FAIL`:
  - qualquer arquivo obrigatório ausente;
  - repo sujo;
  - scorecard não gerado ou `status: "FAIL"`.

### 4.7. Invariantes

- Nenhum outro gate S6‑G1…S6‑G8 é considerado válido se S6‑G0 estiver em `FAIL`.
- Qualquer mudança estrutural em docs ou domínio piloto exige reexecução de S6‑G0.

---

## 5) S6‑G1 — Modelo de Fontes (Source Registry)

### 5.1. Objetivo

Validar que o **Source Registry v0** (P1 do Capítulo 1) está correto, consistente e exercitável via dry‑run.

### 5.2. Relação com o Capítulo 1

- Implementa na prática o pilar **P1 — Registro declarativo de fontes**.
- Garante que, no filme do operador, quando ele abre `config/sources/`, encontra fontes reais e válidas.

### 5.3. Script, entradas e saídas

- Script do gate: `bin/s6_g1_sources_registry.sh`
- Script operacional que ele chama: `bin/inspectah_sources_validate.sh`
- Entradas:
  - diretório `config/sources/` com, no mínimo, `fonte_a.yaml`, `fonte_b.yaml`, `fonte_c.yaml`;
  - domínio piloto definido em `docs/sprint_6/dominio_piloto.md`.
- Saídas:
  - Scorecard: `out/scorecards/S6_G1_sources_registry.json`;
  - Evidência: `out/evidence/S6_G1_sources_registry/` com:
    - logs de validação/dry‑run;
    - amostras de respostas brutas (o necessário para diagnóstico, respeitando ToS).

### 5.4. Pré‑condições

- S6‑G0 em `PASS`.
- Arquivos de fonte existem em `config/sources/`.
- `bin/inspectah_sources_validate.sh` é executável.

### 5.5. Pós‑condições

- Cada fonte essencial do domínio piloto foi lida e validada estruturalmente.
- Para cada fonte, o dry‑run executou e produziu pelo menos uma amostra (salvo fontes documentadas como eventualmente vazias).
- Scorecard S6‑G1 registra o estado de cada fonte.

### 5.6. Critérios de PASS/WARN/FAIL

- `PASS`:
  - todas as fontes essenciais em `PASS` ou `WARN` justificado;
  - nenhum erro estrutural grave de configuração.
- `WARN` (aceitável):
  - fontes secundárias com baixa cobertura temporária;
  - pequenas instabilidades documentadas.
- `FAIL`:
  - qualquer fonte essencial em `FAIL`;
  - validador não roda ou não gera scorecard;
  - todas as fontes retornam zero itens sem explicação.

### 5.7. Invariantes

- Mudanças em `config/sources/*.yaml` exigem reexecução de S6‑G1.
- Nenhum gate posterior pode assumir fontes válidas se S6‑G1 estiver em `FAIL`.

---

## 6) S6‑G2 — Modelo Canônico (Field Designer)

### 6.1. Objetivo

Validar o **modelo canônico do domínio piloto** (P2) e o mapeamento fonte → campos canônicos.

### 6.2. Relação com o Capítulo 1

- Implementa o pilar **P2 — Field Designer v0**.
- Garante que os campos canônicos definidos em `config/fields/dominio_piloto.yaml` funcionam na prática.

### 6.3. Script, entradas e saídas

- Script do gate: `bin/s6_g2_field_designer.sh`
- Entradas:
  - `config/fields/dominio_piloto.yaml`;
  - arquivos de fonte em `config/sources/`;
  - scripts de preview, como `bin/inspectah_fields_preview.sh`.
- Saídas:
  - Scorecard: `out/scorecards/S6_G2_field_designer.json`;
  - Evidência: `out/evidence/S6_G2_field_designer/`, incluindo:
    - amostras de registros canônicos por fonte;
    - estatísticas de preenchimento por campo.

### 6.4. Pré‑condições

- S6‑G1 em `PASS` ou `WARN` aceitável.
- Arquivo de domínio canônico existe e é legível.

### 6.5. Pós‑condições

- Campos obrigatórios do domínio estão preenchidos em amostra significativa.
- Falhas de parsing são conhecidas e documentadas.
- Scorecard S6‑G2 reflete a cobertura de campos por fonte.

### 6.6. Critérios de PASS/WARN/FAIL

- `PASS`:
  - todos os campos obrigatórios com cobertura satisfatória;
  - erros de parsing isolados e explicados.
- `WARN` (aceitável):
  - campos opcionais com cobertura parcial;
  - fontes menos relevantes com lacunas de mapeamento.
- `FAIL`:
  - campos obrigatórios sistematicamente vazios;
  - scripts de preview falham estruturalmente;
  - não há scorecard ou ele indica `FAIL` global.

### 6.7. Invariantes

- Alterações em `config/fields/dominio_piloto.yaml` exigem reexecução de S6‑G2.
- Campos canônicos definidos aqui passam a ser contrato para as sprints futuras.

---

## 7) S6‑G3 — Coleta & Evidência (Watchers + Evidence Vault)

### 7.1. Objetivo

Validar o pilar **P3 — Watchers + Evidence Vault v0**, garantindo que a coleta produz pacotes de evidência completos, imutáveis e deduplicados.

### 7.2. Relação com o Capítulo 1

- Amarra diretamente o contrato de evidência (seção de contratos do Capítulo 1).
- Corresponde à parte do filme do operador em que ele roda `inspectah_collect_once.sh` e vê evidência em disco.

### 7.3. Script, entradas e saídas

- Script do gate: `bin/s6_g3_collect_evidence.sh`
- Script operacional central: `bin/inspectah_collect_once.sh dominio_piloto`
- Entradas:
  - configs em `config/sources/` e `config/fields/`;
  - ambiente preparado pelo S6‑G0.
- Saídas:
  - Scorecard: `out/scorecards/S6_G3_collect_evidence.json`;
  - Evidência:
    - `out/evidence/dominio_piloto/...` com pacotes reais;
    - `out/evidence/S6_G3_collect_evidence/` com logs da execução e amostras.

### 7.4. Pré‑condições

- S6‑G1 e S6‑G2 em `PASS` ou `WARN` aceitáveis.
- Scripts de coleta existem e são executáveis.

### 7.5. Pós‑condições

- Pelo menos um pacote de evidência novo por fonte essencial foi gerado (salvo ausência documentada de novidades).
- Estrutura de diretórios/arquivos respeita o contrato definido (manifest + raw + hash etc.).
- Reexecutar o ciclo não gera duplicatas indevidas.

### 7.6. Critérios de PASS/FAIL

- `PASS`:
  - execução completa com exit 0;
  - evidência materializada conforme contrato;
  - deduplicação consistente.
- `WARN`:
  - **não é permitido** em G3: qualquer quebra do contrato de evidência implica `FAIL`.
- `FAIL`:
  - scripts falham;
  - ausência de evidência;
  - deduplicação claramente quebrada.

### 7.7. Invariantes

- Evidência escrita não é sobrescrita silenciosamente.
- Violação de imutabilidade ou registro sem evidência associada = `FAIL` imediato.

---

## 8) S6‑G4 — Consulta Consolidada (Explore & Verify)

### 8.1. Objetivo

Validar o pilar **P4 — Explore & Verify v0** e a parte central do filme do operador: listar, filtrar e navegar dos resultados até a evidência.

### 8.2. Relação com o Capítulo 1

- Garante que o fluxo descrito na seção “Filme do operador” (Capítulo 1, seção 3) é verdade na prática.

### 8.3. Script, entradas e saídas

- Script do gate: `bin/s6_g4_explore_verify.sh`
- Scripts operacionais chamados:
  - `bin/inspectah_query.sh ...`
  - `bin/inspectah_show_evidence.sh ...`
- Entradas:
  - dados em `out/evidence/dominio_piloto/...`;
  - scripts de consulta e inspeção.
- Saídas:
  - Scorecard: `out/scorecards/S6_G4_explore_verify.json`;
  - Evidência: `out/evidence/S6_G4_explore_verify/` com:
    - outputs JSON/CSV de consultas típicas;
    - manifest + raw de um item inspecionado.

### 8.4. Pré‑condições

- S6‑G3 em `PASS`.
- Scripts de consulta e inspeção existem.

### 8.5. Pós‑condições

- Pelo menos uma consulta sem filtros retorna itens válidos.
- Filtros (datas + categoria + busca textual) funcionam.
- Paginação retorna resultados coerentes.
- É possível ir da consulta ao pacote de evidência de um item com comandos padrão.

### 8.6. Critérios de PASS/FAIL

- `PASS`:
  - todas as rotas de consulta e inspeção funcionam conforme esperado;
  - outputs batem com o modelo canônico e contratos de evidência.
- `WARN`:
  - **não é permitido** em G4; qualquer quebra do fluxo do operador implica `FAIL`.
- `FAIL`:
  - consultas retornam vazio sem justificativa;
  - inspeção de evidência falha;
  - scorecard indica problemas graves.

### 8.7. Invariantes

- Nenhuma alteração em consultas pode ser considerada segura sem reexecução de S6‑G4.
- Um registro retornado em consulta **deve** sempre apontar para evidência acessível.

---

## 9) S6‑G5 — Métricas & Observabilidade

### 9.1. Objetivo

Validar que a Sprint 6 expõe **métricas mínimas** para acompanhar latência, volume, falhas e frescor das fontes.

### 9.2. Relação com o Capítulo 1

- Implementa os SLOs e métricas da seção de métricas do Capítulo 1.

### 9.3. Script, entradas e saídas

- Script do gate: `bin/s6_g5_metrics_obs.sh`
- Script operacional: `bin/inspectah_metrics_snapshot.sh dominio_piloto`
- Entradas:
  - endpoint de métricas ou arquivos gerados pelo sistema;
  - dados recentes da coleta.
- Saídas:
  - Scorecard: `out/scorecards/S6_G5_metrics_obs.json`;
  - Evidência: `out/evidence/S6_G5_metrics_obs/` com:
    - snapshot bruto de métricas;
    - resumo interpretado.

### 9.4. Pré‑condições

- S6‑G3 e S6‑G4 em `PASS`.
- Métricas já expostas pelo sistema.

### 9.5. Pós‑condições

- Pelo menos um snapshot de métricas foi capturado durante a sprint.
- Métricas essenciais estão presentes (latência, volume, falhas, frescor).

### 9.6. Critérios de PASS/WARN/FAIL

- `PASS`:
  - métricas essenciais disponíveis e legíveis;
  - nenhuma anomalia crítica ignorada.
- `WARN` (aceitável):
  - métricas adicionais desejáveis ausentes, mas essenciais presentes;
  - pequenas lacunas na instrumentação, sem risco de cegueira total.
- `FAIL`:
  - ausência de métricas ou snapshot;
  - script de snapshot falha;
  - scorecard indica falhas graves.

### 9.7. Invariantes

- Falta de observabilidade nunca é tratada como detalhe cosmético.
- Futuras sprints podem estender as métricas, mas não remover as essenciais.

---

## 10) S6‑G6 — Bundle & Reprodutibilidade

### 10.1. Objetivo

Validar que o estado entregue pela Sprint 6 é **reprodutível** a partir de um bundle curado, alinhado ao pilar P5.

### 10.2. Relação com o Capítulo 1

- Implementa a ideia de `out/s6_bundle/` como snapshot oficial da Sprint 6.

### 10.3. Script, entradas e saídas

- Script do gate: `bin/s6_g6_bundle_repro.sh`
- Scripts operacionais que ele chama:
  - `bin/inspectah_s6_build_bundle.sh`
  - `bin/inspectah_s6_verify_bundle.sh`
- Entradas:
  - configs, evidências e docs já produzidos.
- Saídas:
  - Scorecard: `out/scorecards/S6_G6_bundle_repro.json`;
  - Evidência: `out/evidence/S6_G6_bundle_repro/` com:
    - lista de arquivos no bundle;
    - hash SHA256 do bundle;
    - resultado da verificação.

### 10.4. Pré‑condições

- Gates S6‑G0…S6‑G5 em `PASS` ou `WARN` aceitáveis.

### 10.5. Pós‑condições

- Bundle S6 existe, está íntegro e verificado.
- Verificador consegue reconstruir um mini fluxo (por exemplo, validação de fontes + pequena consulta) usando apenas o bundle.

### 10.6. Critérios de PASS/WARN/FAIL

- `PASS`:
  - bundle gerado e verificado com sucesso; hashes batem.
- `WARN` (aceitável):
  - bundle incompleto em detalhes não críticos (ex.: faltou um export opcional), mas núcleo está íntegro.
- `FAIL`:
  - bundle não gerado ou corrompido;
  - verificador falha;
  - falta descrição mínima de uso.

### 10.7. Invariantes

- `out/s6_bundle/` é tratado como artefato canônico da Sprint 6.
- Nenhuma evolução futura deve inutilizar esse bundle como ponto de diagnóstico.

---

## 11) S6‑G7 — Guardas Automatizados (CI/Local)

### 11.1. Objetivo

Validar que os gates essenciais da Sprint 6 (especialmente S6‑G1…S6‑G4) podem ser executados de forma **automatizada**, localmente e/ou em CI.

### 11.2. Relação com o Capítulo 1

- Amarra a exigência de que o Inspectah seja operável sem conhecimento secreto, apoiado em comandos únicos claros.

### 11.3. Script, entradas e saídas

- Script do gate: `bin/s6_g7_guard_automation.sh`
- Script guard principal: `bin/inspectah_s6_guard.sh` (invocado por CI e por humanos)
- Entradas:
  - scripts dos gates S6‑G1…S6‑G4.
- Saídas:
  - Scorecard: `out/scorecards/S6_G7_guard_automation.json`;
  - Evidência: `out/evidence/S6_G7_guard_automation/` com logs de execução do guard.

### 11.4. Pré‑condições

- Scripts dos gates S6‑G1…S6‑G4 existem e já foram testados individualmente.

### 11.5. Pós‑condições

- Um único comando (`bin/inspectah_s6_guard.sh`) executa S6‑G1…S6‑G4 em sequência.
- Scorecard S6‑G7 reflete o resultado agregado dessa execução.

### 11.6. Critérios de PASS/FAIL

- `PASS`:
  - guard existe, roda em ambiente limpo e gera scorecard;
  - todos os gates essenciais passam quando executados pelo guard.
- `WARN`:
  - **não é permitido** em G7; guard meio funcional é tratado como `FAIL`.
- `FAIL`:
  - scripts ausentes;
  - guard falha;
  - não há scorecard ou ele indica falhas.

### 11.7. Invariantes

- A existência de um guard automatizado é requisito não negociável para considerar a Sprint 6 como base estável.
- Integrações de CI devem chamar o guard (ou scripts equivalentes) como linha de defesa padrão.

---

## 12) S6‑G8 — Gate Final de GO/NO‑GO da Sprint 6

### 12.1. Objetivo

Ser o **gargalo máximo de validação**: consolidar os resultados de todos os gates anteriores e emitir o veredito final da Sprint 6 (GO/NO‑GO).

### 12.2. Relação com o Capítulo 1

- Amarra todos os pilares (P1–P5), contratos e SLOs numa decisão binária.

### 12.3. Script, entradas e saídas

- Script do gate: `bin/s6_g8_sprint_go_no_go.sh`
- Entradas:
  - scorecards:
    - `S6_G0_domain_setup.json`
    - `S6_G1_sources_registry.json`
    - `S6_G2_field_designer.json`
    - `S6_G3_collect_evidence.json`
    - `S6_G4_explore_verify.json`
    - `S6_G5_metrics_obs.json`
    - `S6_G6_bundle_repro.json`
    - `S6_G7_guard_automation.json`
- Saídas:
  - Scorecard final: `out/scorecards/S6_G8_sprint_go_no_go.json`;
  - Evidência: `out/evidence/S6_G8_sprint_go_no_go/summary.md` com resumo humano.

### 12.4. Pré‑condições

- Todos os gates S6‑G0…S6‑G7 já foram executados ao menos uma vez na sprint.

### 12.5. Pós‑condições

- Existe scorecard final com `status: "GO"` ou `"NO_GO"`;
- Mapa `gate → status` está completo;
- Qualquer `WARN` está documentado.

### 12.6. Lógica de decisão

- Se algum gate S6‑G0…S6‑G7 está em `FAIL` → `status: "NO_GO"`.
- Se falta scorecard de gate essencial → `status: "NO_GO"` (salvo exceção documentada explicitamente).
- Se todos estão em `PASS` (com alguns `WARN` aceitáveis) → `status: "GO"`.

### 12.7. Invariantes

- Nenhuma decisão de “Sprint 6 concluída” é válida sem execução de S6‑G8.
- S6‑G8 é o único ponto onde o veredito GO/NO‑GO da sprint é emitido formalmente.

---

## 13) Relação entre Gates, DoR e DoD da Sprint 6

- S6‑G0 materializa o **DoR** da Sprint 6 descrito no Capítulo 1.
- S6‑G1…S6‑G6 cobrem, em conjunto, o **DoD** (P1–P5: fontes, campos, coleta, consulta, observabilidade, bundle).
- S6‑G7 garante automatização e reexecutabilidade desses checks.
- S6‑G8 cola tudo isso em uma única palavra: `GO` ou `NO_GO`.

Se, ao final da sprint, o scorecard S6‑G8 não puder ser produzido, a Sprint 6 é tratada como **não concluída**, independentemente de quantas features foram implementadas.

---

## 14) Anti‑padrões e proibições explícitas

Para preservar o rigor do funil de validação da Sprint 6, ficam explicitamente proibidos:

1. Declarar a Sprint 6 concluída com qualquer gate S6‑G0…S6‑G7 em `FAIL`.
2. Ajustar manualmente um scorecard para `PASS` sem evidência correspondente em `out/evidence/`.
3. Criar caminhos paralelos de validação que não passem pelos scripts e scorecards definidos aqui.
4. Depender apenas de logs efêmeros de CI sem materializar arquivos de scorecard.
5. Alterar o significado de `PASS`, `WARN`, `FAIL`, `GO` ou `NO_GO` sem atualizar este capítulo.

---

## 15) Como usar este capítulo na prática

- Durante a sprint: cada vez que um pilar P1–P5 é trabalhado, o correspondente gate S6‑G1…S6‑G6 deve ser reexecutado e seu scorecard analisado.
- No dia de corte: seguir o roteiro da seção 2, rodando G0→G7 e finalmente G8, produzindo o veredito final.
- Nos Capítulos 3 e 4: registrar a cronologia de execuções dos gates, os ajustes feitos e as evidências principais, sempre referenciando os scorecards e diretórios descritos aqui.

A partir deste Capítulo 2 (v2), a Sprint 6 do Inspectah passa a ter um **funil de validação máximo, explícito e binário**: se não passou pelos gates, **não está pronto**. O resto é detalhe de implementação.

