# Sprint 14 – Capítulo 2
Gates de validação do loop de contestação v0

---

## 0. TL;DR

Na Sprint 14 o Inspectah ganha um **loop de contestação v0** em cima do backbone S12/S13 (ingestão contínua, casos/timeline, Debunker v0, Explorer e feedback). Este capítulo define **como provar que esse loop funciona**, sem antecipar:

- sistema de blocos completo;
- reputação avançada;
- blockchain automática;
- comunidade/incentivos sofisticados.

A S14 introduz os gates abaixo, todos com scorecards e evidências em `out/scorecards/` e `out/evidence/`:

| Gate    | Nome curto                                    | Pergunta central                                                       | Tipo   |
|---------|-----------------------------------------------|-------------------------------------------------------------------------|--------|
| S14_G0  | Pré-flight de ambiente                        | Estou rodando a S14 em cima de um S12/S13 saudáveis e specs completas? | Hard   |
| S14_G1  | Backlog de contestação                        | O backlog que vou usar na S14 é íntegro, coerente e multi-domínio?     | Soft   |
| S14_G2  | Modelo de contestação v0                      | O modelo/estados de contestação fazem sentido e respeitam o escopo?    | Hard   |
| S14_G3  | Loop feedback → contestação → correção        | O ciclo completo funciona, com estados finais e antes/depois claros?   | Hard   |
| S14_G4  | Painel de contestação + Explorer (E2E)        | Um humano consegue operar contestação e ver o efeito no Explorer?      | Hard   |
| S14_G5  | Impacto na verdade atual e regressão vs S12/13| A S14 melhora a verdade sem quebrar nada que S12/S13 garantiam?        | Hard   |
| S14_G6  | Observabilidade da contestação                | Estou medindo bem a saúde do sistema de contestação v0?                | Soft   |
| S14_G7  | Consolidação S14                              | Tudo que a S14 promete está implementado e consistente?                | Hard   |
| S14_G8  | Decisão GO/NO_GO                             | Com base nos scorecards G0…G7, a S14 está apta a virar estado oficial? | —      |

Regras de decisão no S14_G8 (resumo):

- Qualquer **gate hard** em FAIL ou ausente ⇒ **NO_GO**.
- Gates soft podem ficar em WARN/FAIL, mas isso precisa ser registrado explicitamente como risco.
- `global_health` da contestação (G6) só pode ser "OK" ou "WARN"; "CRITICAL" derruba a S14.

---

## 1. Regras gerais dos gates da S14

Antes de detalhar gate a gate, todo o desenho da S14 segue estes princípios:

1. **Compatibilidade estrita com S12/S13**  
   - S12_G8 e S13_G8 precisam estar em GO (scorecards presentes e saudáveis).  
   - A S14 não pode quebrar pipelines/gates já existentes; qualquer regressão derruba o GO.

2. **Sem antecipar features da Fase 2**  
   - Proibido implementar (nesta sprint): modelo completo de blocos, reputação, blockchain, incentivos econômicos.  
   - É permitido preparar o terreno (nomes, campos, invariantes), mas não construir o sistema inteiro.

3. **Determinismo e reprodutibilidade**  
   - Todos os gates devem ser reexecutáveis via CLI, sem dependência de rede, usando fixtures e snapshots produzidos em S12/S13/S14.  
   - Cada gate gera **um único scorecard JSON oficial** e **uma pasta de evidências** com artefatos mínimos para auditoria.

4. **Naming e layout alinhados ao DNA**  
   - Scripts em `bin/`: `bin/s14_gX_*.sh` + `bin/s14_gates_all.sh` + `bin/s14_g8_decision.sh`.  
   - Lógica em `scripts/`: módulos `scripts/s14_*.py`.  
   - Scorecards em `out/scorecards/S14_GX_*.json`.  
   - Evidências em `out/evidence/S14_GX/`.

5. **Contrato com Capítulos 3 e 4**  
   - Capítulo 3 deve mapear cada gate para scripts/arquivos concretos.  
   - Capítulo 4 deve explicar exatamente como rodar os gates localmente e no CI (incluindo `_s14-gates.yml`).

