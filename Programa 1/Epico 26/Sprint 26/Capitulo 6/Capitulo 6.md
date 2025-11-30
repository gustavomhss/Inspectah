# Inspectah — Sprint 26 (S26)
## Capítulo 6 — Learnings, Roadmap & Anti-gaps

> Arquivo-alvo no repo: `docs/s26_cap_6_macro.md`
>
> Função: consolidar **o que a S26 ensinou**, quais **dívidas técnicas** deixa para trás e **como isso altera o roadmap** S26–S65, de forma que nenhum aprendizado importante se perca e nenhum buraco fique invisível.
>
> Regra: Cap.6 não é "pós-mortem genérico". É um capítulo operacional de memória e de direção.

O Capítulo 6 existe para garantir que a Sprint 26 não seja apenas uma sequência de merges bem-sucedidos, mas um passo consciente dentro de um programa longo (S26–S65). Ele organiza o fechamento da sprint em três dimensões principais:

1. **Lessons Learned** (Bloco 6.1) — o que funcionou, o que doeu, o que precisa virar padrão ou ser evitado.
2. **Dívidas Técnicas** (Bloco 6.2) — o que ficou pendurado, com ID, risco e sugestão clara de quando/onde atacar.
3. **Impacto no Roadmap** (Bloco 6.3) — como S26 empurra, acelera ou ajusta as próximas sprints e épicos.

O resultado esperado é um capítulo que qualquer pessoa consiga ler depois de meses e responder:

> "O que a S26 nos ensinou? O que ainda falta? E o que isso mudou no caminho até S65?"

---

## 1. Relação do Capítulo 6 com os demais capítulos

- **Cap.1** (Contexto & Objetivos) diz o *porquê* da S26: que problemas queríamos resolver, quais estados-alvo queríamos tornar verdade (Design System Admin v1, Console de Fontes v2 operável, etc.).
- **Cap.2** (Gates & Métricas) define *como* medimos sucesso (G0–G6, cenários E2E, thresholds de GO/NO-GO).
- **Cap.3** (Arquitetura & Filemap) mostra *onde* no sistema essas mudanças vivem (ui/admin, features/sources, app/sources, bin/s26_g*, docs de S26).
- **Cap.4** (Execução & Tasks) descreve *como* fizemos: waves, tasks S26-T-XXX, plano de evidências.
- **Cap.5** (ORR, Operação e Risco) mostra *se* S26 funciona no mundo real e se temos freios de emergência.

O **Cap.6** olha para tudo isso retrospectivamente e responde:

- O que aprendemos **sobre o produto** (UI admin, operação de fontes, relação com ingestão)?
- O que aprendemos **sobre o jeito de trabalhar** (waves, gates, Codex, ORR, runbooks)?
- O que **não foi entregue** e precisa ter nome, dono e janela de ataque?
- O que isso muda na **linha S26–S65** (programas, épicos, prioridades)?

Sem Cap.6, o risco é repetir eternamente os mesmos erros ou carregar dívidas invisíveis que explodem mais adiante.

---

## 2. Estrutura do Capítulo 6

O Capítulo 6 é dividido em três blocos, cada um com formato e critérios claros.

### 2.1 Bloco 6.1 — Lessons Learned

Arquivo: `docs/s26_cap_6_1_lessons_learned.md`

Função: capturar os principais aprendizados da S26 em três dimensões:

1. **Técnicas** — arquitetura, design de UI, composição de componentes, contratos de API de fontes, scripts de gates, uso de ferramentas (CI, Codex, etc.).
2. **Processuais** — aplicação do Sprint Playbook v3, trabalho em waves, uso de Cap.4 na prática, interação squads ↔ Spec Office ↔ Conselho.
3. **Produto/UX/Operação** — uso real do Console de Fontes v2, fluidez do Design System Admin v1, eficácia dos runbooks e do plano de ORR.

Formato sugerido por item de aprendizado:

- **O que aconteceu** — fato concreto (ex.: "primeira rodada de sanidade S1–S25 gerou ruído por causa de permissões"; trazer o mesmo padrão para S26).  
- **Por que isso é relevante** — impacto no tempo, na clareza, na qualidade.  
- **Como repetir ou evitar** — ação ou regra que deve entrar no playbook do time.

O objetivo é que o Bloco 6.1 seja curto, intenso e acionável, não uma crônica sentimental da sprint.

### 2.2 Bloco 6.2 — Dívidas Técnicas

Arquivo: `docs/s26_cap_6_2_dividas_tecnicas.md`

Função: nomear e estruturar as **dívidas técnicas da S26** de forma que possam ser cobradas no futuro.

Cada dívida deve ter, no mínimo:

