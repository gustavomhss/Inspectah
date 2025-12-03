# Inspectah — Sprint 28
## Capítulo 1 — Bloco 4
### Fora de escopo, cortes conscientes e fronteiras com outros épicos (E27.1 — CRUD & ON/OFF de Fonte)

---

#### 1.4.1 Por que este bloco existe

A Sprint 28 é estrutural: ela mexe em fontes, em ingestão e no console que os operadores vão usar todos os dias. Sem fronteiras claras, o escopo tende a se esticar para tentar “consertar o mundo inteiro” de uma vez.

Este bloco serve para:
- **Congelar o que NÃO entra** na Sprint 28, mesmo que seja tentador.  
- Explicitar **o que será preparado agora** apenas como gancho para épicos futuros.  
- Evitar que a S28 vire um híbrido confuso de E27.1 + E27.2 + E27.3 + E29–E32.

A regra de ouro: se algo não contribui diretamente para tornar verdade o objetivo da S28 —
> "Fontes operáveis 100% via console, com CRUD consolidado e ON/OFF determinístico conversando com Ingestão 2.0" —
então esse algo é forte candidato a **ficar fora** desta sprint.

---

#### 1.4.2 Fora de escopo funcional (o que não será implementado agora)

1. **Health score completo de fontes (E27.3)**  
   - Não entra nesta sprint o cálculo de:  
     - scores agregados de saúde (ex.: 0–100, "OK", "DEGRADED", "CRITICAL"),  
     - janelas temporais sofisticadas (ex.: erro sustentável em N janelas),  
     - regras completas de alerta e degradação progressiva.  
   - A S28 apenas garante que o modelo de `Source` comporte os campos que serão úteis para E27.3 (ex.: `criticality`, `state_changed_at`, `state_reason`).  
   - A UI pode ter **micro indícios** mínimos (ex.: último `IngestionRun` com falha), mas não pretende entregar o painel de saúde definitivo.

2. **Histórico detalhado de ingestão (E27.2)**  
   - A S28 não entrega:
     - tela de histórico por fonte mostrando todos os `IngestionRun`,  
     - gráficos / charts de sucesso vs falha por período,  
     - filtros avançados por janela temporal, estágio de ingestão, tipo de erro.  
   - O que entra: apenas o essencial para validar ON/OFF (ex.: verificar se `IngestionRun` está ocorrendo ou cessou após uma transição de estado).  
   - A experiência rica de "histórico de ingestão" será tratada como objetivo central de **E27.2 — Histórico & métricas de ingestão**.

3. **Logs administrativos ricos e integração profunda com Evidence Vault (E27.3 + E31)**  
   - S28 não implementa ainda:
     - trilhas auditáveis completas do tipo "Usuário X desativou a fonte Y às 14:32, do IP tal, com este contexto",  
     - acoplamento direto desses logs em uma estrutura de Evidence Vault.  
   - O que entra:  
     - registro mínimo da razão de mudança de estado (`state_reason`) e timestamps (`state_changed_at`),  
     - um desenho de como isso poderá se ligar a logs mais ricos no futuro.  
   - A auditoria completa e o vínculo com Evidence Vault ficam para **E27.3** e **E31 — Evidence Vault & Explore v1**.

4. **Refactor amplo da Ingestão 2.0**  
   - A Ingestão 2.0 é tocada **apenas** naquilo que é necessário para respeitar `Source.state` e `Source.mode`.  
   - Não é escopo da S28:  
     - trocar motor/scheduler,  
     - redesenhar completamente a forma de armazenar `IngestionRun`,  
     - criar nova arquitetura de filas, workers ou paralelismo.  
   - Qualquer insight sobre melhorias profundas na ingestão deve ser:  
     - documentado como input para sprints específicas de ingestão,  
     - e não implementado na S28.

5. **Alterações estruturais no Design System Admin v1 (E26)**  
   - O console de fontes v2 **consome** o Design System Admin v1; ele não o redesenha.  
   - Não entra nesta sprint:  
     - criação de novos princípios core de tipografia, spacing, paleta ou grid de admin,  
     - refactor profundo em componentes base utilizados por outros consoles.  
   - Se a S28 encontrar lacunas claras (ex.: falta um componente de filtro múltiplo que faria muita diferença), o fluxo é:  
     - registrar a necessidade como input para E26,  
     - eventualmente usar um "fallback" temporário, mas sem recriar um mini design system paralelo.

6. **Jornadas completas de casos, Debunker e Truth Console (E29–E32)**  
   - S28 não entrega:  
     - telas de Debunker v1 (fila, workflow),  
     - telas de Truth Console v1.5 (timeline de verdade, policies visíveis),  
     - Case Cockpit v1 com visão completa dos casos.  
   - O que entra na S28 é exclusivamente a parte de fontes que estes módulos futuros vão consumir:  
     - modelo de `Source` decente,  
     - estados consistentes,  
     - rastros mínimos (`state_reason`, timestamps, domínio, criticidade).

7. **Qualquer coisa que mude o modelo de "domínio" do Inspectah**  
   - A S28 pode usar o conceito de `domain` em `Source` (ligação lógica com áreas como política, economia, mercado etc.), mas não vai redesenhar o sistema inteiro de domínios do Inspectah.  
   - Se for detectada uma necessidade de evolução grande nos domínios, isso virará backlog para sprints apropriadas.