---

## 2. Gates da S14 em detalhe

### 2.1 S14_G0 – Pré-flight de ambiente e pré-requisitos

**Pergunta que responde**  
Estou rodando a S14 em um ambiente consistente com o estado final da S12/S13 e com as specs completas da S14?

**Escopo**

- Validar repositório/branch/remote:
  - diretório raiz = `/Users/gustavoschneiter/Documents/Inspectah` (ou equivalente, descoberto via `git rev-parse`).
  - branch atual = `main` (ou `s14_*` quando a branch da sprint existir).  
  - `origin` apontando para `gustavomhss/Inspectah`.
- Verificar saúde das sprints anteriores relevantes:
  - `out/scorecards/S12_G8_decision.json` com `decision = "GO"`.
  - `out/scorecards/S13_G8_decision.json` com `decision = "GO"`.
- Verificar presença dos artefatos mínimos da S14:
  - `Sprint 14/Capitulo 1.md`…`Capitulo 4.md`.  
  - backlog seed vindo da S13, por exemplo `out/evidence/S13_G6/backlog_s14_seed.json` (ou caminho documentado no Cap.3).  
  - configurações e snapshots da S13 usados como base (ex.: `config/s13_pilotos.yml`, snapshots de cases/timelines multi-domínio).
- Gerar **snapshot de ambiente**: branch, HEAD, tags relevantes (ex.: `v0.4-s13`), timestamps dos scorecards S12/S13, etc.

**Entradas principais**

- Git (estado do repo/branch/remote).  
- Scorecards S12_G8 e S13_G8.  
- Arquivos de spec/capítulos S14.  
- Backlog seed e configs herdadas da S13.

**SLIs**

- `preflight_env_ok` ∈ {true,false}.  
- `s12_state_ok` ∈ {true,false}.  
- `s13_state_ok` ∈ {true,false}.  
- `s14_specs_present_ratio` ∈ [0,1].

**SLOs**

- `preflight_env_ok = true`.  
- `s12_state_ok = true` e `s13_state_ok = true`.  
- `s14_specs_present_ratio = 1.0`.

**Artefatos / saídas**

- Scorecard: `out/scorecards/S14_G0_env_repo.json`.  
- Evidência: `out/evidence/S14_G0/env_snapshot.json` (incluindo ponteiros para S12/S13).

**Tipo de gate**  
Hard – falha ⇒ S14_G8 = NO_GO.

---

### 2.2 S14_G1 – Integridade do backlog de contestação

**Pergunta que responde**  
O backlog que a S14 vai usar para testar contestação v0 é íntegro, coerente com os pilotos multi-domínio da S13 e suficientemente rico para um piloto sério?

**Escopo**

- Ler backlog seed de contestação (por exemplo `out/evidence/S13_G6/backlog_s14_seed.json`) e eventuais extensões da S14.  
- Validar que **cada entrada** contém:
  - `case_id` ou `event_id` válido nos snapshots da S13.  
  - `domain` em {`obra_publica`, `evento_climatico`, `projeto_lei`, `carreira_politica`, `influencer`, `atleta`}.  
  - `motivo_contestacao` (texto) e `tipo_problema` (classificação simples: ex. `dado_errado`, `desatualizado`, `interpretacao`, `outro`).
- Detectar problemas:
  - IDs inexistentes.  
  - domínios inválidos.  
  - campos obrigatórios vazios.  
  - duplicatas (mesmo case/event + mesmo tipo de problema).
- Gerar backlog normalizado para uso nos gates seguintes (por exemplo `out/evidence/S14_G1/backlog_resolved.json`).

**Entradas principais**

- Backlog seed da S13.  
- Snapshots de casos/timelines da S13.  
- Eventuais complementos S14.

**SLIs**

- `backlog_entries_total` (número total de entradas).  
- `backlog_integrity_ratio` = fração de entradas com IDs válidos, domínio permitido e campos obrigatórios preenchidos.  
- `backlog_domain_coverage` = fração de domínios que aparecem com pelo menos 1 contestação.

