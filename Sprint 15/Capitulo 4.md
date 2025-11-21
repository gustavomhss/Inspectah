# Inspectah — Sprint 15  
## Capítulo 4 — Runbook de Implementação, Prompts para Codex e Operação (Revisão)

### 0. Papel deste capítulo

Este capítulo é o **guia operacional definitivo da Sprint 15**. Ele converte:

- a visão de inteligência & blindagem (Capítulo 1),
- os gates e critérios de qualidade (Capítulo 2),
- o contrato de layout e arquitetura (Capítulo 3),

em três coisas muito concretas:

1. **Plano de implementação em ondas** para o Codex, com arquivos‑alvo claros e critérios de "feito".  
2. **Superprompts padronizados** para gerar ou refinar código sem desalinhar a sprint.  
3. **Runbook de operação e resposta a incidentes**, incluindo como rodar gates, interpretar scorecards e abastecer a S16 (hardening + ORR final).

Tudo aqui é prescritivo: é o **como fazer**, não o porquê.

---

### 1. Modo de uso e escopo

#### 1.1 Para quem este capítulo existe

1. **Codex (engenheiro de código da S15)**  
   Usa este capítulo como:
   - checklist de implementação (ondas 1–5),  
   - fonte oficial de caminhos de arquivos,  
   - fonte oficial de prompts para gerar/ajustar código.

2. **Operadores e devs humanos**  
   Usam este capítulo para:
   - rodar gates T0–T8 localmente/staging,  
   - ler scorecards e localizar evidências,  
   - seguir o procedimento padrão de investigação de incidentes.

3. **Time da S16 (hardening + ORR final)**  
   Usa este capítulo como:
   - mapa de ataque (onde a S15 vive no código e nos scripts),  
   - referência de comandos para reproduzir cenários de teste e incidentes.

#### 1.2 O que este capítulo cobre e o que não cobre

Cobre:

- ordem recomendada de implementação dos componentes da S15;  
- prompts para Codex **por bloco de responsabilidade** (Debunker, comitês, âncoras, gates/CI);  
- rotina diária/semanal de operação;  
- playbook de incidentes e hand‑off para S16.

Não cobre:

- design conceitual do Sistema de Blocos (Cap. 1 e S13–S14);  
- definição formal dos gates (Cap. 2);  
- alterações de layout que contradigam o Cap. 3 (rev) sem atualizá‑lo primeiro.

Se surgir conflito entre este capítulo e o Cap. 3 (rev) sobre filemap, o **Cap. 3 é a fonte de verdade para caminhos e nomes**.

---

### 2. Checklist pré‑S15 (para humanos)

Antes de acionar o Codex para implementar qualquer parte da S15:

1. **Repositório & branch**  
   - diretório: `/Users/gustavoschneiter/Documents/Inspectah`  
   - branch: `main` ou branch oficial da Sprint 15.

2. **S13–S14 estabilizadas**  
   - S13 (Truth‑DB Core) e S14 (Disputas & write path) com gates críticos em GO;  
   - sem bugs estruturais abertos que invalidem o modelo de log ou máquinas de estado.

3. **Capítulos da S15 alinhados**  
   - `Sprint 15/Capitulo 1.md` (visão)  
   - `Sprint 15/Capitulo 2 (rev).md` (gates)  
   - `Sprint 15/Capitulo 3 (rev).md` (contrato de layout)  
   - este `Sprint 15/Capitulo 4 (rev).md`.

4. **Ambiente local saudável**  
   - testes e CI de sprints anteriores executando com sucesso (por exemplo, `PYTHONPATH=. bin/ci_local.sh` ou equivalente definido no DNA);  
   - dependências necessárias para blockchain e observabilidade instaladas.

Se qualquer item falhar, a S15 deve ser pausada ou o problema deve ser tratado em S13–S14 antes de seguir.

---

### 3. Plano de implementação em ondas (Codex)

A S15 é implementada em **5 ondas**. Cada onda tem objetivo, arquivos‑alvo, tarefas e critérios de conclusão. O Codex deve seguir a ordem a seguir, evitando espalhar mudanças de forma aleatória.

#### Onda 1 — Esqueleto de módulos, contratos e scripts da S15

**Objetivo:** garantir que a estrutura de arquivos e assinaturas está pronta, alinhada ao Cap. 3, antes de adicionar lógica complexa.

