# Épico E26 — Console Full & Coerência de UI/Admin

> Programa 1 — Consolidação & Consoles Full  
> Dono lógico: Squad Consoles (Steve Jobs, Bret Victor, Ben Shneiderman, Kent Beck, Kelsey Hightower)

---

## 1. Identidade do épico

**Código:** E26  
**Nome curto:** Console Full & Coerência de UI/Admin  
**Programa:** Programa 1 — Consolidação & Consoles Full (S26–S32)  
**Status:** Não iniciado / Em design (ajustar quando entrar em execução)  

**Resumo em uma frase:**

> E26 garante que todos os consoles administrativos do Inspectah compartilham uma gramática visual única, previsível e documentada, de forma que qualquer operador consiga navegar o produto inteiro sem reaprender UI a cada tela.

---

## 2. Problema

Hoje o Inspectah tem (ou terá) múltiplos consoles administrativos: Fontes, Ingestão, Agentes/Fluxos, Debunker, Truth Console, Evidence Vault, Case Cockpit, etc. Sem um padrão único de UI/Admin:

- cada console pode nascer com layout, nomenclatura e estados diferentes;  
- operadores precisam reaprender interações básicas a cada tela;  
- a velocidade de operação cai, a curva de aprendizado aumenta;  
- adicionar novos consoles vira uma loteria visual, não uma extensão de um padrão.

Isso é especialmente grave para o Inspectah porque:

- o produto é orientado a **operações complexas e sensíveis** (verdade, contestação, governança);  
- grande parte do valor vem da **capacidade do humano navegar o sistema com confiança**;  
- erros de operação gerados por UI inconsistente podem ter impacto reputacional e político real.

E26 existe para matar esse problema na raiz: antes que o ecossistema exploda em telas desconexas.

---

## 3. Visão & Estado-alvo do épico

### 3.1 Frase de visão

> Quando o épico E26 estiver completo, qualquer console administrativo do Inspectah “parece Inspectah” em menos de 5 segundos de uso: a pessoa reconhece layout, barras, tabelas, estados, padrões de navegação e consegue operar sem manual específico daquela tela.

### 3.2 Estados-alvo (lista canônica)

Ao final de E26, será verdade que:

1. **Padrão de Console Full v1 está definido e versionado** num guia de UI Admin, cobrindo layout, hierarquia de informação, componentes básicos, nomenclatura e estados (loading, vazio, erro, sucesso, confirmação).
2. **Todos os consoles admin existentes aderem ao padrão v1**, com uma taxa de conformidade ≥ X% (definida neste épico) medível automaticamente e via revisão visual.
3. **Qualquer nova tela de console admin nasce a partir do padrão**, usando um kit de componentes/documentação, não de improviso.
4. **Fluxos básicos são consistentes entre consoles** (ex.: filtrar, ordenar, abrir detalhe, editar, salvar, descartar, voltar; padrões de diálogos e confirmação).
5. **Estados de erro e vazio são informativos e consistentes**, com mensagens e ações recomendadas que seguem o mesmo modelo em todos os consoles.
6. **Existe uma linguagem visual clara para estados de risco/atenção**, usada da mesma forma entre Fontes, Ingestão, Debunker, Truth Console, etc.
7. **O padrão E26 é medível**: há checkers estáticos ou heurísticas de revisão que ajudam a verificar se uma nova tela está dentro ou fora da gramática.

Esses estados são a referência para sprints que implementarem partes de E26.

---

## 4. Escopo IN / OUT

### 4.1 Escopo IN (dentro do épico)

E26 cobre:

- Definição de um **Design System mínimo para consoles admin**, incluindo:  
  - grid e layout base (estrutura de header, sidebar, área de conteúdo, painéis laterais);  
  - componentes principais (tabelas, listas, cards, filtros, formulários, modais, toasts, tooltips);  
  - padrões de estado (loading, vazio, erro, vazio com sugestão, sucesso);  
  - padrões de navegação (lista → detalhe → edição, breadcrumbs, tabs, filtros persistentes).
