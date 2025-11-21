# Inspectah – Sprint 12
## Capítulo 2 — Gates de Validação, SLIs/SLOs e DoD

_Ingestão Contínua & Comunidade v0 (fase sem blockchain)_

---

## 0. TL;DR — quando a S12 está realmente DONE + GO

A Sprint 12 **só** é considerada DONE + GO quando todas estas condições são verdade ao mesmo tempo:

1. Todos os gates **S12‑G0…S12‑G7** geram scorecards em `out/scorecards/` com `status = "PASS"` (ou `WARN` apenas nos pontos explicitamente permitidos) e evidências correspondentes em `out/evidence/S12_G*/…`.
2. O gate **S12‑G8** produz `out/scorecards/S12_G8_decision.json` com `decision = "GO"` **e** um wrap humano em `out/evidence/S12_G8/summary.md` explicando por que é GO, quais riscos foram aceitos e quais próximos passos ficam em aberto.
3. A **demo padrão da S12** (definida no Capítulo 1) funciona ponta‑a‑ponta, sem gambiarra manual:
   - scheduler puxando eventos de pelo menos **dois domínios piloto** em cadências distintas;
   - **todo evento** passando pelo **Debunker v0** com estado + racional;
   - eventos aparecendo como **timeline em casos/temas**, respeitando as invariantes I1–I3;
   - **Inspectah Explorer v0** permitindo buscar casos, abrir a página, ver timeline, abrir fontes;
   - botão **“reportar problema”** gerando feedback que chega na fila interna em tempo aceitável.

Se qualquer uma dessas condições falhar, a S12 **não** está pronta, independentemente da sensação subjetiva da equipe.

---

## 1. Papel deste capítulo

O Capítulo 1 define **o que** a Sprint 12 promete entregar (ingestão contínua, Debunker v0 obrigatório, casos/temas com timeline, Explorer v0 e feedback mínimo).

Este Capítulo 2 responde: **“como sabemos, de forma fria e objetiva, se essa promessa foi cumprida?”**

Ele faz isso ao:

- definir os **gates S12‑G0…S12‑G8** e suas perguntas‑chave;
- estabelecer **SLIs/SLOs globais da S12** e sua distribuição por gate;
- especificar o formato mínimo de **scorecards** e **evidências**;
- cravar a **Definition of Done (DoD)** da S12 em termos de gates;
- definir a **governança de mudanças** nesses gates (como evoluir sem quebrar o DNA).

Nenhum gate da S12 pode depender de blockchain, reputação complexa ou Sistema de Blocos completo. Tudo aqui é estritamente **fase sem blockchain**, como definido na nota de escopo.

---

## 2. Formato de scorecards e evidências

Cada gate S12‑G* produz **exatamente um scorecard JSON** em `out/scorecards/`:

```json
{
  "gate": "S12-G5",
  "status": "PASS" | "WARN" | "FAIL",
  "slis": {
    "SLI-1": {"value": 0.98, "slo": 0.95, "status": "PASS"},
    "SLI-4": {"value": 1.0, "slo": 0.98, "status": "PASS"}
  },
  "details": {"notes": "...", "metrics": {"...": 123}},
  "ts": "2025-..T..Z"
}
```

- **Evidências brutas** (logs, dumps, fixtures, capturas, exports de métricas) ficam em `out/evidence/S12_G*/…` com estrutura documentada no Cap. 3.
- **`status`** segue convenção:
  - `PASS` → gate aprovado;
  - `WARN` → gate aprovado com ressalva controlada;
  - `FAIL` → gate reprovado, S12 não pode ir a GO.

**Regra de WARN:**

- só é permitido nos gates explicitamente marcados como `WARN aceitável`;
- deve vir acompanhado de:
  - referência a ADR/ticket;
  - explicação clara do impacto;
  - plano mínimo para remoção do WARN.

Gates estruturais de sanidade (**G0, G3, G4, G6**) não aceitam `WARN`.

---

## 3. SLIs/SLOs globais da Sprint 12

