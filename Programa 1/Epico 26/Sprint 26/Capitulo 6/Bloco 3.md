# Inspectah — Sprint 26 (S26)
## Capítulo 6 — Bloco 6.3
### Impacto da S26 no Roadmap (S26–S65)

> Arquivo-alvo no repo: `docs/s26_cap_6_3_impacto_no_roadmap.md`
>
> Função: explicitar **como a S26 altera o plano S26–S65** descrito em `Roadmap.md` e nos docs de estado do produto pós-S25, conectando:
> - o que foi realmente entregue em S26 (Cap.1–5),
> - as lições e dívidas (Blocos 6.1 e 6.2),
> - e os próximos passos dos programas e épicos afetados.
>
> Regra: nenhum ajuste de roadmap fica implícito. Se S26 mudou algo relevante, isso aparece aqui.

---

## 1. Ponto de partida: o plano pré-S26

Antes da S26, o plano macro indicava, em linhas gerais:

- **Programa 1 — Admin & Fontes**  
  - Consolidar um console admin consistente, mas ainda sem um Design System Admin v1 bem formalizado.  
  - Evoluir o Console de Fontes gradualmente, ainda com heranças de layouts antigos e acoplamentos.

- **Programas de Ingestão & Verdade**  
  - Avançar na Ingestão 2.0 (por fonte, com mais tipos) em sprints dedicadas.  
  - Empurrar Debunker, Truth-DB e camadas de interpretação/contestação (S23–S25) em paralelo com evolução de consoles, mas com pouca integração operacional com fontes.

- **Qualidade, Gates e Operação**  
  - Manter o modelo de gates e ORR evoluindo, mas ainda com variação de qualidade entre sprints.  
  - Runbooks mais focados em partes específicas do sistema, sem um runbook forte para fontes.

A S26 encaixa nessa linha temporal como a sprint que:
- consolida **Admin v1** como base real,  
- estabelece o **Console de Fontes v2** como cliente de referência,  
- e acopla isso a um modelo mais maduro de gates, ORR e runbooks.

---

## 2. O que S26 adiantou no roadmap

### 2.1 Admin Inspectah v1 deixou de ser futuro e virou infraestrutura presente

**Impacto**  
A S26 antecipa a maturidade do **Design System Inspectah Admin v1**: em vez de ser apenas um capítulo de design ou uma sprint futura isolada, ele passa a existir como código e ser usado por um console real (fontes).

**Consequências de roadmap**

- Programas e épicos que dependem de **consoles admin coerentes** (cockpit, Explore, gestão de casos, painéis de Truth-DB, etc.) podem ser planejados assumindo a existência de `ui/admin` como base.  
- Sprints que, originalmente, incluiriam "criar estrutura de admin" podem reduzir ou eliminar essa parte, focando mais no domínio em si.

### 2.2 Operação de fontes passou de "feature" a "capacidade" do sistema

**Impacto**  
Com o Console de Fontes v2 + runbook de operação v1, a gestão de fontes deixa de ser um conjunto de telas e scripts e se torna uma **capacidade operacional** do Inspectah.

**Consequências de roadmap**

- É possível planejar sprints de **Ingestão 2.0** assumindo que operadores conseguem cadastrar, ativar, corrigir e arquivar fontes por conta própria.  
- Programas de Verdade & Interpretação (S23–S25) podem supor uma camada de fontes mais organizada, com contratos e fluxos estáveis.

### 2.3 ORR, runbooks e risco ganharam um modelo replicável

**Impacto**  
O Cap.5 da S26 materializa um **modelo de ORR, runbooks e gerenciamento de risco** aplicável a outros domínios além de fontes.

**Consequências de roadmap**

- Sprints críticas (Debunker, Truth-DB, Evidence Vault, Ingestão 2.0) podem reutilizar o mesmo formato de Cap.5:  
  - cenários E2E,  
  - plano de ORR,  
  - runbooks,  
  - riscos + flags + rollback.  
- O esforço de "inventar o ORR" a cada sprint diminui; o foco passa a ser calibrar conteúdo, não refazer estrutura.

---

## 3. O que S26 empurrou ou explicitou como dependência futura

### 3.1 Monitoração & observabilidade de fontes ainda não resolvidas

**Situação**  
A S26 reconhece R5 (falta de monitoração robusta para fontes) e posiciona isso como algo a ser tratado em outras sprints.

**Ajuste de roadmap**

- Sprints de **Observabilidade / Ingestão 2.0** devem incluir explicitamente:  
  - métricas e alertas específicos para fontes;  
  - correlação entre incidentes I1–I4 e sinais de ingestão.  
- Programas de Truth-DB / Evidence Vault devem considerar a trilha de **evidências de operação de fontes** (logs, histórico de alterações) como parte do escopo futuro.

### 3.2 Dívidas fortes de contrato e auditabilidade

**Situação**  
A S26 expõe dívidas técnicas relevantes:
- `S26-DT-004` (contrato de `Source` sem fonte única de verdade);  
- `S26-DT-005` (log/audit de mudanças em fontes ainda básico).

**Ajuste de roadmap**

