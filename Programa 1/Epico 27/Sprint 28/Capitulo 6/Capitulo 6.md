# Inspectah — Sprint 28
## Capítulo 6 — Learnings, Roadmap & Anti-gaps
### E27.1 — CRUD & ON/OFF de Fonte

---

### 6.1 Objetivo do Capítulo 6

Capítulo 6 é onde a Sprint 28 para, respira e pensa.

Depois de:
- definir contexto e problemas (Cap.1),
- fixar estados-alvo e gates (Cap.2),
- detalhar arquitetura e filemap (Cap.3),
- desenhar a execução e os scripts de evidência (Cap.4),
- mapear riscos, dívidas e backlog de continuidade (Cap.5),

este capítulo responde:

1. **O que aprendemos de fato com a S28?**  
2. **Que dívidas técnicas precisam ser carregadas de forma consciente, como "linha de base" para E27.2/E27.3?**  
3. **Como a S28 mexe no roadmap maior do Programa 1 / E27?**  
4. **Que anti-gaps e recomendações geramos para as próximas sprints, para não repetir erros ou buracos?**

Capítulo 6 não reabre a espec; ele consolida **aprendizado e meta-camadas** da Sprint 28.

---

### 6.2 Bloco 6.1 — Lessons Learned da Sprint 28

#### 6.2.1 Lessons Learned técnicas

1. **Fonte como entidade de primeira classe simplifica o resto**  
   Consolidar `Source` (campos, invariantes, enums) antes de discutir ingestão ou console se mostrou decisivo. Sempre que o time tentou raciocinar "a partir de ingestão", sem o modelo de fonte fechado, o debate ficou nebuloso.  
   **Regra derivada:** próximos épicos que envolvam entidades centrais (ex.: `Case`, `Theme`, `Evidence`) devem seguir a mesma lógica: modelo canonizado primeiro, APIs só depois.

2. **Admin API como contrato canônico de operação é essencial**  
   A decisão de ancorar todas as operações de fonte em `/admin/sources` evitou o caos de paths paralelos (scripts soltos, migrations ad hoc, etc.).  
   **Regra derivada:** em domínios críticos, a Admin API deve ser o único caminho oficial de mutação; qualquer tooling (UI, CLIs, jobs) deve ser client dessa API.

3. **Ingestão 2.0 obedecendo `mode` + `state` é uma simplificação poderosa**  
   A separação conceitual entre "fonte automática vs manual" (`mode`) e "fonte ligada/desligada/deprecada" (`state`) criou uma matriz mental clara tanto para dev quanto para operação.  
   **Regra derivada:** sempre que houver decisão de agendamento/eligibilidade, ela deve ser baseada em um par bem definido de flags de domínio, não em checklists espalhados.

4. **Gates estruturados funcionam bem para evitar regressão**  
   A amarração G0–G7 (especialmente G4, G5 e G7):  
   - tornou explícita a proteção contra regressões em ingestão e legados S21/S22;  
   - evitou que a sprint "passasse" com apenas testes unitários.  
   **Regra derivada:** sprints que mexem em pipelines críticos devem ter pelo menos um gate dedicado a regressão de sprints anteriores (modelo "G5").

5. **Filemap e nomes de scripts influenciam clareza do raciocínio**  
   Nomear scripts como `s28_g4_sources_ingestion_integration.sh` deixa o objetivo explícito antes mesmo de ler o código.  
   **Regra derivada:** seguir padrão `sXX_gY_<domínio>_<propósito>.sh` como convenção fixa em S26–S65.

---

#### 6.2.2 Lessons Learned de produto / UX

1. **Fluxos A–D são bons como MVP, mas não suficientes como produto completo**  
   Focar em criar/editar/desativar/reativar funcionou como linha de chegada de S28, mas já ficou claro que operação real exige:
   - filtros avançados,  
   - visão por criticidade,  
   - contexto (grupo, tema, caso),  
   - histórico de ações.

2. **Console sem trilha de auditoria gera insegurança implícita**  
   Mesmo com `state_reason`, a falta de uma timeline formal de ações reduz a confiança dos operadores ao mexer em fontes críticas.  
   **Regra derivada:** toda ferramenta que permita ações de alto impacto deve vir acompanhada de uma forma clara de ver "quem mexeu em quê".

3. **Dicionário mínimo de termos ajuda a alinhar PO, dev e operação**  
   Conceitos como `mode`, `state`, `criticality` precisam estar escritos, não apenas implícitos. A S28 mostrou ganho imediato quando o time parou e escreveu essas definições em Cap.1/Cap.2.  
   **Regra derivada:** toda sprint que introduz novos conceitos de domínio deve ter um mini-glossário no Cap.1.

---

#### 6.2.3 Lessons Learned processuais (Playbook, squads, Codex)

