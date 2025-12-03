# Inspectah — Sprint 28
## Capítulo 5 — Bloco 4
### Backlog de Continuidade (E27.2, E27.3 e além) + Monitoração Pós-Sprint & Sumário Executivo

---

#### 5.4.1 Objetivo deste bloco

Este bloco fecha o Capítulo 5 conectando diretamente:
- os **riscos** (Bloco 2),
- a **dívida técnica** (Bloco 3)

a um **backlog de continuidade organizado por horizonte** (E27.2, E27.3 e longo prazo), além de definir:
- rotinas de **monitoração e sanity pós-sprint**, e
- um **sumário executivo** para o Conselho/ORR sobre o legado da Sprint 28 dentro de E27.

Aqui o foco é responder: "Dado tudo o que sabemos depois de S28, o que vem na sequência e como garantimos que essa entrega continue saudável e útil no tempo?".

---

### 5.4 Backlog de Continuidade — E27.2, E27.3 e além

O backlog abaixo não é uma fila rígida, mas um **cardápio priorizado** de itens que nascem diretamente da Sprint 28 e dos riscos/dívidas mapeados.

Para cada item, indicamos:
- **ID de referência** (ligado à dívida ou risco correspondente),
- **Descrição curta**, 
- **Benefício principal**,
- **Riscos/dívidas associados**,
- **Sprint-alvo sugerida** (E27.2, E27.3, longo prazo).

---

#### 5.4.1 Itens candidatos para E27.2 (Sprint 29)

##### B-27.2-1 — Implementar `SourceActionLog` (auditoria básica)

- **Ref.**: D-28-AUD-1, R-28-P2, R-28-O1, R-28-O3.  
- **Descrição**: Modelar e implementar a entidade `SourceActionLog` e o pipeline mínimo de gravação de ações de operador em fontes.  
- **Benefício**: Cria fundação de auditoria para operações em fonte, permitindo reconstruir incidentes e apoiar governança futura.  
- **Escopo mínimo**:  
  - Modelo + migration de `SourceActionLog`.  
  - Gravação automática em pontos centrais da Admin API (CREATE/UPDATE/ACTIVATE/DISABLE/DEPRECATE).  
  - Endpoint simples de leitura por `source_id` (sem UI ainda).  
- **Sprint-alvo sugerida**: **E27.2**.

---

##### B-27.2-2 — Validações por tipo de fonte (fase 1 — tipos principais)

- **Ref.**: D-28-VAL-1, R-28-P3, R-28-I3.  
- **Descrição**: Introduzir validações específicas para os tipos de fonte mais importantes (ex.: RSS de notícias, APIs JSON críticas).  
- **Benefício**: Evita que configurações obviamente inválidas cheguem até a ingestão, reduzindo ruído em logs e frustração do operador.  
- **Escopo mínimo**:  
  - Interface de "validador por tipo" no backend.  
  - Implementação para 1–2 tipos críticos.  
  - Erros de validação integrados ao contrato da Admin API e, via DTOs, ao console.  
- **Sprint-alvo sugerida**: **E27.2**.

---

##### B-27.2-3 — Métricas básicas de ingestão por fonte

- **Ref.**: D-28-OBS-1, R-28-I3.  
- **Descrição**: Instrumentar ingestão 2.0 com métricas por `source_id`/estado/mode (em nível controlado de cardinalidade).  
- **Benefício**: Fornece base factual para diagnosticar problemas de ingestão e priorizar correções em fontes mais problemáticas.  
- **Escopo mínimo**:  
  - Métricas como: ingestões bem-sucedidas por fonte, falhas por fonte, tempo desde última ingestão sucedida, etc.  
  - Export em formato compatível com stack de observabilidade atual (ex.: Prometheus).  
- **Sprint-alvo sugerida**: **E27.2**.

---

##### B-27.2-4 — Filtros avançados no console de fontes

- **Ref.**: R-28-P1, R-28-O2.  
- **Descrição**: Evoluir tela de lista de fontes com filtros combinados por estado, modo, domínio, criticidade, tipo.  
- **Benefício**: Reduz o atrito do operador em ambientes com muitas fontes e diminui risco de erro humano por seleção equivocada.  
- **Escopo mínimo**:  
  - UI de filtros com múltiplos critérios.  
  - Persistência de filtros no URL (para compartilhamento entre operadores).  
- **Sprint-alvo sugerida**: **E27.2**.

---

#### 5.4.2 Itens candidatos para E27.3 (Sprint 30)

##### B-27.3-1 — Timeline de ações por fonte no console

