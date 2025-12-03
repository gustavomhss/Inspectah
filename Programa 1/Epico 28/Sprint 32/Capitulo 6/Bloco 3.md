# Inspectah — Sprint 32
## Capítulo 6 — Bloco 3
### Learnings de Processo, Governança & ORR (como operar um núcleo de verdade)

> Este bloco reúne os learnings **não técnicos** da Sprint 32 — tudo aquilo que aprendemos sobre como planejar, executar, revisar e governar um núcleo de verdade. Aqui a S32 vira manual de processo para qualquer sprint futura que queira mexer com o coração do Inspectah.

---

#### 6.3.1 Gates como trilhos de execução, não burocracia

A S32 deixou muito claro que, para um núcleo de verdade, **gates bem desenhados são parte da arquitetura**, não apenas do processo.

O que funcionou bem:

- Pensar G0–G4 já no início da sprint, no Capítulo 2, ajudou a:
  - ordenar a execução (modelo e invariantes antes de serviços; serviços antes de ORR e bundle);  
  - evitar que o time escrevesse código complexo em cima de um schema ainda instável;  
  - definir desde cedo quais evidências seriam exigidas no fim.

- Ter scorecards explícitos (S32_G0…S32_G4) criou um “painel objetivo” para o ORR:  
  - em vez de debates abstratos, o conselho olhou para PASS/WARN/FAIL em pontos bem definidos;  
  - qualquer divergência entre o estado real e o que o scorecard dizia foi tratada como bug de governança.

O que doeu quando ignorado/atalhado:

- Sempre que alguém tentou “pular direto” para um serviço sem antes consolidar G1 (modelos + invariantes), o resultado foi retrabalho:  
  - migrações reescritas;  
  - services que precisaram ser refatorados para respeitar invariantes que só ficaram claras depois;  
  - testes quebrando por detalhes de schema.

Learning de processo:

- Para núcleos críticos (Truth-DB, comitês, causalidade, etc.), **gates são primeira classe**.  
- A pergunta não é “como encaixar os gates no que fizemos?”, e sim “como desenhar o trabalho em função dos gates?”.

---

#### 6.3.2 Bundles como parte do produto, não como “zip de conveniência”

Na S32, o bundle `inspectah_s32_evidence_bundle.zip` se mostrou uma peça central da história, não um detalhe.

O que o bundle viabilizou:

- Um ORR ancorado em evidência:
  - o conselho pôde olhar diretamente para scorecards, logs e dumps incluídos no bundle;  
  - perguntas difíceis (“mostra o antes/depois desta contestação”) foram respondidas abrindo arquivos reais, não slides.

- Capacidade de replay e auditoria:
  - a equipe conseguiu reexecutar G1, G2, G3 em outro ambiente a partir do bundle;  
  - isso transformou discussões de “confio/não confio” em “roda o gate e vê”.

- Base para debug de regressões futuras:
  - o bundle se torna um snapshot da “saúde lógica” do Truth-DB na S32;  
  - se no futuro algo se desviar, é possível comparar contra o estado conhecido da S32.

O que quase virou armadilha:

- Tratar o bundle como formalidade (zipando qualquer coisa só para “marcar presença”) dilui completamente seu valor.  
- Sem padrão mínimo de conteúdo, o bundle vira um arquivo aleatório difícil de entender e quase impossível de reusar.

Learning de governança:

- Para sprints como a S32, o bundle precisa ser tratado como **artefato de produto interno**.  
- A pergunta passa a ser: “**que história operacional esse bundle conta?**” — não apenas “ele existe?”.

---

#### 6.3.3 ORR centrado em perguntas difíceis, não em apresentações

A forma como o ORR da S32 foi estruturado ensinou um padrão importante:

- ORR bom não é o que tem mais slides, é o que tem **perguntas difíceis + artefatos concretos**.

O que funcionou bem:

- Ter um painel de perguntas pré-definido (modelo, invariantes, promoção, contestação, observabilidade, sanidade cruzada) evitou que o ORR virasse um tour de status superficial.  
- Cada pergunta vinha acompanhada de “onde olhar”:  
  - tal teste;  
  - tal log;  
  - tal dump;  
  - tal métrica.

- O conselho foi incentivado a pedir demonstrações específicas:  
  - “me mostra um TruthState antes/depois de uma contestação real”;  
  - “abre o scorecard G2 e me mostra quantas promoções falharam e por quê”.