1. **Escrever Cap.1–3 antes de discutir tasks continua sendo obrigatório**  
   Sempre que a conversa tentou pular direto para "como o Codex vai executar" antes de Cap.1–3 estarem firmes, surgiram ambiguidades.  
   A S28 confirmou o valor da ordem Playbook v3:  
   **Cap.1 → Cap.2 → Cap.3 → só depois Cap.4–6.**

2. **Gates como contrato com Codex funcionam melhor que checklists soltos**  
   O fato de cada gate ter:  
   - um script concreto em `bin/`,  
   - um scorecard em `out/scorecards/`,  
   - uma pasta de evidências em `out/evidence/`  
   deu ao Codex e aos devs um alvo objetivo.  
   **Regra derivada:** qualquer requisito importante deve ter um gate nomeado, não apenas um parágrafo no texto.

3. **Cap.5 e Cap.6 precisam ser completados ainda na sprint, não "depois"**  
   A tentação natural é empurrar aprendizados e dívidas para depois do merge. Na S28, explicitá-los dentro da própria sprint ajudou a ajustar backlog de E27.2/E27.3 imediatamente.  
   **Regra derivada:** Cap.5–6 não são "pós-mortem opcional"; são parte oficial da definição de pronto da sprint.

4. **IDs estáveis (R-28-*, D-28-*, B-27.*) são cruciais para rastreabilidade**  
   Dar IDs para riscos, dívidas e backlog facilitou referenciar itens entre capítulos.  
   **Regra derivada:** manter padrão de IDs (por sprint/épico) e reutilizá-los em tickets/boards.

---

### 6.3 Bloco 6.2 — Dívidas técnicas (visão consolidada)

Cap.5 Bloco 3 já fez o inventário detalhado de dívidas técnicas (D-28-AUD-1, D-28-VAL-1, etc.).  
Aqui, o foco é consolidar e priorizar essas dívidas em uma visão compacta, para facilitar decisão de alocação em E27.2/E27.3.

#### 6.3.1 Top 5 dívidas técnicas prioritárias

1. **D-28-AUD-1 — `SourceActionLog` inexistente**  
   - **Por que é prioritária:** sem log estruturado de ações, qualquer incidente envolvendo fontes exige investigação manual e frágil.  
   - **Consequência de não atacar:** acumulação de decisões não rastreáveis, erosão da confiança na camada de operação.  
   - **Recomendação:** tratar como item obrigatório em E27.2.

2. **D-28-VAL-1 — Validações por tipo ausentes**  
   - **Por que é prioritária:** reduz erro humano no ponto de entrada (formulário/API), evitando que problemas só apareçam na ingestão.  
   - **Recomendação:** começar em E27.2 com 1–2 tipos críticos, estendendo depois.

3. **D-28-OBS-1 — Métricas por fonte/estado/mode inexistentes**  
   - **Por que é prioritária:** sem métricas, operação de fontes depende de logs.  
   - **Recomendação:** instrumentação mínima em E27.2, base para dashboards em E27.3.

4. **D-28-VAL-2 — Wizards inexistentes para fontes complexas**  
   - **Por que é prioritária (nível 2):** melhora significativamente onboarding de operadores, mas depende de D-28-VAL-1.  
   - **Recomendação:** posicionar como item core de E27.3, após consolidar validações.

5. **D-28-GOV-1 — Falta de fluxo de aprovação sistêmico para fontes críticas**  
   - **Por que é prioritária (governança):** sem isso, organização permanece dependente de processos informais.  
   - **Recomendação:** tratar em E27.3+ em conjunto com espec de papéis e permissões.

---

#### 6.3.2 Dívidas técnicas que podem ser tratadas incrementalmente

Algumas dívidas podem ser atacadas em modo "incremental", ao invés de exigir uma sprint inteira dedicada:

- **Refinamentos de migrations (`D-28-T3`)**: incorporar padrões mais cuidadosos de migração conforme novos campos forem surgindo em futuras sprints.  
- **Ajustes finos de invariantes vs API (`D-28-T2`)**: endereçar sempre que uma nova feature tocar transições de estado em `Source`.  
- **Pequenos aprimoramentos de observabilidade (`D-28-OBS-2`)**: adicionar gráficos simples e painéis em paralelo a E27.2/E27.3 conforme métricas forem ficando disponíveis.

---

### 6.4 Bloco 6.3 — Impacto da S28 no Roadmap

Esta seção liga explicitamente o que S28 fez ao que muda no roadmap maior.

#### 6.4.1 Dentro do Épico E27

1. **S28 como "núcleo duro" de E27.1**  
   - Consolida o mínimo inegociável:  
     - modelo `Source`,  
     - Admin API CRUD & ON/OFF,  
     - console v2 funcional,  
     - ingestão obedecendo `mode` + `state` de forma determinística.  
   - A partir de S28, qualquer discussão sobre fontes parte desse piso.

2. **E27.2 ganha escopo muito mais claro**  
   Com Cap.5–6, E27.2 deixa de ser "próximas melhorias vagas" e passa a ter eixos nítidos:  
   - auditoria básica (log de ações),  
   - validações por tipo,  
   - métricas por fonte,  
   - filtros avançados na UI.

