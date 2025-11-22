# Inspectah — Sprint 16  
## Capítulo 4 — Runbook Operacional e Modo de Uso da S16

### 0. Papel deste capítulo

Este Capítulo 4 descreve **como operar** a Sprint 16 na prática:

- como preparar o ambiente para rodar os gates de hardening;
- como executar T0–T8 localmente, em sequência ou de forma isolada;
- como interpretar scorecards e evidências geradas pela S16;
- como integrar a S16 com CI e com o fluxo diário de trabalho;
- como conduzir troubleshooting e investigações a partir de incidentes simulados.

Importante: **Capítulo 4 não é o superprompt do Codex.**  
Ele descreve o comportamento desejado, os comandos e o fluxo operacional. Os superprompts para o Codex são artefatos separados (por exemplo, em `docs/sprint_16_codex_prompts.md`), derivados deste capítulo, mas não misturados nele.

---

### 1. Preparação de ambiente

#### 1.1 Pré‑requisitos básicos

Para operar a S16 em `/Users/gustavoschneiter/Documents/Inspectah` espera‑se:

- Python e dependências já instalados conforme sprints anteriores (S10–S15);
- ambiente local capaz de rodar os scripts do Inspectah com `PYTHONPATH=.`;
- acesso aos serviços de observabilidade (Loki/Prometheus/afins) configurados nas sprints anteriores, quando necessário para T6;
- acesso ao repositório remoto em GitHub para acionar/verificar CI;
- `out/` com estrutura mínima já criada por sprints anteriores (scorecards/evidências).

A S16 supõe que o estado mínimo da S15 está saudável (validado por `bin/s15_all_gates.sh`), como descrito no Capítulo 2 (T0). Se S15 estiver “vermelha”, a prioridade passa a ser corrigir S15 antes de endurecer camadas acima.

#### 1.2 Organização de pastas

O runbook assume a estrutura descrita no Capítulo 3:

- `Sprint 16/Capitulo *.md` — contexto e design da S16 (visão, gates, filemap, runbook);
- `docs/sprint_16_*.md` — visão, Threat Model, filemap/arquitetura, ORR;
- `bin/s16_tX_*.sh`, `bin/s16_all_gates.sh` — gates T0–T8 e orquestração;
- `scripts/s16_*.py` — cenários de ataque, checks, stress, observabilidade e CI;
- `inspectah/*` — módulos de Debunker, comitês, âncoras e anti‑canetada endurecidos;
- `out/scorecards/` e `out/evidence/` — resultados e provas geradas pelos gates.

Se qualquer uma dessas peças estiver ausente, o passo inicial é implementar/ajustar os artefatos faltantes com base nos Capítulos 1–3 e na DNA.

---

### 2. Fluxo padrão de execução local da S16

#### 2.1 Checagem rápida de estado antes de rodar

Antes de rodar os gates da S16, recomenda‑se a seguinte rotina mínima:

1. Certificar‑se de estar na pasta raiz do repo:  
   `cd /Users/gustavoschneiter/Documents/Inspectah`
2. Verificar o estado do Git:  
   `git status`  
   Objetivo: evitar rodar gates em cima de mudanças locais irrelevantes ou sujeitas a descarte.
3. Opcionalmente, revalidar S15 (full ou subset crítico, conforme custo):  
   `PYTHONPATH=. bin/s15_all_gates.sh`

Se S15 falhar de forma estrutural, **não faz sentido rodar S16** até que o problema seja entendido e tratado.

#### 2.2 Execução completa de T0–T8 da S16

Fluxo padrão da S16, assumindo scripts existentes:

1. Estar na raiz do repo:  
   `cd /Users/gustavoschneiter/Documents/Inspectah`
2. Rodar o orquestrador de gates:  
   `PYTHONPATH=. bin/s16_all_gates.sh`

Esperado:

- o script imprime no terminal, na ordem, cada gate T0–T8 com status (OK/FAIL);  
- para cada gate, são criados/atualizados scorecards em `out/scorecards/` e evidências em `out/evidence/`;  
- em caso de FAIL, o script interrompe a sequência (comportamento padrão), informando qual gate quebrou e onde estão os artefatos.

#### 2.3 Execução isolada de um gate

Para debugging ou refinamento, é possível rodar gates isolados, por exemplo:

- `PYTHONPATH=. bin/s16_t0_sanity.sh`  
- `PYTHONPATH=. bin/s16_t3_debunker_and_committees_under_attack.sh`  
- `PYTHONPATH=. bin/s16_t6_security_observability.sh`

