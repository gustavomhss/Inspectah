# Inspectah — Sprint 28
## Capítulo 1 — Bloco 1
### Contexto, visão e encaixe no Programa 1 (E27.1 — CRUD & ON/OFF de Fonte)

---

#### 1.1.1 Posição da Sprint 28 no mapa geral

A Sprint 28 vive na interseção de três forças:

1. **Programa 1 — Consolidação & Consoles Full (E26–E32)**  
   Programa 1 define a ambição macro: toda operação interna do Inspectah precisa acontecer a partir de **consoles consistentes**, com estados claros, sem depender de scripts escondidos ou conhecimento tribal. É o movimento de transformar o sistema em uma ferramenta operável por pessoas que não participaram da construção do código.

2. **Épico E27 — Fontes & Ingestão 2.0 em Modo Operação**  
   E27 pega o que S21 e S22 já construíram (modelo de fontes e Ingestão 2.0) e pergunta: “Como um operador consegue manter isso rodando 24/7 sem entrar em modo arqueólogo de logs e scripts?”. O foco é **governar fontes e ingestão como um sistema vivo**, com ON/OFF previsível, métricas e saúde.

3. **Sub-épico E27.1 — CRUD & ON/OFF de Fonte**  
   E27.1 é o primeiro passo concreto de E27: consolidar **modelo de fonte + API de admin + console + ON/OFF**. A Sprint 28 é a sprint que materializa esse sub-épico.

Dentro desse contexto, a Sprint 28 é o ponto em que o módulo de fontes deixa de ser um conjunto de tabelas, endpoints e telas parcialmente alinhadas, e se torna um **objeto operacional de primeira classe**: algo que alguém pode gerenciar, auditar e confiar sem ter que ler o código-fonte.

---

#### 1.1.2 Estado atual do produto antes da Sprint 28

Antes da Sprint 28, o Inspectah está, em linhas gerais, assim:

- **Modelo de fonte existente, mas incompleto do ponto de vista operacional**  
  - A S21 criou `Source` e `SourceType`, com estados básicos (`ACTIVE`, `DISABLED`, `DEPRECATED`) e tipos (`news_rss`, `http_json`, `price_feed`, `custom_api` etc.).  
  - Esses modelos funcionam, mas foram desenhados quando a visão de operação do produto ainda era mais limitada. Eles carregam decisões que hoje precisam ser revisadas à luz do Programa 1.

- **Ingestão 2.0 funcionando, mas pouco acoplada a um controle fino de fontes**  
  - A S22 introduziu um motor de Ingestão 2.0, com scheduler e registros de `IngestionRun` por fonte, trazendo robustez para o fluxo de dados.  
  - Esse motor, porém, não está inteiramente “amarrado” ao estado de fonte pensando em operação diária: existe ingestão por fonte, mas o contrato exato de ON/OFF ainda é meio implícito.

- **Console de fontes v1 e API de admin em modo “primeira geração”**  
  - A API `/admin/sources` existe, mas reflete uma fase anterior do produto, com campos parcialmente expostos, contratos meio frouxos e validações que não contemplam todas as regras de negócio que o Programa 1 demanda.  
  - O console de fontes v1 cumpre papel de painel, mas ainda não se comporta como uma ferramenta de operação de alta confiança.

- **Lições de S25: sanidade contínua e intolerância a “duas verdades”**  
  - S25 deixou claro que módulos centrais (como fontes e ingestão) não podem evoluir sem uma história de sanidade que cubra o todo, nem sem contratos muito bem definidos.  
  - Ficou explícito que “estado no banco” e “estado observado” não podem divergir silenciosamente. A Sprint 28 leva essa lição para o coração do módulo de fontes.

---

#### 1.1.3 Foto desejada após a Sprint 28

Depois da Sprint 28, o objetivo é que o mundo seja assim:

1. **Fontes são operadas 100% via console, sem scripts secretos**  
   - Criar uma fonte: ação trivial via UI, com formulários e validação forte.  
   - Editar uma fonte: possível dentro de regras claras (com restrições quando fizer sentido, como em fontes `DEPRECATED`).  
   - Ativar/desativar/deprecar: ações explícitas com feedback imediato, sem necessidade de editar banco ou rodar comandos manuais.

2. **ON/OFF de fonte é determinístico e observável**  
   - `ACTIVE`, `DISABLED`, `DEPRECATED` deixam de ser apenas strings em uma tabela e passam a ser **estados com invariantes fortes**.  
   - O scheduler da Ingestão 2.0 respeita esses estados sem exceção: fontes desativadas não são ingeridas, fontes ativas retornam ao fluxo automaticamente.  
   - Logs e registros de `IngestionRun` permitem enxergar essa relação de forma concreta (ex.: antes/despois de desativar uma fonte).

3. **Modelo de fonte consolidado, pronto para E27.2/E27.3**  
   - O `Source` passa a carregar metadados operacionais relevantes: domínio, categoria, criticidade, modo (`MANUAL`/`AUTO`), cadência, motivo da última mudança de estado, etc.  
   - Essas informações são coerentes entre DB, API e UI, preparando o terreno para:
     - E27.2 ler histórico de ingestão por fonte e expor métricas,  
     - E27.3 calcular saúde de fonte e produzir logs administrativos ricos.

4. **Console de fontes v2 fala a mesma língua do Design System Admin v1**  
   - Visualmente, o console de fontes passa a ser um “cidadão de primeira classe” do ecossistema de consoles do Inspectah.  
   - Estados vazios, loading, erro, filtros e tabelas seguem os padrões de E26, reduzindo a entropia visual e cognitiva.

Essa foto desejada não é o fim da jornada de fontes & ingestão, mas é a base sem a qual os próximos passos (E27.2, E27.3, E29–E32) construiriam em terreno instável.

---

#### 1.1.4 Relação com outras sprints e dependências

A Sprint 28 está ancorada em algumas dependências explícitas:

- **S21 — Modelo inicial de fontes & console v1**  
  - A Sprint 28 lê, respeita e refatora o que for necessário, mas não ignora o histórico: invariantes que já se provaram úteis em S21 são preservadas sempre que fizer sentido.  
  - Ao mesmo tempo, qualquer inconsistência entre o modelo antigo e a visão atual de Programa 1 é encarada de frente, não mascarada.

- **S22 — Ingestão 2.0**  
  - O scheduler e os registros de `IngestionRun` construídos em S22 são a base de validação para os cenários de ON/OFF.  
  - A Sprint 28 não reescreve a Ingestão 2.0, mas exige que ela se comporte de forma coerente com o novo contrato de estado de fonte.

- **E26 — Design System Admin v1 (sprints irmãs)**  
  - O console de fontes v2 é um dos primeiros consumidores pesados do Design System Admin v1.  
  - Quaisquer lacunas de design system identificadas (componentes faltando, patterns pouco claros) são devolvidas como insumo para as sprints de E26 — não como atalho dentro de S28.

- **S25 — Lessons Learned e plano anti-gaps**  
  - A Sprint 28 incorpora o plano anti-gaps pós-S25: nenhum gate crítico de S21/S22 é abandonado, e a evolução de fontes & ingestão é acompanhada por sanidade de legado.

Em termos de linha do tempo, a Sprint 28 é o **primeiro tijolo de E27**. Seu sucesso é pré-requisito tácito para que as próximas sprints de E27 e os épicos E29–E32 tenham onde se apoiar sem voltas desnecessárias.

---

#### 1.1.5 Objetivo em frase única

“**Transformar fontes em um ativo operacional de primeira classe, completamente operável via console, com ON/OFF determinístico e modelo consolidado, preparando o terreno para métricas, saúde e cockpits de casos.**”

Este é o norte fixo da Sprint 28: qualquer decisão de escopo, arquitetura ou priorização deve poder ser justificada em relação a essa frase.

