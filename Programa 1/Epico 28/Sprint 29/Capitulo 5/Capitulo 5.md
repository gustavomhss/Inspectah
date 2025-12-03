# Sprint 29 — Capítulo 5
# ORR, Estado do Produto e Integração com o Épico E28

## 1. Papel do Capítulo 5 na Sprint 29

Os capítulos anteriores levaram a Sprint 29 até o ponto em que:

- sabemos claramente **o que** queremos (Cap. 1);
- sabemos **como medir** se chegamos lá (Cap. 2 — gates e scorecards);
- sabemos **onde cada peça vive** na arquitetura e no filemap (Cap. 3);
- sabemos **como executar** a sprint em waves e gerar evidências (Cap. 4).

Falta fechar o arco com uma visão consolidada de:

- como a Sprint 29 será **avaliada** (ORR — Operational Readiness Review);
- qual é o **estado do produto** após a sprint, em linguagem de produto e não só de código;
- como isso se encaixa no **Épico E28** e no Programa 1 como um todo;
- quais são as **recomendações formais** para próximas sprints.

Este Capítulo 5 responde a isso. Ele define o formato do ORR de S29, o checklist de readiness, o mapa de impacto no produto e a amarração com E28.

---

## 2. Documento de ORR da Sprint 29

O ORR (Operational Readiness Review) da Sprint 29 é registrado no arquivo:

- `docs/sprint_29_orr_summary.md`

Este documento deve ser autoexplicativo, de forma que alguém que não acompanhou a sprint consiga entender:

- o que a S29 prometeu;  
- o que foi efetivamente entregue;  
- o estado dos gates e scorecards;  
- o impacto no produto e nos usuários;  
- os riscos remanescentes e recomendações.

### 2.1. Estrutura proposta para `sprint_29_orr_summary.md`

Seções sugeridas:

1. **Resumo executivo**  
   - 3–6 parágrafos curtos respondendo:  
     - "O que a S29 colocou em pé?"  
     - "Para quais domínios isso já é útil?"  
     - "Quais são os principais riscos e limitações?"  
   - Linguagem de produto, não de implementação.

2. **Escopo planejado vs escopo entregue**  
   - Tabela ou lista comparando itens do Capítulo 1 (escopo planejado) com o que foi entregue:  
     - `planejado`: "Fluxo de agentes configurável por domínio (v1)";  
     - `entregue`: detalhar o que está pronto, o que entrou parcial, o que ficou para próximas sprints.  
   - Marcar claramente qualquer corte de escopo.

3. **Estado dos gates S29_G0–S29_G5**  
   - Tabela com colunas: Gate, Descrição, Status, Scorecard, Observações.  
   - Exemplo de linhas:  
     - `S29_G0_scope_and_baseline` — `PASS` — link local do scorecard;  
     - `S29_G1_model_and_migrations` — `PASS`;  
     - ... até `S29_G5_orr_and_bundle`.  
   - Indicar explicitamente se houve alguma exceção consciente.

4. **Evidências principais e bundle**  
   - Referenciar:  
     - diretórios de evidência (`out/evidence/S29_*`);  
     - bundle consolidado `out/bundles/inspectah_s29_evidence_bundle.zip`;  
   - se houver hash do bundle, registrá‑lo;  
   - explicar brevemente o conteúdo do bundle (logs de testes, logs de gates, snapshots, etc.).

5. **Impacto no produto e no Programa 1**  
   - Explicar, em termos de produto:  
     - o que muda na vida do operador admin;  
     - quais domínios já podem usar a configuração de fluxo v1;  
     - como isso fortalece o pipeline de ingestão e truth pipeline do Inspectah;  
     - como isso se posiciona dentro do Programa 1 (ex.: "Eixo: Fluxos de Agentes & Interpretação").

6. **Riscos conhecidos e limitações**  
   - Lista clara de pontos ainda frágeis ou não tratados nesta sprint, por exemplo:  
     - ausência de versionamento formal de fluxos;  
     - falta de interface avançada para branching/condicionais;  
     - catálogo de papéis ainda simplificado;  
     - cobertura parcial de domínios (apenas domínio piloto).  
   - Cada risco deve ter severidade (baixa/média/alta) e recomendação.

7. **Recomendações para próximas sprints (E28.x)**  
   - Sugestões de trabalho para próximas iterações do Épico E28, por exemplo:  
     - E28.2 — Versionamento e histórico de fluxos + approvals;  
     - E28.3 — Fluxos condicionais/branching e métricas;  
     - E28.4 — UI avançada para múltiplos fluxos por domínio;  
     - integração mais forte com camada de verdade/debunker (S23–S25).  
   - Essas recomendações devem conversar com o roadmap macro do Programa 1.

