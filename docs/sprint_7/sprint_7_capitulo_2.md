# Sprint 7 — Capítulo 2

## Gates de Validação (S7-G0…S7-G8)

> Arquivo de referência: `docs/sprint_7/sprint_7_capitulo_2.md`  
> Este capítulo define os gates de validação da Sprint 7. Eles são o gargalo máximo para qualquer entrega da sprint.  
> Se um gate não passar, a Sprint 7 está em **NO-GO**.  
> Os scripts e scorecards aqui definidos devem aparecer **idênticos** no filemap do Capítulo 3.

---

## 0. Papel e contrato dos gates na Sprint 7

Na Sprint 7, os gates S7-G0…S7-G8 garantem que o Inspectah Alpha com interface:

- se apoia em uma base S6 íntegra e reprodutível;
- expõe corretamente o runtime através da UI (sem divergência entre o que a UI mostra e o que o motor faz);
- permite que admin e usuário operem o domínio piloto **sem terminal**;
- calcula uma "verdade consolidada" de forma clara e explicável;
- preserva rastreabilidade até a evidência bruta;
- atende às métricas M1–M6 definidas no Capítulo 1.

Cada gate é um **contrato rígido**. O Capítulo 3 (filemap) e o Capítulo 4 (execução) devem:

- declarar exatamente os scripts `bin/s7_g*_*.sh` e paths de evidência/scorecards descritos aqui;
- garantir que esses gates possam ser executados em sequência (ou individualmente) de forma reprodutível.

Todos os gates seguem o padrão:

- Script principal: `bin/s7_gX_*.sh` (ver tabela a seguir).
- Evidência: `out/evidence/S7_GX_*/`.
- Scorecard: `out/scorecards/S7_GX_*.json`.

A Sprint 7 só pode ser declarada GO se **S7-G0…S7-G7** estiverem em `status == "PASS"` e o gate **S7-G8** retornar `decision == "GO"`.

---

## 1. Visão geral dos gates

| Gate   | Script alvo                         | Scorecard                                      | Foco principal                                            |
|--------|-------------------------------------|------------------------------------------------|-----------------------------------------------------------|
| S7-G0  | `bin/s7_g0_baseline.sh`            | `out/scorecards/S7_G0_baseline.json`          | Baseline S6 íntegra + docs mínimos da S7                  |
| S7-G1  | `bin/s7_g1_ui_boot_health.sh`      | `out/scorecards/S7_G1_ui_boot_health.json`    | UI sobe, responde health e enxerga runtime S6             |
| S7-G2  | `bin/s7_g2_ui_sources_admin.sh`    | `out/scorecards/S7_G2_ui_sources_admin.json`  | Fontes gerenciáveis via UI, refletindo em configs reais   |
| S7-G3  | `bin/s7_g3_ui_fields_preview.sh`   | `out/scorecards/S7_G3_ui_fields_preview.json` | Modelo canônico e preview alinhados ao runtime S6         |
| S7-G4  | `bin/s7_g4_ui_query_consolidation.sh` | `out/scorecards/S7_G4_ui_query_consolidation.json` | Consulta + decisão consolidada corretas e explicáveis |
| S7-G5  | `bin/s7_g5_ui_evidence_trace.sh`   | `out/scorecards/S7_G5_ui_evidence_trace.json` | Rastreabilidade de evidência em até 2 cliques             |
| S7-G6  | `bin/s7_g6_ui_only_flows.sh`       | `out/scorecards/S7_G6_ui_only_flows.json`     | Fluxos UI-only (admin e usuário) sem terminal             |
| S7-G7  | `bin/s7_g7_metrics_and_demo.sh`    | `out/scorecards/S7_G7_metrics_and_demo.json`  | Métricas M1–M6 + demo cronometrada                        |
| S7-G8  | `bin/s7_g8_sprint_go_no_go.sh`     | `out/scorecards/S7_G8_sprint_go_no_go.json`   | Agregador final da S7 — decisão GO/NO-GO                  |

Todos esses nomes e paths devem constar, **sem variação**, no Capítulo 3.

---

## 2. Gate S7-G0 — Baseline S6 + Wiring S7

**Identificação**  
- ID: `S7-G0`  
- Script: `bin/s7_g0_baseline.sh`  
- Scorecard: `out/scorecards/S7_G0_baseline.json`  
- Evidência: `out/evidence/S7_G0_baseline/`