- **Ref.**: D-28-AUD-2, D-28-AUD-1, R-28-P2, R-28-O3.  
- **Descrição**: Construir uma UI de **linha do tempo de ações** por fonte, consumindo `SourceActionLog`.  
- **Benefício**: Permite compreensão imediata de "quem fez o quê" numa fonte, ajudando em incidentes e revisões de governança.  
- **Escopo mínimo**:  
  - Página ou aba "Histórico" em `SourceDetail`.  
  - Filtros por tipo de ação e intervalo de tempo.  
- **Sprint-alvo sugerida**: **E27.3**.

---

##### B-27.3-2 — Wizards de configuração para fontes complexas

- **Ref.**: D-28-VAL-2, D-28-VAL-1, R-28-P3.  
- **Descrição**: Implementar wizards passo-a-passo para criar fontes de tipos mais complexos (por exemplo, API JSON com autenticação).  
- **Benefício**: Reduz erros de configuração e baixa a barreira de entrada para novos operadores.  
- **Escopo mínimo**:  
  - Wizard para pelo menos um tipo de fonte de alto impacto.  
  - Testes de conexão integrados ao fluxo do wizard.  
- **Sprint-alvo sugerida**: **E27.3**.

---

##### B-27.3-3 — Dashboards dedicados de operação de fontes

- **Ref.**: D-28-OBS-2, D-28-OBS-1, R-28-I3, R-28-O2.  
- **Descrição**: Criar painéis (no cockpit admin ou ferramenta de observabilidade) focados em operação de fontes: estados, modos, falhas, envelhecimento.  
- **Benefício**: Dá aos times de operação e produto visão de alto nível sobre saúde do ecossistema de fontes.  
- **Escopo mínimo**:  
  - Painel com: 
    - # de fontes por estado/mode/criticidade,  
    - top N fontes com maior taxa de erro,  
    - fontes desativadas ou deprecadas há muito tempo.  
- **Sprint-alvo sugerida**: **E27.3**.

---

##### B-27.3-4 — Política sistêmica de ações em fontes críticas

- **Ref.**: D-28-GOV-1, R-28-O3.  
- **Descrição**: Introduzir mecanismos sistêmicos (em código) para ações em fontes de alta criticidade, como "duas chaves" ou papéis de aprovação.  
- **Benefício**: Reduz risco de incidentes graves gerados por uma única decisão isolada.  
- **Escopo mínimo**:  
  - Política inicial simples (ex.: apenas usuários com papel X podem desativar fontes com `criticality = HIGH`).  
  - Log estruturado dessas decisões via `SourceActionLog`.  
- **Sprint-alvo sugerida**: **E27.3**.

---

#### 5.4.3 Itens de backlog de longo prazo (além de E27.3)

##### B-LONG-1 — Políticas automáticas de ON/OFF com base em comportamento

- **Ref.**: R-28-I1, R-28-I3, R-28-O2.  
- **Descrição**: Criar regras que possam sugerir ou executar automaticamente ON/OFF em fontes com padrões extremos (ex.: altíssima taxa de falhas, latências absurdas, comportamento suspeito).  
- **Benefício**: Move o sistema de um modelo reativo para um modelo proativo de gestão de fontes.  
- **Notas**:  
  - Requer maturidade em métricas e governança (não é alvo imediato de E27.2/27.3).  

---

##### B-LONG-2 — Integração profunda com Debunker & Comitês de Verdade

- **Ref.**: Riscos de Programa 2 (Verdade & Interpretação), conexões gerais com Sistema de Blocos.  
- **Descrição**: Conectar fontes com reputação/score de confiabilidade calculados por agentes Debunker e comitês, influenciando operação (sugerindo desativação, priorizando auditoria, etc.).  
- **Benefício**: Faz a ponte entre "fonte como entidade técnica" e "fonte como participante de um ecossistema de verdade/fato".  
- **Notas**:  
  - Exige maturidade da camada de Verdade & Interpretação (S23–S25+) e do Sistema de Blocos.

---

##### B-LONG-3 — Mapeamento entre fontes e temas/casos do Inspectah

- **Ref.**: Estratégia geral do Inspectah como Data Hub de Casos/Temas.  
- **Descrição**: Evoluir modelo de dados para mapear fontes aos temas/casos que alimentam (ex.: "todas as fontes que alimentam o caso X").  
- **Benefício**: Permite operação por contexto (desligar fontes irrelevantes para um tema, entender impacto de fontes em casos específicos).  
- **Notas**:  
  - Depende de maturidade da modelagem de casos/temas em sprints de produto futuras.

---

### 5.5 Medidas de Monitoração e Sanity Pós-Sprint