---

## 3. Checklist de ORR da Sprint 29

Além do documento, o ORR de S29 é guiado por um checklist operacional. A ideia é que, antes do GO final da sprint, o time passe por estas perguntas com respostas objetivas.

### 3.1. Checklist de readiness técnica

1. **Modelos & Migrations**  
   - Todas as migrations de S29 foram aplicadas em ambiente de teste e, quando apropriado, em ambiente de staging?  
   - É possível abrir um banco limpo e migrar até o estado atual sem falhas?  
   - As tabelas de fluxo não quebram compatibilidade com dados existentes?

2. **Validador & Serviço**  
   - Todas as invariantes definidas em Cap. 1/2 estão implementadas no `validator.py`?  
   - `create_agent_flow` e `update_agent_flow` chamam o validador sempre, sem atalhos?  
   - Erros de validação produzem mensagens consistentes (`code`, `message`) nas respostas HTTP?

3. **API de admin**  
   - Todos os endpoints (`GET`, `POST`, `PUT`) de `/admin/agent-flows` estão acessíveis e autenticados?  
   - Erros de domínio (`FLOW_ALREADY_EXISTS`, `FLOW_NOT_FOUND`, etc.) aparecem corretamente?  
   - Logs mínimos da API estão sendo emitidos para criação/atualização de fluxos?

4. **UI de fluxo**  
   - A entrada "Fluxos de agentes" aparece no menu admin e leva à página correta?  
   - É possível editar o fluxo de um domínio piloto de ponta a ponta pela UI (carregar → alterar → justificar → salvar)?  
   - A UI se comporta de forma previsível em caso de erro de invariantes (mensagens explícitas, sem travar)?

5. **Runtime & Observabilidade**  
   - O pipeline de ingestão de pelo menos um domínio piloto está consumindo o fluxo configurado?  
   - Logs de runtime registram o `flow_id`, `domain_key` e sequência de papéis executados?  
   - Há visibilidade mínima para identificar quando está sendo usado fallback de fluxo?

### 3.2. Checklist de readiness de produto

1. **Domínio(s) piloto(s) definidos**  
   - Quais domínios são explicitamente considerados piloto para uso da configuração de fluxo v1?  
   - Essas escolhas estão alinhadas com a prioridade de negócio do Inspectah?

2. **Operadores admin preparados**  
   - Os usuários admin responsáveis sabem como usar a UI de fluxos?  
   - Existe uma curta documentação ou walkthrough para a nova feature?

3. **Riscos comunicados**  
   - Os riscos e limitações listados no ORR foram apresentados à equipe mais ampla?  
   - Decisões conscientemente aceitas (por ex., "nesta v1, ainda não haverá versões múltiplas de fluxo por domínio") estão registradas?

Se qualquer resposta crítica for "não", a recomendação padrão do ORR é ajustar antes de declarar GO formal.

---

## 4. Estado do produto após a Sprint 29

Após a Sprint 29, o Inspectah ganha, em termos de produto, um novo bloco de capacidades:

1. **Fluxo de agentes configurável por domínio (v1)**  
   - Para domínios selecionados (pilotos), é possível configurar a sequência de papéis que tratam a informação (INTERPRETER, CLASSIFIER, DEBUNKER, DECISION_MAKER, etc.).  
   - A configuração é persistida em Truth‑DB (nível de config) e exposta via API, não mais codificada em if/else espalhados pelo código.

2. **Camada de governança mínima para fluxos**  
   - Alterações de fluxo exigem justificativa (`change_reason`) e são associadas a quem fez a mudança (`updated_by`).  
   - Qualquer mudança passa pelo validador de invariantes, evitando configurações flagrantemente inconsistentes.

3. **Console de admin com visão de fluxos**  
   - O console admin passa a ter uma área dedicada para as configurações de fluxo de agentes.  
   - Operadores conseguem ver, de forma legível, os passos do fluxo por domínio.

4. **Integração inicial com runtime**  
   - O pipeline real do Inspectah, ao processar itens de um domínio piloto, consulta o fluxo configurado e orquestra agentes na ordem especificada.  
   - Logs de runtime começam a acumular evidência do comportamento real dos fluxos.

Em resumo: S29 não apenas cria um modelo de fluxo bonito; ela **coloca em produção o conceito de fluxo de agentes configurável**, ainda que em escopo piloto.

