# Inspectah — Sprint 27 (S27)
## Capítulo 6 — Bloco 4
### Impacto no Roadmap, Conexão com Riscos/Ações & Recomendações Finais

> Arquivo-alvo sugerido no repo: `docs/s27_cap_6_4_impacto_roadmap_e_recomendacoes.md`
>
> Função: amarrar **o que a S27 decidiu e aprendeu** com o plano concreto de próximos passos — conectando riscos (RISK-XXX), ações (ACT-XXX), dívidas (DEBT-XXX) e o roadmap de curto, médio e longo prazo. Este é o bloco que transforma a S27 de "história passada" em combustível para o futuro.

---

## 1. Ponto de partida: o veredito da S27 e do Épico E26

> Esta seção deve ser preenchida com base no `S27_G6_orr_summary.json` final.

- **Veredito da Sprint 27 (`verdict_sprint`)**: `GO` | `GO_WITH_RISKS` | `NO_GO`.  
- **Veredito do Épico E26 (`verdict_epic`)**: `GO` | `GO_WITH_RISKS` | `NO_GO`.  
- **Principais justificativas** (em 3–6 bullets):  
  - pontos de força que sustentaram o veredito;  
  - riscos aceitos conscientemente;  
  - limitações explicitadas.

Essa fotografia é o anchor: tudo o que vem a seguir (ajustes de roadmap, próximas sprints, novos épicos) deve ser justificável a partir dela.

---

## 2. Tabela de ligação entre Riscos, Dívidas e Ações

Para evitar que `RISK-XXX`, `DEBT-XXX` e `ACT-XXX` virem três universos paralelos, este bloco recomenda uma pequena tabela de ligação.

### 2.1 Estrutura sugerida

> Pode ser mantida aqui em markdown e/ou refletida em um CSV/planilha, desde que a relação seja clara.

Campos mínimos por linha:

- **Risco**: `RISK-XXX` (ou `-` se não houver risco direto).  
- **Dívida associada**: `DEBT-XXX` (ou `-`).  
- **Ação prevista**: `ACT-XXX`.  
- **Tipo de dívida**: `tecnica` | `produto` | `ux` | `operacao` | `processo`.  
- **Due sprint**: sugestão (ex.: `S2X`, `S2Y`).  
- **Status esperado**: `planejada` | `em_andamento` | `concluida` | `nao_iniciada`.  
- **Notas**: contexto rápido.

Exemplo:

| Risco      | Dívida      | Ação     | Tipo     | Due sprint | Status esperado | Notas |
|-----------|-------------|----------|----------|-----------|-----------------|-------|
| RISK-001  | DEBT-001    | ACT-001  | tecnica  | S2X       | planejada       | Cobertura E2E avançada de Debunker |
| RISK-002  | DEBT-002    | ACT-002  | ux       | S2Y       | planejada       | Criar visão consolidada de saúde de Programa 1 |
| (nenhum)  | DEBT-003    | ACT-003  | operacao | S2X       | planejada       | Complementar runbooks para falhas parciais de ingestão |

O importante não é a tabela ser perfeita, mas deixar claro **quem vai atacar o quê, quando e por quê**.

---

## 3. Impacto no roadmap de curto prazo (próximas 1–3 sprints)

> Aqui entram decisões concretas para as sprints imediatamente seguintes.

### 3.1 Temas que se tornam prioridade

Liste de 3 a 7 temas que, à luz da S27, **não podem ser empurrados**:

- **Tema 1 — Fortalecer Debunker E2E & Observabilidade**  
  - Motivação: dívidas técnicas e operacionais associadas a `DEBT-001`, `RISK-001`.  
  - Possível contêiner: nova sprint ou épico "Debunker E2E & Observability".

- **Tema 2 — Visões de saúde de Programa 1 em Admin v1**  
  - Motivação: necessidade de síntese operacional (DEBT-002, learnings de operação).  
  - Possível contêiner: sprint de "Admin v1.2 — painéis de saúde".

- **Tema 3 — Runbooks e playbooks para incidentes parciais**  
  - Motivação: lacunas de operação (DEBT-003).  
  - Possível contêiner: sprint de "Operação Programa 1 v2".

Para cada tema, conectar explicitamente a:

- riscos (RISK-XXX),  
- dívidas (DEBT-XXX),  
- ações (ACT-XXX),  
- e ao impacto direto em Programa 1.

### 3.2 Temas que podem ser empurrados sem grande prejuízo

Não menos importante é explicitar **o que pode esperar**:

- melhorias cosméticas de UI sem impacto direto em operação;  
- refinos de layout que não resolvem dívidas estruturais;  
- experimentos de baixo impacto que podem ser encaixados opportunisticamente.

Registrar isso evita que sprints curtas se percam em polimento enquanto riscos reais seguem abertos.

---

## 4. Impacto no roadmap de médio prazo (épicos seguintes)

### 4.1 Admin v1 além de Programa 1

A S27 fornece insumos para decidir **como e quando** replicar Admin v1 para outros programas:

- Quais aspectos do Admin v1 estão maduros o suficiente para serem template?  
- Quais ainda são específicos de Programa 1 e precisam ser generalizados?  
- Vale a pena abrir um épico como "Admin v1.2 para Programa 2"? Em que momento?

Sugestão de estrutura:

- **O que já parece estável** (shell, padrões de navegação, alguns componentes).  
- **O que é frágil e não deveria ser replicado ainda** (padrões de timeline, visualização de relações complexas, etc.).  
- **Pré-requisitos para escalar Admin v1** (por exemplo, fechar determinadas dívidas técnicas/UX antes de aplicar a outros domínios).

### 4.2 Próximos grandes épicos originados pela S27

A partir de G6, Cap.5 e Cap.6, liste possíveis épicos emergentes, com 1–2 parágrafos cada:

- **Épico A — Debunker E2E & Observability**  
  - Nasce de: DEBT-001, learnings de E2E, riscos de credibilidade.  
  - Objetivo: transformar o Debunker de "casos funcionais" em sistema observável de ponta a ponta.

- **Épico B — Admin v1.2 — Painéis & Insights Operacionais**  
  - Nasce de: DEBT-002, learnings de operação e UX.  
  - Objetivo: oferecer visões sintéticas para operadores, reduzindo tempo de diagnóstico.

- **Épico C — Operação Programa 1 v2 (Runbooks & Playbooks)**  
  - Nasce de: DEBT-003 e outras dívidas de operação.  
  - Objetivo: elevar Programa 1 de "operável" para "operável com confiança".

A lista final depende dos detalhes da S27, mas o formato ajuda a dar nomes e contêineres claros às necessidades que emergiram.

---

## 5. Impacto na visão de longo prazo do Inspectah

> Esta seção é propositalmente mais conceitual, mas não menos importante.

### 5.1 O que a S27 prova ou invalida na visão de produto

Perguntas a responder aqui:

- A aposta em um **Admin v1 unificado** continua fazendo sentido, à luz da experiência em Programa 1?  
- A forma como o Inspectah pretende operar Programas (Fontes, Ingestão, Debunker, etc.) se mostrou realista?  
- O que a S27 revelou sobre a maneira como o sistema de verdade precisa ser exposto e operado via interface admin?

### 5.2 Riscos estruturais reduzidos

Registrar quais riscos de longo prazo a S27 ajudou a reduzir, por exemplo:

- risco de fragmentação de consoles;  
- risco de ter UIs não-operacionais para Programas;  
- risco de não conseguir auditar decisões de Debunker minimamente pela UI.

### 5.3 Riscos estruturais que permanecem ou surgiram

Da mesma forma, registrar riscos que continuam relevantes apesar da S27, tais como:

- complexidade de escalar Debunker para múltiplos Programas;  
- desafios de observabilidade e rastreabilidade ponta a ponta;  
- necessidade de alinhar cada vez mais UI admin com Truth-DB e System of Blocks (quando essas camadas forem avançando).

Esses riscos não precisam virar ações imediatas, mas devem entrar no radar estratégico.

---

## 6. Recomendações explícitas “se eu fosse a próxima sprint”

> Esta seção é mais opinativa, mas deve se apoiar em learnings, dívidas e riscos já descritos.

Sugestão de formato:

### 6.1 Se eu fosse a próxima sprint focada em Debunker

- Priorizar **cenários E2E reais** que envolvam múltiplas evidências, revisões e interações com Fontes/Ingestão.  
- Implementar **instrumentação mínima** (logs, métricas, traces) específica do fluxo de casos.  
- Refinar UX para representar melhor a linha do tempo das decisões.

### 6.2 Se eu fosse a próxima sprint focada em Admin v1 (Programa 2 ou v1.2)

- Reaproveitar ao máximo o shell e componentes estáveis, evitando reinventar layouts.  
- Tratar dívidas de UX/dashboards de Programa 1 como requisitos para o próximo Programa, não como "nice to have".  
- Garantir que novos consoles já nasçam com **visões de saúde** e não só com listas.

### 6.3 Se eu fosse a próxima sprint focada em Operação & ORR

- Formalizar um **ritual leve** para manter G6 vivo ao longo da sprint (registrando riscos à medida que surgem).  
- Ajustar o Sprint Playbook para refletir learnings de waves W0–W3.  
- Automatizar partes dolorosas dos gates mais valiosos (especialmente G2 e G4).

Esse bloco de recomendações deve ser curto e direto, para realmente influenciar o planejamento das próximas sprints.

---

## 7. Como manter este bloco útil ao longo do tempo

- Atualizar links entre `RISK-XXX`, `DEBT-XXX` e `ACT-XXX` à medida que o backlog evoluir (sem reescrever a história).  
- Se novos épicos nascerem diretamente destas recomendações, referenciá-los aqui com IDs e nomes.  
- Em ORRs futuros, revisitar este Bloco 4 para checar o quanto as recomendações da S27 foram seguidas ou superadas.

Com isso, Cap.6 Bloco 4 fecha o arco da S27: dos fatos e evidências (Gates, ORR, bundle) até as decisões concretas de futuro — sem deixar nada importante perdido nas entrelinhas.

