# Sprint 7 — Capítulo 4 (v2)

## Execução da Sprint 7 (Inspectah UI Alpha)

> Arquivo de referência: `docs/sprint_7/sprint_7_capitulo_4.md`  
> Este capítulo traduz os objetivos (Capítulo 1), gates (Capítulo 2) e filemap (Capítulo 3) em um **plano de execução concreto** para a Sprint 7.
>
> O foco é sair de um Inspectah “só terminal” (estado pós-Sprint 6) para um **Inspectah UI Alpha**, capaz de:
> - permitir que um admin gerencie fontes via UI;  
> - permitir que um usuário consulte os dados e veja uma verdade consolidada explicável;  
> - garantir rastreabilidade até a evidência bruta;  
> - rodar uma demo completa (admin + usuário) sem terminal.

---

## 0. Pré-condições da Sprint 7

### 0.1. Estado do repositório

- O repositório local (`Inspectah/`) está limpo (`git status` sem alterações pendentes relevantes).  
- A Sprint 6 está consolidada e validada:
  - diretórios e arquivos da S6 existem conforme o filemap da sprint anterior;  
  - `inspectah/sprint6/` está íntegro;  
  - gates `S6-G0…S6-G8` em **PASS/GO**.

### 0.2. Ambiente local mínimo

- Python configurado com `.venv` funcional.  
- Dependências já instaladas para o runtime da S6.  
- Capítulos 1, 2 e 3 da Sprint 7 presentes em `docs/sprint_7/`.

### 0.3. Respeito à base da Sprint 6

- O módulo `inspectah/sprint6/` e os artefatos consolidados da S6 são tratados como **baseline estável**.  
- A Sprint 7 se apoia nesta base, usando o runtime existente via `runtime_bridge` e sem duplicar lógica de domínio.

### 0.4. Convenção de comandos

Quando este capítulo listar blocos de comandos, assume-se:

```bash
cd /Users/gustavoschneiter/Documents/Inspectah
source .venv/bin/activate 2>/dev/null || true
```

Esse bloco inicial é considerado implícito antes de qualquer sequência de comandos.

---

## 1. Fases macro da execução

A Sprint 7 é executada em **fases**, onde cada fase aproxima o sistema de um conjunto de gates e métricas.

| Fase | Objetivo macro                                         | Gates alvo principais        | Métricas M1–M6 mais impactadas |
|------|--------------------------------------------------------|------------------------------|---------------------------------|
| F0   | Reforçar baseline S6 e dossiê S7                      | S7-G0                        | —                               |
| F1   | Levantar o esqueleto da UI + health básico            | S7-G1                        | M1                              |
| F2   | Implementar administração de fontes via UI            | S7-G2                        | M3                              |
| F3   | Expor modelo canônico + preview pela UI               | S7-G3                        | M3, M4                          |
| F4   | Implementar consulta + decisão consolidada + explicação | S7-G4                      | M4, M5                          |
| F5   | Garantir rastreabilidade de evidência via UI          | S7-G5                        | M6                              |
| F6   | Fechar fluxos UI-only (admin + usuário)               | S7-G6                        | M1, M2                          |
| F7   | Consolidar métricas M1–M6 + demo cronometrada         | S7-G7                        | M1–M6                           |
| F8   | Agregar tudo e decidir GO/NO-GO para a Sprint 7       | S7-G8                        | —                               |

As definições formais de M1–M6 permanecem no Capítulo 1; aqui definimos **como** cada métrica é medida em termos de artefatos e comandos.

---

## 2. Fase F0 — Baseline S6 + dossiê da S7 (S7-G0)

### 2.1. Objetivo

Confirmar que a Sprint 7 começa sobre uma base **saudável** da S6 e que os documentos principais da S7 estão presentes.

### 2.2. Passos principais

1. Validar presença dos docs da S7:
   - `docs/sprint_7/sprint_7_capitulo_1.md`  
   - `docs/sprint_7/sprint_7_capitulo_2.md`  
   - `docs/sprint_7/sprint_7_capitulo_3.md`  
   - `docs/sprint_7/sprint_7_capitulo_4.md` (este)  
   - `docs/sprint_7/sprint_7_resultados.md` (pode iniciar vazio ou como stub).

2. Rodar a suíte de gates da Sprint 6:

```bash
bin/s6_g0_domain_setup.sh
bin/s6_g1_sources_registry.sh
bin/s6_g2_field_designer.sh
bin/s6_g3_collect_evidence.sh
bin/s6_g4_explore_verify.sh
bin/s6_g5_metrics_obs.sh
bin/s6_g6_bundle_repro.sh
bin/s6_g7_guard_automation.sh
bin/s6_g8_sprint_go_no_go.sh
```

3. Implementar/ajustar `bin/s7_g0_baseline.sh` para:
   - chamar os scripts acima (ou verificar seus scorecards S6_G*);  
   - checar que `S6-G8` está em GO;  
   - checar a presença dos docs da S7;  
   - escrever `out/scorecards/S7_G0_baseline.json` e `out/evidence/S7_G0_baseline/summary.json`.

### 2.3. Checklist F0 (Definition of Ready para S7)

- `docs/sprint_7/sprint_7_capitulo_1.md…4.md` existem.  
- `bin/s6_g0_…s6_g8_*.sh` rodam em PASS.  
- `bin/s7_g0_baseline.sh` existe e roda em PASS.

### 2.4. Métricas

- M1–M6 **ainda não são medidas** aqui; F0 é apenas gate estrutural.

---

## 3. Fase F1 — Esqueleto da UI + health (S7-G1)

### 3.1. Objetivo

Levantar a aplicação web básica do Inspectah para a Sprint 7, com:

- entrypoint web funcional (`inspectah/ui/app.py`);  
- leitura de `config/ui_sprint_7.yaml`;  
- endpoint de health respondendo com estado OK e metadados básicos.

### 3.2. Implementação base da UI

1. Criar estrutura da UI:

```bash
mkdir -p inspectah/ui/views inspectah/ui/templates inspectah/ui/static/css inspectah/ui/static/js
: > inspectah/ui/__init__.py
: > inspectah/ui/app.py
: > inspectah/ui/config.py
: > inspectah/ui/runtime_bridge.py
: > inspectah/ui/schemas.py
: > inspectah/ui/view_models.py
```

2. Criar `config/ui_sprint_7.yaml` com parâmetros mínimos (host, port, debug e identificação de versão).  
3. Implementar `inspectah/ui/config.py` para ler `ui_sprint_7.yaml` e expor `get_settings()`.  
4. Implementar `inspectah/ui/app.py` com:
   - criação da app (FastAPI/Flask ou equivalente);  
   - rota `GET /health` retornando JSON com `status`, `version`, `runtime_s6_available`.

5. Criar script para subir a UI:

```bash
: > bin/s7_ui_start.sh
chmod +x bin/s7_ui_start.sh
```

O script deve ler `ui_sprint_7.yaml` (porta/host) e subir a app (por exemplo, `uvicorn inspectah.ui.app:app`).

6. Opcionalmente criar:

```bash
: > bin/s7_ui_stop.sh
: > bin/s7_ui_open_browser.sh
chmod +x bin/s7_ui_stop.sh bin/s7_ui_open_browser.sh
```

### 3.3. Gate S7-G1

- Implementar `bin/s7_g1_ui_boot_health.sh` para:
  - subir a UI;  
  - chamar `GET /health`;  
  - medir tempo de resposta/boot;  
  - escrever `out/scorecards/S7_G1_ui_boot_health.json` e evidência em `out/evidence/S7_G1_ui_boot_health/`.

Exemplo de sequência dev:

```bash
bin/s7_ui_start.sh
curl -s http://localhost:8000/health
bin/s7_g1_ui_boot_health.sh
```

### 3.4. Métrica M1 (como medir)

- M1 (tempo para colocar a UI em estado utilizável) é medido por:
  - timestamp de início (no script `s7_g1_ui_boot_health.sh`);  
  - timestamp de resposta saudável de `/health`.  
- O valor observado de M1 deve ser gravado em `out/scorecards/S7_G1_ui_boot_health.json` em campo específico (por exemplo, `metrics.m1_boot_seconds`).

### 3.5. Checklist F1

- `inspectah/ui/app.py` e `inspectah/ui/config.py` implementados.  
- `config/ui_sprint_7.yaml` existente e carregável.  
- `bin/s7_ui_start.sh` sobe a UI.  
- `bin/s7_g1_ui_boot_health.sh` roda em PASS e preenche `m1_boot_seconds`.

---

## 4. Fase F2 — Administração de fontes via UI (S7-G2)

### 4.1. Objetivo

Permitir que o admin gerencie fontes (listar, criar, editar, opcionalmente desativar) **exclusivamente pela UI**, com reflexo direto em `config/sources/*.yaml`.

