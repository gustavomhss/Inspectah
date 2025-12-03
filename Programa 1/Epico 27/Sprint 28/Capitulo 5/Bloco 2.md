# Inspectah — Sprint 28
## Capítulo 5 — Bloco 2
### Riscos Remanescentes da Sprint 28 (Mapa Detalhado por Categoria)

---

#### 5.2.1 Convenções deste bloco

Para manter os riscos da Sprint 28 manejáveis e auditáveis, cada risco é descrito com os campos:

- **ID**: identificador curto e estável (ex.: `R-28-P1`).  
- **Categoria**: Produto/UX, Técnico (Domínio/API), Técnico (Ingestão 2.0), Operacional.  
- **Descrição**: síntese do risco.  
- **Sintomas / Gatilhos**: como o risco aparece na prática.  
- **Impacto**: o que acontece se o risco se materializar.  
- **Probabilidade (heurística)**: Baixa / Média / Alta.  
- **Severidade (heurística)**: P0 (crítico), P1 (alto), P2 (médio), P3 (baixo).  
- **Mitigação planejada**: como S28 e as próximas sprints pretendem reduzir esse risco.  
- **Janela de tratamento sugerida**: S28 (se ainda der), E27.2, E27.3, ou mais adiante.  
- **Owner sugerido**: papel responsável (não necessariamente uma pessoa).

Este bloco lista apenas riscos **remanescentes após S28 estar em GO**. Riscos que já foram neutralizados pela própria sprint não aparecem aqui.

---

#### 5.2.2 Riscos de Produto / Experiência (UX)

##### R-28-P1 — Console não cobre cenários avançados de operação

- **ID**: R-28-P1  
- **Categoria**: Produto / UX  
- **Descrição**: O console de fontes v2 cobre bem os fluxos A–D (criar, desativar, reativar, editar), mas ainda é limitado para cenários de operação mais complexos (filtros avançados, visão por grupos de fontes, etc.).  
- **Sintomas / Gatilhos**:  
  - Operadores com muitas fontes cadastradas começam a sofrer para encontrar subconjuntos específicos (por domínio, criticidade, modo, combinação de filtros).  
  - Dificuldade em situar fontes dentro de um contexto (ex.: "todas as fontes relacionadas a um tema/caso X").  
- **Impacto**:  
  - Aumento de tempo operacional para tarefas simples.  
  - Risco de erros humanos por seleção equivocada de fontes.  
  - Sensação de "ferramenta limitada" à medida que o sistema cresce.  
- **Probabilidade**: Alta (à medida que o número de fontes cresce, o problema deixa de ser teórico).  
- **Severidade**: P1 (alto impacto em eficiência, ainda que não quebre segurança ou verdade).  
- **Mitigação planejada**:  
  - Evoluir filtros combinados (estado + modo + domínio + criticidade) e permitir salvar visões.  
  - Introduzir no futuro visão orientada a grupos/temas.  
- **Janela de tratamento sugerida**:  
  - Itens iniciais em **E27.2**, aprofundamento em **E27.3**.  
- **Owner sugerido**: Product Owner de E27 + Frontend Owner do console.

---

##### R-28-P2 — Trilha de auditoria insuficiente para operações em fonte

- **ID**: R-28-P2  
- **Categoria**: Produto / UX (com impacto em Governança)  
- **Descrição**: S28 registra mudanças de estado em `Source` (`state`, `state_changed_at`, `state_reason`), mas não oferece uma trilha de auditoria completa (quem fez o quê, de onde, com qual contexto).  
- **Sintomas / Gatilhos**:  
  - Incidente em produção envolvendo desativação ou edição de fonte crítica.  
  - Necessidade de reconstruir "quem desligou o quê" em uma linha do tempo confiável.  
- **Impacto**:  
  - Dificuldade em apurar responsabilidades e causas-raiz de incidentes.  
  - Problemas para aderir a políticas internas de governança e, futuramente, a uma política de verdade/fato baseada em evidências.  
- **Probabilidade**: Média (depende da intensidade de uso e criticidade de fontes).  
- **Severidade**: P1 (impacta segurança operacional e governança).  
- **Mitigação planejada**:  
  - Introdução de um modelo de auditoria `SourceActionLog` em E27.2.  
  - Exposição de timeline por fonte no console em E27.3.  
  - Integração com Sistema de Blocos/Truth-DB em etapas posteriores.  
- **Janela de tratamento sugerida**:  
  - Especificação e implementação inicial em **E27.2**.  
  - UX e integração avançada em **E27.3**+.  
- **Owner sugerido**: Squad de E27 (com participação forte de Verdade & Interpretação e de Stonebraker/Truth-DB para alinhamento futuro).

