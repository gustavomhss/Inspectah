# Sprint 29 — Capítulo 6
## Bloco 3 — Débitos técnicos assumidos na S29 (backend, frontend e documentação)

Este Bloco 3 trata do segundo eixo do Capítulo 6: **débitos técnicos**. Enquanto o Bloco 2 mapeia riscos (o que pode dar errado), aqui o foco é mais direto:

> "Quais simplificações e concessões técnicas a Sprint 29 fez de propósito para caber no escopo, que não podem ser esquecidas?"

A ideia não é demonizar esses débitos — muitos são escolhas corretas para uma v1 —, mas registrá‑los de forma clara para que:

- ninguém ache que a S29 já entregou "a versão definitiva" do sistema de fluxos;  
- squads futuros (E28.2/E28.3/E28.4, S23–S25) saibam exatamente onde estão as quinas a arredondar;  
- o ORR possa apontar pontos de atenção com base em fatos, não em impressões vagas.

Os débitos estão agrupados em três categorias:

- débitos no backend;  
- débitos no frontend;  
- débitos de documentação/descoberta.

---

### 3.1. Débitos no backend

#### D1 — Cobertura de testes limitada em cenários extremos de fluxo

- Situação:  
  - A S29 implementa testes para o validador de fluxo e para as APIs de criação/atualização em cenários principais (happy path, erros típicos, invariantes básicas).  
  - Porém, combinatórias extremas de fluxos (muitos passos, combinações agressivas de papéis, domínios muito numerosos) não são exaustivamente testadas nesta sprint.
- Motivação da dívida:  
  - evitar explosão combinatória de casos de teste na v1;  
  - focar primeiro na robustez para domínios piloto.
- Impacto potencial:  
  - bugs podem aparecer quando o sistema for usado com fluxos muito grandes ou combinações pouco usuais de papéis;  
  - possível comportamento inesperado em domínios futuros que extrapolem o uso inicialmente previsto.
- Sinalizador para o futuro:  
  - E28.2/E28.3 devem incluir explicitamente uma suíte de testes focada em limites (tamanho de fluxo, número de domínios, stress de validação).

#### D2 — Catálogo de papéis simplificado e pouco estruturado

- Situação:  
  - A S29 trabalha com um catálogo relativamente curto de papéis (INTERPRETER, CLASSIFIER, DEBUNKER, DECISION_MAKER, etc.), modelado de forma direta;  
  - ainda não há estrutura para tipos/subtipos, heranças ou famílias de papéis (por exemplo, diferentes tipos de Debunker, classificadores especializados, analistas de domínio).
- Motivação da dívida:  
  - manter o primeiro corte de modelo de fluxo simples e compreensível;  
  - evitar over‑engineering antes das sprints de Verdade/Debunker definirem melhor o espaço de papéis.
- Impacto potencial:  
  - crescimento desorganizado do catálogo ao longo do tempo (nome de papel virando "metadado" codificado em string);  
  - dificuldade para representar nuances (ex.: Debunker generalista vs Debunker especializado em saúde).
- Sinalizador para o futuro:  
  - em sprints de E28.x e S23–S25, repensar o catálogo como parte do design global de papéis de verdade/debunking, mantendo compatibilidade com o modelo de fluxo.

#### D3 — Instrumentação de runtime mínima

- Situação:  
  - O runtime passa a logar uso de fluxo (flow_id, domínio, sequência de papéis executados) de forma básica;  
  - porém, ainda não há um conjunto rico de campos para correlação com casos, comitês, estados de verdade ou métricas agregadas.
- Motivação da dívida:  
  - não travar a S29 esperando um design completo de observabilidade de E28;  
  - garantir apenas o mínimo para rastrear se fluxo configurado está sendo usado.
- Impacto potencial:  
  - análises futuras (por exemplo, "qual fluxo produz menos erros?", "onde está o gargalo?") podem exigir enriquecimento de logs ou retrabalho em pipelines de observabilidade;  
  - incidentes podem ser mais trabalhosos de investigar, por falta de contexto diretamente ligado ao fluxo.
