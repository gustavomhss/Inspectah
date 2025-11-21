# Sprint 13 — Capítulo 2 — Gates & Critérios de Validação (v2)

Versão revisada em conjunto com a equipe (Jobs, Knuth, Kay, Lamport, Vitalik, Kleppmann, Meyer, Pavel), alinhada ao DNA e ao blueprint S10–S16. Este capítulo define **como a Sprint 13 prova, de forma objetiva, que o piloto multi-domínio está pronto**.

---

## 0) Objetivo deste capítulo

O Capítulo 1 descreve **o que** a Sprint 13 quer entregar: um piloto multi-domínio em seis arquétipos de caso (obra pública, evento climático, projeto de lei, carreira política, perfil de influencer, carreira de atleta), apoiado no backbone da S12.

Este Capítulo 2 define **como medimos e garantimos** que essa visão foi realmente entregue, usando:

- um conjunto de **gates S13_G0…S13_G8**;
- **SLIs e SLOs** claros, alinhados à S12;
- **scorecards JSON e evidências em disco**, reprodutíveis via linha de comando.

A ideia é simples: se todos os gates deste capítulo estiverem verdes (e a decisão final G8 for GO), então a Sprint 13 de fato entrega um piloto multi-domínio útil, coeso e pronto para servir de base às próximas sprints.

---

## 1) Relação com S12 e com os outros capítulos da S13

### 1.1 Ponto de partida: S12

A Sprint 13 **não recria infraestrutura**. Ela parte de um estado em que a S12 já entregou:

- ingestão contínua enxuta com registry de fontes e scheduler;
- normalizadores de domínio (obra pública, evento climático) e Debunker v0 obrigatório;
- serviços de casos, timelines e adapter de Truth-DB em memória;
- Explorer v0 + painel de feedback v0 funcional;
- gates S12_G0…S12_G8 com decisão GO e evidências consolidadas.

Os gates da S13 assumem que:

- o repositório está em um commit compatível com a **tag de referência da S12** (ex.: `v0.3-s12`), ou equivalente;
- o scorecard `S12_G8_decision.json` existe e contém `decision = "GO"`;
- os scripts/gates da S12 continuam reprodutíveis.

### 1.2 Papel da S13 dentro da própria sprint

- **Capítulo 1** — define visão e escopo do piloto multi-domínio.
- **Capítulo 2 (este)** — define **gates, SLIs, SLOs e critérios de GO/NO-GO**.
- **Capítulo 3** — mapeia gates em arquitetura e filemap (scripts, serviços, UI, configs).
- **Capítulo 4** — traduz tudo isso em plano de execução (Codex, CI, comandos, orquestrador).

Capítulo 2 é o **gargalo máximo de sanidade**: se algo importante não estiver aqui, a sprint não está verdadeiramente protegida.

---

## 2) SLIs globais da Sprint 13

Para evitar métricas soltas, a S13 trabalha com um conjunto pequeno e forte de SLIs globais, usados por vários gates.

**SLI-1 — domain_pilot_coverage**  
Fração de tipos de domínio piloto que possuem **pelo menos 1 caso piloto ativo e integro**.

- Cálculo:
  - `dominios_totais = 6` (obra_publica, evento_climatico, projeto_lei, carreira_politica, influencer, atleta)
  - `dominios_cobertos = quantidade de domínios com >= 1 caso piloto válido`
  - `domain_pilot_coverage = dominios_cobertos / dominios_totais`
- SLO: `domain_pilot_coverage = 1.0` (todos os 6 domínios cobertos).  
- Natureza: **HARD** (sem WARN).

**SLI-2 — pilot_timeline_integrity_ratio**  
Fração de casos piloto cujas timelines passam nos checks de integridade:

- ordenação temporal coerente;
- estados válidos (aceito/incerto/suspeito ou equivalentes);
- invariantes do serviço de timeline (sem loops impossíveis, estados finais sem base, etc.).

- Cálculo:
  - `casos_piloto_total = n_casos_piloto`
  - `casos_ok = n_casos_piloto_com_timeline_valida`
  - `pilot_timeline_integrity_ratio = casos_ok / casos_piloto_total`
- SLO: `≥ 0.98`.
- Natureza: **HARD**.

