# Inspectah — Sprint 16  
## Capítulo 1 — Contexto, Visão e Objetivos (Hardening do Sistema de Blocos)

### 0. Papel deste capítulo

Este capítulo define **o que é** e **para que existe** a Sprint 16 do Inspectah.

Ele consolida, em linguagem operacional:

- o contexto pós‑Sprint 15 (estado atual do Sistema de Blocos e da camada de blindagem);
- a visão da Sprint 16 (hardening + Threat Model sério, mas focado);
- os objetivos gerais e específicos da sprint;
- o que entra e o que fica explicitamente fora de escopo;
- os entregáveis esperados e a Definição de Pronto (DoD);
- os principais riscos e hipóteses de trabalho.

Os Capítulos 2, 3 e 4 da S16 vão transformar esta visão em:

- gates e critérios de qualidade (Cap. 2);
- filemap/arquitetura, contratos de layout e caminhos oficiais (Cap. 3);
- runbook operacional + superprompts para Codex (Cap. 4).

Aqui, o foco é alinhar **intenção, ambição e limites da S16** — sem ainda entrar em detalhes de scripts, nomes de arquivos ou pipelines.

---

### 1. Contexto: onde estamos após a Sprint 15

Ao final da Sprint 15, o repositório Inspectah em `/Users/gustavoschneiter/Documents/Inspectah` está ancorado no commit:

- `47dfa5bc4538f501b382be59a209231f117fde00` (branch `main`),
- com `PYTHONPATH=. bin/s15_all_gates.sh` rodando T0–T8 em estado PASS/GO,
- e o adendo de ORR da S15 registrado em `docs/sprint_15_orr_summary.md`, com scorecards/evidências em `out/`.

Do ponto de vista funcional, temos:

1. **Sistema de Blocos (S13–S14) em pé**  
   - Modelo de Truth‑DB consolidado: blocos, sub‑blocos, componentes, histórico de eventos e disputas;  
   - Write path estruturado, com fluxos claros para cadastro, contestação e resolução;  
   - Invariantes mínimos já garantidos pelos gates das sprints anteriores.

2. **Camada de inteligência & blindagem entregue na S15**  
   - **Debunker v1** (`inspectah/debunker/*`): motor cético com classificação de risco por domínio, fixtures dedicadas e runner offline (scripts `s15_*` + `bin/s15_t2_debunker_offline.sh`).  
   - **Comitês V1/V2/V3** (`inspectah/committees/*`):  
     - V1 mecânico (check de estrutura, invariantes, integridade);  
     - V2 multi‑brain (inclui Promotores do Diabo, usa relatórios do Debunker);  
     - V3 coerência global (evita estados impossíveis e decisões contraditórias).  
   - **Âncoras em blockchain** (`inspectah/anchors/*` integradas a `inspectah/blocks/__init__.py`):  
     - construção de Merkle, batching, envio a chain e registry interno de âncoras;  
     - ponte entre fatos/versões e âncoras externas.  
   - **Anti‑canetada** (`inspectah/commands/__init__.py`):  
     - write path blindado contra overrides diretos;  
     - pedidos de "canetada" viram eventos/disputas rastreáveis.  
   - Gates T0–T8 da S15 (`bin/s15_t0_sanity.sh`…`bin/s15_t8_go_no_go.sh` + `bin/s15_all_gates.sh`) e workflows `.ci/sprint_15_gates.yml` e `.ci/sprint_15_nightly.yml`.

3. **Observabilidade mínima para acompanhar a S15**  
   - T6 da S15 gera scorecards/evidências sobre Debunker, comitês, âncoras e overrides;  
   - já existe material suficiente para investigar incidentes básicos e fazer troubleshooting.

Em resumo: a S15 instalou um **primeiro sistema imunológico** em cima do Sistema de Blocos. A Sprint 16 não é sobre adicionar novos órgãos; é sobre **testar, atacar e endurecer o sistema imunológico que já existe**, até entendermos com clareza seus limites e pontos de quebra.

---

### 2. Visão da Sprint 16

A Sprint 16 é a sprint de **hardening e Threat Model do Sistema de Blocos + camada de blindagem da S15**.

Visão em uma frase:

