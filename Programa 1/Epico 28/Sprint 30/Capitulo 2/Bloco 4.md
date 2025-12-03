# Inspectah — Sprint 30 — Capítulo 2 — Bloco 4
## Definition of Done (DoD), CI/ORR da Sprint 30 e Empacotamento das Evidências

Este bloco fecha o Capítulo 2 traduzindo gates e métricas em um **ritual concreto de CI/ORR**. A pergunta aqui é binária: “Quando exatamente podemos dizer, sem vergonha, que a Sprint 30 está DONE (GO)?”

---

### 1. Definition of Done da Sprint 30 (nível sprint)

A Sprint 30 só pode ser considerada **DONE / GO** se **todas** as condições abaixo forem verdade ao mesmo tempo:

1. **Gates executados em CI, não só localmente**  
   - Todos os gates G0–G5 foram executados em um workflow oficial de CI (ex.: `.github/workflows/s30-gates.yml`) em branch de sprint ou de PR final.
   - Nenhum gate relevante foi rodado “apenas no meu computador” sem registro no CI.

2. **Scorecards de gates todos em PASS**  
   - Existem arquivos JSON, com formato padronizado, para cada gate:
     - `out/scorecards/S30_G0_scope_and_alignment.json`
     - `out/scorecards/S30_G1_flow_model_and_templates.json`
     - `out/scorecards/S30_G2_flow_console_ops.json`
     - `out/scorecards/S30_G3_flow_operations_safety.json`
     - `out/scorecards/S30_G4_flow_observability.json`
     - `out/scorecards/S30_G5_e2e_canonical_flow.json`
   - Todos com `status == "PASS"`.

3. **Scorecard agregado de métricas de sprint em PASS**  
   - O script `bin/s30_metrics_summary.sh` foi executado.
   - O arquivo `out/scorecards/S30_metrics_summary.json` existe e possui:
     - `epic == "E28_Fluxo_de_Agentes_Config_v1"`;
     - `sprint == "S30"`;
     - `status == "PASS"`.

4. **Bundle de evidências completo gerado e arquivado**  
   - O script `bin/s30_bundle.sh` foi executado ao fim do workflow de CI.
   - O arquivo `out/bundles/inspectah_s30_evidence_bundle.zip` existe e contém, no mínimo:
     - todas as pastas `out/evidence/S30_G*/`;
     - todos os `out/scorecards/S30_G*.json` e `S30_metrics_summary.json`;
     - um resumo textual `out/evidence/S30_ORR_summary.txt`.

5. **Capítulos 1–4 da sprint concluídos, sem buracos**  
   - Todos os docs da sprint (Cap. 1–4) estão presentes nos caminhos definidos no Capítulo 3.
   - Não há `TODO`, `FIXME`, `TBD`, comentários de "preencher depois" ou seções vazias.
   - Quaisquer limitações/remendos assumidos estão descritos explicitamente em Capítulo 4 (Execução & Evidências) como dívidas técnicas de E28.

6. **Repositório limpo e PR de sprint coerente**  
   - No momento do merge do PR da Sprint 30, não existem alterações locais não comitadas relacionadas à sprint.
   - O PR da sprint referencia, na descrição, pelo menos:
     - o contrato central de S30;
     - os principais gates e métricas;
     - o caminho do bundle de evidências.

7. **Confirmação do squad e do conselho**  
   - O Squad Fluxos & Orquestração declara, em nota de revisão, que as métricas definidas no Bloco 3 foram atingidas.
   - Ninguém do squad atribui nota < 9.9/10 para a afirmação "para o caso de notícias, o Console de Fluxos é o cockpit operacional".
   - O conselho técnico do Programa 1 (ou subseto relevante) não aponta blockers conceituais para E28 decorrentes da S30.

Se qualquer um desses pontos estiver pendente, a Sprint 30 deve ser considerada **NO-GO** ou **PARTIAL**, e os gaps precisam ser transcritos como dívida explícita de E28.

---

### 2. Workflow de CI da Sprint 30 (s30-gates.yml)

O workflow de CI da S30 deve ser:
- determinístico;
- legível;
- reproduzível localmente;
- centrado nos gates G0–G5 e na geração de evidence bundle.

#### 2.1. Estrutura recomendada do workflow

Arquivo: `.github/workflows/s30-gates.yml`

Jobs mínimos:

1. **setup**  
   - Checkout do repositório;
   - Setup de Python/Node (versões definidas no Capítulo 3);
   - Instalação de dependências backend/frontend;
   - Setup de serviços auxiliares (banco, collector de telemetria, etc., se necessário).

