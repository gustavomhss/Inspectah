# Inspectah — Sprint 32  
## Capítulo 6 — Learnings, Anti-Gaps & Riscos Residuais (Truth-DB & Contestação v1)

> Este capítulo captura **o que a Sprint 32 ensinou** — técnica e operacionalmente — e **que proteções permanentes** precisamos manter para não repetir erros quando evoluirmos o núcleo de verdade (Truth-DB + Contestação v1) nas próximas sprints.

---

### 6.1 Papel do Capítulo 6 na Sprint 32

O Capítulo 6 da S32 tem três funções principais:

1. Registrar **learnings técnicos** que não cabem em comentários de código ou testes, mas que são críticos para futuras decisões de arquitetura.
2. Documentar **learnings de processo e governança**, em especial tudo que impacta a forma como projetamos, testamos e auditamos verdades no Inspectah.
3. Construir uma camada explícita de **anti-gaps**: coisas que não podem ficar implícitas e precisam estar amarradas em políticas, gates, checklists, tarefas futuras ou práticas obrigatórias.

A S32 é o primeiro passo de colocar o Truth-DB em operação. Isso significa que erros aqui tendem a se tornar **erros estruturais** se não forem encarados de frente neste capítulo.

---

### 6.2 Learnings técnicos — Truth-DB, blocos e contestação

#### 6.2.1 Modelagem de blocos e estados

- A separação explícita entre `FactBlock`, `EvidenceBlock`, `TruthState`, `DecisionBlock` e `ContestRecord` se mostrou **crucial para auditabilidade**:  
  - Qualquer tentativa de “simplificar demais” (ex.: colapsar fatos e estados numa tabela única) rapidamente leva a dificuldades em contar a história de como a verdade evoluiu.  
- A decisão de manter `TruthState` como entidade separada, apontando para blocos e carregando o status atual, é importante para:  
  - consultas rápidas sobre “o que é verdade agora”;  
  - preservação de histórico via blocos (linha do tempo) sem sobrecarregar o modelo de leitura.
- Learnings:  
  - **Não misturar** visão de leitura (`TruthState`) com histórico e evidências (blocos).  
  - Garantir que qualquer evolução futura do modelo preserve a distinção entre “instante da decisão” (DecisionBlock) e “visão atual” (TruthState).

#### 6.2.2 Invariantes como contratos de primeira classe

- A S32 deixou claro que certas invariantes são **não negociáveis**:  
  - não existem blocos órfãos;  
  - estados finais de verdade sempre têm DecisionBlock associado;  
  - histórico é monotônico (nunca deletar blocos/decisões em função de contestação);  
  - ContestRecords não somem sem deixar trilha.
- Importante: essas invariantes não podem viver só em docs – elas precisam estar:  
  - codificadas em modelos (constraints, validações);  
  - protegidas em testes dedicados;  
  - verificadas em gates específicos (G1, G2, G3).  
- Learning: qualquer mudança futura no Truth-DB deve ser lida **primeiro** pelos olhos das invariantes, e **só depois** como refino funcional. As invariantes são o “chão” do sistema.

#### 6.2.3 Fluxos de promoção e contestação

- A S32 mostrou que é mais simples e mais seguro **começar com uma lógica v1 explícita e simples** (promotion/contestation), do que tentar antecipar toda a complexidade futura:  
  - fluxo de promoção claro (claim → blocos → estado);  
  - fluxo de contestação mínimo porém rastreável (estado → ContestRecord → novo DecisionBlock/TruthState).
- Sempre que tentamos sofisticar demais a lógica de decisão na v1, surgiram duas classes de problema:  
  - explosão de casos de teste difíceis de manter;  
  - dificuldade em explicar a lógica em uma sessão de ORR de 30–40 minutos.
- Learning:  
  - v1 deve privilegiar **clareza e auditabilidade**, não complexidade inteligente;  
  - sofisticação (comitês, pesos, políticas mais ricas) deve ser adicionada em camadas posteriores, com gates adicionais.

#### 6.2.4 Métricas e observabilidade