A S12 tem cinco SLIs globais, que aparecem em diferentes gates.

### 3.1. SLI‑1 — Frescor da ingestão contínua

**Pergunta:** os eventos recentes estão sendo ingeridos em tempo hábil?

- Definição (por domínio piloto):
  - janela móvel de 24h;
  - `freshness_ratio = eventos_processados_recentemente / eventos_esperados_recentemente`, considerando um limite de tempo `T_ingest_max` entre captura e processamento.
- SLO: `freshness_ratio >= 0.95` para cada domínio piloto.
- Classificação: **HARD** para domínios piloto (não se discute em produção do V0).

### 3.2. SLI‑2 — Cobertura do Debunker v0

**Pergunta:** algum evento elegível virou candidato a fato principal sem passar pelo Debunker v0?

- Definição:
  - `debunker_coverage = eventos_com_debunker / eventos_elegiveis_truthdb`.
- SLO: `debunker_coverage = 1.0`.
- Classificação: **HARD**, zero tolerância.

### 3.3. SLI‑3 — Integridade de casos/temas e timelines

**Pergunta:** a estrutura de casos/temas e timelines está íntegra e sem buracos?

- Definição (amostra representativa de eventos normalizados):
  - `case_integrity_ratio = eventos_com_caso_valido_e_timeline_ok / eventos_normalizados_amostrados`.
  - Cada evento da amostra precisa:
    - pertencer a exatamente um `id_caso` válido;
    - respeitar as invariantes I1–I3 do Cap. 1 (sem duplicatas lógicas, sem regressão temporal, sem casos cross‑domínio).
- SLO: `case_integrity_ratio >= 0.99` em domínios piloto.
- Classificação: **HARD** (domínios piloto), `WARN` possível apenas em domínios experimentais não críticos.

### 3.4. SLI‑4 — Sucesso de navegação do Explorer v0

**Pergunta:** um humano consegue usar o Explorer v0 para fazer o básico sem travar?

- Fluxos medidos:
  - F1: buscar um caso por texto livre e abrir a página;
  - F2: rolar a timeline e abrir pelo menos uma fonte original;
  - F3: acionar “reportar problema” a partir de um caso/evento.
- Definição:
  - `explorer_success_rate = fluxos_sucesso / fluxos_totais`.
- SLO: `explorer_success_rate >= 0.98` para o conjunto F1–F3.
- Classificação: **HARD**.

### 3.5. SLI‑5 — Entrega do feedback (“reportar problema”)

**Pergunta:** os feedbacks gerados pelo botão “reportar problema” chegam rapidamente numa fila interna triável?

- Definição:
  - `feedback_delivery_ratio = feedbacks_na_fila_em_T / feedbacks_criados`, com `T = T_feedback_max`.
- SLO: `feedback_delivery_ratio = 1.0` com `T_feedback_max <= 2 minutos` em ambiente dev/local.
- Classificação: **HARD**.

---

## 4. Mapa de gates da S12 (visão geral)

| Gate | Pergunta‑chave                                                             | Tipo principal                      | WARN? |
|------|---------------------------------------------------------------------------|-------------------------------------|-------|
| G0   | Repo/branch/env da S12 estão corretos e alinhados com DNA e Cap. 1?      | Sanidade & alinhamento              | Não   |
| G1   | Fontes e scheduler estão configurados e rodando com frescor aceitável?   | Ingestão & cadência                 | Sim   |
| G2   | Pipeline de ingestão/normalização é íntegro, idempotente e observável?   | Pipeline & dados                    | Sim   |
| G3   | Debunker v0 cobre 100% das entradas elegíveis com estados consistentes?   | Qualidade de decisão (Debunker)     | Não   |
| G4   | Casos/temas e timelines respeitam invariantes e mantêm integridade?       | Modelo de casos & timeline          | Não   |
| G5   | Explorer v0 permite navegação básica (buscar → abrir caso → ver timeline)?| UX/E2E frontend                     | Sim   |
| G6   | Fluxo de “reportar problema” funciona ponta a ponta e é triável?         | Feedback & triagem                  | Não   |
| G7   | SLIs/SLOs e observabilidade estão no nível exigido para operação 24/7?    | Observabilidade & operação contínua | Sim   |
| G8   | Há base objetiva para declarar GO/NO‑GO da S12 como um todo?             | Consolidação & decisão final        | Não   |

