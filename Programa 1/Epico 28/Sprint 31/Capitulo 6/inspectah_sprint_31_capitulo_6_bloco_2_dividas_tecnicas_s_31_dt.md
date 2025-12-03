# Inspectah — Sprint 31 (E28-S3)
## Capítulo 6 — Bloco 2: Dívidas Técnicas (S31-DT-*)

### 6.5 Papel deste bloco

Este bloco pega tudo que ficou “quase lá” na Sprint 31 e dá nome, código e direção. A ideia é simples:

> Nenhuma gambiarra honesta deve ficar anônima.

Cada dívida técnica aqui recebe:

- um **ID estável** (`S31-DT-00X`),
- uma **descrição clara**,
- o **risco** de deixar como está,
- e uma **proposta de onde/como atacar** em sprints futuras (de preferência dentro do próprio Épico E28).

Essas dívidas não anulam a S31; elas são o mapa do que precisa ser refinado antes de escalar provider-first para além do domínio piloto.

---

### 6.6 S31-DT-001 — Observabilidade do scheduler de perfis

**Descrição**  
O scheduler que dispara ingestões de `IngestionProfile` ainda não tem:
- painel dedicado por perfil;  
- visão consolidada de runs (sucesso/falha) ao longo do tempo;  
- logs estruturados que facilitem responder “o que este perfil rodou na última semana?”.

Hoje é possível responder essas perguntas olhando logs brutos + métricas gerais, mas não de forma fluida.

**Risco**  
- Fica difícil diagnosticar por que determinados perfis estão com menos (ou mais) runs do que deveriam.  
- Possíveis problemas de agendamento (jobs não disparando ou disparando demais) podem passar despercebidos.  
- Investigações de custo e cobertura por perfil ficam mais lentas e sujeitas a erro humano.

**Sugestão de tratamento**  
- Criar painel específico de scheduler em sprint futura de observabilidade do Épico E28 (por exemplo, S32 ou S33).  
- Estruturar logs de scheduler com campos obrigatórios: `profile_id`, `scheduled_at`, `started_at`, `ended_at`, `status`, `error_code`, `calls`, `items`.  
- Alimentar uma visão de “histórico de runs por perfil” que o Console de Fontes possa consumir (ou ao menos uma API para isso).

---

### 6.7 S31-DT-002 — Testes de carga e stress específicos de provider-first

**Descrição**  
A S31 validou ingestão provider-first em cargas moderadas e em janelas controladas, mas ainda não há uma suíte sistemática de:
- testes de carga (throughput sustentado por perfil/provider);  
- testes de burst (picos curtos de volume ou de calls);  
- testes de limite (n perfis simultâneos).

**Risco**  
- Com expansão de domínios ou inclusão de novos providers, o sistema pode se comportar de forma imprevisível sob carga.  
- Latências podem aumentar em cascata (provider → normalizer → banco), afetando janelas de ingestão.  
- Custo pode explodir sob comportamentos não observados em ambiente real.

**Sugestão de tratamento**  
- Planejar uma sprint do Épico E28 focada em performance/escala de ingestão (ex.: “S3x — Provider Load & Scale”).  
- Criar cenários de load-test para perfis “heavy” (grande volume, janelas menores) usando ferramentas de carga apropriadas, com métricas associadas.  
- Definir SLOs mínimos de ingestão (ex.: X ContentItems/min sob condições Y) e validar.

---

### 6.8 S31-DT-003 — Políticas de dedupe por domínio

**Descrição**  
Hoje, as regras de dedupe e normalização estão afinadas para o domínio de notícias BR, com um conjunto de chaves (provider_id, external_id, título normalizado, URL, etc.). Ainda não existe:
- um mecanismo declarativo para definir políticas de dedupe por domínio/tema;  
- uma matriz de “políticas por domínio” documentada, com critérios e trade-offs.

**Risco**  
- Ao expandir para outros domínios (ex.: dados econômicos, social global, documentos oficiais), as heurísticas atuais podem gerar duplicatas em excesso ou colapsar itens distintos.  
- Fica mais difícil explicar por que certos conteúdos foram unidos ou mantidos separados.

**Sugestão de tratamento**  
- Evoluir o serviço de dedupe para aceitar políticas declarativas (ex.: YAML/JSON) que combinem chaves por domínio.  
- Criar um artefato “Tabela de Políticas de Dedupe por Domínio” em docs, ligado ao Cap.3.  
- Introduzir testes de dedupe orientados a domínio, com datasets sintéticos que exercitem casos-limite.

---

### 6.9 S31-DT-004 — Escalabilidade de UX do Console v2 para muitos providers/perfis

**Descrição**  
A UI do Console v2 foi desenhada e validada em cenário de:
- poucos providers (1–2);  
- número relativamente pequeno de perfis (dezenas, não centenas).

Ainda não está claro como a experiência se comporta com:
- múltiplos providers;  
- dezenas/centenas de perfis por domínio;  
- combinações de filtros mais complexos.

**Risco**  
- O Console pode se tornar difícil de navegar (listas longas, filtros pobres).  
- Operadores podem ter dificuldade em localizar perfis específicos ou ver rapidamente o estado de um subconjunto relevante.  
- Novos domínios podem exigir re-trabalho de UI se a escalabilidade não for tratada cedo.