- **ID**: `S26-DT-XXX` (por exemplo, `S26-DT-001`).  
- **Descrição**: clara e objetiva ("cobertura insuficiente de testes para fluxo X", "scripts Y/Z ainda acoplados a layout antigo", etc.).  
- **Risco**: baixo/médio/alto, com frase curta explicando o impacto se ficar parada.  
- **Contexto**: de onde veio (que task/gate/decisão gerou a dívida).  
- **Sugestão de janela**: sprint/épico em que deve ser atacada (ex.: "idealmente S28–S29", "acoplar a épico de Ingestão 2.0").

Dívida técnica **não é pecado eterno**: é uma linha do tempo explícita de trade-offs. O Bloco 6.2 impede que esses trade-offs desapareçam.

### 2.3 Bloco 6.3 — Impacto no Roadmap

Arquivo: `docs/s26_cap_6_3_impacto_no_roadmap.md`

Função: traduzir o que aconteceu na S26 em linguagem de **roadmap**, respondendo:

- O que S26 **adiantou** em relação ao plano S26–S65 (por exemplo, maturidade antecipada do Design System Admin v1 ou de operação de fontes)?
- O que S26 **empurrou** (epics ou sprints cujo escopo precisa ser replanejado)?
- Que **ajustes finos** de escopo, ordem ou foco precisam acontecer em programas/épicos (Programa 1, epics de Ingestão, Verdade & Interpretação, etc.)?

Esse bloco deve se conectar diretamente ao `Roadmap.md` e ao estado pós-S25 (`inspectah_estado_do_produto_v_0_5_pos_s_25.md`), para mostrar claramente:

- "Antes da S26, o plano era X";  
- "Depois da S26, o plano atualizado é Y".

---

## 3. Uso do Capítulo 6 por diferentes atores

### 3.1 Squads e Spec Office

- Usam o Bloco 6.1 para ajustar o **jeito de trabalhar** (waves, gates, CI, interação com Codex) e incorporar boas práticas imediatamente nas sprints seguintes.  
- Usam o Bloco 6.2 como backlog de dívidas técnicas para negociação explícita com produto e Conselho.  
- Usam o Bloco 6.3 para propor ajustes de roadmap (ordem de sprints, foco de epics) com base em evidências, não em feeling.

### 3.2 Conselho & ORR

- Revisam o Cap.6 ao avaliar programas e epics mais longos (não só a S26).  
- Verificam se padrões de problema estão se repetindo (ex.: sempre as mesmas dívidas empurradas).  
- Usam o Bloco 6.3 para alinhar decisões de prioridade macro com o que realmente aconteceu nas sprints.

### 3.3 Operação & Truth Ops

- Consultam lessons que afetam diretamente operação (ex.: incidentes recorrentes de fontes, lacunas de runbook, pontos fracos da UI admin).  
- Cobram endereçamento de dívidas que geram incidentes repetidos (R1–R5 do Cap.5).  
- Usam o Bloco 6.3 para entender quando melhorias operacionais entrarão no roadmap.

---

## 4. Conexão do Capítulo 6 com o Roadmap S26–S65

O Capítulo 6 é o elo explícito entre a Sprint 26 e a trilha maior S26–S65 descrita em `Roadmap.md`:

- Lessons Learned (6.1) alimentam ajustes de método que devem valer **para todas** as sprints subsequentes, não só S27.  
- Dívidas Técnicas (6.2) viram entradas formais em epics ou sprints específicas.  
- Impacto no Roadmap (6.3) documenta a diferença entre o plano "pré-S26" e a realidade "pós-S26".

Assim, qualquer pessoa pode reconstituir a narrativa:

1. O que planejamos para S26 (Cap.1 + Roadmap).  
2. O que realmente aconteceu (Cap.4 + Cap.5).  
3. O que aprendemos e como isso mudou o futuro (Cap.6).

---

## Nota rápida (wrap W3)

- Gates G0–G3 executados e verdes; fluxos de fontes cobertos por testes RTL/MSW sem warnings.  
- Learnings preliminares: (1) design system admin v1 sustentável para novos consoles; (2) avisos de act exigem disciplina de testes integrada a MSW/RTL; (3) QA manual ajudou a expor desalinhamento front/back (slug/id) e a necessidade de priorizar o router correto de fontes.  
- Dívidas registráveis para Bloco 6.2: expandir cobertura de bordas/validações das fontes, escrever runbook operacional e gerar bundle final (G5/G6).

## 5. Síntese do Capítulo 6

O Capítulo 6 fecha a Sprint 26 como uma unidade de aprendizado, não apenas de entrega:

- **Bloco 6.1** captura aprendizados técnicos, processuais e de produto em formato acionável.  
- **Bloco 6.2** transforma compromissos implícitos em uma lista explícita de dívidas técnicas com risco e janela de ataque.  
- **Bloco 6.3** conecta S26 ao Roadmap S26–S65, atualizando o plano com base em fatos.

No conjunto, o Capítulo 6 garante que S26 não se dilua na memória: ela vira base concreta para trabalhar **melhor**, **com menos dívida invisível** e **com roadmap alinhado à realidade** nas próximas sprints.