A seguir, detalhamos cada gate.

---

## 5. Gates S12‑G0…S12‑G7 em detalhe

### 5.1. S12‑G0 — Sanidade de ambiente, repo e DNA

**Pergunta‑chave**  
“Estamos de fato na S12, com repo, branch, DNA, Cap. 1 e ambiente corretos, antes de rodar qualquer coisa?”

**Escopo**

- Repositório `Inspectah` e branch da S12 corretamente checados.
- Confirmação de que o Cap. 1 e este Cap. 2 da S12 são as versões finais referenciadas.
- Variáveis de ambiente mínimas (paths, flags de modo dev, etc.).
- Estrutura mínima de `out/scorecards/` e `out/evidence/` criada.

**Execução**

- Script: `bin/s12_g0_env_repo.sh`:
  - valida remote/branch;
  - checa presença dos docs de S12;
  - prepara diretórios de saída;
  - grava `out/scorecards/S12_G0_env_repo.json` e evidências em `out/evidence/S12_G0/`.

**SLIs/SLOs**

- Sem SLI global aqui; apenas checagens binárias.

**PASS / WARN / FAIL**

- PASS: todas as checagens de repo/docs/env passam; scorecard com `status = "PASS"`.
- WARN: não permitido.
- FAIL: qualquer checagem crítica falha (branch errado, docs ausentes, env incompleto).

---

### 5.2. S12‑G1 — Fontes e scheduler configurados e saudáveis

**Pergunta‑chave**  
“As fontes prioritárias e o scheduler conseguem rodar sem quebrar o sistema e com frescor aceitável?”

**Escopo**

- Cadastro de fontes para **dois domínios piloto** (ex.: `obra_publica`, `evento_climatico`).
- Configuração de cadências (`realtime`, `hourly`, `daily`, etc.).
- Scheduler central:
  - dispara jobs na cadência correta;
  - registra logs por fonte;
  - evita explosões de volume por erro de configuração.

**Execução**

- Script: `bin/s12_g1_sources_scheduler.sh`:
  - roda uma janela curta de ingestão (real ou simulada);
  - mede `freshness_ratio` por domínio;
  - gera `out/scorecards/S12_G1_sources_scheduler.json` + evidências.

**SLIs/SLOs**

- SLI‑1 (frescor): `freshness_ratio >= 0.95` em cada domínio piloto na janela de teste.

**PASS / WARN / FAIL**

- PASS:
  - scheduler dispara todos os conectores esperados;
  - `freshness_ratio >= 0.95` em domínios piloto;
  - sem erros críticos de autenticação/configuração.
- WARN (permitido):
  - `0.90 <= freshness_ratio < 0.95` em **um** domínio piloto por motivo externo conhecido (ex.: API instável), com ADR/ticket.
- FAIL:
  - `freshness_ratio < 0.90` em qualquer domínio piloto;
  - ou falha grave do scheduler (jobs não disparam, crash sistemático).

---

### 5.3. S12‑G2 — Pipeline de ingestão e normalização íntegro

**Pergunta‑chave**  
“O pipeline que transforma payload bruto em evento normalizado é íntegro, idempotente e visível?”

**Escopo**

- Transformação payload bruto → evento normalizado com campos mínimos do Cap. 1.
- Roteamento determinístico evento → caso/tema.
- Tratamento de duplicatas lógicas (idempotência).
- Logs suficientes para debugar o caminho de cada evento.

**Execução**

- Script: `bin/s12_g2_ingest_pipeline.sh`:
  - injeta fixtures controladas;
  - reprocessa os mesmos inputs 1–2 vezes;
  - verifica se não há duplicação lógica nem perda de eventos;
  - grava `S12_G2_ingest_pipeline.json` + dumps em `out/evidence/S12_G2/`.

