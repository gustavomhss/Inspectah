# Inspectah — Sprint 27 (S27)
## Capítulo 1 — Contexto, Problema e Estados-alvo

> Arquivo-alvo no repo: `docs/s27_cap_1_contexto_e_objetivos.md`
>
> Função: alinhar o **contexto**, o **problema** e os **estados-alvo** da Sprint 27, segunda sprint do épico E26. Este capítulo é a âncora conceitual da S27: tudo que aparecer em Cap.2–6 precisa fazer sentido à luz deste texto.

---

## 1. Contexto pós-S26 e posição da S27 no E26

### 1.1 Linha do tempo relevante

- **S20–S25** construíram o arcabouço de UI, ingestão, interpretação, Debunker e governança de verdade/fato.  
- **S26** deu o salto de unificação de admin:
  - criou o **Design System Inspectah Admin v1** em `ui/admin`,
  - migrou o **Console de Fontes v2** como primeiro cliente real,
  - estabeleceu um modelo forte de **Cap.5 (ORR, operação, risco)** e **Cap.6 (learnings, dívidas, anti-gaps)**.

O épico **E26 — Design System & Consoles Admin v1** foi desenhado como:
- **S26** → preparar o terreno (Admin v1 + Fontes v2 + método de ORR/runbooks),
- **S27** → colocar o padrão Admin v1 para rodar **em todos os consoles admin críticos** do Programa 1 (Fontes, Ingestão, Debunker).

### 1.2 Estado atual que a S27 recebe

Ao iniciar a S27, assumimos como verdade:

1. Existe um **Design System Inspectah Admin v1** minimamente estável:
   - tokens, layout base (`AdminShell`, `AdminHeader`, `AdminSidebar`, `AdminContent`),
   - componentes estruturais e básicos (botões, tabelas, badges, inputs) em `ui/admin`.

2. O **Console de Fontes v2** já está migrado para Admin v1 e operável:
   - operadores conseguem cadastrar, ativar, editar e desativar/arquivar fontes;
   - existe um `runbook_operacao_fontes_v1.md` cobrindo fluxos principais e incidentes I1–I4.

3. O **modelo de método** foi elevado:
   - Cap.4 da S26 usa waves + tasks + evidências de forma madura;
   - Cap.5 tem cenários E2E, ORR estruturado, runbooks e riscos;
   - Cap.6 conecta learnings, dívidas e roadmap, com sistema de anti-gaps.

### 1.3 Por que a S27 é necessária

Mesmo com Admin v1 e Fontes v2, o estado atual ainda tem problemas claros:

- **Assimetria de UI entre os consoles**: Ingestão 2.0 e Debunker ainda usam layouts/paradigmas diferentes do admin v1. Operadores mudam de tela e parecem mudar de sistema.
- **Estados de UI inconsistentes**: vazios, loading, erros e alertas são representados de formas diferentes entre Fontes, Ingestão e Debunker, aumentando a carga cognitiva.
- **Runbooks e operação fragmentados**: há um bom começo para Fontes, mas Ingestão e Debunker ainda não falam a mesma língua visual e operacional.

A S27 existe para fechar esse gap: transformar Admin v1 em **padrão vivo e obrigatório** para os consoles críticos, não apenas um piloto.

---

## 2. Problema central que a Sprint 27 precisa resolver

### 2.1 Formulação do problema

O problema central da S27 pode ser formulado assim:

> Hoje, fontes, ingestão e debunker são operados por consoles que **não falam o mesmo idioma visual nem operacional**.  
> Isso aumenta o risco de erro humano, torna a vida do operador mais difícil e enfraquece o padrão Admin v1 recém-criado.  
> Precisamos que os consoles admin críticos (Fontes, Ingestão, Debunker) sejam **coerentes**, **operáveis** e **protegidos por gates** a partir de um design system único.

### 2.2 Sintomas concretos do problema