---

#### 1.4.3 Fora de escopo técnico (limites em nível de implementação)

Além de escopo funcional, há limites técnicos importantes:

1. **Mudanças de banco destrutivas sem migração clara**  
   - A S28 não fará "limpezas agressivas" de schema sem:  
     - migrations explícitas,  
     - plano de backwards compatibility aceitável,  
     - evidências de que dados existentes não serão corrompidos.  
   - Se algum campo antigo não puder ser retirado com segurança nesta sprint, ele será mantido (marcado como legado) e planejado para migração futura.

2. **Introdução de novas tecnologias infra pesadas**  
   - S28 não introduz novos bancos, novos sistemas de filas, novos stacks de observabilidade.  
   - Quaisquer evoluções desse tipo precisam ser tratadas em sprints próprias, com análise de impacto mais ampla.

3. **Refactor global de testes**  
   - Serão criados/ajustados testes diretamente relacionados a E27.1:  
     - domínio de fontes,  
     - API de admin,  
     - integração ON/OFF × Ingestão.  
   - A sprint não vai "aproveitar o embalo" para refatorar suites inteiras de testes não relacionadas — isso entra como backlog.

4. **Criação de um sistema completo de RBAC (permissões) para fontes**  
   - A Sprint 28 assume um modelo mínimo de acesso (ex.: rotas de admin já protegidas pelo mecanismo atual),  
   - mas não implementa um sistema completo de roles (ex.: "Operador pode desativar, mas não deprecar"), que deve ser tratado em épicos específicos de segurança/governança.

---

#### 1.4.4 Ganchos explícitos para épicos futuros

Embora muita coisa fique fora da Sprint 28, ela precisa **deixar os pontos de costura** preparados. Esta seção lista o que será conscientemente deixado como gancho, não como dívida escondida.

1. **Para E27.2 — Histórico & métricas de ingestão**  
   S28 garante:
   - `Source` com campos consistentes que permitam agrupar e analisar ingestão por: tipo, domínio, categoria, criticidade, modo, estado.  
   - Integração mínima ON/OFF × Ingestão 2.0, que E27.2 poderá observar e quantificar (ex.: tempo médio de inatividade por fonte).  
   - Padrões de nome e localização de testes e scripts (G4) que poderão ser estendidos para cenários mais ricos.

2. **Para E27.3 — Saúde da fonte & logs administrativos**  
   S28 entrega:
   - Campos `criticality`, `state_changed_at` e `state_reason` já presentes e preenchidos nos momentos importantes.  
   - Padrão mínimo de como registrar motivos de transições de estado (texto curto, sem ambiguidade).  
   - Experiência do operador com ON/OFF consolidada, pronta para ser enriquecida com indicadores de saúde e logs.

3. **Para E29 — Debunker v1 (fila & workflow)**  
   - Com fontes operáveis e estados confiáveis, o Debunker poderá, nas próximas sprints, relacionar contestações à qualidade de fontes específicas.  
   - S28 não cria essa relação ainda, mas garante que fontes não sejam uma variável caótica.

4. **Para E30 — Truth Console v1.5**  
   - O Truth Console precisará saber, no futuro, "em que estado estavam as fontes relevantes" quando determinada verdade foi promovida.  
   - S28 inicia isso oferecendo estados de fonte claros e timestamps, sobre os quais E30 poderá construir explicações.

5. **Para E31/E32 — Evidence Vault & Case Cockpit**  
   - S28 garante que o conceito de `Source` seja estável o suficiente para ser referenciado em evidências e casos.  
   - Quando E31/E32 ligarem casos a fontes, não precisarão brigar com estados mal definidos ou campos faltando.

---

#### 1.4.5 Regra operacional: como tratar "descobertas" fora de escopo

Durante a Sprint 28, é inevitável que surjam descobertas e ideias que não cabem no escopo atual. A forma de lidar com isso é padronizada:

1. **Registrar imediatamente**  
   - Toda descoberta relevante é registrada em uma seção específica (ex.: "Backlog E27.x/E29–E32" no Capítulo 4 ou em um doc auxiliar de backlog).  
   - O registro inclui contexto, motivo, impacto potencial e sugestão de onde isso se encaixa no roadmap.

2. **Não expandir o escopo da Sprint 28**  
   - A menos que a descoberta seja um bug crítico que impede a própria S28 de ser concluída, ela **não** entra como escopo adicional.  
   - A prioridade é concluir os estados-alvo de CRUD & ON/OFF com excelência.

3. **Revisar com o conselho de produto/arquitetura no encerramento**  
   - No fechamento da sprint (ORR), a lista de descobertas é revisada com o conselho/squad responsável pelo roadmap,  
   - e cada item é endereçado a um épico/sprint futuro com clareza.

---

Com isso, o Bloco 4 fecha o Capítulo 1 da Sprint 28 definindo com precisão **onde a sprint termina**. Esse contorno é o que permite à equipe atacar E27.1 com profundidade, sem se perder em promessas que pertencem a E27.2, E27.3, E29–E32 ou a programas posteriores.

