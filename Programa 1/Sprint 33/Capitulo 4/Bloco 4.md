# Sprint 33 — Capítulo 4

## Bloco 4 — Evidências, riscos e checklist final de encerramento da S33

Este bloco fecha o Capítulo 4 amarrando três coisas que decidem se a S33 está realmente entregue ou só "bonita no papel":

1. **como as evidências devem ser coletadas e organizadas;**
2. **quais são os riscos principais da sprint e como mitigá‑los;**
3. **qual é o checklist objetivo de encerramento**, que precisa estar em PASS antes de alguém escrever "S33 DONE" em qualquer lugar.

A premissa é simples: **sem evidência, não há DONE**. Sem olhar para riscos, não há operação confiável. Sem checklist, não há alinhamento.

---

### 4.4.1 Estratégia de evidência na S33

A S33 trata evidência como parte do produto, não como subproduto.

#### Princípios gerais

1. **Cada gate deixa pegada.**  
   Sempre que um gate G0–G5 é executado, algum artefato aparece em `out/evidence/S33_G*/` e no scorecard correspondente em `out/scorecards/`.

2. **Incidentes geram bundles, não só memórias.**  
   Qualquer incidente usado em simulação ou estudo de caso relevante para a S33 gera um bundle completo em `out/evidence/S33_G4_incidents/`.

3. **ORR é evento com ata, não só reunião.**  
   A sessão de ORR operacional (G5) deixa um rastro tangível: roteiro preenchido, prints, feedbacks e um scorecard claro.

4. **Evidência é consultável.**  
   Caminhos de evidência são previsíveis, com nomeação consistente, para que alguém consiga revisitar a S33 meses depois sem arqueologia.

---

### 4.4.2 Estrutura de diretórios de evidência e scorecards

A estrutura mínima planejada para a Sprint 33 é:

```text
out/
  scorecards/
    S33_G0_scope_and_baseline.json
    S33_G1_incidents_domain.json
    S33_G2_cockpit_ui.json
    S33_G3_slos_and_observability.json
    S33_G4_runbooks_and_evidence.json
    S33_G5_orr_operacional.json

  evidence/
    S33_G0_scope_and_baseline/
      g0_log.txt
      g0_components_map_check.json
      g0_scope_snapshot.md

    S33_G1_incidents_domain/
      pytest_domain_incidents.log
      incidents_model_schema_dump.json
      sample_lifecycle_traces.md

    S33_G2_cockpit_ui/
      api_overview_responses.json
      api_components_responses.json
      cockpit_overview_screenshots/

    S33_G3_slos_and_observability/
      slo_queries_results.json
      slo_alerts_test_log.txt
      dashboards_screenshots/

    S33_G4_incidents/
      incident_001_bundle/
        incident_timeline.md
        cockpit_screenshots/
        logs_extract.txt
        slo_context.json
        runbook_used.md

    S33_G5_orr_operacional/
      orr_script_filled.md
      orr_notes.md
      orr_cockpit_screenshots/
      orr_feedback_operator.md
```

Cada diretório pode conter outros arquivos, mas essa estrutura é o mínimo esperado para considerar a S33 auditável.

---

### 4.4.3 O que cada scorecard precisa contar

Os scorecards `S33_G*_*.json` não são apenas flags PASS/FAIL; eles codificam o estado do gate de forma estruturada.

#### S33_G0_scope_and_baseline.json

Campos esperados (exemplo):
- `gate`: "G0_scope_and_baseline"
- `status`: "PASS" | "FAIL"
- `components_count`: número total de componentes em `s33_components_map.yaml`
- `critical_components_count`: quantos são CRITICAL
- `issues_found`: lista (vazia em caso de PASS)
- `timestamp`

#### S33_G1_incidents_domain.json

- `gate`: "G1_incidents_domain"
- `status`
- `tests_run`: número de testes de domínio executados
- `tests_failed`: número de testes falhos
- `lifecycle_violations`: lista (se houver)
- `timestamp`

#### S33_G2_cockpit_ui.json

- `gate`: "G2_cockpit_ui"
- `status`
- `endpoints_checked`: lista (`overview`, `components`, `components/{id}`, etc.)
- `components_covered_ratio`: porcentagem de componentes do mapa retornados pela API
- `ui_smoke_passed`: bool
- `timestamp`

#### S33_G3_slos_and_observability.json

- `gate`: "G3_slos_and_observability"
- `status`
- `slos_defined`: total de SLOs em `s33_slos.md`
- `slos_evaluated`: quantos foram avaliados com sucesso
- `slos_with_alerts_configured`: quantos tem alerta testado
- `issues_found`
- `timestamp`