- Sinalizador para o futuro:  
  - E28.4 (ou sprint equivalente focada em métricas de fluxo) deve tratar o enriquecimento de logs como requisito desde o início.

#### D4 — Regras de invariantes ainda focadas em casos principais

- Situação:  
  - O validador de fluxo implementa invariantes consideradas mais importantes: não permitir fluxo vazio, exigir certos papéis em domínios sensíveis, garantir DECISION_MAKER em posição correta, etc.;  
  - invariantes mais sutis (por exemplo, combinações de papéis que fazem pouco sentido, redundâncias óbvias, ou políticas específicas por tipo de domínio) são postergadas.
- Motivação da dívida:  
  - evitar engessar a v1 com regras excessivamente rígidas antes de observar fluxos reais em operação;  
  - manter flexibilidade de experimentação em domínios piloto.
- Impacto potencial:  
  - operadores podem criar fluxos teoricamente válidos, mas subótimos (por exemplo, repetições desnecessárias de papéis, ordem "estranha" porém tecnicamente permitida);  
  - necessidade de ajustar invariantes conforme aprendizado de uso real.
- Sinalizador para o futuro:  
  - revisar invariantes após fase piloto, incorporando feedback de S23–S25 e da operação.

---

### 3.2. Débitos no frontend

#### D5 — UX do editor de fluxo focada em lista linear

- Situação:  
  - O editor de fluxo v1 é baseado em lista: o usuário vê uma sequência de passos com controles de adicionar/remover/mover;  
  - não há visualização em grafo, agrupamentos por tipo de agente, nem camadas visuais para condições ou ramificações.
- Motivação da dívida:  
  - UI simples é mais rápida de entregar e mais fácil de estabilizar na v1;  
  - branching e condicionais ainda não fazem parte do escopo da S29.
- Impacto potencial:  
  - fluxos maiores podem ficar difíceis de entender visualmente;  
  - operadores com background menos técnico podem achar a configuração de fluxo pouco intuitiva.
- Sinalizador para o futuro:  
  - E28.3/E28.4 são candidatas naturais para evoluir a UX do editor (introduzindo agrupamentos, visualizações mais ricas, filtros, etc.).

#### D6 — Validação client-side mínima

- Situação:  
  - A maior parte das regras vive corretamente no backend;  
  - a UI faz apenas validações básicas (campos obrigatórios, sintaxe de parâmetros, etc.), deixando casos mais complexos para o validador do servidor.
- Motivação da dívida:  
  - evitar duplicação de lógica de negócio complexa na camada de frontend;  
  - manter o backend como fonte única de verdade para invariantes.
- Impacto potencial:  
  - experiência de usuário mais "trial and error": o operador tenta salvar, recebe erro do backend e precisa ajustar;  
  - sensação de que a UI "deixa fazer qualquer coisa" até o backend reclamar.
- Sinalizador para o futuro:  
  - introduzir validações client-side que usem apenas dados estáticos (por exemplo, catálogo de papéis e posição da última etapa) para evitar erros mais óbvios antes do envio, sem replicar lógica completa.

#### D7 — Integração limitada com design system e navegação global

- Situação:  
  - A UI de fluxos utiliza componentes do design system existente, mas pode não explorar todas as possibilidades de consistência visual e navegacional (breadcrumbs, estados vazios ricos, tooltips explicativos, etc.);  
  - a navegação entre "visão global de fluxos" e "edição de domínio específico" é funcional, porém ainda simples.
- Motivação da dívida:  
  - priorizar funcionalidade (poder editar fluxos) sobre refinamentos de UX e navegação na v1;  
  - evitar redesenhar padrões globais do console no escopo da S29.
- Impacto potencial:  
  - a área de fluxos pode parecer menos "polida" que outras partes do console;  
  - pequenas fricções de navegação podem cansar operadores em uso intensivo.
