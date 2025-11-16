# Sprint 6 — Capítulo 4

Inspectah Data Hub Alpha — Execução, Trilhas, Cronologia e Wrap da Sprint 6

---

## 0) Papel deste capítulo

Este Capítulo 4 é o capítulo da **execução** da Sprint 6.

Ele parte de três bases já lockadas:

- Capítulo 1 — objetivo único, pilares P1–P5, contratos e DoR/DoD.
- Capítulo 2 — funil de validação S6‑G0…S6‑G8 e lógica GO/NO‑GO.
- Capítulo 3 — filemap oficial da Sprint 6 (onde cada artefato vive).

Com isso, Capítulo 4 responde a quatro perguntas práticas:

1. **Como** o trabalho da Sprint 6 é organizado em trilhas (threads) ao longo do tempo.
2. **Quando** cada gate S6‑G0…S6‑G8 deve ser atacado e estabilizado.
3. **O que** humanos e Codex fazem no dia a dia para empurrar o Inspectah até o Alpha.
4. **Como** registrar o wrap final da sprint (história da execução, evidências e lições aprendidas) usando os artefatos do filemap.

Capítulo 4 é, ao mesmo tempo:

- plano de execução (antes da sprint);
- trilha de navegação (durante a sprint);
- estrutura de wrap (depois da sprint).

---

## 1) Visão geral da execução da Sprint 6

A Sprint 6 tem um objetivo único: deixar o **Inspectah Data Hub Alpha utilizável** para um domínio real, com fontes declaradas, modelo canônico, coleta com evidência, consulta consolidada, observabilidade mínima e bundle S6 reprodutível.

Em termos de execução, isso significa:

- materializar os pilares P1–P5 em código, scripts e dados;
- fazer com que todos os gates S6‑G0…S6‑G8 passem em `PASS` (ou `GO` no caso de S6‑G8);
- deixar o filemap do Capítulo 3 completamente preenchido com arquivos reais;
- capturar a história da sprint (decisões, reworks, riscos) de forma que alguém consiga entender, ao ler este capítulo + scorecards + evidências, **como** o Alpha nasceu.

A execução é organizada em **trilhas (threads)** e **fases cronológicas**, com checkpoints claros. Ao longo do texto, sempre que uma ação for citada, ela será amarrada a:

- um ou mais pilares P1–P5;
- um ou mais gates S6‑G0…S6‑G8;
- caminhos específicos do filemap.

---

## 2) Trilhas de trabalho (Threads) da Sprint 6

A Sprint 6 é organizada em seis trilhas principais, que podem avançar em paralelo respeitando dependências:

- T‑A — Domínio & Sources Hardening (P1, S6‑G0, S6‑G1)
- T‑B — Modelo Canônico & Field Designer (P2, S6‑G2)
- T‑C — Coleta & Evidence Vault (P3, S6‑G3)
- T‑D — Explore & Verify & Jornada do Operador (P4, S6‑G4)
- T‑E — Observabilidade & Bundle S6 (P5, S6‑G5, S6‑G6)
- T‑F — Guardas, CI & GO/NO‑GO (integração de tudo, S6‑G7, S6‑G8)

Cada trilha é descrita abaixo com:

- objetivo;
- dependências;
- principais blocos de trabalho;
- relação com gates e filemap.

### 2.1. T‑A — Domínio & Sources Hardening

Objetivo:

- Fixar o domínio piloto;
- solidificar o Source Registry v0.

Dependências:

- Capítulos 1–3 lockados.

Blocos principais:

1. Finalizar `docs/sprint_6/dominio_piloto.md` com domínio e fontes essenciais.
2. Modelar definitivamente `config/sources/fonte_a.yaml`, `fonte_b.yaml`, `fonte_c.yaml`.
3. Implementar `bin/inspectah_sources_validate.sh`.
4. Implementar e estabilizar `bin/s6_g0_domain_setup.sh` e `bin/s6_g1_sources_registry.sh`.

Gates e filemap:

- S6‑G0 e S6‑G1 devem atingir `PASS` antes de qualquer expansão maior nas outras trilhas.
- Áreas afetadas: `docs/sprint_6/`, `config/sources/`, `bin/inspectah_sources_validate.sh`, `bin/s6_g0_domain_setup.sh`, `bin/s6_g1_sources_registry.sh`, `out/scorecards/S6_G0_*`, `out/scorecards/S6_G1_*`, evidências correspondentes.