- Epics e sprints focados em **modelo de domínio de fontes** e em **auditoria/trace** devem ser puxados um pouco mais cedo ou ganhar peso extra.  
- Sprints de Truth-DB/blocks precisam levar em conta desde já que "fonte" é um ator crítico no grafo de verdade: sem audit trail decente aqui, contestar verdades sobre dados ingeridos fica mais frágil.

### 3.3 Qualidade de frontend (visual regressions, testes mais ricos) como trilha própria

**Situação**  
Dívidas como `S26-DT-002` (regressão visual) e `S26-DT-003` (testes de fluxo limitados) indicam a necessidade de uma trilha de **Quality Frontend** mais forte.

**Ajuste de roadmap**

- Em vez de pulverizar ajustes de quality UI em várias sprints, faz sentido concentrar parte disso em uma ou duas sprints/épicos específicos, alinhados com aumento de criticidade dos consoles.

---

## 4. Recomendações de ajustes concretos no Roadmap S26–S65

> Nota: os itens abaixo não reescrevem o roadmap, mas sugerem ajustes de ênfase e ordenação.

### 4.1 Programa 1 — Admin & Fontes

- **Consolidar Admin v1**  
  - Garantir que nas próximas sprints de Programa 1 qualquer novo console admin (ex.: ingestão, casos, Truth-DB) parta de `ui/admin`.  
  - Planejar pelo menos uma sprint de "Admin v1.1" para:  
    - ampliar cobertura de componentes (`S26-DT-001`),  
    - introduzir camada de regressão visual (`S26-DT-002`).

- **Evoluir Console de Fontes v2 de referência para hub de ingestão**  
  - Conectar explicitamente sprints de Ingestão 2.0 às capacidades do console (ex.: campos extras de configuração, visualização de saúde, etc.).  
  - Puxar dívidas de testes e docs (`S26-DT-003`, `S26-DT-008`, `S26-DT-009`) junto com novas features, para não crescer em cima de base frágil.

### 4.2 Programas de Ingestão 2.0 e Observabilidade

- **Monitoração de fontes como entregável explícito**  
  - Incluir, em epics de Ingestão 2.0 / Observabilidade, objetivos concretos de métricas e alertas por fonte (ligando com incidentes I1–I4).  
  - Prever gates específicos para esse domínio (ex.: "Gx_Fontes_Observabilidade") nas sprints correspondentes.

- **Integração com Evidence Vault / Truth-DB**  
  - Quando a trilha de Truth-DB estiver sendo atacada, garantir que eventos de operação de fontes (ativação, desativação, mudanças de config) possam virar evidência consultável.

### 4.3 Programas Verdade & Interpretação (S23–S25+)

- **Dependência explícita de fontes confiáveis**  
  - Atualizar docs de programas de Verdade & Interpretação para mencionar explicitamente que dependem do estado "pós-S26" de fontes:  
    - contratos minimamente estáveis,  
    - operação via console,  
    - runbooks e gestão de incidentes.  
  - Isso evita desenhar Debunker/committees como se a camada de fontes fosse mágica ou perfeita.

### 4.4 Trilha de Gates & ORR como produto interno

- **Reutilizar formato de Cap.5 em sprints futuras**  
  - Para sprints de grande impacto (Truth-DB, Debunker, Ingestão 2.0, Evidence Vault), reservar tempo explícito de Cap.5 para:  
    - cenários E2E,  
    - ORR,  
    - runbooks,  
    - riscos & flags.  
  - Tratar isso como "infra de método" e não como enfeite.

---

## 5. Como manter o roadmap alinhado ao que S26 ensinou

- Sempre que uma nova sprint for planejada entre S27 e S65, o Spec Office deve:
  - consultar o Bloco 6.1 (learnings) e o Bloco 6.2 (dívidas) para ver se há pontos que precisam ser incorporados;  
  - atualizar `Roadmap.md` quando ajustes de peso forem realizados (e linkar este Bloco 6.3 como justificativa).
- Revisões periódicas de programa (checkpoints de Programa 1, Ingestão, Verdade, etc.) devem incluir uma seção rápida:  
  - "O que S26 já resolveu pra nós?"  
  - "Quais dívidas de S26 ainda estão abertas?"  
  - "Isso muda a ordem ou o escopo das próximas sprints?".

---

## 6. Síntese do Bloco 6.3

O Bloco 6.3 garante que a S26 não seja tratada como evento isolado, e sim como um **pivô de roadmap**:

- Adianta a maturidade de Admin v1, do Console de Fontes v2 e do modelo de ORR/runbooks/risco.  
- Explicita dívidas e dependências que precisam ser atacadas em sprints futuras (contratos de fonte, audit trail, observabilidade, quality frontend).  
- Propõe ajustes claros em Programa 1, Ingestão 2.0, Verdade & Interpretação e trilha de Gates & ORR.

Com isso, qualquer leitura futura do `Roadmap.md` pode ser feita à luz da S26: não é só "mais uma sprint", é a sprint que transformou Admin & Fontes em infraestrutura estável sobre a qual o restante do Inspectah vai se apoiar.