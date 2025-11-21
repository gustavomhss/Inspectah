# Sprint 14 – Contestação v0 & Loop de Correção Multi‑Domínio

## 1. TL;DR — Antes e depois da S14

A Sprint 14 ensina o Inspectah a **corrigir o que ele mesmo mostrou**, de forma controlada, auditável e sem mágica: feedback deixa de ser só reclamação solta e vira **contestation v0**, com estados claros, impacto medido e rastreabilidade de antes/depois.

Pensamos na S14 como o **“modo revisão de prova”** do Inspectah: nada é apagado, tudo é corrigido “a caneta vermelha” por cima da linha do tempo, deixando claro o que estava errado, por que foi corrigido e qual é a verdade atual.

Essa sprint não implementa blockchain, reputação ou o Sistema de Blocos completo: ela entrega o **mínimo write path sério de contestação e correção** em cima do backbone S12–S13, preparando o caminho para a Fase 2 sem explodir a complexidade agora.

### 1.1 Antes da S14

Pós‑S12 e S13, o Inspectah já estava em um estado forte, mas com um buraco claro no loop de correção:

- Ingestão contínua enxuta funcionando.
- Debunker v0 obrigatório nos domínios críticos.
- Casos e timelines auditáveis.
- Explorer v0 para busca/detalhe.
- Painel de feedback v0 gerando um backlog de problemas.
- Piloto multi‑domínio S13 rodando (obra pública, evento climático, projeto de lei, carreira política, influencer, atleta).

Mas, na prática:

- Feedback virava um **backlog “solto”**, sem modelo próprio de contestação.
- Não havia um fluxo claro “isto aqui está errado → alguém decide → o sistema muda de forma rastreável”.
- Ajustes tendiam a ser **manual/implícitos** em dados e snapshots, sem um registro forte de causa/efeito.

### 1.2 Depois da S14

Com a S14 bem‑sucedida, o Inspectah passa a ter:

- Um **modelo explícito de Contestação v0** (entidade própria, estados, severidade, impacto, vínculos com casos/eventos).
- Um pipeline claro **feedback → contestação → decisão → ação corretiva → snapshots atualizados**.
- Um **Painel de Contestação v0** que permite operar esse fluxo sem planilha paralela.
- Métricas específicas de contestação (coverage de backlog, resolution_ratio, tempos de triagem/resolução, impacto por domínio).
- Princípios de contrato para correções: **identificáveis, reversíveis, justificáveis e limitadas a escopos bem definidos**.

Em termos de experiência, a diferença é simples:

> **Antes**: o Inspectah “falava” o que achava que era verdade e anotava reclamações.
>
> **Depois**: o Inspectah **consegue revisar a própria prova**, explicar o que foi corrigido e sustentar uma versão atual da verdade com histórico intacto.

---

## 2. Contexto — Onde a S14 se encaixa no plano S10–S16

### 2.1 O que já foi consolidado (S10, S12, S13)

Do ponto de vista de produto e arquitetura, chegamos na S14 com três pilares consolidados:

1. **S10 – Truth‑DB & Guardião**  
   - Modelo de casos e timelines como forma padrão de representar “o que aconteceu” e “o que o Inspectah acredita agora”.  
   - Debunker v0 como guardião obrigatório de entrada, explicando por que algo é aceito/suspeito.

2. **S12 – Ingestão contínua + Explorer v0**  
   - Ingestão contínua enxuta rodando em domínios piloto.  
   - Caso/timeline auditáveis.  
   - Explorer v0 para busca e consulta de casos.  
   - Painel de feedback v0.  
   - Gates S12_G0…S12_G8 e tag **v0.3‑s12** como marco.

3. **S13 – Piloto multi‑domínio**  
   - Seis domínios operando em cima do backbone S12:  
     - Obra pública municipal.  
     - Evento climático severo.  
     - Projeto de lei.  
     - Carreira política.  
     - Perfil de influencer.  
     - Carreira de atleta.  
   - Pilotos descritos em `config/s13_pilotos.yml`, com timelines reconstruíveis, Debunker cobrindo todos os casos, Explorer navegando cada domínio e feedback alimentando um backlog.  
   - ORR da S13 documenta que chegamos a **v0.4‑s13** com G0…G8 PASS/GO.

