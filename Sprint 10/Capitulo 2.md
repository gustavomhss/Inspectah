# Sprint 10 — Capítulo 2 — Gates, SLIs/SLOs e DoD (Truth-DB & Guardião de Blocos) (v3)

Versão v3 — refinada em conjunto com a “banca” (Jobs, Lamport, Vitalik, Knuth, Kay, Kleppmann, Pérez, Meyer) a partir do Capítulo 1 v3, do DNA/Leassons e da v2 deste capítulo. Foco: máxima clareza operacional, zero ambiguidade e encaixe perfeito com a execução do Cap. 3.

---

## 0) TL;DR — como sabemos, sem dúvida, que a S10 ficou pronta

A Sprint 10 só é considerada **DONE + GO** quando, ao olhar os artefatos da S10:

1. Todos os **gates S10-G0…S10-G7** estão `status="PASS"`, com scorecards e evidências correspondentes.
2. O gate **S10-G8** emite um **`decision = "GO"`** explícito, com resumo humano coerente.
3. Fica evidente que:
   - a Truth-DB existe, está íntegra e pronta para ser consumida por S11/S12;
   - a máquina de estados de fato é respeitada em 100% dos caminhos felizes testados;
   - o contrato de ações do Guardião é pequeno, estável e realmente seguido na prática;
   - a engine mecânica aceita tudo que é válido e rejeita tudo que é inválido, sem corromper dados;
   - há pelo menos dois domínios piloto funcionando ponta a ponta;
   - qualquer fato piloto possui linha do tempo completa (eventos, estados, relatórios) e auditável.

Regra filosófica da S10:

> **Sem Truth-DB confiável não existe Inspectah confiável. Sem gates duros, não existe Truth-DB confiável.**

Gates estruturais (modelo, estados, contrato, engine) **não admitem WARN**. Eles existem para impedir “atalhos inteligentes” que explodam no futuro.

---

## 1) Papel deste capítulo

Este Capítulo 2 responde à pergunta: **“Como medimos, com frieza, se a S10 entregou o que o Capítulo 1 promete?”**

Ele faz isso ao:

1. Definir os **gates S10-G0…S10-G8**.
2. Mapear **quais objetivos do Capítulo 1** cada gate protege.
3. Especificar **SLIs/SLOs** usados para avaliar o resultado.
4. Descrever a **Definition of Done (DoD)** da S10 em termos de gates + evidências.
5. Estabelecer a **governança de mudanças** nesses gates.

Os Capítulos 3 e 4 transformam estes conceitos em arquivos, scripts e prompts.

---

## 2) Mapa objetivo → gate

Do Capítulo 1 (v3), temos sete objetivos principais da S10. Este capítulo amarra cada objetivo aos gates que o protegem.

| Objetivo Cap. 1                                      | Principais gates que validam                     |
|-----------------------------------------------------|--------------------------------------------------|
| Truth-DB canônica v1                                | G1 (modelo), G4 (engine), G5–G6 (E2E), G7       |
| GPT como Guardião com contrato claro                | G3 (contrato), G4 (engine), G5–G6 (E2E)         |
| Camada mecânica de validação                        | G3 (uso do contrato), G4 (engine), G5–G6        |
| Máquina de estados formalizada                      | G2 (estados), G4 (aplicação), G5–G6             |
| Pipelines ponta a ponta em domínios piloto          | G5 (domínio A), G6 (domínio B)                  |
| Auditabilidade forte para Admin                     | G5–G6 (trilhas), G7 (audit & exports)           |
| Preparação explícita para S11/S12                   | G1 (campos futuros), G7 (future-ready), G8      |

Além disso:

- **G0** garante que estamos no repo/branch certo, com DNA e env corretos.
- **G8** consolida tudo em uma decisão GO/NO-GO, com scorecard único da S10.

---

## 3) Mapa geral dos gates S10

Visão resumida:

| Gate   | Pergunta-chave                                                                | Tipo principal                    |
|--------|-------------------------------------------------------------------------------|-----------------------------------|
| G0     | Ambiente, repo e DNA da S10 estão íntegros e alinhados?                      | Sanidade & alinhamento            |
| G1     | O modelo de dados da Truth-DB é consistente, testado e versionado?           | Modelo & schema                   |
| G2     | A máquina de estados de fatos está formalizada e protegida?                  | Estados & invariantes             |
| G3     | O contrato de ações do Guardião é pequeno, claro e aplicado sem desvios?     | Contrato de ações do GPT         |
| G4     | A camada mecânica de validação aplica/rejeita ações corretamente?            | Engine & invariantes operacionais |
| G5     | O pipeline ponta a ponta funciona para o domínio piloto A?                    | E2E domínio A                     |
| G6     | O pipeline ponta a ponta funciona para o domínio piloto B?                    | E2E domínio B                     |
| G7     | Auditabilidade e preparação para S11/S12 estão no nível exigido?             | Auditabilidade & futuro           |
| G8     | Há base objetiva para declarar GO/NO-GO da Sprint 10 como um todo?           | Consolidação & decisão final      |

- **G0** é gate de entrada.
- **G1–G4** são gates estruturais.
- **G5–G6** são gates de fluxo com domínios reais.
- **G7** garante que o resultado é auditável e utilizável por S11/S12.
- **G8** fecha a sprint com decisão explícita.

---

## 4) SLIs e SLOs globais da S10

Estes SLIs são “termômetros” compartilhados entre vários gates.

### 4.1 SLI-1 — Integridade de ações válidas

- **Definição**: proporção de ações válidas, segundo o contrato oficial, que são aceitas pela camada mecânica em cenários de teste.
- **Métrica**: `ratio_valid_actions_accepted = ações_válidas_aceitas / ações_válidas_enviadas`.
- **SLO**: `ratio_valid_actions_accepted = 1.0`.
- **Gates**: G3, G4, G5, G6.
- **Classificação**: HARD.

### 4.2 SLI-2 — Integridade de rejeição de ações inválidas

- **Definição**: proporção de ações claramente inválidas (payload errado, transição proibida, IDs inexistentes) que são rejeitadas com motivo explícito.
- **Métrica**: `ratio_invalid_actions_rejected = ações_inválidas_rejeitadas / ações_inválidas_enviadas`.
- **SLO**: `ratio_invalid_actions_rejected >= 0.99` (meta real 1.0; o 0,99 amortiza apenas ruídos de teste).
- **Gates**: G3, G4.
- **Classificação**: HARD.

### 4.3 SLI-3 — Completude de trilha de auditoria

- **Definição**: proporção de fatos piloto para os quais o sistema consegue gerar, de forma automática, uma linha do tempo completa (eventos de domínio + estados + relatórios) sem buracos.
- **Métrica**: `audit_trace_completeness = fatos_com_trilha_completa / fatos_piloto_amostrados`.
- **SLO**: `audit_trace_completeness = 1.0`.
- **Gates**: G5, G6, G7.
- **Classificação**: HARD.

### 4.4 SLI-4 — Prontidão para S11/S12

- **Definição**: proporção de entidades piloto (blocos/fatos) que possuem todos os campos marcados como “necessários para S11/S12” (IDs estáveis, hashes, vínculos mínimos de evidência, etc.).
- **Métrica**: `future_ready_completeness = entidades_futuro_ok / entidades_piloto_amostradas`.
- **SLO**: `future_ready_completeness >= 0.95`.
- **Gates**: G1, G7.
- **Classificação**: SOFT (pode admitir WARN com ADRs claros).

### 4.5 SLI-5 — Sucesso de pipelines E2E em cenários de demonstração

- **Definição**: proporção de cenários E2E (definidos no Cap. 3) que concluem com Truth-DB atualizada + scorecards PASS.
- **Métrica**: `e2e_scenario_success_rate = cenários_e2e_ok / cenários_e2e_totais`.
- **SLO**: `e2e_scenario_success_rate >= 0.95`.
- **Gates**: G5, G6.
- **Classificação**: SOFT.