**Arquivos‑alvo:**

- Debunker  
  - `inspectah/debunker/__init__.py`  
  - `inspectah/debunker/engine.py`  
  - `inspectah/debunker/rules.py`  
  - `inspectah/debunker/report_models.py`  
  - `inspectah/debunker/fixtures/` (vazios ou com exemplos mínimos).

- Comitês  
  - `inspectah/committees/__init__.py`  
  - `inspectah/committees/common.py`  
  - `inspectah/committees/v1_validator.py`  
  - `inspectah/committees/v2_multibrain.py`  
  - `inspectah/committees/v3_coherence.py`.

- Âncoras  
  - `inspectah/anchors/__init__.py`  
  - `inspectah/anchors/merkle.py`  
  - `inspectah/anchors/chain_client.py`  
  - `inspectah/anchors/batcher.py`  
  - `inspectah/anchors/registry.py`.

- Scripts de gates  
  - `bin/s15_t0_sanity.sh` … `bin/s15_t8_go_no_go.sh`  
  - `bin/s15_all_gates.sh`.

**Tarefas da Onda 1:**

1. Criar todos os arquivos listados, com docstrings explicando a intenção de cada módulo/função.  
2. Definir assinaturas mínimas (funções e classes) conforme descrito no Cap. 3 (rev).  
3. Implementar stubs de scripts `bin/s15_tX_*.sh` que verificam dependências e retornam código de saída não‑zero (placeholder).

**Feito quando:**

- Todos os caminhos de arquivo da S15 existem;  
- Os imports básicos funcionam (`python -m pytest` não explode por `ImportError` nos módulos novos);  
- `bin/s15_tX_*.sh` executam sem "command not found" (mesmo que terminem com `exit 1`).

---

#### Onda 2 — Debunker v1 funcional

**Objetivo:** transformar o Debunker em um componente concreto, pronto para T2 e para servir de insumo a V2/V3.

**Arquivos‑alvo:**

- `inspectah/debunker/report_models.py`  
- `inspectah/debunker/rules.py`  
- `inspectah/debunker/engine.py`  
- `inspectah/debunker/fixtures/`  
- `bin/s15_t2_debunker_offline.sh`.

**Tarefas da Onda 2:**

1. Modelos de relatório em `report_models.py`:  
   - `DebunkerReport`, `EvidenceItem`, `Contradiction`, `RiskLevel`, `Recommendation`, com docstrings e tipos claros.

2. Regras de risco em `rules.py`:  
   - perfis de risco por domínio (política, esporte, clima, fofoca, mandatos, projetos, ciência);  
   - funções para carregar/atualizar essas regras.

3. Motor em `engine.py`:  
   - `select_risky_claims(claims, config)`;  
   - `analyze_claim(claim, context)`;  
   - `recommend_action(report)`;  
   - integração mínima com o Sistema de Blocos via interfaces já existentes (sem reescrever S13–S14).

4. Fixtures em `inspectah/debunker/fixtures/`:  
   - pelo menos 5 domínios, com marcação de risco esperado e recomendação esperada.

5. Script T2 em `bin/s15_t2_debunker_offline.sh`:  
   - rodar Debunker sobre fixtures;  
   - gerar `out/scorecards/S15_T2_debunker_offline.json`;  
   - gravar relatórios em `out/evidence/S15_T2_debunker_offline/`.

**Feito quando:**

- `PYTHONPATH=. bin/s15_t2_debunker_offline.sh` roda, gera scorecard e evidências;  
- Em fixtures de alto risco, o Debunker marca risco alto e recomenda disputa/`questioned`;  
- Em casos com evidência clara, recomenda manutenção do estado com justificativa.

---

#### Onda 3 — Comitês V1/V2/V3 em fluxo

**Objetivo:** tornar `inspectah/committees/` apto a revisar decisões de disputa em três camadas reais.

**Arquivos‑alvo:**

- `inspectah/committees/common.py`  
- `inspectah/committees/v1_validator.py`  
- `inspectah/committees/v2_multibrain.py`  
- `inspectah/committees/v3_coherence.py`  
- `bin/s15_t3_committees_flow.sh`.

**Tarefas da Onda 3:**

1. Tipos em `common.py`:  
   - `CommitteeDecision`, `Vote`, `Reason`, enums de status (APPROVED, REJECTED, ESCALATE, NEED_MORE_EVIDENCE...).