> A Sprint 16 transforma o conjunto “Sistema de Blocos + Debunker v1 + Comitês V1/V2/V3 + Âncoras + Anti‑canetada” de um estado **corretamente implementado** para um estado **defensável, auditável e difícil de quebrar**, com evidências concretas dos seus limites e ameaças.

Na prática, isso significa:

- desenhar e documentar um **Threat Model explícito** dessa pilha (S13–S15);  
- criar **testes de ataque, stress e caos** que exercitem esse modelo de ameaças de forma reprodutível;  
- expor **fraquezas reais** (não cosméticas) e tratá‑las com priorização clara;  
- fechar um **ORR focado em segurança, robustez e sanidade**, e não apenas em funcionalidade.

A S16 é menos sobre "fazer coisas novas" e mais sobre **não deixar o que já existe nos envergonhar quando for pressionado**.

---

### 3. Objetivo geral e objetivos específicos

#### 3.1 Objetivo geral

> **Objetivo geral da Sprint 16:**  
> Demonstrar, com evidências reproduzíveis, que o Sistema de Blocos + camada de blindagem da S15 consegue resistir a um conjunto representativo de ameaças plausíveis (técnicas e de processo), com comportamento previsível e mecanismos de detecção, contenção e recuperação compreensíveis.

#### 3.2 Objetivos específicos

1. **Threat Model formal da pilha S13–S15**  
   - Identificar atores e adversários relevantes (internos, externos, desatentos, maliciosos).  
   - Mapear ativos críticos (verdades consolidadas, blocos de alto impacto, âncoras, decisões de comitês, logs/scorecards).  
   - Mapear vetores de ataque principais (spoofing de fontes, envenenamento de dados, captura de comitês, manipulação de âncoras, bypass de anti‑canetada, falhas de observabilidade).  
   - Registrar tudo em documento versionado (por exemplo, `docs/sprint_16_threat_model.md`), com links para módulos e scripts.

2. **Testes de ataque e stress em cenários chave**  
   - Criar cenários artificiais e semi‑reais alinhados às ameaças do modelo;  
   - Implementar scripts de ataque controlados (ex.: flood de disputas, inputs adversariais para Debunker, conflitos deliberados de blocos, chain offline ou instável, tentativas insistentes de override);  
   - Conectar esses cenários a gates da S16 (principalmente T3/T4/T5/T6) para rodar de forma reprodutível.

3. **Hardening da camada de Debunker e comitês**  
   - Ajustar thresholds, políticas e invariantes do Debunker v1 com base nos resultados dos ataques;  
   - Reforçar regras de V1/V2/V3 para reduzir caminhos de “captura” ou decisões sem explicação;  
   - Garantir que decisões de alto impacto deixem sempre uma trilha auditável (logs estruturados, evidências, scorecards).

4. **Hardening de âncoras e anti‑canetada**  
   - Simular indisponibilidade de chain, latência alta, custos altos e reorgs plausíveis;  
   - Avaliar se o sistema se mantém íntegro com âncoras atrasadas ou temporariamente indisponíveis;  
   - Testar fluxos de override (legal/administrativo) para garantir que nenhum passa “por fora” da trilha de eventos/disputas.

5. **ORR final focado em segurança e resiliência**  
   - Definir gates da S16 (T0–T8) alinhados ao Threat Model;  
   - Rodar ORR com perspectiva de "time de segurança" (não só "time de feature");  
   - Produzir um `docs/sprint_16_orr_summary.md` que responda claramente:  
     - o que o sistema aguenta;  
     - o que ele não aguenta;  
     - em quais condições a solução quebra e como isso é observado.

---

### 4. Escopo da Sprint 16

A Sprint 16 cobre **principalmente**:

1. **Modelagem de ameaças (Threat Modeling)**  
   - Documento explícito de Threat Model para Sistema de Blocos + Debunker + Comitês + Âncoras + Anti‑canetada;  
   - Classificação de ameaças por impacto/probabilidade (sem dogma, mas com rigor de engenharia).

2. **Testes adversariais e de stress**  
   - Criação de cenários de ataque e scripts correspondentes, com parametrização simples;  
   - Integração desses cenários em gates da S16 (T3–T6) e, quando fizer sentido, em pipelines de CI.