---

##### R-28-P3 — UX de formulários ainda básica para configurações complexas

- **ID**: R-28-P3  
- **Categoria**: Produto / UX  
- **Descrição**: O formulário de criação/edição de fontes trabalha com validações genéricas, não com fluxos guiados profundos por tipo de fonte (ex.: RSS, API JSON, etc.).  
- **Sintomas / Gatilhos**:  
  - Operadores preenchem configurações complexas (URLs com parâmetros, headers de API, etc.) sem apoio guiado.  
  - Erros de configuração só aparecem nos logs de ingestão, longe do contexto do formulário.  
- **Impacto**:  
  - Aumento de tentativas e erros para cadastrar/ajustar fontes.  
  - Risco de fontes aparentemente "ativas" que, na prática, nunca ingerem corretamente.  
- **Probabilidade**: Alta (quase garantida em ambientes com fontes diversificadas).  
- **Severidade**: P2 (impacto operacional relevante, mas contornável com suporte da equipe).  
- **Mitigação planejada**:  
  - Criar presets por tipo de fonte com campos específicos e validações mínimas (E27.2).  
  - Evoluir para wizards com testes de conexão em tempo real (E27.3).  
- **Janela de tratamento sugerida**:  
  - Começar em **E27.2**, expandir em **E27.3**.  
- **Owner sugerido**: Frontend Owner + Product Owner de E27, em articulação com quem desenhará integração com ingestão.

---

#### 5.2.3 Riscos Técnicos — Domínio & Backend (Modelo `Source` + Admin API)

##### R-28-T1 — Evolução futura de `Source` quebrar contratos existentes

- **ID**: R-28-T1  
- **Categoria**: Técnico — Domínio / Backend  
- **Descrição**: O modelo `Source` tende a crescer (novos campos, associações, índices), e alterações mal planejadas podem quebrar Admin API, migrations e compatibilidade com ingestão.  
- **Sintomas / Gatilhos**:  
  - Novas sprints adicionam campos, alteram tipos ou constraints sem considerar contratos existentes.  
  - Scripts e testes antigos começam a falhar de forma aparentemente aleatória.  
- **Impacto**:  
  - Migrações custosas e arriscadas em base com muitas fontes.  
  - Riscos de downtime ou inconsistência de dados.  
- **Probabilidade**: Média (depende de disciplina de projeto).  
- **Severidade**: P1 (pode afetar operação em produção).  
- **Mitigação planejada**:  
  - Tratar `Source` como entidade "core" com revisão extra em qualquer mudança de schema.  
  - Manter testes de contrato de API e domínio obrigatórios em futuras sprints.  
  - Evitar mudanças destrutivas sem fase de transição.  
- **Janela de tratamento sugerida**: Contínua, com reforço de processos em **E27.2/E27.3**.  
- **Owner sugerido**: Tech Lead de E27 + Backend Owner do domínio de fontes.

---

##### R-28-T2 — Divergência entre invariantes de domínio e lógica da API

- **ID**: R-28-T2  
- **Categoria**: Técnico — Domínio / Backend  
- **Descrição**: As regras de negócio sobre fontes (especialmente transições de estado) devem ficar concentradas em invariantes de domínio, mas existe o risco de lógica paralela ser implementada diretamente na Admin API.  
- **Sintomas / Gatilhos**:  
  - Funções de mudança de estado replicadas em controladores de API.  
  - Invariantes atualizadas em um lugar e esquecidas em outro.  
- **Impacto**:  
  - Comportamento diferente entre operações via API e operações internas.  
  - Dificuldade em raciocinar sobre o estado real de uma fonte.  
- **Probabilidade**: Média (é um padrão comum em projetos que crescem rápido).  
- **Severidade**: P1 (afeta correção do sistema, não só performance).  
- **Mitigação planejada**:  
  - Centralizar transições de estado em métodos de domínio ou serviços dedicados.  
  - Proibir, por convenção, updates diretos em `state` na API sem passar por essas funções.  
  - Manter testes que operam sempre pela API, validando invariantes.  
- **Janela de tratamento sugerida**:  
  - Iniciar reforço já em **E27.2**, com refactors se necessário.  
- **Owner sugerido**: Backend Owner (Domínio) + QA/ORR Owner.

---

##### R-28-T3 — Migrações futuras pesadas em tabela de fontes

- **ID**: R-28-T3  
- **Categoria**: Técnico — Domínio / Backend  
- **Descrição**: Com o crescimento do número de fontes, migrations que alteram estrutura da tabela (`Source`) podem se tornar pesadas e arriscadas se não forem pensadas com cuidado.  
- **Sintomas / Gatilhos**:  
  - Migrações lentas em ambientes com muitas fontes.  
  - Lock prolongado ou impacto em janelas críticas de operação.  
