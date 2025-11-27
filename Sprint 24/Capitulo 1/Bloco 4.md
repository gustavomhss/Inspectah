# Sprint 24 – Capítulo 1.4  
**Escopo, fora de escopo e dependências (v2 – Playbook v2)**

---

## 1. Visão de escopo da Sprint 24

A Sprint 24 tem como foco exclusivo tirar do papel o **Debunker v0 com humano-no-loop**, operando em produção limitada, mas já integrado ao resto do Inspectah. O objetivo é sair da sprint com:

- Um **fluxo completo de contestação** funcionando ponta a ponta (da detecção de conflito até a decisão registrada),
- Uma **UI mínima, porém utilizável**, para revisores humanos (Debunkers),
- **Contratos claros** entre S23 (interpretação/classificação), S24 (Debunker v0) e S25 (Truth-DB & Governança de Verdade),
- Evidências, logs e métricas suficientes para S25 confiar nas saídas da sprint.

Nada em S24 precisa ser perfeito ou definitivo, mas tudo que entrar no escopo deve ser **operacional, auditável e não-descartável**: é um v0 que já pode rodar de verdade, em regime controlado.

---

## 2. Escopo detalhado – o que entra na Sprint 24

### 2.1. Escopo funcional (produto)

Esta sprint **inclui**:

1. **Modelo de caso para Debunker v0**  
   - Definição de um tipo de entidade explícito para casos de contestação (ex.: `DebunkCase`), com campos mínimos: claim/timeline afetada, fontes relevantes, resumo estruturado do conflito, estado atual, responsável, histórico de decisões.
   - Estados de ciclo de vida iniciais para o Debunker v0 (ex.: `NEW`, `TRIAGED`, `IN_REVIEW`, `WAITING_EVIDENCE`, `DECIDED`, `ARCHIVED`).

2. **Pipeline de entrada de casos (interface com S23)**  
   - Contrato de como S23 envia casos ao Debunker v0 (fila interna, tabela dedicada, API ou evento).  
   - Critérios mínimos para um caso ser elegível para Debunker (ex.: alta divergência entre fontes, conflito entre classificações, contestação explícita de usuário futuro).  
   - Mecanismo para **anexar evidências e metadados** (scores, classificações, trechos de texto, links, IDs de TruthRecords).

3. **UI mínima para revisores humanos (painel do Debunker)**  
   - Tela para listar casos pendentes, com filtros essenciais (estado, prioridade, tipo de claim, data).  
   - Tela de detalhe do caso com: resumo, claims envolvidos, evidências, timeline relevante, proposta inicial do comitê de agentes (S23) e área para decisão humana.  
   - Fluxo de decisão do Debunker: **aceitar, rejeitar, pedir mais evidência, marcar como inconclusivo**, com campos obrigatórios de justificativa.

4. **Lógica de decisão assistida por agentes (comitê de apoio)**  
   - Uso dos agentes da S23 como apoio ao Debunker: resumo do conflito, extração de argumentos pró/contra, identificação de lacunas de evidência.  
   - Geração de um **parecer preliminar automatizado**, sempre acompanhado de explicações e níveis de confiança – nunca decisão final automática.  
   - Registro explícito de quando a decisão humana concorda ou diverge do comitê de agentes.

5. **Registro estruturado da decisão e efeitos colaterais**  
   - Emissão de um **evento de decisão** (ex.: `DebunkDecisionEvent`) consumível por S25, contendo: decisão, justificativa, evidências usadas, referências a TruthRecords/timelines afetadas.  
   - Regras de que tipo de decisão **pode** alterar o estado de verdade e quais ainda dependem de lógica a ser implementada em S25 (Sprint 24 só emite o evento + recomendação).

6. **Métricas, logs e scorecards de S24**  
   - Métricas básicas: tempo médio em cada estado, quantidade de casos decididos por dia, taxa de casos reabertos, divergência entre comitê de agentes e revisores humanos.  
   - Logs estruturados por caso, com trilha completa de quem fez o quê, quando e por quê.  
   - Scorecards específicos da sprint (ex.: `out/scorecards/S24_G*_*.json`) com campos que alimentem S25.