- Criação de um **Guia de UI/Admin v1**, versionado no repo, com exemplos visuais e textuais.
- Refino e adequação das UIs dos consoles:
  - Fontes  
  - Ingestão  
  - Agents/Fluxos  
  - Debunker  
  - Truth Console  
  - Evidence Vault / Explore  
  - Case Cockpit v1
- Definição de **tokens de design mínimos** (cores, tipografia, espaçamentos, ícones) específicos para consoles admin, alinhados com a identidade geral do Inspectah.
- Definição de **padrões de acessibilidade básicos** (contrast ratio mínimo, foco visível, suportar navegação via teclado em flows principais, mensagens não só em cor).
- Criação de um **kit técnico de componentes reutilizáveis** (no frontend) mapeado para o guia, de forma que a implementação siga o padrão com o mínimo de fricção.
- Definição de **critérios de conformidade** (checklist e, se possível, lints/validações automáticas) para telas de console admin.

### 4.2 Escopo OUT (explícita exclusão)

E26 **não** cobre:

- Redesenho conceitual profundo de fluxos de usuário (isso entra em UX v2 no Programa 6).  
- Experimentações avançadas de UX para usuários externos finais (Programa 6 — Ecossistema & UX v2).  
- Designer visual complexo para fluxos de agentes (isso é Programa 4 / E45).  
- Decisões de branding macro (logo, marketing site, identidade pública geral).  
- Refatorações internas de performance do frontend não relacionadas ao padrão de console.

---

## 5. Personas & cenários principais

### 5.1 Personas

- **Operador de Fontes/Ingestão** — mantém fontes saudáveis, monitora ingestão, age quando algo quebra.  
- **Debunker** — trabalha fila de contestação, precisa navegar rápido entre claims, evidências, casos.  
- **Truth Operator / Policy Owner** — ajusta policies de verdade, revisa decisões, consulta timelines.  
- **Investigador de Casos** — vive no Case Cockpit, mas frequentemente salta para Evidence Vault, Truth Console e Debunker.  
- **SRE/Observability** — menos foco em E26, mas se beneficia de consistência para interpretar estados.

### 5.2 Cenários-chave

1. **Operador que só conhece Console de Fontes abre Console de Debunker**:  
   - reconhece padrões de tabela/lista, filtros, ação de abrir detalhe, ações primárias/secundárias;  
   - entende imediatamente que "vermelho" significa crítico/erro em todos os consoles, não só em um.

2. **Investigador abre Case Cockpit e salta para Evidence Vault**:  
   - percebe a mesma estrutura de navegação (lista com filtros → detalhe → ações);  
   - estados vazios e mensagens seguem a mesma gramática (ex.: "Nenhuma evidência encontrada" com CTA consistente).

3. **Nova tela de admin é criada** (ex.: um painel de métricas internas):  
   - time aplica componentes e padrões existentes;  
   - revisão de design se baseia em checklist/guia de E26;  
   - não é necessário reinventar grid, componentes ou micro-padrões.

---

## 6. Interfaces & dependências

### 6.1 Interfaces

E26 interage principalmente com:

- **Frontend admin**: código React/TypeScript (ou stack definida) que renderiza consoles.  
- **Sistema de autenticação/roles**: determina o que cada persona vê, mas E26 define como isso aparece (estados desabilitados, mensagens, etc.).  
- **Backends de domínio** (Fontes, Ingestão, Agents, Debunker, Truth, Evidence, Cases): expõem dados e estados que precisam ser apresentados de forma uniforme.

### 6.2 Dependências

- Depende de:  
  - existência mínima de consoles ou seus protótipos;  
  - decisões de stack frontend (component library base, framework).  
- É dependência para:
  - **Programa 2 (Agent Brain)**, ao fornecer consoles coerentes para configuração/observação de agentes;  
  - **Programa 3 (Blocks)**, ao manter consistência nas UIs que vão expor blocos depois;  
  - **Programa 5 (Governança & Truth Ops)**, pois a operação diária precisa de consoles previsíveis.

---

## 7. Requisitos funcionais detalhados