3. **E27.3 se torna sprint de "polimento avançado" de operação de fontes**  
   - timeline de ações,  
   - wizards,  
   - dashboards de operação,  
   - políticas sistêmicas para fontes críticas.

4. **Coordenação com outros programas**  
   - Verdade & Interpretação: S28 prepara o terreno para conectar fontes a reputação, comitês e Sistema de Blocos (B-LONG-2).  
   - Cockpit/Admin: S28 estabelece padrões para telas de operação (filtros, históricos, relação com métricas) que podem ser replicados em outros módulos.

---

#### 6.4.2 No Programa 1 e trilha S26–S65

1. **Confirmação de que o modelo 6×4 funciona na prática**  
   S28, seguindo Playbook v3 (6 capítulos × 4 blocos), reforça que a estrutura aguenta um épico real e complexo sem explodir em caos.

2. **Refinamento do papel de Cap.5 e Cap.6 no ciclo de vida da sprint**  
   - Cap.5: amarra riscos, dívidas e backlog imediato.  
   - Cap.6: destila aprendizado e conecta à trilha S26–S65 como um todo (roadmap e anti-gaps).  
   Esse padrão deve ser replicado nas próximas sprints núcleo do Programa 1.

3. **Alinhamento com Roadmap global (arquivo `Roadmap.md`)**  
   - S28 "cumpre" uma fatia inteira de E27.  
   - E27.2/E27.3 podem agora ser mapeadas diretamente no Roadmap com base em B-27.2-* e B-27.3-*.

---

### 6.5 Bloco 6.4 — Anti-gaps & Recomendações

Este bloco registra gaps percebidos e recomendações explícitas para as próximas sprints, para que o time futuro não precise reaprender as mesmas lições.

#### 6.5.1 Anti-gaps de especificação

1. **Sempre explicitar glossário mínimo no Cap.1 quando surgirem novos conceitos de domínio**  
   Evita debates laterais sobre o significado de `mode`, `state`, `criticality`, etc.

2. **Garantir que todos os estados-alvo críticos tenham pelo menos um cenário E2E em Cap.5**  
   Se um estado-alvo não é coberto por nenhum cenário E2E, ele tende a ser esquecido na execução.

3. **Evitar misturar escopo de Cap.5 (ORR & operação) com Cap.6 (aprendizado & roadmap)**  
   Em S28, houve tendência natural de colocar backlog e risco tanto em 5 quanto em 6; a distribuição atual (Cap.5 = riscos/backlog; Cap.6 = síntese, prioridades e impacto em roadmap) deve ser mantida.

---

#### 6.5.2 Anti-gaps de execução

1. **Rodar G5 (sanity de legados) antes de sonhar com GO**  
   S28 mostrou o valor de G5 para proteger S21/S22. Em sprints futuras, qualquer sprint que mexa em componentes centrais deve ter um gate similar.

2. **Não empurrar Cap.5–6 para "pós-merge"**  
   Lessons Learned e dívidas precisam ser escritas enquanto a sprint ainda está quente.  
   Recomendação: tratar Cap.6 como parte do último wave de execução (Cap.4.4 deve incluir tasks explícitas de redação Cap.5–6).

3. **Expandir uso de IDs de risco/dívida/backlog em tickets reais**  
   Próximas sprints devem referenciar `R-28-*`, `D-28-*` e `B-27.*` nos próprios tickets, para manter rastreabilidade entre spec e execução.

---

#### 6.5.3 Anti-gaps de governança

1. **Formalizar política de uso da Admin API como único caminho de mutação em produção**  
   Isso deve ser registrado tanto em documentos internos quanto em configurações de permissão/acesso.

2. **Definir desde já quem é o owner de fontes críticas**  
   E27.2/E27.3 devem aproveitar a existência de criticidade para associar responsáveis claros a grupos de fontes.

3. **Trazer o squad Verdade & Interpretação cedo para discutir auditoria e governança de fontes**  
   Mesmo que o Sistema de Blocos ainda esteja em Fase 2, envolver o squad na definição de `SourceActionLog` e de políticas de aprovação evita retrabalho futuro.

---

### 6.6 Fechamento

A Sprint 28 não é só a sprint que ligou ON/OFF de fonte de forma decente.  
Ela é também a sprint que:
- consolidou um padrão de especificação 6×4 em um épico real (E27.1),
- criou uma base auditável para futuras decisões sobre fontes,
- deixou um mapa claro de riscos, dívidas e backlog,
- e registrou, neste Capítulo 6, um conjunto de recomendações concretas para que E27.2/E27.3 e as próximas sprints do Programa 1 partam de um patamar mais alto.

Capítulo 6 encerra a documentação da Sprint 28 com a cabeça no futuro: menos surpresa, mais previsibilidade, mais verdade e menos entropia na operação de fontes do Inspectah.