### 4.6 Quadro-resumo de SLOs

| SLI   | Descrição resumida                     | SLO alvo                 | Tipo  |
|-------|----------------------------------------|--------------------------|-------|
| SLI-1 | Ações válidas aceitas                  | = 1.0                    | HARD  |
| SLI-2 | Ações inválidas rejeitadas             | ≥ 0.99 (meta 1.0)        | HARD  |
| SLI-3 | Trilha de auditoria completa           | = 1.0                    | HARD  |
| SLI-4 | Campos prontos para S11/S12            | ≥ 0.95                   | SOFT  |
| SLI-5 | Cenários E2E concluídos com sucesso    | ≥ 0.95                   | SOFT  |

---

## 5) Gates em detalhe

### 5.1 G0 — Sanidade de ambiente, repo e DNA

**Pergunta-chave**  
“Estamos de fato na S10, com repo, branch, DNA e env corretos, antes de medir qualquer coisa?”

**Escopo**

- Repositório e origem corretos (Inspectah, branch da S10).
- Documentos básicos presentes:
  - Cap. 1 (visão) v3;
  - Cap. 2 (este), versão estável v3;
  - referência ao contrato de ações (`docs/sprint_10_contrato_acoes_guardiao.md`) e ao modelo de dados.
- Variáveis de ambiente mínimas para rodar os scripts de G1–G7.
- Estrutura de `out/scorecards/` e `out/evidence/` preparada para a S10.

**SLIs/SLOs**

- Não há SLI numérico; é gate de sanidade.

**PASS / WARN / FAIL**

- **PASS**: todas as checagens de repo, docs e env passam; scorecard G0 marca `status = "PASS"`.
- **WARN**: não permitido.
- **FAIL**: qualquer checagem crítica falha.

---

### 5.2 G1 — Modelo de dados da Truth-DB consistente

**Pergunta-chave**  
“O modelo de dados da Truth-DB está saudável, completo e preparado para o futuro?”

**Escopo**

- Existência/consistência das entidades centrais:
  - `BlocoTema`, `FatoRegistravel`, `Complemento`, `VersaoFato`, `EstadoFato`.
- Relações básicas válidas (nenhum fato sem bloco, nenhuma versão órfã, etc.).
- Migrations/esquemas versionados e rodando sem erros.
- Testes de integridade estrutural.

**SLIs/SLOs**

- SLI-4 (future_ready_completeness >= 0.95).

**PASS / WARN / FAIL**

- **PASS**:
  - todos os testes de integridade passam;
  - `future_ready_completeness >= 0.95`;
  - não há violações de integridade estrutural nos dados de teste.
- **WARN**:
  - permitido apenas se `0.90 <= future_ready_completeness < 0.95` **e** houver ADR/tickets explicitando o que falta;
  - integridade estrutural não pode ter WARN.
- **FAIL**:
  - qualquer falha grave de integridade (entidade órfã, relação obrigatória faltando, etc.);
  - `future_ready_completeness < 0.90`.

**Evidência**

- Scorecard `out/scorecards/S10_G1_truthdb_model.json`.
- Dumps/resumos de entidades em `out/evidence/S10_G1/…`.

---

### 5.3 G2 — Máquina de estados de fatos

**Pergunta-chave**  
“A máquina de estados de fatos está formalizada, testada e blindada contra transições inválidas?”

**Escopo**

- Lista explícita de estados (ex.: `planejado`, `confirmado`, `concluido`, `nao_confirmado`, `adiado`, `cancelado`, `incerto`).
- Tabela de transições válidas/proibidas (persistida em código/config).
- Testes de transição (válidas e inválidas).
- Documentação legível da máquina de estados.

**SLIs/SLOs**

- SLI-2 (rejeição de ações inválidas) — aqui, focado em transições.

