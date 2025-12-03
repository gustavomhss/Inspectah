# Inspectah — Sprint 31 (E28-S3)
## Capítulo 6 — Bloco 4: Síntese, Checklists & Próximos Passos

### 6.19 Papel deste bloco

Os Blocos 1–3 do Capítulo 6 fizeram o trabalho denso:

- capturaram **lessons learned** técnicas, processuais e de produto (Bloco 1);
- deram nome às **dívidas técnicas S31-DT-*** (Bloco 2);
- redesenharam o **impacto no roadmap** e listaram os **Anti-gaps** (Bloco 3).

Este Bloco 4 tem um objetivo diferente:

> Transformar tudo isso em **checklists operacionais e próximos passos concretos**, para que a Sprint 31 siga viva nas próximas decisões de arquitetura, produto e governança.

Aqui, a S31 vira um pequeno “protocolo de consulta”:

- o que precisa ser checado antes de abrir um novo domínio com provider-first;
- o que precisa ser considerado ao planejar sprints futuras de E28 e de governança de verdade;
- quais decisões **não podem** ser tomadas sem olhar de novo para este capítulo.

---

### 6.20 Checklist A — Abrir um novo domínio com provider-first

Sempre que alguém quiser “ligar provider-first” em um novo domínio (ex.: outro país, outro tema), é obrigatório passar por esta lista.

**A1 — Manifesto de Providers existe?**

- [ ] Existe um **Manifesto de Providers** para o domínio, descrevendo:  
  - providers propostos;  
  - cobertura de cada um;  
  - limites contratuais e TOS;  
  - viéses conhecidos.
- [ ] O Manifesto está linkado aos Programas 1–3.

**A2 — Plano de Ingestão por Domínio (PID) está completo?**

- [ ] O domínio tem um **PID** formal, contendo:  
  - lista de fontes (providers + legados);  
  - escopo do que será ingerido;  
  - custos estimados em diferentes cenários;  
  - métricas de sucesso desejadas;  
  - riscos específicos e mitigação inicial.

**A3 — `IngestionProfiles` bem definidos e limitados**

- [ ] Os perfis iniciais são poucos e fortemente opinados (pilotos), não “tudo de uma vez”.  
- [ ] Cada `IngestionProfile` tem:  
  - filtros claros (idioma, país, tema);  
  - parâmetros de janela;  
  - limites de budget (calls, volume) definidos.

**A4 — Dedupe & normalização compatíveis com o domínio**

- [ ] Existe uma política de dedupe específica para o domínio, documentada com base em S31-DT-003.  
- [ ] Há testes (mesmo que simples) mostrando que a política não colapsa itens distintos nem gera duplicatas insanas.

**A5 — Métricas e observabilidade mínimas configuradas**

- [ ] Perfis estão expondo métricas mínimas: calls, itens brutos, ContentItems, erros, budget_usage.  
- [ ] Há pelo menos um painel básico de ingestão para o domínio;  
- [ ] Alertas mínimos de erro/custo/silêncio estão planejados (mesmo que a implementação completa fique em sprint posterior).

**A6 — Flags e plano de rollout definidos**

- [ ] As flags equivalentes a F1–F4 da S31 estão definidas para o novo domínio (ligar/desligar ingestão, limitar a pilotos, controlar P2–P3).  
- [ ] Existe um plano de rollout por ambiente (dev → staging → prod limitada).

Se qualquer item A1–A6 estiver **claramente não atendido**, o domínio não deveria ser ligado com provider-first em produção. O default é adiar, não improvisar.

---

### 6.21 Checklist B — Planejar sprints futuras do Épico E28

Quando o time for montar novas sprints dentro do Épico E28, este checklist B ajuda a não perder o fio da S31.

**B1 — Em qual cluster a sprint se encaixa?**

- [ ] Cluster A — Expansão de domínios/perfis  
- [ ] Cluster B — Observabilidade, custo e incidentes  
- [ ] Cluster C — Fairness, cobertura e governança de fontes

Se a sprint não se encaixa em nenhum cluster, há chance de estar indefinida demais.

**B2 — Quais dívidas S31-DT-* a sprint pretende atacar?**

- [ ] A sprint referencia explicitamente 1–3 dívidas técnicas S31-DT-* relevantes.  
- [ ] O DoD inclui “S31-DT-00X mitigada/fechada” para pelo menos uma delas.

**B3 — O escopo conversa com Programas 1–3?**

- [ ] Existem pontos de contato claros com Programas 1–3 (não só com ingestão).  
- [ ] Pelo menos um caso de uso/caso piloto real é citado para validar a sprint.

**B4 — Há previsão de impacto em custo e cobertura?**

- [ ] A sprint reconhece, no mínimo qualitativamente, como afeta custo e cobertura.  
- [ ] Se mexe em muitos perfis ou novo domínio, há previsão de utilizar o modo de simulação de custo (quando existir).

**B5 — Existe plano para teste E2E ou caso piloto?**