**SLI-3 — debunker_explanation_coverage**  
Fração de eventos dos casos piloto que receberam **decisão + explicação mínima** do Debunker v0.

- Cálculo:
  - `eventos_totais = n_eventos_piloto`
  - `eventos_cobertos = n_eventos_com_decisao_e_explicacao`
  - `debunker_explanation_coverage = eventos_cobertos / eventos_totais`
- SLO: `≥ 0.95` (alvo recomendado: 1.0).  
- Natureza: **HARD**.

**SLI-4 — explorer_success_rate**  
Fração de cenários de consulta (roteiro de testes) em que o Explorer retorna o caso correto, com timeline acessível.

- Cálculo:
  - `cenarios_totais = n_cenarios_teste`
  - `cenarios_ok = n_cenarios_com_caso_correto_e_timeline`
  - `explorer_success_rate = cenarios_ok / cenarios_totais`
- SLO: `≥ 0.95` (com faixa de WARN).  
- Natureza: **SOFT** (WARN permitido).

**SLI-5 — feedback_delivery_ratio**  
Fração de tentativas de "reportar problema" que resultam em feedback persistido + visível no painel interno.

- Cálculo:
  - `feedback_tentado = n_tentativas`
  - `feedback_ok = n_feedbacks_persistidos_e_listados`
  - `feedback_delivery_ratio = feedback_ok / feedback_tentado`
- SLO: `≥ 0.95` (meta 1.0).  
- Natureza: **SOFT** (WARN permitido, mas limitado).

**SLI-6 — narrative_completeness_ratio**  
Fração de casos piloto que possuem narrativa mínima completa:

- título claro;
- descrição curta;
- campo de estado atual em linguagem humana;
- parágrafo de resumo ("história em 1 minuto").

- Cálculo:
  - `casos_piloto_total = n_casos_piloto`
  - `casos_completos = n_casos_com_narrativa_completa`
  - `narrative_completeness_ratio = casos_completos / casos_piloto_total`
- SLO: `= 1.0`.  
- Natureza: **HARD**.

---

## 3) Mapa de gates S13_G0…S13_G8 (visão geral)

| Gate   | Pergunta principal                                                                                   | Objetivo central                               |
|--------|------------------------------------------------------------------------------------------------------|------------------------------------------------|
| S13_G0 | Estamos no repo/branch/versão certos, com S12 em GO e docs da S13 presentes?                         | Sanidade de ambiente & alinhamento             |
| S13_G1 | Os 6 domínios piloto têm ao menos 1 caso configurado e íntegro cada?                                 | Cobertura multi-domínio                        |
| S13_G2 | As timelines dos casos piloto são válidas e coerentes com o backbone de S12?                         | Integridade de casos & timeline                |
| S13_G3 | O Debunker v0 cobre e explica os eventos dos 6 domínios piloto com consistência mínima aceitável?    | Decisão & explicabilidade                      |
| S13_G4 | O Explorer consegue localizar e abrir corretamente os casos piloto, por domínio?                     | Experiência de consulta (Explorer v0)          |
| S13_G5 | Cada caso piloto possui narrativa mínima legível (título, resumo, estado atual em linguagem humana)? | Narrativa & compreensão humana por caso        |
| S13_G6 | O fluxo de feedback funciona nos casos piloto e gera backlog organizado por domínio?                 | Feedback & geração de backlog para S14+        |
| S13_G7 | As métricas e evidências da S13 estão consolidadas e sem regressão grave vs. S12?                    | Observabilidade & fotografia da sprint         |
| S13_G8 | Há base objetiva para declarar GO/NO-GO para o piloto multi-domínio da S13?                          | Decisão final da sprint (GO/NO-GO fundamentado)|

Os detalhes de implementação (scripts, rotas, caminhos de arquivo) ficam para o Capítulo 3 (arquitetura/filemap) e Capítulo 4 (execução). Aqui definimos **contrato de comportamento** de cada gate.

---

## 4) Gates S13 — Definição detalhada

### 4.1 S13_G0 — Sanidade & alinhamento com S12

**Pergunta-chave**  
"Estamos no ambiente certo, em cima de uma S12 saudável, com a documentação da S13 no lugar?"

**Escopo**