2. V1 em `v1_validator.py`:  
   - checklists mecânicos de integridade;  
   - falhas sempre retornam decisão REJECTED com razão explícita.

3. V2 em `v2_multibrain.py`:  
   - orquestra múltiplos cérebros configuráveis;  
   - incorpora Promotores do Diabo usando relatórios do Debunker;  
   - gera parecer consolidado e registra divergências.

4. V3 em `v3_coherence.py`:  
   - avalia impacto global da decisão;  
   - rejeita estados incoerentes (campeões duplos, resultados incompatíveis etc.).

5. Script T3 em `bin/s15_t3_committees_flow.sh`:  
   - monta disputas de teste;  
   - atravessa Debunker → V1 → V2 → V3;  
   - gera scorecard e evidências.

**Feito quando:**

- `PYTHONPATH=. bin/s15_t3_committees_flow.sh` roda e produz `S15_T3_committees_flow.json` + evidências;  
- existem exemplos de decisões rejeitadas em cada camada (V1, V2, V3);  
- logs permitem reconstruir o caminho da decisão.

---

#### Onda 4 — Âncoras em blockchain + anti‑canetada

**Objetivo:** ligar o Sistema de Blocos a âncoras externas e blindar o write path contra canetadas.

**Arquivos‑alvo:**

- `inspectah/anchors/merkle.py`  
- `inspectah/anchors/chain_client.py`  
- `inspectah/anchors/batcher.py`  
- `inspectah/anchors/registry.py`  
- extensões em `inspectah/blocks/`  
- extensões em `inspectah/commands/`  
- scripts T1, T4, T5, T6.

**Tarefas da Onda 4:**

1. Merkle em `merkle.py`:  
   - construir árvore a partir de eventos/versões;  
   - gerar proofs para auditoria.

2. Cliente de chain em `chain_client.py`:  
   - função `submit_anchor(root)` com retorno de `tx_hash`;  
   - tratamento de erro/retry limitado.

3. Batching em `batcher.py`:  
   - regras de "quando ancorar" (volume/tempo);  
   - integração com `chain_client` e `registry`.

4. Registro em `registry.py`:  
   - criar âncora (`anchor_id`, `chain_id`, `tx_hash`);  
   - mapear fatos/versões para batches/âncoras;  
   - consultas para T4/T6.

5. Extensões de modelos em `inspectah/blocks/`:  
   - campos para referências a âncoras;  
   - invariantes de integridade.

6. Anti‑canetada em `inspectah/commands/`:  
   - proibir alterações diretas de estado;  
   - registrar pedidos de override como eventos/disputas;  
   - emitir logs específicos.

7. Ajustar scripts T1, T4, T5, T6 para considerar âncoras e anti‑canetada.

**Feito quando:**

- Existem cenários de teste com âncoras criadas e recuperáveis;  
- T1 detecta qualquer tentativa de override direto;  
- T4 e T6 usam âncoras em seus checks.

---

#### Onda 5 — Gates T0–T8 sólidos + CI + observabilidade

**Objetivo:** fechar a S15 com gates operacionais, CI rodando e observabilidade específica ativa.

**Arquivos‑alvo:**

- `bin/s15_t0_sanity.sh` … `bin/s15_t8_go_no_go.sh`  
- `bin/s15_all_gates.sh`  
- `.ci/sprint_15_gates.yml`  
- `.ci/sprint_15_nightly.yml` (se existir)  
- scripts/queries para T6.

**Tarefas da Onda 5:**

1. Preencher todos os scripts `bin/s15_tX_*.sh` conforme Cap. 2 e Cap. 3 (rev).  
2. Implementar `bin/s15_all_gates.sh` para rodar T0–T8 em ordem, com resumo final.  
3. Criar/ajustar `.ci/sprint_15_gates.yml` para rodar os gates críticos em PRs/branch principal.  
4. Implementar `.ci/sprint_15_nightly.yml` se a S15 demandar rodadas periódicas.  
5. Implementar script de T6 (`bin/s15_t6_observability.sh`) com consultas padrão e export de evidências.

**Feito quando:**