- Um dos principais learnings foi perceber que **sem métricas mínimas específicas**, o Truth-DB vira uma caixa-preta assustadora:  
  - `truthdb_promotion_success_rate`, `truthdb_contestation_rate`, `truthdb_flow_error_rate`, `truthdb_flow_latency_p95` são o mínimo para saber se o sistema está vivo ou se está morrendo silenciosamente.  
- Métricas genéricas de API ou de banco não são suficientes para responder à pergunta “o núcleo de verdade está saudável?”.
- Learning: qualquer evolução do Truth-DB deve vir acompanhada de **métricas específicas**, alinhadas com suas responsabilidades lógicas, não apenas com infraestrutura.

---

### 6.3 Learnings de processo, governança e ORR

#### 6.3.1 Gates não são burocracia — são trilhos

- A S32 reforçou que gates bem desenhados (G1, G2, G3, G4) funcionam como **trilhos de execução**:  
  - ajudam a equipe a decidir o que fazer primeiro;  
  - evitam que fluxos complexos sejam implementados em cima de um modelo ainda instável;  
  - produzem scorecards que tornam o ORR objetivo.
- Quando o time tentou “atalhar” e implementar serviços antes de consolidar modelos e invariantes, o resultado foi retrabalho e confusão de migrações.
- Learning:  
  - o desenho de gates precisa ser encarado como parte da arquitetura, não como tarefa à parte;  
  - qualquer sprint que mexer com núcleo crítico deve ter gates pensados desde o Capítulo 2.

#### 6.3.2 Bundles como artefato de produto, não de processo

- O bundle `inspectah_s32_evidence_bundle.zip` se mostrou uma ferramenta poderosa para:  
  - ORR (revisão baseada em evidência);  
  - auditorias futuras (replay de estados);  
  - debugging de regressões (reexecução de gates a partir do bundle).
- Learning:  
  - bundles não são “nice-to-have”: eles são parte do produto Inspectah, pois permitem reconstituir o que o sistema sabia e como ele validou isso numa dada sprint.

#### 6.3.3 ORR focado em perguntas difíceis

- ORRs que se limitam a “status do projeto” são superficiais; o formato da S32, centrado em perguntas difíceis (modelo, invariantes, promoção, contestação, observabilidade), produziu discussões muito mais ricas.  
- Learning:  
  - manter, para sprints futuras, a prática de ORR baseada em **painel de perguntas + artefatos**, e não em apresentações genéricas.

---

### 6.4 Anti-gaps — coisas que não podem ficar implícitas

Esta seção lista anti-gaps específicos extraídos da execução da S32. Cada item deve ser tratado como **regra permanente** ou como tarefa explícita em Capítulo 7 / backlog.

#### 6.4.1 Anti-gap: invariantes não podem morar só em docs

- Risco identificado: invariantes críticas descritas apenas em textos (docs, comentários) acabarem não refletidas no código.  
- Proteção:  
  - toda invariante crítica deve ter:  
    - representação clara em `models.py` (constraints, validações);  
    - testes dedicados em `tests/truthdb/test_models_and_invariants.py`;  
    - checagem direta em G1.

#### 6.4.2 Anti-gap: contestações sem trilha

- Risco identificado: contestações serem tratadas como sinais efêmeros (logs, mensagens soltas) e não como entidades de primeira classe.  
- Proteção:  
  - `ContestRecord` é obrigatório para qualquer contestação;  
  - nenhum fluxo de contestação pode “pular” essa entidade;  
  - qualquer novo tipo de contestação deve passar por testes e métricas específicos.

#### 6.4.3 Anti-gap: métricas genéricas tentando substituir métricas de domínio

- Risco: confiar em CPU, memória, 5xx genéricos e tempo de resposta de API para inferir a saúde do Truth-DB.  
- Proteção:  
  - métricas específicas do Truth-DB devem ser consideradas “hard requirement” para qualquer promoção de ambiente;  
  - ORR não deve conceder GO sem evidência de que essas métricas existem e são compreendidas pela equipe.

#### 6.4.4 Anti-gap: ORR sem bundle ou com bundle simbólico

- Risco: tratar o bundle como formalidade (zip vazio, incompleto ou inconsistente).  
- Proteção:  
  - G4 falha se o bundle estiver ausente, quebrado ou fora do padrão mínimo;  
  - ORR não acontece (ou é explícito pré-ORR exploratório) na ausência de bundle decente.