### 2.2. Escopo técnico – backend

- Endpoints / handlers necessários para:
  - Listar, criar e atualizar `DebunkCase` (apenas via ingestão interna, não por usuário final nesta fase).
  - Registrar decisões de Debunker e gerar eventos de saída para S25.  
  - Servir dados para as UIs (painel de casos, detalhe do caso).
- Modelagem mínima no banco para suportar:
  - Tabela de casos de Debunker e tabela de decisões/ações.  
  - Referências para TruthRecords, timelines e evidências (sem duplicar conteúdo pesado desnecessariamente).
- Integração com o sistema de jobs/filas já existente, se necessário, para pré-processar casos em lote.

### 2.3. Escopo técnico – frontend / UX

- Páginas de **admin** específicas para o Debunker v0, integradas ao console existente:
  - Lista de casos com paginação, filtros e indicação visual de prioridade.  
  - Tela de detalhe com layout pensado para leitura rápida: resumo em cima, evidências à esquerda, parecer automático à direita, campo de decisão/julgamento em destaque.  
- Tratamento adequado de estados vazios, erros e carregamento (skeletons coerentes com o resto do Inspectah).
- Telemetria de UI: eventos para abertura de caso, decisão tomada, tempo gasto na tela, abandono sem decisão etc.

### 2.4. Escopo de observabilidade e operação

- Logs de aplicação e de UI com **correlação por ID de caso**, facilitando reconstruir a história de um DebunkCase.  
- Métricas expostas em endpoints de métricas já existentes (Prometheus/Grafana) com painéis mínimos para o squad acompanhar a saúde do Debunker v0.  
- Evidências de gates da sprint (S24_G*) armazenadas em `out/evidence/` com padrão consistente com sprints anteriores.

---

## 3. Fora de escopo – o que **não** entra na Sprint 24

### 3.1. Fora de escopo funcional

Nesta sprint **não entra**:

1. **Comunidade aberta de revisores / crowd-debunking**  
   - S24 trabalha apenas com **revisores humanos internos** (time de confiança).  
   - Mecanismos de reputação pública, gamificação ou moderação aberta ficam explicitamente para fases posteriores.

2. **Mudanças diretas e automáticas no estado de verdade (Truth-DB)**  
   - S24 não implementa a lógica final de promoção/degradação de estados de verdade.  
   - A sprint apenas emite eventos ricos e decisões recomendadas; a aplicação dessas decisões sobre a Truth-DB é responsabilidade da S25.

3. **Suporte a todos os domínios possíveis**  
   - O Debunker v0 não precisa cobrir todos os tipos de casos que o Inspectah terá no futuro.  
   - S24 se concentra em um conjunto restrito de domínios/padrões (ex.: notícias factuais e timelines de eventos públicos), suficientes para validar o modelo.

4. **Interface pública de contestação para usuários finais**  
   - Formulários públicos, autenticação de contestantes, políticas de spam e abuso não são tratados em S24.  
   - A sprint assume contestação “vinda de dentro” (dos próprios agentes do Inspectah e de operadores internos).

5. **Versionamento completo de políticas e modelos de decisão**  
   - Ainda não será criado um sistema sofisticado de versionamento de políticas de Debunker; mudanças de regra podem ser documentadas em config + docs.  
   - O sistema registra decisões e justificativas, mas não precisa permitir re-execução automática com políticas antigas.

### 3.2. Fora de escopo técnico

- Integrações com blockchain, ancoragem on-chain de decisões de Debunker ou de TruthRecords.  
- Infraestrutura de alta disponibilidade específica para o Debunker (ex.: sharding dedicado, filas multi-região); o v0 pode rodar em infraestrutura compartilhada, desde que observável e estável.  
- Mecanismos automáticos de sugestão de novos tipos de casos para Debunker (auto-descoberta de padrões complexos) – isso é material para futuras sprints de inteligência.

### 3.3. Fora de escopo de UX/Produto

- Design visual definitivo da experiência do Debunker (branding próprio, flows super refinados).  
- Onboarding completo de novos revisores (tutoriais interativos, tracking de proficiência).  
- Ferramentas avançadas de anotação colaborativa (comentários encadeados, múltiplos revisores simultâneos).  

