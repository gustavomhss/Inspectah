# Inspectah — Sprint 24 – Capítulo 1.3  
## Objetivos da Sprint (OKRs locais, versão 2)

Este sub‑capítulo traduz o propósito macro da Sprint 24 — **Debunker v0 & Humano‑no‑Loop (Camada de Contestação e Revisão de Claims)** — em um conjunto de **objetivos concretos**, com **resultados‑chave mensuráveis**, alinhados ao Sprint Playbook v2 e diretamente conectados às sprints anteriores (S21–S23) e à S25.

A S24 é o elo entre:
- o que o Inspectah **entende** (S23 – interpretação e classificação),
- o que o Inspectah **contesta e revisa com humanos** (S24 – debunker v0 + humano‑no‑loop),
- o que o Inspectah, mais à frente, **promove a verdade/fato** (S25 – governança e Truth‑DB).

Os objetivos abaixo são escritos para:
1. Orientar **design, arquitetura e execução** da sprint.
2. Servir de base explícita para os **gates de validação** do Capítulo 2.
3. Guiar as decisões do Squad Verdade & Interpretação e do Squad Debunker & Humano‑no‑Loop.

Cada objetivo tem um identificador (O1, O2, …) e resultados‑chave (KR‑x.y) que poderão ser facilmente rastreados em scorecards e evidências (out/scorecards/S24_*.json, out/evidence/S24_* / docs/sprint_24_*).

---

## O1 — Tornar contestação um “primeiro‑class” citizen do Inspectah

**Descrição:** formalizar a contestação como um fluxo explícito do sistema: onde surgem conflitos/alertas, como viram issues estruturadas e como são tratados por humanos e, no futuro, pela S25.

**Resultados‑chave:**
- **KR‑1.1 – Modelo de domínio consolidado:** existir um **modelo de domínio S24** revisado pelo Squad Verdade & Interpretação que descreva, no mínimo: `DebunkIssue`, `DebunkDecision`, `DebunkAction`, `DebunkQueue`, `DebunkPolicy`, `DebunkEvidenceLink`, com estados e transições documentados em nível de máquina de estados. O modelo deve estar versionado em `docs/sprint_24_cap_3_arquitetura.md` e refletido em esquemas (DB + APIs).
- **KR‑1.2 – Fluxo ponta‑a‑ponta mapeado:** haver um **diagrama ponta‑a‑ponta** que mostre claramente o caminho: `claims S23 → detecção de conflito/risco → criação de DebunkIssue → triagem → decisão humana → emissão de DebunkDecision → sinalização para S25`. Esse fluxo deve estar publicado, revisado e sem TODOs.
- **KR‑1.3 – Sem contestação “off‑book”:** qualquer contestação/revisão feita por humanos em cenários da sprint deve, obrigatoriamente, gerar uma `DebunkIssue` e uma `DebunkDecision` persistidas, com evidências anexas. Nenhum cenário oficial de demo pode depender de anotações “paralelas” (planilhas, docs soltos).

---

## O2 — Entregar o Debunker v0 funcional e operável por humanos

**Descrição:** o Debunker v0 precisa existir como **módulo real** (serviços, UI mínima e APIs) que analistas humanos consigam usar sem ajuda do time de desenvolvimento.

**Resultados‑chave:**
- **KR‑2.1 – Mínimo produto completo (MVP coerente):** existir um conjunto fechado de **user stories** para analistas (ex.: “receber fila de claims problemáticos”, “ver evidências”, “registrar decisão”) implementadas e rastreáveis contra cenários de teste/documentação. Cada user story deve ter pelo menos um cenário automatizado (ou semi‑automatizado) em `out/evidence/S24_G*_debunker_e2e/`.
- **KR‑2.2 – UX mínima, mas utilizável:** a **UI do Debunker v0** não precisa ser perfeita, mas deve permitir: visualizar fila, abrir um caso, ler contexto/timeline, ver evidências relevantes (links, anexos, metadados) e registrar decisões estruturadas. Pelo menos **3 analistas fictícios** (personas definidas no Capítulo 1.1) devem conseguir completar o fluxo em testes moderados, sem intervenção do time.
- **KR‑2.3 – Operabilidade & fallback:** a operação diária do Debunker v0 (rodar serviços, consumir fila, registrar decisões) deve estar documentada em um runbook conciso (`docs/sprint_24_cap_4_1_execucao_runbook.md`), com procedimentos de fallback claros caso algum componente falhe (ex.: modo degrado sem ranking automático, mas com criação manual de issues).

