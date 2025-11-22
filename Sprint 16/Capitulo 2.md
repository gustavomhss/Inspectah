# Inspectah — Sprint 16  
## Capítulo 2 — Gates, Critérios de Qualidade e Perguntas Respondidas

### 0. Papel deste capítulo

Este capítulo define **os gates T0–T8 da Sprint 16**, seus objetivos, entradas/saídas, critérios de PASS/FAIL e as **perguntas concretas** que cada gate precisa responder sobre o Sistema de Blocos endurecido.

Ele conecta a visão da S16 (hardening + Threat Model) com:

- o que será efetivamente testado;
- como isso será empacotado em scorecards/evidências;
- quais riscos são reduzidos por cada gate;
- o que permanece como risco residual, explicitamente assumido.

O Capítulo 3 vai transformar estes gates em filemap, caminhos de scripts, layout de scorecards e estrutura detalhada dos artefatos. O Capítulo 4 vai trazer o runbook de execução (local/CI) e os superprompts para Codex.

---

### 1. Mapa geral dos gates da Sprint 16

Na Sprint 16, os gates seguem a mesma numeração T0–T8, mas com foco explícito em **Threat Model, ataques, hardening e ORR de segurança**:

- **T0 — Sanity & Base de Comparação S15**  
  Confirma que o ambiente está saudável, que a S15 segue “verde” e que estamos testando hardening em cima de uma base funcional.

- **T1 — Threat Model Completo e Consistente**  
  Verifica se o Threat Model da pilha S13–S15 existe, está coerente e reflete o código real.

- **T2 — Cenários de Ataque e Harness**  
  Garante que os cenários de ataque/stress estão formalizados em scripts reprodutíveis, alinhados ao Threat Model.

- **T3 — Debunker & Comitês sob Ataque**  
  Exercita Debunker v1 e Comitês V1/V2/V3 em cenários adversariais, verificando se comportamentos perigosos são detectáveis.

- **T4 — Âncoras, Anti‑canetada e Integridade de Estados**  
  Testa a robustez das âncoras e do anti‑canetada perante falhas, reorgs plausíveis e tentativas de bypass.

- **T5 — Stress, Performance e Degradação Controlada**  
  Observa como o sistema se comporta sob carga (ataques e picos), medindo não só latência, mas **modo de falha**.

- **T6 — Observabilidade de Segurança e Forense**  
  Verifica se logs, métricas e evidências permitem investigar incidentes e responder perguntas chave do Threat Model.

- **T7 — CI, Reprodutibilidade e Automatização dos Testes de Segurança**  
  Garante que os testes de segurança mais críticos podem rodar em CI, de forma reprodutível, sem “rituais manuais secretos”.

- **T8 — Go/No‑Go S16 (ORR de Hardening)**  
  Consolida scorecards e evidências e produz a decisão formal de GO/NO_GO da Sprint 16 para o pacote S13–S16.

Cada gate abaixo segue a estrutura padronizada:

- Objetivo;  
- Perguntas que responde;  
- Entradas e saídas (scorecards/evidências);  
- Implementação esperada (alto nível, sem travar o Cap. 3/4);  
- Critério de PASS/FAIL;  
- Riscos reduzidos e riscos residuais.

---

### 2. Gate T0 — Sanity & Base de Comparação S15

**Objetivo**

Garantir que a Sprint 16 está rodando em cima de um estado **funcionalmente saudável** da Sprint 15, sem regressões óbvias e com o pipeline de S15 íntegro. A ideia é impedir que a S16 “endureça” algo que já está quebrado.

**Perguntas que o T0 precisa responder**

1. O repositório está em um estado consistente (sem lixo crítico ou migrações quebradas)?  
2. O commit de referência (ou range) da S16 está claramente vinculado a um estado da S15 com `bin/s15_all_gates.sh` em GO?  
3. As dependências básicas (Python, libs, serviços locais necessários) estão presentes e minimamente saudáveis?

**Entradas esperadas**

- Repositório em `/Users/gustavoschneiter/Documents/Inspectah` em uma branch/commit da S16;  
- `docs/sprint_15_orr_summary.md` com o adendo da S15 (commit 47dfa5b…);  
- scripts e pipelines da S15 acessíveis.