**SLIs/SLOs**

- SLI‑1 (frescor) sob perspectiva de throughput/latência de pipeline (apenas sanity).
- SLI‑3 (integridade de casos): `case_integrity_ratio >= 0.99` na amostra de teste.

**PASS / WARN / FAIL**

- PASS:
  - reprocessar não gera duplicatas lógicas;
  - `case_integrity_ratio >= 0.99`;
  - erros de parsing são logados e não derrubam o pipeline.
- WARN (permitido):
  - `0.97 <= case_integrity_ratio < 0.99` em domínios não piloto, com ADR/ticket.
- FAIL:
  - `case_integrity_ratio < 0.97` em domínios piloto;
  - idempotência quebrada ou eventos sumindo sem log.

---

### 5.4. S12‑G3 — Cobertura e comportamento do Debunker v0

**Pergunta‑chave**  
“Todo evento elegível passa pelo Debunker v0 e recebe estado + racional?”

**Escopo**

- Chamada obrigatória ao Debunker v0 para todo evento elegível à Truth‑DB.
- Registro estruturado de:
  - estado ∈ {`aceito`, `incerto`, `suspeito`};
  - racional curto (texto).
- Checagem de que não existem eventos elegíveis sem esse registro.

**Execução**

- Script: `bin/s12_g3_debunker_coverage.sh`:
  - roda uma bateria de ingestão (fixtures + alguns fluxos reais);
  - coleta estatísticas de cobertura;
  - gera `S12_G3_debunker_coverage.json` + amostras de decisões em `out/evidence/S12_G3/`.

**SLIs/SLOs**

- SLI‑2 (cobertura do Debunker): `debunker_coverage = 1.0`.

**PASS / WARN / FAIL**

- PASS:
  - `debunker_coverage = 1.0`;
  - todos os eventos elegíveis possuem estado + racional.
- WARN: não permitido.
- FAIL:
  - qualquer evento elegível sem decisão do Debunker ou sem racional.

---

### 5.5. S12‑G4 — Integridade de casos/temas e timelines

**Pergunta‑chave**  
“A organização por casos/temas e as timelines refletem, sem buracos, o que o pipeline produziu?”

**Escopo**

- Criação e manutenção de casos conforme definição mínima do Cap. 1.
- Atribuição de eventos a casos, respeitando invariantes I1–I3.
- Geração de timelines ordenadas, append‑only, com correções aparecendo como novos eventos ou versões.

**Execução**

- Script: `bin/s12_g4_cases_timeline.sh`:
  - escolhe um conjunto de casos piloto (A, B, C);
  - injeta/ingere eventos em ordem conhecida;
  - valida invariantes e integridade;
  - exporta snapshots em `out/evidence/S12_G4/cases/*.json`;
  - grava `S12_G4_cases_timeline.json`.

**SLIs/SLOs**

- SLI‑3 (case_integrity_ratio): `>= 0.99` em domínios piloto.

**PASS / WARN / FAIL**

- PASS:
  - nenhuma violação de I1–I3 em domínios piloto;
  - `case_integrity_ratio >= 0.99`.
- WARN: não permitido em domínios piloto; aceito apenas, e com ADR, em domínios experimentais fora da S12.
- FAIL:
  - casos com eventos órfãos, múltiplos casos incoerentes ou `case_integrity_ratio < 0.99` em domínio piloto.

---

### 5.6. S12‑G5 — Explorer v0: navegação básica

**Pergunta‑chave**  
“Um humano consegue, de verdade, usar o Explorer v0 para buscar e entender um caso?”

**Escopo**

- Fluxos mínimos:
  - F1: buscar caso por texto livre → abrir página do caso;
  - F2: rolar timeline → abrir fonte original;
  - F3: acionar “reportar problema” a partir de um caso/evento (até o ponto de submissão).
- Resiliência mínima a erros pontuais (sem telas em branco ou travamentos sistemáticos).

**Execução**