- `PYTHONPATH=. bin/s15_all_gates.sh` gera todos os scorecards `S15_T0`…`S15_T8`;  
- CI executa `.ci/sprint_15_gates.yml` e falha PRs quando gates críticos estão em NO_GO;  
- T6 consegue responder a perguntas chave sobre Debunker, comitês, âncoras e overrides.

---

### 4. Superprompts padronizados para Codex

Os superprompts abaixo são modelos oficiais. Podem ser ajustados, mas mantêm:

- contexto claro da S15,  
- arquivos‑alvo explícitos,  
- critérios de aceitação objetivos.

#### 4.1 Debunker v1

Trecho base de prompt para Codex:

"""
Você é o Codex trabalhando na Sprint 15 do projeto Inspectah. A S15 adiciona uma camada de inteligência e blindagem ao Sistema de Blocos (Debunker v1, comitês V1/V2/V3 e âncoras em blockchain). Este pedido foca apenas no Debunker v1.

Arquivos‑alvo:
- inspectah/debunker/report_models.py
- inspectah/debunker/rules.py
- inspectah/debunker/engine.py
- inspectah/debunker/fixtures/
- bin/s15_t2_debunker_offline.sh

Tarefas:
1. Implementar modelos de relatório do Debunker em report_models.py (DebunkerReport, EvidenceItem, Contradiction, RiskLevel, Recommendation), com tipos e docstrings claras.
2. Implementar regras de risco por domínio em rules.py, permitindo configurar thresholds por tema (política, esporte, clima, fofoca, mandatos, projetos, ciência).
3. Implementar engine.py com as funções select_risky_claims, analyze_claim e recommend_action, integrando com o Sistema de Blocos via interfaces já existentes.
4. Criar fixtures em inspectah/debunker/fixtures/ cobrindo pelo menos 5 domínios diferentes, com labels de risco esperado e recomendação esperada.
5. Implementar bin/s15_t2_debunker_offline.sh para rodar os cenários de fixtures, gerar out/scorecards/S15_T2_debunker_offline.json e evidências em out/evidence/S15_T2_debunker_offline/.

Critérios de aceitação:
- PYTHONPATH=. bin/s15_t2_debunker_offline.sh roda sem erros e produz scorecard + evidências.
- Em cenários de alto risco, o Debunker marca risco alto e recomenda disputa ou questioned.
- Em cenários com evidência clara, o Debunker recomenda manutenção do estado com justificativa.
- Código limpo, com testes básicos das funções centrais.
"""

#### 4.2 Comitês V1/V2/V3

"""
Você é o Codex na Sprint 15 do Inspectah. Precisamos implementar a camada de comitês V1/V2/V3 que revisa decisões de disputas com base em Debunker + regras do Sistema de Blocos.

Arquivos‑alvo:
- inspectah/committees/common.py
- inspectah/committees/v1_validator.py
- inspectah/committees/v2_multibrain.py
- inspectah/committees/v3_coherence.py
- bin/s15_t3_committees_flow.sh

Tarefas:
1. Em common.py, criar tipos e enums para CommitteeDecision, Vote, Reason e status de decisão.
2. Em v1_validator.py, implementar checagens mecânicas (máquinas de estado, integridade de IDs, evidências mínimas).
3. Em v2_multibrain.py, implementar orquestração de múltiplos cérebros, incluindo Promotores do Diabo que usam relatórios do Debunker para levantar objeções.
4. Em v3_coherence.py, implementar verificações de coerência global, detectando estados impossíveis (campeões duplos, resultados incompatíveis, etc.).
5. Em bin/s15_t3_committees_flow.sh, criar script que dispare disputas de teste atravessando V1, V2 e V3, gerando out/scorecards/S15_T3_committees_flow.json e evidências em out/evidence/S15_T3_committees_flow/.

Critérios de aceitação:
- PYTHONPATH=. bin/s15_t3_committees_flow.sh roda com sucesso e gera scorecard + evidências.
- Há exemplos claros de decisões rejeitadas em V1, V2 e V3 em cenários de teste.
- Logs permitem reconstruir o caminho completo da decisão, alinhado com o Cap. 2 e Cap. 3.
"""

#### 4.3 Âncoras + Anti‑canetada