**SLOs**

- `backlog_entries_total ≥ N_minimo` (definido no Cap.3, recomendação: ≥ 12).  
- `backlog_integrity_ratio ≥ 0.98`.  
- `backlog_domain_coverage = 1.0`.

**Artefatos / saídas**

- Scorecard: `out/scorecards/S14_G1_backlog_seed.json`.  
- Evidências:  
  - `out/evidence/S14_G1/backlog_resolved.json`.  
  - `out/evidence/S14_G1/backlog_issues.json` (opcional, lista de problemas detectados).

**Tipo de gate**  
Soft – WARN/FAIL não derruba automaticamente, mas pesa na decisão S14_G8.

---

### 2.3 S14_G2 – Modelo de contestação v0 (estados, referências, invariantes)

**Pergunta que responde**  
O modelo de contestação v0 está bem definido, coerente com a visão da S14 e compatível com o backbone S12/S13, sem inventar o Sistema de Blocos completo antes da hora?

**Escopo**

- Validar o módulo de modelo de contestação (ex.: `scripts/s14_contest_model.py`):
  - Estrutura mínima de `Contestacao` com campos como:  
    - `contestation_id`, `case_id`/`event_id`, `domain`, `source`, `motivo`, `tipo_problema`, `estado`, timestamps, etc.  
  - Conjunto de **estados** alinhado ao Cap.1, por exemplo:  
    - `open`, `in_triage`, `in_analysis`, `resolved_procedent`, `resolved_improcedent`, `archived`.  
  - Máquina de estados explícita: quais transições são permitidas e quais são proibidas.  
  - Ligação obrigatória com cases/eventos da S13.
- Rodar checagens automatizadas de invariantes, por exemplo:
  - nenhuma contestação `resolved_*` sem campo de decisão preenchido;  
  - nenhuma contestação sem vínculo a case/event;  
  - nenhuma contestação em estado desconhecido.
- Assegurar que o modelo NÃO implementa:
  - blocos/sub-blocos/claims/disputas completas;  
  - reputação pesada;  
  - blockchain on-chain.

**Entradas principais**

- Código do modelo de contestação S14.  
- Snapshots de cases/eventos S13 usados para validar referências.

**SLIs**

- `model_schema_integrity_ratio` = fração de campos esperados presentes e com tipos coerentes.  
- `state_machine_valid_ratio` = fração de transições observadas que respeitam a máquina de estados definida.  
- `reference_integrity_ratio` = fração de contestações que apontam para cases/eventos válidos.  
- `out_of_scope_features_detected` ∈ {true,false}.

**SLOs**

- `model_schema_integrity_ratio = 1.0`.  
- `state_machine_valid_ratio = 1.0`.  
- `reference_integrity_ratio ≥ 0.99`.  
- `out_of_scope_features_detected = false`.

**Artefatos / saídas**

- Scorecard: `out/scorecards/S14_G2_contest_model.json`.  
- Evidências em `out/evidence/S14_G2/` (exemplos de contestações válidas, relatório de transições, violação de invariantes se houver).

**Tipo de gate**  
Hard – qualquer violação relevante ⇒ NO_GO.

---

### 2.4 S14_G3 – Loop feedback → contestação → correção

**Pergunta que responde**  
O ciclo completo feedback → contestação → análise → correção na verdade atual funciona de ponta a ponta, sem atalhos estranhos nem estados zumbis?

**Escopo**

- Pegar um subconjunto representativo (ou todo) do backlog normalizado de S14_G1.  
- Para cada item, executar o fluxo completo:
  1. Gerar/associar feedback da S12/S13 à contestação (quando aplicável).  
  2. Criar/atualizar a entidade `Contestacao` com estado inicial `open`.  
  3. Passar por triagem (`in_triage`) e análise (`in_analysis`).  
  4. Decidir (`resolved_procedent`/`resolved_improcedent`).  
  5. Aplicar correção na verdade atual quando procedente (atualizar snapshot de case/timeline, narrativa ou equivalente).  
  6. Garantir rastro de antes/depois.