3. **Hardening incremental de componentes da S15**  
   - Ajustes localizados em `inspectah/debunker/`, `inspectah/committees/`, `inspectah/anchors/`, `inspectah/commands/`;  
   - Introdução de invariantes adicionais, checks defensivos, logs estruturados e métricas específicas para segurança.

4. **Observabilidade focada em segurança**  
   - Métricas e logs que permitam responder perguntas como:  
     - "Quantas disputas de alto risco estão abertas e há quanto tempo?"  
     - "Houve spikes anormais de tentativas de override ou de decisões revertidas?"  
     - "Quantas âncoras falharam ou atrasaram além de um limiar aceitável?"  
   - Export de consultas/painéis referentes a esses riscos (mesmo que em UI crua).

5. **ORR S16 para o pacote S13–S16**  
   - ORR focado no recorte técnico: Truth‑DB + Sistema de Blocos + camada de blindagem;  
   - documento que pode ser mostrado para alguém técnico e crítico, sem vergonha.

---

### 5. Fora de escopo (o que a S16 não vai fazer)

Para preservar a sanidade e evitar drift, a Sprint 16 **não** vai:

1. **Adicionar features de produto para usuário final**  
   - nada de novas UIs de consulta, dashboards de BI sofisticados ou flows de onboard de clientes;  
   - qualquer avanço de UX fica para uma fase posterior.

2. **Redesenhar completamente o Sistema de Blocos**  
   - ajustes pontuais são permitidos quando ligados a riscos do Threat Model;  
   - reescritas amplas de modelo de dados ou semântica ficam fora da S16.

3. **Recriar a camada de inteligência do zero**  
   - Debunker v1 e Comitês V1/V2/V3 serão endurecidos, não substituídos;  
   - qualquer "Debunker v2 gigante" ou comitê extra fica para outro ciclo.

4. **Implementar governança econômica complexa (tokens, bonds, incentivos)**  
   - a S16 pode registrar requisitos futuros, mas não implementa economia avançada;  
   - foco aqui é segurança técnica e operacional.

5. **Levar Inspectah direto para produção crítica**  
   - a S16 prepara material para essa conversa, mas não é a sprint de deployment;  
   - a decisão "produção real" exige uma fase de deployment/SRE em cima do que a S16 entregar.

---

### 6. Entregáveis principais da Sprint 16

Lista de entregáveis de alto nível (os nomes exatos e filemap irão para o Cap. 3):

1. **Documento de Threat Model da S16**  
   - ex.: `docs/sprint_16_threat_model.md`;  
   - contendo visão, ativos, atores, vetores de ataque, matriz impacto/probabilidade, hipóteses e decisões;  
   - com links diretos para módulos/scripts relevantes.

2. **Cenários de ataque e scripts reprodutíveis**  
   - ex.: `scripts/s16_attack_*.py`, `scripts/s16_stress_*.py` ou equivalente;  
   - cobrindo pelo menos:  
     - flood de disputas;  
     - envenenamento de dados/claims;  
     - captura parcial de comitês;  
     - chain offline/instável ou lenta;  
     - picos de overrides (reais ou tentativas).

3. **Ajustes de hardening em código**  
   - commits claros melhorando Debunker, comitês, âncoras e anti‑canetada;  
   - novos invariantes, logs e métricas diretamente ligados a riscos do Threat Model.

4. **Gates S16 (T0–T8) focados em segurança e resiliência**  
   - scripts `bin/s16_t0_*.sh`…`bin/s16_t8_go_no_go.sh`;  
   - orquestrador `bin/s16_all_gates.sh`;  
   - scorecards e evidências da S16 em `out/scorecards/` e `out/evidence/`.

5. **Observabilidade S16 para Threat Model**  
   - consultas/painéis alinhados às ameaças de maior prioridade;  
   - documentação básica de como ler/interpretar essas visões.

6. **`docs/sprint_16_orr_summary.md`**  
   - resumo do ORR da S16, descrevendo:  
     - ataques simulados;  
     - reações observadas;  
     - limitações aceitas;  
     - decisão final (GO/GO com restrições/NO_GO) para o pacote S13–S16.

---