"""
Você é o Codex trabalhando na Sprint 15 do Inspectah. Precisamos implementar o módulo de âncoras em blockchain e as regras anti‑canetada no Sistema de Blocos.

Arquivos‑alvo:
- inspectah/anchors/merkle.py
- inspectah/anchors/chain_client.py
- inspectah/anchors/batcher.py
- inspectah/anchors/registry.py
- inspectah/blocks/ (extensões para campos de âncoras)
- inspectah/commands/ (regras anti‑canetada)
- scripts s15 T1, T4, T5, T6

Tarefas:
1. Implementar Merkle trees e proofs em merkle.py.
2. Implementar cliente de chain em chain_client.py para pelo menos uma testnet, com submit_anchor(root) retornando tx_hash e lidando com falhas.
3. Implementar batcher.py para agrupar eventos/versões em batches configuráveis por volume/tempo.
4. Implementar registry.py para registrar âncoras, mapear fatos/versões para batches e permitir consultas.
5. Atualizar modelos em inspectah/blocks/ para referenciar âncoras relevantes.
6. Implementar, em inspectah/commands/, regras que proíbem alterações diretas de estados; qualquer pedido externo de override deve virar evento/disputa com logs específicos.
7. Ajustar scripts de T1, T4, T5 e T6 para considerar âncoras e checar se o modelo anti‑canetada está operando.

Critérios de aceitação:
- Cenários de teste criam âncoras que podem ser recuperadas via APIs de anchors/.
- T1 e T4 enxergam essas âncoras e as usam nas verificações.
- Não há rotas de override direto detectadas em T1.
- Eventos de override aparecem em evidências/logs usados em T6.
"""

#### 4.4 Gates T0–T8 + CI

"""
Você é o Codex na Sprint 15 do Inspectah. Precisamos finalizar os scripts de gates T0–T8, o orquestrador bin/s15_all_gates.sh e o workflow de CI .ci/sprint_15_gates.yml.

Arquivos‑alvo:
- bin/s15_t0_sanity.sh … bin/s15_t8_go_no_go.sh
- bin/s15_all_gates.sh
- .ci/sprint_15_gates.yml
- .ci/sprint_15_nightly.yml (se aplicável)

Tarefas:
1. Preencher cada bin/s15_tX_*.sh com a lógica descrita no Capítulo 2 (objetivo, entradas, saídas, scorecards e evidências) e filemap do Cap. 3 (rev).
2. Implementar bin/s15_all_gates.sh para rodar T0–T8 em sequência, imprimindo um resumo final de PASS/FAIL por gate.
3. Criar/ajustar .ci/sprint_15_gates.yml para rodar os gates críticos da S15 em PRs e na branch principal, falhando o job quando T1, T2, T3, T4 ou T6 estiverem em NO_GO.
4. Opcionalmente, implementar .ci/sprint_15_nightly.yml para rodar subconjunto de T2–T6 em staging.

Critérios de aceitação:
- PYTHONPATH=. bin/s15_all_gates.sh roda ponta‑a‑ponta, gerando todos os scorecards S15_T0…S15_T8.
- CI executa .ci/sprint_15_gates.yml com resultados consistentes com a execução local.
- Scorecards e evidências são gravados exatamente nos caminhos definidos no Cap. 3 (rev).
"""

---

### 5. Runbook de operação diária e semanal

#### 5.1 Rotina diária mínima

1. **Rodar gates críticos (pelo menos T2, T3, T4, T6) em ambiente de desenvolvimento ou staging:**

```bash
cd /Users/gustavoschneiter/Documents/Inspectah
PYTHONPATH=. bin/s15_t2_debunker_offline.sh
PYTHONPATH=. bin/s15_t3_committees_flow.sh
PYTHONPATH=. bin/s15_t4_golden_scenarios.sh
PYTHONPATH=. bin/s15_t6_observability.sh
```

2. **Verificar scorecards gerados:**

- `out/scorecards/S15_T2_debunker_offline.json`  
- `out/scorecards/S15_T3_committees_flow.json`  
- `out/scorecards/S15_T4_golden_scenarios.json`  
- `out/scorecards/S15_T6_observability.json`

3. **Checar painéis de observabilidade (T6):**

- olhar rapidamente métricas de número de claims de alto risco, disputas, âncoras recentes, overrides;  
- observar qualquer anomalia (picos súbitos, falhas repetidas, latências fora de padrão).

4. **Registrar incidentes:**

- sempre que um gate crítico falhar (T2, T3, T4 ou T6), abrir issue com links diretos para scorecards e evidências.