- Script: `bin/s12_g5_explorer_e2e.sh`:
  - executa fluxos F1–F3 via browser headless ou cliente HTTP;
  - opcionalmente orienta um smoke manual com roteiro fixo;
  - gera `S12_G5_explorer_e2e.json` e evidências em `out/evidence/S12_G5/` (prints, HAR etc.).

**SLIs/SLOs**

- SLI‑4 (explorer_success_rate): `>= 0.98` em F1–F3.

**PASS / WARN / FAIL**

- PASS:
  - `explorer_success_rate >= 0.98` em F1–F3;
  - ausência de erros 500 recorrentes ou páginas vazias.
- WARN (permitido):
  - `0.95 <= explorer_success_rate < 0.98` em **um** fluxo não crítico, com ticket e plano de correção.
- FAIL:
  - qualquer fluxo essencial (F1 ou F2) com `explorer_success_rate < 0.95`;
  - falhas consistentes de navegação.

---

### 5.7. S12‑G6 — Feedback “reportar problema” ponta a ponta

**Pergunta‑chave**  
“Quando alguém aperta ‘reportar problema’, o feedback chega de forma confiável numa fila triável?”

**Escopo**

- Botão “reportar problema” em nível de evento e/ou caso.
- Backend para criação/persistência do feedback.
- Fila interna ou endpoint de listagem para operadores.
- Capacidade mínima de marcar feedback como `novo` / `em_analise` / `resolvido`.

**Execução**

- Script: `bin/s12_g6_feedback_flow.sh`:
  - executa N fluxos de geração de feedback (automatizados + 1–2 manuais);
  - mede tempo entre "clique" e "entrada na fila";
  - verifica persistência e leitura;
  - gera `S12_G6_feedback_flow.json` + evidências.

**SLIs/SLOs**

- SLI‑5 (feedback_delivery_ratio): `= 1.0` com `T_feedback_max <= 2 minutos`.

**PASS / WARN / FAIL**

- PASS:
  - 100% dos feedbacks criados aparecem na fila interna dentro de `T_feedback_max`;
  - operador consegue listar e ler o conteúdo.
- WARN: não permitido.
- FAIL:
  - qualquer feedback perdido;
  - latência sistemática acima do limite sem explicação e correção.

---

### 5.8. S12‑G7 — Observabilidade & operação 24/7

**Pergunta‑chave**  
“Conseguimos operar o Inspectah S12 como serviço 24/7 sem voar cegos?”

**Escopo**

- Métricas disponíveis (via endpoint, arquivo ou painel) para:
  - ingestão por fonte/domínio (eventos/hora, erros/hora);
  - distribuição aceito/incerto/suspeito por fonte/domínio/dia;
  - SLIs SLI‑1…SLI‑5 calculados periodicamente.
- Logs claros para:
  - erros do scheduler/conectores;
  - decisões importantes do Debunker;
  - ações tomadas em feedbacks.
- Runbook mínimo para operadores:
  - como verificar se o sistema está vivo;
  - como identificar uma fonte quebrada;
  - como inspecionar backlog de feedbacks.

**Execução**

- Script: `bin/s12_g7_observabilidade.sh`:
  - coleta amostra de métricas e logs após janela de operação (ex.: 24h reais ou simuladas);
  - valida a existência de consultas/scripts que respondam às perguntas do runbook;
  - gera `S12_G7_observabilidade.json` + evidências.

**SLIs/SLOs**

- Consolida SLI‑1…SLI‑5 ao longo de uma janela de operação.

**PASS / WARN / FAIL**

- PASS:
  - todos os SLIs mensuráveis e dentro dos SLOs em janela considerada;
  - capacidade comprovada de responder às perguntas básicas do runbook.
- WARN (permitido):
  - algum SLI levemente no limite por motivo externo documentado (ex.: instabilidade de fonte), com ADR/ticket;
  - observabilidade básica ainda funcional.
- FAIL:
  - ausência de métricas ou logs essenciais;
  - impossibilidade de calcular SLIs;
  - operador não consegue determinar se o sistema está saudável.

---

## 6. S12‑G8 — Gate de decisão GO/NO‑GO

