# Inspectah — Sprint 26 (S26)
## Capítulo 6 — Bloco 6.1
### Lessons Learned da Sprint 26

> Arquivo-alvo no repo: `docs/s26_cap_6_1_lessons_learned.md`
>
> Função: registrar os principais aprendizados da S26 em três eixos — **Técnico**, **Processual** e **Produto/UX/Operação** — no formato:  
> **O que aconteceu → Por que isso é relevante → Como repetir ou evitar**.
>
> Regra: cada learning precisa ser acionável. Nada de frases genéricas como “foi corrido, mas deu tudo certo”.

---

## 1. Learnings Técnicos

### 1.1 Design System Admin v1 como infraestrutura, não como "tema de projeto"

**O que aconteceu**  
Na S26, o Design System Inspectah Admin v1 deixou de ser um conceito solto e virou código concreto em `frontend/inspectah-ui/src/ui/admin/**`, com tokens, layout (`AdminShell`, `AdminSidebar`, `AdminHeader`, etc.) e componentes básicos reutilizáveis sendo usados pelo Console de Fontes v2.

**Por que isso é relevante**  
Antes, cada tela admin tinha um pouco de CSS artesanal e componentes ad-hoc, o que tornava qualquer evolução de UX/tema algo caro e frágil. Com o admin v1 como infraestrutura, mudanças em tokens e componentes propagam para múltiplos consoles administráveis de forma controlada. Isso prepara terreno para Programas futuros (cockpit, Explore UI, etc.) sem recomeçar UI do zero.

**Como repetir ou evitar**  
- Tratar o Design System Admin como **produto transversal**: toda sprint que cria console admin novo deve primeiro verificar se o componente cabe em `ui/admin` antes de inventar outro padrão.  
- Para S27+ manter a regra: qualquer componente admin usado em 2+ áreas vira candidato a componente/tokens em `ui/admin`.  
- Evitar criar componentes visuais importantes fora de `ui/admin` sem justificativa explícita em Cap.3.

---

### 1.2 Console de Fontes v2 como cliente de referência do admin v1

**O que aconteceu**  
O Console de Fontes v2 foi implementado diretamente em cima do Design System Admin v1 (`AdminShell`, `AdminContent`, `Button`, `Table`, `Badge`, etc.), com páginas e componentes dedicados em `features/sources/**` que consomem a base de UI em vez de replicá-la.

**Por que isso é relevante**  
Ter um cliente de referência real força o design system a ser pragmático: não é um catálogo abstrato, mas algo que suporta fluxos de trabalho com restrições de verdade (operador sob pressão, fontes com problemas, etc.). Isso reduz o risco de o admin v1 virar um "playground de UI" desconectado do produto.

**Como repetir ou evitar**  
- Sempre que o design system evoluir, validar rapidamente em um console real (fontes, ingestão, casos, etc.).  
- Proibir evolução grande do design system que não venha acompanhada de pelo menos um caso real exercitando as mudanças (E2E no estilo do bloco 5.1).  
- Evitar criar páginas admin que ignorem `AdminShell`/`ui/admin` “porque é mais rápido assim”. Esse tipo de atalho precisa ser tratado como dívida técnica explícita.

---

### 1.3 Contratos de API de fontes e UI precisam compartilhar uma fonte de verdade

**O que aconteceu**  
Na S26, o Console de Fontes v2 consumiu contratos de API em `app/sources/**` e modelos/tipos em `Source.ts`, mas ainda houve fricções pontuais entre shape esperado pelo frontend e payload real da API.

**Por que isso é relevante**  
Divergências sutis entre tipos do frontend e schemas do backend geram bugs difíceis: a UI parece funcionar, mas o backend salva campos errados ou ignora ajustes. Em fontes, isso pode significar ingestão quebrada por configuração incoerente, sem o operador perceber de imediato.

**Como repetir ou evitar**  
- Consolidar o modelo de `Source` em um lugar canônico (por exemplo, OpenAPI/JSON Schema) e derivar tipos de front e back a partir dele sempre que possível.  
- Tratar qualquer divergência detectada entre `Source.ts` e `schemas.py` como **bug de contrato**, não como detalhe cosmético.  
- Para S27+, considerar scripts de validação mais agressivos em G4 (ex.: comparar schemas gerados vs. client types) para falhar cedo.

---

### 1.4 Gates de frontend (G1, G2, G3) funcionam como cerca elétrica real

**O que aconteceu**  
A S26 obrigou a estruturar melhor G1 (design system estático), G2 (fluxos do Console de Fontes) e G3 (qualidade global do frontend), com paths claros e evidências em `out/evidence/S26_G*`.

**Por que isso é relevante**  
Em sprints anteriores, era comum existir lint/test/build de frontend, mas sem clareza de **o que exatamente** cada gate garantia. Com S26, ficou mais nítido: G1 protege o design system, G2 protege fluxos de fontes e G3 protege o conjunto. Isso reduz risco de regressões silenciosas.