### 2.2 Handshake com o blueprint S13–S16 e a Nota de Escopo

O blueprint S13–S16 define uma visão ambiciosa:

- S13–S14: write path completo com disputas, contestações, propagação bottom‑up e estruturação em blocos (core, sub‑blocks, components, notes).
- S15–S16: evolução para Sistema de Blocos completo, reputação, incentivos, eventualmente âncoras em blockchain e comunidade avançada.

A **Nota de Escopo Temporário de Sanidade** corta esse plano em fatias menores para não implodir a fase atual, com quatro NÃO explícitos:

- Sem blockchain agora.  
- Sem reputação pesada.  
- Sem Sistema de Blocos completo.  
- Sem comunidade avançada.

A Sprint 14 respeita essas restrições e faz um **handshake explícito** com o blueprint:

- Ela entrega a **versão v0, local e controlada** do write path de contestação/correção.  
- Toda a semântica futura de blocos, reputação e comunidade é tratada como Fase 2.  
- Ainda assim, a S14 **segue o mesmo espírito** do plano original: contestar fatos, tomar decisões e refletir essas decisões no que o Inspectah mostra como verdade atual.

---

## 3. Conceitos centrais da S14

### 3.1 A metáfora: “modo revisão de prova”

A metáfora oficial da S14 é o **modo revisão de prova**:

- A prova original (timeline, casos, snapshots) continua lá, intacta.  
- Contestações são como marcações de caneta vermelha: “esta questão está errada”, “esse enunciado está confuso”, “essa resposta está desatualizada”.  
- A correção não é apagar a prova, é **adicionar camadas por cima**: comentários, versões corrigidas e um novo gabarito que passa a valer dali em diante.  
- O usuário final continua vendo a “prova corrigida”, mas o sistema sabe exatamente o que mudou, por quê e qual era o estado anterior.

Essa metáfora guia todas as decisões da S14: nenhum fluxo pode exigir apagar o passado; tudo precisa ser anotado, corrigido e versionado.

### 3.2 Três definições canônicas

Para evitar confusão entre termos, a S14 fixa três conceitos com nomes estáveis:

1. **Evento de contestação**  
   - É o ato de alguém (humano ou agente GPT) dizer de forma explícita:  
     “esta parte desta verdade (caso/evento/timeline) está errada, incompleta, ambígua ou desatualizada”.  
   - Sempre referencia: domínio, caso, alvo (evento/timeline/narrativa), tipo de problema e justificativa mínima.

2. **Ação corretiva**  
   - É o que o sistema faz em resposta a uma contestação **aceita** ou processada.  
   - Pode ser: reprocessar ingestão, ajustar normalização, recalcular a decisão do Debunker, atualizar narrativa ou marcar o caso/timeline com novo estado oficial.  
   - A ação corretiva **nunca é invisível**: sempre deixa evidência (antes/depois) e vínculo com a contestação de origem.

3. **Impacto**  
   - É como a ação corretiva muda o que o Inspectah mostra para fora.  
   - Ex.: mudar o status de uma obra de “andamento normal” para “revisão em andamento”, corrigir um valor numérico que estava errado, ajustar a narrativa de um evento climático para refletir nova evidência.  
   - Impacto é sempre observável nos snapshots e/ou na UI.

### 3.3 Mini‑máquina de estados para casos/fatos

Sem substituir o design completo do Sistema de Blocos, a S14 adota uma **mini‑máquina de estados conceitual** para casos/fatos:

- `ACEITO`: o Inspectah considera a versão atual do caso/fato “boa o suficiente” para exposição normal.  
- `INCERTO`: há sinais de dúvida (contestação aberta, Debunker em estado ambíguo, dados conflitantes) e o sistema expõe essa incerteza.  
- `SUSPEITO`: há forte indicação de erro ou fraude; o caso/fato é marcado como crítico, e o operador deve priorizar.  
- `REVISADO`: houve ação corretiva; a linha do tempo foi ajustada, a narrativa foi corrigida ou o status mudou com base em nova evidência.  
- `DESCARTADO`: o fato/caso específico foi considerado inválido para fins de verdade atual (mas a linha do tempo histórica continua registrada).