- **Impacto**:  
  - Potenciais indisponibilidades em produção.  
  - Necessidade de planos de migração complexos em sprints futuras.  
- **Probabilidade**: Média (depende de volume e disciplina de schema).  
- **Severidade**: P2 (importante, mas previsível e planejável).  
- **Mitigação planejada**:  
  - Minimizar alterações de schema em campos críticos.  
  - Planejar migrações em etapas quando necessário (ex.: backfill assíncrono).  
  - Utilizar ambientes de staging com volume representativo para testar migrações.  
- **Janela de tratamento sugerida**:  
  - Diretriz contínua, com reforço em **E27.2** ao definir padrões de migrations para fontes.  
- **Owner sugerido**: Stonebraker/Truth-DB Architect + Backend Owner de fontes.

---

#### 5.2.4 Riscos Técnicos — Ingestão 2.0 (ON/OFF × Scheduler)

##### R-28-I1 — Lógica de elegibilidade duplicada ou ignorada

- **ID**: R-28-I1  
- **Categoria**: Técnico — Ingestão 2.0  
- **Descrição**: Embora S28 defina uma função clara de seleção de fontes automáticas (ex.: `get_auto_eligible_sources`), existe o risco de outras partes do código criarem lógicas paralelas ou ignorarem `mode`/`state`.  
- **Sintomas / Gatilhos**:  
  - Novos módulos de ingestão ou scripts geram `IngestionRun` sem usar a função centralizada.  
  - Diferenças de comportamento entre ambientes e caminhos de ingestão.  
- **Impacto**:  
  - Potencial ingestão de fontes `DISABLED`, violando a promessa central de S28.  
  - Dificuldade em auditar "quem decidiu ingerir o quê".  
- **Probabilidade**: Média (cresce com o número de pontos de integração com ingestão).  
- **Severidade**: P0/P1 (dependendo da gravidade da fonte envolvida).  
- **Mitigação planejada**:  
  - Declarar a função/serviço de elegibilidade como **fonte única de verdade**.  
  - Adicionar testes de regressão sempre que novos fluxos de ingestão forem criados.  
  - Monitorar logs para detectar ingestão de fontes desativadas.  
- **Janela de tratamento sugerida**:  
  - Reforçado em **E27.2** e **E27.3**, com vigilância contínua.  
- **Owner sugerido**: Backend Owner (Ingestão) + Squad de Observabilidade.

---

##### R-28-I2 — Corridas entre mudança rápida de estado e ciclos de ingestão

- **ID**: R-28-I2  
- **Categoria**: Técnico — Ingestão 2.0  
- **Descrição**: Se um operador alterna `ACTIVE` ↔ `DISABLED` em janela de tempo pequena, um ciclo de scheduler pode pegar o estado "antigo" e criar runs que parecem contradizer o estado final desejado.  
- **Sintomas / Gatilhos**:  
  - Operações de ON/OFF feitas em sequência rápida.  
  - Ingestões ocorrendo logo após desativar uma fonte.  
- **Impacto**:  
  - Confusão na operação ("achei que tinha desligado essa fonte").  
  - Dúvida sobre confiabilidade do ON/OFF, mesmo que o sistema esteja agindo segundo o tempo real dos eventos.  
- **Probabilidade**: Média (depende de uso, mas é um padrão típico de sistemas de agendamento).  
- **Severidade**: P2 (problema de percepção e janela, não de lógica estrutural).  
- **Mitigação planejada**:  
  - Estudar debouncing ou regras mínimas de intervalo entre mudanças de estado.  
  - Tornar visível na UI o timestamp da última mudança de estado e do último ciclo de ingestão.  
- **Janela de tratamento sugerida**:  
  - Avaliar e, se necessário, endereçar em **E27.3**, após observar uso real.  
- **Owner sugerido**: Product Owner + Backend Owner de ingestão.

---

##### R-28-I3 — Observabilidade de ingestão orientada a fonte ainda limitada

- **ID**: R-28-I3  
- **Categoria**: Técnico — Ingestão 2.0 / Observabilidade  
- **Descrição**: As métricas e painéis herdados de S22 não foram ainda refinados especificamente para acompanhar ingestão por fonte/estado/mode.  
- **Sintomas / Gatilhos**:  
  - Dificuldade em identificar rapidamente quais fontes mais falham.  
  - Falta de indicadores visuais claros sobre impacto de desativar/reativar fontes.  
- **Impacto**:  
  - Operação reativa, baseada em logs ad-hoc, e não em painéis claros.  
