# Inspectah — Sprint 28
## Capítulo 6 — Bloco 2
### Lessons Learned da Sprint 28 (Técnicas, Produto/UX e Processo)

---

### 6.2.1 Lessons Learned técnicas

**LL-T1 — Fonte como entidade de primeira classe simplifica tudo o resto**  
Consolidar `Source` (campos, invariantes, enums, transições de estado) antes de discutir ingestão ou console se mostrou decisivo. Sempre que o time tentou raciocinar “a partir da ingestão”, sem o modelo de fonte fechado, a conversa ficou nebulosa, com decisões inconsistentes.

Regra derivada:
- Próximos épicos que envolvam entidades centrais (ex.: `Case`, `Theme`, `Evidence`, `Anchor`) devem seguir a mesma ordem:  
  1) fechar o modelo de domínio e invariantes,  
  2) só então estabilizar APIs e UIs,  
  3) por fim, plugar pipelines (ingestão, jobs, comitês, etc.).

---

**LL-T2 — Admin API como contrato canônico de operação é essencial**  
A decisão de ancorar todas as operações de fonte em `/admin/sources` evitou a proliferação de caminhos paralelos (scripts de banco, jobs ad hoc, comandos diretos). Quando a Admin API é a fonte única de verdade para mutações, fica claro o que é suportado, auditável e testável.

Regra derivada:
- Em domínios críticos, toda mutação em produção deve passar por uma Admin API bem definida; CLIs, UIs e automações são clientes dessa API, nunca "atalhos" diretos ao banco.

---

**LL-T3 — Ingestão 2.0 obedecendo `mode` + `state` é uma simplificação poderosa**  
Separar explicitamente:
- `mode` (AUTO/MANUAL) — se a fonte entra ou não no scheduler, e  
- `state` (ACTIVE/DISABLED/DEPRECATED) — se a fonte está ligada, desligada ou fora de uso,

criou uma matriz mental muito clara tanto para backend quanto para operação. Em vez de regras espalhadas (flags, colunas, ifs dispersos), a decisão de ingestão passa a ser: "fonte está em `mode=AUTO` e `state=ACTIVE`?".

Regra derivada:
- Sempre que houver lógica de eligibilidade/agendamento, ela deve ser expressa em poucos campos de domínio com semântica forte, não em checklists escondidos em código.

---

**LL-T4 — Gates estruturados são o seguro contra regressão silenciosa**  
A amarração G0–G7 em S28, com destaque para G4 (integração ingestão × fonte) e o papel de regressão em relação a S21/S22, mostrou que:
- Testes unitários isolados não são suficientes quando se mexe em componentes centrais.  
- Ter scripts de gates nomeados, scorecards e evidências força o time a provar que não quebrou o que já funcionava.

Regra derivada:
- Toda sprint que toque pipelines estruturais deve ter pelo menos um gate explícito de regressão (no espírito de G5), referenciando evidencia de sprints anteriores.

---

**LL-T5 — Filemap e nomes de scripts são parte da arquitetura mental**  
O padrão de nomes como `bin/s28_g4_sources_ingestion_integration.sh` não é só estética; ele condiciona o raciocínio do time. Antes mesmo de abrir o arquivo, todos sabem o objetivo daquele gate.

Regra derivada:
- Padrões de nome (scripts, pastas, scorecards) devem ser considerados parte da arquitetura. Para S26–S65, manter o formato:  
  `bin/sXX_gY_<dominio>_<proposito>.sh`  
  `out/evidence/SXX_GY_<nome_do_gate>/`  
  `out/scorecards/SXX_GY_<nome_do_gate>.json`.

---

### 6.2.2 Lessons Learned de produto / UX

**LL-P1 — Fluxos A–D funcionam como MVP, mas não esgotam o problema**  
Focar em quatro fluxos principais (criar, editar, desativar, reativar) foi excelente para dar uma linha clara de chegada. Porém, já ficou evidente que operação real exige mais camadas:
- filtros avançados (por criticidade, modo, domínio, tipo),  
- contexto (quais casos/temas essa fonte alimenta),  
- visão rápida de saúde (erros, tempo desde última ingestão),  
- histórico de ações.

Regra derivada:
- Sempre tratar o "CRUD básico" como piso de produto, nunca como teto — a partir do uso real, evoluir para ferramentas de operação de verdade.

---

**LL-P2 — Console sem trilha de auditoria gera insegurança implícita**  
Mesmo com `state_reason` e timestamps, a ausência de uma timeline explícita de ações torna operadores mais cautelosos (ou inseguros) ao mexer em fontes sensíveis. Em contextos de alta criticidade, o operador quer ver claramente: "quem desligou isso, quando e por quê".

