# Inspectah — Sprint 27 (S27)
## Capítulo 1 — Bloco 1
### Contexto pós-S26 e papel da S27 no Épico E26

> Arquivo-alvo no repo: `docs/s27_cap_1_1_contexto_e_papel_no_epico.md`
>
> Função: detalhar o **contexto que a Sprint 27 recebe** e o **papel exato da S27 dentro do Épico E26 — Design System & Consoles Admin v1**. Este bloco é a leitura rápida que qualquer pessoa precisa fazer antes de discutir escopo, prioridades ou cortes da S27.

---

## 1. Linha do tempo resumida (S20–S27)

Para entender a S27, é útil lembrar o arco recente:

- **S20–S21**  
  - S20 começou a consolidar a visão de UI/admin e a separar melhor responsabilidades de frontend.  
  - S21 estruturou o modelo de Fonte e um primeiro Console de Fontes, ainda sem um design system admin formalizado.

- **S22–S25**  
  - S22 construiu a **Ingestão 2.0** (jobs por fonte, execução, estatísticas), criando a base de dados e APIs para um console de ingestão mais maduro.  
  - S23–S24 focaram em **interpretação, classificação e Debunker v0/v1** (camadas de análise, contestação e decisão).  
  - S25 refinou **governança de verdade/fato** e o jeito de promover informações a "verdade" dentro do Inspectah.

- **S26**  
  - Criou o **Design System Inspectah Admin v1** em `ui/admin`, com layout e componentes padronizados.  
  - Migrou o **Console de Fontes v2** para esse design system, tornando-o o primeiro cliente real de Admin v1.  
  - Estabeleceu um padrão forte de Cap.5 (ORR, runbooks, riscos) e Cap.6 (learnings, dívidas, anti-gaps) aplicado ao domínio de Fontes.

- **S27 (esta sprint)**  
  - Assume Admin v1 e Fontes v2 como base sólida.  
  - Tem como missão levar o **mesmo padrão Admin v1** para os consoles de **Ingestão 2.0** e **Debunker**, fechando o Épico E26 como um todo.

---

## 2. O que o Épico E26 quer resolver

O Épico **E26 — Design System & Consoles Admin v1** surgiu da constatação de que:

- consoles admin críticos (Fontes, Ingestão, Debunker, Cockpit de Verdade, etc.) estavam nascendo com **padrões visuais e estruturais diferentes**, mesmo dentro do mesmo produto;  
- toda evolução de UI/UX exigia retrabalho específico em cada console;  
- operadores e Truth Ops enfrentavam fricção ao navegar entre consoles, em momentos em que o tempo e a clareza são críticos.

E26 foi, então, desenhado com três ambições principais:

1. Criar um **Design System Admin único** (Admin v1) para todos os consoles internos.  
2. Migrar os consoles mais críticos para esse padrão, garantindo coerência e operabilidade.  
3. Conectar esse padrão de UI admin a um **modo de trabalho disciplinado** (gates, ORR, runbooks, anti-gaps) para que a qualidade se mantenha nas próximas sprints.

S26 atacou (1) e parte de (2) com o Console de Fontes. A S27 entra para completar (2) e reforçar (3) na prática.

---

## 3. O que a S26 já entregou e a S27 herda

Ao abrir a S27, assumimos que a S26 deixou como legado:

1. **Design System Inspectah Admin v1**
   - Estrutura de layout (`AdminShell`, `AdminHeader`, `AdminSidebar`, `AdminContent`).  
   - Tokens de cor, tipografia e espaçamento específicos para ambiente admin.  
   - Components básicos (botões, tabelas, badges, inputs, alerts) em `ui/admin`, com uso inicial no Console de Fontes v2.

2. **Console de Fontes v2 em cima de Admin v1**
   - Fluxos principais estáveis: criar, configurar, ativar, desativar/arquivar fontes;  
   - UI coerente com Admin v1 e com runbook de operação;  
   - gates configurados para proteger contratos de fontes e fluxos de UI.

3. **Modelo de método mais rígido**
   - Cap.4 da S26 como referência para waves + tasks + plano de evidências;  
   - Cap.5 como referência para ORR, cenários E2E, runbooks e riscos;  
   - Cap.6 como referência para lessons, dívidas técnicas, impacto de roadmap e anti-gaps.

Do ponto de vista de E26, S26 entregou:

- a **infraestrutura Admin v1**;  
- um **console de referência (Fontes)**;  
- e um **modelo de qualidade/método**.

---

## 4. O buraco que ainda existe sem a S27

Mesmo com o avanço da S26, sem a S27 o cenário ainda tem lacunas importantes:

1. **Assimetria visual e operacional**
   - O operador que sai do Console de Fontes para ver o estado da Ingestão ou do Debunker encontra layouts e padrões diferentes, às vezes até linguagem visual e nomenclatura confusas.

2. **Design System Admin v1 ainda como "piloto"**
   - Admin v1, embora real, está validado em apenas um console (Fontes).  
   - Ingestão e Debunker, que são tão ou mais críticos, continuam com UIs anteriores ou híbridas.

3. **Runbooks e ORR focados em Fontes**
   - O modelo de ORR/runbooks de S26 está muito centrado em Fontes, faltando uma visão integrada de operação para Fontes + Ingestão + Debunker sob o mesmo padrão.

4. **Risco de dívida estrutural de UI/Admin**
   - Se Ingestão e Debunker continuarem a evoluir fora do Admin v1, a distância entre os consoles só aumenta.  
   - Qualquer nova feature nesses domínios se basearia em uma UI que já sabemos que não é a final.

É aqui que a S27 entra: para que E26 **não vire só um "case de Fontes"**, mas sim o ponto de não-retorno da unificação de consoles admin.

---

## 5. Papel específico da S27 dentro do E26

A S27 é, literalmente, a sprint de **consolidação** do Épico E26.

Se S26 foi "abrir a trilha" (criar Admin v1, migrar Fontes, provar o método), a S27 é:

- **espalhar Admin v1 para os consoles mais críticos restantes** (Ingestão e Debunker);  
- **refinar o Console de Fontes** para ficar 100% alinhado ao padrão final (terminologia, estados, navegação);  
- **evoluir o Guia de Consoles Admin** para versão v1.1 com exemplos reais de múltiplos domínios;  
- **fechar E26** como um épico entregue, com todas as peças principais sob o mesmo idioma Admin.

Depois da S27, o papel de E26 passa a ser histórico (infraestrutura e padrão consolidados), e futuras sprints/épicos não precisam mais "negociar" se devem ou não usar Admin v1: a resposta passa a ser **sim, por padrão**, com exceções devidamente justificadas e registradas como dívida.

---

## 6. Como este bloco conversa com o restante do Capítulo 1

- O **Bloco 1** (este doc) foca em **contexto e papel da S27 no épico**.  
- O **Bloco 2** aprofunda a formulação do problema e seus riscos (do ponto de vista de operadores e do produto).  
- O **Bloco 3** detalhará os **estados-alvo e critérios de sucesso** da S27.  
- O **Bloco 4** consolidará escopo IN/OUT, personas, dependências e restrições.

Juntos, esses blocos formam o Capítulo 1 completo da S27, garantindo que qualquer discussão de gates, arquitetura ou execução esteja ancorada em um entendimento comum do **porquê** desta sprint existir.