- Operadores relatam estranhamento ao navegar de Fontes para Ingestão ou Debunker (menus, layout, nomenclatura diferentes).  
- Alguns estados importantes (ingestão atrasada, disputa crítica no Debunker) não têm representação visual padronizada, o que aumenta a chance de serem ignorados.  
- Runbooks precisam compensar diferenças de UI com explicações específicas demais, gerando documentação mais frágil e difícil de manter.

### 2.3 Riscos se o problema não for tratado agora

- **Risco de consolidação de dívidas de UI/Admin**: se Ingestão e Debunker evoluírem mais uma ou duas sprints fora do Admin v1, a migração futura ficará mais cara e arriscada.  
- **Risco operacional**: consoles críticos com UX divergente aumentam a chance de registros incorretos, ações erradas ou atrasos em resposta a incidentes.  
- **Risco de fragmentação de método**: gates, ORR e runbooks passam a ser específicos de cada console, perdendo o ganho de padronização trazido por S26.

---

## 3. Objetivos e estados-alvo da Sprint 27

### 3.1 Objetivo geral

Transformar o Design System Inspectah Admin v1 de **piloto** (Fontes v2) em **infraestrutura padrão** para operação dos consoles críticos de Admin (Fontes, Ingestão, Debunker), garantindo coerência de UI, operação mais segura e fechamento do épico E26.

### 3.2 Estados-alvo detalhados

Ao final da S27, queremos poder afirmar, com evidência:

1. **Todos os consoles admin críticos do Programa 1 rodam sobre Admin v1**
   - Ingestão e Debunker utilizam `AdminShell`, `AdminHeader`, `AdminSidebar`, `AdminContent` e componentes padrão de `ui/admin`.  
   - Não restam layouts paralelos dentro do escopo E26; qualquer exceção é registrada como dívida técnica com ID (`S27-DT-XXX`).

2. **Estados de UI (vazio, carregando, erro, alerta, sucesso) são padronizados entre Fontes, Ingestão e Debunker**
   - Mesma linguagem visual (ícones, cores, hierarquia de informação).  
   - Mesma semântica de mensagens: o que é erro crítico, aviso, informação, etc.

3. **Existe um Guia de Consoles Admin v1.1 com exemplos reais de Ingestão e Debunker**
   - O guia mostra padrões recomendados e anti-padrões ("não faça assim").  
   - Fontes, Ingestão e Debunker aparecem como exemplos de aplicação do design system.

4. **Runbooks de Ingestão e Debunker falam o mesmo idioma de fontes**
   - Mesma nomenclatura de ações (ativar, desativar, arquivar, reprocessar, aprovar, rejeitar).  
   - Mesma referência de componentes visuais ("botão primário", "badge de erro", etc.).

5. **Gates e ORR cobrem o conjunto de consoles Admin v1**
   - G1 protege o design system admin;  
   - G2/G3 protegem fluxos cruzados Fontes ↔ Ingestão ↔ Debunker;  
   - Cap.5 da S27 estende o modelo de ORR/runbooks/risco para o conjunto completo.

6. **O épico E26 pode ser considerado encerrado do ponto de vista de UI/Admin**
   - Não há consoles admin relevantes do Programa 1 fora do Admin v1.  
   - Qualquer lacuna remanescente está registrada em Cap.6 da S27 (dívidas e impacto de roadmap).

---

## 4. Escopo IN/OUT da S27

### 4.1 Escopo IN (dentro da S27)

- Migração de Ingestão 2.0 para Admin v1, incluindo:
  - uso de layout e componentes padrão;  
  - revisão de estados de lista, detalhe, filtros e ações rápidas.

- Migração do console do Debunker v0/v1 para Admin v1, incluindo:
  - listagem de casos/disputas;  
  - exibição de status, severidade, prazos;  
  - ações de aprovação/rejeição/escalação com padrões visuais coerentes.