### 7.1 Guia de UI/Admin v1

O épico deve produzir um guia versionado contendo, no mínimo:

- **Princípios de UI/Admin do Inspectah**:
  - "Consoles são ferramentas de operação, não dashboards bonitos";  
  - prioridade para clareza, legibilidade, previsibilidade, explicabilidade;  
  - minimizar estados ambíguos.
- **Layout base**:
  - header/topbar padrão (logo, título, contexto, usuário, ações globais);  
  - sidebar ou navegação principal com comportamento consistente;  
  - área de conteúdo principal com grid definido;  
  - espaço para barras contextuais (alertas, filtros avançados).
- **Componentes canônicos**:  
  - tabelas com padrões de coluna (nome, status, ações);  
  - filtros (básico/avançado);  
  - cards/resumos;  
  - formulários (edição de entidade) com padrões de validação inline;  
  - modais/diálogos com estrutura e botões fixos (primário, secundário, cancelar).
- **Catálogo de estados**:  
  - loading (com skeletons/spinners definidos);  
  - vazio (texto + ação recomendada);  
  - erro (mensagem, código, link para detalhes/logs quando aplicável);  
  - sucesso (feedback mínimo e discreto);  
  - estados críticos (ex.: "ingestão parada" ou "contestações críticas pendentes").

### 7.2 Aplicação do padrão aos consoles existentes

Para cada console listado em Escopo IN:

- mapear telas atuais e fluxos principais;  
- aplicar gradualmente o padrão (ou, se necessário, redesenho visual completo mantendo o fluxo conceitual);  
- garantir que nomenclatura, componentes e estados sejam os mesmos para situações equivalentes (ex.: lidar com filtros vazios, erro de backend, acesso negado).

### 7.3 Kit de componentes reutilizáveis

- Implementar (ou consolidar) uma **biblioteca de componentes** que represente o guia:  
  - `ConsoleLayout`, `ConsoleHeader`, `ConsoleSidebar`, `ConsoleTable`, `StatusBadge`, `EmptyState`, `ErrorState`, etc.  
- Documentar exemplos de uso (story/docs internos) com boas práticas e anti-padrões.

### 7.4 Checklist de conformidade

- Definir um checklist que deve ser aplicado a qualquer nova tela de console, por exemplo:
  - Usa layout base de E26?  
  - Usa componentes do kit e não versões ad hoc?  
  - Estados de erro/vazio seguem catálogo?  
  - Ações primária/secundária estão posicionadas e nomeadas conforme padrão?  
- Se possível, implementar validações semi-automáticas (lint de CSS/estrutura, uso de componentes proibidos etc.).

---

## 8. Requisitos não funcionais

### 8.1 Usabilidade

- Operadores devem conseguir aprender um console e transferir esse conhecimento para outro com **mínimo atrito cognitivo**.  
- Interações frequentes (filtrar, ordenar, selecionar, editar, confirmar) devem exigir **poucos cliques** e ser consistentes.

### 8.2 Acessibilidade

- Padrão de contraste e uso de cores deve seguir guidelines mínimas (ex.: WCAG AA) onde razoável.  
- Foco visível em elementos interativos, suporte a navegação por teclado em fluxos principais.

### 8.3 Performance percebida

- Estados de loading devem sempre ser explícitos (nunca tela “morta”).  
- Operações longas devem exibir progresso e possibilidade de cancelar quando aplicável.

### 8.4 Consistência & versionamento

- Mudanças na gramática visual (E26) devem ser versionadas (v1, v1.1, etc.) e documentadas com diffs claros.  
- Consoles podem conviver temporariamente com versões diferentes, mas isso deve ser exceção, não regra, e listado explicitamente.

---

## 9. Métricas de sucesso do épico

Propostas de métricas para avaliar se E26 entregou o que prometeu:

- **Consistência visual:** porcentagem de telas de console admin que usam o padrão v1 (alvo: ≥ 90%).  
- **Tempo de onboarding:** tempo médio para um novo operador conseguir executar tarefas básicas em dois consoles diferentes (queda comparada ao baseline).  
- **Número de componentes custom ad hoc:** redução de componentes não-padrão usados em consoles.  
- **Incidentes de UX reportados:** quantidade de tickets internos relacionados a confusão de UI/Admin em consoles (espera-se queda).  
- **Aderência ao checklist:** porcentagem de novas telas aprovadas no checklist de E26 sem retrabalho pesado.

Essas métricas serão amarradas a gates e scorecards específicos nas sprints que implementarem E26.

---

## 10. Decomposição em Sprints & Entregas

E26 é pensado para ser atacado em camadas, não em um tiro único.

### 10.1 Entregas lógicas (exemplo)

- **E26.1 — Guia de UI/Admin v1 + Kit de componentes base**  
  - Principalmente S26 + parte de S27 se necessário.

- **E26.2 — Consoles principais migrados para padrão v1**  
  - Consoles de Fontes, Ingestão, Debunker, Truth, Evidence, Case Cockpit.  
  - Distribuídos entre S26–S32 conforme capacidade.

- **E26.3 — Checklist, lints & revisão cruzada**  
  - Checklist aplicado, registro de conformidade, ajustes finos;  
  - interseção com ORR local de Programa 1.

### 10.2 Relação com sprints

- S26: foca em **definir o padrão e aplicar nas primeiras telas** (pelo menos um console de cada tipo).  
- S27–S32: completam migração e consolidam o padrão ao longo dos demais consoles e casos mais avançados.

Cada sprint terá seus próprios Capítulos do Sprint Playbook, referenciando este épico nas seções de contexto e estados-alvo.

---

## 11. Riscos, decisões e anti-objetivos

### 11.1 Riscos

- **Overdesign:** gastar energia demais em pixel perfect e atrasar entregas de valor funcional.  
- **Inconsistência residual:** alguns consoles ficarem com “débitos visuais” e nunca serem migrados.  
- **Acoplamento forte:** padrão de UI tão engessado que dificulta particularidades de domínios (ex.: Debunker vs Ingestão).

### 11.2 Decisões de design (guidelines)

- Priorizar **clareza e previsibilidade** sobre brilho visual.  
- Permitir variações controladas por domínio, mas sempre dentro de um guarda-chuva comum.  
- Tudo que for decidido aqui deve ser **documentado**, não só “senso comum” da squad.

### 11.3 Anti-objetivos

- E26 **não** é sobre criar um sistema mega complexo de temas, branding avançado ou ferramentas de design externas.  
- E26 **não** é sobre otimizar a UI para usuários finais da sociedade; foco são operadores internos/avançados.

---

## 12. Conexão com outros épicos e programas

- **E27 (Fontes & Ingestão 2.0 em Operação)**: depende de consoles de Fontes/Ingestão coerentes; E26 fornece a base visual.  
- **E28 (Fluxo de Agentes Configurável v1)**: UI de configuração de fluxo se beneficia diretamente do padrão de console.  
- **E29 (Debunker v1)**: fila de issues e painel do debunker precisam seguir a gramática de E26 para serem operáveis em alto volume.  
- **E30–E32 (Truth Console, Evidence Vault, Case Cockpit)**: pilares da experiência do operador; E26 garante que pareçam partes de um mesmo sistema.

No nível de programas:

- Programa 1 entrega Inspectah v0.8 operável com consoles full.  
- Programas 2–7 usam esses consoles diariamente; se E26 falhar, todo o resto fica mais frágil.

---

## 13. Notas finais

Este documento é a **constituição do épico E26**.  
Sprints do Programa 1 (S26–S32) devem referenciar este épico:

- no Cap.1 (Contexto & Escopo da sprint),  
- no Cap.2 (Gates e métricas associadas a estados-alvo de E26),  
- no Cap.3 (impacto em arquitetura/filemap dos consoles),  
- e no Cap.4 (Execution Matrix, apontando tasks que avançam especificamente E26).

Qualquer mudança estrutural na visão de consoles/admin deve passar por revisão deste épico antes de chegar a uma nova sprint.