- Validar invariantes:
  - nenhuma contestação fica presa em estado intermediário após o run;  
  - contestations procedentes têm evidência de antes/depois;  
  - casos/imagens não relacionados não são alterados sem motivo.

**Entradas principais**

- Backlog normalizado (S14_G1).  
- Modelo de contestação (S14_G2).  
- Serviços de cases/timeline/Explorer da S12/S13.

**SLIs**

- `loop_completion_ratio` = fração de contestations do sample que terminam em estado terminal.  
- `state_leak_ratio` = fração que termina em estado inválido ou não-terminal.  
- `before_after_evidence_ratio` = fração de contestations procedentes com evidência clara de antes/depois.  
- `correction_applied_ratio` = fração de contestations procedentes que geram mudança observável na verdade atual.

**SLOs**

- `loop_completion_ratio = 1.0`.  
- `state_leak_ratio = 0.0`.  
- `before_after_evidence_ratio ≥ 0.95`.  
- `correction_applied_ratio` – recomendado PASS ≥ 0.80, WARN ≥ 0.60 (limiares finais definidos no Cap.3).

**Artefatos / saídas**

- Scorecard: `out/scorecards/S14_G3_loop_contestacao.json`.  
- Evidências em `out/evidence/S14_G3/` (log estruturado das transições, lista de correções, diffs de antes/depois).

**Tipo de gate**  
Hard – sem loop confiável não há S14.

---

### 2.5 S14_G4 – Painel de contestação + Explorer (fluxos E2E)

**Pergunta que responde**  
Um operador humano consegue usar o painel de contestação para trabalhar o backlog e ver, no Explorer, o efeito das decisões?

**Escopo**

- Definir e rodar cenários E2E de UI (documentados em um arquivo tipo `docs/sprint_14_cenarios_painel_contestacao.md`):
  - listar contestations filtrando por domínio/status;  
  - abrir uma contestação;  
  - ver contexto completo (case/timeline, motivo, histórico);  
  - aplicar decisão;  
  - voltar ao Explorer e verificar se a verdade exibida está alinhada com a decisão.
- Usar snapshots determinísticos e serviços locais (sem rede) para reproduzir sempre os mesmos cenários.  
- Registrar resultado de cada cenário (sucesso/falha, mensagens de erro, rotas quebradas).

**Entradas principais**

- Serviços de backend de painel/Explorer.  
- Snapshots S13 + alterações S14 (casos/timelines/narrativas).  
- Documento de cenários de UI da S14.

**SLIs**

- `panel_e2e_success_rate` = fração de cenários E2E executados com sucesso.  
- `panel_to_explorer_consistency_ratio` = fração de cenários em que a visão do Explorer reflete corretamente a decisão do painel.  
- `broken_link_ratio` = fração de ações que resultam em erro (404/500 ou tela vazia inesperada).

**SLOs**

- `panel_e2e_success_rate ≥ 0.95`.  
- `panel_to_explorer_consistency_ratio ≥ 0.98`.  
- `broken_link_ratio = 0.0`.

**Artefatos / saídas**

- Scorecard: `out/scorecards/S14_G4_panel_explorer_e2e.json`.  
- Evidências em `out/evidence/S14_G4/` (logs de cenários, dumps das respostas relevantes, eventuais falhas).

**Tipo de gate**  
Hard – se o humano não consegue operar contestação, o feature não existe de verdade.

---

### 2.6 S14_G5 – Impacto na verdade atual e regressão vs S12/S13

**Pergunta que responde**  
As correções da S14 estão tornando a verdade exibida pelo Inspectah melhor, sem destruir nada que S12/S13 já garantiam?

**Escopo**

- Reexecutar um conjunto de cenários da S13 (Explorer multi-domínio) em dois momentos:
  - antes da aplicação das contestations da S14;  
  - depois da aplicação das contestations.