#### 5.2 Rotina semanal recomendada

1. **Rodar a bateria completa da S15 em staging:**

```bash
cd /Users/gustavoschneiter/Documents/Inspectah
PYTHONPATH=. bin/s15_all_gates.sh
```

2. **Rodar manualmente o workflow de CI da S15 (se aplicável):**

- acionar `.ci/sprint_15_gates.yml` em modo on‑demand;  
- comparar resultados com a execução local.

3. **Revisar `docs/sprint_15_orr_summary.md`:**

- atualizar a seção de riscos residuais, se surgiram novos incidentes;  
- documentar mitigação planejada para a S16.

---

### 6. Playbook de investigação de incidente

Quando houver suspeita de erro grave, manipulação de dados ou "canetada", seguir os passos:

1. **Identificar o alvo:**
   - obter ID do bloco/fato/versão contestado.

2. **Rastrear histórico no Sistema de Blocos:**
   - usar APIs ou ferramentas internas para listar eventos históricos daquele objeto (criações, atualizações, disputas, resoluções).

3. **Inspecionar Debunker e comitês:**
   - localizar relatórios do Debunker relacionados;  
   - verificar decisões de V1, V2 e V3 nos logs e evidências de T3/T4.

4. **Checar âncoras:**
   - usar `inspectah/anchors/registry.py` para encontrar batches e âncoras ligados ao fato/versão;  
   - validar se a versão suspeita estava ou não presente em determinada âncora histórica.

5. **Buscar eventos de override:**
   - consultar logs e evidências usados em T6 para eventos de `LegalOverrideSolicitado` ou similares;  
   - verificar como o pedido foi tratado (disputa aberta, rejeição, decisão parcial).

6. **Classificar o incidente:**
   - falha de implementação (bug),  
   - falha de regra (Debunker/comitês subconfigurados),  
   - falha de processo (override realizado fora do fluxo),  
   - falha de observabilidade (impossível rastrear o que houve).

7. **Gerar mini‑relatório de incidente:**
   - descrevendo linha do tempo, causa provável, gates que capturaram ou não o problema;  
   - sugerindo ajustes de regras ou de implementação para S15 ou S16.

---

### 7. DoD operacional da Sprint 15

Do ponto de vista deste runbook, a S15 só pode ser considerada concluída quando:

1. **Plano em ondas aplicado:**  
   - todas as ondas 1–5 implementadas e integradas;  
   - arquivos e caminhos batendo com o Cap. 3 (rev).

2. **Gates T0–T8 rodando ponta‑a‑ponta:**  
   - `PYTHONPATH=. bin/s15_all_gates.sh` gera todos os scorecards S15_T0…S15_T8 com estados consistentes;  
   - scripts idempotentes, adequados para uso em CI e local.

3. **CI da S15 ativo:**  
   - `.ci/sprint_15_gates.yml` rodando em PRs e/ou na branch principal;  
   - PR bloqueado quando gates críticos estão em NO_GO.

4. **Observabilidade útil:**  
   - T6 responde rapidamente a perguntas chave sobre Debunker, comitês, âncoras e overrides;  
   - logs e painéis são suficientes para investigar incidentes.

5. **Docs consolidados:**  
   - `docs/sprint_15_overview.md`, `docs/sprint_15_filemap_e_arquitetura.md` e `docs/sprint_15_orr_summary.md` atualizados;  
   - este Cap. 4 (rev) refletindo o estado real do código e scripts.

---

### 8. Hand‑off para a Sprint 16

Com a S15 concluída segundo este Capítulo 4 (rev), a S16 recebe:

- uma **camada funcional de inteligência & blindagem** (Debunker + comitês + âncoras + anti‑canetada);  
- um conjunto de **gates T0–T8 robustos**, com scorecards e evidências reproduzíveis;  
- **CI dedicado à S15**, que pode ser extendido ou stressado na S16;  
- **observabilidade específica**, que permite construir Threat Models e testes de ataque bem informados;  
- documentação suficiente para atacar, endurecer e, por fim, aprovar o Sistema de Blocos em um ORR final.

Este capítulo encerra a especificação da Sprint 15 do ponto de vista operacional: o que falta a partir daqui não é mais "implementar a S15", e sim **testar, atacar e endurecer o que já está de pé** — missão central da Sprint 16.