### 4.2. Implementação da camada de fontes

1. Evoluir `inspectah/ui/runtime_bridge.py` para incluir funções de fonte:
   - `list_sources()` → lê `config/sources/*.yaml`;  
   - `update_source(id, data)` → persiste alterações;  
   - opcionalmente `create_source(data)` e `disable_source(id)`.

2. Implementar view `inspectah/ui/views/admin_sources.py` com rotas para:
   - listar fontes;  
   - exibir formulário de edição/criação;  
   - aplicar alterações.

3. Implementar template `inspectah/ui/templates/admin_sources.html` para refletir essas operações.

4. Registrar as rotas de `admin_sources` em `inspectah/ui/app.py`.

### 4.3. Gate S7-G2

- Implementar `bin/s7_g2_ui_sources_admin.sh` para:
  - subir a UI;  
  - chamar os endpoints de admin (via `curl`, cliente HTTP ou test client Python);  
  - aplicar uma alteração de teste em uma fonte;  
  - verificar que a alteração apareceu em `config/sources/*.yaml`;  
  - gravar scorecard e evidência.

Sequência típica:

```bash
bin/s7_ui_start.sh
bin/s7_g2_ui_sources_admin.sh
```

### 4.4. Métrica M3 (como medir)

- M3 (capacidade do admin de gerenciar fontes pela UI) pode ser medida como:
  - quantidade de operações CRUD realizadas sem erro;  
  - opcionalmente tempo para concluir um fluxo de alteração simples.

- `s7_g2_ui_sources_admin.sh` deve registrar em `S7_G2_ui_sources_admin.json` campos como:
  - `metrics.m3_admin_crud_success_rate`;  
  - `metrics.m3_sample_flow_seconds` (se definido no Capítulo 1).

### 4.5. Checklist F2

- `runtime_bridge` lê e persiste fontes com segurança.  
- Tela de admin de fontes funcional.  
- Gate `S7-G2` em PASS, com `m3_*` preenchidos.

---

## 5. Fase F3 — Modelo canônico & preview via UI (S7-G3)

### 5.1. Objetivo

Expor, pela UI, o **modelo canônico** do domínio piloto e um **preview de registros**, alinhados com o que o runtime da S6 produz.

### 5.2. Implementação

1. Estender `inspectah/ui/runtime_bridge.py` para:
   - ler `config/fields/dominio_piloto.yaml`;  
   - invocar o mecanismo de preview da S6 (equivalente a `inspectah_fields_preview`);  
   - consolidar amostras canônicas num formato amigável.

2. Implementar view `inspectah/ui/views/model_fields.py` para exibir:
   - lista de campos (nome, tipo, descrição);  
   - amostras de registros canônicos.

3. Implementar template `inspectah/ui/templates/model_fields.html` com essas informações.

4. Ligar a view `model_fields` à aplicação.

### 5.3. Gate S7-G3

- Implementar `bin/s7_g3_ui_fields_preview.sh` para:
  - comparar a estrutura de campos da UI com o conteúdo de `dominio_piloto.yaml`;  
  - rodar um preview via runtime da S6 e outro via UI, comparando campos-chave;  
  - gerar scorecard `S7_G3_ui_fields_preview.json` e evidências.

### 5.4. Métricas M3 e M4 (como medir)

- M3 (admin entende o modelo) pode ser apoiada por:
  - checagens de consistência entre UI e config `dominio_piloto.yaml`.

- M4 (clareza/confiança no modelo e preview) pode registrar:
  - `metrics.m4_field_schema_match_ratio` (percentual de campos alinhados entre UI e config);  
  - `metrics.m4_preview_sample_coverage` (quantidade de campos preenchidos nas amostras).

Esses campos são gravados pelo script de gate em `S7_G3_ui_fields_preview.json`.

### 5.5. Checklist F3

- Tela de "Modelo e preview" funcional.  
- Gate `S7-G3` em PASS.  
- Campos de M3/M4 registrados no scorecard.

---

## 6. Fase F4 — Consulta & decisão consolidada (S7-G4)

### 6.1. Objetivo

Implementar a tela de consulta que:

- mostra valores por fonte;  
- calcula um valor consolidado (estratégia da S7);  
- apresenta uma explicação clara e legível do cálculo.

### 6.2. Implementação