### 7. Definição de pronto (DoD) da Sprint 16

A Sprint 16 só pode ser considerada **concluída** quando, no mínimo:

1. **Threat Model documentado e versionado**  
   - Threat Model criado, revisado e compatível com o estado real do código;  
   - referência explícita a Debunker, comitês, âncoras, anti‑canetada, gates e observabilidade.

2. **Cenários de ataque executáveis**  
   - scripts de ataque/stress rodando com um comando simples, sem configuração manual obscura;  
   - scorecards/evidências mostrando o efeito de cada cenário.

3. **Hardening aplicado e rastreável**  
   - mudanças em Debunker/comitês/âncoras/commands ligadas a riscos do Threat Model (e não a “achismos”);  
   - commits com mensagens que conectam risco → mudança → evidência.

4. **Gates S16 rodando ponta‑a‑ponta**  
   - `PYTHONPATH=. bin/s16_all_gates.sh` executa T0–T8 com scorecards/evidências consistentes;  
   - workflows de CI relevantes configurados (quando fizer sentido para esta fase).

5. **ORR S16 concluído e honesto**  
   - `docs/sprint_16_orr_summary.md` descreve:  
     - Threat Model;  
     - ataques realizados;  
     - comportamentos observados;  
     - o que o sistema ainda não aguenta bem;  
     - a decisão final de GO/NO_GO + recomendações para próximos ciclos.

Se qualquer um desses itens estiver faltando ou claramente incompleto, a S16 deve ser considerada **não concluída**, independentemente de merges ou releases.

---

### 8. Riscos, hipóteses e trade‑offs da S16

Principais riscos ao executar esta sprint:

1. **Escopo virar um "projeto de segurança infinito"**  
   - risco: tentar cobrir todas as ameaças imagináveis;  
   - mitigação: Threat Model foca nos riscos mais relevantes para o estágio atual e para o uso previsto do Inspectah.

2. **Hardening tornando o sistema impraticável para desenvolvimento**  
   - risco: regras de segurança tornarem o fluxo diário insuportável;  
   - mitigação: manter um modo de desenvolvimento com proteções reduzidas, documentado e separado do modo "validação".

3. **Foco excessivo em poucos domínios de dados**  
   - risco: testes ficarem concentrados em política/esporte e negligenciarem outros domínios críticos;  
   - mitigação: garantir pelo menos um cenário representativo para cada grande tipo de domínio (esporte, política, clima, fofoca, mandatos, projetos, ciência).

4. **Observabilidade se tornando barulhenta ou inútil**  
   - risco: excesso de métricas/painéis que ninguém consegue interpretar;  
   - mitigação: escolher poucas métricas realmente úteis para Threat Model e ORR S16, e documentá‑las.

Hipóteses de trabalho:

- a camada da S15 está **funcionalmente correta**; a S16 assume isso e foca em robustez e segurança, não em correção básica;  
- não haverá mudança radical de requisitos de produto durante a sprint;  
- a infraestrutura local/staging permite rodar cenários de stress dentro de limites razoáveis de tempo/custo.

---

### 9. Relação da Sprint 16 com o roadmap do Inspectah

No roadmap do Inspectah, a Sprint 16 fecha um ciclo técnico importante:

- S13: consolidação do Sistema de Blocos (Truth‑DB core);  
- S14: fortalecimento de disputas e write path;  
- S15: camada de inteligência e blindagem (Debunker, comitês, âncoras, anti‑canetada);  
- **S16: hardening e Threat Model desse pacote**.

Ao final da S16, esperamos ter:

- uma visão clara do que o Sistema de Blocos aguenta ou não aguenta sob pressão;  
- um pacote de evidências que permita apresentar o Inspectah como solução tecnicamente séria, mesmo em modo laboratório;  
- uma base mais segura para decidir próximos passos de produto (UI, APIs externas, clientes piloto, mecanismos de governança/incentivos).

Este capítulo encerra a definição de **visão e objetivos da Sprint 16**. Os próximos capítulos vão detalhar:

- gates e critérios de qualidade (Capítulo 2);  
- filemap, arquitetura e contratos de layout (Capítulo 3);  
- runbook operacional e superprompts para Codex (Capítulo 4).