**Saídas esperadas**

- Scorecard JSON, ex.: `out/scorecards/S16_T0_sanity.json`;  
- evidências mínimas em `out/evidence/S16_T0_sanity/` (logs de comandos, checks de versão, etc.).

**Implementação esperada (alto nível)**

- Script T0 da S16 deve:  
  - verificar que `bin/s15_all_gates.sh` roda e retorna todos os S15_T0…S15_T8 em PASS (ou revalidar um subconjunto crítico, se Cap. 3/4 definirem assim);  
  - checar presença e integridade mínima de `docs/sprint_15_orr_summary.md` e do adendo da S15;  
  - executar checks básicos de ambiente (versão de Python, variáveis essenciais, acessos mínimos a storage/logs);  
  - escrever resultado consolidado no scorecard.

**Critério de PASS/FAIL**

- PASS: todas as verificações de integridade de S15 e ambiente retornam OK; nenhum erro estrutural; scorecard T0 indica `status: "PASS"` e `decision: "GO"`.  
- FAIL: se S15 não puder ser revalidada minimamente ou se o ambiente estiver quebrado; scorecard T0 marca `status: "FAIL"` e `decision: "NO_GO"` com motivos claros.

**Riscos reduzidos por T0**

- Começar hardening em cima de uma base corrompida ou com regressões da S15;  
- Confusões de ambiente (testar a S16 em estado “meio quebrado” sem perceber).

**Riscos residuais**

- Problemas sutis de S15 que não se manifestem nos checks do T0;  
- Erros de configuração muito específicos que só apareçam em gates posteriores.

---

### 3. Gate T1 — Threat Model Completo e Consistente

**Objetivo**

Verificar se existe um **Threat Model formal, coerente e atualizado** para a pilha S13–S15 (Sistema de Blocos + Debunker + Comitês + Âncoras + Anti‑canetada), e se esse modelo é consistente com o código e artefatos.

**Perguntas que o T1 precisa responder**

1. Existe um documento de Threat Model da S16, versionado, cobrindo os principais ativos, atores e vetores de ataque?  
2. Esse documento referencia explicitamente os módulos e scripts certos (Debunker, comitês, âncoras, commands, gates S15/S16)?  
3. As ameaças descritas fazem sentido para o estado atual do código (não são só teoria genérica)?

**Entradas esperadas**

- Documento de Threat Model (ex.: `docs/sprint_16_threat_model.md`);  
- Código atual dos módulos relevantes (`inspectah/debunker/`, `inspectah/committees/`, `inspectah/anchors/`, `inspectah/commands/`, scripts S15/S16 associados).

**Saídas esperadas**

- Scorecard `out/scorecards/S16_T1_threat_model.json`;  
- evidências em `out/evidence/S16_T1_threat_model/` (cópias/trechos do Threat Model, checagens de links para módulos, etc.).

**Implementação esperada (alto nível)**

- Script T1 da S16 deve:  
  - validar a existência do doc de Threat Model em local padrão;  
  - rodar um verificador simples (script ou teste) que procure referências a módulos/scripts reais e confirme que eles existem;  
  - realizar checks mínimos de estrutura (seções obrigatórias: ativos, atores, ameaças, mitigação, riscos residuais);  
  - marcar, no scorecard, o nível de completude/consistência.

**Critério de PASS/FAIL**

- PASS: Threat Model presente, com seções mínimas completas, referências coerentes a módulos e scripts, e nenhuma inconsistência grosseira detectada;  
- FAIL: ausência do documento, estrutura claramente incompleta ou referências quebradas a partes críticas do sistema.

**Riscos reduzidos por T1**

- Trabalhar em testes de segurança desconectados de um modelo explícito de ameaças;  
- Deixar vetores relevantes de fora simplesmente por falta de reflexão sistemática.

**Riscos residuais**

- Threat Model incompleto, mas “bem escrito”, que passe nos checks estruturais;  
- Ameaças emergentes que não foram previstas apesar do esforço.

---

### 4. Gate T2 — Cenários de Ataque e Harness

**Objetivo**

Garantir que os **cenários de ataque, stress e caos** identificados no Threat Model foram traduzidos em scripts reprodutíveis e configuráveis, prontos para serem usados nos gates posteriores (T3–T6).