**PASS / WARN / FAIL**

- **PASS**:
  - todas as transições válidas passam;
  - todas as transições inválidas, dentro do conjunto de teste, são rejeitadas;
  - não existem atalhos que ignorem a máquina de estados.
- **WARN**: não permitido.
- **FAIL**:
  - qualquer transição inválida aceita;
  - divergência documentada entre tabela e comportamento.

**Evidência**

- Scorecard `out/scorecards/S10_G2_state_machine.json`.
- Relatório de testes e diagrama textual em `out/evidence/S10_G2/…`.

---

### 5.4 G3 — Contrato de ações do Guardião

**Pergunta-chave**  
“O contrato de ações do Guardião é pequeno, coerente e realmente aplicado?”

**Escopo**

- Artefato canônico de contrato presente (ex.: `docs/sprint_10_contrato_acoes_guardiao.md`).
- Conjunto de ações pequeno e claro:
  - `criar_bloco_tema`, `criar_fato_registravel`, `anexar_complemento`, `atualizar_estado_fato`, `criar_versao_fato`, `promover_complemento_a_fato` (se usada), etc.
- Esquemas/validações de payload para cada ação.
- Testes de ações válidas/ inválidas.
- Prompts do GPT referenciando explicitamente o contrato.

**SLIs/SLOs**

- SLI-1 (ratio_valid_actions_accepted = 1.0).
- SLI-2 (ratio_invalid_actions_rejected >= 0.99).

**PASS / WARN / FAIL**

- **PASS**:
  - todas as ações válidas do contrato são aceitas;
  - ações inválidas de teste são rejeitadas com razão clara;
  - não existem ações implementadas mas não documentadas, ou vice-versa.
- **WARN**: não permitido.
- **FAIL**:
  - divergência contrato ↔ implementação;
  - rejeição de ação válida ou aceitação recorrente de ação inválida;
  - prompts usando formatos/nomes fora do contrato.

**Evidência**

- Scorecard `out/scorecards/S10_G3_guardian_contract.json`.
- Amostras de ações + resultados em `out/evidence/S10_G3/…`.

---

### 5.5 G4 — Camada mecânica de validação/aplicação

**Pergunta-chave**  
“A engine mecânica aplica o contrato e as invariantes de forma determinística e segura?”

**Escopo**

- Componente claro que recebe ações JSON, valida e aplica/rejeita.
- Verificação de invariantes:
  - integridade de IDs;
  - relações obrigatórias;
  - respeito à máquina de estados.
- Tratamento de erros (sem panics nem falhas silenciosas).
- Testes de integração exercitando cenários felizes e de erro.

**SLIs/SLOs**

- SLI-1 e SLI-2 (mesmas metas HARD).

**PASS / WARN / FAIL**

- **PASS**:
  - nenhuma ação válida rejeitada nos testes;
  - ações inválidas rejeitadas com mensagens compreensíveis;
  - ausência de panics/exceções não tratadas/corrupção de dados.
- **WARN**: não permitido.
- **FAIL**:
  - qualquer evidência de corrupção de dados ou violação de invariantes;
  - erros não tratados em cenários previstos.

**Evidência**

- Scorecard `out/scorecards/S10_G4_mechanical_engine.json`.
- Logs de testes e snapshots antes/depois da Truth-DB em `out/evidence/S10_G4/…`.

---

### 5.6 G5 — E2E — Domínio piloto A

**Pergunta-chave**  
“O pipeline S10 funciona de ponta a ponta em um domínio real A (ex.: obras públicas)?”

**Escopo**

- Fluxo completo no domínio A:
  - ingestão de eventos;
  - agrupamento por tema;
  - chamada do GPT Guardião;
  - ações + relatórios;
  - validação mecânica;
  - atualização na Truth-DB;
  - linha do tempo reconstruível para fatos piloto.

**SLIs/SLOs**