- Verificar que:
  - estamos dentro do repo `Inspectah`;
  - o `remote.origin.url` aponta para o GitHub oficial;
  - a branch ativa é `main` ou a branch de trabalho da Sprint 13 (ex.: `s13_piloto_multi_dominio_v0`);
  - existe **tag ou scorecard de S12** indicando `decision = "GO"` (ex.: `v0.3-s12` + `out/scorecards/S12_G8_decision.json`);
  - os Capítulos 1–4 da S13 existem nos caminhos combinados (ex.: `Sprint 13/Capitulo 1.md`…`Capitulo 4.md`).

**SLIs usados**

- Não introduz SLI novo; gate de sanidade pura.

**Regras PASS / WARN / FAIL**

- **PASS**:
  - repo/remote corretos;
  - S12 em GO (tag/scorecard);
  - docs da S13 presentes;
  - estrutura mínima de `out/` (scorecards/evidências) pronta.
- **WARN**: não permitido.
- **FAIL**:
  - repo inválido;
  - remoto errado;
  - ausência de evidência de S12 em GO;
  - Capítulos da S13 ausentes.

**Evidência esperada**

- `out/scorecards/S13_G0_env_repo.json` com checklist de sanidade.
- `out/evidence/S13_G0/env_snapshot.txt` com resumo de branch, remote, tag S12 e presença de docs.

---

### 4.2 S13_G1 — Cobertura de domínios piloto

**Pergunta-chave**  
"Os 6 domínios piloto da Sprint 13 têm pelo menos 1 caso piloto configurado e íntegro cada?"

**Escopo**

- Arquivo canônico de pilotos (ex.: `config/s13_pilotos.yml`), contendo para cada domínio:
  - tipo (`obra_publica`, `evento_climatico`, `projeto_lei`, `carreira_politica`, `influencer`, `atleta`);
  - 1+ casos piloto (ID, nome, contexto, domínio);
  - metadados mínimos (ex.: período, local, chaves de correlação).
- Resolução de cada caso piloto em objetos de caso do backbone S12:
  - verificação de schema;
  - IDs estáveis;
  - ausência de duplicidade.

**SLIs usados**

- SLI-1 `domain_pilot_coverage` (HARD).  
  Esperado: `= 1.0`.

**Regras PASS / WARN / FAIL**

- **PASS**:
  - `domain_pilot_coverage = 1.0` (6/6 domínios com pelo menos 1 caso piloto);
  - nenhum erro estrutural nos casos piloto.
- **WARN**: não permitido (sem G1 verde, não há piloto multi-domínio).
- **FAIL**:
  - qualquer domínio sem caso piloto;
  - conflitos de ID ou schema inválido.

**Evidência esperada**

- `out/scorecards/S13_G1_pilotos_multi_dominio.json` com SLI-1 e lista de domínios cobertos.
- `out/evidence/S13_G1/pilotos_resolved.json` com todos os casos piloto resolvidos.

---

### 4.3 S13_G2 — Integridade de casos & timeline

**Pergunta-chave**  
"As timelines dos casos piloto, em todos os domínios, são coerentes com as invariantes do backbone de S12?"

**Escopo**

- Para cada caso piloto:
  - montagem da timeline via serviços oficiais (ex.: `timeline_service` existente);
  - verificação de:
    - ordenação temporal;
    - estados válidos em cada evento;
    - ausência de buracos grosseiros (caso 'crítico' sem eventos críticos, estados finais impossíveis, etc.).
- Reaproveitamento dos mesmos validadores de timeline já usados na S12 (especialmente G4).

**SLIs usados**

- SLI-2 `pilot_timeline_integrity_ratio` (HARD).  
  Esperado: `≥ 0.98`.

**Regras PASS / WARN / FAIL**

- **PASS**:
  - `pilot_timeline_integrity_ratio ≥ 0.98`;
  - nenhuma violação fatal (timeline vazia, estado ilegal).
- **WARN**: não permitido.
- **FAIL**:
  - `pilot_timeline_integrity_ratio < 0.98`;
  - qualquer caso piloto com timeline claramente quebrada.

**Evidência esperada**

- `out/scorecards/S13_G2_cases_timeline_multi.json` com SLI-2 e lista de violações.
- `out/evidence/S13_G2/timelines/` com snapshots das timelines dos casos piloto.