**Objetivo**  
Garantir que a Sprint 7 parte de uma base íntegra e reproduzível:

- todos os gates da Sprint 6 (`S6-G0…S6-G8`) estão em PASS/GO;
- os artefatos mínimos da Sprint 7 existem e estão acessíveis (Capítulo 1, pasta `docs/sprint_7/` e esqueleto da UI).

> Gate **bloqueante**: se S7-G0 falhar, S7-G8 deve retornar `NO_GO`, independentemente dos demais gates.

**Entradas**  
- Repositório no estado pós-Sprint 6, com commits da S6 aplicados.
- Scripts `bin/s6_g*_*.sh` presentes e executáveis.
- Documentos:
  - `docs/sprint_7/sprint_7_capitulo_1.md` (aprovado).

**Procedimento (alto nível)**

1. Executar a suíte S6, em sequência ou via wrapper:
   - `bin/s6_g0_domain_setup.sh`
   - `bin/s6_g1_sources_registry.sh`
   - `...`
   - `bin/s6_g8_sprint_go_no_go.sh`
2. Verificar que o scorecard de `S6-G8` indica `decision == "GO"`.
3. Verificar existência dos artefatos mínimos:
   - `docs/sprint_7/sprint_7_capitulo_1.md`;
   - pasta `docs/sprint_7/` criada;
   - esqueleto de estrutura da UI (paths definidos no Capítulo 3).
4. Registrar resultado no scorecard S7-G0.

**Evidências**

- `out/evidence/S7_G0_baseline/summary.json` com:
  - status dos gates S6-G0…S6-G8;
  - caminho dos scorecards da S6 usados;
  - flags de presença de docs da S7.
- `out/scorecards/S7_G0_baseline.json` com campos mínimos:
  - `status`: `PASS` ou `FAIL`;
  - `s6_all_gates_pass`: boolean;
  - `s7_docs_present`: boolean;
  - `details`: lista de problemas, se houver.

**Critério de PASS**

- `s6_all_gates_pass == true` **e** `s7_docs_present == true`.
- `status == "PASS"`.

---

## 3. Gate S7-G1 — UI Boot & Health

**Identificação**  
- ID: `S7-G1`  
- Script: `bin/s7_g1_ui_boot_health.sh`  
- Scorecard: `out/scorecards/S7_G1_ui_boot_health.json`  
- Evidência: `out/evidence/S7_G1_ui_boot_health/`

**Objetivo**  
Garantir que a aplicação web da S7:

- sobe corretamente em ambiente local;
- expõe um endpoint de health/status;
- declara sua versão e a presença do runtime S6.

> Gate **bloqueante**: se S7-G1 falhar, S7-G8 deve retornar `NO_GO`.

**Entradas**  
- Código da UI presente conforme filemap da S7 (Capítulo 3).
- Runtime S6 acessível pela camada da UI.

**Procedimento (alto nível)**

1. Subir a aplicação (via script definido no Capítulo 4, ex.: `bin/s7_ui_start.sh`).
2. Aguardar até que o endpoint de health responda (ex.: `GET /health`).
3. Ler o payload de health, verificando:
   - `health_status == "ok"`;
   - campo de versão da UI (ex.: `version: "sprint7-alpha"`);
   - flag indicando `runtime_s6_accessible == true`.
4. Medir o tempo entre start e resposta de health.
5. Encerrar a aplicação, se for o caso.

**Evidências**

- `out/evidence/S7_G1_ui_boot_health/health_response.json` contendo o payload.
- `out/evidence/S7_G1_ui_boot_health/log.txt` com log de boot/stop.
- `out/scorecards/S7_G1_ui_boot_health.json` com campos mínimos:
  - `status`;
  - `ui_boot_time_seconds`;
  - `health_status`;
  - `runtime_s6_accessible`.

**Critério de PASS**

- `health_status == "ok"`.
- `runtime_s6_accessible == true`.
- `ui_boot_time_seconds` dentro do limite definido por M1 (Capítulo 1) e detalhado no Capítulo 4.

---

## 4. Gate S7-G2 — Fontes gerenciáveis via UI

**Identificação**  
- ID: `S7-G2`  
- Script: `bin/s7_g2_ui_sources_admin.sh`  
- Scorecard: `out/scorecards/S7_G2_ui_sources_admin.json`  
- Evidência: `out/evidence/S7_G2_ui_sources_admin/`

**Objetivo**  
Garantir que o admin consegue **gerenciar fontes pela UI**, e que essas mudanças se refletem corretamente nas configs reais, sem edição manual.