- Medir:
  - se campos/narrativas alvo de contestation foram atualizados quando procedentes;  
  - se cenários não contestados se mantêm estáveis;  
  - se algum cenário S13 PASS → FAIL (regressão) por culpa da S14.
- Gerar relatório de impacto (casos melhoraram, pioraram, ficaram iguais).

**Entradas principais**

- Cenários da S13 (especialmente os que envolvem os 6 domínios).  
- Implementação do loop de contestação S14.  
- Snapshots pré e pós-correção.

**SLIs**

- `truth_impact_coverage` = fração de contestations procedentes que produzem mudança observável na verdade atual.  
- `s13_regression_ratio` = fração de cenários da S13 que passaram de PASS → FAIL depois da S14.  
- `unexpected_change_ratio` = fração de cenários não contestados que mudaram sem explicação.

**SLOs**

- `truth_impact_coverage ≥ 0.80` (recomendado; limiares finais definidos no Cap.3).  
- `s13_regression_ratio = 0.0`.  
- `unexpected_change_ratio = 0.0`.

**Artefatos / saídas**

- Scorecard: `out/scorecards/S14_G5_truth_impact.json`.  
- Evidências em `out/evidence/S14_G5/` (relatório de impacto, listas de cenários melhoraram/pioraram, comparativos pré/pós).

**Tipo de gate**  
Hard – se a S14 piorar a verdade atual ou quebrar S13, a decisão deve ser NO_GO.

---

### 2.7 S14_G6 – Observabilidade e métricas da contestação

**Pergunta que responde**  
Estamos medindo de forma minimamente decente a saúde do sistema de contestação v0?

**Escopo**

- Consolidar métricas da contestação em um snapshot único (ex.: `scripts/s14_metrics_snapshot.py`):
  - volume de contestations por domínio;  
  - distribuição de estados (open, in_triage, etc.);  
  - taxa de contestations procedentes vs improcedentes;  
  - métricas derivadas dos gates anteriores (loop_completion, truth_impact_coverage, etc.);  
  - tamanho do backlog residual (contestations não resolvidas ao final da S14).
- Classificar a saúde global em `global_health` ∈ {"OK", "WARN", "CRITICAL"}.  
- Gerar um documento textual de riscos/débitos principais.

**Entradas principais**

- Scorecards S14_G0…S14_G5.  
- Dados de contestation runtime gerados nos gates.

**SLIs**

- `metrics_completeness_ratio` = fração de métricas esperadas presentes no snapshot.  
- `open_backlog_ratio` = contestations não resolvidas / total.  
- `global_health` ∈ {"OK","WARN","CRITICAL"}.

**SLOs**

- `metrics_completeness_ratio ≥ 0.95`.  
- `open_backlog_ratio ≤ 0.20` no snapshot final da S14.  
- `global_health` ∈ {"OK","WARN"}; `CRITICAL` é inaceitável.

**Artefatos / saídas**

- Scorecard: `out/scorecards/S14_G6_observabilidade.json`.  
- Evidências em `out/evidence/S14_G6/metrics_snapshot.json` e `out/evidence/S14_G6/risks_and_debts.md`.

**Tipo de gate**  
Soft – WARN aceita; CRITICAL deve pesar fortemente para NO_GO.

---

### 2.8 S14_G7 – Consolidação final da S14

**Pergunta que responde**  
Tudo que a S14 prometeu (no Cap.1) foi de fato implementado, com scorecards e evidências alinhados aos gates deste Cap.2?

**Escopo**

- Verificar presença de todos os scorecards S14_G0…S14_G6.  
- Validar alinhamento docs ↔ implementação:
  - cada gate descrito neste Cap.2 possui scripts correspondentes no Cap.3;  
  - nomes de arquivos citados existem;  
  - SLIs/SLOs aqui definidos aparecem nos scorecards (mesmo nome ou mapeamento claro);  
  - não há código implementando Sistema de Blocos completo, reputação avançada ou blockchain.
