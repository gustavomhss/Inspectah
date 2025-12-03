# Inspectah — Sprint 30 — Capítulo 4 — Bloco 4
## Ritual de ORR, Checklist Binário de Evidências e Fechamento da Sprint 30

Este bloco fecha o Capítulo 4 amarrando três coisas que, juntas, definem se a Sprint 30 está **realmente pronta** ou só parece pronta:

1. O **ritual de ORR** (Operational Readiness Review) específico da S30;
2. Um **checklist binário de evidências** (sim/não) que não deixa espaço para “achismo”;
3. O **fechamento da sprint** no contexto do Épico E28.

A ideia aqui é transformar o fim da sprint em um processo repetível e quase mecânico: ou os critérios estão atendidos e tudo está documentado, ou não está pronto.

---

## 4.4 Ritual de ORR da Sprint 30

O ORR da S30 é feito **em cima do estado final do repositório e do bundle de evidências**. Não é conversa de corredor, é inspeção de artefatos.

Participantes recomendados:
- Responsável de Programa 1;
- Lead técnico de backend (fluxos);
- Lead de frontend (console/admin);
- Alguém do eixo de observabilidade;
- Pessoa com papel de guardião de qualidade/gates.

### 4.4.1 Preparação para o ORR

Antes da reunião de ORR:

1. **CI final rodando verde**
   - Workflow `.github/workflows/s30-gates.yml` deve ter sido executado na branch candidata ao merge;
   - Execução mais recente precisa estar com status `success`.

2. **Bundle de evidências gerado**
   - `bin/s30_bundle.sh` executado com sucesso (local ou via CI);
   - `out/bundles/inspectah_s30_evidence_bundle.zip` disponível (normalmente como artifact do CI);
   - `out/evidence/S30_ORR_summary.txt` criado (pode ser rascunho que será ajustado após ORR).

3. **Docs de sprint atualizados**
   - `docs/sprint_30_cap_1_contexto_problemas_objetivos.md` e Cap. 2/3 já espelhando o estado final;
   - Este Capítulo 4 (incluindo este bloco) atualizado com qualquer ajuste de última hora.

### 4.4.2 Passos do ORR

Durante a reunião, o time segue um roteiro explícito:

1. **Conferência de CI e gates**
   - Acessar a aba de Actions do repositório;
   - Abrir a última execução de `.github/workflows/s30-gates.yml` na branch da sprint;
   - Verificar que todos os jobs passaram;
   - Confirmar que **não há re‑runs vermelhos ignorados**.

2. **Inspeção de scorecards**
   - Abrir (ou extrair do bundle) os arquivos em `out/scorecards/`:
     - `S30_G0_scope_and_alignment.json`;
     - `S30_G1_flow_model_and_templates.json`;
     - `S30_G2_flow_console_ops.json`;
     - `S30_G3_flow_operations_safety.json`;
     - `S30_G4_flow_observability.json`;
     - `S30_G5_e2e_canonical_flow.json`;
     - `S30_metrics_summary.json`.
   - Confirmar, um por um, que `status = "PASS"`;
   - Verificar campos “reasons”/“notes” em `S30_metrics_summary.json` para entender qualquer ressalva.

3. **Navegação pelas evidências E2E (G5)**
   - Explorar `out/evidence/S30_G5_e2e_canonical_flow/`;
   - Verificar:
     - dataset de notícias usadas no teste;
     - logs de execução E2E (`e2e_run.log` ou equivalente);
     - capturas de tela do Console de Fluxos (lista, detalhe, execuções);
     - snapshot de métricas e logs estruturados relativos ao fluxo de notícias.

4. **Verificação de observabilidade (G4)**
   - Conferir `out/evidence/S30_G4_flow_observability/`;
   - Validar que as métricas e logs presentes respondem às perguntas:
     - “Quantas execuções de fluxo tivemos?”;
     - “Qual a taxa de erro?”;
     - “Como está a latência?”;
   - Se possível, abrir o painel real de métricas para olhar grafos em tempo real.

5. **Checagem de operações seguras (G3)**
   - Ler evidências em `out/evidence/S30_G3_flow_operations_safety/`;
   - Verificar um caso de reprocessamento aceito, um caso recusado e eventos de pausa/retomada documentados;
   - Confirmar que `FlowOperationLog` está sendo povoado corretamente.