**Onde a contestação atua nessa máquina:**

- Eventos de contestação novos tendem a empurrar casos/fatos de `ACEITO` → `INCERTO` ou `SUSPEITO`.  
- Ação corretiva bem‑sucedida tende a levar o caso/fato para `REVISADO` (novo gabarito) ou `DESCARTADO` (invalidado, mas lembrado).  
- A ausência de contestação relevante, combinada com ingestão saudável, mantém o caso/fato em `ACEITO`.

Essa mini‑máquina de estados é a base para os gates de S14 (Cap. 2) e para o filemap que vai organizar evidências e snapshots (Cap. 3).

### 3.4 Separação entre histórico e verdade atual

A S14 reforça explicitamente uma regra que já vinha de S10–S13:

- **Linha do tempo histórica**: o que foi visto, extraído e registrado em cada momento (eventos brutos, normalizados, snapshots datados).  
- **Verdade atual do Inspectah**: a interpretação consolidada que o sistema mostra hoje, levando em conta ingestão, Debunker, contestações e ações corretivas.

Na prática:

- Nenhuma correção mexe direto em `inspectah.db` ou nos snapshots brutos sem deixar rastro;  
- É proibido “apagar o passado” por atalho;  
- Cada correção produz **novos artefatos** (nova versão de snapshot, registro de ação corretiva e link com a contestação correspondente).  

Essa distinção é o que permite o Inspectah “revisar a prova” sem fraudar o histórico.

---

## 4. Objetivos principais da Sprint 14

### 4.1 Objetivo 1 — Modelo de Contestação v0 simples, mas sério

Criar e consolidar um modelo de Contestação v0 que:

- Tenha uma entidade clara de contestação (ID, domínio, caso, alvo, severidade, tipo de problema, justificativa, timestamps).  
- Use a mini‑máquina de estados definida acima para o ciclo de vida da própria contestação (ex.: `open`, `in_triage`, `accepted`, `rejected`, `wont_fix`, `done`).  
- Seja suficientemente simples para operar o piloto multi‑domínio, mas suficientemente rígido para não virar “post‑it solto”.

### 4.2 Objetivo 2 — Fechar o fluxo feedback → contestação → correção

Pegar o backlog vindo da S13 (especialmente `backlog_s14_seed.json`) e:

- Transformar feedbacks relevantes em eventos de contestação bem estruturados.  
- Encadear a partir daí o resto do fluxo: triagem → decisão → ação corretiva → atualização de snapshots e estados de casos/fatos.  
- Garantir que, para contestações aceitas, exista sempre um **efeito visível**: mudança de estado, ajuste em narrativa, reprocessamento de ingestão, etc.  
- Manter o vínculo `feedback_id → contestacao_id → ação corretiva → snapshots antes/depois` em evidência.

### 4.3 Objetivo 3 — Painel de Contestação v0 realmente utilizável

Entregar uma UI mínima, mas funcional, que permita operar contestação no dia a dia:

- Lista consolidada de contestações com filtros por domínio, estado, severidade e período.  
- Visão por caso, integrada à CasePage do Explorer, mostrando contestações associadas e permitindo ações rápidas.  
- Integração com o painel de feedback existente, para que o operador consiga navegar de feedbacks para contestações e vice‑versa.  
- Sempre dentro do escopo atual: o público só consulta e envia feedback; quem mexe em contestação é operador/admin.

### 4.4 Objetivo 4 — Métricas e observabilidade do loop de contestação

Definir, calcular e expor métricas específicas da S14, por exemplo:

- **fraction_backlog_addressed**: quantos itens do backlog inicial da S14 viraram contestações com algum tipo de decisão.  
- **resolution_ratio_global e por domínio**: fração de contestações em estado final (`accepted`, `rejected`, `wont_fix`, `done`).  
- **tempo médio para triagem** e **tempo médio para resolução**.  
- **impacto efetivo**: proporção de contestações aceitas que realmente resultaram em nova versão de caso/timeline ou narrativa.