Mesmo com S28 em GO, a saúde da entrega depende de **rotinas regulares**. Abaixo, uma proposta de baseline.

---

#### 5.5.1 Rotinas semanais sugeridas

1. **Sanity automatizado de ingestão & fontes**  
   - Rodar um subconjunto de scripts inspirados em G4 e S22 (por exemplo, uma versão de teste rápido de ON/OFF × ingestão em staging).  
   - Verificar se nenhuma fonte `DISABLED` gerou ingestões na última semana.

2. **Revisão rápida de métricas (assim que existirem em E27.2)**  
   - Top N fontes com maior taxa de erro.  
   - Fontes críticas com qualquer anomalia (falhas, latências extremas).

3. **Revisão de mudanças recentes em fontes críticas**  
   - Com base em `SourceActionLog` (assim que existir): olhar quem mexeu em fontes de alta criticidade na última semana e se houve impacto visível.

---

#### 5.5.2 Rotinas mensais sugeridas

1. **Revisão de fontes desativadas e deprecadas**  
   - Fontes em `DISABLED` há muito tempo: decidir se devem ser reativadas, ajustadas ou movidas para `DEPRECATED`.  
   - Fontes `DEPRECATED`: considerar limpeza, arquivamento ou outras políticas de ciclo de vida.

2. **Revisão de treinamento e processos de operação**  
   - Validar se operadores novos entenderam bem `mode`, `state`, `criticality`.  
   - Atualizar guias de operação com base em problemas reais observados.

3. **Auditoria amostral de decisões em fontes críticas**  
   - Escolher algumas fontes críticas e revisar decisões recentes (desativar/reativar), cruzando logs de auditoria, ingestão e impacto em pipelines.

---

#### 5.5.3 Watchers e alertas recomendados

Mesmo com métricas e dashboards ainda em evolução, já é possível desenhar alguns watchers conceituais para orientar implementação futura:

- **Watcher W-FO-1 — Fonte crítica com N falhas consecutivas de ingestão**  
  - Ação: disparar alerta para time de operação/produto.  
  - Conecta-se a `criticality` + métricas de erro.

- **Watcher W-FO-2 — Fonte desativada sem `state_reason` adequado**  
  - Ação: alertar para revisão da decisão, pois isso prejudica rastreabilidade.  

- **Watcher W-FO-3 — Fonte `ACTIVE` sem ingestões bem-sucedidas há muito tempo**  
  - Ação: sugerir revisão de configuração ou downgrade de criticidade.

- **Watcher W-FO-4 — Volume anormal de mudanças em fontes em janela curta**  
  - Ação: investigar se há mudança de política, incidente em curso ou uso indevido do console.

Esses watchers podem nascer como queries manuais e, depois, ser automatizados quando a camada de métricas estiver estável.

---

### 5.6 Sumário Executivo — Sprint 28 no contexto do Épico E27

Para o Conselho/ORR e stakeholders de alto nível, a Sprint 28 pode ser resumida em quatro pontos-chave:

1. **Entrega central**  
   - S28 consolidou a fonte (`Source`) como entidade operacional de primeira classe: modelo, Admin API, console v2 e ingestão obedecendo ON/OFF.  
   - Gates G0–G7 formalizam essa entrega com evidências e scorecards.

2. **Posicionamento dentro de E27**  
   - S28 é o "núcleo duro" de E27.1: estabelece o mínimo inegociável para operar fontes com disciplina.  
   - Os próximos passos (E27.2, E27.3) aprofundam auditoria, validações, observabilidade e governança.

3. **Riscos e dívidas são conhecidos e amarrados a plano**  
   - Riscos remanescentes e dívidas técnicas não estão "espalhados na cabeça das pessoas"; estão listados e amarrados a itens de backlog com janelas-alvo claras.  
   - Isso reduz risco de "esquecer" pontos críticos e permite priorização consciente em sprints futuras.

4. **Critério de sucesso pós-GO**  
   - Operadores usam o console de fontes como interface padrão para CRUD & ON/OFF (sem atalhos diretos no banco).  
   - Nenhuma ingestão automática de fonte `DISABLED` é observada em ambientes oficiais.  
   - Feedback da operação indica que a ferramenta reduz fricção, não adiciona.  
   - E27.2/E27.3 são planejadas explicitamente usando o backlog deste capítulo.

---

Com este Bloco 4, o Capítulo 5 da Sprint 28 se fecha: riscos e dívidas se transformam em backlog estruturado, rotinas de monitoração e um quadro executivo claro do que S28 representa dentro do Épico E27 e do Programa 1 como um todo.