# Sprint 29 — Capítulo 2
## Bloco 1 — Papel dos gates na S29 e visão geral da malha de validação

O Capítulo 1 da Sprint 29 explicou **o que** queremos conquistar: transformar o fluxo de agentes por domínio em um ativo configurável, visível, validado e integrado ao runtime. O Capítulo 2 responde **como vamos provar que isso realmente aconteceu**.

Este Bloco 1 estabelece a lógica da malha de validação da S29 e apresenta, em visão geral, os gates que estruturam a sprint.

---

### 1. Por que gates importam tanto na S29

A Sprint 29 mexe no “cérebro operacional” do Inspectah: a coreografia de papéis de agentes que transforma dados em decisões. Isso é sensível o bastante para merecer uma malha de proteção específica. Os gates aqui não são burocracia; são o mecanismo que impede:

- que a configuração de fluxo vire apenas mais uma tela bonitinha sem impacto real;
- que modelos frágeis escapem para a base de código principal;
- que o runtime passe a depender de um sistema de fluxo imaturo;
- que o conselho seja forçado a decidir GO/NO-GO com base em percepções vagas.

Na S29, os gates assumem três funções centrais:

1. **Provar existência** — “As coisas que dizemos que existem de fato existem?” (modelo, API, UI, adapter, bundle, ORR).
2. **Provar correção básica** — “O que existe faz o mínimo que precisa fazer sem quebrar?” (migrations rodando, invariantes aplicadas, tests verdes).
3. **Prover trilha de evidência** — “Conseguimos auditar depois o que foi feito?” (scorecards JSON, logs, bundles, ORR).

Sem isso, qualquer conversa sobre “E28 v1” ficaria no nível de marketing técnico.

---

### 2. O desenho da malha de gates da S29

A Sprint 29 se ancora em uma malha de cinco gates técnicos + um gate de consolidação/ORR. Cada gate ataca um pedaço específico da promessa da sprint:

- **S29_G0 — Scope & Baseline**  
  Garante que a sprint não está sendo tocada “na base do improviso”. Verifica se:
  - os documentos centrais (macro, capítulos da sprint) existem;
  - o filemap mínimo de código para fluxos de agentes está criado;
  - os diretórios de evidência e scorecards estão disponíveis.

- **S29_G1 — Modelos, Schemas e Migrations (AgentFlowConfig)**  
  Amarra a parte mais estrutural:
  - modelos de domínio (`AgentFlowConfig`, `AgentFlowStep`) definidos e consistentes;
  - migrations criadas e aplicáveis em bancos novos e já migrados;
  - testes mínimos garantindo que a modelagem não é apenas teórica.

- **S29_G2 — API de Admin & Validador de Fluxo**  
  É o gate onde a teoria encontra a superfície de operação:
  - rotas de admin para ler/criar/atualizar fluxos existem e funcionam;
  - invariantes de fluxo são implementadas em código, não só em texto;
  - testes de API e de validação mostram que fluxos válidos passam e fluxos inválidos são bloqueados com mensagens claras.

- **S29_G3 — UI & Frontend Quality (Agent Flows UI)**  
  Garante que o operador humano ganhou de fato uma alavanca:
  - a UI de configuração de fluxo existe, renderiza, conversa com a API;
  - lint, testes e build do frontend passam;
  - há evidência concreta de um domínio piloto sendo configurado via interface.

- **S29_G4 — Runtime & Observabilidade de Fluxos**  
  É o gate que separa “feature de catálogo” de “capacidade real de produto”:
  - o runtime chama `get_agent_flow_for_domain(domain_key)`;
  - pelo menos um pipeline real usa o fluxo configurado para guiar a ordem dos agentes;
  - logs e métricas mínimas permitem ver o fluxo em ação e detectar uso de fallback.

- **S29_G5 — ORR & Bundle de Evidências da S29**  
  Gate final de consolidação:
  - reúne evidências de todos os gates em um bundle único (`inspectah_s29_evidence_bundle.zip`);
  - valida a existência de scorecards para todos os gates G0–G4;
  - garante que existe um documento ORR S29 onde o conselho pode basear a decisão GO/NO-GO.

Cada gate é implementado por um script `bin/s29_gX_*.sh`, gera evidências em `out/evidence/S29_GX_*` e um scorecard JSON em `out/scorecards/S29_GX_*.json`. A sprint só é considerada **GO** se **todos os gates obrigatórios** passarem.

---

### 3. Conexão entre gates e objetivos de produto

Os gates da S29 não são caixas pretas isoladas; cada um mapeia diretamente para objetivos de produto do Capítulo 1:

- O desejo de ter **fluxo configurável por domínio** se traduz em G1 (modelo), G2 (API) e G3 (UI).
- A necessidade de **evitar fluxos perigosos** se traduz em G2 (validador) e G4 (runtime observável com fallback controlado).
- A exigência de **governança e auditabilidade mínima** aparece em G1 (auditoria básica em modelo), G2 (erros explicativos) e G5 (scorecards + ORR + bundle).

A malha de gates funciona, portanto, como um "contrato técnico" que garante que, se tudo estiver verde, o que foi prometido como E28 v1 não será apenas uma ideia bonita em documento, mas uma capacidade concreta do Inspectah.

Nos blocos seguintes deste capítulo, cada gate será detalhado:

- quais checks específicos executa;
- quais métricas e arquivos produz;
- como o scorecard registra o resultado;
- qual é o critério objetivo para marcar `PASS` ou `FAIL`.

Este Bloco 1 existe para alinhar a cabeça da equipe: a partir daqui, ninguém deveria olhar para um `bin/s29_gX_*.sh` como um shell script qualquer, mas como um **pedaço codificado do contrato de verdade da Sprint 29**.