O que deve continuar:

- Manter o formato de ORR como **inspeção guiada**: perguntas duras, respostas ancoradas em código, testes, métricas e evidências.  
- Evitar apresentações longas e genéricas; o foco deve ser sempre “prova de que funciona / prova de que sabemos quando não funciona”.

---

#### 6.3.4 Sanidade cruzada como parte da sprint, não como pós-crédito

A S32 também mostrou que, para um núcleo crítico, **sanidade cruzada com sprints anteriores não é opcional**.

O que foi importante perceber:

- É perfeitamente possível ter Truth-DB verde e, ainda assim, ter quebrado ingestão, claims ou outras partes importantes do sistema.  
- Se a sanidade cruzada for deixada para depois do merge, o custo de correção sobe muito.

O que funcionou bem quando feito direito:

- Rodar gates/suites de sprints de ingestão/claims (S21, S24, etc.) em ambiente com a S32 aplicada;  
- Classificar regressões em BLOQUEANTES vs NÃO-BLOQUEANTES com critérios claros;  
- Levar esse quadro-síntese para o ORR, em vez de descobrir problemas ao vivo.

Learning de processo:

- Para qualquer sprint que mexa em núcleo de verdade, deve existir, nos Capítulos 4 e 5, uma seção explícita de **sanidade cruzada obrigatória**, com:  
  - lista de gates antigos a rodar;  
  - registro do resultado;  
  - classificação de regressões.

---

#### 6.3.5 Cultura de evidência: “eu acho” não é argumento

A S32 reforçou uma característica central que o Inspectah quer ter como produto e como equipe: **cultura de evidência**.

Momentos em que isso ficou nítido:

- Discussões técnicas que começaram em “acho que está ok” só foram consideradas encerradas quando apareceram:  
  - testes verdes apontando para invariantes específicas;  
  - logs demonstrando o fluxo;  
  - métricas mostrando comportamento estável.

- No ORR, opiniões sem lastro em artefatos foram tratadas como *insights* para tarefas futuras, não como base para GO/NO-GO.

Learning cultural:

- Para o núcleo de verdade, a regra é:  
  > “Sem evidência, não é verdade — é hipótese.”

- Isso vale tanto para o que o sistema afirma sobre o mundo quanto para o que a equipe afirma sobre o próprio sistema.

---

#### 6.3.6 Responsabilidades claras entre sprint, ORR e operação

A S32 ajudou a clarificar o papel de cada “camada” do ciclo de vida do Truth-DB:

- **Sprint**:  
  - implementa modelos, serviços, testes, gates e bundle;  
  - garante que tudo que foi prometido no Capítulo 1–4 existe e roda.

- **ORR**:  
  - não “refaz a sprint”;  
  - julga, com base em evidências, se o que foi feito é suficiente para operar no ambiente-alvo;  
  - registra decisão formal de GO / GO COM RESTRIÇÕES / NO-GO.

- **Operação**:  
  - consome o que a sprint entregou (modelos, serviços, métricas, runbooks);  
  - roda o Truth-DB todos os dias, lida com incidentes, alimenta novos learnings de volta para o backlog.

Learning organizacional:

- Quando essas responsabilidades se confundem (por exemplo, sprint tentando “forçar” GO sem evidência, ou ORR querendo redesign de arquitetura completo em cima da hora), o resultado é caos.  
- A S32 mostra o modelo desejado: sprint entrega; ORR julga com base em evidência; operação roda e devolve feedback real.

---

#### 6.3.7 Síntese do Bloco 3

Do ponto de vista de processo e governança, a Sprint 32 ensinou que:

- Gates bem pensados são trilhos, não burocracia.  
- Bundles são artefatos de produto interno, essenciais para ORR e auditoria.  
- ORRs precisam ser baseados em perguntas difíceis e evidências concretas, não em status reports genéricos.  
- Sanidade cruzada com sprints anteriores é parte da sprint, não “cena pós-crédito”.  
- Cultura de evidência é requisito tanto para o que o sistema afirma sobre o mundo, quanto para o que a equipe afirma sobre o sistema.  
- Sprint, ORR e operação têm papéis distintos e complementares.

Esses learnings de processo são tão estruturais quanto o modelo de dados: se forem ignorados, o núcleo de verdade pode até compilar e passar testes locais — mas não terá a governança necessária para ser levado a sério quando o Inspectah estiver em produção e sob escrutínio real.