- Ajustes finos no Console de Fontes v2 para alinhamento completo com Admin v1 (terminologias, estados, navegação).

- Atualização do **Guia de Consoles Admin** para versão v1.1, com seções específicas para Ingestão e Debunker.

- Atualização e criação de **runbooks de operação** para Ingestão e Debunker, em sintonia com o runbook de fontes.

- Definição e implementação de **gates específicos** de frontend/admin para cobrir os novos consoles sob Admin v1.

### 4.2 Escopo OUT (fora da S27)

- Mudanças profundas na lógica de ingestão (jobs, retries, backoff, priorização) — isso é tema de sprints de Ingestão 2.0.  
- Novos fluxos de negócio do Debunker (novos tipos de disputa, novas políticas de evidência) — pertencem às sprints de Verdade & Contestação.  
- Consoles não-admin (por exemplo, UI pública de consulta, Explore para usuários externos).  
- Observabilidade avançada (dashboards complexos de métricas, tracing detalhado) além do mínimo necessário para operação dos consoles.

---

## 5. Personas e operadores-alvo

A S27 é guiada por três personas principais:

1. **Operador de Ingestão**  
   - Foco: garantir que dados entrem de forma previsível.  
   - Precisa enxergar rapidamente quais fontes/rotas estão saudáveis, atrasadas ou falhando.

2. **Analista/Debunker**  
   - Foco: analisar disputas, evidências e tomar decisões de verdade/fato.  
   - Precisa identificar casos críticos, priorizar fila e agir com clareza sobre consequências.

3. **Truth Ops / On-call**  
   - Foco: reagir a incidentes (quebras de ingestão, fontes problemáticas, disputas explosivas) com o mínimo de atrito possível.  
   - Precisa navegar entre Fontes, Ingestão e Debunker sem reaprender interface a cada tela.

O design da S27 deve ser revisado sempre perguntando:  
> "Esse console ajuda ou atrapalha esses operadores na hora que a coisa aperta?"

---

## 6. Suposições, dependências e restrições

### 6.1 Suposições

- O Design System Admin v1 está estável o suficiente após S26 para ser reutilizado sem refatorações estruturais grandes.  
- O backend de Ingestão 2.0 e Debunker já expõe APIs mínimas necessárias para que os consoles admin atuais funcionem (a S27 não é uma sprint de backend pesado).

### 6.2 Dependências

- Definições de modelo e estados de ingestão e debunker vindas das sprints S22–S25.  
- Runbook de fontes e lessons da S26, que servirão de base para runbooks de Ingestão e Debunker.  
- Roadmap atualizado pós-S26 para garantir que E26 seja fechado sem atropelar outras trilhas críticas.

### 6.3 Restrições

- **Tempo**: S27 é uma sprint unitária, não pode virar "mini-rewrite" de todos os consoles.  
- **Escopo**: qualquer alteração que mexa em lógica de ingestão ou de decisão do Debunker deve ser tratada como exceção com justificativa e, idealmente, posposta para sprints específicas.

---

## 7. Definição de sucesso da Sprint 27

A S27 será considerada bem-sucedida se, ao final:

- Um operador experiente conseguir alternar entre Fontes, Ingestão e Debunker sem sensação de "mudar de sistema".  
- Os cenários E2E definidos em Cap.2–5 para consoles Admin v1 passarem de forma estável em ambiente de staging/local.  
- O Guia de Consoles Admin v1.1 e os runbooks de Ingestão/Debunker forem usados naturalmente durante ORR e simulações de incidentes.  
- O Conselho puder declarar o épico E26 encerrado, com Admin v1 estabelecido como padrão obrigatório para consoles admin do Programa 1.

Este Capítulo 1 é o norte: qualquer decisão de design, priorização ou corte de escopo na S27 deve ser confrontada com este texto. Se algo importante não se encaixa aqui, ou está mal especificado, precisa ser revisado antes de seguir para Cap.2–4.