1. Estender `inspectah/ui/runtime_bridge.py` para consultas:
   - função `run_query(filters)` que aciona o engine da S6 e retorna resultados por fonte.

2. Implementar a função de consolidação da S7 (por exemplo, mediana ou média ponderada) em módulo apropriado (no próprio bridge ou auxiliar), com assinatura clara.

3. Implementar view `inspectah/ui/views/query.py` para:
   - renderizar formulário de filtros;  
   - exibir tabela de resultados por fonte;  
   - exibir valor consolidado;  
   - exibir explicação textual da regra usada (por exemplo, "mediana das três fontes" ou "média ponderada com pesos X/Y/Z").

4. Implementar template `inspectah/ui/templates/query.html` com estes elementos.

### 6.3. Gate S7-G4

- Implementar `bin/s7_g4_ui_query_consolidation.sh` para:
  - rodar um conjunto de consultas de teste (definidas em fixture de evidência);  
  - comparar resultados por fonte UI vs runtime;  
  - comparar o valor consolidado UI vs função de referência chamada diretamente;  
  - validar que a explicação exibida bate com a estratégia definida;  
  - gerar scorecard `S7_G4_ui_query_consolidation.json` e evidência.

### 6.4. Métricas M4 e M5 (como medir)

- M4 (confiança na consulta) pode ser medida por:
  - `metrics.m4_query_consistency_ratio` (percentual de consultas de teste onde UI == runtime em todas as fontes).

- M5 (clareza/explicabilidade da decisão consolidada) pode ser registrada como:
  - `metrics.m5_explanation_present` (boolean em cada teste);  
  - `metrics.m5_explanation_quality_score` (opcional, se houver heurística ou checklist simples).

### 6.5. Checklist F4

- Tela de consulta funcional, com valor consolidado e explicação.  
- Gate `S7-G4` em PASS, com M4/M5 refletidas no scorecard.

---

## 7. Fase F5 — Evidência & rastreabilidade via UI (S7-G5)

### 7.1. Objetivo

Permitir que qualquer registro exibido pela UI seja rastreado até sua evidência bruta em **até 2 cliques**, conforme o objetivo de rastreabilidade da S7.

### 7.2. Implementação

1. Evoluir `inspectah/ui/runtime_bridge.py` para permitir:
   - mapear um registro canônico (ID, fonte, timestamp) para um pacote de evidência em `out/evidence/dominio_piloto/...`.

2. Implementar view `inspectah/ui/views/evidence.py` para:
   - receber um identificador de registro;  
   - localizar a evidência;  
   - exibir metadados principais e links (por exemplo, para o arquivo bruto, se apropriado).

3. Implementar template `inspectah/ui/templates/evidence_detail.html` para mostrar esses dados.

4. Adicionar botões/links "Ver evidência" na tela de consulta (`query.html`).

### 7.3. Gate S7-G5

- Implementar `bin/s7_g5_ui_evidence_trace.sh` para:
  - selecionar alguns registros exibidos na UI (via script ou cenário pré-definido);  
  - seguir o fluxo de links até a tela de evidência;  
  - contar o número de cliques necessários;  
  - verificar a existência física dos arquivos de evidência referenciados;  
  - gerar scorecard `S7_G5_ui_evidence_trace.json` e evidência.

### 7.4. Métrica M6 (como medir)

- M6 (rastreabilidade até evidência) é medida por:
  - `metrics.m6_max_clicks_to_evidence` (máximo de cliques entre os casos de teste);  
  - `metrics.m6_evidence_found_ratio` (percentual de registros com evidência encontrada).

### 7.5. Checklist F5

- Link de evidência presente para cada registro relevante na tela de consulta.  
- Gate `S7-G5` em PASS.  
- `m6_max_clicks_to_evidence <= 2` para os casos medidos.

---

## 8. Fase F6 — Fluxos UI-only (admin e usuário) (S7-G6)

### 8.1. Objetivo

Garantir que as histórias principais definidas no Capítulo 1 (admin e usuário) possam ser executadas **sem uso de terminal**, dentro dos limites de tempo desejados.

### 8.2. Implementação

1. Validar funcionalmente que:
   - o admin consegue, via UI, revisar fontes e modelo;  
   - o usuário consegue, via UI, consultar um valor e ver evidência.

2. Ajustar detalhes de UX que prejudiquem o fluxo (labels, mensagens, navegação, links de retorno).