Regra derivada:
- Toda tela que permita ações de alto impacto (ON/OFF, DEPRECATE, mudanças em criticidade) deve vir acompanhada de um painel simples de histórico de ações por entidade.

---

**LL-P3 — Glossário mínimo de domínio alinha PO, dev e operação**  
Termos como `mode`, `state`, `criticality` e "fonte crítica" geram ruído se não tiverem definição escrita. Assim que S28 consolidou essas definições no Cap.1/Cap.2, discussões ficaram menos ambíguas e decisões de UX ficaram mais coerentes.

Regra derivada:
- Sempre que uma sprint introduzir novos conceitos de domínio, o Cap.1 precisa trazer um mini-glossário, mesmo que enxuto, usado como referência única pelo resto do documento.

---

**LL-P4 — Mostrar impacto da ação no contexto reduz medo de usar o console**  
Operadores hesitam em desativar fontes sem entender onde aquela fonte é usada. Em S28 isso apareceu como percepção, mesmo que ainda não haja modelagem formal de "tema/caso".

Regra derivada:
- Assim que o mapeamento fonte → tema/caso estiver disponível (em sprints futuras), o console deve mostrar explicitamente o impacto de desativar uma fonte (ex.: "alimenta X pipelines e Y painéis").

---

### 6.2.3 Lessons Learned processuais (Playbook, squads, Codex)

**LL-PR1 — Cap.1–3 precisam estar minimamente estáveis antes de falar em tasks**  
Quando o time tentou antecipar tasks/cmds de Cap.4 com Cap.1–3 ainda flutuando, surgiram mudanças de escopo e retrabalho. Em contraste, quando Cap.1–3 foram fechados primeiro, Cap.4 fluiu mais naturalmente.

Regra derivada:
- Respeitar a ordem do Playbook v2/v3 em sprints núcleo:  
  1) Cap.1 — Contexto & Problemas,  
  2) Cap.2 — Gates, métricas & DoD,  
  3) Cap.3 — Arquitetura & Filemap,  
  4) só então Cap.4 — Execução & Evidências.

---

**LL-PR2 — Gates como contrato com Codex funcionam melhor que checklists textuais**  
Ao invés de frases vagas do tipo "rodar testes de ingestão", a S28 usou gates concretos: scripts em `bin/`, diretórios de evidências, scorecards. Isso facilitou enormemente tanto o trabalho do Codex quanto a leitura humana da sprint.

Regra derivada:
- Qualquer requisito relevante deve virar gate nomeado (Gx), com script + scorecard + pasta de evidência. Checklists textuais sozinhos não sustentam a disciplina da trilha S26–S65.

---

**LL-PR3 — Cap.5 e Cap.6 precisam ser concluídos dentro da própria sprint**  
Há sempre a tentação de deixar riscos, backlog, learnings e anti-gaps para "depois do merge". Em S28, fazê-los dentro da sprint permitiu que E27.2/E27.3 já nascessem com escopo mais nítido e prioridades claras.

Regra derivada:
- Tratar Cap.5 e Cap.6 como parte da definição de pronto. Nenhuma sprint núcleo é considerada "completamente encerrada" sem riscos/dívidas/backlog (Cap.5) e síntese de aprendizado/roadmap (Cap.6).

---

**LL-PR4 — IDs estáveis para riscos, dívidas e backlog são multiplicadores de clareza**  
Usar padrões como `R-28-*`, `D-28-*`, `B-27.2-*` permitiu referência cruzada entre capítulos e facilitará a criação de tickets e issues correlacionadas.

Regra derivada:
- Fixar convenção de IDs por sprint/épico e usá-la tanto na spec quanto em boards/tickets. Exemplo:
  - Riscos: `R-<sprint>-<grupo>-<n>`  
  - Dívidas: `D-<sprint>-<eixo>-<n>`  
  - Backlog: `B-<épico>.<sprint>-<n>`.

---

**LL-PR5 — Squad certo na hora certa evita debates difusos**  
Sempre que discussões de S28 envolveram fonte como entidade, ingestão e operação, a presença combinada de backend, ingestão, produto e observabilidade foi decisiva. Em contrapartida, discussões com composição de squad errada tendiam a girar em círculos.

Regra derivada:
- Para épicos como E27, garantir que workshops de definição envolvam o "quadrilátero" correto: Domínio (PO), Backend, Ingestão, Observabilidade — e, quando o tema encostar em verdade/fato, também Verdade & Interpretação.

---

Com este Bloco 2, o Capítulo 6 captura as principais lições da Sprint 28 em três dimensões — técnica, produto/UX e processo — e gera regras derivadas que devem ser carregadas para E27.2/E27.3 e para o restante da trilha S26–S65. Os próximos blocos consolidam as dívidas técnicas em uma visão priorizada e conectam essas lições ao roadmap e aos anti-gaps para as próximas sprints.