### 2.2. T‑B — Modelo Canônico & Field Designer

Objetivo:

- Criar o modelo canônico do domínio piloto;
- garantir que fontes conseguem preencher os campos essenciais.

Dependências:

- T‑A pelo menos com S6‑G1 em `PASS` (ou `WARN` aceitável).

Blocos principais:

1. Consolidar `config/fields/dominio_piloto.yaml` com campos obrigatórios e opcionais.
2. Implementar `bin/inspectah_fields_preview.sh` para amostras.
3. Implementar `bin/s6_g2_field_designer.sh` para consolidar cobertura e emitir scorecard.

Gates e filemap:

- S6‑G2 deve atingir `PASS` antes de investir pesado em coleta (T‑C).
- Áreas afetadas: `config/fields/`, `bin/inspectah_fields_preview.sh`, `bin/s6_g2_field_designer.sh`, `out/scorecards/S6_G2_*`, `out/evidence/S6_G2_*`.

### 2.3. T‑C — Coleta & Evidence Vault

Objetivo:

- Construir o pipeline de coleta;
- materializar o contrato de evidência (P3) em `out/evidence/dominio_piloto/...`.

Dependências:

- T‑A (sources válidas);
- T‑B (modelo canônico funcional).

Blocos principais:

1. Desenhar estrutura definitiva de evidência (dirs + manifest).
2. Implementar `bin/inspectah_collect_once.sh dominio_piloto`.
3. Garantir dedupe e imutabilidade na prática.
4. Implementar `bin/s6_g3_collect_evidence.sh` e consolidar scorecard de G3.

Gates e filemap:

- S6‑G3 deve atingir `PASS` antes que se considere o Alpha utilizável.
- Áreas afetadas: `bin/inspectah_collect_once.sh`, `out/evidence/dominio_piloto/...`, `bin/s6_g3_collect_evidence.sh`, `out/scorecards/S6_G3_*`.

### 2.4. T‑D — Explore & Verify & Jornada do Operador

Objetivo:

- Transformar a evidência bruta e registros canônicos em experiência real de consulta (P4);
- fazer o filme do operador do Capítulo 1 funcionar ponta a ponta.

Dependências:

- T‑C com coleta mínima já funcionando.

Blocos principais:

1. Implementar `bin/inspectah_query.sh` com filtros, paginação e exports.
2. Implementar `bin/inspectah_show_evidence.sh` para navegação item → evidência.
3. Implementar `bin/s6_g4_explore_verify.sh` e scorecard.

Gates e filemap:

- S6‑G4 deve atingir `PASS` antes de declarar que o Inspectah Alpha é utilizável para humanos.
- Áreas afetadas: `bin/inspectah_query.sh`, `bin/inspectah_show_evidence.sh`, `out/queries/`, `bin/s6_g4_explore_verify.sh`, `out/scorecards/S6_G4_*`.

### 2.5. T‑E — Observabilidade & Bundle S6

Objetivo:

- Garantir métricas mínimas de operação (P5);
- construir o bundle S6 como snapshot reprodutível da sprint.

Dependências:

- T‑C e T‑D com G3 e G4 em estado avançado.

Blocos principais:

1. Instrumentar métricas essenciais (latência, volume, falhas, frescor).
2. Implementar `bin/inspectah_metrics_snapshot.sh` e `bin/s6_g5_metrics_obs.sh`.
3. Implementar `bin/inspectah_s6_build_bundle.sh`, `bin/inspectah_s6_verify_bundle.sh` e `bin/s6_g6_bundle_repro.sh`.

Gates e filemap:

- S6‑G5 e S6‑G6 devem atingir `PASS` antes de considerar a S6 encerrada.
- Áreas afetadas: `bin/inspectah_metrics_snapshot.sh`, `bin/s6_g5_metrics_obs.sh`, `bin/inspectah_s6_build_bundle.sh`, `bin/inspectah_s6_verify_bundle.sh`, `bin/s6_g6_bundle_repro.sh`, `out/s6_bundle/`, scorecards/evidências de G5 e G6.

### 2.6. T‑F — Guardas, CI & GO/NO‑GO

Objetivo:

- Automatizar o funil essencial de validação da S6;
- produzir o veredito final de sprint (GO/NO‑GO).

Dependências:

- T‑A…T‑E em estágio maduro.

Blocos principais:

1. Implementar `bin/inspectah_s6_guard.sh` (encadeia G1…G4).
2. Implementar `bin/s6_g7_guard_automation.sh`.
3. Integrar `inspectah_s6_guard.sh` em CI (se aplicável).
4. Implementar `bin/s6_g8_sprint_go_no_go.sh` e produzir scorecard final + summary.

Gates e filemap:

- S6‑G7 precisa estar em `PASS` antes de qualquer discurso de “estabilidade”.
- S6‑G8 é o gate que oficializa o encerramento da S6.

---

## 3) Fases cronológicas da Sprint 6

Sem amarrar a datas de calendário específicas, a S6 é dividida em seis fases lógicas:

- F1 — Fundamentos (G0, G1)
- F2 — Modelo Canônico (G2)
- F3 — Coleta & Evidência (G3)
- F4 — Explore & Verify (G4)
- F5 — Observabilidade & Bundle (G5, G6)
- F6 — Guards & GO/NO‑GO (G7, G8)

### 3.1. F1 — Fundamentos (G0, G1)

Objetivo:

- Deixar domínio, docs e fontes em estado sólido.

Condições de saída:

- `docs/sprint_6/sprint_6_capitulo_1.md`, `sprint_6_capitulo_2.md`, `sprint_6_capitulo_3.md` e `dominio_piloto.md` presentes e estáveis.
- `config/sources/fonte_a.yaml`, `fonte_b.yaml`, `fonte_c.yaml` implementados na primeira versão.
- S6‑G0 e S6‑G1 em `PASS`.

### 3.2. F2 — Modelo Canônico (G2)

Objetivo:

- Consolidar o Field Designer v0.

Condições de saída:

- `config/fields/dominio_piloto.yaml` estável.
- `bin/inspectah_fields_preview.sh` funcionando com amostras reais.
- S6‑G2 em `PASS` com cobertura aceitável dos campos obrigatórios.

### 3.3. F3 — Coleta & Evidência (G3)

Objetivo:

- Fazer o pipeline de coleta escrever evidência real com contrato sólido.

Condições de saída:

- `bin/inspectah_collect_once.sh dominio_piloto` executa de ponta a ponta.
- `out/evidence/dominio_piloto/...` contém pacotes de evidência reais.
- S6‑G3 em `PASS` sem violações de imutabilidade/dedupe.

### 3.4. F4 — Explore & Verify (G4)

Objetivo:

- Tornar o Alpha utilizável via CLI (filme do operador funcionando).

Condições de saída:

- `bin/inspectah_query.sh` lista, filtra, pagina e exporta.
- `bin/inspectah_show_evidence.sh` navega de um resultado até o pacote de evidência.
- S6‑G4 em `PASS`.

### 3.5. F5 — Observabilidade & Bundle (G5, G6)

Objetivo:

- Garantir que o Alpha é monitorável e reprodutível.

Condições de saída:

- Métricas essenciais disponíveis e snapshot capturado (`bin/inspectah_metrics_snapshot.sh`).
- S6‑G5 em `PASS`.
- `out/s6_bundle/` gerado e verificado por `inspectah_s6_verify_bundle.sh`.
- S6‑G6 em `PASS`.

### 3.6. F6 — Guards & GO/NO‑GO (G7, G8)

Objetivo:

- Automatizar checks essenciais;
- emitir veredito final da sprint.

Condições de saída:

- `bin/inspectah_s6_guard.sh` confiável, rodando em ambiente limpo.
- S6‑G7 em `PASS`.
- `bin/s6_g8_sprint_go_no_go.sh` executado com scorecard final `S6_G8_sprint_go_no_go.json`.
- `status` de S6‑G8 em `GO`.

---

## 4) Rotina diária de execução (Humanos + Codex)

Esta seção descreve uma rotina diária idealizada durante a Sprint 6, sem datas específicas. O objetivo é maximizar alinhamento com P1–P5, gates e filemap.

### 4.1. Ritual de início de dia

1. Abrir `docs/sprint_6/sprint_6_capitulo_1.md` e `sprint_6_capitulo_2.md` para relembrar objetivo único e estado desejado de gates.
2. Conferir estado atual dos scorecards em `out/scorecards/` (quais gates já estão em `PASS`, quais ainda não existem).
3. Escolher uma trilha T‑A…T‑F como foco principal do dia (no máximo duas trilhas ativas por dia para evitar dispersão).