O comportamento esperado é o mesmo: scorecard + evidências por gate, sem obrigar a rodar a sequência inteira.

---

### 3. Modo de operação gate a gate

Aqui o foco é **uso diário** de cada gate. As perguntas de qualidade e critérios de PASS/FAIL estão no Capítulo 2; este capítulo descreve como aplicar.

#### 3.1 T0 — Sanity & Base de Comparação S15

Comando:

- `PYTHONPATH=. bin/s16_t0_sanity.sh`

Esperado operacionalmente:

- verificar integridade mínima do ambiente local (versões, variáveis essenciais, diretórios);  
- reusar ou chamar `bin/s15_all_gates.sh` (full ou subset crítico) para garantir que S15 está saudável;  
- escrever `out/scorecards/S16_T0_sanity.json` e `out/evidence/S16_T0_sanity/*`.

Uso típico:

- rodar T0 antes de qualquer outra atividade da S16;  
- se T0 falha, tratar primeiro a causa (ambiente ou S15) antes de insistir em T1–T8.

#### 3.2 T1 — Threat Model Completo e Consistente

Comando:

- `PYTHONPATH=. bin/s16_t1_threat_model.sh`

Esperado operacionalmente:

- garantir a existência de `docs/sprint_16_threat_model.md` no formato esperado;  
- acionar `scripts/s16_threat_model_checks.py` para validar estrutura mínima do documento e referências a módulos/scripts reais;  
- gerar `out/scorecards/S16_T1_threat_model.json` e `out/evidence/S16_T1_threat_model/*`.

Uso típico:

- após editar o Threat Model, rodar T1 para garantir que o documento continua coerente com o repositório;  
- manter T1 verde antes de rodar T2–T6, para evitar cenários de ataque desconectados da realidade.

#### 3.3 T2 — Cenários de Ataque e Harness

Comando:

- `PYTHONPATH=. bin/s16_t2_attack_scenarios.sh`

Esperado operacionalmente:

- acionar `scripts/s16_attack_scenarios.py` em modo smoke, garantindo que cada ameaça prioritária do Threat Model tem um cenário associado e executável;  
- gerar inventário de cenários (nome, ameaça associada, comando, tags);  
- escrever `out/scorecards/S16_T2_attack_scenarios.json` e `out/evidence/S16_T2_attack_scenarios/*`.

Uso típico:

- rodar T2 após criar/ajustar cenários;  
- usar T2 como “sanity check” para a biblioteca de ataques antes de exercícios mais caros (T3–T5).

#### 3.4 T3 — Debunker & Comitês sob Ataque

Comando:

- `PYTHONPATH=. bin/s16_t3_debunker_and_committees_under_attack.sh`

Esperado operacionalmente:

- chamar `scripts/s16_debunker_and_committees_under_attack.py`, que orquestra cenários adversariais focados em Debunker v1 e Comitês V1/V2/V3;  
- capturar decisões, relatórios e classificações de risco;  
- consolidar estatísticas e exemplos representativos;  
- escrever `out/scorecards/S16_T3_debunker_and_committees_under_attack.json` e `out/evidence/S16_T3_debunker_and_committees/*`.

Uso típico:

- rodar T3 após alterações em Debunker ou comitês;  
- usar evidências de T3 como base para discutir riscos residuais e justificar decisões de GO_WITH_RESTRICTIONS no ORR.

#### 3.5 T4 — Âncoras, Anti‑canetada e Integridade de Estados

Comando:

- `PYTHONPATH=. bin/s16_t4_anchors_and_anti_canetada.sh`

Esperado operacionalmente:

- acionar `scripts/s16_anchors_and_anti_canetada_tests.py`;  
- simular envio de batches de âncoras em condições normais e degradadas;  
- tentar invocar rotas de override direto e verificar atuação do anti‑canetada;  
- registrar logs e resultados em `out/evidence/S16_T4_anchors_and_anti_canetada/*`;  
- escrever `out/scorecards/S16_T4_anchors_and_anti_canetada.json`.

Uso típico:

- rodar T4 após alterações em `inspectah/anchors/*`, `inspectah/commands/__init__.py` ou integrações de chain;  
- confirmar se estados críticos continuam protegidos contra “canetadas” silenciosas.

#### 3.6 T5 — Stress, Performance e Degradação Controlada

Comando:

- `PYTHONPATH=. bin/s16_t5_stress_and_degradation.sh`

Esperado operacionalmente:

- invocar `scripts/s16_stress_and_degradation.py` com parâmetros adequados ao ambiente;
- executar testes de stress controlado em fluxos críticos (disputas, anchoring, comitês);
- coletar métricas essenciais (latência, taxa de erro, saturação) e registrar modo de falha;
- escrever `out/scorecards/S16_T5_stress_and_degradation.json` e `out/evidence/S16_T5_stress_and_degradation/*`.

Uso típico:

- rodar T5 em momentos chave (pós‑refatoração, antes de milestones, em nightly de segurança);  
- usar resultados para ajustar limites, timeouts, políticas de backoff e alertas.

#### 3.7 T6 — Observabilidade de Segurança e Forense

Comando:

- `PYTHONPATH=. bin/s16_t6_security_observability.sh`

Esperado operacionalmente:

- acionar `scripts/s16_security_observability_checks.py`;  
- executar consultas padrão em logs/métricas (Loki/Prometheus/afins) para responder às perguntas do Threat Model;  
- registrar as respostas, lacunas e dificuldades em `out/evidence/S16_T6_security_observability/*`;  
- escrever `out/scorecards/S16_T6_security_observability.json`.

Uso típico:

- rodar T6 após alterações relevantes em logging, métricas ou painéis;  
- usar evidências para ajustar o que é logado/medido e incrementar playbooks de resposta a incidentes.

#### 3.8 T7 — CI, Reprodutibilidade e Automatização dos Testes de Segurança

Comando local:

- `PYTHONPATH=. bin/s16_t7_ci_and_repro.sh`

Esperado operacionalmente:

- inspecionar `.ci/sprint_16_gates.yml` e `.ci/sprint_16_nightly.yml`;  
- verificar se existiram execuções recentes relevantes na CI (por leitura de artefatos/relatórios baixados ou via integrações simples);  
- comparar, quando possível, resultados locais vs. resultados da CI;  
- escrever `out/scorecards/S16_T7_ci_and_repro.json` e `out/evidence/S16_T7_ci_and_repro/*`.

Uso típico:

- rodar T7 periodicamente para garantir que a CI continua alinhada com o uso local;  
- rodar em branches de hardening para validar se novos testes de segurança entraram realmente na CI.

#### 3.9 T8 — Go/No‑Go S16 (ORR de Hardening)

Comando:

- `PYTHONPATH=. bin/s16_t8_go_no_go.sh`

Esperado operacionalmente:

- ler todos os scorecards S16_T0…S16_T7;  
- avaliar se os critérios de pronto da S16 (Capítulo 1) foram cumpridos;  
- produzir `out/scorecards/S16_T8_go_no_go.json` com `decision` ∈ {"GO", "GO_WITH_RESTRICTIONS", "NO_GO"};  
- gerar `out/evidence/S16_T8_go_no_go/MANIFEST.json` apontando para scorecards e evidências relevantes;  
- opcionalmente, gerar um rascunho de seções para `docs/sprint_16_orr_summary.md` (a edição final do ORR permanece humana e revisada).

Uso típico:

- rodar T8 ao final de ciclos importantes de trabalho na S16 (por exemplo, ao fechar a sprint);  
- usar o scorecard de T8 como base para decisões de exposição do sistema (pilotos controlados, ambientes mais críticos, etc.).

---

### 4. Interpretação de scorecards e evidências

#### 4.1 Leitura rápida de scorecards

Para uma leitura rápida do estado da S16:

1. Listar scorecards da S16:  
   `ls out/scorecards/S16_T*.json`
2. Inspecionar T8 primeiro (visão consolidada):  
   `cat out/scorecards/S16_T8_go_no_go.json`
3. Em caso de `decision` diferente de `GO`, olhar para gates marcados como FAIL e navegar até seus scorecards/evidências.

Os campos mínimos de cada scorecard (gate, status, decision, metrics, evidence_paths, notes) devem permitir entender rapidamente o que foi testado e o que deu errado.

#### 4.2 Navegação por evidências

Para uma investigação mais profunda:

1. Localizar a pasta de evidências do gate de interesse, por exemplo:  
   `ls out/evidence/S16_T3_debunker_and_committees/`
2. Abrir `MANIFEST.json` para entender o conteúdo e os checksums;  
3. Em seguida, abrir arquivos de logs, relatórios e snapshots indicados no manifesto.

Princípio: scorecards respondem “o que aconteceu” em alto nível; evidências mostram “como e por que” em detalhes.

---

### 5. Integração com CI

#### 5.1 Workflows da S16