- Sinalizador para o futuro:  
  - quando o uso de fluxos se tornar mais central na operação, revisar essa tela em conjunto com o time de UX/design para nivelar a experiência com o restante do console.

---

### 3.3. Débitos de documentação e descoberta

#### D8 — Documentação de operação ainda enxuta

- Situação:  
  - O ORR da S29 e o Capítulo 5 descrevem o estado do produto, mas ainda não existe um documento dedicado do tipo "Como editar fluxos de agentes sem se machucar";  
  - explicações sobre o que cada papel faz e como combinar agentes ainda podem estar dispersas entre capítulos e discussões de projeto.
- Motivação da dívida:  
  - priorizar especificação, implementação e ORR dentro da S29;  
  - deixar material de onboarding detalhado para depois da estabilização inicial.
- Impacto potencial:  
  - onboarding mais difícil para novos operadores;  
  - risco de uso inadequado da feature por falta de orientação clara.
- Sinalizador para o futuro:  
  - produzir um guia curto e opinativo de operação em sprint futura (pode ser anexado ao Programa 1 ou às sprints de Verdade/Debunker).

#### D9 — Ausência de catálogo público de fluxos canônicos por domínio

- Situação:  
  - Não há ainda um "catálogo oficial" de fluxos recomendados por tipo de domínio (ex.: política, economia, saúde, dados de mercado);  
  - configurações de domínios piloto existem, mas não estão documentadas como exemplos pedagógicos.
- Motivação da dívida:  
  - a S29 foca na infraestrutura e no suporte mínimo para pilotos;  
  - desenho de fluxos ideais por domínio é tarefa que depende fortemente do squad Verdade & Interpretação e de aprendizado em campo.
- Impacto potencial:  
  - operadores podem improvisar fluxos sem referência de boas práticas;  
  - dificuldade em alinhar configuração de fluxo com política de verdade/debunking.
- Sinalizador para o futuro:  
  - em E28.2/E28.3 ou sprints de Verdade, criar um catálogo de fluxos de referência, com justificativas de design, para ser usado como base.

#### D10 — Falta de "tour" guiado ou walkthrough na própria UI

- Situação:  
  - A UI de fluxos é funcional, mas não oferece, por enquanto, um walkthrough guiado (dicas contextuais, tooltips iniciais, mini-tutorial) para novos usuários;  
  - o operador depende de conhecimento prévio ou de documentação separada.
- Motivação da dívida:  
  - evitar atrasar a entrega da v1 por conta de UX avançada;  
  - manter a tela simples, com foco nos usuários iniciais e próximos à equipe.
- Impacto potencial:  
  - novos operadores podem precisar de ajuda humana nas primeiras utilizações;  
  - maior risco de configurações equivocadas nos primeiros ciclos de uso.
- Sinalizador para o futuro:  
  - considerar, em E28.4 ou em uma sprint de UX, adicionar dicas inline, estados vazios explicativos e exemplos prontos na UI.

---

### 3.4. Amarração do Bloco 3

Com este Bloco 3, o Capítulo 6 ganha um inventário explícito de **débitos técnicos** assumidos na Sprint 29:

- no backend, a fundação de fluxo foi priorizada em detrimento de testes extremos, catálogo hiperestruturado e instrumentação completa;  
- no frontend, a prioridade foi entregar uma UI funcional e alinhada à v1 do modelo, deixando UX avançada e validações mais ricas para sprints futuras;  
- na documentação, a S29 apostou em especificação e ORR robustos, aceitando uma dívida em materiais de operação e catálogos de boas práticas.

Nos próximos blocos do Capítulo 6, esses débitos serão conectados a:

- um **plano de mitigação e follow-up** (quem puxa o quê, em qual horizonte);  
- critérios de **monitoramento pós-sprint, rollback e expansão de escopo**;  
- e ao **long tail** da S29, garantindo que futuras squads e sprints não precisem redescobrir essas decisões do zero.