---

### 4.4 S13_G3 — Debunker v0 multi-domínio

**Pergunta-chave**  
"O Debunker v0 consegue classificar e explicar os eventos dos 6 domínios piloto com consistência mínima aceitável?"

**Escopo**

- Reuso do serviço `debunker_runner` da S12 para todos os eventos dos casos piloto:
  - decisão (`aceito`, `incerto`, `suspeito`, eventualmente `critico`);
  - explicação curta associada a cada evento crítico.
- Verificar, por domínio:
  - nenhuma sequência obviamente absurda (ex.: tudo aceito em um caso coberto só por fofoca sem fonte oficial);
  - casos "claramente sensíveis" (denúncias fortes, alertas altos, escândalos relevantes) marcados adequadamente.

**SLIs usados**

- SLI-3 `debunker_explanation_coverage` (HARD).  
  Esperado: `≥ 0.95`, ideal 1.0.

**Regras PASS / WARN / FAIL**

- **PASS**:
  - `debunker_explanation_coverage ≥ 0.95`;
  - nenhum domínio com cobertura catastrófica (grande parte dos eventos sem decisão/explicação).
- **WARN**: não permitido.
- **FAIL**:
  - `debunker_explanation_coverage < 0.95`;
  - domínios inteiros sem decisões do Debunker;
  - buracos graves não justificados.

**Evidência esperada**

- `out/scorecards/S13_G3_debunker_multi_dominio.json` com SLI-3.
- `out/evidence/S13_G3/decisions_by_domain/*.json` com decisões por domínio.

---

### 4.5 S13_G4 — Explorer v0 multi-domínio (experiência de consulta)

**Pergunta-chave**  
"O Explorer consegue localizar e abrir corretamente os casos piloto em cada domínio, de maneira reproduzível?"

**Escopo**

- Definição de um roteiro de cenários de teste (ex.: `docs/sprint_13_cenarios_explorer.md`), contendo, para cada domínio:
  - 1+ consultas de entrada (ex.: string de busca, filtros);
  - caso esperado (ID do caso piloto);
  - verificações esperadas (timeline carregada, estado consolidado disponível, etc.).
- Execução automática dos cenários via backend do Explorer.

**SLIs usados**

- SLI-4 `explorer_success_rate` (SOFT).  
  Esperado: `≥ 0.95`, WARN permitido entre 0.90 e 0.95.

**Regras PASS / WARN / FAIL**

- **PASS**:
  - `explorer_success_rate ≥ 0.95`;
  - pelo menos 1 cenário bem-sucedido por domínio.
- **WARN**:
  - `0.90 ≤ explorer_success_rate < 0.95`, com:
    - domínios afetados identificados;
    - problemas registrados no backlog S14.
- **FAIL**:
  - `explorer_success_rate < 0.90`;
  - qualquer domínio sem nenhum cenário bem-sucedido.

**Evidência esperada**

- `out/scorecards/S13_G4_explorer_multi_dominio.json` com SLI-4.
- `out/evidence/S13_G4/queries/*.json` com pedidos/respostas e marcação de sucesso.

---

### 4.6 S13_G5 — Narrativa mínima legível por caso

**Pergunta-chave**  
"Se eu abrir qualquer caso piloto, eu entendo em 1 minuto o que está acontecendo?"

**Escopo**

- Para cada caso piloto, exigir a presença de:
  - título claro e específico;
  - descrição curta (1–3 frases);
  - campo "estado atual" em linguagem humana (não apenas enum);
  - um parágrafo de resumo narrativo (o que é, o que aconteceu, qual a situação atual, qual o ponto de atenção principal).
- A fonte desses textos pode ser:
  - campos em serviços/backend;
  - arquivos markdown em `out/evidence/S13_G5/narrativas/*.md` usados pela UI;
  - ou combinação de ambos, desde que reprodutível.

**SLIs usados**

- SLI-6 `narrative_completeness_ratio` (HARD).  
  Esperado: `= 1.0`.

**Regras PASS / WARN / FAIL**

- **PASS**:
  - `narrative_completeness_ratio = 1.0`;
  - nenhum caso piloto com texto placeholder, vazio ou ininteligível.