**Perguntas que o T2 precisa responder**

1. Para cada ameaça prioritária do Threat Model, existe pelo menos um cenário de teste associado?  
2. Esses cenários podem ser executados com comandos simples (sem passos manuais obscuros)?  
3. Os cenários produzem logs/artefatos suficientes para que T3–T6 consigam medir algo útil?

**Entradas esperadas**

- Threat Model (doc do T1) com lista de ameaças prioritárias;  
- Scripts de ataque/stress da S16 (por exemplo `scripts/s16_attack_*.py`, `scripts/s16_stress_*.py`).

**Saídas esperadas**

- Scorecard `out/scorecards/S16_T2_attack_scenarios.json`;  
- evidências em `out/evidence/S16_T2_attack_scenarios/` (lista de cenários, comandos de execução, logs de amostra).

**Implementação esperada (alto nível)**

- Script T2 da S16 deve:  
  - percorrer a lista de ameaças de alta prioridade do Threat Model;  
  - verificar se há mapeamento ameaça → cenário de ataque;  
  - executar smoke tests de alguns desses cenários (ou todos, se custo permitir);  
  - registrar quais cenários existem, quais foram executados, quais falharam e por quê.

**Critério de PASS/FAIL**

- PASS: todas as ameaças prioritárias têm cenários associados e os scripts principais executam ao menos em modo smoke, produzindo logs/artefatos esperados;  
- FAIL: lacunas grandes (ameaças sem cenário), scripts ausentes ou cenários que não rodam nem em modo mínimo.

**Riscos reduzidos por T2**

- Threat Model ficar só no papel, sem tradução em testes concretos;  
- Descobrir, tarde demais, que não existem ferramentas para simular ataques relevantes.

**Riscos residuais**

- Cenários implementados de forma superficial ou pouco realista;  
- Ameaças cobertas por cenários muito genéricos.

---

### 5. Gate T3 — Debunker & Comitês sob Ataque

**Objetivo**

Avaliar o comportamento do **Debunker v1** e dos **Comitês V1/V2/V3** quando submetidos a entradas adversariais, cenários maliciosos ou casos extremos de disputa, medindo se decisões perigosas ou incoerentes são detectáveis e justificadas.

**Perguntas que o T3 precisa responder**

1. O Debunker reage de forma razoável a claims deliberadamente maliciosos ou confusos?  
2. Os Comitês V1/V2/V3 conseguem rejeitar/mitigar decisões claramente perigosas ou incoerentes?  
3. As decisões (especialmente as erradas ou arriscadas) deixam trilha suficiente para investigação posterior?

**Entradas esperadas**

- Scripts de ataque que geram disputas/claims adversariais para Debunker/comitês;  
- Implementação atual de `inspectah/debunker/*` e `inspectah/committees/*`.

**Saídas esperadas**

- Scorecard `out/scorecards/S16_T3_debunker_and_committees_under_attack.json`;  
- evidências em `out/evidence/S16_T3_debunker_and_committees/` (logs, exemplos de decisões, relatórios do Debunker, outputs de comitês).

**Implementação esperada (alto nível)**

- Script T3 da S16 deve:  
  - acionar um conjunto de cenários de ataque focados em Debunker + comitês (diretamente ou via helpers);  
  - capturar decisões e relatórios produzidos;  
  - classificar resultados em categorias (OK, suspeito mas detectável, perigoso e não detectável, erro estrutural);  
  - escrever estatísticas e exemplos no scorecard.

**Critério de PASS/FAIL**

- PASS:  
  - Debunker e comitês lidam corretamente com a maioria dos cenários adversariais previstos;  
  - casos perigosos aparecem, mas são ao menos detectáveis (logs claros, flags, estados classificados como arriscados);  
  - não existem decisões claramente incoerentes “silenciosas”.  
- FAIL:  
  - Debunker/comitês aprovam ou consolidam estados perigosos/incoerentes sem qualquer alerta ou trilha;  
  - muitos cenários terminam em erro estrutural não tratado.

**Riscos reduzidos por T3**

- Sistema parecer robusto em cenários triviais, mas colapsar quando confrontado com entradas adversariais;  
- Decisões perigosas passarem sem registro ou contestação interna.

**Riscos residuais**