> Gate **bloqueante** para M3: se S7-G2 falhar, a métrica M3 não pode ser considerada atendida e S7-G8 deve retornar `NO_GO`.

**Entradas**  
- UI da S7 operando.
- Fontes iniciais (`fonte_a`, `fonte_b`, `fonte_c`) configuradas.

**Procedimento (alto nível)**

1. Via UI, listar as fontes do domínio piloto.
2. Escolher uma fonte existente (ex.: `fonte_b`):
   - alterar um parâmetro controlado (ex.: label, descrição ou endpoint de teste);
   - salvar;
   - verificar, de forma automatizada, que `config/sources/fonte_b.yaml` foi atualizado.
3. Criar uma nova fonte de teste (ex.: `fonte_teste_ui`):
   - definir tipo e endpoint plausíveis;
   - salvar;
   - verificar que o novo arquivo de config existe e é válido.
4. Se houver suporte a "desativar" fonte via UI, testar e verificar que o estado de desativado é persistido.

**Evidências**

- `out/evidence/S7_G2_ui_sources_admin/before_after_sources.json` com diffs dos arquivos de config impactados.
- `out/evidence/S7_G2_ui_sources_admin/ui_flow_notes.md` com passos executados.
- `out/scorecards/S7_G2_ui_sources_admin.json` com campos mínimos:
  - `status`;
  - `sources_listed_via_ui`;
  - `update_reflected_in_config`;
  - `new_source_created`;
  - `disabled_state_supported` (se aplicável);
  - `errors`.

**Critério de PASS**

- `sources_listed_via_ui == true`.
- `update_reflected_in_config == true`.
- `new_source_created == true`.
- Arquivos gerados/alterados são válidos (YAML parseável, campos obrigatórios presentes).

---

## 5. Gate S7-G3 — Modelo canônico & preview via UI

**Identificação**  
- ID: `S7-G3`  
- Script: `bin/s7_g3_ui_fields_preview.sh`  
- Scorecard: `out/scorecards/S7_G3_ui_fields_preview.json`  
- Evidência: `out/evidence/S7_G3_ui_fields_preview/`

**Objetivo**  
Garantir que a UI exibe o modelo canônico e o preview de registros **em linha** com o que o runtime S6 produz.

**Entradas**  
- `config/fields/dominio_piloto.yaml` vigente.
- Dados coletados previamente pelo runtime S6.

**Procedimento (alto nível)**

1. Via UI, acessar "Modelo de campos" do domínio piloto.
2. Capturar a lista de campos exibidos.
3. Ler `config/fields/dominio_piloto.yaml` e construir a lista de campos esperados.
4. Solicitar um preview canônico na UI, usando registros de exemplo.
5. Rodar `bin/inspectah_fields_preview.sh` (ou equivalente) e capturar amostras.
6. Comparar amostras UI x CLI campo a campo.

**Evidências**

- `out/evidence/S7_G3_ui_fields_preview/ui_fields_snapshot.json`.
- `out/evidence/S7_G3_ui_fields_preview/cli_vs_ui_sample.json`.
- `out/scorecards/S7_G3_ui_fields_preview.json` com campos mínimos:
  - `status`;
  - `fields_schema_match`;
  - `sample_records_compared`;
  - `sample_records_mismatched`.

**Critério de PASS**

- `fields_schema_match == true`.
- `sample_records_mismatched == 0` para o conjunto de amostras definido.

---

## 6. Gate S7-G4 — Consulta & decisão consolidada

**Identificação**  
- ID: `S7-G4`  
- Script: `bin/s7_g4_ui_query_consolidation.sh`  
- Scorecard: `out/scorecards/S7_G4_ui_query_consolidation.json`  
- Evidência: `out/evidence/S7_G4_ui_query_consolidation/`

**Objetivo**  
Garantir que a tela de consulta:

- retorna resultados por fonte de forma consistente com o runtime;
- calcula um valor consolidado conforme a estratégia da S7;
- apresenta uma explicação legível de como o valor foi obtido.

> Gate **bloqueante** para M4 e M5: se S7-G4 falhar, as métricas M4 e M5 não podem ser consideradas atendidas e S7-G8 deve retornar `NO_GO`.

**Entradas**  
- UI operacional, com dados coletados.
- Estratégia de agregação implementada.

**Procedimento (alto nível)**