### 4.2. Bloco de implementação com o Codex

1. Traduzir trechos deste capítulo (trilha e fase alvo) em prompts de implementação para o Codex.
2. Codex cria/ajusta scripts em `bin/`, `config/`, etc., sempre respeitando nomes e caminhos do filemap.
3. Humanos revisam scripts gerados, ajustam detalhes, escrevem comentários mínimos quando necessário.

### 4.3. Bloco de validação via gates

1. Após qualquer ajuste relevante, rodar o gate correspondente (por exemplo, mexeu em fontes → rodar `bin/s6_g1_sources_registry.sh`).
2. Verificar se scorecards e evidências foram atualizados corretamente.
3. Se gate falhar, tratar a falha como **evento de estudo**, não como ruído: registrar o motivo em commit/PR e, se necessário, em `docs/sprint_6/sprint_6_capitulo_4.md`.

### 4.4. Bloco de estabilização e limpeza

1. Garantir que `git status` continue limpo fora dos arquivos que estão em desenvolvimento.
2. Consolidar commits pequenos em commits significativos por trilha/gate.
3. Atualizar, quando fizer sentido, seções de execução/wrap deste próprio capítulo.

### 4.5. Ritual de fim de dia

1. Rodar `bin/inspectah_s6_guard.sh` (ou parte dele) como check rápido do estado de saúde da sprint.
2. Registrar em poucas linhas (em `sprint_6_capitulo_4.md` ou outro doc auxiliar) quais gates andaram e quais riscos emergiram.

---

## 5) Checkpoints obrigatórios da Sprint 6

A execução da S6 é balizada por quatro checkpoints principais:

- C1 — Fundamentos bloqueados (F1 concluída)
- C2 — Modelo + Fontes integrados (F2 concluída)
- C3 — Filme do operador rodando (F3 + F4 concluídas)
- C4 — Observabilidade + Bundle + Guard (F5 + F6 concluídas)

### 5.1. C1 — Fundamentos bloqueados

Condição para marcar C1:

- S6‑G0 e S6‑G1 em `PASS`;
- `docs/sprint_6/dominio_piloto.md` e configs de fonte considerados estáveis.

### 5.2. C2 — Modelo + Fontes integrados

Condição para marcar C2:

- S6‑G2 em `PASS`;
- `config/fields/dominio_piloto.yaml` estável;
- fontes da T‑A e campos da T‑B funcionando juntos.

### 5.3. C3 — Filme do operador rodando

Condição para marcar C3:

- S6‑G3 e S6‑G4 em `PASS`;
- `bin/inspectah_collect_once.sh`, `inspectah_query.sh` e `inspectah_show_evidence.sh` funcionando em fluxo contínuo;
- operador consegue executar o cenário do filme do Capítulo 1 sem hacks.

### 5.4. C4 — Observabilidade + Bundle + Guard

Condição para marcar C4:

- S6‑G5, S6‑G6 e S6‑G7 em `PASS`;
- `out/s6_bundle/` gerado e verificado;
- `bin/inspectah_s6_guard.sh` rodando com confiança;
- S6‑G8 já executado pelo menos uma vez em modo ensaio geral (mesmo que o veredito final ainda vá ser emitido apenas no fim da sprint).

---

## 6) Gestão de riscos durante a S6

A execução da Sprint 6 deve ser conduzida com algumas decisões explícitas de gestão de risco:

1. **Risco de escopo difuso**
   - Mitigação: qualquer tarefa que não se mapeie claramente para P1–P5, para uma trilha T‑A…T‑F ou para um gate S6‑G* deve ser questionada e, em caso de dúvida, descartada ou adiada.

2. **Risco de filemap divergente da realidade**
   - Mitigação: toda vez que um artefato novo se torna essencial, o Capítulo 3 deve ser atualizado; se o time sentir que "algo importante" não aparece no filemap, isso é sinal de dívida técnica de documentação.

3. **Risco de gates ignorados**
   - Mitigação: nenhuma entrega é considerada "pronta" sem passar pelo gate correspondente (por exemplo, fontes sem S6‑G1 em `PASS` não são fontes prontas).

4. **Risco de bundle incompleto**
   - Mitigação: `inspectah_s6_build_bundle.sh` e `inspectah_s6_verify_bundle.sh` devem ser rodados mais de uma vez durante a sprint, não só na última semana.