- Ataques criativos ainda não prototipados;  
- Limitações intrínsecas de modelos de IA (quando existirem) na interpretação de texto e nuances.

---

### 6. Gate T4 — Âncoras, Anti‑canetada e Integridade de Estados

**Objetivo**

Testar, em cenários de falha, a robustez do módulo de **âncoras** em blockchain e do mecanismo **anti‑canetada**, garantindo que estados importantes não possam ser adulterados sem deixar rastros e que o sistema se comporte bem com problemas de chain.

**Perguntas que o T4 precisa responder**

1. O sistema continua íntegro se a chain ficar lenta, indisponível ou sofrer reorgs plausíveis?  
2. As referências de âncora (Merkle/batches/registry) permanecem consistentes em cenários de stress?  
3. Tentativas de override direto ou de bypass de anti‑canetada são bloqueadas e registradas?

**Entradas esperadas**

- Implementação de `inspectah/anchors/*`, `inspectah/blocks/__init__.py`, `inspectah/commands/__init__.py`;  
- scripts de ataque/stress relacionados a chain/overrides.

**Saídas esperadas**

- Scorecard `out/scorecards/S16_T4_anchors_and_anti_canetada.json`;  
- evidências em `out/evidence/S16_T4_anchors_and_anti_canetada/` (logs de âncoras, tentativas de override, estados antes/depois).

**Implementação esperada (alto nível)**

- Script T4 da S16 deve:  
  - simular envio de batches de âncoras em condições normais e degradadas;  
  - simular indisponibilidade temporária ou falha no `chain_client`;  
  - tentar acionar rotas de override direto;  
  - verificar, nos logs e estados, se o anti‑canetada está operando conforme o design.

**Critério de PASS/FAIL**

- PASS:  
  - estados não são alterados silenciosamente por override direto;  
  - falhas em âncoras não corrompem o histórico; no máximo atrasam garantias externas;  
  - tentativas de bypass são registradas com clareza.  
- FAIL:  
  - é possível alterar estados críticos sem disputa/evento/registro;  
  - inconsistências graves em referências de âncora aparecem sem qualquer alerta.

**Riscos reduzidos por T4**

- "Canetadas" invisíveis;  
- perda de vínculo entre estados internos e âncoras externas;  
- falsa sensação de segurança em relação à chain.

**Riscos residuais**

- Ataques complexos envolvendo múltiplas chains ou camadas externas;  
- Problemas de compliance/regulatórios além do escopo técnico da S16.

---

### 7. Gate T5 — Stress, Performance e Degradação Controlada

**Objetivo**

Avaliar **como o sistema falha** sob carga intensa e cenários de ataque em volume, priorizando o entendimento de **modos de degradação** em vez de apenas números de latência.

**Perguntas que o T5 precisa responder**

1. O sistema degrada de forma graciosa (fila, timeouts, backoff) ou simplesmente entra em colapso?  
2. Operações críticas (como resolução de disputas ou registro de âncoras) mantêm integridade mesmo sob stress?  
3. Existem gargalos óbvios ou pontos únicos de falha que se tornam evidentes em stress tests?

**Entradas esperadas**

- Scripts de stress/carga (por exemplo, `scripts/s16_stress_*`);  
- Configurações de ambiente (limites de conexão, recursos de CPU/memória). 

**Saídas esperadas**

- Scorecard `out/scorecards/S16_T5_stress_and_degradation.json`;  
- evidências em `out/evidence/S16_T5_stress_and_degradation/` (resumos de métricas, gráficos/relatórios simples, logs de falhas controladas).

**Implementação esperada (alto nível)**

- Script T5 da S16 deve:  
  - rodar um conjunto de testes de stress em endpoints/fluxos chave do Sistema de Blocos + camada de blindagem;  
  - recolher métricas essenciais (latência, taxa de erro, fila, saturação de recursos);  
  - registrar, em texto simples, o comportamento observado (ex.: padrões de timeouts, retentativas, quedas controladas).

**Critério de PASS/FAIL**

- PASS:  
  - o sistema mantém integridade de dados;  
  - falhas ocorrem de forma controlada (timeouts, backoff, refusals claros);  
  - não surgem sinais óbvios de corrupção ou comportamento caótico.  