- SLI-1, SLI-2 (para ações do domínio A).
- SLI-3 (audit_trace_completeness = 1.0).
- SLI-5 (e2e_scenario_success_rate >= 0.95) — considerando apenas cenários do domínio A.

**PASS / WARN / FAIL**

- **PASS**:
  - cenários felizes A concluem com Truth-DB atualizada;
  - trilha de auditoria completa para fatos piloto A;
  - SLI-5 dentro do SLO; falhas apenas em casos-limite documentados.
- **WARN**:
  - permitido se `0.90 <= e2e_scenario_success_rate < 0.95` **e** os cenários que falham forem explicitamente marcados como trabalho futuro;
  - SLI-3 deve continuar = 1.0 para os fatos piloto.
- **FAIL**:
  - falha em cenários felizes;
  - buracos de auditabilidade em fatos piloto.

**Evidência**

- Scorecard `out/scorecards/S10_G5_e2e_domain_A.json`.
- Cenários executados + dumps de blocos/fatos em `out/evidence/S10_G5/…`.

---

### 5.7 G6 — E2E — Domínio piloto B

**Pergunta-chave**  
“O pipeline S10 funciona de ponta a ponta em um segundo domínio B (ex.: preços)?”

**Escopo**

- Igual ao G5, mas exercendo caminhos diferentes do modelo/estados.

**SLIs/SLOs**

- SLI-1, SLI-2, SLI-3, SLI-5 — avaliados para o domínio B.

**PASS / WARN / FAIL**

- Regras idênticas ao G5, avaliadas nos cenários do domínio B.

**Evidência**

- Scorecard `out/scorecards/S10_G6_e2e_domain_B.json`.
- Cenários executados + dumps de blocos/fatos em `out/evidence/S10_G6/…`.

---

### 5.8 G7 — Auditabilidade & preparação para S11/S12

**Pergunta-chave**  
“Dá para auditar as decisões da S10 e usar a Truth-DB diretamente em S11/S12?”

**Escopo**

- Trilhas de auditoria para fatos piloto (A e B) completas e fáceis de consultar.
- Exports estruturados (por bloco/fato) prontos para consumo de S11/S12.
- Campos “futuros” (IDs estáveis, hashes, etc.) realmente preenchidos.
- Documentação clara explicando como S11/S12 devem consumir esses dados.

**SLIs/SLOs**

- SLI-3 (audit_trace_completeness = 1.0) — considerando conjunto de fatos piloto.
- SLI-4 (future_ready_completeness >= 0.95).

**PASS / WARN / FAIL**

- **PASS**:
  - trilha de auditabilidade completa (SLI-3 = 1.0);
  - SLI-4 >= 0.95;
  - pelo menos um formato de export estável e documentado.
- **WARN**:
  - permitido se `0.90 <= future_ready_completeness < 0.95` **e** os casos faltantes forem documentados como não críticos;
  - não é permitido WARN em auditabilidade.
- **FAIL**:
  - qualquer buraco de auditabilidade em fatos piloto;
  - `future_ready_completeness < 0.90`.

**Evidência**

- Scorecard `out/scorecards/S10_G7_audit_and_future.json`.
- Exports de blocos/fatos + doc de consumo em `out/evidence/S10_G7/…`.

---

### 5.9 G8 — GO/NO-GO da Sprint 10

**Pergunta-chave**  
“Dado tudo que os gates G0…G7 mostraram, a S10 é GO ou NO-GO?”

**Escopo**

- Agregar resultados de G0…G7 em um scorecard único da sprint.
- Produzir um resumo humano que explique:
  - status de cada gate;
  - SLIs/SLOs atingidos ou não;
  - riscos residuais aceitos;
  - débitos técnicos registrados.

**Regras para avaliar GO**

- Pré-condições:
  - G0 deve ser PASS;
  - G1, G2, G3, G4 devem ser PASS, sem WARN;
  - G5, G6, G7 podem ter WARN apenas em SLIs SOFT (SLI-4, SLI-5), com ADR/tickets.