A camada de CI da S16 vive em arquivos como:

- `.ci/sprint_16_gates.yml` — roda T0–T8 (ou subset crítico) em PRs/branches relevantes;  
- `.ci/sprint_16_nightly.yml` — roda cenários mais pesados de stress/ataque em base diária ou cadência acordada.

O Capítulo 3 define a presença desses arquivos; este Capítulo 4 define o modo de uso esperado.

#### 5.2 Uso típico em PRs

Fluxo sugerido:

1. Desenvolvedor abre PR com mudanças relevantes a S13–S16;  
2. CI executa `.ci/sprint_16_gates.yml`;  
3. O PR só é elegível para merge se os gates críticos da S16 estiverem verdes ou se houver justificativa explícita e registrada para qualquer exceção.

Os resultados da CI (logs, artefatos de scorecards/evidências) devem ser rastreáveis no provedor de CI, e o T7 consome esses artefatos quando possível.

#### 5.3 Uso típico em nightly

Fluxo sugerido:

1. `.ci/sprint_16_nightly.yml` roda em horário de baixa carga;  
2. são executados testes de stress/ataque que seriam caros demais para rodar em cada PR;  
3. eventuais falhas disparam alertas (issues automáticos, notificações) e viram itens de trabalho para hardening adicional.

---

### 6. Troubleshooting e investigações

#### 6.1 Quando um gate falha

Em caso de FAIL em um gate:

1. Identificar o gate pela saída do terminal ou pelo T8 (se já tiver sido rodado);  
2. Abrir o scorecard específico (`out/scorecards/S16_TX_*.json`) para ver motivo e métricas;  
3. Navegar para a respectiva pasta de evidências;  
4. Localizar logs, cenários específicos e entradas que levaram à falha.

A partir disso, há dois caminhos principais:

- corrigir um bug real ou um comportamento problemático;  
- revisar Threat Model e critérios de PASS/FAIL, se o comportamento observado for aceitável mas não estava previsto.

#### 6.2 Quando tudo passa, mas algo estranho acontece

Caso não haja FAIL explícito, mas incidentes estranhos sejam observados:

1. Usar T6 (observabilidade) para reconstruir o incidente via logs/métricas;  
2. Se o incidente não for explicável com os artefatos atuais, registrar lacunas em `docs/sprint_16_orr_summary.md` como riscos residuais;  
3. Planejar ajustes em Threat Model, logging, métricas e cenários de ataque para ciclos futuros (pós‑S16).

---

### 7. Checklist resumido de operação da S16

Um checklist resumido para uso prático:

1. Garantir que S15 está verde ou que eventuais falhas são entendidas.  
2. Rodar T0 para validar base da S16.  
3. Garantir que o Threat Model está atualizado (T1).  
4. Checar se cenários de ataque estão completos e executáveis (T2).  
5. Exercitar Debunker/comitês sob ataque (T3).  
6. Validar âncoras e anti‑canetada em cenários adversos (T4).  
7. Rodar stress tests focados em modos de falha (T5).  
8. Confirmar que observabilidade permite investigar incidentes (T6).  
9. Garantir que CI cobre os testes críticos da S16 (T7).  
10. Consolidar resultado em T8 e registrar decisão no ORR.

---

### 8. Relação com superprompts do Codex

Os superprompts para o Codex são **derivados** deste Capítulo 4, mas mantidos em arquivos dedicados. A ideia é:

- este capítulo define comportamento, comandos e contratos;  
- os superprompts convertem estes contratos em instruções específicas para o Codex criar/ajustar arquivos.

Exemplos conceituais (não textuais):

- um superprompt para `bin/s16_t3_debunker_and_committees_under_attack.sh` tomaria como entrada as seções 3.4, 4 e 7 deste capítulo;  
- um superprompt para `scripts/s16_stress_and_degradation.py` usaria as seções 3.6, 4 e 6.

Esses superprompts devem:

- viver em arquivos como `docs/sprint_16_codex_prompts.md` ou similar;  
- ser versionados junto com o restante do repo;  
- ser mantidos em sincronia com Capítulos 1–4 da S16.

Capítulo 4 encerra, assim, o "circuito" da S16:  
Capítulo 1 define o **porquê**, Capítulo 2 define **o que** precisa ser garantido, Capítulo 3 define **onde** tudo mora, e Capítulo 4 define **como operar** no dia a dia. A partir daqui, execução e superprompts podem evoluir sem perder alinhamento com o DNA e com o Threat Model da Sprint 16.