- [ ] A sprint prevê ao menos um cenário E2E (próprio) ou extensão dos cenários da S31.  
- [ ] Há clareza sobre quais evidências serão produzidas (logs, traces, casos piloto).

---

### 6.22 Checklist C — Conectar provider-first com governança de verdade

À medida que providers ganham peso, é obrigatório conectar ingestão com política de verdade. Este checklist deve ser usado pelos squads de Verdade & Interpretação ao desenhar políticas ou painéis.

**C1 — Mix de fontes é explicitado no nível de caso/fato?**

- [ ] Para casos relevantes, é possível ver quais providers/fontes alimentaram as Claims/FactBlocks.  
- [ ] O sistema consegue distinguir “caso sustentado só por news” vs “news + dados oficiais + social”.

**C2 — Peso relativo de providers é discutido, não assumido**

- [ ] Há discussão explícita (mesmo que interna) sobre quanto confiar em cada provider, por domínio.  
- [ ] Existe espaço para, no futuro, atribuir pesos a providers na hora de decidir promoção a verdade.

**C3 — Transparência para usuário final está no radar**

- [ ] Já existe ao menos uma ideia embrionária de como mostrar “mix de fontes” para o usuário (Fact Cards, timeline, painéis).  
- [ ] Sprints de governança já consideram provider-first como insumo de primeira classe, não só “mais um detalhe técnico”.

---

### 6.23 Decisões que devem sempre consultar este capítulo

Algumas decisões são grandes demais para serem tomadas “de cabeça”. Sempre que uma delas aparecer, o time deve abrir o Capítulo 6 da S31 antes de seguir:

1. **Decisão de ligar provider-first em qualquer novo país/região**
   - Checar Checklists A e B;  
   - Garantir que Manifesto de Providers + PID existem.

2. **Decisão de expandir agressivamente número de perfis dentro de um domínio**
   - Revisit ar lições de custo e métricas (Seções 6.1 e 6.2);  
   - Verificar se as dívidas S31-DT-001/002/005 estão, no mínimo, parcialmente atacadas.

3. **Decisão de usar conteúdo provider-first como base principal de promoção a verdade em um tema sensível**
   - Consultar Anti-gaps 3 e 7 (fairness, políticas de verdade);  
   - Garantir que haja visão clara de mix de fontes.

4. **Decisão de “desligar scrapers legados” em massa**
   - Revisar impacto em fallback e redundância;  
   - Verificar se os comparativos legado vs provider (Cenário E2E 4 e sucessores) estão robustos o bastante.

---

### 6.24 Próximos passos recomendados pós-S31

Com a Sprint 31 concluída, a recomendação da equipe (E28 + Verdade & Interpretação + Console) é:

1. **Fechar rapidamente 1–2 dívidas técnicas mais críticas**  
   Prioridade alta para:  
   - S31-DT-001 (observabilidade do scheduler);  
   - S31-DT-005 (alertas de custo/erro).  
   Isso reduz risco operacional enquanto novos domínios começam a ser estudados.

2. **Formalizar o primeiro conjunto completo de artefatos BR**  
   - Manifesto de Providers BR;  
   - PID BR (plano de ingestão por domínio);  
   - registro consolidado do piloto (casos, métricas, incidentes).  
   Esse pacote vira “modelo de ouro” para outros domínios.

3. **Planejar a próxima sprint de E28 com foco temático claro**  
   Por exemplo:  
   - E28-S4 focada em Observabilidade & Alertas; ou  
   - E28-S4 focada em Expansão Moderada de Perfis BR, usando o modelo de S31.

4. **Abrir o diálogo com squads de governança de verdade usando dados da S31**  
   - Levar casos piloto, exemplos de mix de fontes e sinais de viés para o time de governança;  
   - alinhar expectativas sobre como providers serão tratados nas políticas de verdade.

5. **Revisitar este Capítulo 6 após 1–2 sprints adicionais**  
   - Atualizar lessons learned com base em incidentes e expansões reais;  
   - marcar S31-DT-* resolvidas ou migradas para novas dívidas mais refinadas.

---

### 6.25 Fechamento do Capítulo 6 e da S31

O Capítulo 6 encerra a Sprint 31 com uma mensagem simples:

> Provider-first + Console v2 deixaram de ser ideia e viraram infraestrutura real — mas só valem a pena se forem tratados como parte do cérebro de ingestão e de verdade do Inspectah, não como um atalho temporário.

Com os quatro blocos deste capítulo:

- sabemos **o que aprendemos** (Bloco 1);
- sabemos **onde estamos devendo** (Bloco 2);
- sabemos **como isso mexe no roadmap e nos pontos cegos** (Bloco 3);
- e temos **checklists e próximos passos concretos** para não desperdiçar esse aprendizado (Bloco 4).

A S31, assim, entra oficialmente na história do Épico E28 como a sprint que colocou provider-first no mapa de forma séria, auditável e expansível. O próximo passo é honrar isso nas sprints seguintes, usando este capítulo como referência obrigatória sempre que alguém sugerir “vamos só ligar mais um provider aqui rapidinho…”.