**Como repetir ou evitar**  
- Nas próximas sprints de frontend, mapear gates para responsabilidades específicas (ex.: um gate só de regressão visual, outro só de contratos de API, etc.).  
- Não misturar responsabilidades de gate para não perder legibilidade (“esse script faz tudo” = ninguém sabe o que quebrou).  
- Manter a disciplina de evidências por gate (logs nomeados, `g*_*.log`, índices de cenários).

---

### 1.5 Feature flags como parte do design, não remendo de produção

**O que aconteceu**  
A S26 foi desenhada já com as feature flags lógicas `FF_ADMIN_DS_V1` e `FF_SOURCES_CONSOLE_V2` em mente, mesmo antes de implementar detalhes, e o Cap.5.4 as tratou como parte da arquitetura operacional.

**Por que isso é relevante**  
Esperar a véspera do rollout para lembrar de feature flags leva a toggles improvisados, difíceis de operar e testar. Tratar flags como peça de design permite planejar cenários de ativação gradual, rollback e testes em paralelo.

**Como repetir ou evitar**  
- Em cada sprint que introduzir algo potencialmente disruptivo (novo console, novo fluxo), exigir no Cap.3/Cap.4 uma seção explícita de flags e dos caminhos com flag ON/OFF.  
- Incluir testes (automatizados ou roteiros manuais) que cubram comportamento com flag ligada e desligada, pelo menos em staging.  
- Evitar “flags escondidas” em variáveis de ambiente sem documentação clara.

---

## 2. Learnings Processuais

### 2.1 Capítulo 4 v3 (waves + plano operacional + evidências) funcionou melhor

**O que aconteceu**  
A S26 adotou a versão mais recente do Sprint Playbook no Cap.4: waves W0–W3 bem definidas, plano de evidências (Bloco 4.3) e tasks S26-T-XXX (Bloco 4.4) conectando tudo.

**Por que isso é relevante**  
Em sprints anteriores, Cap.4 às vezes virava um checklist genérico. Na S26, ele passou a ser um **roteiro de execução** real: cada task aponta para artefatos, gates e evidências, e waves têm checklists próprios. Isso facilita tanto a execução quanto a auditoria posterior.

**Como repetir ou evitar**  
- Usar o modelo de Cap.4 de S26 como referência explícita para S27+: waves curtas, tasks com IDs, mapeamento gate→evidência.  
- Impedir Cap.4 “vago”: se uma task não aponta para código/gate/evidência, ela ainda não está pronta.  
- Sempre manter o vínculo Cap.4 ↔ Cap.5: o que não está no plano operacional não pode magicamente aparecer como cenário E2E ou item de ORR.

---

### 2.2 ORR como procedimento com roteiro, não como reunião solta

**O que aconteceu**  
O Cap.5.2 definiu um plano de ORR com pré-requisitos, passos e critérios de GO/NO-GO; não ficou só na ideia genérica de "fazer um review".

**Por que isso é relevante**  
A experiência de S25 mostrou que ORR informal vira sessão de terapia, não mecanismo de decisão. Com roteiro formal, o ORR passa a ser reexecutável: se duas pessoas seguirem o plano, devem chegar a vereditos parecidos.

**Como repetir ou evitar**  
- Em sprints futuras críticas (UI, ingestão, Truth-DB, Debunker), reproduzir a estrutura de Cap.5.2: pré-requisitos, passos, template de resumo, critérios objetivos de GO/NO-GO.  
- Evitar ORR sem evidências: nenhuma decisão GO/NO-GO deve ser tomada sem olhar scorecards, logs e cenários E2E pelo menos em amostra.

---

### 2.3 Relacionar dívidas técnicas diretamente com gates e tasks ajudou a priorizar

**O que aconteceu**  
Durante a S26, ficou mais evidente uma prática: quando uma dívida técnica aparecia (ex.: cobertura incompleta de G2, hack de layout fora de `ui/admin`), ela era associada a um gate (G2/G3/G4) e a uma task S26-T-XXX ou futura.

**Por que isso é relevante**  
Dívidas soltas em listas genéricas se perdem. Amarrar a dívida a gate/task ajuda a entender o impacto: “se essa dívida não for paga, qual gate continua frágil?”

**Como repetir ou evitar**  
- No Bloco 6.2, sempre incluir o campo "Gates afetados" em cada `S26-DT-XXX`.  
- Em planejamento de próximas sprints, puxar dívidas técnicas priorizando as que fortalecem gates estruturais (sanidade global, contratos, Debunker, Truth-DB, etc.).

---

### 2.4 Playbook v3 funcionou melhor com ligação forte a Roadmap e Programa 1

**O que aconteceu**  
A S26 foi desenhada já alinhada aos docs de estado do produto pós-S25 e ao `Roadmap.md`, como parte do Programa 1 (Admin + Fontes).