- **GO**:
  - todas as pré-condições satisfeitas;
  - nenhum FAIL em G0…G7;
  - WARNs, se existirem, são explícitos, pequenos e já registrados como trabalho futuro.

- **NO-GO**:
  - qualquer FAIL em qualquer gate;
  - qualquer WARN em gates estruturais (G1–G4);
  - ausência de evidência para um gate obrigatório.

**Evidência**

- Scorecard final `out/scorecards/S10_G8_go_no_go.json` com `decision = "GO"` ou `"NO_GO"`.
- Resumo humano em `docs/sprint_10_summary.md` e espelho em `out/evidence/S10_G8/summary.json`.

---

## 6) Definition of Done (DoD) da Sprint 10

A S10 é **DONE** apenas se **todas** estas condições forem verdadeiras:

1. **Gates estruturais**
   - G0, G1, G2, G3, G4 em PASS, sem WARN.

2. **Gates E2E (domínios piloto)**
   - Domínio A e domínio B cobertos por pipelines ponta a ponta;
   - SLI-3 = 1.0 para fatos piloto;
   - SLI-5 >= 0.95 para cada domínio (ou WARN SOFT bem justificado);
   - quaisquer WARNs estão em SLIs SOFT e não afetam o fluxo feliz.

3. **Gate de futuro (G7)**
   - auditabilidade completa (SLI-3 = 1.0);
   - SLI-4 >= 0.95 ou WARN SOFT com ADR.

4. **Gate final (G8)**
   - scorecard G8 existe e marca `decision = "GO"`;
   - resumo humano da S10 alinhado com o Cap. 1 e com os resultados dos gates.

5. **Documentação e trilha de evidências**
   - scorecards S10-G0…S10-G8 presentes em `out/scorecards/`;
   - pastas `out/evidence/S10_G*/` preenchidas;
   - Capítulos 1–4 da S10 atualizados, coerentes entre si e consistentes com os scorecards.

Se qualquer ponto acima falhar, a Sprint 10 **não** está DONE, mesmo que “pareça quase pronta”.

---

## 7) Governança de mudanças nos gates

Para impedir que os gates se tornem um alvo móvel:

1. **Congelamento inicial**
   - Este Cap. 2 é considerado “congelado” após o primeiro PASS do G0 na branch da S10.

2. **Mudanças permitidas sem drama**
   - clarificações de texto;
   - adição de SLIs complementares (sem remover SLIs existentes);
   - ajustes menores em descrições de evidência.

3. **Mudanças que exigem ADR**
   - afrouxar qualquer SLO HARD (SLI-1, SLI-2, SLI-3);
   - mudar limiares de GO/NO-GO;
   - remover ou fundir gates.

4. **Mudanças proibidas (sem ADR forte + consenso)**
   - alterar gates para “maquiar” FAILs;
   - rebaixar HARD → SOFT para passar sprint sem corrigir problemas estruturais.

5. **Registro obrigatório**
   - qualquer mudança relevante neste capítulo deve estar rastreada via commit + ADR, e referenciada no resumo da S10 (G8).

---

## 8) Relação com os outros capítulos da S10

- **Capítulo 1 — Visão**  
  Define o *porquê* e o *o quê* da Truth-DB & Guardião de Blocos.

- **Capítulo 2 — Gates (este)**  
  Define *como medimos* se essa visão foi entregue.

- **Capítulo 3 — Execução & filemap**  
  Vai transformar cada gate em arquivos, scripts (`bin/s10_g*_*.sh`) e rotinas que produzem scorecards e evidências.

- **Capítulo 4 — Codex & automação**  
  Vai alinhar o contrato de ações do Guardião e os gates com prompts e fluxos do Codex.

Juntos, os quatro capítulos garantem que a S10 não seja só uma ideia boa, mas uma sprint **gated, auditável e repetível**, no nível de excelência esperado pelo DNA do projeto.