**Sugestão de tratamento**  
- Reservar uma sprint de UX para “Console Scalability” dentro do Épico E28.  
- Introduzir filtros por domínio, tema, provider, status, tags.  
- Validar paginação, busca textual e agrupamentos (por domínio, por criticidade) com cenários simulando 100+ perfis.

---

### 6.10 S31-DT-005 — Automação de alertas de custo e erro

**Descrição**  
A S31 entregou métricas e runbooks, mas alertas automáticos ainda são:
- inexistentes ou rudimentares;  
- dependentes de alguém olhar manualmente gráficos e logs.

**Risco**  
- Incidentes de custo (calls em explosão, budget_usage anormal) podem ser percebidos tarde demais.  
- Problemas persistentes de erro (5xx, 4xx de provider, falhas de normalizer) podem se arrastar por horas sem disparar reação.

**Sugestão de tratamento**  
- Em sprint futura, integrar métricas de provider-first com o sistema de alertas padrão (ex.: thresholds de calls/dia por perfil, taxa de erro, ausência de dados).  
- Definir playbook de alertas mínimos:  
  - custo (budget_usage_ratio > X por N runs);  
  - erro (error_rate > Y% por janela T);  
  - silêncio (nenhum item ingerido para perfil crítico numa janela que deveria ter dados).  
- Vincular esses alertas aos runbooks já definidos (RB3 e RB4).

---

### 6.11 S31-DT-006 — Hardening da trilha Provider → P2–P3

**Descrição**  
A trilha Provider → Perfil → ContentItem → Claim → FactBlock foi validada com um caso piloto real, mas:
- ainda não existe uma suíte robusta de testes de integração que cubra a trilha completa;  
- casos de erro (dados incompletos, inconsistentes, múltiplas fontes divergentes) não foram plenamente exercitados.

**Risco**  
- Mudanças em modelos ou pipelines de P2–P3 podem quebrar a trilha sem que CI perceba imediatamente.  
- A camada de verdade pode receber conteúdo provider-first em estado degradado sem evidência clara.

**Sugestão de tratamento**  
- Criar testes de integração E2E que injetem ContentItems provider-first em P2–P3 e validem:  
  - criação correta de Claims;  
  - construção consistente de FactBlocks;  
  - manutenção de trilha de proveniência.  
- Simular cenários de conflito entre fontes (ex.: diferentes providers relatando números diferentes) e registrar como P2–P3 reage.

---

### 6.12 S31-DT-007 — Coverage & bias-check automatizado por provider

**Descrição**  
Na S31, a análise de cobertura e viés (por país, tema, linha editorial) foi majoritariamente manual e baseada em intuição + amostras. Não há hoje:
- jobs periódicos que quantifiquem cobertura por tema/região;  
- relatórios automáticos que ajudem a identificar viés de forma objetiva.

**Risco**  
- Dependência de percepção subjetiva sobre “se o provider é enviesado ou não”.  
- Risco de construir políticas de verdade sobre uma base de notícias desequilibrada sem perceber.

**Sugestão de tratamento**  
- Introduzir, em sprints posteriores do Épico E28, jobs que:  
  - agreguem estatísticas por tema, país, entidade, tom, etc.;  
  - gerem relatórios internos simples de cobertura/bias.  
- Usar esses relatórios como insumo para squads de Verdade & Governança na hora de definir peso de fontes.

---

### 6.13 S31-DT-008 — Estrutura formal de “Plano de Ingestão por Domínio”

**Descrição**  
A S31 tratou o plano de ingestão BR de forma relativamente explícita nos capítulos e programas, mas não existe ainda:
- um artefato único que, para cada domínio, descreva: fontes, providers, escopo, custo estimado, métricas-alvo, riscos e mix de fontes desejado.

**Risco**  
- Entrada de novos domínios de forma ad-hoc, sem critérios claros.  
- Dificuldade em comparar domínios entre si em termos de custo, cobertura e maturidade de ingestão.

**Sugestão de tratamento**  
- Definir um template formal de “Plano de Ingestão por Domínio” (PIDs) e tratá-lo como pré-requisito para ligar provider-first em qualquer novo domínio.  
- Conectar esse template aos Programas 1–3, para que decisões de ingestão sejam sempre discutidas junto com verdade, custo e produto.

---

### 6.14 Como estas dívidas devem ser usadas

Estas dívidas técnicas não são uma lista de lamentações; são uma **to-do list de luxo** para as próximas sprints do Épico E28:

- Ao planejar novas sprints, revisitar S31-DT-001..008 e puxar as que fizerem mais sentido para o foco daquela sprint (observabilidade, escala, fairness, etc.).
- Ao discutir escopo de novos domínios/providers, garantir que pelo menos S31-DT-003 (dedupe por domínio) e S31-DT-008 (plano de ingestão) estejam no radar.
- Ao revisar incidentes futuros, mapear quais deles poderiam ter sido mitigados se alguma dessas dívidas já estivesse paga.

O objetivo deste bloco é garantir que a S31 seja ponto de partida, não teto: os IDs S31-DT-* viram ganchos explícitos para as evoluções que transformam provider-first + Console v2 de piloto BR em espinha dorsal de ingestão do Inspectah.