6. **Avaliação qualitativa do Console de Fluxos**
   - Abrir o Console de Fluxos em ambiente de teste/QA;
   - Navegar pelos fluxos de notícias, mudar estados, ver execuções, abrir detalhe de execução;
   - Confirmar, subjetivamente, se o cockpit está **usável** para operação 24/7 (não é só “rodou uma vez”).

7. **Discussão de riscos residuais e dívidas**
   - Listar quaisquer riscos que permaneceram (ex.: limites de reprocessamento conservadores demais, UX ainda pouco polida em algum ponto);
   - Classificar cada risco como:
     - dívida de **épico** (para próximos sprints E28);
     - dívida de **produto** (para futuro programa);
     - ou blocker, caso realmente impeça GO.

8. **Preenchimento do resumo de ORR**
   - Atualizar `out/evidence/S30_ORR_summary.txt` com:
     - contexto da sprint;
     - principais entregas observáveis;
     - resumo de scorecards e métricas;
     - riscos residuais e dívidas declaradas;
     - decisão final (GO/NO‑GO) e justificativa curta.

### 4.4.3 Decisão de GO/NO‑GO

A decisão final é binária.

A S30 é considerada **GO** se, e somente se:
- todos os scorecards G0–G5 estão com `status = "PASS"`;
- `S30_metrics_summary.json` está com `status = "PASS"`;
- não existem blockers apontados no resumo de ORR;
- o squad responsável dá nota **≥ 9.9/10** para a pergunta:
  > “O Console de Fluxos para notícias está pronto para ser usado como cockpit real de operação, no nível de exigência do Inspectah?”

Caso qualquer um desses itens falhe, a sprint é **NO‑GO** e o bloco 4 orienta que os gaps sejam classificados e endereçados antes de tentar fechar a S30.

---

## 4.5 Checklist Binário de Evidências

Para eliminar ambiguidade, este checklist define o que precisa existir ao final da Sprint 30. Ele pode ser literalmente lido em voz alta no ORR.

### 4.5.1 Documentação

- [ ] `docs/sprint_30_cap_1_contexto_problemas_objetivos.md` existe, está completo e sem TODO/FIXME.
- [ ] `docs/sprint_30_cap_2_gates_metricas_dod.md` existe, está completo e sem TODO/FIXME.
- [ ] `docs/sprint_30_cap_3_arquitetura_filemap.md` existe, está completo e sem TODO/FIXME.
- [ ] `docs/sprint_30_cap_4_execucao_evidencias.md` existe, contém este bloco e está alinhado com o estado final.

### 4.5.2 Código e Arquitetura

- [ ] Módulo `app/flows/` contém models, service, routing, execution_engine e instrumentation conforme Cap. 3.
- [ ] `app/api/flow_console_routes.py` implementa todas as rotas previstas e não contém TODO/FIXME.
- [ ] `frontend/inspectah-ui/src/features/flows/` existe com páginas e componentes descritos no Cap. 3.
- [ ] Tests de backend para fluxos e APIs de console existem e rodam em verde.
- [ ] Tests de frontend do Console de Fluxos existem e rodam em verde.

### 4.5.3 Migrations e dados

- [ ] `migrations/versions/0030_s30_flow_model_v15.py` existe e aplica limpo em banco vazio e pós‑S29.
- [ ] Template de fluxo de notícias (`Fluxo_Noticias_Geral_v1` ou equivalente) existe em `FlowTemplate` e é validado como topologia correta.

### 4.5.4 Scripts e Workflows

- [ ] Todos os scripts de gate existem e são executáveis:
  - [ ] `bin/s30_g0_scope_and_alignment.sh`
  - [ ] `bin/s30_g1_flow_model_and_templates.sh`
  - [ ] `bin/s30_g2_flow_console_ops.sh`
  - [ ] `bin/s30_g3_flow_operations_safety.sh`
  - [ ] `bin/s30_g4_flow_observability.sh`
  - [ ] `bin/s30_g5_e2e_canonical_flow.sh`
- [ ] `bin/s30_metrics_summary.sh` existe e gera `S30_metrics_summary.json`.
- [ ] `bin/s30_bundle.sh` existe e gera `inspectah_s30_evidence_bundle.zip`.
- [ ] `.github/workflows/s30-gates.yml` existe e executa todos os scripts acima.