- FAIL:  
  - perda de integridade;  
  - falhas catastróficas silenciosas;  
  - comportamento imprevisível sob stress.

**Riscos reduzidos por T5**

- Supor que o sistema "aguenta bem" só porque funciona em volume baixo;  
- Não saber como o sistema reage a picos ou ataques de volumetria.

**Riscos residuais**

- Cenários de stress extremos ainda não testados;  
- Dependência de ambiente específico (resultado pode variar em outras infraestruturas).

---

### 8. Gate T6 — Observabilidade de Segurança e Forense

**Objetivo**

Verificar se a observabilidade do Inspectah (logs, métricas, painéis) permite **investigar incidentes de segurança** e responder às perguntas cruciais do Threat Model, sem depender de memória humana ou soluções ad‑hoc.

**Perguntas que o T6 precisa responder**

1. É possível, a partir de logs/métricas, reconstruir o que aconteceu em um incidente simulado (ataque, falha de âncora, override tentado)?  
2. Existem métricas que indiquem tendências perigosas (acúmulo de disputas de alto risco, aumento de overrides, âncoras falhando)?  
3. Os artefatos gerados pelos outros gates (T3–T5) são localizáveis e interpretáveis?

**Entradas esperadas**

- Configurações de observabilidade (Loki/Prometheus/etc.), dashboards quando existirem;  
- logs e dados gerados por cenários de ataque/stress dos outros gates.

**Saídas esperadas**

- Scorecard `out/scorecards/S16_T6_security_observability.json`;  
- evidências em `out/evidence/S16_T6_security_observability/` (consultas, snapshots de painéis, transcrições de "investigações").

**Implementação esperada (alto nível)**

- Script T6 da S16 deve:  
  - executar um conjunto de consultas pré‑definidas a logs/métricas;  
  - simular uma pequena investigação, respondendo a perguntas do Threat Model (“houve spike de overrides?”, “quais disputas de alto risco falharam?”, “quais âncoras deram erro nos últimos N minutos?”);  
  - registrar as respostas e dificuldades encontradas.

**Critério de PASS/FAIL**

- PASS:  
  - pelo menos as principais perguntas de segurança podem ser respondidas com base em dados reais;  
  - há artefatos suficientes para montar uma linha do tempo básica de incidentes simulados.  
- FAIL:  
  - perguntas fundamentais do Threat Model não podem ser respondidas;  
  - logs/métricas existem, mas são inúteis ou impossíveis de navegar.

**Riscos reduzidos por T6**

- Ter um sistema teórica e funcionalmente robusto, mas opaco;  
- Ser incapaz de explicar "como e por que" algo deu errado.

**Riscos residuais**

- Cenários em que volume de logs é grande demais para inspeção manual;  
- Necessidade futura de ferramentas adicionais de análise.

---

### 9. Gate T7 — CI, Reprodutibilidade e Automatização dos Testes de Segurança

**Objetivo**

Garantir que os testes de segurança da S16 (pelo menos o subconjunto mais crítico) podem rodar em **CI**, com resultados reprodutíveis e sem depender de passos manuais frágeis.

**Perguntas que o T7 precisa responder**

1. Existe um workflow de CI (ou etapas integradas em workflows existentes) rodando os gates críticos da S16?  
2. O resultado dos gates em CI bate com o resultado local (sem flakiness absurda)?  
3. É possível acionar esses testes sob demanda (por branch ou tag específica) para revalidar hardening?

**Entradas esperadas**

- Configuração de CI (`.ci/*`), incluindo novos jobs/steps da S16;  
- scripts S16 já integrados (`bin/s16_tX_*.sh`, `bin/s16_all_gates.sh`).

**Saídas esperadas**

- Scorecard `out/scorecards/S16_T7_ci_and_repro.json`;  
- evidências em `out/evidence/S16_T7_ci_and_repro/` (logs de jobs em CI, links para runs, resumos de comparações local vs. CI).

**Implementação esperada (alto nível)**

- Script T7 da S16 deve:  
  - checar a existência de workflows de CI relacionados à S16;  
  - verificar uma execução recente desses workflows (ou fornecer comandos para acioná‑los);  
  - comparar resultados dos gates em CI com execuções locais recentes;  
  - registrar divergências e flakiness.