1. Selecionar um conjunto de consultas de teste representativas (definidas neste gate como parte da evidência `test_queries.json`).
2. Para cada consulta:
   - executar via UI;
   - capturar resultados por fonte, valor consolidado e explicação;
   - executar consulta equivalente via CLI/query engine;
   - comparar UI x CLI registro a registro.
3. Validar se o valor consolidado bate com a regra documentada.

**Evidências**

- `out/evidence/S7_G4_ui_query_consolidation/test_queries.json`.
- `out/evidence/S7_G4_ui_query_consolidation/ui_vs_cli_results.json`.
- `out/scorecards/S7_G4_ui_query_consolidation.json` com campos mínimos:
  - `status`;
  - `queries_executed`;
  - `queries_with_per_source_mismatch`;
  - `queries_with_consolidation_mismatch`;
  - `explanations_present`.

**Critério de PASS**

- `queries_with_per_source_mismatch == 0`.
- `queries_with_consolidation_mismatch == 0`.
- `explanations_present == true`.

---

## 7. Gate S7-G5 — Evidência & rastreabilidade na UI

**Identificação**  
- ID: `S7-G5`  
- Script: `bin/s7_g5_ui_evidence_trace.sh`  
- Scorecard: `out/scorecards/S7_G5_ui_evidence_trace.json`  
- Evidência: `out/evidence/S7_G5_ui_evidence_trace/`

**Objetivo**  
Garantir que, a partir da UI, é possível navegar até a evidência bruta de qualquer registro exibido, em até 2 cliques, de forma confiável.

> Gate **bloqueante** para M6: se S7-G5 falhar, a métrica M6 não pode ser considerada atendida e S7-G8 deve retornar `NO_GO`.

**Entradas**  
- UI de consulta e/ou tela de detalhe implementada.
- Pacotes de evidência em `out/evidence/dominio_piloto/...` coerentes com os dados exibidos.

**Procedimento (alto nível)**

1. Selecionar um subconjunto de registros exibidos na UI (por ex., 5 registros distintos).
2. Para cada registro:
   - seguir os links/botões de evidência pela UI;
   - contar cliques até atingir uma representação de evidência;
   - capturar identificador/caminho do pacote de evidência.
3. Verificar, no filesystem, que os identificadores apontam para pacotes reais e consistentes.

**Evidências**

- `out/evidence/S7_G5_ui_evidence_trace/navigation_paths.json`.
- `out/evidence/S7_G5_ui_evidence_trace/evidence_checks.json`.
- `out/scorecards/S7_G5_ui_evidence_trace.json` com campos mínimos:
  - `status`;
  - `records_tested`;
  - `max_clicks_to_evidence`;
  - `records_with_inconsistent_evidence`.

**Critério de PASS**

- `max_clicks_to_evidence <= 2`.
- `records_with_inconsistent_evidence == 0`.

---

## 8. Gate S7-G6 — Fluxos UI-only (admin e usuário)

**Identificação**  
- ID: `S7-G6`  
- Script: `bin/s7_g6_ui_only_flows.sh`  
- Scorecard: `out/scorecards/S7_G6_ui_only_flows.json`  
- Evidência: `out/evidence/S7_G6_ui_only_flows/`

**Objetivo**  
Validar que as histórias-chave S7-A1 (admin) e S7-B1 (usuário) podem ser executadas **sem terminal**, atendendo às métricas M1 e M2.

> Gate diretamente ligado a M1 e M2: se S7-G6 falhar, M1 e M2 são consideradas não atendidas e S7-G8 deve retornar `NO_GO`.

**Entradas**  
- UI completa da S7 disponível.
- Cenários de teste para S7-A1 e S7-B1.

**Procedimento (alto nível)**

1. História S7-A1 (admin):
   - uma pessoa executa o fluxo de listar fontes → editar uma fonte → salvar → validar preview canônico;
   - registrar se em algum momento o terminal foi usado;
   - registrar tempo total do fluxo.
2. História S7-B1 (usuário):
   - executar o fluxo de abrir tela de consulta → definir parâmetros → rodar consulta → ver fontes + consolidado + explicação;
   - registrar uso (ou não) de terminal;
   - registrar tempo total do fluxo.

**Evidências**

- `out/evidence/S7_G6_ui_only_flows/flow_notes.md`.
- `out/evidence/S7_G6_ui_only_flows/timings.json`.
- `out/scorecards/S7_G6_ui_only_flows.json` com campos mínimos:
  - `status`;
  - `admin_flow_duration_seconds`;
  - `user_flow_duration_seconds`;
  - `terminal_used` (boolean).