**Pergunta‑chave**  
“Com todos os scorecards G0…G7 em mãos, podemos declarar a Sprint 12 GO para uso real do V0?”

**Escopo**

- Leitura mecânica dos scorecards S12‑G0…S12‑G7.
- Consolidação em um scorecard de decisão: `out/scorecards/S12_G8_decision.json`.
- Wrap humano em `out/evidence/S12_G8/summary.md` contendo:
  - decisão (`GO` ou `NO_GO`);
  - resumo dos principais achados;
  - riscos/resíduos aceitos;
  - próximos passos propostos.

**Execução**

- Script: `bin/s12_g8_decision.sh`:
  - verifica a existência e o `status` de todos os scorecards anteriores;
  - aplica regras de decisão (abaixo);
  - grava scorecard + wrap.

**Regras de decisão**

- GO:
  - G0, G3, G4, G6 obrigatoriamente `PASS`;
  - G1, G2, G5, G7 `PASS` ou `WARN` apenas nos cenários permitidos e documentados;
  - demo padrão da S12 executável de ponta a ponta.
- NO_GO:
  - qualquer gate HARD com `status = "FAIL"`;
  - qualquer WARN não permitido;
  - incapacidade de executar a demo do Cap. 1 sem intervenção manual pesada.

---

## 7. Definition of Done (DoD) da Sprint 12

A Sprint 12 é considerada **DONE** (antes da decisão formal) quando:

1. Todos os scripts `bin/s12_g0…bin/s12_g7` existem, rodam localmente e produzem scorecards e evidências conforme este capítulo.
2. Os SLIs SLI‑1…SLI‑5 são computados a partir de dados reais ou simulações controladas e registrados de maneira consultável.
3. O fluxo de demo descrito no Cap. 1 (seção 0) é reproduzível em ambiente dev/local, seguindo um roteiro documentado.
4. Existe documentação mínima (Cap. 3/4) explicando como rodar cada gate, interpretar scorecards, ler métricas e logs.

A Sprint 12 é considerada **DONE + GO** quando, além dos pontos acima, o gate **S12‑G8** grava `decision = "GO"` e o wrap humano explicita que os riscos aceitos estão em linha com a nota de escopo (sem blockchain, sem reputação pesada, sem Sistema de Blocos completo).

---

## 8. Governança de mudanças nos gates da S12

- Qualquer mudança em **SLIs/SLOs** ou em critérios de `PASS/WARN/FAIL`:
  - exige ADR (`docs/adr/adr_s12_*.md`);
  - deve atualizar simultaneamente este Cap. 2, os scripts de gate (Cap. 3) e, se aplicável, as consultas de métricas.
- Mudanças em **nomes de scripts/arquivos**:
  - devem preservar compatibilidade ou vir acompanhadas de uma nota de migração;
  - não podem quebrar reexecução de gates históricos sem justificativa forte.
- Inclusão de **novos gates**:
  - só é aceitável se proteger objetivo crítico do Cap. 1 ainda não coberto;
  - não pode deslocar o foco da S12 para temas da fase 2 (blockchain, reputação, Sistema de Blocos full).

---

## 9. Relação com os outros capítulos da Sprint 12

- **Capítulo 1 – Visão**: define por que a S12 existe e o que ela promete entregar (serviço 24/7, Debunker v0 em tudo, Explorer v0, feedback mínimo).
- **Capítulo 2 – Gates (este)**: define como medir, com SLIs/SLOs e gates S12‑G0…S12‑G8, se essa promessa foi cumprida.
- **Capítulo 3 – Arquitetura e filemap**: transformará cada gate em arquivos, diretórios, scripts e dados de teste concretos.
- **Capítulo 4 – Execução e Codex**: alinhará os gates com prompts do Codex, pipelines de CI e rotinas de execução local.

Quando os quatro capítulos estiverem alinhados, a Sprint 12 deixa de ser uma ideia e vira um **pacote replicável, auditável e operacional**, no nível de excelência esperado pelo DNA do Inspectah.