### 4.5.5 Scorecards

- [ ] `out/scorecards/S30_G0_scope_and_alignment.json` com `status = "PASS"`.
- [ ] `out/scorecards/S30_G1_flow_model_and_templates.json` com `status = "PASS"`.
- [ ] `out/scorecards/S30_G2_flow_console_ops.json` com `status = "PASS"`.
- [ ] `out/scorecards/S30_G3_flow_operations_safety.json` com `status = "PASS"`.
- [ ] `out/scorecards/S30_G4_flow_observability.json` com `status = "PASS"`.
- [ ] `out/scorecards/S30_G5_e2e_canonical_flow.json` com `status = "PASS"`.
- [ ] `out/scorecards/S30_metrics_summary.json` com `status = "PASS"`.

### 4.5.6 Evidências de Execução

- [ ] Pastas `out/evidence/S30_G0_*` … `S30_G5_*` existem e contêm logs, dumps e arquivos descritos no Bloco 3.
- [ ] `out/evidence/S30_ORR_summary.txt` existe, está preenchido e coerente com scorecards.
- [ ] `out/bundles/inspectah_s30_evidence_bundle.zip` existe e contém:
  - [ ] todos os `S30_G*.json`;
  - [ ] `S30_metrics_summary.json`;
  - [ ] todas as pastas `out/evidence/S30_G*`;
  - [ ] `S30_ORR_summary.txt`.

Se qualquer item deste checklist estiver em **não**, a sprint não deve ser declarada DONE sem uma decisão consciente de exceção (documentada em ORR).

---

## 4.6 Fechamento da Sprint 30 no Contexto do Épico E28

Com o ORR realizado e o checklist binário atendido, a Sprint 30 pode ser posicionada de forma clara dentro do Épico E28.

### 4.6.1 O que passa a ser verdade após a S30

Quando a S30 é GO, podemos afirmar, sem malabarismo, que:

1. **Existe um fluxo‑pivô de notícias configurável**
   - baseado em template canônico;
   - com estados fortes (`draft`, `em_teste`, `ativo`, `pausado`, `deprecado`).

2. **O Console de Fluxos é um cockpit real para notícias**
   - operadores conseguem criar fluxos a partir de template;
   - mudar estados com segurança;
   - acionar reprocessamentos limitados;
   - inspecionar execuções e jornadas.

3. **Execuções de fluxo são rastreáveis e observáveis**
   - há métricas e logs suficientes para monitorar saúde e desempenho;
   - existe cenário E2E documentado provando o caminho ingestão → fluxo → console → telemetria.

4. **O repositório incorpora a S30 como primeira peça sólida do E28**
   - scripts, scorecards e bundle transformam a sprint em algo audível e reexecutável.

### 4.6.2 O que fica como base para as próximas sprints do E28

As próximas sprints do Épico E28 (S31–S35) passam a tratar os artefatos da S30 como **infraestrutura de fluxo**. Em particular:

- S31+ podem:
  - generalizar o modelo de fluxos para outros tipos de entrada (dados diretos, casos especiais);
  - conectar fluxos de forma mais profunda com Debunker, Truth‑DB, casos e evidências;
  - sofisticar o cockpit (mais filtros, drill‑downs, dashboards dedicados).

- A S30 garante que:
  - o alicerce de “fluxo operável via console” está firme;
  - não é necessário reinventar a base de fluxos a cada nova sprint;
  - o time pode se concentrar em aumentar o poder e a inteligência dos fluxos, não em fazê‑los existir.

### 4.6.3 Regra de ouro de fechamento

A regra de ouro para encerrar a Sprint 30 é:

> “Se alguém, daqui a 6 meses, precisar reentender o que a S30 fez, deve conseguir fazê‑lo apenas com o repositório, os docs de sprint, os scorecards e o bundle de evidências — sem perguntar nada para pessoas específicas.”

Se essa frase for verdadeira, a S30 não é só uma sprint que “passou no CI”; ela é uma peça sólida e auditável do Épico E28.

Com isso, o Bloco 4 encerra o Capítulo 4 da Sprint 30 e transforma o fechamento da sprint em um procedimento claro, repetível e à prova de memória seletiva.