2. **gates-core**  
   - Executa, em sequência, os scripts:
     - `bin/s30_g0_scope_and_alignment.sh`
     - `bin/s30_g1_flow_model_and_templates.sh`
     - `bin/s30_g2_flow_console_ops.sh`
     - `bin/s30_g3_flow_operations_safety.sh`
     - `bin/s30_g4_flow_observability.sh`
   - Cada script deve:
     - ser idempotente;
     - produzir scorecard e evidências;
     - retornar código de saída não zero em caso de falha.

3. **gates-e2e**  
   - Executa `bin/s30_g5_e2e_canonical_flow.sh` em ambiente instrumentado:
     - inicializa fontes de teste de notícias;
     - injeta eventos;
     - coleta métricas e logs;
     - valida execuções no Console/API.

4. **metrics-and-bundle**  
   - Executa `bin/s30_metrics_summary.sh`;
   - Verifica que todos os scorecards G0–G5 estão presentes;
   - Executa `bin/s30_bundle.sh`;
   - Publica `out/bundles/inspectah_s30_evidence_bundle.zip` como artifact do workflow.

Todos os jobs devem:
- falhar o workflow se qualquer script retornar código ≠ 0;
- armazenar logs com retenção adequada para auditoria futura.

---

### 3. ORR de Sprint 30 (Operational Readiness Review)

A ORR da Sprint 30 não é um documento separado gigante; ela é uma **leitura estruturada de três camadas de evidência**:

1. **Scorecards de gates (G0–G5)**  
   - Respondem à pergunta: "cada peça crítica está saudável?".

2. **Scorecard agregado de métricas da sprint**  
   - Responde à pergunta: "a sprint, como unidade, cumpriu o contrato de E28?".

3. **Bundle de evidências**  
   - Permite auditar, se necessário, logs, prints, métricas e execuções reais.

Ritual mínimo de ORR para S30:

- Rodar o workflow `s30-gates` em branch candidata a merge;
- Baixar o `inspectah_s30_evidence_bundle.zip`;
- Navegar, na seguinte ordem:
  1. `out/scorecards/S30_G*_*.json` — garantir que todos estão em PASS;
  2. `out/scorecards/S30_metrics_summary.json` — verificar estado geral da sprint;
  3. `out/evidence/S30_G5_e2e_canonical_flow/` — conferir rapidamente a sanidade do cenário E2E;
  4. `out/evidence/S30_ORR_summary.txt` — leitura sintética da sprint.

Se, durante a ORR, surgir qualquer dúvida grave (por exemplo, indício de que o fluxo de notícias ainda depende de intervenção manual de dev), o merge deve ser bloqueado até que:
- o problema seja corrigido;
- os gates sejam rerodados;
- novos scorecards e bundle sejam produzidos.

---

### 4. Tratamento de falhas de gate e de métrica

Falhas são esperadas durante o desenvolvimento; o que não é aceitável é **normalizar** gate vermelho.

Regra do squad para S30:

- Qualquer falha em G0–G5 deve resultar em:
  - correção de código/config;
  - rerun do script do gate;
  - atualização de scorecards e evidências.
- Se, próximo ao fim da sprint, ainda houver falhas em métricas de sprint (Bloco 3), o squad deve decidir, explicitamente, entre:
  - estender o esforço até cumprir o contrato; ou
  - registrar as falhas como dívida crítica do Épico E28, com plano explícito em S31+.

Não existe cenário em que S30 é declarada "GO" com métricas críticas em aberto sem essa decisão conscientemente registrada.

---

### 5. Ligação com o restante do Programa 1

O DoD da S30 foi desenhado para que, ao marcar a sprint como DONE, o Programa 1 possa assumir, com segurança, que:

- existe um caso de prova concreto de fluxo operável (notícias) sobre o qual outros times podem se apoiar (Debunker, Truth‑DB, UI de Casos);
- a infraestrutura de fluxos e console está madura o suficiente para ser replicada/adaptada a outros tipos de fluxo nas sprints seguintes;
- o risco de "fluxos bonitos no papel, inoperáveis na prática" foi drasticamente reduzido.

Este Bloco 4 encerra o Capítulo 2 da Sprint 30: a partir daqui, qualquer pessoa que leia os Capítulos 1 e 2 sabe **o que** S30 quer entregar, **como** isso será testado e **quando** podemos, com rigor, declarar a sprint como concluída.