- Produzir um resumo final da S14:
  - o que a S14 colocou de pé;  
  - limitações conhecidas;  
  - recomendações explícitas para próximas sprints (S15/S16).

**Entradas principais**

- Capítulos 1–4 da S14.  
- Scorecards S14_G0…S14_G6.  
- Scripts e docs citados nesses capítulos.

**SLIs**

- `scorecards_presence_ratio` = scorecards encontrados / scorecards esperados (G0…G6).  
- `docs_impl_alignment_ratio` = fração de itens deste Cap.2 que aparecem na implementação.  
- `out_of_scope_violation_ratio` = fração de trechos de código que antecipam features de Fase 2.

**SLOs**

- `scorecards_presence_ratio = 1.0`.  
- `docs_impl_alignment_ratio ≥ 0.95`.  
- `out_of_scope_violation_ratio = 0.0`.

**Artefatos / saídas**

- Scorecard: `out/scorecards/S14_G7_consolidation.json`.  
- Evidência: `out/evidence/S14_G7/summary.md` (wrap humano da S14).

**Tipo de gate**  
Hard – sem consolidação coerente não há GO.

---

### 2.9 S14_G8 – Decisão GO/NO_GO

**Pergunta que responde**  
Com base nos scorecards S14_G0…S14_G7, o piloto de contestação v0 está em condições de ser considerado estado oficial da S14?

**Escopo**

- Ler todos os scorecards S14_G0…S14_G7.  
- Aplicar regras de decisão:
  - Gates **hard** (G0, G2, G3, G4, G5, G7):  
    - qualquer `status = "FAIL"` ou scorecard ausente ⇒ `decision = "NO_GO"`.  
  - Gates **soft** (G1, G6):  
    - `FAIL` não derruba automaticamente, mas deve gerar `reasons` e pelo menos WARN na decisão.  
  - `global_health` (G6):  
    - `CRITICAL` ⇒ `decision = "NO_GO"`.
- Construir payload de decisão com:  
  - `decision` ∈ {"GO","NO_GO","WARN_GO"};  
  - estado de cada gate;  
  - principais métricas agregadas;  
  - `reasons` (lista de riscos/débitos relevantes).

**Política de decisão (resumo)**

- **GO**
  - todos os gates hard = PASS;  
  - gates soft ∈ {PASS, WARN};  
  - `global_health` ∈ {"OK","WARN"}.

- **WARN_GO** (opcional, se optarmos por usar esta categoria)
  - todos os gates hard = PASS;  
  - pelo menos um gate soft em FAIL;  
  - riscos documentados e aceitos explicitamente para uso restrito.

- **NO_GO**
  - qualquer gate hard em FAIL ou ausente;  
  - ou `global_health = "CRITICAL"`.

**Artefatos / saídas**

- Scorecard: `out/scorecards/S14_G8_decision.json`.  
- Evidências: `out/evidence/S14_G8/summary.md` (wrap humano com como rodar, resumo dos gates, decisão final e próximos passos).

---

## 3. Como este capítulo conversa com os demais

- **Capítulo 1 (visão)** define o que é contestação v0 em linguagem de produto: quando deveria ser usada, que problema resolve, o que fica fora de escopo (blocos, reputação, chain).
- **Capítulo 2 (este)** transforma a visão em **contrato mensurável**: uma lista de perguntas que o sistema deve conseguir responder com scorecards/evidências.
- **Capítulo 3** deve desenhar a arquitetura, filemap e naming de scripts para que implementar esses gates seja quase mecânico (sem improviso de última hora).
- **Capítulo 4** deve se apoiar diretamente neste capítulo para montar o runbook de execução local/CI (como rodar S14_G0…S14_G8, como interpretar scorecards, como colher evidências para ORR).

Se Capítulos 3 e 4 obedecerem este Capítulo 2, e todos os gates S14_G0…S14_G7 ficarem verdes com decisão GO/WARN_GO em S14_G8, a S14 entrega um **loop de contestação v0 confiável**, pronto para ser usado como base concreta do futuro Sistema de Blocos e da camada de reputação avançada na Fase 2.