3. Implementar `bin/s7_g6_ui_only_flows.sh` para orquestrar uma execução guiada:
   - registrar tempos de cada fluxo (admin, usuário);  
   - marcar se houve necessidade de usar terminal (deve ser `false` para PASS);  
   - gravar evidências (`flow_notes.md`, `timings.json`).

### 8.3. Métricas M1 e M2 (como medir)

- M1 (tempo de chegar a uma consulta útil desde "UI desligada") pode ser reavaliada aqui com dados mais próximos de um uso real.
- M2 (tempo para o usuário comum executar uma consulta e ver a resposta consolidada) pode ser medido como:
  - `metrics.m2_user_flow_seconds` em `S7_G6_ui_only_flows.json`.

### 8.4. Checklist F6

- Fluxo admin executável do início ao fim sem terminal.  
- Fluxo usuário executável do início ao fim sem terminal.  
- Gate `S7-G6` em PASS, com M1/M2 dentro dos thresholds do Capítulo 1.

---

## 9. Fase F7 — Métricas M1–M6 & demo cronometrada (S7-G7)

### 9.1. Objetivo

Consolidar as evidências de desempenho e usabilidade da Sprint 7, verificando quantitativamente as métricas **M1–M6** e costurando um roteiro de demo replicável.

### 9.2. Implementação

1. Implementar `bin/s7_g7_metrics_and_demo.sh` para:
   - ler os scorecards `S7_G1…S7_G6`;  
   - extrair valores observados relevantes para cada métrica M1–M6;  
   - opcionalmente rodar uma demo final cronometrada;  
   - comparar com thresholds definidos no Capítulo 1;  
   - gerar `out/scorecards/S7_G7_metrics_and_demo.json` com:
     - `metrics.m1_*…m6_*`;  
     - `flags.m1_pass…m6_pass`.

2. Atualizar `docs/sprint_7/sprint_7_resultados.md` com:
   - tabela final de M1–M6 (valores observados vs thresholds);  
   - roteiro de demo:
     - ligar UI;  
     - mostrar health;  
     - admin de fontes;  
     - modelo/preview;  
     - consulta e consolidação;  
     - evidência;  
     - visão geral de métricas.

### 9.3. Checklist F7

- `S7_G7_metrics_and_demo.json` criado com M1–M6 e flags pass/fail.  
- `docs/sprint_7/sprint_7_resultados.md` atualizado com resultados e roteiro de demo.

---

## 10. Fase F8 — Sprint 7 GO/NO-GO (S7-G8)

### 10.1. Objetivo

Reunir todas as evidências produzidas nas fases F0–F7 e emitir uma decisão final da Sprint 7: **GO** ou **NO-GO**.

### 10.2. Implementação

1. Implementar `bin/s7_g8_sprint_go_no_go.sh` para:
   - ler scorecards `S7_G0…S7_G7`;  
   - verificar que todos têm `status == "PASS"`;  
   - verificar que `flags.m1_pass…flags.m6_pass == true` em `S7_G7_metrics_and_demo.json`;  
   - gerar `out/evidence/S7_G8_sprint_go_no_go/summary.json` com resumo textual;  
   - gerar `out/scorecards/S7_G8_sprint_go_no_go.json` com campos:
     - `decision` (GO/NO_GO);  
     - `all_gates_pass`;  
     - `failed_gates` (lista, se algum);  
     - `all_metrics_pass`;  
     - `notes`.

2. Rodar `bin/s7_g8_sprint_go_no_go.sh` como último passo da sprint.

### 10.3. Critério de GO

- `all_gates_pass == true`;  
- `all_metrics_pass == true`;  
- `decision == "GO"`.

Se qualquer gate S7-G0…S7-G7 estiver em FAIL, ou se alguma métrica M1…M6 estiver reprovada, a decisão deve ser `NO_GO`, com `failed_gates` e `notes` detalhando o motivo.

### 10.4. Checklist F8

- Scorecard `S7_G8_sprint_go_no_go.json` presente e com `decision` definido.  
- Evidência em `out/evidence/S7_G8_sprint_go_no_go/summary.json`.  
- `docs/sprint_7/sprint_7_resultados.md` atualizado com a decisão final e próximo passo recomendado.

---

## 11. Execução recomendada “end-to-end”

Fluxo recomendado, assumindo repo preparado:

```bash
# F0 — Baseline
bin/s7_g0_baseline.sh

# F1 — UI básica
bin/s7_g1_ui_boot_health.sh

# F2 — Admin fontes
bin/s7_g2_ui_sources_admin.sh

# F3 — Modelo + preview
bin/s7_g3_ui_fields_preview.sh

# F4 — Consulta + consolidação
bin/s7_g4_ui_query_consolidation.sh

# F5 — Evidência via UI
bin/s7_g5_ui_evidence_trace.sh

# F6 — Fluxos UI-only
bin/s7_g6_ui_only_flows.sh

# F7 — Métricas + demo
bin/s7_g7_metrics_and_demo.sh

# F8 — GO/NO-GO
bin/s7_g8_sprint_go_no_go.sh
```

Esse bloco resume a sequência de validação da Sprint 7; cada script pressupõe que a fase anterior foi implementada e está em PASS.

---

## 12. Riscos, contenção e rollback

### 12.1. Riscos principais

1. **UI quebrada afetando experiência, mas não o runtime S6**  
   - A UI é uma casca em cima da S6. Se quebrou, o runtime de coleta/evidência continua íntegro.

2. **Divergência entre UI e runtime S6**  
   - Risco de UI exibir resultados ou consolidações que não batem 100% com a S6.

3. **Evidência inacessível via UI**  
   - Risco de links de evidência levarem a destinos inexistentes, apesar de os pacotes existirem em disco.

### 12.2. Estratégias de contenção

- Em caso de problema grave de UI durante desenvolvimento ou demo:
  - parar a UI (`s7_ui_stop.sh` ou matar o processo);  
  - usar os scripts de S6 (`inspectah_collect_once`, `inspectah_query`, etc.) para manter a capacidade de coleta/consulta por terminal.

- Em caso de divergência UI vs runtime S6:
  - rodar `bin/s7_g4_ui_query_consolidation.sh` focando nos casos que falharam;  
  - ajustar, se necessário, apenas o `runtime_bridge` ou a função de consolidação;  
  - garantir que `inspectah/sprint6/` não seja alterado sem revisão de uma sprint futura.

### 12.3. Rollback lógico da S7

Em caso de NO_GO ou problema grave que exija rollback:

1. Não tocar na S6: manter `inspectah/sprint6/` e seus artefatos intactos.  
2. Isolar a UI:
   - se necessário, desligar a UI em produção;  
   - travar o uso de scripts S7 até correção (por convenção de operação).

3. Se houver versionamento remoto (GitHub):
   - marcar a release da S6 como baseline estável;  
   - tratar as mudanças da S7 em branches específicas até nova tentativa de GO.

---

## 13. Definition of Done da Sprint 7

A Sprint 7 só é considerada **entregue** quando todos os itens abaixo forem verdadeiros:

1. **Docs**
   - `docs/sprint_7/sprint_7_capitulo_1.md` locked e refletindo o que foi implementado;  
   - `docs/sprint_7/sprint_7_capitulo_2.md` alinhado aos scripts reais;  
   - `docs/sprint_7/sprint_7_capitulo_3.md` respeitado pelo repositório;  
   - `docs/sprint_7/sprint_7_capitulo_4.md` (este) atualizado com a execução real;  
   - `docs/sprint_7/sprint_7_resultados.md` descrevendo a entrega, demo e decisão final.

2. **UI + runtime**
   - `inspectah/ui/` implementado conforme filemap;  
   - UI sobe com `bin/s7_ui_start.sh`;  
   - health responde;  
   - fluxos de admin e usuário funcionam de ponta a ponta.

3. **Gates**
   - `S7-G0…S7-G7` com `status == "PASS"`;  
   - scorecards `out/scorecards/S7_G*.json` presentes;  
   - evidências correspondentes em `out/evidence/S7_G*/`.

4. **Métricas M1–M6**
   - `flags.m1_pass…m6_pass == true` em `out/scorecards/S7_G7_metrics_and_demo.json`;  
   - valores observados documentados em `docs/sprint_7/sprint_7_resultados.md`.

5. **Decisão final**
   - `out/scorecards/S7_G8_sprint_go_no_go.json` com `decision == "GO"`;  
   - resumo da decisão e próximos passos em `out/evidence/S7_G8_sprint_go_no_go/summary.json` e em `docs/sprint_7/sprint_7_resultados.md`.

Quando todos esses pontos forem verdadeiros, o Inspectah passa a contar com um **Inspectah UI Alpha** sólido, validado por gates rígidos e pronto para demos reais do domínio piloto, sem depender de terminal para as operações principais de admin e usuário.