5. **Risco de regressões silenciosas**
   - Mitigação: uso disciplinado do `inspectah_s6_guard.sh` e, se possível, integração em CI.

---

## 7) Estrutura de wrap final da Sprint 6

Ao final da sprint, este próprio `sprint_6_capitulo_4.md` deve ser enriquecido com um wrap da execução. A estrutura sugerida é:

1. **Resumo executivo da S6**
   - 3–5 parágrafos explicando o que foi entregue, que domínio foi coberto, cómo está a usabilidade do Alpha e qual é o veredito final (GO/NO‑GO, conforme S6‑G8).

2. **Linha do tempo de gates**
   - Pequeno quadro ou parágrafo listando quando cada gate S6‑G0…S6‑G8 atingiu `PASS`/`GO` pela primeira vez.

3. **Trilhas — o que funcionou bem, o que doeu**
   - 1–2 parágrafos por trilha T‑A…T‑F, destacando decisões certas, erros, refactors importantes e dívidas que ficaram para sprints futuras.

4. **Métricas chave da S6**
   - Ponto a ponto com:
     - número de fontes do domínio piloto ativas;
     - volume de evidência coletada;
     - latências típicas (quando disponíveis);
     - estado do bundle (tamanho, tempo para rodar verificação).

5. **Lições aprendidas e impacto nos próximos passos**
   - Conectar com as próximas sprints: o que a S6 ensinou sobre domains, fontes, field design, evidência, consulta, observabilidade e automação.

O arquivo `docs/sprint_6/sprint_6_resultados.md` pode ser usado como versão condensada e executiva desses pontos, apontando para este Capítulo 4 e para os scorecards.

---

## 8) Critério de excelência da execução (20/10)

A execução da Sprint 6 será considerada no nível máximo (20/10) se, ao final:

1. **Alinhamento total com os capítulos anteriores**  
   - Capítulos 1–3 permanecem corretos quando confrontados com a realidade do repositório, dos scorecards e dos bundles.
   - Não existe divergência entre o que os capítulos prometem e o que `config/`, `bin/` e `out/` mostram.

2. **Gates e filemap 100% coerentes**  
   - Todos os gates S6‑G0…S6‑G7 em `PASS` e S6‑G8 em `GO`.  
   - Todos os caminhos citados no filemap do Capítulo 3 existem, com o tipo de artefato esperado (config, script, scorecard, evidência, bundle).

3. **História reconstituível**  
   - A partir deste Capítulo 4, dos scorecards, das evidências e do bundle, um terceiro não envolvido consegue reconstruir a história da Sprint 6: o que foi feito, em que ordem, por quê e com quais riscos.  
   - A linha do tempo de quando cada gate atingiu `PASS`/`GO` pode ser deduzida de commits, scorecards e, se necessário, anotações em `sprint_6_capitulo_4.md` e `sprint_6_resultados.md`.

4. **Operabilidade real do Alpha**  
   - Um operador consegue, apenas com `docs/sprint_6/`, `bin/inspectah_*.sh`, `bin/s6_g*.sh` e as pastas `out/`, usar o Inspectah como hub de dados do domínio piloto (consultar, ver evidência, entender estado de saúde e, se necessário, restaurar a partir do bundle S6).  
   - O "filme do operador" do Capítulo 1 funciona exatamente como descrito, sem passos secretos.

5. **Base sólida para as próximas sprints**  
   - O time sente que pode expandir domínios, tipos de fonte e profundidade de análise sem precisar refazer o alicerce construído na S6.  
   - Sprints seguintes (S7, S8, …) conseguem usar o filemap, os scripts e os bundles da S6 como base sem ajustes dolorosos.

Quando estes cinco pontos forem verdade, a Sprint 6 terá cumprido seu papel: transformar o Inspectah em um **Alpha utilizável, observável e reprodutível**, pronto para ser ampliado nas próximas fases.

---

## 9) Playbook operacional por gate (execução concreta)

Esta seção traduz a visão de execução em uma forma mais "clicável": para cada gate, quando ele entra em cena e o que fazer na prática.

### 9.1. S6‑G0 — Domínio & Setup

**Quando usar:**
- Início da sprint;
- após mudanças relevantes em `docs/sprint_6/` ou `dominio_piloto.md`.