- **Probabilidade**: Alta (é o estado inicial padrão após S28).  
- **Severidade**: P2 (não quebra o sistema, mas reduz inteligência operacional).  
- **Mitigação planejada**:  
  - Incluir métricas por fonte/estado em E27.2.  
  - Montar painéis dedicados em E27.3.  
- **Janela de tratamento sugerida**:  
  - **E27.2** (métricas), **E27.3** (painéis e alertas).  
- **Owner sugerido**: Squad de Observabilidade + Backend Owner de ingestão.

---

#### 5.2.5 Riscos Operacionais

##### R-28-O1 — Operadores usando caminhos alternativos fora da Admin API

- **ID**: R-28-O1  
- **Categoria**: Operacional  
- **Descrição**: Mesmo com Admin API e console, ainda há o risco de times usarem scripts diretos de banco ou ferramentas paralelas para alterar fontes.  
- **Sintomas / Gatilhos**:  
  - Acesso privilegiado ao banco sendo usado para "ajustes rápidos".  
  - Divergência entre o que o console mostra e o que está na base.  
- **Impacto**:  
  - Invariantes quebradas silenciosamente.  
  - Dificuldade em auditar e reproduzir incidentes.  
- **Probabilidade**: Média (depende de disciplina operacional e de cultura).  
- **Severidade**: P1 (pode corroer a confiabilidade do sistema).  
- **Mitigação planejada**:  
  - Formalizar política: em produção, `Source` só pode ser alterada via Admin API/console.  
  - Monitorar acessos diretos ao banco.  
  - Futuramente, cruzar trilha de auditoria com logs de banco.  
- **Janela de tratamento sugerida**:  
  - Começa já no pós-S28 (comunicação/processo) e ganha reforços em **E27.2** (auditoria).  
- **Owner sugerido**: Time de Operações / SRE + Tech Lead de E27.

---

##### R-28-O2 — Falta de capacitação sobre `mode`, `state`, `criticality`

- **ID**: R-28-O2  
- **Categoria**: Operacional  
- **Descrição**: Operadores precisam entender conceitos de `mode` (AUTO/MANUAL), `state` (ACTIVE/DISABLED/DEPRECATED) e `criticality` para tomar decisões corretas no console.  
- **Sintomas / Gatilhos**:  
  - Fonte crítica desativada sem consciência do impacto.  
  - Uso incorreto de `DEPRECATED` versus `DISABLED`.  
- **Impacto**:  
  - Incidentes evitáveis, perda de dados ou atrasos de ingestão.  
- **Probabilidade**: Média/Alta (conceitos novos sempre exigem aprendizado).  
- **Severidade**: P1 (impacto real na operação se mal usados).  
- **Mitigação planejada**:  
  - Criar material de treinamento leve (guia de operações de fontes) pós-S28.  
  - Usar a própria demo de G6 como base para formação.  
  - Reforçar conceitos em futuras melhorias de UX (tooltips, ajuda contextual).  
- **Janela de tratamento sugerida**:  
  - Imediato pós-S28 e contínuo em E27.2/E27.3.  
- **Owner sugerido**: Product Owner + Time de Operações.

---

##### R-28-O3 — Decisões críticas de fonte sem política formal de aprovação

- **ID**: R-28-O3  
- **Categoria**: Operacional / Governança  
- **Descrição**: Por enquanto, qualquer operador com acesso ao console pode, em tese, desativar ou deprecar uma fonte crítica sem um fluxo formal de aprovação.  
- **Sintomas / Gatilhos**:  
  - Mudanças em fontes de alta criticidade feitas por uma única pessoa, sem segunda revisão.  
- **Impacto**:  
  - Risco elevado de incidentes em pipelines dependentes de fontes críticas.  
- **Probabilidade**: Baixa/Média (depende de cultura e número de operadores).  
- **Severidade**: P1 (afeta pipelines críticos).  
- **Mitigação planejada**:  
  - Em curto prazo, política organizacional (procedimentos internos).  
  - Em médio prazo (E27.3+), estudar fluxos de aprovação (ex.: "duas chaves" para fontes com `criticality = HIGH`).  
- **Janela de tratamento sugerida**:  
  - Política provisória no pós-S28, solução sistêmica em **E27.3+**.  
- **Owner sugerido**: Governança/Conselho de Produto + Tech Lead.

---

Com este Bloco 2, o Capítulo 5 da Sprint 28 transforma o "mapa geral" de riscos em uma lista estruturada, com IDs, categorias, impacto e mitigação clara. Os próximos blocos aprofundam a **dívida técnica assumida** e o **backlog de continuidade** (E27.2, E27.3 e além), sempre ancorando os itens nos riscos mapeados aqui.