#### S33_G4_runbooks_and_evidence.json

- `gate`: "G4_runbooks_and_evidence"
- `status`
- `runbooks_count`: quantos runbooks existem em `docs/s33/runbooks/`
- `incidents_simulated`: quantos cenários foram exercitados
- `bundles_complete`: quantos bundles atendem ao checklist mínimo
- `issues_found`
- `timestamp`

#### S33_G5_orr_operacional.json

- `gate`: "G5_orr_operacional"
- `status`: "PASS" | "NO_GO"
- `operator_role`: descrição da pessoa convidada (ex.: "engenheiro que não implementou a S33")
- `steps_completed`: lista de passos do roteiro executados com sucesso
- `frictions`: lista de principais dificuldades
- `followups`: itens de backlog gerados a partir da ORR
- `timestamp`

Esses campos podem variar no detalhe, mas a ideia é que qualquer pessoa lendo o JSON entenda rapidamente **o que foi testado, o que passou, o que não passou e quando**.

---

### 4.4.4 Riscos principais da S33 e estratégias de mitigação

Mesmo com um plano bem definido, a S33 carrega riscos específicos de sprints de operação. Abaixo, os principais riscos e como mitigá‑los na prática.

#### Risco 1 — Escopo turvo (G0 fraco)

**Sintoma:** componentes importantes da operação ficam fora de `s33_components_map.yaml`, ou o mapa vira um dumping ground sem prioridade.

**Impacto:** cockpit e SLOs não cobrem o que realmente importa; operadores aprendem a ignorar a ferramenta.

**Mitigação:**
- revisar G0 com participação ativa de quem opera fontes/pipelines na prática;
- classificar criticidade com critérios objetivos (por exemplo, impacto em usuários ou em ingestão de fatos chave);
- manter o mapa enxuto: melhor cobrir bem um recorte pequeno do que cobrir mal tudo.

#### Risco 2 — Incident tratado como ticket genérico

**Sintoma:** Incident vira um campo de texto gigante com estado qualquer; lifecycle e vínculos com componentes/SLOs são ignorados.

**Impacto:** difícil aprender com incidentes passados; bundles viram coleções caóticas.

**Mitigação:**
- exigir testes de domínio de Incident (G1) bem cobrindo lifecycle;
- não considerar G1 PASS enquanto não houver exemplos reais/simulados coerentes;
- usar os próprios bundles de G4 como validação concreta do modelo.

#### Risco 3 — Cockpit só de aparência

**Sintoma:** UI bonita, mas alimentada por mocks isolados ou dados que não batem com observabilidade real.

**Impacto:** operadores perdem confiança; voltam a usar logs crus e painéis soltos.

**Mitigação:**
- amarrar G2 à execução real de `ops_health_summary` e da API, não a mocks rasos;
- garantir que scripts de sanity chamem o backend real em ambiente de teste;
- envolver operador desde cedo para validar se a visão faz sentido.

#### Risco 4 — SLOs "de PowerPoint"

**Sintoma:** SLO descrito em doc, mas sem query, sem alerta, sem integração com cockpit.

**Impacto:** sensação de que a ferramenta fala em SLOs sem nunca monitorá‑los de verdade.

**Mitigação:**
- G3 exige, no mínimo, queries rodando e testes de alerta para SLOs críticos;
- não considerar SLO "pronto" sem aparecer no cockpit (`SloSummaryPanel`);
- registrar em `G3` quando um SLO está parcialmente implementado, com plano claro de completude.

#### Risco 5 — Runbooks que não sobrevivem ao primeiro incidente

**Sintoma:** runbooks escritos de forma genérica, sem comandos concretos ou referências a painéis/logs reais.

**Impacto:** operadores abandonam runbooks em situações de pressão; cada incidente vira improviso.

**Mitigação:**
- exigir que pelo menos um incidente seja conduzido 100% via runbook (G4);
- ajustar runbooks logo após simulações, incorporando fricções observadas;
- tratar runbooks como código: versionados, revisados, melhorados com o tempo.

#### Risco 6 — ORR tratada como teatro

**Sintoma:** ORR encenada com autores operando o sistema, sem fricção real, slides lindos e pouco aprendizado.

**Impacto:** gaps de usabilidade e confiabilidade aparecem só em produção ou em situações críticas.

**Mitigação:**
- ORR sempre com um operador convidado que não escreveu o código;
- facilitador com liberdade para declarar NO_GO se operação não fluir;
- follow‑ups da ORR viram itens de backlog com dono e prazo.

---

### 4.4.5 Checklist final de encerramento da Sprint 33

Este é o checklist objetivo que precisa estar em PASS antes da S33 ser declarada concluída. A resposta para cada item precisa ser "sim" de forma honesta, e verificável via código/docs/evidência.

