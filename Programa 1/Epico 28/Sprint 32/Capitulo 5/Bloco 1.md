# Inspectah — Sprint 32
## Capítulo 5 — Bloco 1
### Objetivo do ORR da Sprint 32 & Papel Operacional do Truth-DB v1

> Este bloco define, com precisão cirúrgica, **o que o ORR da Sprint 32 precisa decidir** e **por que essa sprint é diferente das demais**. É o enquadramento macro do Capítulo 5: qual é o alvo, o que está em jogo e qual o resultado esperado da revisão.

---

#### 5.1.1 Por que a Sprint 32 merece um ORR especial

A S32 não entrega apenas mais um serviço: ela coloca em operação o **núcleo de verdade do Inspectah**:

- o **Truth-DB** (modelo de dados, blocos, estados);  
- o **Sistema de Blocos v1 operacional** (FactBlock, EvidenceBlock, DecisionBlock, ContestRecord);  
- a **Contestação v1** (capacidade de desafiar e revisar estados de verdade).

Isso significa que, a partir da S32, o Inspectah passa a ter um lugar oficial onde responde, na prática:

> "O que o sistema considera verdadeiro agora? Em que condições isso pode ser contestado? E como reconstituímos essa decisão depois?"

Por esse motivo, o ORR da S32 precisa funcionar como uma **auditoria inaugural do núcleo de verdade** — não apenas como checklist de feature.

---

#### 5.1.2 Objetivo central do ORR da Sprint 32

O objetivo do ORR da S32 pode ser resumido em uma pergunta única:

> "Podemos colocar o Truth-DB + Contestação v1 para rodar em ambiente compartilhado com ingestão/claims **sem comprometer integridade, auditabilidade e operação do sistema**?"

Para responder a essa pergunta, o ORR precisa verificar, com base em artefatos concretos (scorecards, logs, bundle, testes), se:

1. O núcleo de verdade está **correto**  
   - Modelos e migrações representam fielmente o design aprovado (Capítulo 3).  
   - Invariantes críticas (sem blocos órfãos, estados finais com DecisionBlock, histórico monotônico) estão implementadas e testadas.

2. O núcleo de verdade está **integro**  
   - Não há evidência de corrupção de dados ou perda silenciosa de histórico.  
   - Fluxos de promoção e contestação preservam rastros completos (blocos + estados + contestações).

3. O núcleo de verdade está **observável**  
   - Métricas mínimas existem e dizem algo útil sobre saúde do Truth-DB.  
   - Erros são detectáveis e não se escondem atrás de logs genéricos.

4. O núcleo de verdade está **reexecutável e auditável**  
   - O bundle da S32 permite reexecutar gates principais (G1–G3) em outro ambiente.  
   - É possível reconstruir a trajetória de pelo menos um caso real de promoção + contestação usando apenas os artefatos da sprint.

A saída formal do ORR será uma decisão explícita **GO / GO COM RESTRIÇÕES / NO-GO** para o ambiente-alvo definido (staging, pre-prod, etc.).

---

#### 5.1.3 O que o ORR da S32 NÃO é

Para manter o foco, este ORR **não** tem a função de:

- avaliar toda a visão de produto do Inspectah;  
- discutir roadmap de features de UI, monetização ou expansão de fontes;  
- redesenhar o modelo conceitual do Sistema de Blocos ou políticas de verdade de longo prazo.

Ele é, deliberadamente, mais estreito:

- julga **se a implementação atual do Truth-DB + Contestação v1** é segura para entrar em operação no escopo definido;  
- julga **se a sprint cumpriu o contrato** especificado nos Capítulos 1–4 (estados-alvo, gates, bundle);  
- registra **restrições, riscos residuais e dívidas operacionais** que precisam ser carregadas com consciência para as próximas sprints.

Qualquer discussão estratégica mais ampla (ex.: evolução do sistema de comitês, políticas de promoção, integração com blockchain, etc.) deve ser registrada como **insumo para Programas/Sprints futuros**, não como bloqueio imediato da S32, a menos que revele um risco estrutural.

---

#### 5.1.4 Como este Bloco 1 orienta o resto do Capítulo 5

Nos blocos seguintes do Capítulo 5, o conteúdo deste Bloco 1 é desdobrado em:

- **pré-requisitos concretos de ORR** (scorecards, bundle, sanidade cruzada);  
- **painel de perguntas** que o conselho precisa conseguir responder usando os artefatos da S32;  
- **critérios formais de GO / GO COM RESTRIÇÕES / NO-GO**;  
- **runbook de operação pós-sprint** para o Truth-DB + Contestação v1;  
- **classificação de regressões** e como elas influenciam a decisão.

Este Bloco 1 é, portanto, o "mandato" do ORR da Sprint 32: define por que estamos aqui, qual é a pergunta central e qual é o padrão mínimo de seriedade que o núcleo de verdade do Inspectah exige daqui para frente.