Essas métricas vão alimentar os gates de observabilidade (S14_G7) e a decisão final (S14_G8), a serem detalhados no Capítulo 2.

---

## 5. Papel do GPT e do Debunker na S14

A S14 deixa claro que **GPT e Debunker não são juízes finais da verdade**. Eles atuam dentro de um contrato pequeno e verificável:

- GPT:
  - Sugere onde contestar (identifica trechos inconsistentes, ambíguos ou desatualizados).  
  - Ajuda a redigir justificativas e sumarizar evidências para contestações.  
  - Apoia o operador na escolha de ações corretivas dentro da mini‑máquina de estados, mas **não muda estados diretamente**.

- Debunker v0:
  - Continua responsável por explicar por que algo é aceito/suspeito.  
  - Na S14, também é usado como fonte de sinal adicional: contestação pode ser disparada quando o Debunker aponta inconsistências fortes ou baixa confiança.  
  - É reexecutado quando ações corretivas exigem reavaliar um caso.

Todo uso de GPT e Debunker precisa deixar rastro: estamos em modo “revisor assistido por IA”, não em modo “IA decidindo sozinha o que é verdade”.

---

## 6. Princípios de contrato para correções na S14

A S14 formaliza quatro princípios que qualquer correção precisa respeitar:

1. **Identificável**  
   - Toda correção deve ser rastreável a uma contestação específica (ou, em casos excepcionais, a um evento de operador claramente registrado).  
   - Deve ser possível responder “por que isso foi corrigido?” com base em arquivos/evidências.

2. **Reversível**  
   - O sistema precisa manter snapshots suficientes para reverter uma correção, se necessário.  
   - Reversão não apaga a correção anterior: cria um novo passo na linha do tempo de verdade atual.

3. **Justificável**  
   - Cada correção deve ter uma justificativa mínima compreensível por humanos (texto curto, link para evidências, ou ambos).  
   - “Porque o modelo falou” nunca é justificativa aceitável.

4. **Limitada**  
   - Correções precisam declarar claramente **qual é o escopo**: caso, evento, narrativa, domínio.  
   - É proibido “dar canetada global” sem granularidade (ex.: mudar o status de todos os casos de um domínio sem motivo explícito).

Esses princípios são o norte de design para o Capítulo 2 (gates), Capítulo 3 (filemap/arquitetura) e Capítulo 4 (execução com Codex). Se algum fluxo violar qualquer um deles, a regra é simples: não entra na S14.

---

## 7. Fora de escopo (reafirmação)

Para não deixar dúvidas, a S14 **não** faz:

- Blockchain, contratos on‑chain, Merkle trees ou âncoras de verdade em redes públicas.  
- Sistema de reputação completo para fontes, operadores ou comunidade.  
- Comitês de disputa em múltiplas fases, jurados, staking/bonds, ou gamificação de contestação.  
- Modelo completo de Sistema de Blocos com core blocks, sub‑blocks, components e notes formais.  
- Abertura de contestações públicas via API para comunidade em larga escala.

O foco é **aprender a revisar a própria prova**, com alta sanidade, sobre um conjunto limitado de pilotos, em preparação para a Fase 2.

---

## 8. Critérios de sucesso (visão de alto nível)

A Sprint 14 é considerada bem‑sucedida quando, ao final:

- O modelo de Contestação v0 está implementado e preenchido com dados reais dos pilotos multi‑domínio.  
- O backlog inicial (especialmente `backlog_s14_seed.json`) foi efetivamente consumido e convertido em contestações triadas e majoritariamente resolvidas.  
- Existe um Painel de Contestação v0 usável no dia a dia, sem depender de planilhas externas.  
- As métricas de contestação (coverage de backlog, resolution_ratio, tempos médios, impacto) são calculadas e expostas de forma confiável.  
- A ORR da S14 consegue contar, de forma simples, uma história clara: **onde o Inspectah já consegue revisar e corrigir suas verdades** e quais são os próximos passos naturais para a Fase 2 do Sistema de Blocos.

