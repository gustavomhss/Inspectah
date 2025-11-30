# Inspectah — Sprint 26 (S26)
## Capítulo 2 — Bloco 2.4
### Definition of Done (DoD) da S26 & Regras de NO-GO

Este bloco define o **Definition of Done (DoD)** da Sprint 26 e explicita as condições formais de **NO-GO**. Ele amarra, em uma visão única, tudo o que foi definido nos blocos 2.1, 2.2 e 2.3: gates, scripts, scorecards e evidências.

A S26 só é considerada **DONE / GO** se **todos** os critérios abaixo forem verdadeiros ao mesmo tempo.

---

## 1. DoD Técnico

1. **Todos os gates G0–G6 executam com sucesso em ambiente local e em CI**
   - Scripts `bin/s26_g0_scope_and_baseline.sh` a `bin/s26_g6_orr_bundle.sh` retornam exit code `0` na branch de release da sprint.
   - Não há “bypass manual” de gate (ex.: alteração de scorecard à mão para mascarar falhas).

2. **Scorecards de G0–G6 presentes e coerentes**
   - Todos os arquivos `out/scorecards/S26_G*.json` existem, são JSON válidos e contêm os campos esperados definidos no Bloco 2.2.
   - Todos os campos críticos de cada scorecard respeitam os thresholds de GO (por exemplo, nenhum contador de erros > 0 onde o limite aceitável é 0).

3. **Design System Admin v1 integrado e consistente**
   - O Design System Admin v1 está implementado na árvore de frontend dedicada (ex.: `ui/admin` ou path equivalente definido no Cap.3).
   - Não existem componentes admin novos fora dessa árvore (nenhum “component solto” para telas de admin introduzido na S26).
   - Os testes específicos do design system estão verdes (G1) e não há erros de lint/TypeScript na pasta.

4. **Console de Fontes v2 funcional sobre o design system**
   - Todos os fluxos principais do Console de Fontes v2 (lista, criação, edição, ativar/desativar/arquivar) estão cobertos por testes de G2 e passam integralmente.
   - O console utiliza exclusivamente componentes do Design System Admin v1 (sem componentes legacy misturados em áreas principais da UI).

---

## 2. DoD de Produto & UX

1. **Operação de fontes 100% via UI (para fluxos básicos)**
   - Um operador técnico consegue, usando apenas o Console de Fontes v2, sem scripts externos, executar os fluxos:
     - listar fontes;
     - cadastrar uma nova fonte;
     - ajustar uma fonte existente;
     - ativar, desativar e arquivar fontes nos cenários suportados.

2. **Aderência ao Design System Admin v1**
   - O Console de Fontes v2 respeita tokens, tipografia, espaçamentos, estilos de erro/loading/vazio e componentes definidos pelo design system.
   - Não há incoerências visuais gritantes (por exemplo, botões fora do padrão, cores ad hoc, textos desalinhados com guidelines).

3. **Coerência com o modelo de dados de fontes**
   - Labels, mensagens e estados exibidos na UI refletem o modelo de dados real e suas invariantes.
   - Não há campos “fantasma” (expostos na UI mas ignorados no backend) nem campos críticos invisíveis para o operador.

---

## 3. DoD de Documentação & Evidências

1. **Guia do Design System Admin v1 publicado**
   - Arquivo de guia (ex.: `docs/design_system_admin_v1.md`) existe e descreve:
     - o propósito do design system;  
     - onde encontrar os componentes;  
     - como criar novas telas admin seguindo o padrão.
   - O guia tem tamanho mínimo (≥ 30 linhas, conforme G5) e está alinhado com a implementação real (não é um rascunho teórico obsoleto).

2. **Runbook de operação de fontes publicado**
   - Arquivo de runbook (ex.: `docs/runbook_operacao_fontes_v1.md`) existe e explica, em linguagem operacional:
     - como listar fontes;  
     - como criar/editar fontes;  
     - como ativar/desativar/arquivar;  
     - quais cuidados tomar em operações sensíveis.
   - O runbook tem tamanho mínimo (≥ 30 linhas, conforme G5) e foi escrito com base nas telas finais da sprint.

3. **Mapa de evidências completo e bundle gerado**
   - Todas as pastas `out/evidence/S26_G*/` (G0–G6) existem e contêm artefatos consistentes com o que está descrito no Bloco 2.3.
   - O bundle `out/bundles/inspectah_s26_evidence_bundle.zip` existe, é legível e contém, no mínimo, as pastas de evidências e os scorecards da S26.

---

## 4. Regras Formais de NO-GO

Independentemente da percepção do squad, de demos bonitas ou de pressões de calendário, a S26 é **NO-GO** se **qualquer** das condições abaixo for verdadeira:

1. **Algum gate G0–G6 falha em CI**
   - Se qualquer script `bin/s26_g*_*.sh` retornar exit code diferente de `0` na execução oficial da sprint, a S26 não pode ser promovida.

2. **Scorecards indicam métricas críticas fora do threshold**
   - Exemplo: `lint_errors_count > 0` em G1 ou G3;  
   - `ds_component_tests_passed < ds_component_tests_total` em G1;  
   - `flows_passed < flows_total` ou `flows_blocking_failures > 0` em G2;  
   - `api_tests_passed < api_tests_total` ou `contract_violations_found > 0` em G4;  
   - ausência ou tamanho abaixo do mínimo dos docs em G5;  
   - `bundle_created == false` ou `bundle_size_bytes == 0` em G6.

3. **Operação básica de fontes ainda depende de scripts externos**
   - Se, na prática, for necessário editar banco ou rodar scripts manuais para executar fluxos que deveriam estar cobertos pelo Console de Fontes v2 (como ativar/desativar/arquivar fontes), a sprint é NO-GO.

4. **Inconsistência grave entre UI e backend de fontes**
   - Se forem detectadas discrepâncias críticas entre o que a UI mostra (estados, campos, labels) e o que o backend realmente persiste ou retorna, sem correção registrada na sprint, S26 não deve ser dada como concluída.

5. **Bundle de evidências ausente ou incompleto**
   - Se o ZIP de evidências não puder ser gerado, estiver corrompido ou faltar pastas de evidências obrigatórias (G0–G6), não há como auditar a sprint, logo não há GO.

---

## 5. Síntese do Bloco 2.4

O Bloco 2.4 fecha o Capítulo 2 da S26 com um veredito binário: 

- se **todos** os gates G0–G6 estão verdes, scorecards e evidências estão no lugar, UI e backend estão coerentes, docs e runbooks existem e o bundle foi gerado, a S26 é **GO**;  
- se **qualquer** uma das condições de NO-GO for verdadeira, a sprint permanece em estado **incompleta**, e os problemas devem ser registrados e tratados antes que o trabalho seja considerado parte estável do Programa 1.

Dessa forma, o DoD deixa de ser opinião e passa a ser um conjunto de condições verificáveis, alinhado com o espírito de rigor e auditabilidade que o Inspectah exige do próprio produto.