1. **Gates e scorecards**  
   - [ ] Existem scorecards para G0–G5 em `out/scorecards/S33_G*_*.json`.  
   - [ ] Todos os scorecards G0–G4 estão em `status = PASS`.  
   - [ ] O scorecard G5 existe, com `status` explícito (PASS ou NO_GO) e campos preenchidos.

2. **Evidências por gate**  
   - [ ] `out/evidence/S33_G0_scope_and_baseline/` contém logs e snapshot do scope + components_map.  
   - [ ] `out/evidence/S33_G1_incidents_domain/` contém logs de testes de domínio e exemplos de lifecycle.  
   - [ ] `out/evidence/S33_G2_cockpit_ui/` contém respostas reais de API e prints do cockpit.  
   - [ ] `out/evidence/S33_G3_slos_and_observability/` contém resultados de queries e, se possível, teste de alerta.  
   - [ ] `out/evidence/S33_G4_incidents/` contém pelo menos um bundle completo de incidente.  
   - [ ] `out/evidence/S33_G5_orr_operacional/` contém roteiro da ORR, notas e feedbacks.

3. **Documentação em `docs/s33/`**  
   - [ ] Capítulos 1, 2 e 3 estão atualizados e coerentes com o código (componentes, domínios, filemap).  
   - [ ] `s33_scope_ops.md` e `s33_components_map.yaml` refletem o recorte operado de fato.  
   - [ ] `s33_slos.md` lista os SLOs que foram implementados e avaliados.  
   - [ ] `s33_incidents_lifecycle.md` bate com o comportamento observado nos testes e bundles.  
   - [ ] `docs/s33/runbooks/` contém runbooks usados na prática na sprint.  
   - [ ] `s33_incidents_learnings.md` registra aprendizados e backlog gerado (especialmente da ORR).

4. **Backend e frontend alinhados com o Capítulo 3**  
   - [ ] Módulos `ops_components`, `incidents`, `ops_slos`, `ops_health_summary`, `ops_slo_evaluator` existem e são usados.  
   - [ ] API `ops_cockpit_routes.py` expõe os endpoints planejados e eles são consumidos pela UI.  
   - [ ] A feature `oracleops` no frontend contém as páginas e componentes descritos (Overview, ComponentDetails, Incidents, SloSummaryPanel, RunbookLinks).  
   - [ ] O cockpit mostra dados consistentes com observabilidade e Incident (sem mocks secretos).

5. **CI e scripts de gates**  
   - [ ] O workflow `s33-gates.yml` (ou equivalente) existe e está verde para o último commit da branch da sprint.  
   - [ ] Scripts `bin/s33_g0..g5_*.sh` existem, rodam sem erro e produzem scorecards/evidências.  
   - [ ] CI falha caso algum dos scripts de gate relevantes retorne erro.

6. **ORR operacional**  
   - [ ] A ORR foi executada com um operador que não implementou o núcleo da S33.  
   - [ ] O operador conseguiu:  
     - inspecionar saúde geral pelo cockpit;  
     - aprofundar-se em um componente crítico;  
     - acompanhar um incidente e entender o que aconteceu;  
     - encontrar e seguir um runbook até uma resolução razoável (mesmo que simulada).  
   - [ ] As fricções encontradas foram registradas e, as mais críticas, endereçadas ou planejadas.

7. **Decisão final: GO / NO_GO**  
   - [ ] A equipe (Produto, Engenharia, Ops) revisou os scorecards e evidências.  
   - [ ] Há um consenso explícito registrado (nem que seja em um doc simples) sobre o status da S33:  
     - GO — OracleOps v1 está pronto para ser considerado parte funcional do Inspectah no recorte da S33; ou  
     - NO_GO — faltam elementos críticos, com plano claro de correção em sprint(s) seguinte(s).

---

### 4.4.6 Conclusão: o que significa S33 realmente DONE

A Sprint 33 só pode ser chamada de concluída, no espírito deste bloco, quando:

- **os gates contam uma história consistente** (scorecards, scripts, CI em PASS);
- **as evidências existem e são legíveis** (bundles, logs, prints, docs coerentes);
- **o operador convidado conseguiu operar o recorte da S33** usando cockpit, SLOs, Incident e runbooks;
- **o estado final está refletido nos documentos da sprint**, especialmente no Capítulo 4 e em `s33_incidents_learnings.md`.

Quando isso acontece, o OracleOps v1 deixa de ser apenas um desejo e passa a ser uma camada concreta do Inspectah — auditável, consultável e evolutiva. Esse é o verdadeiro significado de DONE na S33.