**Passos práticos:**
1. Garantir que Capítulos 1–3 e `dominio_piloto.md` estão atualizados.  
2. Rodar `bin/s6_g0_domain_setup.sh`.  
3. Verificar `out/scorecards/S6_G0_domain_setup.json` e `out/evidence/S6_G0_domain_setup/`.  
4. Se `status != PASS`, corrigir problemas de docs ou estado do repo e repetir.

### 9.2. S6‑G1 — Source Registry v0

**Quando usar:**
- Sempre que algum `config/sources/fonte_*.yaml` for alterado.

**Passos práticos:**
1. Ajustar YAMLs de fonte conforme necessário.  
2. Rodar `bin/s6_g1_sources_registry.sh`.  
3. Conferir se amostras em `out/evidence/S6_G1_sources_registry/` fazem sentido.  
4. Se `status: FAIL`, priorizar correção da fonte antes de tocar em coleta ou fields.

### 9.3. S6‑G2 — Field Designer v0

**Quando usar:**
- Sempre que `config/fields/dominio_piloto.yaml` for alterado;
- antes de mexer pesado na coleta.

**Passos práticos:**
1. Ajustar campos no `dominio_piloto.yaml`.  
2. Rodar `bin/s6_g2_field_designer.sh`.  
3. Analisar amostras canônicas em `out/evidence/S6_G2_field_designer/`.  
4. Se campos obrigatórios continuam vazios, ajustar mapeamentos até `PASS`.

### 9.4. S6‑G3 — Coleta & Evidence Vault

**Quando usar:**
- Após qualquer mudança relevante em coleta ou layout de evidência;
- periodicamente, para testar saúde da coleta.

**Passos práticos:**
1. Rodar `bin/s6_g3_collect_evidence.sh` (que chama `inspectah_collect_once.sh`).  
2. Inspecionar novos pacotes em `out/evidence/dominio_piloto/...`.  
3. Verificar scorecard `S6_G3_collect_evidence.json`.  
4. Se surgirem duplicatas, pacotes quebrados ou ausência de evidência, tratar como regressão séria.

### 9.5. S6‑G4 — Explore & Verify

**Quando usar:**
- Após mudanças em consultas, filtros, exports ou navegação de evidência;
- como teste funcional do "filme do operador".

**Passos práticos:**
1. Rodar `bin/s6_g4_explore_verify.sh`.  
2. Conferir exports em `out/queries/` e navegar para evidência com `inspectah_show_evidence.sh`.  
3. Validar se o fluxo consulta → item → evidência está íntegro.  
4. Corrigir qualquer quebra de ponte e repetir.

### 9.6. S6‑G5 — Métricas & Observabilidade

**Quando usar:**
- Após instrumentar/alterar métricas;
- próximo ao fechamento da sprint.

**Passos práticos:**
1. Rodar `bin/s6_g5_metrics_obs.sh`.  
2. Conferir snapshots em `out/evidence/S6_G5_metrics_obs/`.  
3. Verificar se métricas essenciais (latência, volume, falhas, frescor) existem e fazem sentido.  
4. Se estiver "cego" em algum aspecto essencial, priorizar instrumentação antes de seguir.

### 9.7. S6‑G6 — Bundle & Reprodutibilidade

**Quando usar:**
- Pelo menos duas vezes: ensaio geral no meio/fim da sprint e no fechamento final.

**Passos práticos:**
1. Rodar `bin/s6_g6_bundle_repro.sh`.  
2. Conferir se `out/s6_bundle/` foi gerado/atualizado.  
3. Validar o log de verificação em `out/evidence/S6_G6_bundle_repro/`.  
4. Se o verificador falhar, tratar o bundle como inválido até corrigir.

### 9.8. S6‑G7 — Guards automatizados

**Quando usar:**
- Sempre que gates essenciais forem considerados estáveis;
- em rodadas de sanity check diárias ou de CI.

**Passos práticos:**
1. Rodar `bin/s6_g7_guard_automation.sh` (que chama `inspectah_s6_guard.sh`).  
2. Conferir `S6_G7_guard_automation.json` e evidências.  
3. Se falhar, abrir o log e identificar em qual gate encadeado houve problema.  
4. Corrigir gate base e repetir.

### 9.9. S6‑G8 — GO/NO‑GO da Sprint 6

**Quando usar:**
- No ensaio geral (final da fase F6);
- no fechamento oficial da sprint.