---

## 5. Integração com o Épico E28 e Programa 1

A Sprint 29 foi definida como a sprint que **abre o Épico E28** dentro do Programa 1.

### 5.1. Papel da S29 dentro de E28

O Épico E28 trata do tema macro:

- "Fluxos de Agentes & Orquestração de Interpretação/Clasificação/Debunking/Decisão" (nome ilustrativo, mas alinhado ao DNA do Inspectah).

Dentro dele, a S29 cumpre o papel de:

- introduzir o conceito de fluxo de agentes como entidade de domínio;  
- tornar esse fluxo configurável por domínio via UI e API;  
- encaixar essa configuração no pipeline de ingestão;  
- produzir a infraestrutura de validação e evidências que as próximas sprints vão reaproveitar.

Sem a S29, o Épico E28 ficaria apoiado em estruturas ad hoc. Com a S29, E28 ganha um "chão técnico" sólido.

### 5.2. Pontes explícitas para futuras sprints de E28

A partir do estado pós‑S29, algumas trilhas naturais de trabalho para o Épico E28 (e para o Programa 1) são:

1. **E28.2 — Versionamento de fluxos e approvals**  
   - Introduzir múltiplas versões de fluxo por domínio (draft, active, deprecated);  
   - criar um fluxo de aprovação (por ex., dois admins precisam aprovar alterações em domínios sensíveis);  
   - expor histórico de alterações na UI.

2. **E28.3 — Fluxos condicionais e branching**  
   - Permitir condições do tipo "se a notícia for sobre tema X, passar por DEBUNKER2";  
   - representar essas condições no domínio (não só em código) e oferecer UI adequada;  
   - ajustar runtime para avaliar condições sem explodir a complexidade.

3. **E28.4 — Métricas e tuning de fluxos**  
   - A partir de logs, calcular métricas: quantos itens passaram por qual sequência de agentes, tempos médios, taxas de erro, etc.;  
   - usar essas métricas para sugerir ajustes de fluxo (agentes desnecessários, gargalos, etc.).

4. **Integração profunda com camadas de verdade (S23–S25)**  
   - Amarrar papéis do fluxo aos agentes Debunker, Classifier, Committees e Truth‑DB;  
   - garantir que o fluxo configurado respeita a política de promoção de verdade/fato.

O Capítulo 5 não especifica essas sprints, mas deixa claro que o desenho de S29 foi feito para acomodá‑las.

---

## 6. Recomendações formais do ORR da Sprint 29

Ao final do ORR de S29, o time deve registrar uma recomendação explícita, em linguagem semelhante a:

1. **Recomendação de GO/NO-GO**  
   - `GO` para uso da configuração de fluxo v1 nos domínios piloto acordados, com monitoramento próximo;  
   - `NO-GO` para expandir a todos os domínios até que certas condições sejam atendidas (por ex., maturidade de métricas, UX de fluxos condicionais).

2. **Recomendação de escopo para E28.2**  
   - Dar prioridade a versionamento e approvals de fluxo (caso riscos de governança sejam maiores);  
   - ou priorizar fluxos condicionais (caso a necessidade de flexibilidade seja urgente).

3. **Recomendação de observabilidade mínima**  
   - Definir quais logs e métricas de fluxo são obrigatórios antes de aumentar a exposição da feature;  
   - considerar integrar essas métricas a painéis de operação do Inspectah.

Essas recomendações formam a "ponte" entre S29 e as próximas sprints do Programa 1, evitando que o conhecimento acumulado se perca.

---

## 7. Amarração final do Capítulo 5

O Capítulo 5 fecha a Sprint 29 em três eixos:

- **Eixo técnico** — consolida o ORR, o estado dos gates e o bundle de evidências, garantindo que a sprint não é apenas um conjunto de commits, mas um bloco auditável de trabalho.  
- **Eixo de produto** — traduz o que foi feito em termos de capacidade nova do Inspectah: fluxos de agentes configuráveis, UI de admin, integração com runtime.  
- **Eixo de programa/épico** — posiciona a S29 como a fundação do Épico E28 e prepara o terreno para sprints futuras.

Com o Capítulo 5 completo, a Sprint 29 está pronta para ser julgada, encaixada no roadmap maior e servir de base sólida para as próximas iterações. O Capítulo 6 pode, então, focar em consolidar riscos, débito técnico e planos de mitigação de longo prazo associados a essa nova camada de fluxos de agentes.

