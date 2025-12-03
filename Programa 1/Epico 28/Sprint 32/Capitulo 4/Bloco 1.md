# Inspectah — Sprint 32
## Capítulo 4 — Bloco 1
### Estratégia Geral de Execução da Sprint 32

> Este bloco responde à pergunta: **“como a Sprint 32 vai ser executada na prática, do zero até o bundle final?”**. Ele define a estratégia macro, os princípios de execução e a visão de fases que orientarão os blocos seguintes.

---

#### 4.1.1 Princípios-guia da execução da S32

A execução da Sprint 32 é guiada por três princípios simples e duros:

1. **Primeiro fundação, depois fluxo, depois contestação**  
   - Fundação = modelos, migrações e invariantes do Truth-DB (o chão não pode ceder).  
   - Fluxo = claim → blocos → estado de verdade funcionando para um tipo de claim prioritário.  
   - Contestação = capacidade real de contestar um estado, gerar novos blocos e atualizar o estado sem destruir histórico.

2. **Gates como trilhos, não burocracia**  
   - Cada etapa importante de execução aponta para um gate:  
     - G0 abre o jogo (estrutura/documentos/scripts prontos).  
     - G1 garante que o Truth-DB não é areia movediça.  
     - G2 prova que a promoção funciona.  
     - G3 prova que a contestação funciona.  
     - G4 confirma que tudo isso está empacotado, reexecutável e pronto para ORR.  
   - A ordem de trabalho nasce do que é necessário para deixar esses gates verdes, não o contrário.

3. **Evidência como entregável de primeira classe**  
   - O “produto” da S32 não é só o código do Truth-DB, mas:  
     - código + testes + scripts de gate + scorecards + bundle de evidências.  
   - Se algo não deixa rastro em `out/scorecards/`, `out/evidence/` ou no bundle, a sprint não sabe provar que fez o que prometeu.

---

#### 4.1.2 Fases macro da execução

A S32 é organizada em cinco fases lógicas, que podem ter alguma sobreposição, mas idealmente são tratadas como degraus:

1. **Fase 0 — Preparação & G0 (Scope & Baseline)**  
   - Colocar a casa em ordem: docs da sprint, scripts `bin/s32_g*.sh` esqueleto, diretórios de evidência e scorecards criados.  
   - Resultado: G0 verde e time alinhado sobre o plano.

2. **Fase 1 — Fundamentos do Truth-DB (Modelos, Migrações & Invariantes / G1)**  
   - Implementar/ajustar modelos e migrações conforme Capítulo 3.  
   - Codificar invariantes críticas em testes.  
   - Resultado: G1 verde, banco consistente e modelo de dados confiável.

3. **Fase 2 — Fluxo de Promoção (PromotionService & G2)**  
   - Implementar o fluxo claim → blocos → estado de verdade, com métricas e testes de integração.  
   - Resultado: G2 verde, um tipo de claim já “vira verdade” de ponta a ponta.

4. **Fase 3 — Fluxo de Contestação (ContestationService & G3)**  
   - Implementar registro e processamento de contestações, com atualização de estado e histórico monotônico.  
   - Resultado: G3 verde, contestação v1 funcionando com trilha auditável.

5. **Fase 4 — Sanidade cruzada, regressões & G4 (Bundle + ORR)**  
   - Garantir que ingestão/claims não foram quebrados.  
   - Montar o bundle de evidências da S32 e consolidar scorecards.  
   - Resultado: G4 verde, bundle pronto e sprint julgável em ORR.

Os blocos seguintes do Capítulo 4 vão detalhar **o que fazer em cada fase**, quais comandos rodar, quais evidências produzir e como amarrar tudo ao bundle final.

---

#### 4.1.3 Relação com Estados-alvo (SA32_x) e Capítulos anteriores

A estratégia de execução da S32 não nasce do nada — ela é a tradução operacional dos capítulos 1–3:

- **Capítulo 1** define o contexto e o “porquê” da sprint (Truth-DB vivo, contestação v1, bundle reexecutável).  
- **Capítulo 2** define **o que precisa ser verdadeiro no final** (SA32_1–SA32_6, gates, métricas, invariantes).  
- **Capítulo 3** define **onde o trabalho acontece no código** (arquitetura, serviços, filemap).  
- **Capítulo 4** — começando por este Bloco 1 — define **como andamos de A até B**:
  - que fases seguimos;  
  - que gates queremos deixar verdes em cada fase;  
  - que tipo de evidência precisa existir para provar que chegamos lá.

Este Bloco 1 funciona como mapa macro de execução. Nos próximos blocos do Capítulo 4, cada fase será decomposta em tarefas concretas, comandos, evidências esperadas e checkpoints de sanidade para garantir que a Sprint 32 não apenas “faz”, mas **consegue provar** o que fez.