- **WARN**: não permitido.
- **FAIL**:
  - qualquer caso piloto sem narrativa mínima completa;
  - presença de textos claramente provisórios ("TODO", "em construção" etc.).

**Evidência esperada**

- `out/scorecards/S13_G5_narrativas_multi_dominio.json` com SLI-6.
- `out/evidence/S13_G5/narrativas/*.md` (uma narrativa por caso piloto).

---

### 4.7 S13_G6 — Feedback & backlog multi-domínio

**Pergunta-chave**  
"Consigo reportar problemas nos casos piloto (em todos os domínios) e ver isso se refletir em um backlog organizado para S14+?"

**Escopo**

- Exercitar o fluxo de feedback (UI + API + painel interno) em todos os domínios piloto:
  - criar feedbacks por caso (ex.: "informação errada", "evento faltando", "fonte quebrada", "dúvida sobre Debunker");
  - listar feedbacks por domínio/caso;
  - atualizar status (aberto, em análise, resolvido, etc.);
  - exportar uma visão agregada em formato de backlog (ex.: `backlog_s14_seed.json`).

**SLIs usados**

- SLI-5 `feedback_delivery_ratio` (SOFT).  
  Esperado: `≥ 0.95`, WARN entre 0.90 e 0.95.

**Regras PASS / WARN / FAIL**

- **PASS**:
  - `feedback_delivery_ratio ≥ 0.95`;
  - todos os domínios com pelo menos 1 feedback registrado e visível.
- **WARN**:
  - `0.90 ≤ feedback_delivery_ratio < 0.95`, com falhas pontuais documentadas e encaminhadas ao backlog S14.
- **FAIL**:
  - `feedback_delivery_ratio < 0.90`;
  - feedbacks não persistidos ou não listáveis no painel interno.

**Evidência esperada**

- `out/scorecards/S13_G6_feedback_multi_dominio.json` com SLI-5.
- `out/evidence/S13_G6/backlog_s14_seed.json` consolidando feedbacks em backlog por domínio.

---

### 4.8 S13_G7 — Observabilidade & consolidação da Sprint 13

**Pergunta-chave**  
"Temos uma fotografia consolidada das métricas e evidências da S13, sem regressão grave em relação à S12?"

**Escopo**

- Ler todos os scorecards S13_G0…S13_G6.
- Comparar SLIs relevantes com baseline de S12 (quando aplicável):
  - integridade de timeline;
  - comportamento do Debunker;
  - fluxo do Explorer;
  - feedback.
- Gerar um snapshot consolidado de S13, contendo:
  - valores de SLI-1…SLI-6;
  - marcação explícita de regressões vs S12 (quando comparável);
  - lista de riscos/débitos técnicos que seguem para S14–S16.

**SLIs usados**

- Reutiliza SLI-1…SLI-6; não define novo SLI.

**Regras PASS / WARN / FAIL**

- **PASS**:
  - nenhuma regressão grave em SLIs HARD;
  - SLIs SOFT dentro ou muito próximos das metas, com justificativas claras.
- **WARN**:
  - pequenas regressões em SLIs SOFT (Explorer/feedback), desde que:
    - documentadas;
    - já mapeadas no backlog de S14.
- **FAIL**:
  - regressão séria em SLI-1, 2, 3 ou 6;
  - ausência de snapshot consolidado.

**Evidência esperada**

- `out/scorecards/S13_G7_observabilidade.json` com resumo dos SLIs.
- `out/evidence/S13_G7/metrics_snapshot.json` com valores consolidados.
- `out/evidence/S13_G7/risks_and_debts.md` com riscos/débitos da sprint.

---

### 4.9 S13_G8 — GO/NO-GO do piloto multi-domínio

**Pergunta-chave**  
"Temos base objetiva suficiente para declarar GO ou NO-GO para o piloto multi-domínio da Sprint 13?"

**Escopo**

- Leitura de todos os scorecards S13_G0…S13_G7.
- Aplicação de regras de decisão usando a classificacão de gates em **HARD** e **SOFT**:
  - Gates **HARD** (não admitem WARN): G0, G1, G2, G3, G5, G6.
  - Gates **SOFT** (podem admitir WARN): G4, G7.

**Regra de decisão sugerida**