**Critério de PASS**

- `terminal_used == false`.
- Tempos dentro do limite de M1 (demo completa em até 5 minutos, conforme Capítulo 1).

---

## 9. Gate S7-G7 — Métricas M1–M6 & demo cronometrada

**Identificação**  
- ID: `S7-G7`  
- Script: `bin/s7_g7_metrics_and_demo.sh`  
- Scorecard: `out/scorecards/S7_G7_metrics_and_demo.json`  
- Evidência: `out/evidence/S7_G7_metrics_and_demo/`

**Objetivo**  
Consolidar, em um gate único, a verificação objetiva das métricas **M1–M6** e do roteiro de demo UI-only.

> Gate **leonino**: se qualquer métrica M1…M6 falhar aqui, S7-G8 deve retornar `NO_GO`.

**Entradas**  
- Evidências e scorecards dos gates S7-G1…S7-G6.
- Thresholds de M1–M6, conforme Capítulo 1.

**Procedimento (alto nível)**

1. Consumir evidências de S7-G1…S7-G6 e extrair valores observados para M1–M6.
2. Se necessário, executar uma rodada final da demo UI-only para confirmar tempos.
3. Comparar valores observados com thresholds de M1–M6.
4. Emitir scorecard consolidado com flags `M1_pass`…`M6_pass`.

**Evidências**

- `out/evidence/S7_G7_metrics_and_demo/m1_m6_observed.json`.
- `out/evidence/S7_G7_metrics_and_demo/demo_log.md`.
- `out/scorecards/S7_G7_metrics_and_demo.json` com campos mínimos:
  - `status`;
  - `M1_pass`, `M2_pass`, `M3_pass`, `M4_pass`, `M5_pass`, `M6_pass`;
  - `details`.

**Critério de PASS**

- Todas as flags `M1_pass`…`M6_pass` marcadas como `true`.
- `status == "PASS"`.

---

## 10. Gate S7-G8 — Sprint 7 GO/NO-GO

**Identificação**  
- ID: `S7-G8`  
- Script: `bin/s7_g8_sprint_go_no_go.sh`  
- Scorecard: `out/scorecards/S7_G8_sprint_go_no_go.json`  
- Evidência: `out/evidence/S7_G8_sprint_go_no_go/`

**Objetivo**  
Agregador final da Sprint 7. Este gate lê os scorecards S7-G0…S7-G7 (e opcionalmente o S6-G8 mais recente) e emite uma decisão única:

- `decision`: `GO` ou `NO_GO`.

**Entradas**  
- `out/scorecards/S7_G0_baseline.json`
- `out/scorecards/S7_G1_ui_boot_health.json`
- `out/scorecards/S7_G2_ui_sources_admin.json`
- `out/scorecards/S7_G3_ui_fields_preview.json`
- `out/scorecards/S7_G4_ui_query_consolidation.json`
- `out/scorecards/S7_G5_ui_evidence_trace.json`
- `out/scorecards/S7_G6_ui_only_flows.json`
- `out/scorecards/S7_G7_metrics_and_demo.json`

**Procedimento (alto nível)**

1. Ler todos os scorecards S7-G0…S7-G7.
2. Verificar que `status == "PASS"` em cada um.
3. Opcionalmente, verificar se o S6-G8 mais recente ainda está em GO.
4. Construir um resumo consolidado com:
   - lista de gates e seus status;
   - flags M1–M6;
   - observações de risco ou limitações.
5. Definir `decision`:
   - `GO` se todos os gates S7-G0…S7-G7 estiverem em `status == "PASS"`;
   - `NO_GO` caso contrário.

**Evidências**

- `out/evidence/S7_G8_sprint_go_no_go/summary.json`.
- `out/scorecards/S7_G8_sprint_go_no_go.json` com campos mínimos:
  - `decision` (`GO`/`NO_GO`);
  - `all_gates_pass` (boolean);
  - `failed_gates` (lista, se houver);
  - `timestamp`;
  - `notes`.

**Critério de GO**

- `all_gates_pass == true`.
- `decision == "GO"`.

Qualquer outro cenário implica **NO-GO** para a Sprint 7. O produto pode ser útil, mas, do ponto de vista do Sprint Playbook, a Sprint 7 só é considerada entregue quando o S7-G8 retornar **GO**.