**Passos práticos:**
1. Confirmar que todos os gates S6‑G0…S6‑G7 foram executados recentemente.  
2. Rodar `bin/s6_g8_sprint_go_no_go.sh`.  
3. Ler `out/scorecards/S6_G8_sprint_go_no_go.json` e `out/evidence/S6_G8_sprint_go_no_go/summary.md`.  
4. Se `status: "NO_GO"`, usar o próprio summary para definir plano de correção ou aceitar conscientemente que a sprint não está pronta.

---

## 10) Tratamento de falhas e "rollback leve" por gate

Falhas de gate são parte normal da Sprint 6. Este capítulo define um padrão explícito de reação:

1. **Nunca mascarar falhas**  
   - É proibido editar scorecards manualmente para forçar `PASS`. Scorecards devem sempre ser produto dos scripts `bin/s6_g*.sh`.

2. **Reação padrão ao `FAIL`**  
   - Identificar o artefato diretamente ligado ao gate (YAML, script, layout de evidência, consulta, métrica, etc.).  
   - Reverter o último conjunto de mudanças que o afetou (via `git`), ou ajustar a implementação até que o gate volte a `PASS`.  
   - Reexecutar o gate e registrar mentalmente (ou em nota de wrap) a causa raiz principal.

3. **Rollback leve vs. redesign**  
   - Se a falha surgiu de um ajuste recente, preferir rollback leve (voltar para o estado anterior conhecido como bom).  
   - Se a falha expõe algo estrutural (por exemplo, modelo canônico irrealista), considerar um mini-redesign deliberado, com atualização dos Capítulos 1–3.

4. **Falhas em cadeia via guard**  
   - Se S6‑G7 falhar, usar os logs para descobrir qual gate encadeado quebrou.  
   - Corrigir o gate base e só então voltar a rodar o guard.

5. **Falhas recorrentes**  
   - Se o mesmo gate falha repetidas vezes pelo mesmo motivo, registrar essa recorrência na seção de lições aprendidas de `sprint_6_capitulo_4.md`.

---

## 11) Storyboard Execução ↔ Scorecards ↔ Bundle

Para deixar a história da S6 totalmente reconstituível, recomenda-se a seguinte amarração prática:

1. **Linha do tempo em `sprint_6_capitulo_4.md`**  
   - Manter, ao longo da sprint, uma mini linha do tempo textual (sem datas rígidas, se preferir):  
     - "Dia X: S6‑G1 passou com PASS pela primeira vez. Ajustamos fonte_b.yaml para…"  
     - "Dia Y: S6‑G3 começou a falhar por causa de…" etc.

2. **Marcos via scorecards**  
   - Cada vez que um gate mudar de status de `FAIL`/`WARN` para `PASS` pela primeira vez, opcionalmente marcar esse commit ou PR com uma mensagem padronizada (ex.: `S6-G3: first PASS`).

3. **Snapshots via bundle S6**  
   - Em momentos chave (por exemplo C3 e C4), rodar `s6_g6_bundle_repro.sh` e anotar em `sprint_6_resultados.md` quais bundles correspondem a quais marcos ("Bundle #1 — pré G4 PASS", "Bundle #2 — pós C4", etc.).

4. **Conexão com lições aprendidas**  
   - Quando uma falha de gate gerar uma lição importante (por exemplo, sobre desenho de campos, dedupe ou métrica), registrar o episódio em `sprint_6_capitulo_4.md` com referência ao scorecard e, se útil, ao commit/bundle.

Com esse storyboard leve, a Sprint 6 vira uma narrativa auditável: não só sabemos como o Alpha ficou, mas também **como ele chegou lá**.

---

## 12) Como este capítulo deve ser usado

- **Antes da sprint**: como plano de ataque — escolher trilhas, entender fases F1…F6, preparar estrutura de checkpoints C1…C4 e alinhar expectativas de excelência.  
- **Durante a sprint**: como guia operacional diário — decidir qual trilha atacar, quais gates rodar em seguida, como reagir a falhas e quando gerar bundles parciais.  
- **Depois da sprint**: como espinha dorsal do wrap — preencher a seção de linha do tempo, trilhas, métricas e lições aprendidas, amarrando sempre scorecards, evidências e bundles.

Com o Capítulo 4 nesta forma, a Sprint 6 deixa de ser apenas uma lista de entregas e passa a ser um **roteiro operacional completo**: do objetivo ao GO/NO‑GO, do primeiro YAML de fonte ao bundle final, com espaço explícito para registrar como o Inspectah Data Hub Alpha evoluiu ao longo do caminho.