**Por que isso é relevante**  
Em sprints anteriores, havia risco de cada sprint virar um mini-projeto isolado. Com S26 alinhada ao Programa 1 e ao roadmap S26–S65, ficou mais claro como cada capítulo (1–6) contribui para o long game.

**Como repetir ou evitar**  
- Manter, no Cap.1 de cada sprint, uma seção explícita "Ligação com Roadmap" com referências a `Roadmap.md` e ao estado do produto.  
- Não aprovar sprints que não saibam dizer claramente qual programa/épico estão empurrando.

---

## 3. Learnings de Produto, UX e Operação

### 3.1 Console de Fontes v2 precisa ser pensado como ferramenta de trabalho, não vitrine

**O que aconteceu**  
Ao trazer o Console de Fontes v2 para cima do admin v1, surgiu a tensão natural entre “ficar bonito” e “ajudar operadores a sobreviver”. Runbooks (Cap.5.3) e cenários E2E (Cap.5.1) ajudaram a puxar para o lado certo.

**Por que isso é relevante**  
Fontes são parte crítica da ingestão. Uma UI polida, mas confusa, gera incidentes operacionais (I1–I4) mesmo com backend perfeito. O valor real da S26 está em operadores conseguirem cadastrar, ativar, corrigir e arquivar fontes com menos atrito.

**Como repetir ou evitar**  
- Em sprints futuras de consoles, explicitar no Cap.1 quem é o operador, em que contexto ele usa a tela e quais são as ações de sobrevivência (ex.: “desligar fonte bomba em 30s”).  
- Garantir que runbooks sejam escritos e testados com alguém que pense como operador, não como dev.

---

### 3.2 Runbook de fontes virou peça central de operação

**O que aconteceu**  
A S26 exigiu a criação do `runbook_operacao_fontes_v1.md`, com fluxos F1–F4 e incidentes I1–I4, conectando UI, operação e Truth Ops.

**Por que isso é relevante**  
Sem runbook, conhecimento operacional fica preso na cabeça de quem desenvolveu a UI ou nos logs. Com runbook, qualquer on-call minimamente treinado consegue reagir sem inventar roteiro no meio da crise.

**Como repetir ou evitar**  
- Tratar runbooks como entregáveis obrigatórios para qualquer sprint que crie ou modifique consoles de operação.  
- Validar runbooks em pequenos "fire drills": simular incidente I1–I4 e ver se alguém consegue resolvê-lo apenas lendo o doc.

---

### 3.3 Risco de UX confusa é risco de produção, não só de estética

**O que aconteceu**  
Durante a S26 ficou claro que certas decisões de UX (nomes de ações, posição de botões, diferenciação visual entre "desativar" e "arquivar") têm impacto direto na chance de operadores errarem.

**Por que isso é relevante**  
O Cap.5.4 explicitou o R4 (UX confusa) como risco operacional. Isso muda a conversa: UX ruim deixa de ser apenas "questão de gosto" e passa a ser risco de incidente.

**Como repetir ou evitar**  
- Em reviews de UX, pedir exemplos concretos: “mostra onde o operador clica pra não derrubar fonte errada”.  
- Documentar riscos UX no capítulo de riscos, associando-os a incidentes potenciais, como foi feito com R4.

---

### 3.4 Flags e rollback dão coragem para evoluir consoles críticos

**O que aconteceu**  
Ao prever `FF_SOURCES_CONSOLE_V2` como kill switch e desenhar cenários de rollback, a equipe ganhou margem para ousar mais na melhoria do console sem paralisar por medo de impacto.

**Por que isso é relevante**  
Consoles críticos muitas vezes ficam travados em UX antiga por medo de quebrar produção. Ter plano de rollback bem documentado (Cap.5.4) reduz esse medo e incentiva evolução controlada.

**Como repetir ou evitar**  
- Para cada console importante, garantir ao menos uma flag de proteção ou caminho claro de retorno.  
- Nunca fazer rollout big-bang de console crítico sem estratégia de rollback e sem pelo menos um ambiente onde as flags possam ser ensaiadas.

---

## 4. Como estes learnings alimentam Cap.6.2 e 6.3

- Itens que exigem correção concreta (ex.: gaps de contrato, testes insuficientes, escolhas de UX arriscadas) devem ser espelhados no Bloco 6.2 como `S26-DT-XXX`, com risco e janela sugerida.  
- Itens que mudam o modo de trabalhar (ex.: uso maduro de Cap.4, ORR roteirizado, papel dos runbooks) devem ser refletidos em ajustes do Sprint Playbook e de instruções gerais no `Leasson Learned so far v1.md`.  
- Itens que apontam para oportunidades maiores (ex.: "admin v1 habilita consoles futuros") devem entrar no Bloco 6.3 como ajustes de roadmap (quais sprints/programas se beneficiam diretamente dessa infraestrutura).

Dessa forma, o Bloco 6.1 não é um memorial: ele é a **entrada de dados** para dívidas técnicas (6.2) e para a evolução do Roadmap (6.3).