**Critério de PASS/FAIL**

- PASS:  
  - existe CI cobrindo pelo menos T0–T4 (ou o subconjunto acordado como crítico);  
  - resultados locais e em CI são compatíveis, sem flakiness severa;  
  - existe documentação mínima de como acionar esses jobs.  
- FAIL:  
  - ausência de workflows;  
  - resultados altamente instáveis ou divergentes entre local e CI.

**Riscos reduzidos por T7**

- Testes de segurança dependerem exclusivamente de rodadas manuais;  
- Perda gradual de hardening ao longo do tempo por falta de guardrails automáticos.

**Riscos residuais**

- Limitações da infraestrutura de CI (custo/tempo para rodar cenários completos);  
- Cenários de ataque muito pesados não viáveis em cada PR.

---

### 10. Gate T8 — Go/No‑Go S16 (ORR de Hardening)

**Objetivo**

Consolidar, em um **scorecard final e um resumo de ORR**, o estado de hardening do Sistema de Blocos (S13–S16), decidindo se ele está **apto ou não** para avançar para próximos passos (por exemplo, pilotos controlados, exposição mais ampla, etc.).

**Perguntas que o T8 precisa responder**

1. Os gates T0–T7 da S16 foram executados, e o que cada um concluiu?  
2. Que ameaças do Threat Model foram efetivamente mitigadas/testadas, e quais permanecem como riscos residuais?  
3. Qual a decisão final para este estágio: GO, GO_WITH_RESTRICTIONS ou NO_GO?

**Entradas esperadas**

- Todos os scorecards da S16 (`S16_T0`…`S16_T7`);  
- evidências associadas em `out/evidence/S16_TX_*`;  
- Threat Model e demais docs da S16.

**Saídas esperadas**

- Scorecard `out/scorecards/S16_T8_go_no_go.json`;  
- evidências consolidadas em `out/evidence/S16_T8_go_no_go/` (manifest, resumos, links para scorecards anteriores);  
- documento `docs/sprint_16_orr_summary.md` atualizado.

**Implementação esperada (alto nível)**

- Script T8 da S16 deve:  
  - ler todos os scorecards T0–T7;  
  - avaliar se os critérios de pronto da S16 (DoD do Cap. 1) foram cumpridos;  
  - produzir um scorecard final com `decision` ∈ {"GO", "GO_WITH_RESTRICTIONS", "NO_GO"};  
  - gerar um resumo estruturado das principais evidências e riscos residuais.

**Critério de PASS/FAIL**

- PASS (no sentido de execução): T8 consegue ler scorecards, gerar o consolidado e produzir uma decisão clara;  
- A decisão em si pode ser GO, GO_WITH_RESTRICTIONS ou NO_GO, conforme o estado.  
- FAIL (do gate): T8 não consegue consolidar informações ou não gera decisão estruturada.

**Riscos reduzidos por T8**

- Ficar sem conclusão clara sobre o estado de segurança e robustez;  
- Avançar para próximos passos sem visão consolidada de riscos.

**Riscos residuais**

- Decisões baseadas em informação incompleta ou em julgamentos conservadores/demasiado otimistas;  
- Mudanças futuras no contexto de uso que invalidem parte das suposições.

---

### 11. Relação com Capítulos 3 e 4

Este Capítulo 2 descreve **o que cada gate precisa garantir** e **quais perguntas ele responde**. Os próximos capítulos vão tornar isso acionável:

- **Capítulo 3 (filemap e arquitetura da S16)**:  
  - mapeia cada gate para scripts específicos (`bin/s16_tX_*.sh`, `scripts/s16_*`),  
  - define caminhos exatos de scorecards e evidências,  
  - descreve a organização de diretórios e contratos de layout.

- **Capítulo 4 (runbook da S16)**:  
  - define como rodar os gates localmente e em CI,  
  - traz superprompts para o Codex implementar/ajustar scripts e cenários,  
  - descreve como conduzir investigações de incidentes usando os artefatos da S16.

Com isso, a Sprint 16 passa a ter um **mapa de qualidade explícito**: se T0–T8 estiverem verdes, sabemos exatamente **que tipo de hardening foi de fato realizado** e **quais ameaças foram encaradas de frente**.