Tudo isso pode ser antecipado conceitualmente em S24 (como notas para o futuro), mas **não entra como critério de GO**.

---

## 4. Dependências internas e externas

### 4.1. Dependências internas de Inspectah

1. **S21 – Console de Fontes / Cadastro de Fontes**  
   - Dependência: fontes mínimas cadastradas e funcionando para produzir conteúdo que, em última instância, gere casos de contestação.  
   - Mitigação: caso alguma fonte ainda não esteja madura, a sprint pode trabalhar com um subconjunto controlado de fontes já estáveis.

2. **S22 – Ingestão 2.0 por Fonte**  
   - Dependência crítica: ingestão confiável e rastreável (logs e metadados suficientes para entender de onde veio cada claim/evidência).  
   - Sem isso, o Debunker v0 vira um sistema cego que não sabe “de onde veio a verdade”.

3. **S23 – Interpretação e Classificação (camadas de agentes)**  
   - Dependência direta: S24 **não descobre casos do nada**.  
   - Precisa de S23 produzindo:
     - Claims estruturados,  
     - Classificações de risco/consistência,  
     - Sinais de conflito ou incerteza que elevem um caso a DebunkCase.
   - Contrato: formato dos artefatos que chegam a S24 (schema, campos obrigatórios, tipos de conflito).

4. **S19 – Timeline & XRay**  
   - Dependência secundária, porém importante: o Debunker v0 precisa enxergar a timeline de um caso (eventos, verdades provisórias, mudanças passadas).  
   - Mesmo que S24 não edite a timeline diretamente, ela precisa consumir essa visão.

5. **Infraestruturas de logs e métricas (Sprints anteriores)**  
   - Necessário aproveitar o que já existe para não reinventar tracking de eventos e métricas.  
   - Dependência em coletores, dashboards e padrões de nome de métricas.

### 4.2. Dependências externas

- **Modelos de linguagem (LLMs) estáveis**  
  - A sprint assume disponibilidade estável dos modelos usados pelos comitês de agentes (S23).  
  - Estratégia de mitigação: ter pelo menos um modelo de fallback configurado e logs claros de qual modelo decidiu o quê.

- **Ambiente de CI/CD consolidado**  
  - Necessário para rodar gates automatizados, testes de regressão e manter a saúde do Debunker v0.  
  - Dependência em pipelines já definidos (ORR, scorecards, evidências).

- **Infra mínima de banco de dados e filas**  
  - O cluster e as filas usadas pelo Inspectah precisam suportar o acréscimo de carga de casos de Debunker, mesmo em regime limitado.

### 4.3. Dependências de pessoas e alinhamento

- **Squad Verdade & Interpretação ativo** (Pearl, Stonebraker, Norvig, Percy)  
  - Essencial para definir, revisar e aprovar o modelo de casos, contratos entre sprints e critérios de decisão.  
- **PO do Inspectah**  
  - Responsável por decisões de trade-off entre profundidade do Debunker v0 e prazo da sprint.  
- **Squad de Timeline/UI**  
  - Necessário para alinhar como o Debunker consome e eventualmente afeta a visualização de timelines.

---

## 5. Resumo executivo do escopo

- **Entra em S24:** Debunker v0 operacional, com casos estruturados, pipeline de entrada bem definido, UI mínima de revisão humana, integração com comitês de agentes e emissão de eventos ricos para S25, tudo rastreável e medido.
- **Não entra em S24:** comunidade aberta de revisores, governança completa da Truth-DB, integração on-chain, suporte a todos os domínios possíveis, design visual definitivo ou features avançadas de colaboração.
- **Depende de:** ingestão 2.0 estável, interpretação/classificação de S23 funcionando, timeline consultável, infra de logs/métricas, modelos de linguagem disponíveis e squad de Verdade & Interpretação alinhado.

Esse subcapítulo amarra **o que exatamente a Sprint 24 promete entregar**, **o que conscientemente fica para depois** e **de quem ela depende** para conseguir chegar ao GO com o Debunker v0 digno do Inspectah.