---

## O3 — Criar um pipeline robusto de seleção de casos para contestação

**Descrição:** a S24 não pode contestar “tudo”. Precisamos de um **pipeline explícito de priorização** de casos sensíveis: conflitos entre agentes, incerteza alta, temas de alto impacto, sinais de anomalia.

**Resultados‑chave:**
- **KR‑3.1 – Critérios formais de seleção:** existir um conjunto de **regras formais de priorização** que usem sinais vindos de S23 (ex.: divergência entre comitês, score de incerteza, flags de sensibilidade temática) para alimentar a `DebunkQueue`. Essas regras precisam estar descritas de forma declarativa (YAML / config) e versionadas.
- **KR‑3.2 – Métricas de qualidade da fila:** para os cenários da sprint, pelo menos **80% dos casos que chegam à fila de DebunkIssue** devem ser considerados “válidos e relevantes” pelo squad (ou seja, não são ruídos óbvios ou repetições triviais). Isso deve ser medido e registrado em scorecards de S24 (ex.: `precision_debunk_queue >= 0.8` para o corpus da sprint).
- **KR‑3.3 – Volume controlado:** o pipeline não pode inundar analistas. Para o conjunto de cenários da sprint, a relação **casos por analista por dia** deve ser mantida em um intervalo alvo (ex.: 5–20 casos/dia/persona). Qualquer violação desse intervalo deve ser registrada como risco/ajuste de política, não como “detalhe futuro”.

---

## O4 — Estruturar o humano‑no‑loop como parte do protocolo de verdade

**Descrição:** o humano‑no‑loop aqui não é um remendo; é **parte do protocolo de verdade**. Cada decisão humana precisa ser legível, audível e reaproveitável pela S25.

**Resultados‑chave:**
- **KR‑4.1 – Modelo claro de DebunkDecision:** toda `DebunkDecision` deve registrar, no mínimo: claim(s) afetado(s), tipo de decisão (ex.: CONFIRMED, REJECTED, NEEDS_MORE_EVIDENCE, PARTIALLY_TRUE), rationale textual curto, vínculo a evidências consultadas, identidade do analista (ou persona) e timestamp. O modelo deve estar documentado e refletido na base de dados.
- **KR‑4.2 – Traço auditável ponta‑a‑ponta:** para cada cenário da sprint, deve ser possível reconstruir, apenas com dados do sistema, o caminho: `claim → por que entrou na fila → quem analisou → qual decisão tomou → em qual contexto/evidências se baseou`. Esse reconstruído deve ser demonstrado com pelo menos **3 casos‑exemplo** em `out/evidence/S24_G*_audit_trail/`.
- **KR‑4.3 – Reutilização pela S25:** o formato de `DebunkDecision` e de `DebunkIssue` deve ser declarado **compatível com os requisitos de S25**, com uma nota explícita de alinhamento entre squads (S24 e S25). Nenhum campo essencial para a governança futura (ex.: sinal de confiança, relação com políticas de verdade, escopo temporal/origem) pode ficar “para decidir depois”.

---

## O5 — Blindar o Debunker v0 contra erro grosseiro e alucinação de modelos

**Descrição:** a S24 precisa nascer com **redundâncias mínimas** para evitar que um único erro de modelo ou de humano provoque decisões absurdas ou inconsistentes com o restante do sistema.

**Resultados‑chave:**
- **KR‑5.1 – Triple redundancy conceitual aplicada:** o design do Debunker v0 deve demonstrar, de forma concreta, o uso de **pelo menos três camadas de defesa** contra erros graves: (1) filtro automático baseado em sinais de S23 e regras rígidas; (2) revisão humana obrigatória com checklist mínimo; (3) alertas de inconsistência entre decisões, evidências e estados de claims. Essas camadas devem estar descritas e validadas em cenários de teste.
- **KR‑5.2 – Scorecards de qualidade por decisão:** existir scorecards que avaliem a qualidade de decisões do Debunker em termos de: consistência com evidências, alinhamento com políticas, ausência de viés óbvio e reversões indevidas. Para a amostra da sprint, uma taxa mínima de **95% de decisões sem “erro grosseiro” identificado pela própria equipe** deve ser atingida.
- **KR‑5.3 – Testes de estresse com casos adversariais:** a sprint deve incluir um conjunto de **casos adversariais curados** (ex.: notícias malformadas, cliquesbait, desinformação óbvia, dados contraditórios). O Debunker v0 precisa: (a) evitar confirmar como verdade algo claramente falso em pelo menos 98% desses casos; (b) encaminhar para `NEEDS_MORE_EVIDENCE` ou similar quando a evidência for insuficiente.