- `decision = "GO"` se, e somente se:
  - G0, G1, G2, G3, G5, G6 estiverem com `status = "PASS"`;
  - G4 e G7 estiverem em `status ∈ {"PASS", "WARN"}`;
  - qualquer WARN em G4 ou G7 estiver:
    - documentado;
    - associado a itens explícitos no backlog S14.
- `decision = "NO_GO"` em qualquer outro caso.

**PASS / WARN / FAIL do próprio gate**

- S13_G8 em si é binário quanto à conclusão:
  - `status = "PASS"` indica que o gate conseguiu ler todos os scorecards anteriores e calcular uma decisão consistente (GO ou NO_GO);
  - não existe WARN para S13_G8; a nuance está na própria `decision`.

**Evidência esperada**

- `out/scorecards/S13_G8_decision.json`, contendo no mínimo:
  - `gate = "S13_G8"`;
  - `status = "PASS"` ou mensagem de erro clara;
  - `decision = "GO"` ou `"NO_GO"`;
  - resumo dos gates e SLIs chave usados na decisão.
- `out/evidence/S13_G8/summary.md` com resumo humano:
  - lista de WARNs (se houver);
  - riscos residuais;
  - débitos técnicos encaminhados.

---

## 5) Definition of Done (DoD) da Sprint 13 sob a ótica dos gates

A Sprint 13 só pode ser considerada **DONE** se **todos** os seguintes pontos forem verdadeiros:

1. **Execução completa dos gates**: scripts oficiais (definidos no Cap. 4) para S13_G0…S13_G8 foram executados com sucesso na branch alvo.
2. **Scorecards presentes**: todos os arquivos `out/scorecards/S13_G*_*.json` existem e são coerentes com este capítulo.
3. **Evidências geradas**: as pastas `out/evidence/S13_G*/` contêm os snapshots, dumps, narrativas e backlog descritos nas seções acima.
4. **Decisão formal**: `out/scorecards/S13_G8_decision.json` existe, com `status = "PASS"` e `decision = "GO"`.
5. **Coerência doc ↔ realidade**: os Capítulos 1–4 da S13 estão atualizados e alinhados com o que os gates realmente medem (sem contradições).

Se qualquer um desses pontos falhar, a Sprint 13 **não está concluída**, mesmo que haja uma impressão subjetiva de "quase lá".

---

## 6) Governança de mudanças nos gates da S13

Para evitar que os gates sejam "mexidos" apenas para mascarar problemas, a S13 adota as seguintes regras de governança:

- Este Capítulo 2 é considerado **congelado** a partir do primeiro PASS de S13_G0 na branch de trabalho da sprint.

- Mudanças consideradas **não dramáticas** (não exigem ADR formal):
  - ajustes de texto, ortografia, formatação;
  - inclusão de SLIs adicionais que **não afrouxem** SLOs existentes;
  - clarificações de caminhos de evidência, nomes de arquivos, exemplos.

- Mudanças que exigem **ADR (Architecture Decision Record)**:
  - afrouxar qualquer SLO de SLI marcado como HARD;
  - modificar regras de decisão de S13_G8 (o que é GO vs NO_GO);
  - remover ou fundir gates.

- Mudanças **proibidas** sem ADR forte + consenso:
  - alterar gates apenas para transformar FAIL em PASS sem corrigir o problema subjacente;
  - rebaixar SLIs de HARD para SOFT ou eliminar validações críticas simplesmente porque estão "dando trabalho".

---

## 7) Encadeamento com Capítulos 3 e 4

Com este Capítulo 2, a Sprint 13 passa a ter **um contrato de validação claro**:

- sabemos **o que** precisa ser medido;
- sabemos **quanto** é suficiente para chamar o piloto de GO;
- sabemos **onde** devem existir scorecards e evidências.

O Capítulo 3 vai conectar cada gate a componentes concretos (scripts, serviços, UI, configs, filemap).  
O Capítulo 4 vai transformar esses gates em um plano de execução reprodutível (Codex + CI), com comandos exatos para rodar localmente e em pipeline.

O conjunto Cap. 1–4 garante que a Sprint 13 não seja apenas mais uma ideia de piloto, mas uma **entrega multi-domínio gated, auditável, reprodutível e coerente com a Fase 2 (Sistema de Blocos)** que virá em seguida.