#### 6.4.5 Anti-gap: sanidade cruzada deixada para “depois”

- Risco: integrar o Truth-DB com ingestão/claims sem rodar gates/suites das sprints de ingestão.  
- Proteção:  
  - toda sprint que mexer em núcleo crítico deve ter **seção específica de sanidade cruzada** (Capítulo 4 + Capítulo 5);  
  - ORR deve exigir evidência dessa sanidade antes de discutir GO/NO-GO.

---

### 6.5 Riscos residuais identificados na S32

Mesmo com todos os gates e evidências, a S32 deixa alguns riscos residuais, que precisam ser monitorados e tratados nas sprints seguintes.

Exemplos (ajustáveis conforme execução real):

1. **Cobertura limitada de tipos de claims**  
   - v1 pode cobrir apenas um tipo de claim; há risco de uso indevido do Truth-DB para tipos não suportados.  
   - Mitigação: validações fortes em PromotionService; mensagens de erro claras; tasks futuras para ampliar cobertura.

2. **Lógica de contestação simplificada demais**  
   - v1 pode apenas marcar estados como contestados ou ajustar status de forma simples;  
   - risco de overtrust ou undertrust do estado resultante.  
   - Mitigação: documentar limites da v1; usar GO COM RESTRIÇÕES se necessário; planejar evolução em S33+.

3. **Observabilidade ainda em estágio inicial**  
   - Mesmo com métricas mínimas, os painéis podem ser simples demais para detectar padrões complexos de falha.  
   - Mitigação: tasks para enriquecer painéis; inclusão de alertas para thresholds básicos.

4. **Dependência forte de conhecimento interno**  
   - Modelo de dados e fluxo ainda podem exigir muito contexto da equipe núcleo;  
   - risco de novos membros usarem o Truth-DB de forma incorreta.  
   - Mitigação: melhorar documentação de “how-to” (dev & operação); criar exemplos reexecutáveis a partir do bundle.

Cada risco residual deve ser mapeado para tasks concretas (Capítulo 7) ou para épicos futuros, com prioridade clara.

---

### 6.6 Recomendações estruturais para S33+ (e além)

Baseado na S32, as recomendações estruturais para o futuro do núcleo de verdade são:

1. **Manter a disciplina de núcleos críticos**  
   - Qualquer sprint que mexa com Truth-DB, comitês, causalidade ou políticas de promoção deve herdar:  
     - gates derivados da S32;  
     - bundle obrigatório;  
     - ORR com painel de perguntas específico.

2. **Evoluir por camadas, não por reescrita**  
   - Em vez de reescrever o Truth-DB, adicionar camadas:  
     - lógica de decisão mais rica;  
     - camadas de comitê;  
     - integração com blockchain/ancoragem quando for a hora certa.  
   - Sempre preservar compatibilidade com dados e invariantes da S32.

3. **Tratar o Truth-DB como produto interno de plataforma**  
   - Consumido por ingestão, por comitês, por UI e por produtos externos;  
   - com SLAs, métricas e expectativas claras de comportamento.

4. **Amplificar a “cultura de evidência” inaugurada pela S32**  
   - Scorecards, bundles, sanidade cruzada e ORR centrado em perguntas devem se tornar padrão cultural, não exceção.

---

### 6.7 Síntese final do Capítulo 6

- A Sprint 32 ensinou que **verdade sem estrutura é opinião** e que, no Inspectah, essa estrutura precisa ser:  
  - modelada com blocos e estados claros;  
  - protegida por invariantes codificadas;  
  - auditável via bundles e scorecards;  
  - operada com métricas e runbooks.

- Este Capítulo 6 cristaliza esses learnings e anti-gaps para que:  
  - nenhuma próxima sprint trate o Truth-DB como “só mais um módulo”;  
  - qualquer evolução futura parta da consciência dos riscos e das proteções já estabelecidas aqui.

A S32, portanto, não é apenas a sprint que “ligou o Truth-DB”, mas a sprint que definiu **como o Inspectah trata verdade, contestação e evidência** em nível de engenharia e operação. O Capítulo 6 é o manual para não esquecer isso quando o sistema ficar muito maior.