---

## O6 — Integrar S24 com o restante do pipeline Inspectah sem gambiarras

**Descrição:** o Debunker v0 precisa se encaixar no pipeline S21–S23/S25 de forma limpa: sem endpoints “secretos”, sem tabelas paralelas, sem fluxos que não possam ser reproduzidos em ambiente de teste.

**Resultados‑chave:**
- **KR‑6.1 – Integração contratual com S23:** as interfaces entre S23 (interpretation/classification) e S24 (debunker) devem estar especificadas em contratos claros: esquemas de payload, eventos ou tabelas intermediárias. Esses contratos devem ser usados tanto pelos serviços quanto pelos testes de integração.
- **KR‑6.2 – Hooks para S25 já previstos:** mesmo que S25 ainda não esteja implementada, devem existir pontos claros de integração (ex.: eventos de `DebunkDecision` prontos para alimentar o motor de governança, views/materializações no Truth‑DB). Esses pontos devem ser documentados em Capítulo 3 (Arquitetura & Filemap) e validados em pelo menos um cenário “de ponta a ponta parcial”.
- **KR‑6.3 – Reprodutibilidade em ambiente limpo:** deve ser possível subir um ambiente mínimo (backend + Debunker v0 + banco) e rodar os cenários da sprint com um único comando/documento de orquestração (ex.: `bin/s24_all_gates.sh` ou equivalente), gerando sempre a mesma sequência de evidências para os casos exemplares. Qualquer dependência extra‑oficial (scripts soltos, ajustes manuais de banco) é considerada falha de objetivo.

---

## O7 — Produzir documentação e evidências em nível de “manual de referência”

**Descrição:** a S24 precisa sair da sprint com documentação que permita a outro time entender, operar e evoluir o Debunker v0 sem depender da memória oral do squad.

**Resultados‑chave:**
- **KR‑7.1 – Documentação de produto e fluxo:** existir um documento de visão de produto específico da S24 (ou seção dedicada em docs macro) que explique, em linguagem acessível, o papel do Debunker v0, quando ele entra em ação, como os analistas trabalham e como isso conversa com a promoção de verdade na S25.
- **KR‑7.2 – Documentação técnica alinhada ao código:** Capítulos 3.x (Arquitetura & Filemap) e 4.x (Execução & Evidências) da S24 precisam estar **sem divergências materiais** em relação ao código, scripts e esquemas do repositório. Divergências encontradas durante a sprint devem gerar issues explícitos e correções antes do GO.
- **KR‑7.3 – Pacote de evidências completo:** ao final da sprint, deve existir um pacote de evidências (zip ou equivalente) contendo: scorecards, logs de execução dos gates, exemplos de DebunkIssue/DebunkDecision reais, trilhas de auditoria reconstruídas e um conjunto mínimo de casos adversariais. Esse pacote deve ser suficiente para um revisor externo (ex.: Conselho) avaliar a solidez da S24.

---

## Encerramento deste sub‑capítulo

Os objetivos desta S24 foram definidos para **forçar rigor máximo** em três frentes: modelagem de verdade contestada, operação humana e integração com o pipeline maior do Inspectah. Eles serão refinados e amarrados em detalhes no **Capítulo 2 (Gates & Métricas)** e no **Capítulo 3 (Arquitetura & Filemap)**, que devem referenciá‑los diretamente (via O/KR) para garantir rastreabilidade.

Nenhuma decisão relevante da S24 — de modelos de dados a atalhos operacionais — deve ser tomada fora do contexto desses objetivos. Se algum trade‑off for necessário (ex.: reduzir escopo de UI para manter robustez de trilha de auditoria), ele precisa ser explicitado como tal e amarrado a um KR afetado, não como dívida oculta.

